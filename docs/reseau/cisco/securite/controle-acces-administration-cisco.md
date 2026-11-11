---
description: "Contrôle et restriction des accès d'administration aux commutateurs Cisco de Dortmund"
---

# BLOC 3 - Contrôle des accès d'administration Cisco

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** Amine
> - **Date :** 11/11/2026
> - **Domaine :** Réseau et cybersécurité

---

## 1. Sommaire

- [2. Contexte](#2-contexte)
- [3. Contrôles préalables](#3-controles-prealables)
- [4. Limiter les accès SSH](#4-limiter-les-acces-ssh)
- [5. Contrôler le service web](#5-controler-le-service-web)
- [6. Recette et retour arrière](#6-recette-et-retour-arriere)

## 2. Contexte

Cette procédure décrit la restriction des connexions SSH aux commutateurs Cisco depuis le VLAN 20 (`192.168.4.192/28`). Le filtrage des flux entre VLAN est défini séparément par les règles de routage et de sécurité.

> [!warning] Accès de secours
> Prévoir un accès console fonctionnel, sauvegarder la configuration courante et conserver une session administrative ouverte. Vérifier les adresses sources réellement autorisées avant application. Le bastion VLAN 53 n'est pas autorisé dans l'exemple ; si son accès est nécessaire, ajouter une règle validée avant d'appliquer l'ACL.

## 3. Contrôles préalables

3.1. **Relever la configuration active et les accès existants.**

```text
show running-config | section line vty
show running-config | include ip http
show access-lists
show ip interface brief
show vlan brief
show interfaces trunk
```

Contrôler les deux plages VTY, les restrictions déjà en place, le nom de l'ACL, les services HTTP/HTTPS utilisés et les accès depuis la console. S'assurer que l'adresse source de la session de test appartient au VLAN autorisé.

## 4. Limiter les accès SSH

4.1. **Exemple de restriction VTY pour le VLAN 20.** Après validation des sources et du nom disponible, appliquer sur le switch concerné :

```text
configure terminal
ip access-list standard CUB-MGMT-VTY
 permit 192.168.4.192 0.0.0.15
 exit
line vty 0 4
 access-class CUB-MGMT-VTY in
 transport input ssh
 exit
line vty 5 15
 access-class CUB-MGMT-VTY in
 transport input ssh
 end
```

- `access-class ... in` : limite les sources des connexions entrantes aux lignes VTY ; la fin implicite de l'ACL refuse les sources non autorisées.
- `transport input ssh` : conserve SSH comme protocole d'accès distant aux lignes ciblées.
- Vérifier les plages VTY réellement présentes et éviter d'écraser une ACL ou une politique déjà utilisée. Cette ACL ne protège pas à elle seule HTTP/HTTPS ni les flux transitant entre VLAN.

## 5. Contrôler le service web

5.1. **Choisir le service nécessaire.** Vérifier les usages existants. Si l'interface web n'est pas utilisée, désactiver HTTP et HTTPS après validation :

```text
configure terminal
no ip http server
no ip http secure-server
end
```

Si HTTPS est nécessaire, conserver le service sécurisé, désactiver HTTP non chiffré si possible et définir une restriction d'accès compatible avec le modèle et la version IOS. Vérifier séparément l'accès web : la restriction VTY ne s'y applique pas.

## 6. Recette et retour arrière

6.1. **Contrôler avant sauvegarde.** Sur le switch, afficher `show access-lists` et la configuration des lignes VTY et des services web. Depuis un poste VLAN 20, ouvrir une nouvelle session SSH. Depuis un réseau non autorisé, confirmer le refus ; vérifier également l'accès web selon la décision prise. Tester toute exception validée, notamment le bastion. Une fois les tests réussis, sauvegarder la configuration selon la procédure d'exploitation.

6.2. **Rétablir l'accès si nécessaire.** Depuis la console, retirer l'`access-class` ajoutée de chaque plage VTY concernée ou restaurer la configuration précédente relevée à l'étape 3 ; rétablir les services web uniquement s'ils étaient nécessaires. Refaire les tests avant toute sauvegarde.
