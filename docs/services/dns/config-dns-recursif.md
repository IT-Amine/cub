---
description: Procédure de déploiement et de configuration d'un serveur DNS Récursif avec Unbound.
---

# BLOC 2 - Configuration DNS Récursif

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 16/09/2026</p>
    <p><strong>Contexte :</strong> Configuration d'un DNS récursif (Unbound sur Debian)</p>
</div>

---

## 1. Contexte
Un serveur DNS **récursif** (ou résolveur) a pour rôle de répondre aux requêtes DNS des postes clients de l'entreprise. Contrairement à un DNS faisant autorité, le récursif va interroger les serveurs racine sur Internet pour trouver les adresses IP demandées par les utilisateurs, puis va **mettre en cache** les réponses.

Dans l'infrastructure CUB, ce service est mis en place sur un serveur Debian via la solution **Unbound**.

---

## 2. Installation de Unbound et des outils

On installe Unbound ainsi que quelques utilitaires d'administration réseaux indispensables :

```bash
sudo apt install unbound dnsutils tcpdump tmux curl
```

---

## 3. Configuration de base de Unbound

On édite le fichier de configuration principal d'Unbound :

```bash
sudoedit /etc/unbound/unbound.conf
```

Ajoutez/Modifiez le contenu suivant (en l'adaptant à vos adresses réseau, ici l'interface `192.168.1.10`) :

```text
# Unbound configuration file for Debian.
#
# See the unbound.conf(5) man page.
# See /usr/share/doc/unbound/examples/unbound.conf for a commented reference config file.

include: "/etc/unbound/unbound.conf.d/*.conf"

server:
    # Interface d'écoute IPv4 sur le réseau
    interface: 192.168.1.10
    interface: 127.0.0.1

    # Quels réseaux ont le droit de se servir du serveur DNS recursif
    # Attention !! Ne pas laisser votre serveur récursif ouvert à tous !
    # Allow_snoop autorise le traçage des requêtes DNS avec la commande dig +trace
    access-control: 192.168.1.0/24 allow_snoop
    access-control: 127.0.0.0/8 allow_snoop

    # Fichier indiquant les serveurs DNS racines
    root-hints: "/var/lib/unbound/root.hints"

    # On cache la version de Unbound et on augmente la sécurité
    hide-version: yes
    hide-identity: yes
    qname-minimisation: yes

    # On autorise l'IPv4
    do-ip4: yes

    # On journalise et garde une trace des événements (Très important)
    logfile: /var/log/unbound.log
    verbosity: 1
    log-queries: yes
```

Il est important de vérifier ensuite que la syntaxe des lignes contenues dans le fichier de configuration est correcte :

```bash
sudo unbound-checkconf
```

---

## 4. Configuration des domaines locaux (Stub Zones)

Notre serveur récursif va nativement s’adresser aux serveurs faisant autorité sur Internet. Dans le cas où il doit traiter des domaines locaux (ex : `btssio.lan` ou `epoka.local`) en dehors de l'arborescence officielle, il faut lui indiquer les serveurs internes.

Ajoutez ces lignes à la fin de la section `server:` (ou à la racine) dans votre `/etc/unbound/unbound.conf` :

```text
    # Précision que le domaine local ne gère pas DNSSEC (désactivation de la vérification)
    domain-insecure: "btssio.lan."
    private-domain: btssio.lan.

# Déclaration de la zone locale et des serveurs internes faisant autorité
stub-zone:
    name: "btssio.lan."
    stub-addr: 172.16.20.10
    stub-addr: 172.16.20.11
```

---

## 5. Téléchargement des serveurs racines (Root Hints)

On récupère les adresses des serveurs racines et nous les stockons dans `/var/lib/unbound/root.hints`. Ce fichier est indispensable au service Unbound pour contacter le serveur racine le plus proche.

```bash
sudo curl --output /var/lib/unbound/root.hints https://www.internic.net/domain/named.cache
sudo chown -R unbound:unbound /var/lib/unbound/
```

---

## 6. Journalisation (Logs) et configuration AppArmor

On crée le fichier de log spécifique à Unbound :

```bash
sudo touch /var/log/unbound.log
sudo chown unbound:unbound /var/log/unbound.log
```

!!! warning "Attention - AppArmor"
    Sur les systèmes Debian récents, le module de sécurité **AppArmor** est activé par défaut. Il empêche nativement le service `unbound` de lire et d'écrire dans le répertoire `/var/log/`. Il est donc indispensable d'adapter ses permissions.

Éditez le profil AppArmor de Unbound :

```bash
sudoedit /etc/apparmor.d/usr.sbin.unbound
```

Ajoutez la ligne suivante (à l'intérieur du bloc d'autorisation principal) pour permettre l'écriture des logs :

```text
  # On autorise le daemon unbound à lire et ecrire dans son fichier de log
  /var/log/unbound.log rw,
```

Vérifiez que le fichier AppArmor ne contient pas d'erreurs et redémarrez les services :

```bash
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.unbound
sudo systemctl restart apparmor

sudo systemctl restart unbound
sudo systemctl status unbound
```

---

## 7. Suivi et maintenance

Pour observer les événements journalisés (requêtes DNS entrantes, erreurs, etc.) :

```bash
# Afficher l'intégralité du journal
sudo cat /var/log/unbound.log

# Observer les événements en temps réel
sudo tail -f /var/log/unbound.log
```
