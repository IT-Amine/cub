---
description: "Procédure de déploiement, authentification HTTP, filtrage IP et sécurisation du scanner réseau (VHOST scanner1) en DMZ"
---

# Configuration et Sécurisation du Scanner Réseau (VHOST scanner1)

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** Amine
> - **Date :** 15/10/2026
> - **Domaine :** Services Web & Sécurité (Scanner Réseau)

---

## 1. Sommaire

- [2. Contexte et prérequis](#2-contexte-et-prerequis)
- [3. Déploiement de l'outil de diagnostic réseau](#3-deploiement-de-loutil-de-diagnostic-reseau)
- [4. Authentification HTTP basique (.htpasswd)](#4-authentification-http-basique-htpasswd)
- [5. Configuration de l'hôte virtuel Apache avec filtrage IP (scanner1.conf)](#5-configuration-de-lhote-virtuel-apache-avec-filtrage-ip-scanner1conf)
- [6. Déclaration DNS autoritaire Bind9](#6-declaration-dns-autoritaire-bind9)
- [7. Configuration du pare-feu local (UFW)](#7-configuration-du-pare-feu-local-ufw)
- [8. Sécurité et prévention de l'injection de commandes](#8-securite-et-prevention-de-linjection-de-commandes)
- [9. Validation et recette des accès](#9-validation-et-recette-des-acces)

---

## 2. Contexte et prérequis

Au sein de l'infrastructure CUB de l'agence de Dortmund, le serveur Web **`ServeurWeb1`** (`192.36.4.21/24`) situé dans la zone démilitarisée (**DMZ - VLAN 84**) héberge un outil interne de diagnostic réseau (`scanner1.dortmund.cub.sioplc.fr`).

Étant donné la sensibilité de cet outil permettant d'exécuter des requêtes ICMP depuis la DMZ, il est soumis à une **double barrière de sécurité obligatoire** au niveau d'Apache :
1. **Un filtrage d'adresses IP (`mod_authz_host`)** autorisant **exclusivement le VLAN 20 Administration (`192.168.4.192/28`)**, tout autre réseau étant rejeté avec le code HTTP **403 Forbidden**.
2. **Une authentification HTTP basique (`mod_auth_basic`)** s'appuyant sur un fichier de mots de passe chiffrés `.htpasswd`.

> [!important] Prérequis obligatoires
> - La pile LAMP (Apache 2 avec modules `auth_basic`, `authn_file`, `authz_host`, `headers` et PHP 8) doit être installée : [Installation et configuration d'Apache2, MariaDB et PHP](installation-apache2-mariadb.md).
> - Le pare-feu hôte UFW doit être configuré sur le serveur : [Procédure de configuration UFW (`docs/securite/ufw/installation-configuration-ufw.md`)](../../securite/ufw/installation-configuration-ufw.md).

---

## 3. Déploiement de l'outil de diagnostic réseau

3.1. **Création du répertoire applicatif et du script PHP.** Déploiement de l'interface de scan sécurisée dans `/var/www/html/scanner`.

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

3.2. **Attribution des permissions système.**

```bash
chown -R www-data:www-data /var/www/html/scanner
chmod -R 755 /var/www/html/scanner
```

- `chown -R www-data:www-data` : Assigne la propriété des fichiers de scan au service Web.
- `chmod -R 755` : Autorise la lecture et l'exécution des scripts par le serveur Apache.

---

## 4. Authentification HTTP basique (`.htpasswd`)

4.1. **Génération du fichier d'identifiants.** Création du compte d'administration technique autorisé (`admin_tech`) et restriction des droits sur le fichier `.htpasswd`.

```bash
htpasswd -c /etc/apache2/.htpasswd admin_tech
chown root:www-data /etc/apache2/.htpasswd
chmod 640 /etc/apache2/.htpasswd
```

- `htpasswd -c /etc/apache2/.htpasswd admin_tech` : Crée le fichier et génère le hachage du mot de passe pour `admin_tech`.
- `chmod 640 /etc/apache2/.htpasswd` : Restreint la lecture du fichier aux seuls comptes `root` et au groupe du serveur Web `www-data`.

---

## 5. Configuration de l'hôte virtuel Apache avec filtrage IP (`scanner1.conf`)

5.1. **Création du fichier VirtualHost.** Définition de l'hôte virtuel combinant la restriction stricte au **VLAN 20 (Administration : `192.168.4.192/28`)** et l'authentification HTTP basique via `<RequireAll>`.

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

- `<RequireAll>` : Exige la validation simultanée de toutes les conditions pour autoriser l'accès.
- `Require ip 192.168.4.192/28` : Bloque immédiatement tout client n'appartenant pas au sous-réseau d'administration (retourne un code **403 Forbidden** avant même la demande d'identifiants).
- `AuthType Basic` / `Require valid-user` : Impose la saisie d'un compte valide déclaré dans `/etc/apache2/.htpasswd`.

5.2. **Activation du site et rechargement d'Apache.**

```bash
a2dissite 000-default.conf
a2ensite scanner1.conf
apache2ctl configtest
systemctl reload apache2
```

- `a2dissite 000-default.conf` : Désactive l'hôte par défaut.
- `a2ensite scanner1.conf` : Active l'hôte virtuel du scanner réseau.
- `apache2ctl configtest` : Contrôle la syntaxe globale des fichiers de configuration Apache.
- `systemctl reload apache2` : Applique à chaud la nouvelle configuration.

---

## 6. Déclaration DNS autoritaire Bind9

6.1. **Ajout de l'enregistrement de type `A`.** Sur le serveur DNS faisant autorité maître (`ns0` sur `192.36.4.10`), ajouter l'entrée pointant vers `192.36.4.21` dans `/etc/bind/db.dortmund.cub.sioplc.fr` (en incrémentant le numéro de série SOA) :

```text title="/etc/bind/db.dortmund.cub.sioplc.fr"
; Enregistrement ServeurWeb1 (Scanner)
scanner1    IN  A   192.36.4.21
```

6.2. **Validation et rechargement de la zone DNS.**

```bash
named-checkzone dortmund.cub.sioplc.fr /etc/bind/db.dortmund.cub.sioplc.fr
rndc reload
```

- `named-checkzone` : Valide l'intégrité syntaxique du fichier de zone.
- `rndc reload` : Recharge la zone et notifie le serveur esclave (`ns1`).

---

## 7. Configuration du pare-feu local (UFW)

7.1. **Articulation entre UFW et le filtrage Apache.** Le serveur `ServeurWeb1` hébergeant également le site public WordPress sur le port `80/tcp`, le flux HTTP est ouvert sur UFW pour permettre l'accès aux VirtualHosts, tandis que la restriction stricte du scanner au VLAN 20 est assurée au niveau de l'hôte virtuel Apache (`Require ip 192.168.4.192/28`). L'administration SSH demeure strictement filtrée par UFW aux VLANs 20 et 53 :

```bash
sudo ufw allow 80/tcp comment 'HTTP Apache'
```

> [!note] Documentation complète du pare-feu UFW
> L'ensemble de la procédure d'installation, de définition des politiques par défaut, de restriction SSH (VLAN 20 et Bastion VLAN 53) et d'activation est détaillé dans :
>
> - **Fichier UFW :** [`docs/securite/ufw/installation-configuration-ufw.md`](../../securite/ufw/installation-configuration-ufw.md)

---

## 8. Sécurité et prévention de l'injection de commandes

8.1. **Protection contre l'injection de commandes shell OS (RCE).** Dans un outil Web exécutant une commande système (`ping`), la concaténation directe d'une entrée utilisateur (`shell_exec("ping -c 4 " . $target)`) exposerait le serveur à une exécution de code arbitraire à distance via des métacaractères shell (ex : `127.0.0.1; cat /etc/passwd`).

Les contre-mesures implémentées dans `/var/www/html/scanner/index.php` sont :
- `filter_var($target, FILTER_VALIDATE_IP)` / `preg_match('/^[a-zA-Z0-9.-]+$/', $target)` : Validation stricte en liste blanche garantissant que la cible est uniquement une adresse IP valide ou un nom d'hôte alphanumérique.
- `escapeshellarg($target)` : Encapsule l'argument entre apostrophes et neutralise tout caractère spécial avant transmission au shell.
- `htmlspecialchars($result)` : Prévient les failles XSS lors de l'affichage du résultat dans la page HTML.

---

## 9. Validation et recette des accès

9.1. **Matrice des tests d'acceptation pour le Scanner (`scanner1`) :**

| N° Test | Objectif du Test | Équipement Source / VLAN | Action Réalisée | Résultat Attendu |
| :--- | :--- | :--- | :--- | :--- |
| **T1** | Résolution DNS de `scanner1` | Poste Admin (VLAN 20) | `nslookup scanner1.dortmund.cub.sioplc.fr` | L'adresse `192.36.4.21` est retournée avec succès. |
| **T2** | Accès Scanner depuis VLAN Admin | Poste Admin (`192.168.4.193` - VLAN 20) | Navigation vers `http://scanner1.dortmund.cub.sioplc.fr` | Invite d'authentification $\rightarrow$ saisie `admin_tech` $\rightarrow$ affichage du formulaire (**200 OK**). |
| **T3** | Exécution d'un ping depuis le Scanner | Poste Admin (VLAN 20) | Saisie de la cible `192.168.4.190` dans le formulaire | 4 paquets ICMP exécutés et résultat retourné. |
| **T4** | Rejet du Scanner depuis VLAN Client | Poste Client (`192.168.4.135` - VLAN 10) | Navigation vers `http://scanner1.dortmund.cub.sioplc.fr` | **Accès refusé immédiatement (Code HTTP 403 Forbidden)** sans invite d'authentification. |
| **T5** | Rejet du Scanner avec mauvais mot de passe | Poste Admin (VLAN 20) | Saisie d'identifiants incorrects | Refus d'accès (Code HTTP **401 Unauthorized**). |
