---
description: "Procédure d'initialisation et de configuration du contrôleur de domaine Active Directory sous Windows Server 2025 Core"
---

# BLOC 2 - Initialisation et Configuration du Contrôleur de Domaine AD Core

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** INFRAMINE
> - **Date :** 09/09/2026
> - **Domaine :** Système & Annuaire (Active Directory)

---

## 1. Sommaire

- [2. Contexte](#2-contexte)
- [3. Déploiement des utilitaires de virtualisation](#3-deploiement-des-utilitaires-de-virtualisation)
- [4. Configuration du service de temps (NTP / W32Time)](#4-configuration-du-service-de-temps-ntp-w32time)
- [5. Paramétrage de la sécurité et du pare-feu](#5-parametrage-de-la-securite-et-du-pare-feu)
- [6. Maintenance et mise à jour du système](#6-maintenance-et-mise-a-jour-du-systeme)
- [7. Sécurisation du compte local Administrateur](#7-securisation-du-compte-local-administrateur)
- [8. Installation du rôle Active Directory Domain Services (AD DS)](#8-installation-du-role-active-directory-domain-services-ad-ds)
- [9. Déploiement de la forêt et promotion du Contrôleur de Domaine principal](#9-deploiement-de-la-foret-et-promotion-du-controleur-de-domaine-principal)
- [10. Promotion du second Contrôleur de Domaine (Haute Disponibilité)](#10-promotion-du-second-controleur-de-domaine-haute-disponibilite)
- [11. Vérification de l'état de santé et de la réplication Active Directory](#11-verification-de-letat-de-sante-et-de-la-replication-active-directory)
- [12. Initialisation de l'arborescence des Unités d'Organisation (OU)](#12-initialisation-de-larborescence-des-unites-dorganisation-ou)

---

## 2. Contexte

Ce document détaille la procédure d'initialisation logicielle et de sécurisation (Hardening) du serveur Windows Server 2025 (édition Core) destiné au rôle de contrôleur de domaine Active Directory (`ServeurAD1` / `ServeurAD0`) au sein du sous-réseau de Production (VLAN 54).

Il couvre l'intégration des pilotes de paravirtualisation nécessaires au fonctionnement sur l'hyperviseur, l'alignement temporel strict requis par le protocole d'authentification Kerberos, l'audit du pare-feu avancé, l'application automatisée des correctifs de sécurité, ainsi que la protection du compte d'administration local.

---

## 3. Déploiement des utilitaires de virtualisation

Toutes les actions sont exécutées dans une console PowerShell avec élévation des privilèges.

3.1. **Exécution de l'installateur des pilotes paravirtualisés.** Lancement de l'agent invité QEMU depuis le support monté.

```powershell
Start-Process -FilePath "D:\virtio-win-guest-tools.exe"
```

- `-FilePath` : Chemin absolu vers l'exécutable d'installation des outils VirtIO sur le lecteur virtuel D:.

3.2. **Configuration du service QEMU Guest Agent.** Activation du démarrage automatique du service pour garantir la communication continue avec l'hyperviseur.

```powershell
Set-Service -Name "QEMU-GA" -StartupType Automatic
Start-Service -Name "QEMU-GA"
```

- `-Name "QEMU-GA"` : Nom du service Windows associé à l'agent invité.
- `-StartupType Automatic` : Configure le service pour un démarrage automatique dès le boot de Windows.

---

## 4. Configuration du service de temps (NTP / W32Time)

4.1. **Configuration des sources de temps NTP externes.** Paramétrage de la synchronisation manuelle sur les serveurs de temps de référence pour assurer la validité des tickets Kerberos.

```powershell title="Configuration W32Time"
w32tm /config /manualpeerlist:"0.fr.pool.ntp.org 1.fr.pool.ntp.org" /syncfromflags:manual /reliable:yes /update
Restart-Service W32Time
w32tm /resync
```

- `/manualpeerlist` : Liste des serveurs NTP publics fiables interrogés par le démon de temps.
- `/reliable:yes` : Déclare ce serveur comme source temporelle fiable pour les clients du domaine.
- `/syncfromflags:manual` : Impose la synchronisation d'après la liste manuelle définie.
- `Restart-Service W32Time` : Redémarre le service Windows Time pour charger les nouvelles directives.

4.2. **Validation des homologues NTP.** Contrôle de l'état de synchronisation et de la dérive de l'horloge système.

```powershell
w32tm /query /peers
w32tm /query /status
```

- `/peers` : Affiche l'état des connexions établies avec les serveurs NTP distants.
- `/status` : Renvoie les informations d'état, la précision et la source de temps active.

---

## 5. Paramétrage de la sécurité et du pare-feu

5.1. **Contrôle de l'état des profils du pare-feu Windows.** Vérification de l'activation des profils de filtrage (Domaine, Privé, Public).

```powershell
Get-NetFirewallProfile | Select-Object Name, Enabled
```

- `Get-NetFirewallProfile` : Interroge les profils de sécurité du pare-feu Windows avec fonctions avancées de sécurité.
- `Select-Object Name, Enabled` : Filtre la sortie pour n'afficher que le nom du profil et son état opérationnel.

---

## 6. Maintenance et mise à jour du système

6.1. **Installation du module de mise à jour Windows Update.** Automatisation du téléchargement et du déploiement des correctifs de sécurité via PowerShell.

```powershell
Get-Service -Name wuauserv
Start-Service -Name wuauserv

Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force
Install-Module -Name PSWindowsUpdate -Force
Install-WindowsUpdate -AcceptAll -Install
```

- `Start-Service -Name wuauserv` : Démarre le service Windows Update s'il est inactif.
- `Install-Module -Name PSWindowsUpdate` : Rapatrie le module PowerShell de gestion des KBs.
- `Install-WindowsUpdate -AcceptAll -Install` : Télécharge et applique l'ensemble des correctifs sans invite interactive.

> [!warning] Redémarrage requis
> L'application des mises à jour cumulatives nécessite un redémarrage système pour finaliser l'installation :
> ```powershell
> Restart-Computer
> ```

---

## 7. Sécurisation du compte local Administrateur

7.1. **Renommage du compte administrateur local (SID 500).** Modification du nom d'utilisateur par défaut pour neutraliser les attaques par énumération et force brute ciblées sur le compte Administrateur natif.

```powershell
Get-LocalUser -Name "Administrateur" | Select-Object Name, SID, Enabled
Rename-LocalUser -Name "Administrateur" -NewName "ADM-SRV-01"
Get-LocalUser -Name "ADM-SRV-01" | Select-Object Name, SID, Enabled
```

- `Rename-LocalUser` : Renomme le compte local sans altérer son identifiant de sécurité immuable (SID).
- `-NewName "ADM-SRV-01"` : Nouveau nom attribué au compte d'administration locale.

7.2. **Renouvellement sécurisé du mot de passe administrateur.** Définition d'un mot de passe robuste via une saisie masquée en mémoire vive.

```powershell
Set-LocalUser -Name "ADM-SRV-01" -Password (Read-Host "Nouveau mot de passe" -AsSecureString)
```

- `-AsSecureString` : Chiffre la saisie du mot de passe dans l'invite pour éviter toute exposition en clair dans l'historique PowerShell.

---

## 8. Installation du rôle Active Directory Domain Services (AD DS)

8.1. **Déploiement des binaires AD DS et des modules d'administration.** Installation du rôle d'annuaire et des outils RSAT PowerShell associés sans redémarrage automatique.

```powershell
Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
```

- `-Name AD-Domain-Services` : Identifiant du rôle d'annuaire LDAP / Kerberos de Microsoft.
- `-IncludeManagementTools` : Déploie le module PowerShell `ActiveDirectory`, les utilitaires en ligne de commande (`dcdiag`, `repadmin`, `ntdsutil`) et les consoles RSAT.

---

## 9. Déploiement de la forêt et promotion du Contrôleur de Domaine principal

Cette étape est exécutée sur le premier serveur (`ServeurAD0`) pour initialiser la forêt racine et la zone DNS intégrée.

9.1. **Saisie sécurisée du mot de passe de restauration des services d'annuaire (DSRM).**

```powershell
$DSRMPassword = Read-Host "Saisir le mot de passe DSRM (Restauration d'annuaire)" -AsSecureString
```

- `-AsSecureString` : Conserve le secret DSRM sous forme chiffrée en mémoire volatile.

9.2. **Instanciation de la nouvelle forêt Active Directory.** Déploiement de la base NTDS et intégration automatique du serveur DNS.

```powershell
Install-ADDSForest `
    -DomainName "local.dortmund.cub.sioplc.fr" `
    -DomainNetbiosName "DORTMUND" `
    -DomainMode "WinThreshold" `
    -ForestMode "WinThreshold" `
    -InstallDns:$true `
    -CreateDnsDelegation:$false `
    -DatabasePath "C:\Windows\NTDS" `
    -LogPath "C:\Windows\NTDS" `
    -SysvolPath "C:\Windows\SYSVOL" `
    -SafeModeAdministratorPassword $DSRMPassword `
    -Force:$true
```

- `-DomainName "local.dortmund.cub.sioplc.fr"` : Nom FQDN complet du domaine d'entreprise interne.
- `-DomainNetbiosName "DORTMUND"` : Identifiant NetBIOS hérité pour les clients et applications compatibles.
- `-DomainMode / -ForestMode "WinThreshold"` : Définit le niveau fonctionnel le plus récent supporté par Windows Server (Windows Server 2025 / 2016).
- `-InstallDns:$true` : Active l'installation et la configuration automatique du serveur DNS intégré à Active Directory.
- `-CreateDnsDelegation:$false` : Empêche la tentative de mise à jour automatique d'une délégation parente sur les serveurs DNS externes non autorisés.
- `-DatabasePath / -LogPath / -SysvolPath` : Spécifie les répertoires de stockage officiels de la base NTDS et du partage SYSVOL.
- `-Force:$true` : Ignore les alertes de compatibilité non bloquantes et force le redémarrage automatique post-promotion.

---

## 10. Promotion du second Contrôleur de Domaine (Haute Disponibilité)

Cette étape est exécutée sur le deuxième serveur (`ServeurAD1`) pour créer un nœud réplica et éliminer le point unique de défaillance (SPOF) d'authentification.

> [!important] Prérequis DNS
> Avant la promotion, `ServeurAD1` doit pointer vers l'adresse IP de `ServeurAD0` (`192.168.4.1`) comme serveur DNS principal pour être en mesure de résoudre les enregistrements SRV du domaine.

10.1. **Saisie des identifiants d'administration et du mot de passe DSRM.**

```powershell
$CredAdmin = Get-Credential -UserName "DORTMUND\Administrateur" -Message "Saisir les identifiants d'administration du domaine"
$DSRMPasswordReplica = Read-Host "Saisir le mot de passe DSRM du réplica" -AsSecureString
```

- `Get-Credential` : Instancie un objet PSCredential pour autoriser la jonction et la promotion dans le domaine existant.

10.2. **Promotion du réplica dans le domaine existant.**

```powershell
Install-ADDSDomainController `
    -DomainName "local.dortmund.cub.sioplc.fr" `
    -Credential $CredAdmin `
    -InstallDns:$true `
    -SiteName "Default-First-Site-Name" `
    -ReplicationSourceDC "ad0.local.dortmund.cub.sioplc.fr" `
    -DatabasePath "C:\Windows\NTDS" `
    -LogPath "C:\Windows\NTDS" `
    -SysvolPath "C:\Windows\SYSVOL" `
    -SafeModeAdministratorPassword $DSRMPasswordReplica `
    -Force:$true
```

- `-ReplicationSourceDC` : Spécifie le contrôleur de domaine source pour la réplication initiale de la partition d'annuaire.
- `-InstallDns:$true` : Installe le rôle DNS répliqué pour garantir la résilience de la résolution de noms.

---

## 11. Vérification de l'état de santé et de la réplication Active Directory

11.1. **Contrôle de l'inventaire des contrôleurs de domaine.**

```powershell
Get-ADDomainController -Filter * | Select-Object Name, IPv4Address, Site, OperatingSystem, IsGlobalCatalog
```

- `Get-ADDomainController` : Énumère l'ensemble des DCs actifs enregistrés dans la partition de configuration.

11.2. **Contrôle de l'état des tests d'intégrité (DCDiag).**

```powershell
dcdiag /v /c /d /e
```

- `/v` : Mode verbeux détaillé.
- `/c` : Exécute l'intégralité des tests de cohérence (DNS, NetLogon, FSMO, Kerberos).
- `/e` : Teste l'ensemble des serveurs de la forêt.

11.3. **Validation de la réplication multimaître.**

```powershell
repadmin /replsummary
repadmin /showrepl * /csv | ConvertFrom-Csv | Out-GridView
```

- `repadmin /replsummary` : Affiche un résumé synthétique des deltas et des erreurs de réplication entre les nœuds.

---

## 12. Initialisation de l'arborescence des Unités d'Organisation (OU)

12.1. **Création de la structure hiérarchique conforme aux standards de gouvernance CUB.**

```powershell
$BaseOU = "DC=local,DC=dortmund,DC=cub,DC=sioplc,DC=fr"

New-ADOrganizationalUnit -Name "CUB_Dortmund" -Path $BaseOU -ProtectedFromAccidentalDeletion $true
New-ADOrganizationalUnit -Name "Administration" -Path "OU=CUB_Dortmund,$BaseOU" -ProtectedFromAccidentalDeletion $true
New-ADOrganizationalUnit -Name "Production" -Path "OU=CUB_Dortmund,$BaseOU" -ProtectedFromAccidentalDeletion $true
New-ADOrganizationalUnit -Name "Clients" -Path "OU=CUB_Dortmund,$BaseOU" -ProtectedFromAccidentalDeletion $true
New-ADOrganizationalUnit -Name "Serveurs" -Path "OU=CUB_Dortmund,$BaseOU" -ProtectedFromAccidentalDeletion $true
New-ADOrganizationalUnit -Name "Groupes" -Path "OU=CUB_Dortmund,$BaseOU" -ProtectedFromAccidentalDeletion $true
```

- `New-ADOrganizationalUnit` : Crée les conteneurs organisationnels pour l'application future des stratégies de groupe (GPO).
- `-ProtectedFromAccidentalDeletion $true` : Verrouille l'OU contre toute suppression impromptue (contrôle d'intégrité ANSSI).