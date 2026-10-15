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
│   │   └── cisco/
│   │       ├── configurations/   → Commandes de base CUB
│   │       ├── dhcp/             → Relais DHCP
│   │       ├── nat/              → NAT Cisco
│   │       ├── routage/          → Routage statique
│   │       ├── securite/         → Mots de passe & sécurité d'accès
│   │       ├── ssh/              → SSH commutateur & routeur
│   │       ├── vtp/              → VTP
│   │       └── recettes/         → Recette commutateur L3
│   │
│   ├── windows/                  → Administration Windows
│   │   ├── core/                 → Déploiement Windows Server Core, AD, DHCP
│   │   ├── powershell/           → Scripts et fondamentaux PowerShell
│   │   └── wac/                  → Windows Admin Center
│   │
│   ├── securite/                 → Cybersécurité
│   │   ├── cybersecurite-cub.md  → Théorie UTM, Stormshield vs Stateful, VLAN
│   │   ├── stormshield/
│   │   │   ├── procedures/       → Config interface, NAT, routage, sous-interface, sauvegarde
│   │   │   ├── problemes/        → Résolution d'erreurs
│   │   │   └── recettes/         → Recette pare-feu
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
│   ├── General - CUB/            → Description, plan et présentation
│   └── index.md                  → Page d'accueil du site
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

## Bonnes pratiques Git & GitHub (Workflow de contribution)

Afin de maintenir une base de code et une documentation saines, prévisibles et exemptes de conflits, tout contributeur doit appliquer les standards d'ingénierie suivants :

### 1. Cycle de vie des branches (Branching Strategy)
- **Protection de `main` :** Aucun commit direct n'est autorisé sur la branche `main`. Toute évolution transite obligatoirement par une branche dédiée et une Pull Request.
- **Convention de nommage :**
  - `feat/<sujet>` : Ajout d'une fonctionnalité ou d'une nouvelle procédure (ex : `feat/ajout-docs-dns`).
  - `fix/<sujet>` : Correction d'une anomalie technique, typographique ou de routage (ex : `fix/masque-vlan53`).
  - `docs/<sujet>` : Mise à jour éditoriale de documentation existante.
  - `refactor/<sujet>` : Restructuration sans modification fonctionnelle.
- **Création d'une branche propre :**
  ```bash
  git fetch origin
  git checkout -b feat/ma-fonctionnalite origin/main
  ```

### 2. Norme des messages de commit (Conventional Commits)
Les commits doivent être atomiques et respecter la nomenclature standard :
```text
<type>(<portée>): <description concise à l'impératif>

[corps optionnel détaillant les choix techniques]
```
- **Types autorisés :**
  - `feat` : Nouvelle fonctionnalité / nouvelle documentation.
  - `fix` : Correction d'un bug ou d'une coquille.
  - `refactor` : Réécriture ou réorganisation de configurations / templates.
  - `ci` : Modification des workflows d'intégration continue (`.github/workflows/`).
  - `chore` : Tâche de maintenance courante (dépendances, gitignore).
- **Exemple :**
  ```bash
  git commit -m "feat(securite): durcissement des regles UFW et integration Gitleaks"
  ```

### 3. Checklist pré-push (Zéro régression)
Avant de pousser vos modifications sur le serveur distant :
1. **Compilation locale :** Valider qu'aucune erreur ou avertissement Zensical n'est présent :
   ```bash
   zensical build
   ```
2. **Synchronisation avec `main` :** Réappliquer vos commits par-dessus la dernière version du dépôt pour garantir un historique linéaire et prévenir les conflits de fusion :
   ```bash
   git fetch origin
   git rebase origin/main
   ```
3. **Push avec suivi :**
   - Premier push : `git push -u origin feat/ma-fonctionnalite`
   - Pushs ultérieurs : `git push`
   - En cas de push post-rebase : `git push --force-with-lease` (l'usage de `--force` brut est strictement proscrit).

### 4. Revue de code et intégration continue (Pull Requests)
- Ouvrir une Pull Request vers la branche `main`.
- Vérifier le statut des contrôles automatisés exécutés par GitHub Actions :
  - **Documentation :** Validation de la compilation Zensical.
  - **Security :** Scan anti-fuite de secrets (TruffleHog & Gitleaks) et audit de vulnérabilités des dépendances (`pip-audit`).
- Après validation et approbation de la revue, effectuer la fusion via **Squash and merge** ou **Rebase and merge**.

---

## Déploiement

Le site est automatiquement déployé sur **GitHub Pages** à chaque push sur la branche `main` via le workflow `.github/workflows/docs.yml`.

- 🌐 [Docs CUB — INFRAMINE](https://IT-Amine.github.io/cub)
- 🌐 [Docs CUB — Partenaire (Louis)](https://cub.bts.loutik.fr/)
- 🌐 [Docs CUB — Professeur](https://cubdocumentation.sioplc.fr/)

---

## Mainteneurs

- **INFRAMINE** | [GitHub](https://github.com/IT-Amine)
