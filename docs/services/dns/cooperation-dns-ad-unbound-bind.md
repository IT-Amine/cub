---
description: "Procédure de coopération DNS entre Active Directory, Unbound et Bind9 pour l'agence de Dortmund"
---

# BLOC 2 - Coopération des services DNS de l'agence Dortmund

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** Amine
> - **Date :** 11/11/2026
> - **Domaine :** Services réseau (DNS et Active Directory)

---

## 1. Sommaire

- [2. Contexte](#2-contexte)
- [3. Architecture et chemin des requêtes](#3-architecture-et-chemin-des-requetes)
- [4. Prérequis et contrôles avant configuration](#4-prerequis-et-controles-avant-configuration)
- [5. Configuration des redirecteurs DNS Active Directory](#5-configuration-des-redirecteurs-dns-active-directory)
- [6. Configuration DHCP des clients](#6-configuration-dhcp-des-clients)
- [7. Recette de la résolution](#7-recette-de-la-resolution)
- [8. Dépannage et retour arrière](#8-depannage-et-retour-arriere)

---

## 2. Contexte

Cette procédure décrit la configuration des services DNS Active Directory, Unbound et Bind9 pour la résolution des noms de l'agence Dortmund.

Les postes membres du domaine ont besoin des enregistrements DNS Active Directory, notamment des enregistrements SRV. Les serveurs Unbound assurent la résolution récursive et le cache. Les serveurs Bind9 font autorité sur la zone `dortmund.cub.sioplc.fr`.

## 3. Architecture et chemin des requêtes

| Composant | Adresses documentées | Rôle |
| :--- | :--- | :--- |
| DNS Active Directory AD0 / AD1 | `192.168.4.1` / `192.168.4.2` | Hébergent la zone AD `local.dortmund.cub.sioplc.fr` ; répondent aux postes et transmettent les demandes non résolues localement. |
| Résolveurs Unbound DNS0 / DNS1 | `192.168.4.10` / `192.168.4.11` | Reçoivent les demandes transmises par les DNS AD et effectuent la résolution récursive ou utilisent leur cache. |
| DNS faisant autorité Bind9 ns0 / ns1 | `192.36.4.10` / `192.36.4.11` | Fournissent les réponses faisant autorité pour la zone `dortmund.cub.sioplc.fr` et sa délégation éventuelle. |

```text
Poste VLAN 10
  -> DNS AD0 ou AD1 : 192.168.4.1 / 192.168.4.2
     -> zone locale AD : réponse par le DNS AD
     -> autre nom : transmission vers Unbound .10 / .11
        -> cache ou résolution récursive vers les serveurs faisant autorité
```

> [!important] DNS public et disponibilité
> Ne pas distribuer de DNS public directement aux postes membres du domaine comme secours : il ne connaît généralement pas la zone AD interne. Le poste pourrait perdre la résolution des noms internes. AD0 et AD1 constituent les deux DNS clients. Les résolveurs Unbound assurent la résolution en amont ; une panne des deux résolveurs affecte les noms non présents localement ou en cache. La résolution publique de secours éventuelle doit être conçue côté serveurs DNS, en tenant compte des zones internes et de la politique de routage.

## 4. Prérequis et contrôles avant configuration

4.1. **Vérifier la configuration existante de chaque DNS AD.** Exécuter dans une session PowerShell administrateur sur AD0 puis AD1 et conserver les résultats.

```powershell
Get-DnsServerForwarder
Get-DnsServerRecursion
Get-DnsServerZone | Select-Object ZoneName, ZoneType, IsDsIntegrated
```

- `Get-DnsServerForwarder` : affiche les redirecteurs existants et leurs paramètres.
- `Get-DnsServerZone` : permet de repérer les zones locales et les éventuels redirecteurs conditionnels.
- Vérifier la réplication AD/DNS et la présence de la zone AD sur les deux contrôleurs avant de distribuer leurs adresses.

4.2. **Tester les deux résolveurs depuis chaque serveur AD.**

```powershell
Resolve-DnsName -Server 192.168.4.10 -Name www.microsoft.com -DnsOnly
Resolve-DnsName -Server 192.168.4.11 -Name www.microsoft.com -DnsOnly
```

Les deux tests doivent retourner une réponse exploitable. Vérifier les flux DNS UDP et TCP 53 entre AD et Unbound ainsi que les flux nécessaires vers les serveurs d'autorité. Les caches peuvent masquer temporairement une panne en amont.

> [!warning] Boucle DNS
> Avant de définir Unbound comme redirecteur général des DNS AD, vérifier que les résolveurs Unbound ne renvoient pas ces mêmes requêtes générales vers les DNS AD.

## 5. Configuration des redirecteurs DNS Active Directory

5.1. **Définir les deux résolveurs Unbound comme redirecteurs généraux.** Après contrôle des prérequis, exécuter sur AD0 puis sur AD1 :

```powershell
Set-DnsServerForwarder -IPAddress 192.168.4.10,192.168.4.11 -PassThru
Get-DnsServerForwarder
```

- `Set-DnsServerForwarder` remplace la liste générale existante : conserver les valeurs relevées avant l'opération. Il ne configure pas le DNS des interfaces réseau des contrôleurs.
- Définir explicitement la politique de repli vers les serveurs racine selon les flux autorisés et l'architecture souhaitée ; ne pas présumer de la valeur actuellement configurée.
- Vérifier séparément les redirecteurs conditionnels et les éventuelles zones locales, prioritaires selon la configuration DNS.

## 6. Configuration DHCP des clients

6.1. **Configurer et vérifier les options de l'étendue VLAN 10.** Sur le serveur DHCP actif, une fois les deux DNS AD validés :

```powershell
Set-DhcpServerv4OptionValue -ScopeId 192.168.4.128 -DnsServer 192.168.4.1,192.168.4.2
Set-DhcpServerv4OptionValue -ScopeId 192.168.4.128 -DnsDomain "local.dortmund.cub.sioplc.fr"
Invoke-DhcpServerv4FailoverReplication -Name 'Failover-CUB-HotStandby'
Get-DhcpServerv4OptionValue -ScopeId 192.168.4.128
```

Le nom de la relation est celui de la procédure DHCP locale ; vérifier le nom et l'état réels avant la réplication. Contrôler également les options sur le serveur partenaire et renouveler le bail d'un poste de test. Les options ne modifient pas immédiatement les postes conservant leur bail existant.

## 7. Recette de la résolution

7.1. **Contrôler les DNS distribués depuis un poste Windows du VLAN 10.**

```powershell
ipconfig /all
Resolve-DnsName -Server 192.168.4.1 -Type SRV _ldap._tcp.dc._msdcs.local.dortmund.cub.sioplc.fr
Resolve-DnsName -Server 192.168.4.2 -Type SRV _ldap._tcp.dc._msdcs.local.dortmund.cub.sioplc.fr
Resolve-DnsName -Server 192.168.4.1 -Name www.microsoft.com
Resolve-DnsName -Server 192.168.4.2 -Name www.microsoft.com
```

Les options reçues doivent mentionner les deux DNS AD ; chaque contrôleur doit répondre avec les enregistrements SRV attendus et résoudre un nom externe. Comparer les résultats, sans conclure qu'un repli fonctionne simplement parce que les deux serveurs répondent.

7.2. **Tester directement les serveurs faisant autorité depuis une machine autorisée.**

```bash
dig @192.36.4.10 dortmund.cub.sioplc.fr SOA +norecurse
dig @192.36.4.11 dortmund.cub.sioplc.fr SOA +norecurse
dig @192.36.4.10 local.dortmund.cub.sioplc.fr NS +norecurse
dig @192.36.4.11 local.dortmund.cub.sioplc.fr NS +norecurse
```

Comparer la zone SOA et les numéros de série des deux serveurs ; pour la délégation, vérifier les enregistrements NS et la joignabilité des serveurs AD. Une délégation renvoie généralement une référence, pas nécessairement une réponse faisant autorité pour la zone enfant. Tester ensuite la résolution des noms de Dortmund depuis chacun des DNS AD et chacun des Unbound.

7.3. **Vérifier la continuité.** Sur un poste de test, tester successivement chaque DNS AD par son adresse, puis organiser un test de panne contrôlé selon la fenêtre de maintenance. Vérifier les noms internes et externes ; le cache et les délais de basculement peuvent influencer le résultat.

## 8. Dépannage et retour arrière

| Symptôme | Contrôle prioritaire |
| :--- | :--- |
| Échec SRV AD sur un contrôleur | Zone AD, service DNS, réplication, enregistrements et flux TCP/UDP 53. |
| AD répond en interne mais les noms externes échouent | Tester séparément les deux Unbound depuis AD, leurs redirecteurs, les routes et les filtrages. |
| Unbound répond pour Internet mais pas pour Dortmund | Vérifier la délégation, les serveurs NS, les routes vers la DMZ et les réponses Bind9. |
| Le poste reçoit encore d'anciens DNS | Vérifier l'étendue, les options spécifiques et le partenaire DHCP ; renouveler le bail du poste de test. |

Pour revenir en arrière, restaurer sur chaque DNS AD les redirecteurs généraux et la politique de repli relevés à l'étape 4 ; restaurer si nécessaire les anciennes options DHCP depuis les valeurs relevées avant modification, puis répliquer et vérifier la relation. Ne pas supprimer de zone ou de redirecteur conditionnel sans avoir vérifié sa fonction.
