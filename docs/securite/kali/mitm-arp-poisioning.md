---
description: "Interception de trafic réseau : Port Mirroring (SPAN Cisco) et attaque Man-in-the-Middle par ARP Poisoning avec Ettercap et Wireshark"
---

# BLOC 2 - Interception Réseau : Port Mirroring et Attaque Man-in-the-Middle (ARP Poisoning)

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** Amine
> - **Date :** Novembre 2026
> - **Domaine :** Cybersécurité & Pentest (Interception réseau)

---

## 1. Sommaire

- [3. Scénario 1 — Interception légitime par Port Mirroring (SPAN Cisco)](#3-scenario-1-interception-legitime-par-port-mirroring-span-cisco)
- [4. Scénario 2 — Attaque offensive Man-in-the-Middle par ARP Poisoning (Ettercap)](#4-scenario-2-attaque-offensive-man-in-the-middle-par-arp-poisoning-ettercap)
- [5. Sécurisation applicative — Chiffrement HTTPS et certificat TLS auto-signé](#5-securisation-applicative-chiffrement-https-et-certificat-tls-auto-signe)

---

## 3. Scénario 1 — Interception légitime par Port Mirroring (SPAN Cisco)

Le **Port Mirroring** (dénommé **SPAN** - *Switched Port Analyzer* chez Cisco) permet de copier l'intégralité du trafic réseau transitant sur un ou plusieurs ports sources (ou VLANs) et de le renvoyer vers un port de destination dédié où est raccordée une sonde d'analyse (Wireshark sur Kali Linux).

### 3.1. Configuration du port mirroring sur le commutateur Cisco

3.1.1. **Passage en mode privilégié et accès à la configuration globale.**

```cisco
enable
configure terminal
```

3.1.2. **Configuration du port source de la session de capture.**  
Sélection du port source connecté à l'équipement à surveiller (ex : port `FastEthernet 0/10`). La directive `both` copie aussi bien les paquets entrants (`rx`) que sortants (`tx`).

```cisco
monitor session 1 source interface FastEthernet 0/10 both
```

> [!TIP] Capture par VLAN source
> Il est également possible de surveiller l'ensemble des trames d'un VLAN particulier au lieu d'une interface physique isolée :
> ```cisco
> monitor session 1 source vlan 10 both
> ```

3.1.3. **Configuration du port de destination.**  
Le port de destination (ex : `FastEthernet 0/12`) est le port physique du commutateur sur lequel est branchée la station d'analyse Wireshark.

```cisco
monitor session 1 destination interface FastEthernet 0/12
```

3.1.4. **Vérification de l'état de la session SPAN.**

```cisco
show monitor session 1
```

```text title="Exemple de retour console Cisco Catalyst"
Session 1
---------
Type                     : Local Session
Source VLANs             :
    Both                 : 10
Destination Ports        : Fa0/12 (ou Gi1/0/13)
    Encapsulation        : Native
          Ingress        : Disabled
```

### 3.2. Récupération des identifiants dans la capture de trame

Une fois le mirroring actif, l'administrateur lance l'écoute sur l'interface réseau de la station d'analyse avec **Wireshark** et applique le filtre d'affichage `http`.

Lorsqu'un utilisateur se connecte à un service non chiffré tel que l'outil de diagnostic réseau hébergé sur `http://scanner1.dortmund.cub.sioplc.fr/` (`192.36.4.21`), l'authentification HTTP basique (`mod_auth_basic`) transmet les identifiants sous forme d'une chaîne encodée en Base64 dans l'en-tête `Authorization`.

![Capture Wireshark de l'authentification HTTP en clair](./img/wireshark.png)

#### Analyse détaillée des données interceptées :

- **Trame analysée :** Trame n° 1041 (Requête `GET / HTTP/1.1`)
- **Adresse IP Source (Client) :** `192.168.4.197`
- **Adresse IP Destination (Serveur Web DMZ) :** `192.36.4.21`
- **Hôte virtuel interrogé :** `scanner1.dortmund.cub.sioplc.fr`
- **Champ d'en-tête HTTP :** `Authorization: Basic YWRtaW5fdGVjaDpQWVhWcWo3dKJrN2JPYjE=`
- **Décodage direct de la charge utile :**
  - **Identifiant :** `admin_tech`
  - **Mot de passe :** `PYXVqj7vBk7b0b1`

> [!CAUTION] Vulnérabilité majeure de l'authentification HTTP en clair
> Le codage Base64 ne constitue **en aucun cas un chiffrement**. Toute entité disposant d'une vue sur le trafic réseau peut immédiatement reconstituer le mot de passe en clair sans nécessiter de clé cryptographique.

---

## 4. Scénario 2 — Attaque offensive Man-in-the-Middle par ARP Poisoning (Ettercap)

En l'absence de port mirroring configuré sur les commutateurs, un commutateur réseau filtre le trafic monocast (*Unicast*) en n'envoyant les trames qu'au port associé à l'adresse MAC de destination (via sa table CAM).

L'attaque **ARP Cache Poisoning** (ou *ARP Spoofing*) consiste à envoyer des paquets ARP non sollicités (*Gratuitous ARP*) pour altérer la table de correspondance IP/MAC de la victime et de la passerelle. Kali Linux s'intercale alors entre la victime et la passerelle, forçant tout le trafic à transiter par son interface réseau.

### 4.1. Définition des cibles et activation du routage IP

4.1.1. **Identification des adresses IP et MAC du banc d'essai :**
- **Passerelle cible (Target 1) :** `192.168.4.206` (MAC `a4:11:bb:d7:3a:56`)
- **Poste victime (Target 2) :** `192.168.4.197` (MAC `c8:17:f5:fa:0e:5d`)
- **Poste attaquant :** `192.168.4.196` (MAC `00:0c:29:08:9f:dc`)

4.1.2. **Activation du routage IPv4 sur Kali Linux (IP Forwarding).**  
Cette étape est indispensable : sans routage actif, la machine attaquante absorberait le trafic du client sans le réexpédier vers la passerelle, causant une rupture de service immédiate (*Déni de service - DoS*) au lieu d'une interception transparente.

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

Pour pérenniser cette directive (optionnel) :
```bash
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
```

### 4.2. Déroulement de l'attaque avec l'interface graphique Ettercap

1. **Démarrage d'Ettercap GUI :** Exécuter `sudo ettercap -G`. Dans la fenêtre de démarrage, sélectionner l'interface réseau primaire `eth0` et valider en cliquant sur la coche en haut à droite.

![Validation de l'interface réseau dans Ettercap](./img/valide.png)

2. **Recherche des hôtes actifs :** Cliquer sur l'icône de loupe en haut à gauche (*Scan for hosts*) afin de balayer le sous-réseau `192.168.4.192/28`.

![Balayage des hôtes sur le sous-réseau](./img/loupe.png)

3. **Affichage de la liste des hôtes :** Cliquer sur l'icône représentant une liste de serveurs (*Host List*) pour afficher les adresses IP et MAC recensées.

![Liste des machines découvertes](./img/serv.png)

4. **Sélection et affectation des cibles (Targets) :**
   - Sélectionner l'adresse IP de la passerelle (`192.168.4.206`) et cliquer sur **Add to Target 1**.
   - Sélectionner l'adresse IP du poste client victime (`192.168.4.197`) et cliquer sur **Add to Target 2**.

![Attribution des cibles Target 1 et Target 2](./img/target.png)

5. **Lancement de l'attaque d'empoisonnement ARP :**  
   Cliquer sur l'icône du globe en haut à droite (*Menu MITM*), puis sélectionner **ARP poisoning...**.

![Sélection de l'attaque ARP Poisoning](./img/planete.png)

6. **Validation des paramètres d'écoute :**  
   Dans la fenêtre contextuelle *MITM Attack: ARP Poisoning*, cocher la case **Sniff remote connections** afin de capturer le trafic bidirectionnel, puis cliquer sur **OK**.

![Configuration des paramètres de l'attaque](./img/mitm.png)

### 4.3. Vérification de l'altération du cache ARP

Pour valider l'effectivité du détournement, on inspecte la table de voisinage ARP sur les deux machines à l'aide de la commande `ip neigh` (ou `arp -a`).

```bash
# Vérification sur le poste d'audit Kali Linux
ip neigh
```

```text title="Table ARP observée sur Kali Linux (192.168.4.196)"
192.168.4.205 dev eth0 lladdr 00:0d:b4:20:6b:29 STALE 
192.168.4.196 dev eth0 lladdr 00:0c:29:08:9f:dc STALE 
192.168.4.206 dev eth0 lladdr a4:11:bb:d7:3a:56 REACHABLE 
192.168.4.197 dev eth0 lladdr c8:17:f5:fa:0e:5d STALE 
```

Sur le poste de la victime (`192.168.4.197`), on consulte la table ARP :

```text title="Table ARP empoisonnée sur le poste victime (192.168.4.197)"
? (192.168.4.196) at 00:0c:29:08:9f:dc on en4 ifscope [ethernet]
? (192.168.4.205) at 00:0d:b4:20:6b:29 on en4 ifscope [ethernet]
? (192.168.4.206) at 00:0c:29:08:9f:dc on en4 ifscope [ethernet]
```

> [!IMPORTANT] Preuve technique de l'usurpation
> Dans la table ARP de la victime, l'adresse IP de la passerelle par défaut (`192.168.4.206`) est désormais associée à l'adresse MAC `00:0c:29:08:9f:dc`, qui correspond à la carte réseau de **Kali Linux**.
> La victime communique désormais à son insu avec l'attaquant pour tout paquet destiné à l'extérieur de son segment local.

### 4.4. Interception et analyse du trafic dans Wireshark

L'attaquant exécute alors Wireshark sur l'interface `eth0` de Kali Linux et filtre les paquets avec l'expression `http`. Lorsque le client se connecte à l'application web d'administration (`192.36.4.21`), l'ensemble de la transaction est intercepté en transit.

![Interception des flux HTTP détournés via Wireshark](./img/wireshark.png)

Les requêtes HTTP GET/POST, les paramètres d'en-tête et les identifiants d'authentification (`admin_tech:PYXVqj7vBk7b0b1`) sont interceptés en clair de la même manière que lors du port mirroring.

---

## 5. Sécurisation applicative — Chiffrement HTTPS et certificat TLS auto-signé

Pour neutraliser l'interception en clair des identifiants HTTP lors d'une écoute passive (**Port Mirroring**) ou d'une attaque **ARP Poisoning** en mode relais, il est indispensable de basculer les hôtes virtuels Apache de `ServeurWeb1` (`192.36.4.21`) en **HTTPS (`443/tcp`)** à l'aide de certificats TLS et d'une redirection permanente depuis le port `80`.

Une fois le chiffrement TLS 1.2/1.3 actif :
- Les requêtes HTTP, les en-têtes `Authorization: Basic` et les formulaires WordPress apparaissent uniquement sous forme de segments chiffrés (`Application Data`) dans **Wireshark**.
- Les deux hôtes virtuels hébergés sur `192.36.4.21` coexistent sur le même port `443/tcp` grâce à l'extension TLS **SNI (*Server Name Indication*)**.

> [!IMPORTANT] Fiches détaillées de configuration HTTPS
> Afin d'alléger ce document d'audit, les procédures complètes (génération OpenSSL 3.x avec SAN, VirtualHosts durcis ANSSI/Mozilla, adaptation `wp-config.php`, règles UFW sur `ens18` et validation SNI) sont réparties dans deux fiches dédiées :
>
> - **Scanner Réseau (`scanner1`) :** [Configuration HTTPS et certificat TLS auto-signé — `scanner1`](../../services/web/config-https-scanner1.md)
> - **Site Vitrine WordPress (`www1`) :** [Configuration HTTPS et certificat TLS auto-signé — `www1`](../../services/web/config-https-www1.md)

> [!WARNING] Limite du certificat auto-signé face à un MITM actif
> Un certificat auto-signé protège efficacement contre l'écoute passive et le simple relais IP, mais ne suffit pas contre un attaquant effectuant une interception TLS active (*SSL Intercept* dans Ettercap avec forge de certificat). En production, déployez une **PKI interne d'entreprise** ou un certificat public (**Let's Encrypt**) associé à **HSTS**.


