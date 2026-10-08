---
description: Déploiement et configuration d'un serveur DNS autoritaire Esclave (ns1)
---

# BLOC 2 - Déploiement DNS Esclave (ns1)

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 01/10/2026</p>
    <p><strong>Contexte :</strong> Mise en place du serveur DNS autoritaire esclave (ns1 - 192.36.4.11) dans la DMZ de l'agence de Dortmund pour la zone dortmund.cub.sioplc.fr, en redondance du serveur maître (ns0) déployé par Louis MEDO.</p>
</div>

---

## 1. Sommaire

- [1. Sommaire](#1-sommaire)
- [2. Contexte](#2-contexte)
- [3. Préparation et sauvegarde](#3-preparation-et-sauvegarde)
- [4. Configuration globale du service](#4-configuration-globale-du-service)
- [5. Déclaration de la zone DNS esclave](#5-declaration-de-la-zone-dns-esclave)
- [6. Configuration de la journalisation](#6-configuration-de-la-journalisation)
- [7. Configuration de la sécurité AppArmor](#7-configuration-de-la-securite-apparmor)
- [8. Vérification et validation](#8-verification-et-validation)
- [9. Retour arrière](#9-retour-arriere)

---

## 2. Contexte

Ce document détaille la procédure de déploiement en production du serveur DNS secondaire (esclave) `ns1` de l'agence de Dortmund. Positionné dans la DMZ avec l'adresse IP `192.36.4.11`, ce serveur assure la haute disponibilité de la résolution de noms pour le domaine `dortmund.cub.sioplc.fr`. Contrairement au serveur maître (`ns0` sur `192.36.4.10`) géré par Louis MEDO, ce serveur ne nécessite pas la création manuelle du fichier de zone. Il est configuré pour rapatrier dynamiquement et automatiquement les enregistrements via un transfert de zone sécurisé (AXFR) depuis le maître.

---

## 3. Préparation et sauvegarde

Avant toute modification de la configuration système, il est impératif d'installer les paquets requis et de générer une sauvegarde de l'état initial pour permettre un retour arrière propre.

### 3.1. Mise à jour et installation de Bind9

Actualisation des dépôts et installation du service DNS.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install bind9 -y
```

### 3.2. Sauvegarde de la configuration

Sécurisation des répertoires avant modification.

```bash
sudo cp -r /etc/bind /etc/bind.bak
sudo cp /etc/apparmor.d/usr.sbin.named /etc/apparmor.d/usr.sbin.named.bak
```

---

## 4. Configuration globale du service

### 4.1. Définition des options globales

Modification du fichier d'options pour définir l'interface d'écoute locale, désactiver la récursivité (prévention des attaques d'amplification) et masquer la version du daemon.

```bash
sudoedit /etc/bind/named.conf.options
```

**Ajouter ou modifier le contenu suivant :**

```text
options {
    // Directory permet de définir où se situe le cache du serveur DNS
    directory "/var/cache/bind";

    // Définit le port et la ou les adresses IPv4 d’écoute du service Bind
    listen-on port 53 { 127.0.0.1; 192.36.4.11; };

    // Recursion permet d'autoriser ou d'interdire la récursivité sur un serveur DNS. 
    // Par défaut un serveur DNS faisant autorité ne doit pas être récursif.
    recursion no;

    // Empêche la diffusion de la version du service Bind utilisée (sécurité).
    version none;
};
```

---

## 5. Déclaration de la zone DNS esclave

> [!info] Synchronisation de la zone
> Le répertoire `/var/cache/bind/` est utilisé en raison des droits d'écriture natifs accordés à l'utilisateur système `bind`. Aucun fichier de zone n'est à créer manuellement : la directive `file` instruit Bind9 de l'emplacement de sauvegarde du fichier compilé à la suite du transfert AXFR.

### 5.1. Ajout de la zone esclave

Configuration de la zone pour désigner ce serveur comme secondaire et pointer vers le serveur maître.

```bash
sudoedit /etc/bind/named.conf.local
```

**Ajouter le bloc suivant :**

```text
zone "dortmund.cub.sioplc.fr" {
    type slave;
    masters { 192.36.4.10; };
    file "/var/cache/bind/db.dortmund.cub.sioplc.fr";
};

// Déclaration de la zone inverse pour le réseau 192.36.4.0/24
zone "4.36.192.in-addr.arpa" {
    type slave;
    masters { 192.36.4.10; };
    file "/var/cache/bind/db.192.36.4";
};
```

---

## 6. Configuration de la journalisation

Afin de monitorer efficacement le service et diagnostiquer la bonne exécution du transfert de zone, une journalisation dédiée est mise en place.

### 6.1. Création du fichier de log

Initialisation du journal et attribution des permissions au compte de service `bind`.

```bash
sudo touch /var/log/bind.log
sudo chown bind:bind /var/log/bind.log
```

### 6.2. Paramétrage du module de log

Configuration de la rétention, du format et du niveau de verbosité.

```bash
sudoedit /etc/bind/named.conf.log
```

**Contenu du fichier :**

```text
logging {
    channel bind_log {
        file "/var/log/bind.log" versions 3 size 100m;
        severity info;
        print-category  yes;
        print-severity  yes;
        print-time      yes;
    };
    category default { bind_log; };
};
```

### 6.3. Inclusion de la configuration

Intégration du module de log à la configuration primaire du service.

```bash
sudoedit /etc/bind/named.conf
```

**Ajouter la ligne d'inclusion à la fin :**

```text
// This is the primary configuration file for the BIND DNS server named.

include "/etc/bind/named.conf.options";
include "/etc/bind/named.conf.local";
include "/etc/bind/named.conf.root-hints";

// Ajout du fichier de parametrage de la journalisation du service BIND
include "/etc/bind/named.conf.log";
```

---

## 7. Configuration de la sécurité AppArmor

> [!warning] Contrôle d'accès MAC
> Sous Debian, AppArmor interdit par défaut au daemon `named` d'écrire en dehors de ses répertoires stricts. Une exception doit être ajoutée pour permettre l'écriture dans `/var/log/bind.log`.

### 7.1. Ajustement des droits

Déclaration de l'autorisation explicite de lecture/écriture pour le fichier de log.

```bash
sudoedit /etc/apparmor.d/usr.sbin.named
```

**Ajouter la ligne suivante :**

```text
# On autorise le daemon Bind 9 à lire et ecrire dans le fichier /var/log/bind.log
/var/log/bind.log rw,
```

### 7.2. Rechargement d'AppArmor

Prise en compte à chaud des nouvelles règles de confinement.

```bash
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.named
sudo systemctl restart apparmor
```

---

## 8. Vérification et validation

### 8.1. Contrôle de la syntaxe globale

Validation des fichiers de configuration. *(Note : l'utilitaire `named-checkconf` est exécuté sans l'option `-z` ici car le fichier de zone n'existe pas encore avant le premier démarrage).*

```bash
sudo named-checkconf
```

### 8.2. Redémarrage et vérification du statut

Application des modifications et contrôle de l'état d'exécution du daemon pour déclencher le premier transfert.

```bash
sudo systemctl restart bind9
sudo systemctl status bind9
```

### 8.3. Validation du transfert de zone (AXFR)

**Objectif :** Confirmer la synchronisation effective depuis le maître `192.36.4.10`.

**Commande :**

```bash
sudo grep -i "transfer" /var/log/bind.log
```

**Résultat attendu :**

```text
etudiant@ns1:~$ sudo grep -i "transfer" /var/log/bind.log
08-Oct-2026 08:15:00.129 xfer-in: info: zone dortmund.cub.sioplc.fr/IN: Transfer started.
08-Oct-2026 08:15:00.129 xfer-in: info: 0x7fe813c2a000: transfer of 'dortmund.cub.sioplc.fr/IN' from 192.36.4.10#53: connected using 192.36.4.10#53
08-Oct-2026 08:15:00.129 xfer-in: info: zone dortmund.cub.sioplc.fr/IN: transferred serial 2026100101
08-Oct-2026 08:15:00.129 xfer-in: info: 0x7fe813c2a000: transfer of 'dortmund.cub.sioplc.fr/IN' from 192.36.4.10#53: Transfer status: success
08-Oct-2026 08:15:00.129 xfer-in: info: 0x7fe813c2a000: transfer of 'dortmund.cub.sioplc.fr/IN' from 192.36.4.10#53: Transfer completed: 1 messages, 7 records, 222 bytes, 0.001 secs (222000 bytes/sec) (serial 2026100101)
```

**Statut :**

- [x] Ok
- [ ] KO

**Commentaire :**

> Le transfert de zone AXFR s'est bien déclenché et les enregistrements sont récupérés avec succès depuis le ns0.

---

## 9. Retour arrière

En cas de dysfonctionnement critique ou d'erreur de syntaxe empêchant le démarrage du service, exécuter les commandes suivantes pour restaurer la configuration d'origine.

```bash
sudo rm -rf /etc/bind
sudo mv /etc/bind.bak /etc/bind
sudo mv /etc/apparmor.d/usr.sbin.named.bak /etc/apparmor.d/usr.sbin.named
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.named
sudo systemctl restart bind9
```