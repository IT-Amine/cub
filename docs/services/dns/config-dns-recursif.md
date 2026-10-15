---
description: "Procédure de configuration d'un serveur DNS récursif avec Unbound et sécurisation AppArmor"
---

# BLOC 2 - Configuration du Serveur DNS Récursif (Unbound)

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** INFRAMINE
> - **Date :** 23/09/2026
> - **Domaine :** Services Réseau (DNS)

---

## 1. Sommaire

- [2. Contexte](#2-contexte)
- [3. Installation de Unbound et des outils d'administration](#3-installation-de-unbound-et-des-outils-dadministration)
- [4. Configuration principale du service Unbound](#4-configuration-principale-du-service-unbound)
- [5. Configuration des zones locales et stubs](#5-configuration-des-zones-locales-et-stubs)
- [6. Téléchargement des serveurs racines (Root Hints)](#6-telechargement-des-serveurs-racines-root-hints)
- [7. Journalisation et ajustement de la politique de sécurité AppArmor](#7-journalisation-et-ajustement-de-la-politique-de-securite-apparmor)
- [8. Configuration du résolveur local et validation](#8-configuration-du-resolveur-local-et-validation)

---

## 2. Contexte

Un serveur DNS **récursif** (ou résolveur) a pour rôle de traiter les requêtes de résolution émises par les postes clients et serveurs de l'entreprise. Contrairement à un serveur faisant autorité, le résolveur interroge itérativement les serveurs racine de l'Internet, puis les TLDs et enfin les serveurs faisant autorité pour trouver les adresses IP demandées, avant de **mettre en cache** les réponses pour optimiser les temps d'accès et économiser la bande passante WAN.

Au sein de l'infrastructure CUB, ce service est assuré sur les serveurs Debian `ServeurDNS0` (`192.168.4.10`) et `ServeurDNS1` (`192.168.4.11`) à l'aide de la solution **Unbound**.

---

## 3. Installation de Unbound et des outils d'administration

3.1. **Déploiement des paquets système.** Installation du démon Unbound et des utilitaires d'analyse et de diagnostic réseau.

```bash
sudo apt update
sudo apt install -y unbound dnsutils tcpdump tmux curl
```

- `unbound` : Démon du serveur DNS récursif validant et sécurisé.
- `dnsutils` : Fournit les outils de diagnostic réseau `dig` et `nslookup`.
- `tcpdump` : Analyseur de paquets pour l'écoute du trafic DNS sur le port UDP 53.

---

## 4. Configuration principale du service Unbound

4.1. **Édition du fichier de configuration du démon.** Définition des interfaces d'écoute, des règles de contrôle d'accès réseau et des paramètres de sécurité dans `/etc/unbound/unbound.conf`.

```bash
sudoedit /etc/unbound/unbound.conf
```

```text title="/etc/unbound/unbound.conf"
include: "/etc/unbound/unbound.conf.d/*.conf"

server:
    # Interface d'ecoute IPv4 locale et sur le reseau
    interface: 192.168.4.11
    interface: 127.0.0.1

    # Controle d'acces : restriction stricte aux reseaux de l'agence
    access-control: 192.168.4.0/24 allow_snoop
    access-control: 127.0.0.0/8 allow_snoop

    # Fichier indiquant les serveurs DNS racines
    root-hints: "/var/lib/unbound/root.hints"

    # Durcissement et confidentialite
    hide-version: yes
    hide-identity: yes
    qname-minimisation: yes

    # Protocole autorise
    do-ip4: yes

    # Journalisation des requetes
    logfile: /var/log/unbound.log
    verbosity: 1
    log-queries: yes
```

- `interface` : Restreint l'écoute aux adresses IP explicitement spécifiées (`192.168.4.11` et boucle locale).
- `access-control 192.168.4.0/24 allow_snoop` : Autorise les machines de l'agence à interroger le résolveur tout en permettant le traçage des requêtes.
- `hide-version: yes` : Masque la version d'Unbound pour limiter la reconnaissance passive par des attaquants.
- `qname-minimisation: yes` : Renforce la confidentialité en n'envoyant aux serveurs racine que le strict nécessaire de la requête DNS.

4.2. **Validation syntaxique de la configuration.** Contrôle de l'absence d'erreurs de syntaxe avant chargement du service.

```bash
sudo unbound-checkconf
```

- `unbound-checkconf` : Utilitaire vérifiant l'intégrité syntaxique du fichier `/etc/unbound/unbound.conf`.

---

## 5. Configuration des zones locales et stubs

5.1. **Déclaration des redirecteurs de zones internes.** Indication des serveurs DNS internes faisant autorité pour les domaines locaux privés ne figurant pas dans la racine publique.

```text title="/etc/unbound/unbound.conf"
    # Desactivation de la verification DNSSEC pour la zone interne
    domain-insecure: "sio.lan."
    private-domain: sio.lan.

# Redirection vers les serveurs internes faisant autorite
stub-zone:
    name: "sio.lan."
    stub-addr: 172.16.20.21
    stub-addr: 172.16.20.22
```

- `stub-zone` : Délègue la résolution d'un sous-domaine spécifique à des serveurs de noms faisant autorité désignés par `stub-addr`.
- `domain-insecure` : Désactive la validation DNSSEC sur la zone interne non signée.

---

## 6. Téléchargement des serveurs racines (Root Hints)

6.1. **Récupération de la liste officielle des serveurs racine Internet.** Téléchargement de la base `named.cache` officielle et enregistrement dans le répertoire de travail d'Unbound.

```bash
sudo curl --output /var/lib/unbound/root.hints https://www.internic.net/domain/named.cache
sudo chown -R unbound:unbound /var/lib/unbound/
```

- `curl --output` : Télécharge et enregistre la liste des 13 serveurs racine (de A à M).
- `chown -R unbound:unbound` : Assigne la propriété du fichier au compte de service `unbound`.

---

## 7. Journalisation et ajustement de la politique de sécurité AppArmor

7.1. **Création du fichier de journalisation.** Initialisation du fichier de log et affectation des droits au service Unbound.

```bash
sudo touch /var/log/unbound.log
sudo chown unbound:unbound /var/log/unbound.log
```

7.2. **Modification du profil AppArmor d'Unbound.** Autorisation en lecture/écriture sur le fichier de journalisation dans `/etc/apparmor.d/usr.sbin.unbound`.

```bash
sudoedit /etc/apparmor.d/usr.sbin.unbound
```

Ajouter la ligne suivante à l'intérieur du bloc principal du profil, avant l'accolade fermante `}` :

```text title="/etc/apparmor.d/usr.sbin.unbound"
  # Autorisation d'ecriture des logs Unbound
  /var/log/unbound.log rw,
```

- `/var/log/unbound.log rw,` : Autorise le binaire confiné `/usr/sbin/unbound` à ouvrir en lecture (`r`) et écriture (`w`) son fichier de logs.

7.3. **Rechargement de la politique AppArmor et redémarrage du service.** Application de la nouvelle règle et relance d'Unbound.

```bash
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.unbound
sudo systemctl restart apparmor
sudo systemctl restart unbound
sudo systemctl status unbound
```

- `apparmor_parser -r` : Recharge à chaud le profil de sécurité mis à jour dans le noyau Linux.

---

## 8. Configuration du résolveur local et validation

8.1. **Définition de l'adresse de bouclage comme résolveur local.** Configuration du fichier `/etc/resolv.conf` pour forcer la machine locale à interroger son propre service Unbound.

```bash
echo "nameserver 127.0.0.1" | sudo tee /etc/resolv.conf
```

8.2. **Suivi des événements journalisés en direct.** Surveillance des requêtes DNS interceptées et résolues par le service.

```bash
sudo tail -f /var/log/unbound.log
```

- `tail -f` : Affiche en continu les nouvelles lignes écrites dans le journal des requêtes d'Unbound.
