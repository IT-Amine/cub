---
description: Procédure de déploiement et de configuration initiale pour le serveur BLOC 2 - AD1 Core.
---

# BLOC 2 - AD1 Core

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere_cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 09/09/2026</p>
    <p><strong>Contexte :</strong> configuration du serveur AD1 Core</p>
</div>

---

## 1. Sommaire
- [1. Sommaire](#1-sommaire)
- [2. Contexte](#2-contexte)
- [3. Déploiement des utilitaires de virtualisation](#3-déploiement-des-utilitaires-de-virtualisation)
- [4. Configuration NTP](#4-configuration-ntp)
- [5. Paramétrage Sécurité et Pare-feu](#5-paramétrage-sécurité-et-pare-feu)
- [6. Mise à jour du système](#6-mise-à-jour-du-système)
- [7. Sécurisation du compte local Administrateur](#7-sécurisation-du-compte-local-administrateur)

## 2. Contexte
Ce document détaille la procédure d'initialisation et de sécurisation (Hardening) du serveur Windows Server 2025 (édition Core) nommé AD1 Core. Il couvre la synchronisation temporelle indispensable à Active Directory, la configuration du pare-feu, la gestion des mises à jour centralisées via PowerShell, la sécurisation du compte administrateur local, ainsi que l'intégration des pilotes VirtIO/QEMU nécessaires au fonctionnement optimal sur l'hyperviseur.

## 3. Déploiement des utilitaires de virtualisation

### 3.1. Exécution des agents VirtIO. Lancement de l'installateur des pilotes paravirtualisés depuis le support monté.
```powershell
Start-Process
```
Puis mettre dans le FilePath : "D:\virtio-win-guest-tools.exe"

- Start-Process : Exécute le binaire d'installation de l'agent invité QEMU.

![Dossier CD](assets/ad/lscd.png)
![Start Process](assets/ad/startprocess.png)
![QEMU1](assets/ad/qemu1.png)

### 3.2. Configuration du service QEMU-GA. Définition du lancement automatique pour assurer la communication hyperviseur/machine virtuelle.
```powershell
Set-Service -Name "QEMU-GA" -StartupType Automatic
Start-Service QEMU-GA
```

- -StartupType Automatic : Garantit la disponibilité du service QEMU Guest Agent dès le démarrage de Windows Server.

![QEMU-GA](assets/ad/qemu2.png)

## 4. Configuration NTP

### 4.1. Configuration des pools de serveurs. Établissement de la synchronisation manuelle sur les serveurs de temps publics pour garantir l'intégrité de l'horloge système.

```powershell title="Configuration W32Time"
w32tm /config /manualpeerlist:"0.fr.pool.ntp.org 1.fr.pool.ntp.org" /syncfromflags:manual /reliable:yes /update
Restart-Service W32Time
w32tm /resync
```
- /manualpeerlist : Spécifie les adresses des pairs NTP externes.
- /reliable:yes : Indique que cet ordinateur est une source de temps fiable (nécessaire pour un futur contrôleur de domaine).

![Configuration NTP](assets/ad/ntp.png)

### 4.2. Validation des homologues NTP. Contrôle de l'état du service de temps local.
```powershell
w32tm /query /peers
w32tm /query /status
```
- /peers : Affiche l'état des connexions avec les serveurs de temps configurés.
- /status : Renvoie les détails sur la latence, la précision et la dernière synchronisation effectuée.

![Validation NTP](assets/ad/ntp23.png)

## 5. Paramétrage Sécurité et Pare-feu

### 5.1. Vérification UAC et Profils Pare-feu. Audit des politiques de pare-feu globales (Domaine, Privé, Public).
```powershell
Get-NetFirewallProfile | Select-Object Name, Enabled
Get-NetFirewallProfile
Select-Object Name, Enabled # Filtre l'affichage pour confirmer que chaque profil réseau dispose du pare-feu actif.
```

![Profils Pare-feu](assets/ad/firewall.png)

## 6. Mise à jour du système

### 6.1. Téléchargement et installation des KBs. Utilisation de l'API Windows Update pour mettre le système en conformité via le module PSWindowsUpdate.
```powershell
Get-Service -Name wuauserv
Start-Service -Name wuauserv
UsoClient StartScan

Install-Module PSWindowsUpdate
Install-WindowsUpdate -AcceptAll -Install
Restart-Computer 
```

- UsoClient StartScan : Force le lancement asynchrone de la recherche de mises à jour.
- -AcceptAll -Install : Approuve et installe automatiquement tous les correctifs approuvés sans interaction manuelle.

![Mise à jour](assets/ad/update.png)

!!! warning "Action requise"
Un redémarrage du système (Restart-Computer) est strictement requis après la passe d'installation des correctifs cumulatifs.

## 7. Sécurisation du compte local Administrateur

### 7.1. Renommage et changement de mot de passe. Modification du nom d'utilisateur associé au SID 500 pour compliquer les attaques par énumération, et renouvellement du mot de passe avec une entrée sécurisée.
```powershell
Get-LocalUser -Name "Administrateur" | Select-Object Name, SID, Enabled
Rename-LocalUser -Name "Administrateur" -NewName "ADM-SRV-01"
Get-LocalUser -Name "ADM-SRV-01" | Select-Object Name, SID, Enabled
Set-LocalUser -Name "ADM-SRV-01" -Password (Read-Host "Nouveau mot de passe" -AsSecureString)
```
- Rename-LocalUser : Modifie le SAMAccountName local.
- -AsSecureString : Chiffre la saisie du mot de passe stocké en mémoire vive pendant la transaction.

![Sécurisation SID](assets/ad/SID.png)
![Renommage SID](assets/ad/SID2.png)