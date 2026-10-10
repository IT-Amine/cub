---
description: "Tables NAT"
---

# Tables NAT

![Bannière CUB](../assets/banniere-cub.png)

!!! abstract "Informations sur le document"
    - **Auteur :** KADA Amine
    - **Classe :** BTS SIO 2 - Option SISR
    - **Date :** 04/09/2026
    - **Sujet :** Tables NAT

---

## Contexte

Documentation référençant les règles de traduction d'adresses réseau (Source NAT / SNAT). Ce mécanisme masque les plans d'adressage internes (LAN et INTER-CO) en les traduisant vers une adresse IP publique unique (192.36.253.40), permettant ainsi l'accès à des Réseaux externes tout en sécurisant la topologie de l'infrastructure de base.

## Tables NAT

| Description | IP src (Avant) | Port src | IP dst (Avant) | Port dst | IP src (Après) | Port src | IP dst (Après) | Port dst |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LAN | `192.168.4.0/24` | `*` | `*` | `*` | `192.36.253.40` | `*` | `*` | `*` |
| INTER-CO | `192.168.44.248/29` | `*` | `*` | `*` | `192.36.253.40` | `*` | `*` | `*` |
