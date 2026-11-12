---
description: "Procédure d'installation et de configuration de la pile LAMP (Apache2, MariaDB et PHP 8) sur Debian en DMZ"
---

# Installation et Configuration d'Apache2, MariaDB et PHP (Pile LAMP)

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** Amine
> - **Date :** 15/10/2026
> - **Domaine :** Services Web (LAMP - Apache2 & MariaDB)

---

## 1. Sommaire

- [2. Contexte](#2-contexte)
- [3. Installation et configuration d'Apache 2](#3-installation-et-configuration-dapache-2)
- [4. Durcissement du serveur Apache 2](#4-durcissement-du-serveur-apache-2)
- [5. Installation et configuration de MariaDB](#5-installation-et-configuration-de-mariadb)
- [6. Installation de PHP 8 et des dépendances applicatives](#6-installation-de-php-8-et-des-dependances-applicatives)
- [7. Pare-feu local et suite du déploiement](#7-pare-feu-local-et-suite-du-deploiement)

---

## 2. Contexte

Au sein de l'infrastructure CUB de l'agence de Dortmund, les services Web de l'entreprise sont hébergés dans la zone démilitarisée (**DMZ - VLAN 84 : `192.36.4.0/24`**), notamment sur le serveur **`ServeurWeb1`** (`192.36.4.21/24`).

Ce document détaille l'installation et le paramétrage de la pile logicielle **LAMP** (Linux, Apache2, MariaDB, PHP 8) constituant le socle commun des deux hôtes virtuels (VirtualHosts) hébergés sur ce serveur :

1. **Site Vitrine WordPress (`www1.dortmund.cub.sioplc.fr`)** : [Configuration du site vitrine WordPress](config-wordpress.md)
2. **Scanner Réseau d'Exploitation (`scanner1.dortmund.cub.sioplc.fr`)** : [Configuration et sécurisation du scanner réseau](config-scanner.md)

---

## 3. Installation et configuration d'Apache 2

3.1. **Installation du serveur HTTP Apache 2.** Déploiement du service Web et activation de son démarrage automatique.

```bash
apt update && apt install -y apache2
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
- `authz_host` : Permet le contrôle d'accès basé sur les adresses IP ou blocs CIDR des clients (`Require ip`).
- `headers` : Autorise la manipulation et l'injection des en-têtes HTTP de sécurité.

3.3. **Désactivation de l'hôte virtuel par défaut.** Neutralisation de la page d'accueil par défaut d'Apache avant le déploiement des VirtualHosts dédiés.

```bash
a2dissite 000-default.conf
apache2ctl configtest
systemctl reload apache2
```

- `a2dissite 000-default.conf` : Désactive l'hôte virtuel par défaut pour éviter toute réponse non maîtrisée.
- `apache2ctl configtest` : Valide la syntaxe globale des fichiers de configuration Apache.

---

## 4. Durcissement du serveur Apache 2

4.1. **Masquage des informations serveur et ajout des en-têtes de sécurité.** Modification du fichier `/etc/apache2/conf-available/security.conf` pour neutraliser la divulgation de version et protéger les navigateurs clients :

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

- `ServerTokens Prod` : Masque la version précise d'Apache et du système dans les en-têtes HTTP (`Server: Apache`).
- `ServerSignature Off` : Supprime la signature du serveur en pied des pages d'erreur HTTP.
- `X-Frame-Options "SAMEORIGIN"` : Bloque l'inclusion des pages du site dans des iframes externes (protection anti-clickjacking).
- `X-Content-Type-Options "nosniff"` : Empêche le reniflage de type MIME par les navigateurs.
- `X-XSS-Protection "1; mode=block"` : Active le filtrage XSS côté navigateur sur les anciens clients.

---

## 5. Installation et configuration de MariaDB

5.1. **Installation et initialisation du SGBD MariaDB.** Mise en place du moteur de base de données relationnelle et exécution du script de sécurisation.

```bash
apt install -y mariadb-server mariadb-client
systemctl enable mariadb
systemctl start mariadb
mariadb-secure-installation
```

- `apt install -y mariadb-server mariadb-client` : Installe le serveur de base de données MariaDB et son client en ligne de commande.
- `mariadb-secure-installation` : Lance l'assistant de sécurisation initiale (définition du mot de passe `root`, suppression des comptes anonymes, désactivation de l'accès `root` à distance, purge de la base de test).

5.2. **Création de la base de données et du compte de service WordPress.** Connexion à l'invite MariaDB et création des objets relationnels dédiés au futur site vitrine.

```bash
mariadb -u root -p
```

```sql
CREATE DATABASE wordpress_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wp_admin'@'localhost' IDENTIFIED BY 'AdminCUB2026!';
GRANT ALL PRIVILEGES ON wordpress_db.* TO 'wp_admin'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

- `CREATE DATABASE wordpress_db` : Initialise la base de données WordPress avec l'encodage `utf8mb4` (support complet UTF-8).
- `CREATE USER 'wp_admin'@'localhost'` : Crée l'utilisateur applicatif strictement restreint aux connexions locales.
- `GRANT ALL PRIVILEGES` : Assigne l'ensemble des privilèges sur la base `wordpress_db` à l'utilisateur `wp_admin`.
- `FLUSH PRIVILEGES` : Force l'application immédiate des modifications de privilèges en mémoire.

---

## 6. Installation de PHP 8 et des dépendances applicatives

6.1. **Déploiement de l'interpréteur PHP et des bibliothèques requises.** Installation des paquets nécessaires au fonctionnement de WordPress et de l'outil de diagnostic réseau.

```bash
apt install -y php libapache2-mod-php php-mysql php-curl php-gd \
               php-mbstring php-xml php-xmlrpc php-soap php-intl php-zip
systemctl restart apache2
```

- `libapache2-mod-php` : Module d'intégration de l'interpréteur PHP dans le serveur Web Apache.
- `php-mysql` : Connecteur PHP permettant l'interaction avec le SGBD MariaDB.
- `php-curl`, `php-gd`, `php-xml`, `php-mbstring`, `php-intl`, `php-zip` : Extensions requises pour l'exécution du CMS WordPress, le traitement des médias et les appels réseau.

---

## 7. Pare-feu local et suite du déploiement

7.1. **Sécurisation des flux via UFW.** Avant d'exposer les applications, le pare-feu local UFW doit autoriser uniquement les flux nécessaires (HTTP `80/tcp` et SSH restreint aux VLANs d'administration) :

$\rightarrow$ Consulter la procédure dédiée : [Installation et configuration du pare-feu UFW](../../securite/ufw/installation-configuration-ufw.md).

7.2. **Déploiement des hôtes virtuels.** Poursuivre la mise en service avec les deux procédures applicatives :

- [Configuration du site vitrine WordPress (VHOST www1)](config-wordpress.md)
- [Configuration et sécurisation du scanner réseau (VHOST scanner1)](config-scanner.md)
