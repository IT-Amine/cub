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

### 2.3. Vérification de la journalisation (Logs via AppArmor)

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
