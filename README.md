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
│   │
│   ├── reseau/                   → Administration & supervision des réseaux
│   │   ├── vlsm-routage.md       → Calculs VLSM, tables de routage & NAT
│   │   └── cisco/                → Dossier aplati (NAT, routage, SSH, etc.)
│   │
│   ├── windows/                  → Administration Windows
│   │   ├── core/                 → Déploiement Windows Server Core, AD, DHCP
│   │   ├── powershell/           → Scripts et fondamentaux PowerShell
│   │   └── wac/                  → Windows Admin Center
│   │
│   ├── securite/                 → Cybersécurité
│   │   ├── cybersecurite-cub.md  → Théorie UTM, Stormshield vs Stateful, VLAN
│   │   ├── stormshield/          → Dossier aplati (Procédures, recettes, erreurs)
│   │   ├── bastion/              → Apache Guacamole
│   │   └── ufw/                  → Configuration UFW
│   │
│   ├── services/                 → Exploitation des services
│   │   ├── communs/              → Configuration initiale Debian
│   │   ├── dns/                  → Bind9 et Unbound
│   │   ├── glpi/                 → Installation et gestion ITIL
│   │   ├── etckeeper/            → Versioning
│   │   └── totp/                 → Authentification 2FA
│   │
│   ├── ressources/               → Base documentaire commune
│   ├── description.md            → Description de l'infrastructure CUB
│   ├── index.md                  → Page d'accueil du site
│   ├── plan.md                   → Schémas logique & physique
│   └── presentation.md           → Présentation du contexte CUB
│
├── .gitignore
├── README.md
├── requirements.txt              → Dépendances Python
├── wrangler.toml                 → Configuration Cloudflare Pages
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
Créez simplement un fichier `.md` dans le dossier thématique correspondant (`reseau/`, `securite/`, `services/`, etc.). Zensical générera automatiquement le menu de navigation en se basant sur l'arborescence des dossiers et le titre principal (`# Titre`) de votre fichier.

---

## Déploiement

Le site est automatiquement déployé sur **GitHub Pages** à chaque push sur la branche `main` via le workflow `.github/workflows/docs.yml`.

- 🌐 [Docs CUB — Amine Kada](https://IT-Amine.github.io/cub)
- 🌐 [Docs CUB — Partenaire (Louis)](https://cub.bts.loutik.fr/)
- 🌐 [Docs CUB — Professeur](https://cubdocumentation.sioplc.fr/)

---

## Mainteneurs

- **Amine KADA** | [GitHub](https://github.com/IT-Amine)
