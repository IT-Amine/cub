# cub-docs

![Bannière CUB](docs/assets/banniere-cub.png)

## Contexte

Documentation officielle du projet **CUB** pour le BTS SIO 2 (option SISR) du lycée Paul-Louis Courier.

Ce dépôt centralise les fiches de révision, les procédures techniques et les ressources liées au contexte CUB, organisées par BLOC.

---

## Structure du dépôt

```text
cub-docs/
├── .github/
│   ├── workflows/
│   │   ├── docs.yml          → Build & déploiement GitHub Pages (Zensical)
│   │   └── security.yml      → Scan de secrets (TruffleHog)
│   └── pull_request_template.md
├── docs/
│   ├── assets/               → Bannière
│   │   ├── cisco/            → Maquettes Cisco
│   │   ├── resource/         → Modèles et référentiels (BTS SIO)
│   │   └── schema/           → Schémas logiques et physiques
│   ├── bloc2/                → Fichiers relatifs au BLOC 2
│   │   ├── commande-cub.md
│   │   ├── config-ad.md
│   │   └── exploitation-services.md
│   ├── bloc3/                → Fichiers relatifs au BLOC 3
│   │   ├── config-dns-recursif.md
│   │   ├── cybersecurite-cub.md
│   │   └── vlsm-routage.md
│   ├── description.md        → Plan d'adressage, serveurs, administration
│   ├── index.md              → Page d'accueil
│   ├── plan.md               → Schémas
│   └── presentation.md       → Présentation du contexte CUB
├── .gitignore
├── README.md
├── autopush.sh               → Script d'automatisation des sauvegardes Git
└── zensical.toml             → Configuration du site de documentation
```

---

## Utilisation de cub-docs

### 1. Cloner le dépôt localement

```bash
git clone https://github.com/IT-Amine/cub.git
cd cub
```

### 2. Installer Zensical

```bash
python3 -m pip install zensical
```

### 4. Ajouter une fiche

Créez un fichier `.md` dans le dossier `docs/`, puis référencez-le dans la section `nav` du fichier `zensical.toml`.

---

## Déploiement

Le site est automatiquement déployé sur **GitHub Pages** à chaque push sur la branche `main` via le workflow `.github/workflows/docs.yml`.

- Site en ligne : [Docs CUB Amine](https://IT-Amine.github.io/cub)
- Site en ligne : [Docs CUB Louis (Partenaire)](https://firetoak.github.io/cub-docs/)
- Site en ligne : [Docs CUB Prof](https://cubdocumentation.sioplc.fr/)

---

## Mainteneurs

- **Amine KADA** | [GitHub](https://github.com/IT-Amine)
