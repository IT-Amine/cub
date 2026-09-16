---
description: Documentation et procédure technique.
---

# BLOC 2 - Tables NAT

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 04/09/2026</p>
    <p><strong>Contexte :</strong> Configuration Tables NAT</p>
</div>

---

## Informations

* **Auteur :** Amine Kada
* **Date :** 04/09/2026
* **Domaine :** réseaux

---

## 1. Sommaire

* [1. Sommaire](#1-sommaire)
* [2. Contexte](#2-contexte)
* [3. Tables NAT](#3-tables-nat)

## 2. Contexte

Documentation référençant les règles de traduction d'adresses réseau (Source NAT / SNAT). Ce mécanisme masque les plans d'adressage internes (LAN et INTER-CO) en les traduisant vers une adresse IP publique unique (192.36.253.40), permettant ainsi l'accès à des réseaux externes tout en sécurisant la topologie de l'infrastructure de base.

## 3. Tables NAT

| Description | IP src (Avant) | Port src | IP dst (Avant) | Port dst | IP src (Après) | Port src | IP dst (Après) | Port dst |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LAN | `192.168.4.0/24` | `*` | `*` | `*` | `192.36.253.40` | `*` | `*` | `*` |
| INTER-CO | `192.168.44.248/29` | `*` | `*` | `*` | `192.36.253.40` | `*` | `*` | `*` |
