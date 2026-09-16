# cub-docs

![Bannière CUB](docs/assets/banniere-cub.png)

## Contexte

Documentation officielle du projet **CUB** pour le BTS SIO 2 (option SISR) du lycée Paul-Louis Courier.

Ce dépôt centralise les fiches de révision, les procédures techniques et les ressources liées au contexte CUB, organisées par thématique.

---

## Structure du dépôt

```text
cub-docs/
├── .github/
│   ├── workflows/
│   │   ├── docs.yml              → Build & déploiement GitHub Pages (Zensical)
│   │   └── security.yml          → Scan de secrets (TruffleHog)
│   └── pull_request_template.md
├── docs/
│   ├── assets/                   → Ressources statiques
│   │   ├── ad/                   → Captures Active Directory
│   │   ├── cisco/                → Maquettes Cisco (logique & physique)
│   │   ├── resource/             → Modèles et référentiels BTS SIO
│   │   └── schema/               → Schémas logiques et physiques
│   │
│   ├── reseau/                   → Administration & supervision des réseaux
│   │   ├── vlsm-routage.md       → Calculs VLSM, tables de routage & NAT
│   │   └── cisco/
│   │       ├── configurations/   → Configs complètes SW L2, L3, routeur
│   │       ├── dhcp/             → Relais DHCP
│   │       ├── nat/              → NAT Cisco
│   │       ├── routage/          → Routage statique
│   │       ├── securite/         → Mots de passe & sécurité d'accès
│   │       ├── ssh/              → SSH commutateur & routeur
│   │       ├── vtp/              → VTP
│   │       └── recettes/         → Recette commutateur L3
│   │
│   ├── windows/                  → Administration Windows
│   │   └── core/
│   │       ├── configuration-windows-core.md  → Config Windows Core
│   │       └── config-ad.md                   → Déploiement & hardening AD1 Core
│   │
│   ├── securite/                 → Cybersécurité
│   │   ├── cybersecurite-cub.md  → Théorie UTM, Stormshield vs Stateful, VLAN
│   │   └── stormshield/
│   │       ├── procedures/       → Config interface, NAT, routage, sous-interface, sauvegarde
│   │       ├── problemes/        → Résolution d'erreurs
│   │       └── recettes/         → Recette pare-feu
│   │
│   ├── services/                 → Exploitation des services
│   │   ├── exploitation-services.md  → Résumé Etckeeper + TOTP (fiche révision)
│   │   ├── dns/                  → DNS Récursif Bind9 sur Debian
│   │   ├── etckeeper/            → Versioning /etc avec Git
│   │   ├── totp/                 → Authentification TOTP (2FA SSH)
│   │   └── communs/              → Paquets communs Debian
│   │
│   ├── ressources/               → Base documentaire commune
│   │   ├── configurations/       → Fichiers de config switch & firewall
│   │   ├── maquettes/            → Maquette Packet Tracer (.pkt)
│   │   ├── schemas/              → Schémas brassage, logique, physique (.drawio & .pdf)
│   │   ├── plan-adressage.md     → Plan d'adressage IP complet
│   │   ├── tables-nat.md         → Tables NAT
│   │   └── tables-routage.md     → Tables de routage
│   │
│   ├── description.md            → Description de l'infrastructure CUB
│   ├── index.md                  → Page d'accueil du site
│   ├── plan.md                   → Schémas logique & physique
│   └── presentation.md           → Présentation du contexte CUB
│
├── Logs/                         → Journaux du script autopush
├── .gitignore
├── README.md
├── autopush.sh                   → Script d'automatisation des sauvegardes Git
└── zensical.toml                 → Configuration du site de documentation
```

---

## Utilisation

### 1. Cloner le dépôt

```bash
git clone https://github.com/IT-Amine/cub.git
cd cub
```

### 2. Installer Zensical

```bash
python3 -m pip install zensical
```

### 3. Prévisualiser le site en local

```bash
zensical serve
```

### 4. Ajouter une fiche

Créez un fichier `.md` dans le dossier thématique correspondant (`reseau/`, `securite/`, `services/`, etc.), puis référencez-le dans la section `nav` du fichier `zensical.toml`.

---

## Déploiement

Le site est automatiquement déployé sur **GitHub Pages** à chaque push sur la branche `main` via le workflow `.github/workflows/docs.yml`.

- 🌐 [Docs CUB — Amine Kada](https://IT-Amine.github.io/cub)
- 🌐 [Docs CUB — Partenaire (Louis)](https://cub.bts.loutik.fr/)
- 🌐 [Docs CUB — Professeur](https://cubdocumentation.sioplc.fr/)

---

## Mainteneurs

- **Amine KADA** | [GitHub](https://github.com/IT-Amine)
