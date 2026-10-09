---
description: Documentation et procédure technique du contexte CUB.
---

# Contexte CUB - BTS SIO

![Bannière CUB](../assets/banniere-cub.png)

!!! abstract "Informations sur le document"
    - **Auteur :** KADA Amine
    - **Classe :** BTS SIO 2 - Option SISR
    - **Contexte :** Présentation générale de l'entreprise CUB

---

## Présentation de l'entreprise CUB

Née en décembre 2010, la société **CUB** est une entreprise spécialisée dans l'incubation de startups partageant les mêmes valeurs de solidarité et de développement durable. Au travers de sa plate-forme web, CUB permet à des professionnels d'accéder à des espaces de travail dédiés : salles de réunion, de formation ou de séminaire.

CUB met à disposition de ses clients un ensemble de solutions techniques d'accès dans un millier de salles de réunion situées dans une quarantaine de villes différentes. Les ressources et outils du Web 2.0 qui permettent aux entreprises de gérer leurs contenus et leurs connaissances de manière sécurisée sont accessibles indépendamment via des prestataires de type *Cloud Computing* : partage de fichiers, gestion de projet, réseau social d'entreprise, wiki d'entreprise, etc.

Le siège social de CUB est situé à Paris, des agences sont implantées dans plusieurs grandes villes internationales : Anvers, Barcelone, Hong-Kong, Los Angeles et en Corse.

---

## Infrastructure et Gestion Réseau

Chaque agence dispose d'une adresse IPv4 publique propre et nominative. Pour cela, l'entreprise CUB a obtenu auprès du **RIPE NCC** un numéro d'AS et un préfixe IPv4 : `192.36.0.0/16`. Elle est donc considérée comme un LIR (Local Internet Registry). De plus, l'entreprise possède le nom de domaine `cub.sioplc.fr` géré par le bureau d'enregistrement OVH.

La **Direction des Systèmes d'Information (DSI)**, située à Paris, participe étroitement aux choix stratégiques de CUB. Elle a pour mission de définir et mettre en œuvre la politique informatique en accord avec la stratégie générale et ses objectifs de performance.

Le siège social est le cœur du système d'information interne de CUB, mais un **Service Informatique de Proximité (SIP)** est présent sur chaque agence. Le SIP est responsable de l'assistance aux utilisateurs locaux et de la maintenance des ressources locales (infrastructure réseau et serveurs). Le SIP prend également en charge des projets qui concernent ponctuellement leur site.

---

## Fiches disponibles

### BLOC 2 — Exploitation des systèmes

* [**Commande CUB**](../reseau/cisco/configurations/commande-cub.md) : Les commandes essentielles et l'administration système.
* [**Exploitation des services**](../services/exploitation-services.md) : Mise en œuvre et gestion des services réseau (DNS, Bastion, etc.).

### BLOC 3 — Cybersécurité & Réseaux

* [**Cybersécurité CUB**](../securite/cybersecurite-cub.md) : Concepts fondamentaux de la sécurité des systèmes d'information.
* [**VLSM & Table de routage CUB**](../reseau/vlsm-routage.md) : Sous-réseaux, adressage IP et principes de routage.

---

## À propos de ce site

Ce site de documentation technique est généré statiquement via [Zensical](https://zensical.org/) (MkDocs) et est déployé sur GitHub Pages / Cloudflare Pages.
