---
description: Documentation et procédure technique.
---

# BLOC 2 - DHCP Core

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 16/09/2026</p>
    <p><strong>Contexte :</strong> configuration du serveur DHCP Core</p>
</div>

---

## 1. Sommaire
- [1. Sommaire](#1-sommaire)
- [2. Contexte](#2-contexte)
- [3. Déploiement des utilitaires de virtualisation](#3-déploiement-des-utilitaires-de-virtualisation)
- [4. Configuration réseau statique](#4-configuration-reseau-statique)
- [5. Configuration NTP](#5-configuration-ntp)
- [6. Paramétrage Sécurité et Pare-feu](#6-paramétrage-securite-et-pare-feu)
- [7. Mise à jour du système](#7-mise-a-jour-du-systeme)
- [8. Sécurisation du compte local Administrateur](#8-securisation-du-compte-local-administrateur)
- [9. Installation et configuration du rôle DHCP](#9-installation-et-configuration-du-rôle-dhcp)

## 2. Contexte
Ce document détaille la procédure d'initialisation et de sécurisation (Hardening) du serveur Windows Server 2025 (édition Core) dédié au rôle DHCP. Il couvre la synchronisation temporelle indispensable à la cohérence des baux réseau, la configuration du pare-feu, la gestion des mises à jour centralisées via PowerShell, la sécurisation du compte administrateur local, l'intégration des pilotes VirtIO/QEMU nécessaires au fonctionnement optimal sur l'hyperviseur, ainsi que le déploiement du service DHCP.

## 3. Déploiement des utilitaires de virtualisation

### 3.1. Exécution des agents VirtIO.

Lancement de l'installateur des pilotes paravirtualisés depuis le support monté.

```powershell
Start-Process -FilePath "D:\virtio-win-guest-tools.exe"
```

- `Start-Process` : Exécute le binaire d'installation de l'agent invité QEMU.

### 3.2. Configuration du service QEMU-GA.

Définition du lancement automatique pour assurer la communication hyperviseur/machine virtuelle.

```powershell
Set-Service -Name "QEMU-GA" -StartupType Automatic
Start-Service QEMU-GA
```

- `-StartupType Automatic` : Garantit la disponibilité du service QEMU Guest Agent dès le démarrage de Windows Server.

## 4. Configuration réseau statique

### 9.1. Identification de l'interface réseau
Il faut d'abord repérer le numéro d'index (`ifIndex`) de la carte réseau virtuelle pour lui appliquer les paramètres.
```powershell
Get-NetAdapter
```
- Repérez la valeur dans la colonne `ifIndex` correspondant à votre carte réseau (généralement nommée Ethernet).

### 5.2. Attribution de l'adresse IP, du Masque et de la Passerelle
Utilisez l'index récupéré pour définir les paramètres IP statiques. *(Exemple avec l'index `3`, l'IP `192.168.4.11`, masque `/25` et la passerelle `192.168.4.126`)*.

```powershell
New-NetIPAddress -InterfaceIndex 3 -IPAddress "192.168.4.11" -PrefixLength 25 -DefaultGateway "192.168.4.126"
```
- `-InterfaceIndex` : L'index de la carte réseau (ici `3`).
- `-IPAddress` : L'adresse IP statique du serveur DHCP.
- `-PrefixLength` : La longueur du masque de sous-réseau en notation CIDR (ex: `25` pour `255.255.255.128`).
- `-DefaultGateway` : L'adresse IP de la passerelle par défaut.

### 4.3. Configuration des serveurs DNS
Configuration du serveur DNS pointant vers le contrôleur de domaine (AD) ou le DNS récursif.

```powershell
Set-DnsClientServerAddress -InterfaceIndex 3 -ServerAddresses ("192.168.4.10", "1.1.1.1")
```
- `-ServerAddresses` : Liste des adresses IP des serveurs DNS séparées par une virgule.

## 5. Configuration NTP

### 9.1. Configuration des pools de serveurs.

Établissement de la synchronisation manuelle sur les serveurs de temps publics pour garantir l'intégrité de l'horloge système.

```powershell
w32tm /config /manualpeerlist:"0.fr.pool.ntp.org 1.fr.pool.ntp.org" /syncfromflags:manual /reliable:yes /update
Restart-Service W32Time
w32tm /resync
```

- `/manualpeerlist` : Spécifie les adresses des pairs NTP externes.
- `/reliable:yes` : Indique que cet ordinateur est une source de temps fiable sur le réseau.

### 5.2. Validation des homologues NTP.

Contrôle de l'état du service de temps local.

```powershell
w32tm /query /peers
w32tm /query /status
```

- `/peers` : Affiche l'état des connexions avec les serveurs de temps configurés.
- `/status` : Renvoie les détails sur la latence, la précision et la dernière synchronisation effectuée.

## 6. Paramétrage Sécurité et Pare-feu

### 9.1. Vérification UAC et Profils Pare-feu.

Audit des politiques de pare-feu globales (Domaine, Privé, Public).

```powershell
Get-NetFirewallProfile | Select-Object Name, Enabled
```

- `Select-Object Name, Enabled` : Filtre l'affichage pour confirmer que chaque profil réseau dispose du pare-feu actif.

## 7. Mise à jour du système

### 9.1. Téléchargement et installation des KBs.

Utilisation de l'API Windows Update pour mettre le système en conformité via le module PSWindowsUpdate.

```powershell
Get-Service -Name wuauserv
Start-Service -Name wuauserv
UsoClient StartScan

Install-Module PSWindowsUpdate
Install-WindowsUpdate -AcceptAll -Install
Restart-Computer 
```

- `UsoClient StartScan` : Force le lancement asynchrone de la recherche de mises à jour.
- `-AcceptAll -Install` : Approuve et installe automatiquement tous les correctifs approuvés sans interaction manuelle.

!!! warning "Action requise"
    Un redémarrage du système (`Restart-Computer`) est strictement requis après la passe d'installation des correctifs cumulatifs.

## 8. Sécurisation du compte local Administrateur

### 9.1. Renommage et changement de mot de passe.

Modification du nom d'utilisateur associé au SID 500 pour compliquer les attaques par énumération, et renouvellement du mot de passe avec une entrée sécurisée.

```powershell
Get-LocalUser -Name "Administrateur" | Select-Object Name, SID, Enabled
Rename-LocalUser -Name "Administrateur" -NewName "ADM-SRV-01"
Get-LocalUser -Name "ADM-SRV-01" | Select-Object Name, SID, Enabled
Set-LocalUser -Name "ADM-SRV-01" -Password (Read-Host "Nouveau mot de passe" -AsSecureString)
```

- `Rename-LocalUser` : Modifie le SAMAccountName local.
- `-AsSecureString` : Chiffre la saisie du mot de passe stocké en mémoire vive pendant la transaction.

