# cub-docs

![Bannière CUB](docs/assets/banniere_cub.png)

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
│   ├── assets/               → Bannière et schémas (logique, physique)
│   ├── presentation.md       → Présentation du contexte CUB
│   ├── description.md        → Plan d'adressage, serveurs, administration
│   ├── plan.md               → Schéma logique & schéma physique
│   ├── BLOC 2 - Commande CUB.md
│   ├── BLOC 2 - Exploitation des services.md
│   ├── BLOC 3 - Cybersécurité CUB.md
│   └── BLOC 3 - Cybersécurité VLSM & Table de routage CUB.md
├── .gitignore
├── README.md
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

Site en ligne : [https://IT-Amine.github.io/cub](https://IT-Amine.github.io/cub)

---

## Mainteneurs

- **Amine KADA** | [GitHub](https://github.com/IT-Amine)
- ** Louis MEDO** | [CUB Partenaire](https://github.com/FireToak/cub-docs)
