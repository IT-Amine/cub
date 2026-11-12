---
description: "Configuration du filtrage Stormshield pour le serveur Web WordPress et le scanner en DMZ"
---

# BLOC 3 - Filtrage Stormshield du serveur Web (`ServeurWeb1`)

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** Amine
> - **Date :** 12/11/2026
> - **Domaine :** Réseau et cybersécurité (Stormshield SN210)

---

## 1. Sommaire

- [2. Contexte](#2-contexte)
- [3. Prérequis et topologie](#3-prerequis-et-topologie)
- [4. Création des objets réseau Stormshield](#4-creation-des-objets-reseau-stormshield)
- [5. Configuration des règles de filtrage](#5-configuration-des-regles-de-filtrage)
- [6. Validation de la politique](#6-validation-de-la-politique)
- [7. Contrôle et dépannage](#7-controle-et-depannage)

---

## 2. Contexte

Au sein de l'agence CUB de Dortmund, le serveur **`ServeurWeb1`** (`192.36.4.21/24`) est positionné dans la zone démilitarisée (**DMZ - VLAN 84 : `192.36.4.0/24`**) derrière le pare-feu **`STORMSHIELD01`** (`dmd-fw-c1`, interface DMZ `192.36.4.254/24`). Il héberge deux hôtes virtuels Apache sur le port TCP `80` :

1. **Site vitrine WordPress** : `www1.dortmund.cub.sioplc.fr` ([Procédure WordPress](config-wordpress.md)).
2. **Scanner réseau d'exploitation** : `scanner1.dortmund.cub.sioplc.fr` ([Procédure Scanner](config-scanner.md)).

La politique de filtrage autorise exclusivement les flux HTTP légitimes vers `ServeurWeb1` ainsi que l'administration SSH depuis les réseaux autorisés (**VLAN 20 Administration** et **VLAN 53 Bastion**), puis bloque tout autre flux entrant à destination du serveur Web.

---

## 3. Prérequis et topologie

3.1. **Sauvegarde préalable.** Avant toute modification de la politique active sur `STORMSHIELD01` (`https://192.168.4.205`), effectuer une sauvegarde de la configuration ([Sauvegarde Stormshield](../../securite/stormshield/procedures/sauvegarde-configuration-stormshield.md)) et vérifier que l'accès d'administration depuis le VLAN 20 (`192.168.4.192/28`) reste garanti.

3.2. **Vérification du service et du pare-feu hôte.** Confirmer sur `ServeurWeb1` (`192.36.4.21`) l'écoute d'Apache sur TCP `80`, de SSH sur TCP `22`, ainsi que la présence des règles UFW correspondantes ([Configuration UFW](../../securite/ufw/installation-configuration-ufw.md)).

3.3. **Routage sans NAT vers la DMZ (spécificité CUB).** Conformément au plan d'adressage de l'agence Dortmund, le réseau DMZ (`192.36.4.0/24`) est directement routé sans translation d'adresse (ni DNAT entrant, ni Masquerading sur la DMZ) :
- La destination des règles de filtrage est directement l'adresse DMZ de `ServeurWeb1` (`192.36.4.21`).
- La règle de Masquerading (`RESEAU_LAN` `192.168.4.0/24` $\rightarrow$ `Firewall_out` `192.36.253.40`) ne doit s'appliquer qu'aux flux sortant vers le **WAN (`Internet`)**, et **jamais vers la DMZ (`192.36.4.0/24`)**. Dans le cas contraire, `ServeurWeb1` recevrait l'adresse IP DMZ du pare-feu (`192.36.4.254`) au lieu de l'IP du client (`192.168.4.192/28`), ce qui bloquerait l'accès au scanner Apache (`403 Forbidden`).

---

## 4. Création des objets réseau Stormshield

4.1. **Respecter la convention de nommage (`MACHINE_` / `RESEAU_`).** Dans **Configuration > Objets > Tous les objets**, créer ou vérifier les objets suivants :

| Nom de l'objet | Type | Valeur | Utilisation |
| :--- | :--- | :--- | :--- |
| `MACHINE_WEB1` | Machine (Hôte) | `192.36.4.21` | Serveur Web `ServeurWeb1` en DMZ (VLAN 84). |
| `RESEAU_CLIENTS` | Réseau | `192.168.4.128/26` | Postes clients du VLAN 10 accédant à WordPress. |
| `RESEAU_ADMINISTRATION` | Réseau | `192.168.4.192/28` | Postes d'administration du VLAN 20 (accès WordPress, Scanner et SSH). |
| `RESEAU_BASTION` | Réseau | `192.168.4.208/29` | Sous-réseau Bastion Guacamole (VLAN 53 : `.210` et `.211`) pour le rebond SSH. |
| `RESEAU_LAN` | Réseau | `192.168.4.0/24` | Agrégat des réseaux internes de l'agence Dortmund. |
| `RESEAU_DMZ` | Réseau | `192.36.4.0/24` | Réseau DMZ (VLAN 84). |
| `Internet` | Objet système | `0.0.0.0/0` (hors réseaux privés/locaux) | Trafic WAN / externe accédant au site vitrine WordPress. |

---

## 5. Configuration des règles de filtrage

5.1. **Ouvrir la politique.** Accéder à **Configuration > Politique de sécurité > Filtrage et NAT**, sélectionner l'onglet **Filtrage** et la politique active.

5.2. **Règle 1 — Autoriser le trafic HTTP vers `ServeurWeb1`.** Cliquer sur **Nouvelle règle > Règle simple**, puis renseigner :

| Champ | Valeur |
| :--- | :--- |
| État | `On` |
| Action | `Passer` |
| Source | `Internet`, `RESEAU_LAN` *(ou `Any` si site vitrine exposé sans restriction de source)* |
| Destination | `MACHINE_WEB1` (`192.36.4.21`) |
| Port destination | `http` (TCP `80`) |
| Protocole | `TCP` |
| Inspection | `IPS` (profil standard HTTP) |
| Journalisation | `Activée` |
| Commentaire | `Autoriser HTTP vers ServeurWeb1 (WordPress & Scanner)` |

5.3. **Règle 2 — Autoriser l'administration SSH vers `ServeurWeb1`.** Créer une règle `Passer` dédiée aux flux d'administration :

| Champ | Valeur |
| :--- | :--- |
| État | `On` |
| Action | `Passer` |
| Source | `RESEAU_ADMINISTRATION` (`192.168.4.192/28`), `RESEAU_BASTION` (`192.168.4.208/29`) |
| Destination | `MACHINE_WEB1` (`192.36.4.21`) |
| Port destination | `ssh` (TCP `22`) |
| Protocole | `TCP` |
| Journalisation | `Activée` |
| Commentaire | `Autoriser SSH Admin (VLAN 20) et Bastion (VLAN 53) vers ServeurWeb1` |

5.4. **Règle 3 — Bloquer tous les autres flux entrants vers `ServeurWeb1`.** Créer une règle de blocage explicite placée **immédiatement après** les deux règles d'autorisation précédentes (et avant toute règle générale `Any -> Any` éventuelle) :

| Champ | Valeur |
| :--- | :--- |
| État | `On` |
| Action | `Bloquer` |
| Source | `Any` |
| Destination | `MACHINE_WEB1` (`192.36.4.21`) |
| Port destination | `Any` |
| Protocole | `Any` |
| Journalisation | `Activée` |
| Commentaire | `Bloquer tout autre trafic entrant vers ServeurWeb1` |

> [!warning] Ordre d'évaluation des règles
> L'analyse Stormshield s'effectue de haut en bas (first match). Les règles `Passer` (HTTP et SSH) doivent impérativement précéder la règle `Bloquer` ciblant `MACHINE_WEB1`. Vérifier l'ordre avant de cliquer sur **Sauvegarder et appliquer**.

> [!important] Distinction WordPress vs Scanner sur le port 80
> Les deux VirtualHosts (`www1.dortmund.cub.sioplc.fr` et `scanner1.dortmund.cub.sioplc.fr`) partagent l'adresse IP `192.36.4.21` et le port TCP `80`. Le filtrage IP/Port L3/L4 de Stormshield ne distingue pas le nom d'hôte HTTP (`Host:`). L'isolation du scanner est donc assurée par Apache via `Require ip 192.168.4.192/28` et l'authentification `.htpasswd` (cf. [Configuration du scanner](config-scanner.md)).

5.5. **Préparation au chiffrement HTTPS (TCP `443`).** Une fois le certificat TLS et les VirtualHosts HTTPS configurés sur Apache, ajouter une règle `Passer` vers `MACHINE_WEB1` sur le port `https` (TCP `443`) au-dessus de la règle de blocage, et ouvrir `443/tcp` dans UFW sur `ServeurWeb1`.

---

## 6. Validation de la politique

6.1. **Matrice de recette des accès depuis les différents VLANs :**

| Test | Source | Action | Résultat attendu |
| :--- | :--- | :--- | :--- |
| **Site WordPress (Interne)** | Poste Client (`192.168.4.135` - VLAN 10) | `http://www1.dortmund.cub.sioplc.fr` | Accès autorisé (**200 OK**). |
| **Site WordPress (Externe)** | Poste WAN (`192.36.253.x`) | `http://www1.dortmund.cub.sioplc.fr` | Accès autorisé (**200 OK**). |
| **SSH autorisé (Admin)** | Poste Admin (`192.168.4.193` - VLAN 20) | `ssh <compte_admin>@192.36.4.21` | Connexion SSH établie. |
| **SSH autorisé (Bastion)** | `ServeurBastion0` (`192.168.4.210` - VLAN 53) | Connexion SSH via Guacamole vers `192.36.4.21` | Connexion SSH établie. |
| **SSH non autorisé** | Poste Client (`192.168.4.135` - VLAN 10) ou WAN | `ssh <compte_admin>@192.36.4.21` | Connexion bloquée (Drop Stormshield + UFW). |
| **Scanner autorisé** | Poste Admin (`192.168.4.193` - VLAN 20) | `http://scanner1.dortmund.cub.sioplc.fr` | Invite Basic Auth $\rightarrow$ saisie `admin_tech` $\rightarrow$ **200 OK**. |
| **Scanner non autorisé** | Poste Client (`192.168.4.135` - VLAN 10) ou WAN | `http://scanner1.dortmund.cub.sioplc.fr` | Refusé par Apache (**403 Forbidden**). |

> [!note] Trafic en clair HTTP
> L'authentification HTTP Basic et le trafic sur le port `80` circulent en clair ; le passage en HTTPS (`443/tcp`) est recommandé en environnement de production.

6.2. **Contrôle des journaux Stormshield.** Dans **Monitoring > Journaux > Filtrage**, filtrer sur `dst=192.36.4.21` afin de vérifier le numéro de règle appliqué (`Passer` sur `80`/`22`, `Bloquer` sur tout autre port ou source SSH non autorisée).

---

## 7. Contrôle et dépannage

| Symptôme | Points de contrôle |
| :--- | :--- |
| **Site `www1` inaccessible** | Résolution DNS (`ns0` `192.36.4.10` / `ns1` `192.36.4.11`), écoute Apache (`ss -lntup \| grep 80`), règle UFW (`80/tcp`), routage vers `192.36.4.254` et règle Stormshield `Passer` HTTP. |
| **Flux autorisé mais bloqué par le pare-feu** | Ordre des règles (la règle `Passer` doit précéder la règle `Bloquer`), valeur de `MACHINE_WEB1` (`192.36.4.21`), et logs dans **Monitoring > Journaux > Filtrage**. |
| **SSH refusé depuis VLAN 20 ou VLAN 53** | Présence des deux réseaux `192.168.4.192/28` et `192.168.4.208/29` dans la règle SSH Stormshield **et** dans UFW sur `ServeurWeb1`, et état du démon `sshd`. |
| **Scanner accessible hors VLAN 20 ou refusant un administrateur** | Vérifier qu'aucune règle SNAT (Masquerading) ne s'applique aux flux `LAN -> DMZ` (`192.36.4.254` masquerait l'IP réelle du poste Admin) et contrôler `Require ip 192.168.4.192/28` dans `/etc/apache2/sites-available/scanner1.conf`. |
