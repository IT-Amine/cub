---
description: Fiche de recette et de validation pour le serveur DNS Récursif (Unbound).
---

# BLOC 2 - Recette Serveur DNS Récursif (Unbound)

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 23/09/2026</p>
    <p><strong>Contexte :</strong> Validation du serveur DNS récursif (Unbound)</p>
</div>

---

## 1. Contexte du test

Validation du bon fonctionnement du serveur DNS récursif Unbound sous Debian. Le scénario vérifie l'écoute du service sur les interfaces réseau configurées, la capacité à résoudre un nom de domaine public (requête récursive) via les serveurs racines, et la correcte écriture des événements dans le fichier de journalisation (logs) au travers des politiques AppArmor.

## 2. Procédures de validation

### 2.1. Vérification de l'écoute du service DNS

**Objectif :** S'assurer que le processus Unbound écoute bien les requêtes sur le port standard DNS (53) pour les adresses configurées.

**Commande utilisée :**

```bash
ss -tulpn | grep :53
```

- `ss` : Utilitaire réseau permettant d'afficher les statistiques des sockets.
- `-tulpn` : Arguments combinés pour afficher les sockets TCP (t), UDP (u), en écoute (l), avec les numéros de processus associés (p), sans résoudre les noms d'hôtes (n).
- `| grep :53` : Filtre la sortie pour n'afficher exclusivement que les lignes correspondant au port 53.

**Résultat attendu :**

```text
udp   UNCONN 0      0         192.168.4.11:53       0.0.0.0:*    users:(("unbound",pid=6334,fd=5))
udp   UNCONN 0      0            127.0.0.1:53       0.0.0.0:*    users:(("unbound",pid=6334,fd=3))
tcp   LISTEN 0      256       192.168.4.11:53       0.0.0.0:*    users:(("unbound",pid=6334,fd=6))
tcp   LISTEN 0      256          127.0.0.1:53       0.0.0.0:*    users:(("unbound",pid=6334,fd=4))
```

**Statut :**

- [ ] Ok
- [ ] KO

**Commentaire :**

................................................................................................................................................................................................................................................................................................................................................................

### 2.2. Test de résolution de nom de domaine (Récursion)

**Objectif :** Vérifier que le serveur est capable d'interroger la hiérarchie DNS externe pour résoudre un nom de domaine public avec un code de retour valide.

**Commande utilisée :**

```bash
dig @127.0.0.1 debian.org
```

- `dig` : Outil de requêtage des serveurs de noms de domaine (DNS).
- `@127.0.0.1` : Cible explicitement le serveur DNS local (Unbound) pour contourner d'éventuels autres DNS configurés sur le réseau.
- `debian.org` : Nom de domaine public utilisé comme cible pour le test de résolution.

**Résultat attendu :**

```text
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 58241
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; ANSWER SECTION:
debian.org.             3600    IN      A       130.89.148.77

;; SERVER: 127.0.0.1#53(127.0.0.1)
```

**Statut :**

- [ ] Ok
- [ ] KO

**Commentaire :**

................................................................................................................................................................................................................................................................................................................................................................

### 2.3. Traçage complet de la requête DNS (+trace)

**Objectif :** Valider que le serveur Unbound effectue bien le cheminement complet de la récursion en interrogeant la racine (`.`), puis le TLD (`org.`), et enfin le domaine (`debian.org.`).

**Commande utilisée :**

```bash
dig @192.168.4.11 debian.org +trace
```

- `+trace` : Force l'outil `dig` à désactiver la récursion du serveur local et à afficher le cheminement hiérarchique complet en partant des serveurs racines.

**Résultat attendu :**

```text
; <<>> DiG 9.10.6 <<>> @192.168.4.11 debian.org +trace
; (1 server found)
;; global options: +cmd
.			85958	IN	NS	d.root-servers.net.
.			85958	IN	NS	e.root-servers.net.
.			85958	IN	NS	f.root-servers.net.
.			85958	IN	NS	g.root-servers.net.
.			85958	IN	NS	h.root-servers.net.
.			85958	IN	NS	i.root-servers.net.
.			85958	IN	NS	j.root-servers.net.
.			85958	IN	NS	k.root-servers.net.
.			85958	IN	NS	l.root-servers.net.
.			85958	IN	NS	m.root-servers.net.
.			85958	IN	NS	a.root-servers.net.
.			85958	IN	NS	b.root-servers.net.
.			85958	IN	NS	c.root-servers.net.
.			85958	IN	RRSIG	NS 8 0 518400 20261006050000 20260923040000 57780 . MX47UVf3AUFPXSW9332rUsAAPoo1ppYoSLAE0Jqkiik9yEQA2jaFfIZN KFYDnoWrTvoZxMGwQ7afOcqZj9vuD1Vp6Oy5tEJw0magL64C/cs7EO/m O+UJAslrEQAWozluYVYAj9WFnysMInX+p2xiPogbO0ixFOl/81zF+2Om TVSmty4Z4NJ7/1mCU7bOQxC7Sl/5ECZ1OIM9nYFvpYHKd+hwPakRa25t uvLiMmz52clEY2+bgn6gwV/6zHN08Us7hoyh6UmtzmW9ENc3Zo/QJtTD R3C/0PwnWFXEGIIFwRCk+2RluXixI7IHHcIk3caC+o22A5gUWh+iKmI5 hzqHOg==
;; Received 1097 bytes from 192.168.4.11#53(192.168.4.11) in 1 ms

org.			172800	IN	NS	a2.org.afilias-nst.info.
org.			172800	IN	NS	a0.org.afilias-nst.info.
org.			172800	IN	NS	b2.org.afilias-nst.org.
org.			172800	IN	NS	c0.org.afilias-nst.info.
org.			172800	IN	NS	d0.org.afilias-nst.org.
org.			172800	IN	NS	b0.org.afilias-nst.org.
org.			86400	IN	DS	26974 8 2 4FEDE294C53F438A158C41D39489CD78A86BEB0D8A0AEAFF14745C0D 16E1DE32
org.			86400	IN	RRSIG	DS 8 1 86400 20261006050000 20260923040000 57780 . Ze5KTnrWSN3RCoxnPQHU+R60EhJ/j8U7EYDOUZ0MQrG/0EwQ21iRESJH og1Tgmj9URLFeIeqSdYlfs2dE4Up9LhS3JJXxHjAoVjdOgke7rDgFcOU Vsz7FntaTMigr1oJAVhCW/cw+tdsXcR/c5f2T7DM7RKj1dKOtfJOCIdQ pBlxwt7OB4+xtGHbBcvcDMY3fC5+ZAzbwXuah5SphZ5YvOYd+Hqm/upQ 5kTwa9JQ7klIaI8aAf4/tVnMeDHP2vEsNmkDgWtVLQpHGs0nSRfbh0UY wE8bih2VVJlROpzPNjro6CC/lS4sUQozMCtQgFQaxUV47n4GYFBsjYHa /1neHg==
;; Received 776 bytes from 192.36.148.17#53(i.root-servers.net) in 23 ms

debian.org.		3600	IN	NS	sec1.rcode0.net.
debian.org.		3600	IN	NS	dns4.easydns.info.
debian.org.		3600	IN	NS	nsp.dnsnode.net.
debian.org.		3600	IN	NS	sec2.rcode0.net.
debian.org.		3600	IN	DS	40756 8 2 BBE42151B1A41EFC1F7E6D74D86E601D55051D2B9EB99B1CD0CEAA6E 2A5618F5
debian.org.		3600	IN	RRSIG	DS 8 2 3600 20261009184307 20260918174307 25488 org. kFISbW9BlocHWLZRelsm8PzD4MNlm+C/h7IOd/5tk3Ixu9ugOTxIMPo0 HPC+toNvAjxe219koDvZc5DKtR6hz7bSmELZxaUrxJBWlrRype8TsRvE zbLUoIwzRXDy5T/zyVB2mfsuFhTMwIkKYYe7F4Hd1Kyvm00ThPylEi0z xIM=
;; Received 355 bytes from 199.19.56.1#53(a0.org.afilias-nst.info) in 148 ms

debian.org.		300	IN	A	151.101.2.132
debian.org.		300	IN	A	151.101.66.132
debian.org.		300	IN	A	151.101.130.132
debian.org.		300	IN	A	151.101.194.132
debian.org.		300	IN	RRSIG	A 8 2 300 20261020022652 20260910014857 29026 debian.org. cLV794KfNPKb4i42Ph23sbLd2kTjkZiVYOU68f7PFyfFCjcf94o4dy3Z JPUJupHpnLDvkAuT/TTlOYZ+EkpIE+pABGvzYANUCgy/MTo6kTDKLre1 v5D/TieWTPCgdDYHXZ5AjSj92VRRvGW/zOJkGRuee+A8Y8TXEJdhld9D N4bprGqRlqIsH/A0nLvQ8vaGfaTZBozGXHaIssCP2Fs8785j6szgtDaB sdr5rvK0NoxL3awj+LJerI84dT5qnxOM
debian.org.		300	IN	RRSIG	A 13 2 300 20261020022652 20260910014857 2461 debian.org. 6V20qfX6dLvYxPkli7+LIkIeZOYyTTGkQmwfNeZsERssaN9SnZtIzOBh dB1bpuQDYH67hEb/KrrLmhrre/QyiQ==
;; Received 443 bytes from 176.97.158.100#53(sec2.rcode0.net) in 15 ms
```

**Statut :**

- [ ] Ok
- [ ] KO

**Commentaire :**

................................................................................................................................................................................................................................................................................................................................................................

### 2.4. Vérification de la journalisation (Logs via AppArmor)

**Objectif :** Confirmer que les requêtes traitées par Unbound sont correctement inscrites dans le fichier de log et que les permissions AppArmor fonctionnent.

**Commande utilisée :**

```bash
sudo tail -n 10 /var/log/unbound.log
```

- `sudo` : Exécute la commande avec les privilèges d'administrateur nécessaires pour lire le répertoire de logs.
- `tail` : Utilitaire lisant et affichant la fin d'un fichier texte.
- `-n 10` : Spécifie que seules les 10 dernières lignes du fichier doivent être affichées.
- `/var/log/unbound.log` : Chemin absolu vers le fichier de journalisation spécifié dans la configuration d'Unbound.

**Résultat attendu :**

```text
Sep 23 16:38:12 unbound[6334:0] info: 127.0.0.1 debian.org. A IN
```

**Statut :**

- [ ] Ok
- [ ] KO

**Commentaire :**

................................................................................................................................................................................................................................................................................................................................................................
