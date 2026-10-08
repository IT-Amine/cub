---
description: Fiche recette du serveur DNS autoritaire Esclave (ns1)
---

# Fiche Recette : DNS Autoritaire Esclave

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 08/10/2026</p>
    <p><strong>Contexte :</strong> Validation fonctionnelle (tests de résolution et autorité) du serveur DNS autoritaire esclave (ns1 - 192.36.4.11) de l'agence de Dortmund.</p>
</div>

---

## 1. Sommaire

- [1. Sommaire](#1-sommaire)
- [2. Objectif des tests](#2-objectif-des-tests)
- [3. Tests de validation de la zone](#3-tests-de-validation-de-la-zone)
  - [3.1. Résolution d'un enregistrement (www)](#31-resolution-dun-enregistrement-www)
  - [3.2. Vérification de l'autorité (SOA)](#32-verification-de-lautorite-soa)
  - [3.3. Test de réponse sur l'interface réseau publique](#33-test-de-reponse-sur-linterface-reseau-publique)
  - [3.4. Vérification de la synchronisation (Serial SOA)](#34-verification-de-la-synchronisation-serial-soa)
- [4. Conclusion](#4-conclusion)

---

## 2. Objectif des tests

Cette fiche recette a pour but de vérifier que le serveur DNS secondaire (ns1) est bien configuré en tant que DNS autoritaire pour la zone `dortmund.cub.sioplc.fr`. Les tests s'assurent qu'il possède bien une copie fonctionnelle de la zone, qu'il répond avec autorité (sans interroger d'autres serveurs), et que sa sécurité (refus des requêtes récursives) est opérationnelle.

---

## 3. Tests de validation de la zone

### 3.1. Résolution d'un enregistrement (www)

**Objectif :** S'assurer que le serveur local (interrogé sur `127.0.0.1`) résout correctement un enregistrement spécifique de la zone.

**Commande exécutée :**
```bash
dig @127.0.0.1 www.dortmund.cub.sioplc.fr
```

**Résultat :**
```text
etudiant@ns1:~$ dig @127.0.0.1 www.dortmund.cub.sioplc.fr

; <<>> DiG 9.20.29-1~deb13u1-Debian <<>> @127.0.0.1 www.dortmund.cub.sioplc.fr
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 53506
;; flags: qr aa rd; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1
;; WARNING: recursion requested but not available

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; COOKIE: f77728855402bab0010000006ac75bf0f3a63fbcf1f7097d (good)
;; QUESTION SECTION:
;www.dortmund.cub.sioplc.fr.    IN      A

;; ANSWER SECTION:
www.dortmund.cub.sioplc.fr. 43200 IN    A       192.36.4.20

;; Query time: 0 msec
;; SERVER: 127.0.0.1#53(127.0.0.1) (UDP)
;; WHEN: Thu Oct 08 11:01:36 CEST 2026
;; MSG SIZE  rcvd: 99
```

**Explication :** 
Le service BIND9 tourne correctement. La réponse affiche `status: NOERROR` et le flag `aa` (*Authoritative Answer*), ce qui signifie que le serveur répond de manière ferme, sans chercher sur Internet, car il a bien la zone en mémoire. Il renvoie la bonne IP : `192.36.4.20`.

---

### 3.2. Vérification de l'autorité (SOA)

**Objectif :** Demander l'enregistrement SOA (*Start of Authority*), qui fait office de "carte d'identité" de la zone DNS.

**Commande exécutée :**
```bash
dig @127.0.0.1 dortmund.cub.sioplc.fr SOA
```

**Résultat :**
```text
etudiant@ns1:~$ dig @127.0.0.1 dortmund.cub.sioplc.fr SOA

; <<>> DiG 9.20.29-1~deb13u1-Debian <<>> @127.0.0.1 dortmund.cub.sioplc.fr SOA
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 9217
;; flags: qr aa rd; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1
;; WARNING: recursion requested but not available

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; COOKIE: a34393779cbc428a010000006ac75bf40aba7cc99f3e9f6f (good)
;; QUESTION SECTION:
;dortmund.cub.sioplc.fr.                IN      SOA

;; ANSWER SECTION:
dortmund.cub.sioplc.fr. 43200   IN      SOA     ns0.dortmund.cub.sioplc.fr. postmaster.dortmund.cub.sioplc.fr. 2026100101 86400 3600 604800 10800

;; Query time: 0 msec
;; SERVER: 127.0.0.1#53(127.0.0.1) (UDP)
;; WHEN: Thu Oct 08 11:01:40 CEST 2026
;; MSG SIZE  rcvd: 130
```

**Explication :** 
Le serveur renvoie correctement les informations vitales de la zone. Le point le plus important de cette réponse est le numéro de série : `2026100101`. En production, interroger le SOA permet de comparer ce numéro de série avec celui du serveur maître pour s'assurer que l'esclave est bien à jour et synchronisé.

---

### 3.3. Test de réponse sur l'interface réseau publique

**Objectif :** Utiliser l'adresse IP réseau de l'esclave (`192.36.4.11`) au lieu de la boucle locale, pour lui demander où se trouve le serveur maître (`ns0`).

**Commande exécutée :**
```bash
dig @192.36.4.11 ns0.dortmund.cub.sioplc.fr
```

**Résultat :**
```text
etudiant@ns1:~$ dig @192.36.4.11 ns0.dortmund.cub.sioplc.fr

; <<>> DiG 9.20.29-1~deb13u1-Debian <<>> @192.36.4.11 ns0.dortmund.cub.sioplc.fr
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 39894
;; flags: qr aa rd; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1
;; WARNING: recursion requested but not available

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; COOKIE: 819be59cd1b6f41d010000006ac75bfa2a24c212a1a1b5ed (good)
;; QUESTION SECTION:
;ns0.dortmund.cub.sioplc.fr.    IN      A

;; ANSWER SECTION:
ns0.dortmund.cub.sioplc.fr. 43200 IN    A       192.36.4.10

;; Query time: 0 msec
;; SERVER: 192.36.4.11#53(192.36.4.11) (UDP)
;; WHEN: Thu Oct 08 11:01:46 CEST 2026
;; MSG SIZE  rcvd: 99
```

**Explication :** 
Cela valide que le service BIND9 n'écoute pas seulement en local, mais qu'il est bien ouvert et fonctionnel sur sa carte réseau (grâce à la directive `listen-on` dans le fichier d'options). Il trouve instantanément l'adresse du maître (`192.36.4.10`).

---

### 3.4. Vérification de la synchronisation (Serial SOA)

**Objectif :** Vérifier si le serveur esclave est parfaitement à jour en comparant l'enregistrement SOA du serveur maître et celui du serveur esclave.

**Commandes exécutées :**
```bash
# Interroger le serveur maître (192.36.4.10)
dig +short @192.36.4.10 dortmund.cub.sioplc.fr SOA

# Interroger le serveur esclave (192.36.4.11)
dig +short @192.36.4.11 dortmund.cub.sioplc.fr SOA
```
*(L'option `+short` est une astuce très pratique en production : elle masque tout le superflu pour n'afficher que la donnée brute).*

**Résultat :**
```text
etudiant@ns1:~$ dig +short @192.36.4.10 dortmund.cub.sioplc.fr SOA
ns0.dortmund.cub.sioplc.fr. postmaster.dortmund.cub.sioplc.fr. 2026100101 86400 3600 604800 10800

etudiant@ns1:~$ dig +short @192.36.4.11 dortmund.cub.sioplc.fr SOA
ns0.dortmund.cub.sioplc.fr. postmaster.dortmund.cub.sioplc.fr. 2026100101 86400 3600 604800 10800
```

**Analyse du résultat (le 3ème nombre correspond au "Serial") :**
- **Les deux numéros de série sont identiques (`2026100101`) :** Le serveur esclave est parfaitement à jour. Il possède l'exacte copie de la base de données du maître.
- *(À titre d'information)* **Si le numéro du maître est plus grand :** Une modification a été faite sur le maître (ajout d'une IP, d'un nom...), mais l'esclave ne l'a pas encore téléchargée. On peut forcer la mise à jour manuellement avec `sudo rndc retransfer dortmund.cub.sioplc.fr`.
- *(À titre d'information)* **Si le numéro du maître est plus petit :** C'est une erreur humaine. L'administrateur a modifié le fichier de zone sur le maître mais a oublié d'incrémenter le numéro de série à la main. L'esclave refusera alors de se mettre à jour, pensant avoir une version plus récente.

---

## 4. Conclusion

> [!success] Validation fonctionnelle et sécurité
> Sur les trois requêtes, on aperçoit le message d'avertissement `WARNING: recursion requested but not available`. C'est une excellente chose. La commande `dig` demande par défaut une recherche récursive, mais le serveur la refuse car elle a été explicitement bloquée dans sa configuration (`recursion no;`). Cela prouve que le serveur joue strictement son rôle de DNS Autoritaire et que les paramètres de sécurité anti-amplification DNS sont actifs.
