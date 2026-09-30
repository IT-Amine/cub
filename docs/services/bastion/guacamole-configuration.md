---
description: Configuration des accès, utilisateurs et connexions sur le bastion Guacamole.
---

# BLOC 2 - Gestion des utilisateurs et des sessions (Guacamole)

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 30/09/2026</p>
    <p><strong>Contexte :</strong> CUB - Situation 4 - Activité 2 (Configuration du Bastion)</p>
</div>

---

## 1. PARTIE 2 : Gestion des utilisateurs

Toutes les configurations suivantes sont réalisées depuis l'interface web de Guacamole en se connectant initialement avec le compte par défaut (`guacadmin`). 

### 1.1. Sécurisation du compte administrateur
Création d'un compte administrateur dédié et suppression du compte par défaut.

1. Naviguer vers **Paramètres** (en haut à droite) > onglet **Utilisateurs** > **Nouvel utilisateur**.
2. Nom d'utilisateur : `adminbastion`.
3. Mot de passe : *Saisir un mot de passe robuste via un gestionnaire dédié*.
4. **Autorisations :** Cocher toutes les cases (Administrer le système, Créer des utilisateurs, etc.) **SAUF** le droit d'audit (`audit system`).
5. Enregistrer, se déconnecter, puis se reconnecter avec `adminbastion`.
6. Retourner dans **Utilisateurs** et **supprimer le compte `guacadmin`** par défaut.

> **Question 4 - Recommandations de l'ANSSI concernant l'audit :**
> Conformément au principe de séparation des privilèges, l'administrateur système du bastion ne doit pas posséder les droits d'audit. Si un administrateur malveillant (ou compromis) dispose de ce droit, il pourrait altérer ou effacer les journaux de connexion et les enregistrements de session pour masquer ses traces. Le rôle d'auditeur doit être strictement confié à une entité tierce (ex: RSSI).

### 1.2. Création des groupes d'utilisateurs
Création de deux groupes distincts pour restreindre les accès par système d'exploitation.

1. Naviguer vers **Paramètres** > onglet **Groupes** > **Nouveau groupe**.
2. **Groupe 1 :** `ServeursLinux`.
   - Autorisations : Cocher uniquement **"Créer de nouvelles connexions"**.
3. **Groupe 2 :** `ServeursWindows`.
   - Autorisations : Cocher uniquement **"Créer de nouvelles connexions"**.

### 1.3. Création des comptes d'administration déléguée
Création des comptes associés aux groupes précédents.

1. Naviguer vers **Paramètres** > onglet **Utilisateurs** > **Nouvel utilisateur**.
2. **Utilisateur 1 :** `adminlinux`.
   - Autorisations : Cocher **"Créer de nouvelles connexions"** et **"Modifier son propre mot de passe"**.
   - Groupes (en bas de page) : Cocher `ServeursLinux`.
3. **Utilisateur 2 :** `adminwindows`.
   - Autorisations : Cocher **"Créer de nouvelles connexions"** et **"Modifier son propre mot de passe"**.
   - Groupes : Cocher `ServeursWindows`.

---

## 2. PARTIE 3 : Gestion des sessions SSH et RDP

### 2.1. Configuration de la session SSH (Serveur Linux)
1. Naviguer vers **Paramètres** > onglet **Connexions** > **Nouvelle connexion**.
2. **Nom :** Serveur Linux SSH
3. **Protocole :** SSH
4. **Réseau :** 
   - Nom d'hôte : `192.168.8.X` (Remplacer le X par l'IP exacte du serveur Linux).
   - Port : `22`
5. **Authentification :** Saisir les identifiants locaux de la machine Linux.
6. **Affectation au groupe :** Dans les paramètres de la connexion (ou du groupe d'utilisateurs), affecter cette connexion au groupe `ServeursLinux`.

> **Vérification (Question 7 & 8) :** 
> En se connectant avec l'utilisateur `adminlinux`, seule la connexion SSH apparaît et lance un rebond valide. En se connectant avec `adminwindows`, la connexion SSH est invisible (accès refusé).

### 2.2. Configuration de la session RDP (ServeurWAC1)
1. Naviguer vers **Paramètres** > onglet **Connexions** > **Nouvelle connexion**.
2. **Nom :** ServeurWAC1 RDP
3. **Protocole :** RDP
4. **Réseau :**
   - Nom d'hôte : `192.168.8.5`
   - Port : `3389`
5. **Authentification :** Saisir les identifiants locaux du Serveur Windows.
6. **Affectation au groupe :** Affecter cette connexion au groupe `ServeursWindows`.
*(Vérifier avec `adminwindows` que la connexion s'ouvre correctement, et qu'elle est invisible pour `adminlinux`).*

---

## 3. Analyse réseau et Rupture Protocolaire

L'observation du trafic réseau via `tcpdump` (sur le serveur Linux) et `Wireshark` (sur le serveur ServeurWAC1) met en évidence le fonctionnement fondamental d'un bastion : **la rupture protocolaire**.

> **Constatation (Questions 9 & 11) :**
> Lors d'une écoute réseau sur le serveur cible, les trames entrantes (TCP/22 pour SSH ou TCP/3389 pour RDP) ont pour adresse IP source **l'adresse IP du bastion Guacamole**, et non l'adresse IP du poste physique de l'étudiant.
>
> **Justification :** Le bastion agit comme un proxy applicatif strict. Il scinde la communication en deux flux totalement isolés. Le poste client ne dialogue avec le bastion qu'en HTTPS (port 443). Le démon interne du bastion (`guacd`) initie lui-même une nouvelle requête vers la cible dans le protocole d'administration natif (SSH/RDP). Il est donc impossible pour un attaquant sur le réseau d'attaquer directement les ports d'administration des serveurs, car seul le bastion est autorisé à s'y connecter.

### Diagramme de Séquence de la Rupture Protocolaire

```mermaid
sequenceDiagram
    autonumber
    participant Client as Poste Étudiant (Navigateur)
    participant Nginx as Proxy Nginx (Port 443)
    participant Guac as Tomcat Guacamole (Port 8080)
    participant Guacd as Démon guacd
    participant Cible as Serveur Cible (192.168.8.X)

    rect rgb(230, 240, 255)
        Note over Client, Guac: Flux externe chiffré (Web)
        Client->>Nginx: Connexion HTTPS (TLS)
        Nginx->>Guac: Transfert HTTP (Proxy Pass)
    end
    
    Guac->>Guacd: Demande d'ouverture de session
    
    rect rgb(255, 230, 230)
        Note over Guacd, Cible: Flux interne d'administration (Rupture)
        Guacd->>Cible: Initiation connexion native (SSH:22 ou RDP:3389)
        Cible-->>Guacd: Authentification et flux vidéo/texte
    end
    
    Guacd-->>Guac: Conversion protocolaire (Guacamole Protocol)
    Guac-->>Nginx: Renvoi des trames Web
    Nginx-->>Client: Affichage dynamique (Canvas HTML5)