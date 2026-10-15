---
description: "Implémentation du Relais DHCP sur équipement Cisco"
---

# Implémentation du Relais DHCP sur équipement Cisco

![Bannière CUB](../../../assets/banniere-cub.png)

!!! abstract "Informations sur le document"
    - **Auteur :** INFRAMINE
    - **Classe :** BTS SIO 2 - Option SISR
    - **Date :** 05/09/2026
    - **Sujet :** Implémentation du Relais DHCP sur équipement Cisco

---

## Contexte

Le protocole DHCP repose nativement sur des requêtes de diffusion (Broadcast) systématiquement bloquées par les limites de domaines de diffusion (routeurs ou commutateurs de niveau 3). L'implémentation d'un agent relais DHCP via la fonction IP Helper permet d'écouter ces diffusions locales et de les encapsuler dans des trames monodiffusées (Unicast) à destination d'un serveur DHCP centralisé. Au sein de l'infrastructure CUB, cette approche d'ingénierie centralisée évite le déploiement de serveurs DHCP dédiés dans chaque VLAN d'accès.

## Implémentation de l'agent relais (IP Helper) {#3-implementation-de-lagent-relais-ip-helper}

4.1. **Configuration du relais DHCP sur l'interface passerelle.** Définition de l'adresse du serveur DHCP cible sur l'interface servant de passerelle par défaut pour le sous-réseau client (Interface physique sur un routeur, ou Interface VLAN / SVI sur un commutateur).

!!! INFO
    La commande `ip helper-address` transmet par défaut 8 services UDP (dont TFTP, DNS, Time, et DHCP). Dans des environnements de très haute sécurité, il est recommandé de filtrer les ports relayés avec `no ip forward-protocol udp`.

```text
dmd-sw-c1(config)# interface Vlan 10
dmd-sw-c1(config-if)# description VLAN CLIENTS
dmd-sw-c1(config-if)# ip address 192.168.4.190 255.255.255.192
dmd-sw-c1(config-if)# ip helper-address 192.168.4.3
dmd-sw-c1(config-if)# ip helper-address 192.168.4.4
dmd-sw-c1(config-if)# end
dmd-sw-c1# write memory
```

- `interface Vlan 10` : Sélectionne l'interface de routage SVI associée au sous-réseau des postes de travail clients (`192.168.4.128/26`).
- `ip address 192.168.4.190 255.255.255.192` : Assigne l'adresse IP de passerelle par défaut. Cette adresse est insérée dans le champ `giaddr` (Gateway IP Address) des paquets DHCP relayés, instruisant les serveurs DHCP sur l'étendue (Scope) à distribuer.
- `ip helper-address 192.168.4.3` : Relaie les requêtes Broadcast DHCP (ports UDP 67/68) en Unicast vers le serveur DHCP principal (`ServeurDHCP0` en VLAN 54).
- `ip helper-address 192.168.4.4` : Relaie simultanément vers le serveur DHCP secondaire (`ServeurDHCP1` en VLAN 54) pour assurer le basculement et la haute disponibilité (Load Balancing 50/50 ou Hot Standby).
- `write memory` : Sauvegarde la configuration active dans la mémoire non volatile (NVRAM).
