---
description: "Annuaire des machines et services"
---

# Annuaire des machines

![Bannière CUB](../assets/banniere-cub.png)

!!! abstract "Informations sur le document"
    - **Auteur :** KADA Amine
    - **Classe :** BTS SIO 2 - Option SISR
    - **Date :** 14/10/2026
    - **Sujet :** Annuaire des machines et des services de l'infrastructure CUB

---

## Contexte

Ce document recense l'inventaire complet des machines virtuelles, des équipements d'interconnexion réseau, ainsi que des services applicatifs déployés au sein de l'agence Dortmund de l'infrastructure CUB. Les noms d'hôtes et FQDN respectent la convention de nommage du domaine Active Directory délégué (`local.dortmund.cub.sioplc.fr`) et de la zone publique faisant autorité (`dortmund.cub.sioplc.fr`).

---

## Réseau PRODUCTION (VLAN 54)

> **Passerelle par défaut (SVI Switch L3) :** `192.168.4.126`  
> **Masque de sous-réseau :** `255.255.255.128 (/25)`

| Nom machine | FQDN | Adresse IP | Rôle / Fonction |
| :--- | :--- | :--- | :--- |
| **ServeurAD0** | `ad0.local.dortmund.cub.sioplc.fr` | `192.168.4.1/25` | Contrôleur de domaine AD DS Maître (PDC) & DNS intégré |
| **ServeurAD1** | `ad1.local.dortmund.cub.sioplc.fr` | `192.168.4.2/25` | Contrôleur de domaine AD DS Réplica (Secondaire) & DNS intégré |
| **ServeurDHCP0** | `dhcp0.local.dortmund.cub.sioplc.fr` | `192.168.4.3/25` | Serveur DHCP principal (Windows Server Core) |
| **ServeurDHCP1** | `dhcp1.local.dortmund.cub.sioplc.fr` | `192.168.4.4/25` | Serveur DHCP secondaire (Windows Server Core) |
| **ServeurWAC0** | `wac0.local.dortmund.cub.sioplc.fr` | `192.168.4.5/25` | Windows Admin Center principal (Portail d'administration) |
| **ServeurWAC1** | `wac1.local.dortmund.cub.sioplc.fr` | `192.168.4.6/25` | Windows Admin Center secondaire (Nœud d'administration) |
| **ServeurDNS0** | `dns0.local.dortmund.cub.sioplc.fr` | `192.168.4.10/25` | Serveur DNS récursif interne Maître (Unbound) |
| **ServeurDNS1** | `dns1.local.dortmund.cub.sioplc.fr` | `192.168.4.11/25` | Serveur DNS récursif interne Esclave / Secondaire (Unbound) |

---

## Réseau DMZ (VLAN 84)

> **Passerelle par défaut (Pare-feu Stormshield) :** `192.36.4.254`  
> **Masque de sous-réseau :** `255.255.255.0 (/24)`

| Nom machine | FQDN | Adresse IP | Rôle / Fonction |
| :--- | :--- | :--- | :--- |
| **ServeurDNS0 (ns0)** | `ns0.dortmund.cub.sioplc.fr` | `192.36.4.10/24` | Serveur DNS faisant autorité Maître (Bind9 Maître) |
| **ServeurDNS1 (ns1)** | `ns1.dortmund.cub.sioplc.fr` | `192.36.4.11/24` | Serveur DNS faisant autorité Esclave (Bind9 Esclave) |
| **ServeurWeb0 (www)** | `www.dortmund.cub.sioplc.fr` | `192.36.4.20/24` | Serveur Web vitrine DMZ (Apache/Nginx) |

---

## Réseau BASTION (VLAN 53)

> **Passerelle par défaut (SVI Switch L3) :** `192.168.4.214`  
> **Masque de sous-réseau :** `255.255.255.248 (/29)`

| Nom machine | FQDN | Adresse IP | Rôle / Fonction |
| :--- | :--- | :--- | :--- |
| **ServeurBastion0** | `bastion0.local.dortmund.cub.sioplc.fr` | `192.168.4.210/29` | Passerelle Bastion Apache Guacamole 0 (Principal) |
| **ServeurBastion1** | `bastion1.local.dortmund.cub.sioplc.fr` | `192.168.4.211/29` | Passerelle Bastion Apache Guacamole 1 (Secondaire) |

---

## Équipements Réseau & Sécurité

| Nom équipement | Modèle | FQDN d'administration | Adresses IP d'interfaces |
| :--- | :--- | :--- | :--- |
| **STORMSHIELD01** | Stormshield SN210 | `stormshield01.dortmund.cub.sioplc.fr` | `192.168.4.205/28` (Admin VLAN 20)<br>`192.36.4.254/24` (DMZ VLAN 84)<br>`192.168.44.254/29` (Inter-co VLAN 2)<br>`192.36.253.40/24` (WAN) |
| **dmd-sw-coeur01** | Cisco Catalyst 3560 (L3) | `dmd-sw-c1.local.dortmund.cub.sioplc.fr` | `192.168.4.126/25` (SVI Prod 54)<br>`192.168.4.190/26` (SVI Clients 10)<br>`192.168.4.206/28` (SVI Admin 20)<br>`192.168.4.214/29` (SVI Bastion 53)<br>`192.168.44.253/29` (SVI Inter-co 2) |
| **dmd-sw-acces01** | Cisco Catalyst 2960 (L2) | `dmd-sw-a1.local.dortmund.cub.sioplc.fr` | `192.168.4.194/28` (SVI Management VLAN 20) |

---

## Services & Interfaces d'Administration

| Service | Machine hôte | FQDN / URL | Adresse IP et Port | Protocole |
| :--- | :--- | :--- | :--- | :--- |
| **Active Directory Maître** | ServeurAD0 | `ad0.local.dortmund.cub.sioplc.fr` | `192.168.4.1:389 / 636` | LDAP / LDAPS / Kerberos (Port 88) |
| **Active Directory Esclave** | ServeurAD1 | `ad1.local.dortmund.cub.sioplc.fr` | `192.168.4.2:389 / 636` | LDAP / LDAPS / Kerberos (Port 88) |
| **Service DHCP0 (Principal)**| ServeurDHCP0 | `dhcp0.local.dortmund.cub.sioplc.fr` | `192.168.4.3:67` | UDP 67 (DHCPv4 Server) |
| **Service DHCP1 (Secondaire)**| ServeurDHCP1 | `dhcp1.local.dortmund.cub.sioplc.fr` | `192.168.4.4:67` | UDP 67 (DHCPv4 Server) |
| **WAC Principal** | ServeurWAC0 | [https://wac0.local.dortmund.cub.sioplc.fr:10443](https://192.168.4.5:10443) | `192.168.4.5:10443` | HTTPS / WinRM |
| **WAC Secondaire** | ServeurWAC1 | [https://wac1.local.dortmund.cub.sioplc.fr:10443](https://192.168.4.6:10443) | `192.168.4.6:10443` | HTTPS / WinRM |
| **DNS Récursif Maître** | ServeurDNS0 | `dns0.local.dortmund.cub.sioplc.fr` | `192.168.4.10:53` | TCP/UDP 53 (Unbound) |
| **DNS Récursif Esclave** | ServeurDNS1 | `dns1.local.dortmund.cub.sioplc.fr` | `192.168.4.11:53` | TCP/UDP 53 (Unbound) |
| **DNS Autoritaire Maître** | ServeurDNS0 (ns0) | `ns0.dortmund.cub.sioplc.fr` | `192.36.4.10:53` | TCP/UDP 53 (Bind9 Maître) |
| **DNS Autoritaire Esclave** | ServeurDNS1 (ns1) | `ns1.dortmund.cub.sioplc.fr` | `192.36.4.11:53` | TCP/UDP 53 (Bind9 Esclave) |
| **Bastion Guacamole 0** | ServeurBastion0 | [https://bastion0.local.dortmund.cub.sioplc.fr:8443](https://192.168.4.210:8443) | `192.168.4.210:8443` | HTTPS / Reverse Proxy |
| **Bastion Guacamole 1** | ServeurBastion1 | [https://bastion1.local.dortmund.cub.sioplc.fr:8443](https://192.168.4.211:8443) | `192.168.4.211:8443` | HTTPS / Reverse Proxy |
| **Pare-feu Stormshield** | STORMSHIELD01 | [https://192.168.4.205](https://192.168.4.205) | `192.168.4.205:443` | HTTPS / SSH (Port 22) |
| **Serveur Web DMZ** | ServeurWeb0 (www) | [https://www.dortmund.cub.sioplc.fr](https://192.36.4.20) | `192.36.4.20:80 / 443` | HTTP / HTTPS |
