---
description: Documentation et procédure technique.
---

# BLOC 2 - Procédure : Extension du volume système (C:) sur machine virtuelle

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 09/09/2026</p>
    <p><strong>Contexte :</strong> configuration serveur Core</p>
</div>

---

## 1. Objectif
Augmenter la capacité de la partition système `C:` (ajout de 50 Go) sur un serveur Windows virtualisé. Cette opération nécessite d'agrandir le disque virtuel depuis l'hyperviseur, puis de supprimer une partition de récupération bloquante avant d'étendre le volume dans l'OS.

## 2. Prérequis
* Accès à l'interface d'administration de l'hyperviseur (ex: Proxmox).
* Privilèges administrateur sur le serveur Windows cible.
* Une sauvegarde à jour ou un snapshot de la machine virtuelle avant toute manipulation des partitions.

---

## 3. Agrandissement du disque virtuel (Hyperviseur)
Avant de modifier la table des partitions dans Windows, il est impératif d'augmenter la taille physique du disque virtuel alloué à la machine.

**Sous Proxmox VE :**
1. Éteindre la machine virtuelle (recommandé).
2. Sélectionner la machine virtuelle dans l'arborescence.
3. Se rendre dans le menu **Hardware** (Matériel).
4. Sélectionner le disque dur cible (**Hard Disk**).
5. Cliquer sur le menu déroulant **Disk Action** > **Resize** (Redimensionner).
6. Entrer la valeur d'ajout d'espace (ex: `+50G`) et valider.
7. Démarrer la machine virtuelle.

---

## 4. Actualisation et suppression de la partition bloquante (Diskpart)
Windows place généralement une partition de récupération immédiatement après le lecteur `C:`. Le nouvel espace non alloué s'ajoutant à la fin du disque physique, cette partition de récupération empêche l'extension du lecteur `C:` (l'espace libre doit être strictement contigu). Il faut la supprimer via l'utilitaire en ligne de commande `diskpart`.

> **Attention :** La suppression de la partition de récupération supprime l'accès aux outils de dépannage avancés locaux (WinRE). Dans un environnement virtualisé professionnel bénéficiant de snapshots et de sauvegardes complètes, la présence de cette partition locale n'est pas critique.

Ouvrir une invite de commandes en tant qu'Administrateur et exécuter :

    diskpart

Dans l'utilitaire Diskpart, lancer l'actualisation des disques et identifier la partition :

    DISKPART> rescan
    DISKPART> select disk 0
    DISKPART> list partition

*Note : Repérer le numéro de la partition de récupération (généralement la partition 3, d'une taille d'environ 800 Mo).*

Supprimer la partition ciblée (remplacer `X` par le numéro identifié à l'étape précédente) :

    DISKPART> select partition X
    DISKPART> delete partition override
    DISKPART> exit

**Explication des commandes :**
* `rescan` : Force Windows à scanner le bus matériel pour détecter le nouvel espace de 50 Go ajouté depuis l'hyperviseur.
* `delete partition override` : Force la suppression d'une partition système protégée, ce qu'une simple suppression classique refuserait de faire.

---

## 5. Extension du volume système (C:)
Une fois la partition bloquante supprimée, l'espace non alloué se retrouve directement collé à droite de la partition `C:`, autorisant son extension.

**Méthode graphique (Gestion des disques) :**
1. Ouvrir le gestionnaire de disques (`diskmgmt.msc`).
2. Faire un clic droit sur le volume **(C:)**.
3. Sélectionner **Étendre le volume...**
4. Suivre l'assistant de configuration en laissant les valeurs par défaut pour utiliser l'intégralité du nouvel espace disponible.

**Méthode en ligne de commande (PowerShell) :**
Cette méthode est particulièrement adaptée aux environnements Windows Server Core dépourvus d'interface graphique.

    Resize-Partition -DriveLetter C -Size (Get-PartitionSupportedSize -DriveLetter C).SizeMax