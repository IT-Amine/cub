---
description: "Procédure de sécurisation HTTPS avec certificat TLS auto-signé, VirtualHost Apache SNI, adaptation wp-config.php et filtrage UFW pour WordPress (www1)"
---

# Configuration HTTPS et Certificat TLS Auto-Signé — WordPress (`www1`)

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** Amine
> - **Date :** 26/11/2026
> - **Domaine :** Services Web & Cybersécurité (TLS / WordPress)

---

## 1. Sommaire

- [2. Contexte et prérequis](#2-contexte-et-prerequis)
- [3. Génération du certificat TLS auto-signé (OpenSSL 3.x)](#3-generation-du-certificat-tls-auto-signe-openssl-3x)
- [4. Configuration des VirtualHosts Apache (SNI et redirection)](#4-configuration-des-virtualhosts-apache-sni-et-redirection)
- [5. Adaptation HTTPS dans WordPress (wp-config.php)](#5-adaptation-https-dans-wordpress-wp-configphp)
- [6. Pare-feu local UFW et Stormshield](#6-pare-feu-local-ufw-et-stormshield)
- [7. Validation TLS, SNI et limites du certificat auto-signé](#7-validation-tls-sni-et-limites-du-certificat-auto-signe)

---

## 2. Contexte et prérequis

Le site vitrine WordPress hébergé sur **`ServeurWeb1`** (`192.36.4.21`, Debian 12 / Apache 2.4) et accessible via `www1.dortmund.cub.sioplc.fr` partage l'adresse IP et les ports d'écoute avec le scanner réseau (`scanner1`).

Le passage en **HTTPS (`443/tcp`)** chiffre la navigation des utilisateurs (VLAN 10 Clients, VLAN 20 Administration et accès externes) ainsi que les authentifications d'administration WordPress (`/wp-admin`), empêchant l'interception de mots de passe ou cookies de session via Wireshark ou ARP Poisoning (cf. [Port Mirroring et ARP Poisoning](../../securite/kali/mitm-arp-poisioning.md)).

> [!important] Prérequis obligatoires
> - La pile LAMP doit être déployée et les modules `ssl` / `headers` activés : [Installation Apache2, MariaDB et PHP](installation-apache2-mariadb.md).
> - Le site WordPress et le VirtualHost HTTP initial doivent être opérationnels : [Configuration WordPress (`www1`)](config-wordpress.md).
> - Le serveur `ServeurWeb1` utilise **SNI (*Server Name Indication*)** dans Apache 2.4 pour héberger conjointement `www1` et [`scanner1`](config-https-scanner1.md) sur `192.36.4.21:443`.

---

## 3. Génération du certificat TLS auto-signé (OpenSSL 3.x)

Sur `ServeurWeb1` (`192.36.4.21`), génération d'une clé privée RSA de 2048 bits (minimum exigé par l'ANSSI ; `3072` bits recommandés pour un usage pérenne) et d'un certificat X.509 v3 valide 365 jours.

> [!IMPORTANT] Extension SAN (Subject Alternative Name) obligatoire
> Depuis la **RFC 2818** et l'évolution des navigateurs modernes (Chrome 58+, Firefox 48+), le champ `CN` (*Common Name*) seul est ignoré lors de la vérification d'identité. L'extension **`subjectAltName`** listant les noms DNS et l'adresse IP est **obligatoire** via `-addext`, sans quoi le certificat sera rejeté (`ERR_CERT_COMMON_NAME_INVALID`).  
> Sous OpenSSL 3.0+, l'option `-noenc` remplace `-nodes` (dépréciée) pour ne pas chiffrer la clé privée par phrase secrète.

```bash
# Génération de la clé privée RSA et du certificat auto-signé X.509 v3 avec extensions SAN
sudo openssl req -x509 -newkey rsa:2048 -noenc -days 365 \
  -keyout /etc/ssl/private/www1.key \
  -out /etc/ssl/certs/www1.crt \
  -subj "/C=FR/ST=Centre-Val de Loire/L=Tours/O=CUB/OU=DSI/CN=www1.dortmund.cub.sioplc.fr" \
  -addext "basicConstraints=CA:FALSE" \
  -addext "keyUsage=digitalSignature,keyEncipherment" \
  -addext "extendedKeyUsage=serverAuth" \
  -addext "subjectAltName=DNS:www1.dortmund.cub.sioplc.fr,DNS:www1,IP:192.36.4.21"

# Restriction stricte des permissions système
sudo chown root:root /etc/ssl/private/www1.key
sudo chmod 600 /etc/ssl/private/www1.key
sudo chmod 644 /etc/ssl/certs/www1.crt
```

Vérification des extensions SAN du certificat généré :

```bash
openssl x509 -in /etc/ssl/certs/www1.crt -text -noout | grep -A 3 "Subject Alternative Name"
```

---

## 4. Configuration des VirtualHosts Apache (SNI et redirection)

4.1. **Activation des modules Apache requis (si non déjà effectuée) :**

```bash
sudo a2enmod ssl headers
```

*(Vérifier que `/etc/apache2/ports.conf` contient `<IfModule ssl_module> Listen 443 </IfModule>`).*

4.2. **Création du VirtualHost HTTPS (`/etc/apache2/sites-available/www1-ssl.conf`) :**

Contrairement à `scanner1`, le site vitrine `www1` reste ouvert aux visiteurs (`Require all granted`) et conserve `AllowOverride All` pour les règles `.htaccess` des permaliens WordPress. La configuration TLS suit le profil **Mozilla SSL Configuration Generator (Intermediate)** et les **recommandations TLS de l'ANSSI**.

```apache title="/etc/apache2/sites-available/www1-ssl.conf"
<VirtualHost *:443>
    ServerName www1.dortmund.cub.sioplc.fr
    ServerAlias www1
    ServerAdmin webmaster@cub.sioplc.fr
    DocumentRoot /var/www/html/www1

    # Activation du moteur TLS et association du certificat X.509
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/www1.crt
    SSLCertificateKeyFile /etc/ssl/private/www1.key

    # Protocoles et suites cryptographiques conformes ANSSI / Mozilla Intermediate
    SSLProtocol -all +TLSv1.2 +TLSv1.3
    SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305
    SSLCipherSuite TLSv1.3 TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256
    SSLHonorCipherOrder off
    SSLSessionTickets off

    # En-tête HSTS : À activer UNIQUEMENT une fois le certificat (ou l'AC interne) approuvé par les postes clients
    # Header always set Strict-Transport-Security "max-age=31536000"

    <Directory /var/www/html/www1>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/www1_ssl_error.log
    CustomLog ${APACHE_LOG_DIR}/www1_ssl_access.log combined
</VirtualHost>
```

> [!WARNING] Précaution d'usage pour HSTS avec un certificat auto-signé
> L'activation de `Strict-Transport-Security` (HSTS) empêche les navigateurs modernes de proposer le bouton d'exception (*Avancé → Continuer*) face à un certificat non approuvé. N'activez HSTS qu'après avoir déployé une AC interne approuvée ou un certificat émis par une AC publique (Let's Encrypt).

4.3. **Redirection HTTP (`80`) vers HTTPS (`443`) dans `www1.conf` :**

```apache title="/etc/apache2/sites-available/www1.conf"
<VirtualHost *:80>
    ServerName www1.dortmund.cub.sioplc.fr
    ServerAlias www1

    # Redirection permanente 301 (mod_alias) vers le canal chiffré HTTPS
    Redirect permanent / https://www1.dortmund.cub.sioplc.fr/
</VirtualHost>
```

4.4. **Activation des sites et rechargement d'Apache :**

```bash
sudo a2ensite www1-ssl.conf
sudo a2ensite www1.conf
sudo apache2ctl configtest
sudo systemctl restart apache2
```

---

## 5. Adaptation HTTPS dans WordPress (`wp-config.php`)

Sans mise à jour des URLs dans WordPress, le CMS continue de rediriger les requêtes vers `http://`, ce qui provoque une boucle de redirection infinie (`ERR_TOO_MANY_REDIRECTS`) avec Apache ainsi que du contenu mixte (*Mixed Content*).

Ajouter ces directives dans `/var/www/html/www1/wp-config.php` (avant `require_once ABSPATH . 'wp-settings.php';`) :

```php title="/var/www/html/www1/wp-config.php (constantes HTTPS)"
// Passage en HTTPS et chiffrement obligatoire de l'interface d'administration (/wp-admin)
define( 'WP_HOME', 'https://www1.dortmund.cub.sioplc.fr' );
define( 'WP_SITEURL', 'https://www1.dortmund.cub.sioplc.fr' );
define( 'FORCE_SSL_ADMIN', true );
```

*(Si des articles ou médias préexistants contiennent des URLs absolues en `http://`, mettre à jour la base avec WP-CLI : `wp search-replace 'http://www1.dortmund.cub.sioplc.fr' 'https://www1.dortmund.cub.sioplc.fr'`.)*

---

## 6. Pare-feu local UFW et Stormshield

Le site vitrine `www1` devant rester accessible aux clients (VLAN 10, VLAN 20 et accès externes, à l'image de la règle `80/tcp ALLOW IN Anywhere`), l'accès HTTPS `443/tcp` doit être autorisé vers `192.36.4.21` sur l'interface `ens18` :

```bash
# Autoriser le trafic HTTPS vers www1 (clients VLAN 10, VLAN 20 et accès externes)
sudo ufw allow in on ens18 \
  to 192.36.4.21 \
  port 443 proto tcp \
  comment 'CUB - HTTPS www1 (WordPress)'

# Contrôle de la table UFW active
sudo ufw status numbered
```

```text title="Résultat attendu de la table UFW sur ServeurWeb1 (192.36.4.21)"
Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 22/tcp                     ALLOW IN    192.168.4.192/28           # SSH depuis VLAN 20 Admin
[ 2] 22/tcp                     ALLOW IN    192.168.4.208/29           # SSH depuis VLAN 53 Bastion
[ 3] 80/tcp                     ALLOW IN    Anywhere                   # HTTP Apache
[ 4] 192.36.4.21 443/tcp on ens18 ALLOW IN    192.168.4.192/28           # CUB - HTTPS scanner1 depuis VLAN20
[ 5] 80/tcp (v6)                ALLOW IN    Anywhere (v6)              # HTTP Apache
[ 6] 192.36.4.21 443/tcp on ens18 ALLOW IN    Anywhere                   # CUB - HTTPS www1 (WordPress)
```

> [!NOTE]
> Ajouter la règle `Passer` sur le port `https` (TCP `443`) vers `MACHINE_WEB1` dans le pare-feu **Stormshield (`STORMSHIELD01`)** (cf. [Filtrage Stormshield ServeurWeb1](firewall-wordpress.md)).

---

## 7. Validation TLS, SNI et limites du certificat auto-signé

7.1. **Test de validation TLS et sélection SNI multi-hôtes :**

```bash
# Test de la réponse HTTPS sur www1 avec vérification du certificat local
curl -I --cacert /etc/ssl/certs/www1.crt https://www1.dortmund.cub.sioplc.fr

# Vérification de la sélection SNI distincte pour chaque VirtualHost sur le port 443
openssl s_client -connect 192.36.4.21:443 -servername www1.dortmund.cub.sioplc.fr </dev/null 2>/dev/null | openssl x509 -noout -subject
openssl s_client -connect 192.36.4.21:443 -servername scanner1.dortmund.cub.sioplc.fr </dev/null 2>/dev/null | openssl x509 -noout -subject
```

- **Impact face au sniffing :** Sous Wireshark, les requêtes et formulaires de connexion WordPress deviennent des segments `Application Data` chiffrés sous TLS 1.2/1.3.
- **Limite face à un MITM actif (*SSL Intercept* / *SSL Stripping*) :** Un certificat auto-signé n'étant pas signé par une autorité de certification reconnue, un attaquant peut présenter son propre faux certificat à l'utilisateur. Pour un site vitrine accessible par des clients externes, l'utilisation d'un certificat signé par une **AC publique reconnue (ex : Let's Encrypt)** et l'activation de **HSTS** sont recommandées en production.
