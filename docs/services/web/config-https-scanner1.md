---
description: "Procédure de sécurisation HTTPS avec certificat TLS auto-signé, VirtualHost Apache durci et filtrage UFW pour le scanner réseau (scanner1)"
---

# Configuration HTTPS et Certificat TLS Auto-Signé — Scanner Réseau (`scanner1`)

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** Amine
> - **Date :** 26/11/2026
> - **Domaine :** Services Web & Cybersécurité (TLS / HTTPS)

---

## 1. Sommaire

- [2. Contexte et prérequis](#2-contexte-et-prerequis)
- [3. Génération du certificat TLS auto-signé (OpenSSL 3.x)](#3-generation-du-certificat-tls-auto-signe-openssl-3x)
- [4. Activation des modules Apache et vérification du port 443](#4-activation-des-modules-apache-et-verification-du-port-443)
- [5. Configuration des VirtualHosts Apache (HTTPS et redirection)](#5-configuration-des-virtualhosts-apache-https-et-redirection)
- [6. Pare-feu local UFW et Stormshield](#6-pare-feu-local-ufw-et-stormshield)
- [7. Validation TLS et limites du certificat auto-signé](#7-validation-tls-et-limites-du-certificat-auto-signe)

---

## 2. Contexte et prérequis

Le scanner réseau d'exploitation hébergé sur **`ServeurWeb1`** (`192.36.4.21`, Debian 12 / Apache 2.4) et accessible via `scanner1.dortmund.cub.sioplc.fr` utilise une authentification HTTP basique (`mod_auth_basic`). Sans chiffrement TLS, les identifiants encodés en Base64 sont directement lisibles lors d'une interception réseau (cf. [Port Mirroring et ARP Poisoning](../../securite/kali/mitm-arp-poisioning.md)).

Cette procédure sécurise `scanner1` en **HTTPS (`443/tcp`)** tout en maintenant son isolation stricte au **VLAN 20 Administration (`192.168.4.192/28`)**.

> [!important] Prérequis obligatoires
> - La pile LAMP doit être déployée : [Installation Apache2, MariaDB et PHP](installation-apache2-mariadb.md).
> - Le VirtualHost HTTP initial et le fichier `.htpasswd` doivent être en place : [Configuration du scanner réseau (`scanner1`)](config-scanner.md).
> - Le pare-feu hôte UFW doit être actif : [Configuration UFW](../../securite/ufw/installation-configuration-ufw.md).

---

## 3. Génération du certificat TLS auto-signé (OpenSSL 3.x)

Sur `ServeurWeb1` (`192.36.4.21`), génération d'une clé privée RSA de 2048 bits (minimum exigé par l'ANSSI ; `3072` bits recommandés pour un usage pérenne) et d'un certificat X.509 v3 valide 365 jours.

> [!IMPORTANT] Extension SAN (Subject Alternative Name) obligatoire
> Depuis la **RFC 2818** et l'évolution des navigateurs modernes (Chrome 58+, Firefox 48+), le champ `CN` (*Common Name*) seul est ignoré lors de la vérification d'identité. L'extension **`subjectAltName`** listant les noms DNS et l'adresse IP est **obligatoire** via `-addext`, sans quoi le certificat sera rejeté (`ERR_CERT_COMMON_NAME_INVALID`).  
> Sous OpenSSL 3.0+, l'option `-noenc` remplace `-nodes` (dépréciée) pour ne pas chiffrer la clé privée par phrase secrète.

```bash
# Génération de la clé privée RSA et du certificat auto-signé X.509 v3 avec extensions SAN
sudo openssl req -x509 -newkey rsa:2048 -noenc -days 365 \
  -keyout /etc/ssl/private/scanner1.key \
  -out /etc/ssl/certs/scanner1.crt \
  -subj "/C=FR/ST=Centre-Val de Loire/L=Tours/O=CUB/OU=DSI/CN=scanner1.dortmund.cub.sioplc.fr" \
  -addext "basicConstraints=CA:FALSE" \
  -addext "keyUsage=digitalSignature,keyEncipherment" \
  -addext "extendedKeyUsage=serverAuth" \
  -addext "subjectAltName=DNS:scanner1.dortmund.cub.sioplc.fr,DNS:scanner1,IP:192.36.4.21"

# Restriction stricte des permissions système
sudo chown root:root /etc/ssl/private/scanner1.key
sudo chmod 600 /etc/ssl/private/scanner1.key
sudo chmod 644 /etc/ssl/certs/scanner1.crt
```

Vérification de la présence des entrées SAN dans le certificat généré :

```bash
openssl x509 -in /etc/ssl/certs/scanner1.crt -text -noout | grep -A 3 "Subject Alternative Name"
```

---

## 4. Activation des modules Apache et vérification du port 443

4.1. **Activation des modules `ssl` et `headers` :**  
*(La directive `Redirect permanent` repose sur `mod_alias`, activé par défaut sous Debian ; `mod_headers` permet l'ajout ultérieur d'en-têtes de sécurité tels que HSTS).*

```bash
sudo a2enmod ssl headers
```

4.2. **Vérification de `/etc/apache2/ports.conf` :**  
Sous Debian, l'activation de `mod_ssl` permet à Apache d'écouter sur le port `443` via le bloc natif suivant :

```apache title="/etc/apache2/ports.conf (vérification)"
<IfModule ssl_module>
    Listen 443
</IfModule>
```

---

## 5. Configuration des VirtualHosts Apache (HTTPS et redirection)

5.1. **Création du VirtualHost HTTPS (`/etc/apache2/sites-available/scanner1-ssl.conf`) :**

La configuration TLS suit le profil **Mozilla SSL Configuration Generator (Intermediate)** et les **recommandations TLS de l'ANSSI** :
- Protocoles limités exclusivement à **TLS 1.2** et **TLS 1.3** (`SSLProtocol -all +TLSv1.2 +TLSv1.3`).
- Suites TLS 1.2 restreintes aux suites offrant le **Perfect Forward Secrecy (ECDHE)** et un chiffrement authentifié **AEAD (GCM / ChaCha20-Poly1305)**.
- Définition explicite des suites TLS 1.3 via la syntaxe Apache ≥ 2.4.43 (`SSLCipherSuite TLSv1.3 ...`).

```apache title="/etc/apache2/sites-available/scanner1-ssl.conf"
<VirtualHost *:443>
    ServerName scanner1.dortmund.cub.sioplc.fr
    ServerAlias scanner1
    ServerAdmin webmaster@cub.sioplc.fr
    DocumentRoot /var/www/html/scanner

    # Activation du moteur TLS et association du certificat X.509
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/scanner1.crt
    SSLCertificateKeyFile /etc/ssl/private/scanner1.key

    # Protocoles et suites cryptographiques conformes ANSSI / Mozilla Intermediate
    SSLProtocol -all +TLSv1.2 +TLSv1.3
    SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305
    SSLCipherSuite TLSv1.3 TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256
    SSLHonorCipherOrder off
    SSLSessionTickets off

    # En-tête HSTS : À activer UNIQUEMENT une fois le certificat (ou l'AC interne) approuvé par les postes clients
    # Header always set Strict-Transport-Security "max-age=31536000"

    <Directory /var/www/html/scanner>
        Options -Indexes +FollowSymLinks
        AllowOverride None

        <RequireAll>
            # Condition 1 : Restriction stricte au VLAN 20 (Administration)
            Require ip 192.168.4.192/28

            # Condition 2 : Authentification HTTP basique obligatoire (protégée par le tunnel TLS)
            AuthType Basic
            AuthName "Acces Restreint - Administration CUB"
            AuthUserFile /etc/apache2/.htpasswd
            Require valid-user
        </RequireAll>
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/scanner1_ssl_error.log
    CustomLog ${APACHE_LOG_DIR}/scanner1_ssl_access.log combined
</VirtualHost>
```

> [!WARNING] Précaution d'usage pour HSTS avec un certificat auto-signé
> L'activation de `Strict-Transport-Security` (HSTS) empêche les navigateurs modernes de proposer le bouton d'exception (*Avancé → Continuer*) face à un certificat non approuvé. N'activez HSTS qu'après avoir importé le certificat (ou le certificat racine d'une PKI interne) dans le magasin de confiance des postes d'administration.

5.2. **Redirection HTTP (`80`) vers HTTPS (`443`) dans `scanner1.conf` :**  
Il est essentiel de ne laisser **aucune directive `AuthType Basic`** dans `<VirtualHost *:80>`, afin d'éviter qu'un navigateur ne transmette les identifiants en clair avant la redirection.

```apache title="/etc/apache2/sites-available/scanner1.conf"
<VirtualHost *:80>
    ServerName scanner1.dortmund.cub.sioplc.fr
    ServerAlias scanner1

    # Redirection permanente 301 (mod_alias) vers le canal chiffré HTTPS
    Redirect permanent / https://scanner1.dortmund.cub.sioplc.fr/
</VirtualHost>
```

5.3. **Activation des sites et rechargement d'Apache :**

```bash
sudo a2ensite scanner1-ssl.conf
sudo a2ensite scanner1.conf
sudo apache2ctl configtest
sudo systemctl restart apache2
```

---

## 6. Pare-feu local UFW et Stormshield

6.1. **Ouverture ciblée sur `UFW` (`ens18`) :**  
Autorisation du port `443/tcp` sur `192.36.4.21` exclusivement depuis le sous-réseau d'administration **VLAN 20 (`192.168.4.192/28`)** :

```bash
sudo ufw allow in on ens18 \
  from 192.168.4.192/28 \
  to 192.36.4.21 \
  port 443 proto tcp \
  comment 'CUB - HTTPS scanner1 depuis VLAN20'

sudo ufw status numbered
```

```text title="Résultat de la table UFW sur ServeurWeb1 (192.36.4.21)"
Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 22/tcp                     ALLOW IN    192.168.4.192/28           # SSH depuis VLAN 20 Admin
[ 2] 22/tcp                     ALLOW IN    192.168.4.208/29           # SSH depuis VLAN 53 Bastion
[ 3] 80/tcp                     ALLOW IN    Anywhere                   # HTTP Apache
[ 4] 192.36.4.21 443/tcp on ens18 ALLOW IN    192.168.4.192/28           # CUB - HTTPS scanner1 depuis VLAN20
[ 5] 80/tcp (v6)                ALLOW IN    Anywhere (v6)              # HTTP Apache
```

> [!IMPORTANT] Flux réseau sur le pare-feu périmétrique
> En complément de la règle UFW sur `ServeurWeb1`, le flux **TCP `443` (`https`)** doit également être autorisé dans les règles de filtrage du pare-feu **Stormshield (`STORMSHIELD01`)** vers `MACHINE_WEB1` (`192.36.4.21`) (cf. [Filtrage Stormshield ServeurWeb1](firewall-wordpress.md)).

---

## 7. Validation TLS et limites du certificat auto-signé

7.1. **Test de validation TLS depuis un poste autorisé du VLAN 20 :**

```bash
curl -I --cacert /etc/ssl/certs/scanner1.crt -u admin_tech https://scanner1.dortmund.cub.sioplc.fr
```

- **Impact face au sniffing :** Sous Wireshark, les paquets deviennent des segments `Application Data` chiffrés (TLS 1.2/1.3). L'en-tête `Authorization: Basic` et les identifiants `admin_tech` deviennent illisibles.
- **Limite face à un MITM actif (*SSL Intercept* / *SSL Stripping*) :** Un certificat auto-signé n'étant pas signé par une autorité de certification reconnue, un attaquant effectuant une interception SSL peut présenter son propre faux certificat à la victime. En production, l'usage d'une **PKI interne d'entreprise** (ou d'une AC reconnue comme Let's Encrypt) déployée sur les postes clients et combinée à **HSTS** est indispensable.
