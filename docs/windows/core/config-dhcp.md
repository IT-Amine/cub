---
description: "Procédure de configuration et de haute disponibilité du service DHCP sur Windows Server 2025 Core"
---

# BLOC 2 - Configuration et Haute Disponibilité du Service DHCP sur Windows Server 2025 Core

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** Amine
> - **Date :** 04/11/2026
> - **Domaine :** Système & Réseau (DHCP)

---

## 1. Sommaire

- [2. Contexte](#2-contexte)
- [3. Prérequis liés à l'environnement Workgroup](#3-prerequis-lies-a-lenvironnement-workgroup)
- [4. Installation du rôle DHCP](#4-installation-du-role-dhcp)
- [5. Configuration de l'étendue Clients (VLAN 10)](#5-configuration-de-letendue-clients-vlan-10)
- [6. Configuration de la redondance Actif / Passif (Hot Standby)](#6-configuration-de-la-redondance-actif-passif-hot-standby)
- [7. Configuration du relais DHCP Cisco (Switch L3)](#7-configuration-du-relais-dhcp-cisco-switch-l3)
- [8. Commandes d'exploitation et de diagnostic](#8-commandes-dexploitation-et-de-diagnostic)
- [9. Sécurité et durcissement du service DHCP](#9-securite-et-durcissement-du-service-dhcp)

---

## 2. Contexte

Au sein de l'infrastructure CUB de l'agence de Dortmund, le service d'adressage dynamique DHCP est hébergé sur deux serveurs sous **Windows Server 2025 Core** situés dans le sous-réseau de production (**VLAN 54 : `192.168.4.0/25`**), hors domaine Active Directory (**Workgroup**) :

- **SERVEURDHCP0 (Serveur Actif / Maître)** : `192.168.4.3`
- **SERVEURDHCP1 (Serveur de Secours / Esclave)** : `192.168.4.4`
- **Compte d'administration commun** : `adm-srv-dhcp`

Cette procédure détaille le déploiement du service et de sa redondance logicielle (**Failover Hot Standby**) pour distribuer les baux réseau au **VLAN 10 (Clients : `192.168.4.128/26`)**.

---

## 3. Prérequis liés à l'environnement Workgroup

3.1. **Configuration du profil réseau et du pare-feu.** Modification de la catégorie de la carte réseau et ouverture des flux pour le trafic de basculement. À exécuter sur les deux serveurs (`SERVEURDHCP0` et `SERVEURDHCP1`).

```powershell title="prerequis_reseau.ps1"
Get-NetConnectionProfile | Where-Object NetworkCategory -eq 'Public' | Set-NetConnectionProfile -NetworkCategory Private
Get-NetFirewallRule -DisplayName *DHCP*Failover | Enable-NetFirewallRule
```

- `-NetworkCategory Private` : Passe la carte en réseau privé pour éviter le blocage des règles DHCP par le profil pare-feu public.
- `Enable-NetFirewallRule` : Active l'écoute sur le port TCP 647 (entrant/sortant) requis par le protocole de basculement Failover.

3.2. **Désactivation du filtrage des jetons locaux.** Autorisation de l'administration réseau à distance pour le compte `adm-srv-dhcp` (l'UAC étant déjà désactivé ou actif). À exécuter sur les deux serveurs.

```powershell
New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "LocalAccountTokenFilterPolicy" -Value 1 -PropertyType DWord -Force
Restart-Service WinRM
```

- `-Name "LocalAccountTokenFilterPolicy"` : Clé de registre autorisant l'authentification réseau avec privilèges élevés complets (Full Admin Token) en environnement Workgroup.
- `Restart-Service WinRM` : Redémarre le service Windows Remote Management pour appliquer immédiatement la politique de jeton d'élévation.

---

## 4. Installation du rôle DHCP

4.1. **Installation des binaires du service et des outils de gestion.** Déploiement du rôle serveur sur les deux nœuds (`SERVEURDHCP0` et `SERVEURDHCP1`).

```powershell
Install-WindowsFeature -Name DHCP -IncludeManagementTools
```

- `-Name DHCP` : Désigne le rôle serveur DHCP.
- `-IncludeManagementTools` : Déploie les modules d'administration PowerShell (`DhcpServer`) et outils RSAT.

4.2. **Initialisation des groupes de sécurité et démarrage du service.** Activation et contrôle de l'état d'exécution du démon DHCP.

```powershell
Add-DhcpServerSecurityGroup
Set-Service -Name DHCPServer -StartupType Automatic
Restart-Service -Name DHCPServer
```

- `Add-DhcpServerSecurityGroup` : Crée les groupes de sécurité locaux `Utilisateurs DHCP` et `Administrateurs DHCP`.
- `-StartupType Automatic` : Active le démarrage automatique du service au lancement du système.
- `Restart-Service -Name DHCPServer` : Redémarre le service pour valider son bon fonctionnement.

> [!warning] "Contrainte Workgroup"
> L'appartenance à un domaine n'étant pas exigée, les serveurs en Workgroup ne doivent pas être autorisés dans Active Directory. La commande `Add-DhcpServerInDC` est proscrite ici.

---

## 5. Configuration de l'étendue Clients (VLAN 10)

5.1. **Création de l'étendue et configuration de la plage IP.** Opérations à exécuter uniquement sur **SERVEURDHCP0 (`192.168.4.3`)**. La plage ne doit pas exister sur le partenaire `SERVEURDHCP1` (elle sera répliquée par le Failover).

```powershell
Add-DhcpServerv4Scope -Name "Clients - VLAN 10" -StartRange 192.168.4.130 -EndRange 192.168.4.189 -SubnetMask 255.255.255.192 -LeaseDuration 4.00:00:00 -State Active
```

- L’identifiant de l’étendue est `192.168.4.128`, déduit de la plage et du masque.
- `-StartRange 192.168.4.130` / `-EndRange 192.168.4.189` : Bornes de la plage de distribution dynamique d'adresses IPv4.
- `-SubnetMask 255.255.255.192` : Masque de sous-réseau `/26` correspondant au découpage VLSM.
- `-LeaseDuration 4.00:00:00` : Durée du bail fixée à 4 jours.
- `-State Active` : Active immédiatement l'étendue pour distribution.

5.2. **Définition de l'exclusion, de la réservation et des options DHCP.**

> [!note] Les postes membres utilisent les DNS AD ; ceux-ci peuvent transmettre les requêtes non locales à Unbound. Voir la [procédure de coopération DNS](../../services/dns/cooperation-dns-ad-unbound-bind.md).

```powershell
Add-DhcpServerv4ExclusionRange -ScopeId 192.168.4.128 -StartRange 192.168.4.180 -EndRange 192.168.4.189
Add-DhcpServerv4Reservation -ScopeId 192.168.4.128 -IPAddress 192.168.4.179 -ClientId "00-15-5D-01-A2-34" -Name "Poste-VIP-Clients"
Set-DhcpServerv4OptionValue -ScopeId 192.168.4.128 -Router 192.168.4.190
Set-DhcpServerv4OptionValue -ScopeId 192.168.4.128 -DnsServer 192.168.4.1,192.168.4.2
Set-DhcpServerv4OptionValue -ScopeId 192.168.4.128 -DnsDomain "local.dortmund.cub.sioplc.fr"
```

- `Add-DhcpServerv4ExclusionRange` : Exclut la plage `192.168.4.180` à `192.168.4.189` pour les équipements à adressage fixe (imprimantes réseau, bornes).
- `Add-DhcpServerv4Reservation` : Réserve l'adresse IP statique `192.168.4.179` liée à l'adresse MAC du poste client VIP.
- `-Router 192.168.4.190` : Injection de l'option 3 (Passerelle par défaut / SVI VLAN 10 du commutateur L3).
- `-DnsServer 192.168.4.1,192.168.4.2` : Contrôleurs de domaine DNS internes (option 6). Vérifier leur résolution des noms externes et les flux DNS avant déploiement.
- `-DnsDomain "local.dortmund.cub.sioplc.fr"` : Injection de l'option 15 (Suffixe DNS principal).

---

## 6. Configuration de la redondance Actif / Passif (Hot Standby)

6.1. **Création de la relation de basculement.** Commande à exécuter uniquement sur **SERVEURDHCP0 (`192.168.4.3`)** dans la session `adm-srv-dhcp`.

```powershell
Add-DhcpServerv4Failover -Name 'Failover-CUB-HotStandby' -PartnerServer '192.168.4.4' -ScopeId 192.168.4.128 -ServerRole Active -ReservePercent 10 -MaxClientLeadTime (New-TimeSpan -Minutes 5) -AutoStateTransition $true -StateSwitchInterval (New-TimeSpan -Minutes 10) -SharedSecret 'cub' -Force
```

- `-PartnerServer '192.168.4.4'` : Adresse IPv4 de `SERVEURDHCP1` (serveur de secours).
- `-ServerRole Active` : Définit le rôle du serveur local (`SERVEURDHCP0`) en tant que serveur actif.
- `-ReservePercent 10` : Quota de 10% du pool libre octroyé au serveur de secours (`SERVEURDHCP1`).
- `-MaxClientLeadTime` : Durée (5 minutes) durant laquelle le bail reste acceptable par le partenaire (MCLT).
- `-AutoStateTransition $true` : Active la transition automatique vers l'état `Partner-Down` en cas de rupture prolongée de la communication.
- `-StateSwitchInterval (New-TimeSpan -Minutes 10)` : Délai de 10 minutes après perte de communication avant bascule automatique.
- `-SharedSecret 'cub'` : Activation de l'authentification des messages de la relation (port TCP 647).
- `-Force` : Valide la création de la relation sans invite interactive.

6.2. **Contrôle de l'état de la réplication.** Vérification à exécuter sur les deux nœuds pour confirmer la synchronisation des baux et des étendues.

```powershell
Get-DhcpServerv4Failover | Format-List Name, PartnerServer, Mode, ServerRole, State, ScopeId
```

- `State` : Doit retourner la valeur `Normal` sur les deux nœuds (session TCP 647 établie).

---

## 7. Configuration du relais DHCP Cisco (Switch L3)

7.1. **Déploiement de l'agent IP Helper.** Configuration de l'interface SVI du VLAN 10 sur le commutateur de niveau 3 `dmd-sw-coeur01` pour le routage des requêtes UDP 67/68 vers les serveurs DHCP.

```text
dmd-sw-coeur01# configure terminal
dmd-sw-coeur01(config)# interface Vlan 10
dmd-sw-coeur01(config-if)# ip address 192.168.4.190 255.255.255.192
dmd-sw-coeur01(config-if)# ip helper-address 192.168.4.3
dmd-sw-coeur01(config-if)# ip helper-address 192.168.4.4
dmd-sw-coeur01(config-if)# end
dmd-sw-coeur01# write memory
```

- `interface Vlan 10` : Interface de routage SVI du réseau des postes clients.
- `ip address 192.168.4.190 255.255.255.192` : Adresse IPv4 de passerelle par défaut (insérée dans le champ `giaddr` pour identifier l'étendue).
- `ip helper-address 192.168.4.3` : Cible le serveur DHCP principal (`SERVEURDHCP0`).
- `ip helper-address 192.168.4.4` : Cible le serveur DHCP de secours (`SERVEURDHCP1`).
- `write memory` : Sauvegarde permanente de la configuration dans la mémoire NVRAM du commutateur.

---

## 8. Commandes d'exploitation et de diagnostic

8.1. **Matrice des opérations et des commandes sous Windows Server Core :**

| Opération d'administration | Commande PowerShell (Windows Core) | Description / Objectif |
| :--- | :--- | :--- |
| :lucide-check: **Vérifier l'écart de temps** | `Get-Date` | L'écart entre les serveurs doit être < 1 minute (critique pour la synchronisation). |
| :lucide-check: **Tester la bascule (Sur SERVEURDHCP0)** | `Stop-Service DHCPServer` | Stoppe le service sur le serveur actif (`SERVEURDHCP0`) pour éprouver la continuité de service. |
| :lucide-check-check: **Forcer la bascule (Sur SERVEURDHCP1)** | `Set-DhcpServerv4Failover -Name 'Failover-CUB-HotStandby' -PartnerDown -Force` | Bascule manuellement le serveur de secours (`SERVEURDHCP1`) en état `PartnerDown` pour lui allouer 100% de la charge du pool. |
| :lucide-check-check: **Forcer la réplication manuelle (Sur SERVEURDHCP0)** | `Invoke-DhcpServerv4FailoverReplication -Name 'Failover-CUB-HotStandby' -Force` | Déclenche la synchronisation immédiate de l'étendue vers `SERVEURDHCP1`. |
| :lucide-x: **Détruire la relation** | `Remove-DhcpServerv4Failover -Name 'Failover-CUB-HotStandby' -Force` | Supprime l'association Failover sans détruire les étendues. |
| :lucide-x: **Purger l'étendue (Sur SERVEURDHCP1)** | `Remove-DhcpServerv4Scope -ScopeId 192.168.4.128 -Force` | Supprime l'étendue répliquée orpheline sur `SERVEURDHCP1` en cas de réinitialisation complète. |
| :lucide-list: **Consulter les baux actifs délivrés** | `Get-DhcpServerv4Lease -ScopeId 192.168.4.128` | Affiche l'inventaire des adresses allouées aux clients avec leur adresse MAC. |
| :lucide-bar-chart: **Auditer l'occupation du pool** | `Get-DhcpServerv4ScopeStatistics -ScopeId 192.168.4.128` | Affiche les compteurs d'adresses libres, utilisées et réservées. |
| :lucide-eye: **Afficher les options distribuées** | `Get-DhcpServerv4OptionValue -ScopeId 192.168.4.128` | Contrôle la conformité des options 003 (Passerelle), 006 (DNS) et 015 (Suffixe). |

---

## 9. Sécurité et durcissement du service DHCP

9.1. **Consulter la note technique dédiée.** L'analyse approfondie des menaces protocolaires (**DHCP Starvation** et **Rogue DHCP / Man-in-the-Middle**), ainsi que les contre-mesures techniques (**Port Security**, **Filtrage MAC** et **DHCP Snooping**) sont détaillées dans le document spécialisé :

$\rightarrow$ Consulter la [Note Technique de Sécurité : Vulnérabilités DHCP et Contre-Mesures](securite-dhcp.md).
