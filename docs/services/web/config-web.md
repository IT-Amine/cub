---
description: "Procédure de configuration d'un serveur Web LAMP et d'hôtes virtuels (WordPress et Scanner) en DMZ"
---

# BLOC 2 - Configuration d'un Serveur Web LAMP et Hôtes Virtuels en DMZ

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** INFRAMINE
> - **Date :** 15/10/2026
> - **Domaine :** Services Web (LAMP)

---

## 1. Sommaire

- [2. Contexte](#2-contexte)
- [3. Déploiement de la pile LAMP (Linux, Apache, MariaDB, PHP 8)](#3-deploiement-de-la-pile-lamp-linux-apache-mariadb-php-8)
- [4. Configuration de la base de données MariaDB pour WordPress](#4-configuration-de-la-base-de-donnees-mariadb-pour-wordpress)
- [5. Configuration du site vitrine WordPress (VHOST www1)](#5-configuration-du-site-vitrine-wordpress-vhost-www1)
- [6. Configuration et sécurisation du scanner réseau (VHOST scanner1)](#6-configuration-et-securisation-du-scanner-reseau-vhost-scanner1)
- [7. Déclaration des enregistrements DNS autoritaires Bind9](#7-declaration-des-enregistrements-dns-autoritaires-bind9)
- [8. Validation et recette des accès](#8-validation-et-recette-des-acces)
- [9. Analyse de sécurité et durcissement avancé](#9-analyse-de-securite-et-durcissement-avance)

---

## 2. Contexte

À la suite de l'internalisation de la gestion du nom de domaine d'entreprise, l'agence CUB de Dortmund héberge ses services Web au sein de la zone démilitarisée (DMZ - VLAN 84).

Cette procédure détaille exclusivement la mise en œuvre applicative sur le serveur **`ServeurWeb1`** (`192.36.4.21/24`), hébergeant deux sites par hôtes virtuels Apache (**VirtualHosts**) :
1. **Site Vitrine WordPress (`www1.dortmund.cub.sioplc.fr`) :** Portail CMS de l'agence alimenté par MariaDB et PHP 8.
2. **Scanner Réseau d'Exploitation (`scanner1.dortmund.cub.sioplc.fr`) :** Outil de diagnostic interne protégé par une double sécurité obligatoire :
   - Une **authentification HTTP basique** gérée par le module Apache `mod_auth_basic` avec fichier de mots de passe `.htpasswd`.
   - Un **filtrage d'adresses IP** géré par `mod_authz_host` autorisant **exclusivement le VLAN Administration (VLAN 20 : `192.168.4.192/28`)**, tout autre réseau étant rejeté avec le code HTTP **403 Forbidden**.

---

## 3. Déploiement de la pile LAMP (Linux, Apache, MariaDB, PHP 8)

3.1. **Installation du serveur HTTP Apache 2.** Déploiement du service Web et activation de son démarrage automatique.

```bash
apt install -y apache2
systemctl enable apache2
systemctl start apache2
```

- `apt install -y apache2` : Installe le serveur HTTP Apache 2.
- `systemctl enable apache2` : Active le démarrage automatique du service au démarrage du système.
- `systemctl start apache2` : Démarre immédiatement le service Apache.

3.2. **Activation des modules Apache requis.** Chargement des modules nécessaires aux hôtes virtuels, aux contrôles d'accès et à la sécurité.

```bash
a2enmod rewrite auth_basic authn_file authz_host headers
systemctl restart apache2
```

- `rewrite` : Permet la réécriture des URLs nécessaire aux permaliens WordPress.
- `auth_basic` : Active l'authentification HTTP basique.
- `authn_file` : Permet d'authentifier les utilisateurs via un fichier de stockage chiffré (`.htpasswd`).
- `authz_host` : Permet le contrôle d'accès basé sur les adresses IP ou blocs CIDR des clients.
- `headers` : Autorise la manipulation et l'injection des en-têtes HTTP de sécurité.

3.3. **Installation et initialisation du SGBD MariaDB.** Mise en place du moteur de base de données relationnelle.

```bash
apt install -y mariadb-server mariadb-client
systemctl enable mariadb
systemctl start mariadb
mariadb-secure-installation
```

- `apt install -y mariadb-server` : Installe le serveur de base de données MariaDB.
- `mysql_secure_installation` : Lance le script de sécurisation initiale (suppression des comptes anonymes, désactivation du root à distance, purge de la base test).

3.4. **Installation de PHP 8 et des dépendances applicatives.** Déploiement de l'interpréteur PHP et des bibliothèques requises par WordPress.

```bash
apt install -y php libapache2-mod-php php-mysql php-curl php-gd \
               php-mbstring php-xml php-xmlrpc php-soap php-intl php-zip
```

- `libapache2-mod-php` : Module d'intégration de PHP au serveur Web Apache.
- `php-mysql` : Module d'interaction avec le SGBD MariaDB.
- `php-curl`, `php-gd`, `php-xml`, `php-mbstring`, `php-zip` : Bibliothèques fonctionnelles requises pour l'exécution du CMS WordPress.

---

## 4. Configuration de la base de données MariaDB pour WordPress

4.1. **Création du schéma de base de données et du compte de service.** Connexion à l'invite MariaDB et création des objets relationnels dédiés.

```bash
mariadb -u root -p
```

```sql
CREATE DATABASE wordpress_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wp_admin'@'localhost' IDENTIFIED BY 'MDP_BITWARDEN';
GRANT ALL PRIVILEGES ON wordpress_db.* TO 'wp_admin'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

- `CREATE DATABASE wordpress_db` : Initialise la base de données WordPress avec l'encodage `utf8mb4`.
- `CREATE USER 'wp_admin'@'localhost'` : Crée l'utilisateur applicatif restreint aux connexions locales.
- `GRANT ALL PRIVILEGES` : Assigne l'ensemble des privilèges sur la base `wordpress_db` à l'utilisateur `wp_admin`.
- `FLUSH PRIVILEGES` : Force l'application immédiate des modifications de privilèges en mémoire.

---

## 5. Configuration du site vitrine WordPress (VHOST www1)

5.1. **Déploiement des fichiers sources de WordPress.** Récupération de l'archive officielle et déploiement dans le répertoire cible `/var/www/html/www1`.

```bash
cd /tmp
wget https://wordpress.org/latest.tar.gz
tar -xzf latest.tar.gz
mkdir -p /var/www/html/www1
cp -r /tmp/wordpress/* /var/www/html/www1/
```

- `wget https://wordpress.org/latest.tar.gz` : Télécharge la dernière version stable de WordPress.
- `tar -xzf latest.tar.gz` : Décompresse le paquet téléchargé.
- `cp -r /tmp/wordpress/* /var/www/html/www1/` : Copie les fichiers dans la racine web du site vitrine.

5.2. **Attribution des permissions système.** Assignation de la propriété à l'utilisateur Apache `www-data` et application des droits d'accès minimaux requis.

```bash
chown -R www-data:www-data /var/www/html/www1
find /var/www/html/www1/ -type d -exec chmod 755 {} \;
find /var/www/html/www1/ -type f -exec chmod 644 {} \;
```

- `chown -R www-data:www-data` : Assigne le propriétaire et le groupe d'exécution du serveur web.
- `chmod 755` sur les répertoires : Accorde les droits de lecture et d'exécution à tous, et d'écriture au propriétaire.
- `chmod 644` sur les fichiers : Accorde les droits de lecture à tous, et d'écriture au propriétaire.

5.3. **Paramétrage du fichier de configuration applicative.** Configuration des paramètres de connexion à la base de données dans le fichier `wp-config.php`.

```bash
cd /var/www/html/www1
cp wp-config-sample.php wp-config.php
nano wp-config.php

// Chargement des variables d'environnement depuis le fichier .env
if ( file_exists( __DIR__ . '/.env' ) ) {
    $env = parse_ini_file( __DIR__ . '/.env' );
    define( 'DB_NAME',     $env['DB_NAME'] );
    define( 'DB_USER',     $env['DB_USER'] );
    define( 'DB_PASSWORD', $env['DB_PASSWORD'] );
}
```

```bash
sudo tee .env <<EOF
DB_NAME=wordpress_db
DB_USER=wp_admin
DB_PASSWORD=MDP_BITWARDEN
EOF

chmod 640 wp-config.php
chown www-data:www-data wp-config.php
```

- `chmod 640 wp-config.php` : Restreint la lecture du fichier contenant les mots de passe de base de données à l'administrateur et au service Web.

5.4. **Configuration de l'hôte virtuel Apache (`www1.conf`).** Création du fichier de déclaration VirtualHost pour intercepter le FQDN `www1.dortmund.cub.sioplc.fr`.

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

- `ServerName www1.dortmund.cub.sioplc.fr` : Définit le FQDN traité par cet hôte virtuel.
- `DocumentRoot /var/www/html/www1` : Spécifie le répertoire racine hébergeant l'application.
- `AllowOverride All` : Active la prise en charge des directives de réécriture du fichier `.htaccess`.
- `Options -Indexes` : Désactive l'affichage de l'arborescence des dossiers en l'absence de fichier index.

5.5. **Activation du site vitrine.** Activation de l'hôte virtuel dans la configuration d'Apache.

```bash
a2ensite www1.conf
```

- `a2ensite www1.conf` : Crée le lien symbolique d'activation vers `/etc/apache2/sites-enabled/`.

---

## 6. Configuration et sécurisation du scanner réseau (VHOST scanner1)

6.1. **Déploiement de l'outil de diagnostic réseau.** Création du répertoire `/var/www/html/scanner` et écriture de la page de scan PHP.

```bash
mkdir -p /var/www/html/scanner
```

```php title="/var/www/html/scanner/index.php"
<?php
/**
 * Script de diagnostic réseau - Outil d'administration CUB Dortmund
 * Permet d'exécuter un test ping sécurisé vers une cible du réseau.
 */

// Récupération de l'adresse IP du client distant pour l'audit de sécurité
$client_ip = $_SERVER['REMOTE_ADDR'];

// Récupération de l'utilisateur authentifié (via HTTP Basic Auth ou proxy), défini sur 'Anonyme' par défaut
$auth_user = isset($_SERVER['PHP_AUTH_USER']) ? htmlspecialchars($_SERVER['PHP_AUTH_USER']) : 'Anonyme';
$result = "";

// Vérification de la soumission du formulaire et de la non-vacuité du champ cible
if (isset($_POST['target']) && !empty($_POST['target'])) {
    $target = trim($_POST['target']);
    
    // VALIDATION STRICTE : Empêche les injections de commandes en vérifiant 
    // soit qu'il s'agit d'une adresse IP valide, soit d'un nom d'hôte alphanumérique sécurisé
    if (filter_var($target, FILTER_VALIDATE_IP) || preg_match('/^[a-zA-Z0-9.-]+$/', $target)) {
        
        // PROTECTION SUPPLÉMENTAIRE : Échappe les caractères spéciaux pour sécuriser l'exécution de la commande système
        $safe_target = escapeshellarg($target);
        
        // Exécution de la commande ping (4 paquets, timeout de 2 secondes) de manière sécurisée
        $result = shell_exec("ping -c 4 -W 2 " . $safe_target);
    } else {
        // En cas de tentative d'injection ou de format incorrect
        $result = "Erreur : Format de cible non valide.";
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Scanner Réseau - Administration CUB</title>
    <style>
        /* Styles de mise en page pour l'interface d'administration (Thème sombre) */
        body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 40px; }
        .card { background: #1e293b; padding: 25px; border-radius: 8px; border: 1px solid #334155; max-width: 800px; margin: auto; }
        h1 { color: #38bdf8; font-size: 1.4em; }
        .meta { color: #94a3b8; font-size: 0.9em; margin-bottom: 20px; }
        input[type=text] { width: 70%; padding: 10px; border-radius: 4px; border: 1px solid #475569; background: #020617; color: #fff; }
        input[type=submit] { padding: 10px 20px; background: #0284c7; color: white; border: none; border-radius: 4px; cursor: pointer; }
        pre { background: #020617; padding: 15px; border-radius: 6px; color: #4ade80; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Outil de Diagnostic Réseau - CUB Dortmund</h1>
        
        <!-- Bloc d'affichage des métadonnées de traçabilité (Utilisateur et IP source) -->
        <div class="meta">
            Utilisateur authentifié : <strong><?php echo $auth_user; ?></strong> | IP source : <strong><?php echo $client_ip; ?></strong> (VLAN Administration)
        </div>
        
        <!-- Formulaire de saisie de la cible à tester -->
        <form method="POST">
            <label for="target">Adresse IP ou équipement à tester :</label><br><br>
            <input type="text" id="target" name="target" placeholder="ex: 192.168.4.190" required>
            <input type="submit" value="Lancer le Ping">
        </form>

        <!-- Affichage conditionnel des résultats du diagnostic -->
        <?php if (!empty($result)): ?>
            <h3>Résultat du diagnostic :</h3>
            <!-- Utilisation de htmlspecialchars pour contrer les failles XSS lors de l'affichage du retour système -->
            <pre><?php echo htmlspecialchars($result); ?></pre>
        <?php endif; ?>
    </div>
</body>
</html>
```

```bash
chown -R www-data:www-data /var/www/html/scanner
chmod -R 755 /var/www/html/scanner
```

- `chown -R www-data:www-data` : Assigne la propriété des fichiers de scan au service Web.
- `chmod -R 755` : Autorise la lecture et l'exécution des scripts par le serveur Apache.

6.2. **Génération du fichier d'authentification HTTP basique (`.htpasswd`).** Création du compte utilisateur autorisé et protection du fichier de stockage.

```bash
htpasswd -c /etc/apache2/.htpasswd admin_tech
chown root:www-data /etc/apache2/.htpasswd
chmod 640 /etc/apache2/.htpasswd
```

- `htpasswd -c /etc/apache2/.htpasswd admin_tech` : Crée le fichier et génère le hachage cryptographique du mot de passe de l'utilisateur `admin_tech`.
- `chmod 640 /etc/apache2/.htpasswd` : Empêche la lecture du fichier aux utilisateurs ordinaires du système.

6.3. **Configuration de l'hôte virtuel Apache avec restriction IP et authentification (`scanner1.conf`).** Création de l'hôte virtuel cumulant l'obligation d'authentification et le filtrage réseau strict réservé au **VLAN 20 (Administration : `192.168.4.192/28`)** :

```apache title="/etc/apache2/sites-available/scanner1.conf"
<VirtualHost *:80>
    ServerName scanner1.dortmund.cub.sioplc.fr
    ServerAlias scanner1
    ServerAdmin webmaster@cub.sioplc.fr
    DocumentRoot /var/www/html/scanner

    <Directory /var/www/html/scanner>
        Options -Indexes +FollowSymLinks
        AllowOverride None

        <RequireAll>
            # Condition 1 : Restriction stricte au VLAN 20 (Administration)
            Require ip 192.168.4.192/28

            # Condition 2 : Authentification HTTP basique obligatoire
            AuthType Basic
            AuthName "Acces Restreint - Administration CUB"
            AuthUserFile /etc/apache2/.htpasswd
            Require valid-user
        </RequireAll>
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/scanner1_error.log
    CustomLog ${APACHE_LOG_DIR}/scanner1_access.log combined
</VirtualHost>
```

- `<RequireAll>` : Exige la validation simultanée de toutes les conditions pour autoriser la consultation.
- `Require ip 192.168.4.192/28` : Bloque tout client n'appartenant pas au sous-réseau `192.168.4.192/28` (VLAN 20 Administration).
- `AuthType Basic` / `Require valid-user` : Impose la saisie d'un compte valide déclaré dans le fichier `/etc/apache2/.htpasswd`.

6.4. **Activation du site et basculement d'Apache.** Désactivation du site par défaut, activation de l'hôte virtuel et rechargement du service.

```bash
a2dissite 000-default.conf
a2ensite scanner1.conf
apache2ctl configtest
systemctl reload apache2
```

- `a2dissite 000-default.conf` : Désactive l'hôte par défaut pour éviter toute réponse involontaire.
- `a2ensite scanner1.conf` : Active l'hôte virtuel du scanner réseau.
- `apache2ctl configtest` : Valide la syntaxe globale des fichiers de configuration Apache.
- `systemctl reload apache2` : Recharge à chaud la nouvelle configuration.

---

## 7. Déclaration des enregistrements DNS autoritaires Bind9

Pour que les deux sites soient joignables par leurs noms de domaine respectifs, les enregistrements de type `A` sont déclarés sur le serveur DNS faisant autorité (`ns0` sur `192.36.4.10`).

7.1. **Déclaration des enregistrements DNS dans le fichier de zone.** Ajout des entrées pointant vers l'adresse IP `192.36.4.21` de `ServeurWeb1` dans `/var/cache/bind/db.dortmund.cub.sioplc.fr` :

```text title="/etc/bind/zones/db.dortmund.cub.sioplc.fr"
; Enregistrements ServeurWeb1
www1        IN  A   192.36.4.21
scanner1    IN  A   192.36.4.21
```

7.2. **Rechargement de la zone DNS Bind9.** Contrôle de syntaxe de la zone et application immédiate :

```bash
named-checkzone dortmund.cub.sioplc.fr /var/cache/bind/db.dortmund.cub.sioplc.fr
rndc reload
```

- `named-checkzone` : Valide l'intégrité syntaxique du fichier de zone.
- `rndc reload` : Recharge la zone et notifie les serveurs esclaves du changement de numéro de série.

---

## 8. Validation et recette des accès

8.1. **Matrice de validation fonctionnelle et d'accès.** Tests d'acceptation à exécuter pour valider la conformité de la configuration :

| N° Test | Objectif du Test | Équipement Source / VLAN | Action Réalisée | Résultat Attendu |
| :--- | :--- | :--- | :--- | :--- |
| **T1** | Résolution DNS de `www1` | Poste Client (VLAN 10) | `nslookup www1.dortmund.cub.sioplc.fr` | L'adresse `192.36.4.21` est retournée avec succès. |
| **T2** | Résolution DNS de `scanner1` | Poste Admin (VLAN 20) | `nslookup scanner1.dortmund.cub.sioplc.fr` | L'adresse `192.36.4.21` est retournée avec succès. |
| **T3** | Accès au site WordPress | Navigateur Web quelconque | Navigation vers `http://www1.dortmund.cub.sioplc.fr` | Affichage du site WordPress (Code HTTP **200 OK**). |
| **T4** | Accès Scanner depuis VLAN Admin | Poste Admin (`192.168.4.193` - VLAN 20) | Navigation vers `http://scanner1.dortmund.cub.sioplc.fr` | Invite d'authentification $\rightarrow$ saisie `admin_tech` $\rightarrow$ affichage du formulaire (**200 OK**). |
| **T5** | Exécution d'un ping depuis le Scanner | Poste Admin (VLAN 20) | Saisie de la cible `192.168.4.190` dans le formulaire | 4 paquets ICMP exécutés et résultat retourné. |
| **T6** | Rejet du Scanner depuis VLAN Client | Poste Client (`192.168.4.135` - VLAN 10) | Navigation vers `http://scanner1.dortmund.cub.sioplc.fr` | **Accès refusé immédiatement (Code HTTP 403 Forbidden)** sans invite d'authentification. |
| **T7** | Rejet du Scanner avec mauvais mot de passe | Poste Admin (VLAN 20) | Saisie d'identifiants incorrects | Refus d'accès (Code HTTP **401 Unauthorized**). |

---

## 9. Analyse de sécurité et durcissement avancé

9.1. **Correction de la vulnérabilité d'injection de commande shell OS.** Dans un script de diagnostic, la concaténation directe d'une variable non assainie (`shell_exec("ping -c 4 " . $target)`) expose à l'exécution de code arbitraire à distance (RCE) via des caractères de contrôle (`127.0.0.1; cat /etc/passwd`).

Les parades mises en place dans le code de `scanner1` sont :
- `filter_var($target, FILTER_VALIDATE_IP)` : Vérifie que la chaîne correspond rigoureusement à une adresse IP valide.
- `escapeshellarg($target)` : Protège la chaîne avec des apostrophes et échappe les caractères spéciaux shell avant exécution.

9.2. **Durcissement du serveur Apache 2.** Modification du fichier `/etc/apache2/conf-available/security.conf` pour neutraliser la divulgation d'informations :

```apache title="/etc/apache2/conf-available/security.conf"
ServerTokens Prod
ServerSignature Off

Header always set X-Frame-Options "SAMEORIGIN"
Header always set X-Content-Type-Options "nosniff"
Header always set X-XSS-Protection "1; mode=block"
```

```bash
a2enconf security
systemctl reload apache2
```

- `ServerTokens Prod` : Masque la version d'Apache dans les bannières HTTP.
- `ServerSignature Off` : Supprime la signature du serveur des pages d'erreur.
- `X-Frame-Options SAMEORIGIN` : Bloque l'inclusion du site dans des iframes (anti-clickjacking).
- `X-Content-Type-Options nosniff` : Empêche le reniflage de type MIME.

9.3. **Durcissement du CMS WordPress.** Verrouillage de la configuration dans `/var/www/html/www1/wp-config.php` :

```php
define('DISALLOW_FILE_EDIT', true);
```

- `DISALLOW_FILE_EDIT` : Désactive l'éditeur de fichiers intégré dans le panneau d'administration WordPress, empêchant toute injection de code malveillant en cas de compromission d'un compte administrateur.
