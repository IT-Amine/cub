# Pull Request - Documentation CUB

---

## Description des modifications

<!-- Décrivez de manière synthétique et précise les modifications apportées dans cette PR -->
- 

---

## Type de modification

- [ ] Ajout d'une nouvelle documentation ou procédure technique
- [ ] Mise à jour ou correction d'une fiche existante
- [ ] Évolution de l'architecture ou de la configuration réseau/système
- [ ] Correctif de sécurité ou mise à jour de dépendances

---

## Checklist de validation avant fusion (Definition of Done)

Merci de vérifier et cocher l'ensemble des points suivants avant de soumettre la validation :

### Validation technique & Build
- [ ] La compilation locale s'exécute sans aucune erreur ni avertissement (`zensical build` ou `zensical serve`).
- [ ] Tous les blocs de code Markdown (```) sont proprement ouverts et fermés avec leur syntaxe de langage.
- [ ] Tous les liens relatifs (vers les autres documentations, schémas et fichiers PDF) sont valides et fonctionnels.
- [ ] Les images et schémas sont correctement référencés et s'affichent sans rupture de lien.

### Sécurité & Données sensibles
- [ ] Aucun mot de passe réel n'est présent en clair dans les fichiers commités (usage strict de placeholders ou saisies sécurisées).
- [ ] Aucune clé d'API, token de session, clé privée ou secret sensible n'est exposé.
- [ ] Le workflow de sécurité GitHub Actions (TruffleHog, pip-audit, scan regex) passe avec succès.

### Conformité & Charte CUB
- [ ] Les adresses IP, masques de sous-réseau et FQDN sont conformes à l'annuaire officiel (`docs/ressources/annuaire-machines.md`) et au plan d'adressage VLSM.
- [ ] Le cartouche d'en-tête standard (`!!! abstract "Informations sur le document"`) est présent avec l'auteur, la classe et la date.
- [ ] Zéro émoji dans le corps des fiches techniques afin de garantir un rendu rigoureux et professionnel.
- [ ] La barre de navigation (`zensical.toml`) a été actualisée si de nouveaux fichiers ont été créés.
