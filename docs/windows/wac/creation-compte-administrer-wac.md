---
description: Création d'un compte administrateur local pour WAC.
---

# BLOC 2 - Création d'un compte WAC

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 28/09/2026</p>
    <p><strong>Contexte :</strong> Administration WAC</p>
</div>

---

## 1. Sommaire

- [1. Sommaire](#1-sommaire)
- [2. Contexte](#2-contexte)
- [3. Création du compte pour Administrer WAC](#3-creation-du-compte-pour-administrer-wac)

## 2. Contexte

Le déploiement et la gestion de Windows Admin Center (WAC) requièrent des droits d'administration sur l'hôte. Cette procédure documente l'automatisation par script PowerShell de la création d'un utilisateur local dédié. L'intégration de ce compte au groupe de sécurité local "Administrateurs" lui octroie les privilèges système nécessaires pour administrer la plateforme WAC.

## 3. Création du compte pour Administrer WAC {#3-creation-du-compte-pour-administrer-wac}

3.1. **Création du compte utilisateur local.** Conversion du mot de passe en chaîne sécurisée et instanciation du compte système.

```powershell
$Password = ConvertTo-SecureString "etudiant_007" -AsPlainText -Force
New-LocalUser -Name "administrateurWAC1" -Password $Password -FullName "Administrateur WAC"
```

- `ConvertTo-SecureString` : Cmdlet convertissant une chaîne de caractères standard en une chaîne sécurisée chiffrée (SecureString) manipulable en mémoire.
- `-AsPlainText` : Paramètre indiquant que la chaîne fournie en entrée est en texte clair.
- `-Force` : Paramètre forçant l'exécution de la conversion, outrepassant l'avertissement de sécurité lié à l'utilisation du texte clair.
- `New-LocalUser` : Cmdlet créant un nouvel objet utilisateur dans la base SAM (Security Account Manager) de la machine locale.
- `-Name` : Argument définissant l'identifiant unique de connexion du compte (ici `administrateurWAC1`).
- `-Password` : Argument assignant l'objet SecureString stocké dans la variable `$Password` comme mot de passe.
- `-FullName` : Argument renseignant le nom d'affichage complet du profil utilisateur.

3.2. **Élévation des privilèges.** Ajout du compte nouvellement créé au groupe des administrateurs locaux pour débloquer les droits sur WAC.

```powershell
Add-LocalGroupMember -Group "Administrateurs" -Member "administrateurWAC1"
```

- `Add-LocalGroupMember` : Cmdlet modifiant l'appartenance d'un groupe de sécurité local en y ajoutant un nouveau membre.
- `-Group` : Argument désignant le nom du groupe cible disposant des hauts privilèges (ici `Administrateurs`).
- `-Member` : Argument spécifiant l'identifiant exact de l'utilisateur à intégrer au groupe (ici `administrateurWAC1`).
