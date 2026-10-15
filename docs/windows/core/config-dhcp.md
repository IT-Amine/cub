---
description: "Procédure de configuration et de haute disponibilité du service DHCP sur Windows Server 2025 Core"
---

# BLOC 2 - Configuration et Haute Disponibilité du Service DHCP sur Windows Server 2025 Core

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** INFRAMINE
> - **Date :** 15/10/2026
> - **Domaine :** Système & Réseau (DHCP)

---

## 1. Sommaire

- [2. Contexte](#2-contexte)
- [3. Installation et autorisation du rôle DHCP](#3-installation-et-autorisation-du-role-dhcp)
- [4. Configuration de l'étendue Clients (VLAN 10)](#4-configuration-de-letendue-clients-vlan-10)
- [5. Configuration de la redondance Actif / Actif (Load Balance 50/50)](#5-configuration-de-la-redondance-actif-actif-load-balance-5050)
- [6. Configuration de la redondance Actif / Passif (Hot Standby)](#6-configuration-de-la-redondance-actif-passif-hot-standby)
- [7. Configuration du relais DHCP Cisco (Switch L3)](#7-configuration-du-relais-dhcp-cisco-switch-l3)
- [8. Commandes d'exploitation et de diagnostic PowerShell](#8-commandes-dexploitation-et-de-diagnostic-powershell)
- [9. Sécurité et durcissement du service DHCP](#9-securite-et-durcissement-du-service-dhcp)

---

## 2. Contexte

Au sein de l'infrastructure CUB de l'agence de Dortmund, le service d'adressage dynamique DHCP est hébergé sur deux serveurs sous **Windows Server 2025 Core** situés dans le sous-réseau de production :
- **`ServeurDHCP1` (Serveur Local)** : Nœud administré (`192.168.4.4/25` - FQDN : `dhcp1.local.dortmund.cub.sioplc.fr`).
- **`ServeurDHCP0` (Serveur Partenaire)** : Second nœud (`192.168.4.3/25` - FQDN : `dhcp0.local.dortmund.cub.sioplc.fr`).

Cette procédure traite exclusivement du paramétrage logiciel du rôle DHCP et de sa haute disponibilité pour distribuer les configurations réseau aux équipements situés dans le **VLAN 10 (Clients : `192.168.4.128/26`)** via un agent relais configuré sur le commutateur de niveau 3.

---

## 3. Installation et autorisation du rôle DHCP

Toutes les commandes PowerShell sont exécutées en tant qu'administrateur sur le serveur local **`ServeurDHCP1`**.

3.1. **Installation du rôle DHCP et des outils RSAT.** Déploiement des binaires du service et des commandes d'administration PowerShell.

```powershell
Install-WindowsFeature -Name DHCP -IncludeManagementTools
```

- `-Name DHCP` : Spécifie le rôle serveur DHCP à installer.
- `-IncludeManagementTools` : Inclut le module PowerShell `DhcpServer` et les outils RSAT associés.

3.2. **Création des groupes de sécurité locaux et démarrage du service.** Initialisation des groupes Active Directory locaux pour l'administration déléguée et activation du service.

```powershell
Add-DhcpServerSecurityGroup
Set-Service -Name DHCPServer -StartupType Automatic
Restart-Service -Name DHCPServer
```

- `Add-DhcpServerSecurityGroup` : Crée les groupes de sécurité locaux `Utilisateurs DHCP` et `Administrateurs DHCP`.
- `-StartupType Automatic` : Configure le démarrage automatique du service au lancement du système.
- `Restart-Service -Name DHCPServer` : Redémarre le service pour appliquer les nouveaux groupes de sécurité.

3.3. **Autorisation du serveur DHCP dans Active Directory.** Déclaration de `ServeurDHCP1` dans la partition de configuration du domaine pour l'autoriser à émettre sur le réseau.

```powershell
Add-DhcpServerInDC -DnsName "dhcp1.local.dortmund.cub.sioplc.fr" -IPAddress "192.168.4.4"
Get-DhcpServerInDC
```

- `-DnsName` : Nom d'hôte FQDN du serveur DHCP à autoriser dans l'annuaire Active Directory.
- `-IPAddress` : Adresse IPv4 du serveur déclaré.
- `Get-DhcpServerInDC` : Liste l'ensemble des serveurs DHCP autorisés dans l'annuaire de l'entreprise.

---

## 4. Configuration de l'étendue Clients (VLAN 10)

4.1. **Création de l'étendue à l'état inactif.** Définition de la plage dynamique globale sur le sous-réseau `192.168.4.128/26`.

```powershell
Add-DhcpServerv4Scope `
    -Name "Clients" `
    -Description "Etendue DHCP VLAN 10 Clients - Situation 4 CUB" `
    -StartRange "192.168.4.130" `
    -EndRange "192.168.4.189" `
    -SubnetMask "255.255.255.192" `
    -LeaseDuration 4.00:00:00 `
    -State InActive
```

- `-Name "Clients"` : Désignation de l'étendue DHCP.
- `-StartRange "192.168.4.130"` et `-EndRange "192.168.4.189"` : Plage des adresses IP distribuées aux clients du VLAN 10.
- `-SubnetMask "255.255.255.192"` : Masque de sous-réseau `/26`.
- `-LeaseDuration 4.00:00:00` : Durée de validité du bail (4 jours selon le cahier des charges ; alternativement `0.04:00:00` pour 4 heures).
- `-State InActive` : Crée l'étendue à l'état inactif pour permettre la déclaration préalable des options et exclusions.

4.2. **Définition de la plage d'exclusion.** Réservation des adresses spécifiques (imprimantes, bornes Wi-Fi) pour empêcher leur distribution dynamique.

```powershell
Add-DhcpServerv4ExclusionRange `
    -ScopeId "192.168.4.128" `
    -StartRange "192.168.4.180" `
    -EndRange "192.168.4.189"
```

- `-ScopeId "192.168.4.128"` : Identifiant réseau du sous-réseau de l'étendue.
- `-StartRange` et `-EndRange` : Bornes de début et de fin de la plage d'adresses exclues du pool d'attribution.

4.3. **Configuration de la réservation statique.** Affectation permanente et exclusive d'une adresse IP basée sur l'adresse physique (MAC) de l'équipement.

```powershell
Add-DhcpServerv4Reservation `
    -ScopeId "192.168.4.128" `
    -IPAddress "192.168.4.179" `
    -ClientId "00-15-5D-01-A2-34" `
    -Name "Poste-VIP-Clients" `
    -Description "Reservation statique - Document 1"
```

- `-IPAddress "192.168.4.179"` : Adresse IP réservée.
- `-ClientId "00-15-5D-01-A2-34"` : Adresse MAC de l'équipement client cible.

4.4. **Configuration des options d'étendue (Passerelle, DNS et Suffixe).** Injection des options DHCP indispensables au routage et à la résolution de noms.

```powershell
Set-DhcpServerv4OptionValue -ScopeId "192.168.4.128" -Router "192.168.4.190"
Set-DhcpServerv4OptionValue -ScopeId "192.168.4.128" -DnsServer ("192.168.4.10", "192.168.4.11", "8.8.8.8")
Set-DhcpServerv4OptionValue -ScopeId "192.168.4.128" -DnsDomain "dortmund.cub.sioplc.fr"
```

- `-Router "192.168.4.190"` : Option 003 indiquant l'adresse de la passerelle par défaut (SVI L3 du VLAN 10).
- `-DnsServer` : Option 006 spécifiant les résolveurs DNS internes de l'agence (`192.168.4.10` et `192.168.4.11`) et le secours (`8.8.8.8`).
- `-DnsDomain "dortmund.cub.sioplc.fr"` : Option 015 définissant le suffixe DNS du domaine de l'agence.

4.5. **Activation et contrôle de l'étendue.** Basculement de l'étendue à l'état actif et contrôle de conformité des options.

```powershell
Set-DhcpServerv4Scope -ScopeId "192.168.4.128" -State Active
Get-DhcpServerv4Scope -ScopeId "192.168.4.128"
Get-DhcpServerv4OptionValue -ScopeId "192.168.4.128"
```

- `-State Active` : Rend l'étendue opérationnelle et prête à répondre aux requêtes DORA des clients.

---

## 5. Configuration de la redondance Actif / Actif (Load Balance 50/50)

5.1. **Création du partenariat Load Balance.** Répartition de la charge des attributions d'adresses entre `ServeurDHCP1` et `ServeurDHCP0` avec synchronisation automatique.

```powershell
Add-DhcpServerv4Failover `
    -Name "Failover-CUB-ActifActif" `
    -ScopeId "192.168.4.128" `
    -PartnerServer "dhcp0.local.dortmund.cub.sioplc.fr" `
    -Mode LoadBalance `
    -Percentage 50 `
    -MaxClientLeadTime 01:00:00 `
    -SharedSecret "cub" `
    -AutoStateTransition $true `
    -StateSwitchInterval 00:30:00
```

- `-PartnerServer` : FQDN du serveur DHCP partenaire (`ServeurDHCP0` sur `192.168.4.3`).
- `-Mode LoadBalance` : Mode de basculement avec répartition dynamique de charge.
- `-Percentage 50` : Répartition égale à 50% entre le serveur local et le partenaire.
- `-MaxClientLeadTime 01:00:00` : Délai MCLT fixé à 1 heure.
- `-SharedSecret "cub"` : Clé secrète partagée pour authentifier les échanges de synchronisation.
- `-AutoStateTransition $true` : Active la transition automatique en état d'interruption de communication.
- `-StateSwitchInterval 00:30:00` : Intervalle de basculement après 30 minutes de perte de contact.

5.2. **Réplication et validation du partenariat Actif/Actif.** Déclenchement de la synchronisation de l'étendue et vérification de l'état.

```powershell
Invoke-DhcpServerv4FailoverReplication -Name "Failover-CUB-ActifActif"
Get-DhcpServerv4Failover -Name "Failover-CUB-ActifActif"
```

- `Invoke-DhcpServerv4FailoverReplication` : Propage immédiatement la configuration de l'étendue vers `ServeurDHCP0`.
- `Get-DhcpServerv4Failover` : Affiche l'état de la relation (`Normal`).

---

## 6. Configuration de la redondance Actif / Passif (Hot Standby)

6.1. **Suppression de la relation précédente.** Nettoyage du partenariat Actif/Actif avant reconfiguration.

```powershell
Remove-DhcpServerv4Failover -Name "Failover-CUB-ActifActif" -Force
```

- `-Force` : Supprime la relation sans demander de confirmation interactive.

6.2. **Création du partenariat Hot Standby.** Mise en place du mode secours à chaud où `ServeurDHCP1` reste en réserve avec 10% des adresses du pool.

```powershell
Add-DhcpServerv4Failover `
    -Name "Failover-CUB-HotStandby" `
    -ScopeId "192.168.4.128" `
    -PartnerServer "dhcp0.local.dortmund.cub.sioplc.fr" `
    -Mode HotStandby `
    -ServerRole Standby `
    -ReservePercent 10 `
    -MaxClientLeadTime 01:00:00 `
    -SharedSecret "cub" `
    -AutoStateTransition $true `
    -StateSwitchInterval 00:30:00
```

- `-Mode HotStandby` : Basculement en mode secours à chaud (Actif/Passif).
- `-ServerRole Standby` : Désigne `ServeurDHCP1` comme serveur de réserve *(ou `Active` si ServeurDHCP1 assure le rôle principal nominal)*.
- `-ReservePercent 10` : Alloue un contingent de 10% des adresses pour les attributions d'urgence en cas de défaillance du partenaire.

6.3. **Synchronisation et validation du partenariat Actif/Passif.** Application des paramètres vers le serveur partenaire et contrôle de l'état.

```powershell
Invoke-DhcpServerv4FailoverReplication -Name "Failover-CUB-HotStandby"
Get-DhcpServerv4Failover -Name "Failover-CUB-HotStandby"
```

---

## 7. Configuration du relais DHCP Cisco (Switch L3)

7.1. **Configuration de l'agent relais IP Helper sur le commutateur cœur.** Encapsulation des requêtes de diffusion UDP 67/68 du VLAN 10 vers les adresses Unicast des serveurs DHCP en production (`192.168.4.4` et `192.168.4.3`).

```text
dmd-sw-coeur01# configure terminal
dmd-sw-coeur01(config)# interface Vlan 10
dmd-sw-coeur01(config-if)# ip address 192.168.4.190 255.255.255.192
dmd-sw-coeur01(config-if)# ip helper-address 192.168.4.4
dmd-sw-coeur01(config-if)# ip helper-address 192.168.4.3
dmd-sw-coeur01(config-if)# end
dmd-sw-coeur01# write memory
```

- `interface Vlan 10` : Sélectionne l'interface de routage SVI du réseau des postes clients.
- `ip helper-address 192.168.4.4` : Relaie les requêtes DHCP vers le serveur local `ServeurDHCP1`.
- `ip helper-address 192.168.4.3` : Relaie les requêtes DHCP vers le serveur secondaire `ServeurDHCP0`.
- `write memory` : Sauvegarde la configuration active dans la mémoire NVRAM du commutateur.

---

## 8. Commandes d'exploitation et de diagnostic PowerShell

8.1. **Matrice des commandes d'administration courante.** Commandes PowerShell pour le suivi opérationnel des baux et de la réplication sous Windows Server Core :

| Opération d'administration | Commande PowerShell (Windows Core) |
| :--- | :--- |
| **Consulter l'état de l'étendue** | `Get-DhcpServerv4Scope -ScopeId 192.168.4.128` |
| **Auditer l'occupation du pool** | `Get-DhcpServerv4ScopeStatistics -ScopeId 192.168.4.128` |
| **Lister les baux actifs délivrés** | `Get-DhcpServerv4Lease -ScopeId 192.168.4.128` |
| **Vérifier l'état de la redondance** | `Get-DhcpServerv4Failover` |
| **Déclencher la synchronisation Failover**| `Invoke-DhcpServerv4FailoverReplication -Name "Failover-CUB-ActifActif"` |
| **Consulter les exclusions déclarées**| `Get-DhcpServerv4ExclusionRange -ScopeId 192.168.4.128` |
| **Consulter les réservations statiques**| `Get-DhcpServerv4Reservation -ScopeId 192.168.4.128` |
| **Afficher les options distribuées** | `Get-DhcpServerv4OptionValue -ScopeId 192.168.4.128` |

---

## 9. Sécurité et durcissement du service DHCP

9.1. **Consulter la note technique dédiée.** L'analyse approfondie des menaces protocolaires (**DHCP Starvation** et **Rogue DHCP / Man-in-the-Middle**), ainsi que les contre-mesures techniques (**Port Security**, **Filtrage MAC** et **DHCP Snooping**) sont détaillées dans le document spécialisé :

$\rightarrow$ Consulter la [Note Technique de Sécurité : Vulnérabilités DHCP et Contre-Mesures](securite-dhcp.md).
