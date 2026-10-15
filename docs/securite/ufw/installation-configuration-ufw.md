---
description: "Procédure d'installation et de configuration durcie du pare-feu hôte UFW sur Debian"
---

# Procédure et configuration durcie du pare-feu hôte UFW sur Debian"

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** INFRAMINE
> - **Date :** 01/10/2026
> - **Domaine :** Cybersécurité & Pare-feu hôte (UFW)

---

## 1. Sommaire

- [2. Contexte](#2-contexte)
- [3. Installation du paquet UFW](#3-installation-du-paquet-ufw)
- [4. Définition des politiques de filtrage par défaut](#4-definition-des-politiques-de-filtrage-par-defaut)
- [5. Ouverture des flux applicatifs et durcissement des accès d'administration](#5-ouverture-des-flux-applicatifs-et-durcissement-des-acces-dadministration)
- [6. Activation du service de filtrage](#6-activation-du-service-de-filtrage)
- [7. Vérification de l'état opérationnel et recette](#7-verification-de-letat-operationnel-et-recette)

---

## 2. Contexte

UFW (Uncomplicated Firewall) constitue une interface d'administration simplifiée pour le sous-système de filtrage de paquets du noyau Linux (`iptables` / `nftables`). 

Au sein de l'infrastructure CUB, UFW est déployé en tant que pare-feu d'hôte local (défense en profondeur) sur les serveurs applicatifs sous Debian. Il permet d'isoler strictement chaque composant logiciel et d'appliquer le principe de moindre privilège :
- Les accès d'administration distante (SSH - Port 22) sont strictement réservés aux adresses du **VLAN 20 (Administration : `192.168.4.192/28`)** et du **VLAN 53 (Bastion Guacamole : `192.168.4.208/28`)**.
- Le port alternatif **8080/tcp** est ouvert spécifiquement pour exposer l'interface de gestion de parc informatique **GLPI**.
- Les ports sécurisés **443/tcp** (HTTPS) et **8443/tcp** (Portail Bastion Guacamole) sont autorisés pour les consultations sécurisées.

---

## 3. Installation du paquet UFW

3.1. **Mise à jour des dépôts et installation.** Déploiement des binaires officiels du pare-feu sur le système Debian.

```bash
sudo apt update && sudo apt install -y ufw
```

- `apt update` : Actualise le catalogue local des paquets disponibles depuis les dépôts officiels.
- `apt install -y ufw` : Installe le paquet `ufw` sans solliciter de confirmation interactive.

---

## 4. Définition des politiques de filtrage par défaut

4.1. **Application du principe de moindre privilège.** Verrouillage systématique de tout flux entrant non explicitement autorisé, tout en autorisant les requêtes initiées par le système vers l'extérieur.

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

- `default deny incoming` : Rejette ou ignore tout paquet entrant n'ayant pas de règle d'autorisation explicite.
- `default allow outgoing` : Permet au serveur d'initier des connexions sortantes (mises à jour système, requêtes DNS, résolutions NTP).

---

## 5. Ouverture des flux applicatifs et durcissement des accès d'administration

5.1. **Déclaration des règles de filtrage ciblées.** Restriction drastique du port SSH aux postes d'administration et au bastion, suivie de l'exposition des services applicatifs.

```bash
# 1. Restriction stricte de l'accès SSH (Port 22 TCP)
sudo ufw allow from 192.168.4.192/28 to any port 22 proto tcp comment 'SSH depuis VLAN 20 Admin'
sudo ufw allow from 192.168.4.208/28 to any port 22 proto tcp comment 'SSH depuis VLAN 53 Bastion'

# 2. Ouverture des flux applicatifs Web
sudo ufw allow 8080/tcp comment 'Serveur Web GLPI (ITSM)'
sudo ufw allow 443/tcp comment 'Serveur Web HTTPS'
sudo ufw allow 8443/tcp comment 'Portail Bastion Guacamole'
```

- `allow from 192.168.4.192/28 ...` : Restreint l'administration SSH au sous-réseau VLAN 20 d'administration.
- `allow from 192.168.4.208/28 ...` : Autorise le serveur de rebond Apache Guacamole (VLAN 53) à relayer les sessions d'administration.
- `8080/tcp` : Port d'écoute du serveur Web GLPI.
- `443/tcp` / `8443/tcp` : Ports d'accès Web chiffrés en HTTPS.

---

## 6. Activation du service de filtrage

> [!warning] Vérification préalable de l'adresse IP source
> Avant d'activer UFW, assurez-vous d'être connecté depuis une machine située dans le **VLAN 20 (Administration : `192.168.4.192/28`)** ou le **VLAN 53 (Bastion : `192.168.4.208/28`)**. Si vous lancez l'activation depuis un autre réseau (ex: VLAN 10 Clients ou VLAN 54 Production), votre session SSH sera immédiatement coupée.

6.1. **Activation et persistance au démarrage.**

```bash
sudo ufw enable
```

- `enable` : Charge immédiatement les règles dans le pare-feu du noyau et active le service au démarrage de la machine.

---

## 7. Vérification de l'état opérationnel et recette

7.1. **Contrôle de l'état et de la politique active.**

```bash
sudo ufw status verbose
```

- `status verbose` : Affiche l'état d'activation, les politiques globales par défaut et la liste détaillée des règles numérotées avec leurs commentaires.

```text title="Sortie attendue sur la console"
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), deny (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    192.168.4.192/28           # SSH depuis VLAN 20 Admin
22/tcp                     ALLOW IN    192.168.4.208/28           # SSH depuis VLAN 53 Bastion
8080/tcp                   ALLOW IN    Anywhere                   # Serveur Web GLPI (ITSM)
443/tcp                    ALLOW IN    Anywhere                   # Serveur Web HTTPS
8443/tcp                   ALLOW IN    Anywhere                   # Portail Bastion Guacamole
```
