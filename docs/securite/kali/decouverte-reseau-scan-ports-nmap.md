---
description: "Fiche de tests de découverte réseau et de scan de ports Nmap pour l'agence CUB Dortmund"
---

# BLOC 2 - Découverte réseau et analyse des ports avec Nmap

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

---

> [!note] "Informations"
>
> - **Auteur :** Amine
> - **Date :** 12/11/2026
> - **Domaine :** Kali Linux (nmap & wireshark)

---

## 1. Contexte du test

Les tests sont effectués le 12 novembre 2026 depuis la machine Kali Linux de l'agence Dortmund avec Nmap 7.95. Ils portent sur la connectivité, la découverte des équipements, les ports TCP et UDP, ainsi que l'identification des services et systèmes.

| Paramètre | Valeur observée |
| :--- | :--- |
| Interface Kali | `eth0` |
| Adresse Kali | `192.168.4.196/28` |
| Réseau source | VLAN 20 Administration — `192.168.4.192/28` |
| Passerelle par défaut | `192.168.4.206` |
| DNS utilisés après modification de `/etc/resolv.conf` | `192.168.4.10` et `192.168.4.11` |

> [!warning] Position de la machine
> L'activité demande une Kali dans le VLAN 54 Production. Les résultats ci-dessous ont été obtenus depuis le VLAN 20 Administration. Ils attestent les accès depuis cette position ; répéter les mesures depuis le VLAN 54 pour satisfaire le périmètre demandé et comparer les filtrages.

## 2. Procédures de validation

### 2.1. Vérification de l'adressage et du routage

**Objectif :** Identifier l'interface réseau, l'adresse IP, la passerelle et les serveurs DNS de Kali.

**Commandes utilisées :**

```bash
ip -br address
ip route
cat /etc/resolv.conf
```

- `ip -br address` : affiche les adresses des interfaces au format synthétique.
- `ip route` : affiche la table de routage et la passerelle par défaut.
- `cat /etc/resolv.conf` : affiche les résolveurs configurés au moment du contrôle.

**Résultat observé :** `eth0` est active avec `192.168.4.196/28` et la route par défaut passe par `192.168.4.206`. Le fichier DNS affiche initialement `1.1.1.1`, puis `192.168.4.10` et `192.168.4.11` après modification. NetworkManager gère le fichier ; une modification directe peut être remplacée lors d'une reconnexion.

**Statut :** Connectivité IPv4 configurée ; position en VLAN 54 à réaliser.

### 2.2. Tests ICMP, DNS et HTTP

**Objectif :** Vérifier la communication avec les équipements internes, la résolution DNS et l'accès au site Web.

**Commandes utilisées :**

```bash
ping -c 4 192.168.4.126
ping -c 4 192.168.4.10
ping -c 4 192.168.4.11
ping -c 4 1.1.1.1
dig @192.168.4.10 www1.dortmund.cub.sioplc.fr
dig @192.168.4.10 example.com
curl -I --max-time 5 http://www1.dortmund.cub.sioplc.fr
```

- `ping -c 4` : envoie quatre requêtes ICMP à l'adresse indiquée.
- `dig @192.168.4.10` : interroge directement le résolveur DNS indiqué.
- `curl -I` : demande les en-têtes HTTP ; `--max-time 5` limite la durée du test.

**Résultats observés :**

| Test | Résultat |
| :--- | :--- |
| ICMP vers `192.168.4.126`, `192.168.4.10` et `192.168.4.11` | 4 réponses sur 4 pour chaque adresse. |
| ICMP vers `1.1.1.1` | 4 réponses sur 4. |
| DNS interne via `192.168.4.10` | `www1.dortmund.cub.sioplc.fr` est un alias CNAME de `web1.dortmund.cub.sioplc.fr`, résolu en `192.36.4.21`. |
| DNS externe via `192.168.4.10` | `example.com` retourne `NOERROR` et deux adresses IPv4. |
| HTTP vers `www1` | Réponse `HTTP/1.1 200 OK` avec un en-tête de lien vers l'API WordPress. |

**Statut :** Tests réalisés avec succès depuis le VLAN Administration.

### 2.3. Découverte des hôtes par réseau

**Objectif :** Identifier les adresses répondant aux sondes de découverte sur les réseaux de l'agence.

**Commandes utilisées :**

```bash
sudo nmap -sn -n 192.168.4.0/25 -oN ~/cub-pentest/decouverte/vlan54-production.txt
sudo nmap -sn -n 192.168.4.128/26 -oN ~/cub-pentest/decouverte/vlan10-clients.txt
sudo nmap -sn -n 192.168.4.192/28 -oN ~/cub-pentest/decouverte/vlan20-administration.txt
sudo nmap -sn -n 192.168.4.208/29 -oN ~/cub-pentest/decouverte/vlan53-bastion.txt
sudo nmap -sn -n 192.168.44.248/29 -oN ~/cub-pentest/decouverte/interconnexion.txt
sudo nmap -sn -n 192.36.4.0/24 -oN ~/cub-pentest/decouverte/vlan84-dmz.txt
```

- `-sn` : effectue la découverte sans scan de ports.
- `-n` : désactive la résolution DNS inverse.
- `-oN` : enregistre la sortie Nmap en texte.

**Résultats observés :**

| Réseau | Adresses utilisables signalées actives | Résultat Nmap brut |
| :--- | :--- | :--- |
| VLAN 54 Production | `192.168.4.2`, `192.168.4.10`, `192.168.4.11`, `192.168.4.126` | [`vlan54-production.txt`](../../assets/cub-pentest/decouverte/vlan54-production.txt) |
| VLAN 10 Clients | `192.168.4.190` | [`vlan10-clients.txt`](../../assets/cub-pentest/decouverte/vlan10-clients.txt) |
| VLAN 20 Administration | `192.168.4.193`, `192.168.4.195`, `192.168.4.196` (Kali), `192.168.4.204`, `192.168.4.205`, `192.168.4.206` | [`vlan20-administration.txt`](../../assets/cub-pentest/decouverte/vlan20-administration.txt) |
| VLAN 53 Bastion | `192.168.4.210`, `192.168.4.211`, `192.168.4.214` | [`vlan53-bastion.txt`](../../assets/cub-pentest/decouverte/vlan53-bastion.txt) |
| Interconnexion | `192.168.44.253`, `192.168.44.254` | [`interconnexion.txt`](../../assets/cub-pentest/decouverte/interconnexion.txt) |
| DMZ | `192.36.4.10`, `192.36.4.11`, `192.36.4.20`, `192.36.4.21`, `192.36.4.254` | [`vlan84-dmz.txt`](../../assets/cub-pentest/decouverte/vlan84-dmz.txt) |

Les résultats bruts signalent aussi `192.168.4.0`, `.127`, `.128`, `.191`, `.208`, `.215`, ainsi que `192.168.44.248` et `.255`. Ce sont les adresses réseau ou de diffusion des sous-réseaux indiqués ; elles ne sont pas retenues comme hôtes individuels sans vérification complémentaire.

> [!note] Limite de découverte
> Une adresse qui ne répond pas peut être hors ligne, filtrée ou ne pas répondre aux sondes. La découverte ne constitue pas un inventaire exhaustif garanti.

### 2.4. Scan TCP et UDP de la passerelle

**Objectif :** Identifier les ports accessibles sur `192.168.4.126`, interface du switch L3 pour le VLAN Production.

**Commandes utilisées :**

```bash
sudo nmap -sS -n 192.168.4.126 -oN ~/cub-pentest/ports/passerelle-tcp.txt
sudo nmap -sU -n 192.168.4.126 -oN ~/cub-pentest/ports/passerelle-udp.txt
sudo nmap -sU -p- -n 192.168.4.126 -oN ~/cub-pentest/ports/passerelle-udp-complet.txt
```

- `-sS` : scan TCP SYN.
- `-sU` : scan UDP.
- `-p-` : demande le scan de tous les ports ; sans ce paramètre, Nmap teste sa sélection de ports courants.

**Résultats observés :**

| Protocole | Résultat | Résultat Nmap brut |
| :--- | :--- | :--- |
| TCP | `22`, `80` et `443` ouverts ; 997 ports fermés sur les 1 000 testés. | [`passerelle-tcp.txt`](../../assets/cub-pentest/ports/passerelle-tcp.txt) |
| UDP | `67/udp open\|filtered` ; 999 ports indiqués filtrés sur les 1 000 testés. | [`passerelle-udp.txt`](../../assets/cub-pentest/ports/passerelle-udp.txt) |
| UDP complet `-p-` | Fichier sans résultat final : le scan complet n'est pas exploitable. | [`passerelle-udp-complet.txt`](../../assets/cub-pentest/ports/passerelle-udp-complet.txt) |

**Statut :** Scans TCP et UDP courants terminés ; scan UDP complet non terminé dans les données disponibles.

### 2.5. Scan TCP et UDP du Stormshield et des serveurs

**Objectif :** Recenser les ports exposés sur l'interface du pare-feu et les serveurs identifiés.

**Commandes utilisées :**

```bash
sudo nmap -sS -n 192.168.44.254 -oN ~/cub-pentest/ports/stormshield-tcp.txt
sudo nmap -sU -n 192.168.44.254 -oN ~/cub-pentest/ports/stormshield-udp.txt
sudo nmap -sS -n 192.168.4.1-6 192.168.4.10-11 -oN ~/cub-pentest/ports/serveurs-production-tcp.txt
sudo nmap -sU -n 192.168.4.1-6 192.168.4.10-11 -oN ~/cub-pentest/ports/serveurs-production-udp.txt
sudo nmap -sS -n 192.36.4.10-11 192.36.4.20-21 -oN ~/cub-pentest/ports/serveurs-dmz-tcp.txt
sudo nmap -sU -n 192.36.4.10-11 192.36.4.20-21 -oN ~/cub-pentest/ports/serveurs-dmz-udp.txt
```

- `192.168.4.1-6` et les autres plages : définissent les adresses ciblées.
- Les scans TCP et UDP utilisent chacun la sélection par défaut de 1 000 ports de Nmap.

**Résultats observés :**

| Cible | Ports TCP ouverts | Ports UDP ouverts ou état | Résultats Nmap bruts |
| :--- | :--- | :--- | :--- |
| Stormshield `192.168.44.254` | `22`, `443` ; `113` fermé | 1 000 ports `open\|filtered` | [`stormshield-tcp.txt`](../../assets/cub-pentest/ports/stormshield-tcp.txt) / [`stormshield-udp.txt`](../../assets/cub-pentest/ports/stormshield-udp.txt) |
| AD1 `192.168.4.2` | `53`, `88`, `135`, `139`, `389`, `445`, `464`, `593`, `636`, `3268`, `3269`, `5985` | `53`, `88`, `123`, `389` ouverts ; 996 `open\|filtered` | [`serveurs-production-tcp.txt`](../../assets/cub-pentest/ports/serveurs-production-tcp.txt) / [`serveurs-production-udp.txt`](../../assets/cub-pentest/ports/serveurs-production-udp.txt) |
| DNS récursifs `192.168.4.10` et `.11` | `22`, `53` sur chacun | `53` ouvert sur chacun | [`serveurs-production-tcp.txt`](../../assets/cub-pentest/ports/serveurs-production-tcp.txt) / [`serveurs-production-udp.txt`](../../assets/cub-pentest/ports/serveurs-production-udp.txt) |
| DNS autoritaires `192.36.4.10` et `.11` | `22`, `53` sur chacun | `53` ouvert ; autres ports signalés `open\|filtered` : `69`, `80`, `88`, `123`, `443`, `5060`, `47808` | [`serveurs-dmz-tcp.txt`](../../assets/cub-pentest/ports/serveurs-dmz-tcp.txt) / [`serveurs-dmz-udp.txt`](../../assets/cub-pentest/ports/serveurs-dmz-udp.txt) |
| Web0 `192.36.4.20` | `22`, `80`, `443` | `69`, `80`, `88`, `123`, `443`, `5060`, `47808` en `open\|filtered` | [`serveurs-dmz-tcp.txt`](../../assets/cub-pentest/ports/serveurs-dmz-tcp.txt) / [`serveurs-dmz-udp.txt`](../../assets/cub-pentest/ports/serveurs-dmz-udp.txt) |
| Web1 `192.36.4.21` | `22`, `80` ; 998 ports filtrés | 1 000 ports `open\|filtered` | [`serveurs-dmz-tcp.txt`](../../assets/cub-pentest/ports/serveurs-dmz-tcp.txt) / [`serveurs-dmz-udp.txt`](../../assets/cub-pentest/ports/serveurs-dmz-udp.txt) |

Dans les scans de Production, `192.168.4.1` et `192.168.4.3` à `.6` ne sont pas rapportées comme actives. L'absence de réponse aux sondes de découverte ne prouve pas que ces serveurs sont éteints.

- `open` : Nmap a reçu une réponse compatible avec un port ouvert.
- `closed` : la cible a répondu que le port était fermé.
- `filtered` : un filtrage ou une absence de réponse empêche l'identification de l'état.
- `open|filtered` : le scan ne distingue pas un port ouvert d'un port filtré ; cette valeur ne confirme pas la présence d'un service.

### 2.6. Identification des services et systèmes

**Objectif :** Déterminer les services détectables et obtenir une estimation du système d'exploitation.

**Commande utilisée :**

```bash
sudo nmap -sS -sV -O -n 192.168.4.126 192.168.44.254 \
  192.168.4.1-6 192.168.4.10-11 192.36.4.10-11 192.36.4.20-21 \
  -oN ~/cub-pentest/ports/services-systemes.txt
```

- `-sV` : interroge les services pour tenter d'identifier leur logiciel et leur version.
- `-O` : tente d'identifier le système d'exploitation à partir de l'empreinte réseau.
- `-oN` : conserve le rapport complet au format texte.

**Résultats observés :** ([`services-systemes.txt`](../../assets/cub-pentest/ports/services-systemes.txt))

| Cible | Identification Nmap |
| :--- | :--- |
| `192.168.4.126` | Cisco SSH 1.25, protocole SSH 2.0 ; service Web identifié OpenResty ; système IOS estimé sans correspondance exacte. |
| `192.168.44.254` | OpenSSH 7.8 et service HTTPS ; système non identifié avec certitude. |
| `192.168.4.2` | Services Microsoft Windows et Kerberos identifiés ; système Windows estimé sans correspondance exacte. |
| `192.168.4.10` et `.11` | OpenSSH 10.0p2 Debian et Unbound. |
| `192.36.4.10` et `.11` | OpenSSH 10.0p2 Debian et ISC BIND. |
| `192.36.4.20` | OpenSSH 10.0p2 Debian et Apache HTTP ; `443/tcp` ouvert, service indiqué `https?` à confirmer. |
| `192.36.4.21` | OpenSSH 10.0p2 Debian et Apache HTTP ; estimation du système peu fiable selon Nmap. |

Des scans complémentaires `-Pn -sS -sV` ont confirmé les ports TCP ci-dessus pour Web0 et Web1. L'option `-Pn` désactive la découverte préalable des hôtes ; elle ne contourne pas le filtrage des ports.

**Statut :** Détection effectuée depuis le VLAN Administration ; les estimations de système restent à confirmer sur les équipements.

## 3. Conclusion des tests

Les tests confirment la connectivité observée de Kali vers les résolveurs et le site WordPress, ainsi que les ports listés depuis le VLAN Administration. Le sujet demandant une machine de test en VLAN Production, les mesures doivent être répétées depuis ce VLAN. La capture UDP complète de la passerelle ne contient pas de résultat final ; le scan UDP courant a, lui, été mené à terme.

## 4. Annexes — Résultats bruts Nmap (`cub-pentest`)

L'ensemble des captures brutes issues de la campagne Nmap est stocké dans le dossier `docs/assets/cub-pentest/` :

### Scans de découverte d'hôtes (`decouverte/`)
- [VLAN 54 Production (`vlan54-production.txt`)](../../assets/cub-pentest/decouverte/vlan54-production.txt)
- [VLAN 10 Clients (`vlan10-clients.txt`)](../../assets/cub-pentest/decouverte/vlan10-clients.txt)
- [VLAN 20 Administration (`vlan20-administration.txt`)](../../assets/cub-pentest/decouverte/vlan20-administration.txt)
- [VLAN 53 Bastion (`vlan53-bastion.txt`)](../../assets/cub-pentest/decouverte/vlan53-bastion.txt)
- [Interconnexion (`interconnexion.txt`)](../../assets/cub-pentest/decouverte/interconnexion.txt)
- [VLAN 84 DMZ (`vlan84-dmz.txt`)](../../assets/cub-pentest/decouverte/vlan84-dmz.txt)

### Scans de ports et services (`ports/`)
- [Passerelle TCP (`passerelle-tcp.txt`)](../../assets/cub-pentest/ports/passerelle-tcp.txt)
- [Passerelle UDP (`passerelle-udp.txt`)](../../assets/cub-pentest/ports/passerelle-udp.txt)
- [Passerelle UDP complet (`passerelle-udp-complet.txt`)](../../assets/cub-pentest/ports/passerelle-udp-complet.txt)
- [Stormshield TCP (`stormshield-tcp.txt`)](../../assets/cub-pentest/ports/stormshield-tcp.txt)
- [Stormshield UDP (`stormshield-udp.txt`)](../../assets/cub-pentest/ports/stormshield-udp.txt)
- [Serveurs Production TCP (`serveurs-production-tcp.txt`)](../../assets/cub-pentest/ports/serveurs-production-tcp.txt)
- [Serveurs Production UDP (`serveurs-production-udp.txt`)](../../assets/cub-pentest/ports/serveurs-production-udp.txt)
- [Serveurs DMZ TCP (`serveurs-dmz-tcp.txt`)](../../assets/cub-pentest/ports/serveurs-dmz-tcp.txt)
- [Serveurs DMZ UDP (`serveurs-dmz-udp.txt`)](../../assets/cub-pentest/ports/serveurs-dmz-udp.txt)
- [Services et systèmes (`services-systemes.txt`)](../../assets/cub-pentest/ports/services-systemes.txt)
