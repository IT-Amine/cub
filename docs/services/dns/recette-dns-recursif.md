---
description: "Fiche Recette : DNS Récursif (Unbound)"
---

# Fiche Recette : DNS Récursif (Unbound)

![Bannière CUB](../../assets/banniere-cub.png)

!!! abstract "Informations sur le document"
    - **Auteur :** KADA Amine
    - **Classe :** BTS SIO 2 - Option SISR
    - **Date :** 08/10/2026
    - **Sujet :** Fiche Recette : DNS Récursif (Unbound)

---

## Objectif des tests

Cette fiche recette a pour but de vérifier que le serveur DNS récursif local (`dns1` sous Unbound) est parfaitement capable de résoudre des noms de domaines de manière récursive en partant des serveurs racines d'Internet (Root Servers), jusqu'aux serveurs faisant autorité pour les sous-domaines du projet CUB (`dortmund.cub.sioplc.fr`).

Ces tests valident le bon fonctionnement de la délégation de zone depuis le domaine principal `sioplc.fr` jusqu'à la DMZ.

---

## Tests de l'arborescence (Traçage DNS)

Pour tester la résolution complète depuis la racine, la commande `dig +trace` est exécutée sur le client `dns1`. Elle force le résolveur à interroger successivement chaque niveau de la hiérarchie DNS.

### Traçage vers le serveur Esclave (ns1)

**Commande exécutée :**
```bash
dig +trace ns1.dortmund.cub.sioplc.fr
```

**Résultat :**
```text
etudiant@dns1:~$ dig +trace ns1.dortmund.cub.sioplc.fr

; <<>> DiG 9.20.29-1~deb13u1-Debian <<>> +trace ns1.dortmund.cub.sioplc.fr
;; global options: +cmd
.                       85101   IN      NS      b.root-servers.net.
.                       85101   IN      NS      k.root-servers.net.
[... Serveurs Racines ...]
;; Received 1097 bytes from 192.168.4.10#53(192.168.4.10) in 0 ms

fr.                     172800  IN      NS      d.nic.fr.
fr.                     172800  IN      NS      f.ext.nic.fr.
fr.                     172800  IN      NS      g.ext.nic.fr.
[... Signatures DNSSEC .fr ...]
;; Received 606 bytes from 192.36.148.17#53(i.root-servers.net) in 24 ms

sioplc.fr.              3600    IN      NS      dns15.ovh.net.
sioplc.fr.              3600    IN      NS      ns15.ovh.net.
[... Signatures DNSSEC sioplc.fr ...]
;; Received 284 bytes from 194.0.36.1#53(g.ext.nic.fr) in 16 ms

cub.sioplc.fr.          3600    IN      NS      ns0.cub.sioplc.fr.
[... Enregistrements NSEC3 ...]
;; Received 373 bytes from 5.39.114.9#53(ns15.ovh.net) in 12 ms

dortmund.cub.sioplc.fr. 43200   IN      NS      ns0.dortmund.cub.sioplc.fr.
dortmund.cub.sioplc.fr. 43200   IN      NS      ns1.dortmund.cub.sioplc.fr.
;; Received 147 bytes from 192.36.250.10#53(ns0.cub.sioplc.fr) in 0 ms

ns1.dortmund.cub.sioplc.fr. 43200 IN    A       192.36.4.11
dortmund.cub.sioplc.fr. 43200   IN      NS      ns0.dortmund.cub.sioplc.fr.
dortmund.cub.sioplc.fr. 43200   IN      NS      ns1.dortmund.cub.sioplc.fr.
;; Received 147 bytes from 192.36.4.10#53(ns0.dortmund.cub.sioplc.fr) in 0 ms
```

**Explication de l'arborescence :**
1. **`.` (Racine) :** La requête contacte les serveurs racines (ex: `i.root-servers.net`) qui délèguent le TLD `.fr` aux serveurs de l'AFNIC (`d.nic.fr`, etc.).
2. **`.fr` :** Les serveurs de l'AFNIC sont interrogés et délèguent le domaine `sioplc.fr` aux serveurs d'OVH (`ns15.ovh.net`).
3. **`sioplc.fr` :** OVH renvoie la délégation du sous-domaine `cub.sioplc.fr` vers votre propre serveur DNS (`ns0.cub.sioplc.fr`).
4. **`cub.sioplc.fr` :** Le serveur de la CUB (192.36.250.10) informe que la zone de l'agence `dortmund.cub.sioplc.fr` est gérée par `ns0` et `ns1`.
5. **Résolution finale :** Le serveur maître de Dortmund renvoie avec succès l'IP de l'esclave `192.36.4.11`.

---

### Traçage vers le serveur Maître (ns0)

**Commande exécutée :**
```bash
dig +trace ns0.dortmund.cub.sioplc.fr
```

**Résultat :**
```text
etudiant@dns1:~$ dig +trace ns0.dortmund.cub.sioplc.fr

; <<>> DiG 9.20.29-1~deb13u1-Debian <<>> +trace ns0.dortmund.cub.sioplc.fr
;; global options: +cmd
.                       85096   IN      NS      a.root-servers.net.
[... Serveurs Racines ...]
;; Received 1097 bytes from 192.168.4.10#53(192.168.4.10) in 0 ms

fr.                     172800  IN      NS      g.ext.nic.fr.
fr.                     172800  IN      NS      d.nic.fr.
[... Signatures DNSSEC .fr ...]
;; Received 588 bytes from 202.12.27.33#53(m.root-servers.net) in 8 ms

sioplc.fr.              3600    IN      NS      dns15.ovh.net.
sioplc.fr.              3600    IN      NS      ns15.ovh.net.
[... Signatures DNSSEC sioplc.fr ...]
;; Received 275 bytes from 194.0.9.1#53(d.nic.fr) in 8 ms

cub.sioplc.fr.          3600    IN      NS      ns0.cub.sioplc.fr.
[... Enregistrements NSEC3 ...]
;; Received 373 bytes from 5.135.110.101#53(dns15.ovh.net) in 12 ms

dortmund.cub.sioplc.fr. 43200   IN      NS      ns0.dortmund.cub.sioplc.fr.
dortmund.cub.sioplc.fr. 43200   IN      NS      ns1.dortmund.cub.sioplc.fr.
;; Received 147 bytes from 192.36.250.10#53(ns0.cub.sioplc.fr) in 4 ms

ns0.dortmund.cub.sioplc.fr. 43200 IN    A       192.36.4.10
dortmund.cub.sioplc.fr. 43200   IN      NS      ns0.dortmund.cub.sioplc.fr.
dortmund.cub.sioplc.fr. 43200   IN      NS      ns1.dortmund.cub.sioplc.fr.
;; Received 147 bytes from 192.36.4.11#53(ns1.dortmund.cub.sioplc.fr) in 0 ms
```

**Explication :**
Tout comme pour l'esclave, la chaîne de délégation est suivie de bout en bout sans aucune erreur. Ici, c'est le serveur esclave (`192.36.4.11`) qui répond à la dernière étape pour fournir l'adresse IP du serveur maître (`192.36.4.10`), prouvant que la redondance entre ns0 et ns1 fonctionne à merveille.

---

## Conclusion

> [!success] Bon fonctionnement du résolveur et des délégations
> Les tests avec la commande `dig +trace` démontrent de manière irréfutable que le serveur DNS récursif (`dns1`) navigue correctement dans l'arbre DNS mondial pour trouver les adresses de l'infrastructure CUB.
>
> La chaîne de délégation (`.fr` -> `sioplc.fr` -> `cub.sioplc.fr` -> `dortmund.cub.sioplc.fr`) est parfaitement fluide et fonctionnelle, garantissant l'accessibilité des ressources de l'agence de Dortmund.

