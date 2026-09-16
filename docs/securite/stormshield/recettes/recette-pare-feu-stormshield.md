---
description: Documentation et procédure technique.
---

# BLOC 3 - Fiche Recette : Pare-feu Stormshield

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 09/09/2026</p>
    <p><strong>Contexte :</strong> Configuration Fiche Recette : Pare-feu Stormshield</p>
</div>

---

## Informations

- **Auteur :** Amine Kada
- **Date :** 09/09/2026
- **Domaine :** Réseau

---

## 1. Contexte du Test

Validation de l'infrastructure réseau autour du pare-feu Stormshield (Couches 3 et 4 du modèle OSI). 
L'objectif est de certifier :
- Les règles de translation d'adresses (NAT) autorisant internet pour le LAN.
- L'absence de NAT pour la zone DMZ.
- L'accès exclusif aux interfaces de management (SSH/HTTPS) pour le VLAN Administration.

### Rappel de la topologie d'adressage

| Zone | VLAN | Adressage IP |
| :--- | :---: | :--- |
| **DMZ** | `84` | `192.36.4.0/24` |
| **LAN** (Production/Clients) | `-` | `192.168.4.0/25` et `192.168.4.128/26` |
| **Administration** | `20` | `192.168.4.192/28` |

---

## 2. Procédures de Validation

### 2.1. Validation du NAT (Réseau LAN -> WAN)

**Objectif :** Vérifier que les requêtes ICMP issues du LAN ont bien accès à Internet et sont translatées par le pare-feu avec l'IP publique (`192.36.253.40`).

**Commande utilisée :**
```bash
tcpdump -i mvneta0 -nn icmp
```
* **`tcpdump`** : Analyseur de paquets réseau en ligne de commande.
* **`-i mvneta0`** : Spécifie l'interface réseau sur laquelle écouter (l'interface externe/WAN).
* **`-nn`** : Désactive la résolution de noms d'hôtes et de ports (accélère l'affichage en gardant les IPs brutes).
* **`icmp`** : Filtre uniquement les paquets du protocole ICMP (les requêtes et réponses ping).

**Résultat attendu :**
```text
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on mvneta0, link-type EN10MB (Ethernet), capture size 262144 bytes
16:22:16.965500 IP 192.36.253.40 > 8.8.8.8: ICMP echo request, id 1, seq 37, length 40
16:22:16.972498 IP 8.8.8.8 > 192.36.253.40: ICMP echo reply, id 1, seq 37, length 40
16:22:17.963059 IP 192.36.253.40 > 8.8.8.8: ICMP echo request, id 1, seq 38, length 40
16:22:17.970000 IP 8.8.8.8 > 192.36.253.40: ICMP echo reply, id 1, seq 38, length 40
```

---

### 2.2. Validation du non-NAT (Réseau DMZ -> WAN)

**Objectif :** Vérifier que le trafic sortant de la DMZ (VLAN 84) conserve son adresse IP source d'origine sans subir de translation (mascarade).

**Commande utilisée :**
```bash
tcpdump -i mvneta0 -nn icmp
```
* **`tcpdump`** : Outil d'écoute réseau.
* **`-i mvneta0`** : Interface externe écoutée.
* **`-nn`** : Format numérique pour les adresses et ports.
* **`icmp`** : Capture des paquets de diagnostic (ping).

**Résultat attendu :**
```text
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on mvneta0, link-type EN10MB (Ethernet), capture size 262144 bytes
16:24:43.575455 IP 192.36.4.1 > 8.8.8.8: ICMP echo request, id 1, seq 41, length 40
16:24:43.582459 IP 8.8.8.8 > 192.36.4.1: ICMP echo reply, id 1, seq 41, length 40
16:24:44.587458 IP 192.36.4.1 > 8.8.8.8: ICMP echo request, id 1, seq 42, length 40
16:24:44.594459 IP 8.8.8.8 > 192.36.4.1: ICMP echo reply, id 1, seq 42, length 40
```
> **Critère de réussite :** L'adresse IP source lisible dans la capture doit rester l'IP privée de la machine en DMZ (ex: `192.36.4.1`).

---

### 2.3. Validation de l'accès au Management depuis le VLAN Admin

**Objectif :** S'assurer que les administrateurs situés dans le sous-réseau `192.168.4.192/28` accèdent bien au pare-feu sur l'IP `192.168.4.205`.

#### Test de fonctionnement de l'accès SSH
*(Depuis un poste du VLAN 20)*

**Commande :**
```bash
ssh admin@192.168.4.205
```
* **`ssh`** : Démarre le client SSH (Couche 7) pour ouvrir un terminal distant chiffré.
* **`admin@192.168.4.205`** : Spécifie le nom d'utilisateur `admin` et l'adresse IP cible du pare-feu.

#### Test de fonctionnement de l'interface d'administration

**Commande :**
```bash
curl -kI [https://192.168.4.205](https://192.168.4.205)
```
* **`curl`** : Client HTTP/HTTPS en ligne de commande.
* **`-k`** : Ignore les erreurs de certificat SSL/TLS (fréquent sur les pare-feux).
* **`-I`** : Requête de type HEAD, n'affiche que les en-têtes HTTP renvoyés par le serveur.

**Résultat attendu :**
```text
# Succès SSH (Demande de mot de passe puis accès prompt) :
Password: 
dmd-fw-c1-SN210A30HC710A7> 

# Succès HTTPS :
HTTP/1.1 200 OK
Server: nginx
```