---
description: Théorie et mise en place d'une zone de résolution DNS inverse (Reverse DNS) sous Bind9.
---

# BLOC 2 - Résolution DNS Inverse

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 08/10/2026</p>
    <p><strong>Contexte :</strong> Configuration et explication de la résolution DNS inverse (Reverse DNS).</p>
</div>

---

## 1. Sommaire

- [1. Sommaire](#1-sommaire)
- [2. Qu'est-ce que la résolution inverse ?](#2-quest-ce-que-la-resolution-inverse-)
- [3. Mise en place d'une résolution inverse](#3-mise-en-place-dune-resolution-inverse)

---

## 2. Qu'est-ce que la résolution inverse ?

Une recherche DNS inversée est une requête DNS pour obtenir le nom de domaine associé à une adresse IP donnée. Cette méthode est le contraire de la recherche DNS directe, plus couramment utilisée, qui consiste à interroger le système DNS pour obtenir une adresse IP.

Il existe des normes de l'Internet Engineering Task Force (IETF) suggérant que chaque domaine devrait être capable de recherche DNS inversée, mais comme les recherches inversées ne sont pas essentielles au fonctionnement normal d'Internet, elles ne constituent pas une exigence stricte. Par conséquent, les recherches DNS inversées ne sont pas universellement adoptées.

Les recherches DNS inversées interrogent les serveurs DNS pour obtenir un enregistrement `PTR` (pointeur). Si le serveur n'a pas d'enregistrement PTR, il ne peut pas résoudre une recherche inversée. Les enregistrements PTR stockent les adresses IP avec leurs segments inversés, et leur ajoutent `.in-addr.arpa`. Par exemple, si un domaine a pour adresse IP `192.0.2.1`, l'enregistrement PTR stockera cette information sous la forme `1.2.0.192.in-addr.arpa.`.

Dans IPv6, la dernière version du protocole Internet, les enregistrements PTR sont stockés dans le domaine `.ip6.arpa` au lieu de `.in-addr.arpa`.

> [!warning] Attention
> Une résolution inverse opérationnelle est indispensable notamment dans le cadre de la mise en place d'un service de messagerie (mail) lors de la vérification de la légitimité des serveurs SMTP utilisés.

---

## 3. Mise en place d'une résolution inverse

### 3.1. Création d’un fichier de zone pour le réseau 192.36.4.0/24

Création du fichier de zone inverse pour le sous-réseau cible :

```bash
sudoedit /var/cache/bind/db.192.36.4
```

**Ajouter le contenu suivant :**

```text
$TTL 43200
4.36.192.in-addr.arpa. IN SOA ns0.dortmund.cub.sioplc.fr. postmaster.dortmund.cub.sioplc.fr. ( 
    2021070601 ; Serial 
    604800     ; Refresh 
    86400      ; Retry 
    2419200    ; Expire 
    604800 )   ; Negative Cache TTL 

; Enregistrements Name Server (NS)
4.36.192.in-addr.arpa.  IN NS   ns0.dortmund.cub.sioplc.fr. 

; Enregistrements PTR
10.4.36.192.in-addr.arpa. IN PTR ns0.dortmund.cub.sioplc.fr. 
11.4.36.192.in-addr.arpa.  IN PTR ns1.dortmund.cub.sioplc.fr.
```

Ce fichier de zone inverse ressemble à un fichier de zone classique. Il sert à mettre en œuvre la résolution DNS inversée. Il est nécessaire que le service Bind dispose des droits appropriés afin d’accéder au fichier de zone inverse nouvellement créé :

```bash
sudo chown bind:bind /var/cache/bind/db.192.36.4
```

### 3.2. Déclaration de la zone inverse dans le fichier local

Déclaration de la nouvelle zone dans la configuration locale de Bind9 :

```bash
sudoedit /etc/bind/named.conf.local
```

**Ajouter le bloc suivant :**

```text
zone "4.36.192.in-addr.arpa" { 
    type master; 
    file "/var/cache/bind/db.192.36.4"; 
};
```

### 3.3. Prise en compte des modifications

Une fois le fichier de configuration sauvegardé, recharger le service pour appliquer la nouvelle zone inverse :

```bash
sudo systemctl reload bind9
```


---

## 4. Validation et Tests

Pour vérifier que la résolution inverse fonctionne correctement, on peut utiliser des utilitaires de requêtes DNS classiques (`dig`, `nslookup` ou `host`) en interrogeant directement une adresse IP.

### 4.1. Test avec la commande `dig`

La commande `dig` couplée à l'option `-x` permet d'interroger explicitement la zone inverse (PTR).

```bash
dig @127.0.0.1 -x 192.36.4.10
```

**Résultat attendu :** 
Dans la section `ANSWER SECTION`, vous devriez voir la correspondance avec le nom d'hôte.
```text
;; ANSWER SECTION:
10.4.36.192.in-addr.arpa. 43200 IN	PTR	ns0.dortmund.cub.sioplc.fr.
```

### 4.2. Test avec la commande `nslookup`

```bash
nslookup 192.36.4.11 127.0.0.1
```

**Résultat attendu :**
```text
11.4.36.192.in-addr.arpa	name = ns1.dortmund.cub.sioplc.fr.
```

### 4.3. Test avec la commande `host`

```bash
host 192.36.4.10
```

**Résultat attendu :**
```text
10.4.36.192.in-addr.arpa domain name pointer ns0.dortmund.cub.sioplc.fr.
```
