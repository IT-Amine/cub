---
description: "Procédure de déploiement, configuration et sécurisation du site vitrine WordPress (VHOST www1) en DMZ"
---

# Configuration du Site Vitrine WordPress (VHOST www1)

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** Amine
> - **Date :** 15/10/2026
> - **Domaine :** Services Web (WordPress)

---

## 1. Sommaire

- [2. Contexte et prérequis](#2-contexte-et-prerequis)
- [3. Déploiement des sources et attribution des permissions](#3-deploiement-des-sources-et-attribution-des-permissions)
- [4. Configuration applicative et durcissement (wp-config.php)](#4-configuration-applicative-et-durcissement-wp-configphp)
- [5. Configuration de l'hôte virtuel Apache (www1.conf)](#5-configuration-de-lhote-virtuel-apache-www1conf)
- [6. Déclaration DNS autoritaire Bind9](#6-declaration-dns-autoritaire-bind9)
- [7. Configuration du pare-feu local (UFW)](#7-configuration-du-pare-feu-local-ufw)
- [8. Validation et recette des accès](#8-validation-et-recette-des-acces)

---

## 2. Contexte et prérequis

Au sein de l'infrastructure CUB de l'agence de Dortmund, le serveur Web **`ServeurWeb1`** (`192.36.4.21/24`) situé dans la zone démilitarisée (**DMZ - VLAN 84**) héberge le portail vitrine de l'agence sous **WordPress**, accessible via le FQDN `www1.dortmund.cub.sioplc.fr`.

> [!important] Prérequis obligatoires
> - La pile LAMP (Apache 2, MariaDB, PHP 8) ainsi que la base de données `wordpress_db` et l'utilisateur `wp_admin` doivent être préalablement déployés : [Installation et configuration d'Apache2, MariaDB et PHP](installation-apache2-mariadb.md).
> - Le pare-feu hôte UFW doit autoriser le trafic HTTP entrant (`80/tcp`) : [Procédure de configuration UFW (`docs/securite/ufw/installation-configuration-ufw.md`)](../../securite/ufw/installation-configuration-ufw.md).

---

## 3. Déploiement des sources et attribution des permissions

3.1. **Récupération et extraction de WordPress.** Téléchargement de l'archive officielle et déploiement dans la racine Web `/var/www/html/www1`.

```bash
cd /tmp
wget https://wordpress.org/latest.tar.gz
tar -xzf latest.tar.gz
mkdir -p /var/www/html/www1
cp -r /tmp/wordpress/* /var/www/html/www1/
```

- `wget https://wordpress.org/latest.tar.gz` : Télécharge la dernière version stable de WordPress.
- `tar -xzf latest.tar.gz` : Décompresse l'archive téléchargée.
- `cp -r /tmp/wordpress/* /var/www/html/www1/` : Copie les fichiers sources dans la racine du site vitrine.

3.2. **Attribution des permissions système.** Assignation de la propriété à l'utilisateur Apache `www-data` et application des droits d'accès minimaux requis.

```bash
chown -R www-data:www-data /var/www/html/www1
find /var/www/html/www1/ -type d -exec chmod 755 {} \;
find /var/www/html/www1/ -type f -exec chmod 644 {} \;
```

- `chown -R www-data:www-data` : Assigne le propriétaire et le groupe d'exécution du serveur Web.
- `chmod 755` sur les répertoires : Accorde les droits de lecture et d'exécution à tous, et d'écriture au propriétaire.
- `chmod 644` sur les fichiers : Accorde les droits de lecture à tous, et d'écriture au propriétaire.

---

## 4. Configuration applicative et durcissement (`wp-config.php`)

4.1. **Externalisation des secrets via `.env` et configuration de `wp-config.php`.** Isolation des identifiants de base de données et désactivation de l'éditeur de fichiers intégré pour limiter l'impact d'une compromission.

```bash
cd /var/www/html/www1
cp wp-config-sample.php wp-config.php
```

Éditer `/var/www/html/www1/wp-config.php` pour charger les variables depuis le fichier `.env` et bloquer l'édition de code depuis le panneau d'administration :

```php title="/var/www/html/www1/wp-config.php"
// Chargement des variables d'environnement depuis le fichier .env
if ( file_exists( __DIR__ . '/.env' ) ) {
    $env = parse_ini_file( __DIR__ . '/.env' );
    define( 'DB_NAME',     $env['DB_NAME'] );
    define( 'DB_USER',     $env['DB_USER'] );
    define( 'DB_PASSWORD', $env['DB_PASSWORD'] );
}

// Durcissement : désactivation de l'éditeur de thèmes/extensions intégré
define('DISALLOW_FILE_EDIT', true);
```

4.2. **Création du fichier `.env` et verrouillage des droits.**

```bash
sudo tee /var/www/html/www1/.env <<EOF
DB_NAME=wordpress_db
DB_USER=wp_admin
DB_PASSWORD=AdminCUB2026!
EOF

chmod 640 /var/www/html/www1/wp-config.php /var/www/html/www1/.env
chown www-data:www-data /var/www/html/www1/wp-config.php /var/www/html/www1/.env
```

- `chmod 640` : Restreint la lecture des fichiers contenant les identifiants de base de données à l'administrateur (`root`) et au service Web (`www-data`).
- `DISALLOW_FILE_EDIT` : Empêche toute injection de code PHP malveillant via l'interface d'administration WordPress.

---

## 5. Configuration de l'hôte virtuel Apache (`www1.conf`)

5.1. **Création du fichier VirtualHost.** Configuration d'Apache pour répondre aux requêtes destinées au FQDN `www1.dortmund.cub.sioplc.fr`.

```apache title="/etc/apache2/sites-available/www1.conf"
<VirtualHost *:80>
    ServerName www1.dortmund.cub.sioplc.fr
    ServerAlias www1
    ServerAdmin webmaster@cub.sioplc.fr
    DocumentRoot /var/www/html/www1

    <Directory /var/www/html/www1>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/www1_error.log
    CustomLog ${APACHE_LOG_DIR}/www1_access.log combined
</VirtualHost>
```

- `ServerName www1.dortmund.cub.sioplc.fr` : Définit le nom d'hôte principal traité par cet hôte virtuel.
- `DocumentRoot /var/www/html/www1` : Spécifie le répertoire racine hébergeant le CMS WordPress.
- `AllowOverride All` : Active la prise en charge des directives de réécriture d'URL du fichier `.htaccess`.
- `Options -Indexes` : Désactive le listage automatique des répertoires en l'absence de fichier index.

5.2. **Activation et rechargement d'Apache.**

```bash
a2ensite www1.conf
apache2ctl configtest
systemctl reload apache2
```

- `a2ensite www1.conf` : Crée le lien symbolique d'activation dans `/etc/apache2/sites-enabled/`.
- `apache2ctl configtest` : Contrôle la validité de la syntaxe avant le rechargement à chaud.

---

## 6. Déclaration DNS autoritaire Bind9

6.1. **Ajout de l'enregistrement de type `A`.** Sur le serveur DNS faisant autorité maître (`ns0` sur `192.36.4.10`), ajouter l'entrée pointant vers `192.36.4.21` dans le fichier de zone `/etc/bind/db.dortmund.cub.sioplc.fr` (en pensant à incrémenter le numéro de série SOA) :

```text title="/etc/bind/db.dortmund.cub.sioplc.fr"
; Enregistrement ServeurWeb1 (WordPress)
www1        IN  A   192.36.4.21
```

6.2. **Validation et rechargement de la zone DNS.**

```bash
named-checkzone dortmund.cub.sioplc.fr /etc/bind/db.dortmund.cub.sioplc.fr
rndc reload
```

- `named-checkzone` : Valide l'intégrité syntaxique du fichier de zone.
- `rndc reload` : Recharge la zone et déclenche la notification vers le serveur esclave (`ns1`).

---

## 7. Configuration du pare-feu local (UFW)

7.1. **Exposition contrôlée du service Web.** Le serveur `ServeurWeb1` étant exposé en DMZ, le pare-feu hôte UFW doit être activé et autoriser uniquement le port HTTP `80/tcp` (en plus du SSH restreint aux réseaux d'administration) :

```bash
sudo ufw allow 80/tcp comment 'HTTP Apache'
```

> [!note] Documentation complète du pare-feu UFW
> L'ensemble de la procédure d'installation, de définition des politiques par défaut, de restriction SSH (VLAN 20 et Bastion VLAN 53) et d'activation est détaillé dans :
>
> - **Fichier UFW :** [`docs/securite/ufw/installation-configuration-ufw.md`](../../securite/ufw/installation-configuration-ufw.md)

---

## 8. Validation et recette des accès

8.1. **Matrice des tests d'acceptation pour WordPress (`www1`) :**

| N° Test | Objectif du Test | Équipement Source / VLAN | Action Réalisée | Résultat Attendu |
| :--- | :--- | :--- | :--- | :--- |
| **T1** | Résolution DNS de `www1` | Poste Client (VLAN 10) | `nslookup www1.dortmund.cub.sioplc.fr` | L'adresse `192.36.4.21` est retournée avec succès. |
| **T2** | Accès au site WordPress | Navigateur Web quelconque | Navigation vers `http://www1.dortmund.cub.sioplc.fr` | Affichage du site vitrine WordPress (Code HTTP **200 OK**). |
| **T3** | Vérification UFW | Console `ServeurWeb1` | `sudo ufw status verbose` | Règle `80/tcp ALLOW IN` active et SSH limité aux VLAN 20/53. |
