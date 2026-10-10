---
description: "Configuration du hostname"
---

# Configuration du hostname

![Bannière CUB](../../assets/banniere-cub.png)

!!! abstract "Informations sur le document"
    - **Auteur :** KADA Amine
    - **Classe :** BTS SIO 2 - Option SISR
    - **Date :** 30/09/2026
    - **Sujet :** Configuration du hostname

---

## Contexte

La configuration rigoureuse du nom d'hôte (hostname) est primordiale pour l'identification unique et standardisée des serveurs au sein de l'infrastructure CUB. Ce paramètre impacte directement la journalisation centralisée, la résolution DNS interne et le bon fonctionnement de certains services.

Dans le contexte de l'agence de Dortmund, le nom de domaine complet (FQDN) doit impérativement respecter la structure suivante :
`NOM_VM.dortmund.cub.sioplc.fr` *(ex : `bastion1.dortmund.cub.sioplc.fr`)*.

## Vérification de l'état actuel

**3.1. Consultation des paramètres d'hôte.**
Identifier l'identité courante du serveur avant d'appliquer la nouvelle norme de nommage.

```bash
hostnamectl status
hostname
```

## Changement du nom d'hôte

!!! warning "Avertissement de redémarrage de services"
    Bien que la modification du hostname soit appliquée à chaud, certains processus (ex: `syslog`) peuvent nécessiter un redémarrage pour acquérir la nouvelle valeur.

**4.1. Définition de la nouvelle identité cible.**
Utilisation de l'outil d'administration `hostnamectl` pour modifier le hostname localement de manière persistante (remplacez `NOM_VM` par le nom court de votre serveur).

```bash
sudo hostnamectl set-hostname NOM_VM
```

- `set-hostname` : Met à jour le nom d'hôte statique dans le fichier `/etc/hostname`.

## Configuration de la résolution locale (/etc/hosts)

Le changement via `hostnamectl` ne met pas à jour le fichier de résolution local `/etc/hosts`. Il est impératif de le modifier manuellement pour que la machine puisse résoudre son propre FQDN sur son adresse locale. Sans cela, des commandes comme `sudo` risquent d'afficher des avertissements du type *"unable to resolve host"*.

**5.1. Édition du fichier hosts :**

```bash
sudo nano /etc/hosts
```

**5.2. Ajout du FQDN CUB :**
Modifiez la ligne `127.0.1.1` (ou ajoutez l'IP de votre serveur si elle est fixe) pour y intégrer le FQDN complet suivi du nom court :

```text
127.0.0.1       localhost
127.0.1.1       NOM_VM.dortmund.cub.sioplc.fr    NOM_VM

# Lignes suivantes inchangées...
```

*Remarque : Respectez bien la syntaxe `IP FQDN Alias`.*

## Vérification de la persistance et résolution

**6.1. Vérification de l'écriture disque.**
S'assurer que le fichier de configuration statique contient le bon nom court.

```bash
cat /etc/hostname
```

**6.2. Test de la résolution système.**
Vérifier que le système d'exploitation parvient à résoudre le nouveau nom d'hôte et afficher son FQDN complet de Dortmund.

```bash
hostname -f
```
*(Le résultat attendu est : `NOM_VM.dortmund.cub.sioplc.fr`)*

```bash
getent hosts NOM_VM
```

!!! success "Critère de réussite"
    L'opération est validée si la commande `hostname -f` renvoie bien le FQDN complet de Dortmund (`NOM_VM.dortmund.cub.sioplc.fr`) et qu'aucune erreur réseau locale n'est remontée par le système.
