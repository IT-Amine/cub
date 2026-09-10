---
description: Procédure de déploiement et de configuration d'un serveur DNS Récursif.
---

# BLOC 3 - Configuration DNS Récursif

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere_cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Contexte :</strong> Configuration d'un DNS récursif (Bind9 sur Debian)</p>
</div>

---

## 1. Contexte
Un serveur DNS **récursif** (ou résolveur) a pour rôle de répondre aux requêtes DNS des postes clients de l'entreprise. Contrairement à un DNS faisant autorité (qui gère sa propre zone, ex: `cub.sioplc.fr`), le récursif va interroger les serveurs racine (Root Servers) et les serveurs d'autorité sur Internet pour trouver les adresses IP demandées par les utilisateurs, puis va **mettre en cache** les réponses pour accélérer les requêtes futures.

Dans l'infrastructure CUB, ce service peut être installé sur un serveur Debian via le paquet `bind9`.

---

## 2. Installation de Bind9

Sur votre serveur Debian (par exemple, dans la DMZ ou le LAN Admin) :

```bash
# Mise à jour des paquets
sudo apt update && sudo apt upgrade -y

# Installation du service DNS Bind9 et de ses utilitaires (dig, nslookup)
sudo apt install bind9 bind9utils bind9-doc dnsutils -y
```

---

## 3. Configuration en mode Récursif (Cache)

Le fichier de configuration principal pour les options de Bind9 est `/etc/bind/named.conf.options`.

```bash
# Édition du fichier de configuration
sudo nano /etc/bind/named.conf.options
```

Modifiez le fichier pour l'adapter à la configuration suivante :

```text
acl "trusted" {
    127.0.0.0/8;
    192.168.0.0/16;   # Autoriser le réseau local CUB
    172.16.0.0/12;    # Autoriser les réseaux pédagogiques
};

options {
    directory "/var/cache/bind";

    # Activer la récursion (Essentiel pour un DNS récursif)
    recursion yes;

    # N'autoriser que nos réseaux internes à faire des requêtes
    allow-query { trusted; };

    # Sécurité : Cacher la version de Bind pour éviter le fingerprinting
    version "Non communiquée";

    # Forwarders (Optionnel) : 
    # Si Bind ne connaît pas la réponse, il peut demander directement 
    # à un autre DNS récursif (ex: Quad9 ou FDN) plutôt qu'aux serveurs racines.
    forwarders {
        9.9.9.9;      # Quad9 (Filtrage malware)
        80.67.169.12; # FDN (Neutre)
    };
    forward only;

    dnssec-validation auto;
    listen-on-v6 { any; };
};
```

---

## 4. Validation et Redémarrage

Avant de relancer le service, il est indispensable de vérifier que la syntaxe du fichier de configuration est correcte :

```bash
# Vérification de la syntaxe
sudo named-checkconf

# Si la commande ne retourne rien, la syntaxe est bonne !
# On redémarre le service :
sudo systemctl restart bind9

# On vérifie que le service tourne correctement :
sudo systemctl status bind9
```

---

## 5. Tests de résolution (Client)

Depuis un poste client (ex: VLAN 10 ou 54), configurez l'adresse IP de ce serveur Debian comme DNS principal.
Ensuite, effectuez un test avec l'outil `nslookup` ou `dig`.

```bash
# Test de résolution externe
dig google.com @192.168.X.X

# Test de temps de réponse (Cache)
# Lancez la commande deux fois. La deuxième fois, le "Query time" 
# devrait être de 0 msec grâce à la mise en cache de Bind9.
```

