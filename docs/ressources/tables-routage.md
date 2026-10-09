---
description: Documentation et procédure technique.
---

# BLOC 2 - Tables de routage

![Bannière CUB](../assets/banniere-cub.png)

!!! abstract "Informations sur le document"
    - **Auteur :** KADA Amine
    - **Classe :** BTS SIO 2 - Option SISR
    - **Date :** 04/09/2026
    - **Contexte :** Configuration Tables de routage

---

## 1. Sommaire

- [1. Sommaire](#1-sommaire)
- [2. Contexte](#2-contexte)
- [3. Tables de routage](#3-tables-de-routage)

## 2. Contexte

Ce document définit les règles de routage statique et les Réseaux directement connectés appliqués aux équipements cœur de l'infrastructure. Il détaille les tables de routage du commutateur de niveau 3 (dmd-sw-coeur01), responsable du routage inter-VLAN (Production, Clients, Administration), et du pare-feu (dmd-fw-coeur01), qui gère les flux vers la DMZ et l'accès extérieur (WAN). L'objectif est de garantir l'acheminement des paquets entre les différents segments logiques tout en centralisant le contrôle des flux Réseaux.

## 3. Tables de routage

### 4.1. Switch dmd-sw-coeur01

| Commentaire | Destination | Masque | Passerelle | Interface | Type |
| :--- | :--- | :--- | :--- | :--- | :---: |
| Production | 192.168.4.0 | 255.255.255.128 | 192.168.4.126 | 192.168.4.126 | C |
| Clients | 192.168.4.128 | 255.255.255.192 | 192.168.4.190 | 192.168.4.190 | C |
| Administration | 192.168.4.192 | 255.255.255.240 | 192.168.4.206 | 192.168.4.206 | C |
| Inter-co | 192.168.44.248 | 255.255.255.248 | 192.168.44.253 | 192.168.44.253 | C |
| Default | 0.0.0.0 | 0.0.0.0 | 192.168.44.254 | 192.168.44.253 | S* |

### 4.2. Pare-feu dmd-fw-coeur01

| Commentaire | Destination | Masque | Passerelle | Interface | Type |
| :--- | :--- | :--- | :--- | :--- | :---: |
| DMZ | 192.36.4.0 | 255.255.255.0 | 192.36.4.254 | 192.36.4.254 | C |
| Inter-co | 192.168.44.248 | 255.255.255.248 | 192.168.44.254 | 192.168.44.254 | C |
| WAN | 192.36.253.0 | 255.255.255.0 | 192.36.253.40 | 192.36.253.40 | C |
| LAN | 192.168.4.0 | 255.255.255.0 | 192.168.44.253 | 192.168.44.254 | S |
| Default | 0.0.0.0 | 0.0.0.0 | 192.36.253.254 | 192.36.253.40 | S* |
