---
description: Fichiers de configuration des équipements Cisco.
---

# BLOC 2 - Configurations Cisco (CUB)

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 30/09/2026</p>
    <p><strong>Contexte :</strong> Fichiers de configuration réseau</p>
</div>

---

Les configurations complètes des équipements de l'infrastructure CUB ne sont plus stockées en texte brut dans cette page afin de garantir qu'elles soient toujours à jour par rapport aux équipements réels.

Veuillez vous référer directement aux fichiers de sauvegarde (sauvegardés dans le dossier `ressources`) :

## 1. Commutateur d'Accès Layer 2 (dmd-sw-a1)

- 📄 **Fichier de configuration complet :** [dmd-sw-a1.txt](../../../ressources/configurations/dmd-sw-a1.txt)

## 2. Cœur de Réseau Layer 3 (dmd-sw-c1)

- 📄 **Fichier de configuration complet :** [dmd-sw-c1.txt](../../../ressources/configurations/dmd-sw-c1.txt)

## 3. Pare-feu Stormshield (dmd-fw-c1)

- 🛡️ **Fichier de configuration chiffré :** [dmd-fw-c1.na](../../../ressources/configurations/dmd-fw-c1.na) *(Nécessite le mot de passe d'archive)*

---

!!! tip "Bonnes Pratiques Git"
    Si vous modifiez la configuration sur un commutateur (ex: ajout d'un VLAN, modification d'un mot de passe), **n'oubliez pas d'écraser le fichier texte correspondant** et de faire un commit + push pour garder la documentation synchronisée avec la production !
