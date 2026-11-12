---
description: "Procédure d'installation et de configuration durcie du pare-feu hôte UFW sur Debian"
---

# Procédure et configuration durcie du pare-feu hôte UFW sur Debian

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** Amine
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
- Les accès d'administration distante (SSH - Port 22) sont strictement réservés aux adresses du **VLAN 20 (Administration : `192.168.4.192/28`)** et du **VLAN 53 (Bastion Guacamole : `192.168.4.208/29`)**.
- Le port **80/tcp** permet l’accès HTTP aux sites WordPress et scanner hébergés sur le serveur Web.
- Les ports HTTPS sont autorisés uniquement pour les services configurés sur le serveur concerné.

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
sudo ufw allow from 192.168.4.208/29 to any port 22 proto tcp comment 'SSH depuis VLAN 53 Bastion'

# Les règles applicatives sont à choisir séparément selon le service hébergé.
```

- `allow from 192.168.4.192/28 ...` : Restreint l'administration SSH au sous-réseau VLAN 20 d'administration.
- `allow from 192.168.4.208/29 ...` : Autorise le serveur de rebond Apache Guacamole (VLAN 53) à relayer les sessions d'administration.
- `80/tcp` : Port HTTP des VirtualHosts Apache WordPress et scanner.
- `443/tcp` / `8443/tcp` : Ports possibles selon le service et le proxy ; ne pas les ouvrir automatiquement sur tous les serveurs.

---

5.2. **Identifier les services et appliquer seulement les règles nécessaires.**

```bash
sudo ss -lntup
sudo ufw status numbered
```

Sur le serveur Web, autoriser les connexions HTTP vers les VirtualHosts Apache :

```bash
sudo ufw allow 80/tcp comment 'HTTP Apache'
```

Les deux VirtualHosts utilisent le port 80. La restriction du scanner au VLAN Administration est configurée dans Apache. En présence d’un reverse proxy ou de NAT, vérifier l’adresse source reçue par Apache. En HTTPS ou sur un autre port, autoriser le port correspondant au service configuré.

## 6. Activation du service de filtrage

> [!warning] Vérification préalable de l'adresse IP source
> Avant d'activer UFW, assurez-vous d'être connecté depuis une machine située dans le **VLAN 20 (Administration : `192.168.4.192/28`)** ou le **VLAN 53 (Bastion : `192.168.4.208/29`)**. Si vous lancez l'activation depuis un autre réseau (ex: VLAN 10 Clients ou VLAN 54 Production), votre session SSH sera immédiatement coupée.

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

Exemple pour le serveur Web avec HTTP autorisé :

```text title="Exemple de sortie"
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), deny (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    192.168.4.192/28           # SSH depuis VLAN 20 Admin
22/tcp                     ALLOW IN    192.168.4.208/29           # SSH depuis VLAN 53 Bastion
80/tcp                     ALLOW IN    Anywhere                   # HTTP Apache
```
