---
description: Procédure de déploiement et de configuration initiale pour un Bastion Guacamole (via Docker).
---

# BLOC 2 - Bastion Guacamole (Docker)

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 30/09/2026</p>
    <p><strong>Contexte :</strong> Déploiement d'un Bastion Guacamole sécurisé sous Debian 13</p>
</div>

---

## 1. Contexte
Dans le cadre de la sécurisation des accès distants de l'infrastructure CUB, un bastion basé sur Apache Guacamole est déployé. En raison d'incompatibilités de paquets (comme `freerdp3`) sur Debian 13, l'installation est réalisée via Docker.

L'architecture repose sur quatre composants isolés :
1. **Guacamole** : L'interface web de gestion.
2. **Guacd** : Le proxy protocolaire gérant nativement RDP, VNC et SSH.
3. **PostgreSQL** : La base de données de configuration (utilisateurs, connexions).
4. **Nginx** : Le proxy inverse assurant le chiffrement HTTPS des communications.

Docker garantit un déploiement rapide, une portabilité facilitée et le redémarrage automatique des services en cas d'incident.

---

## 2. Installation des prérequis (Docker & Pare-feu)

### 2.1. Installation de Docker
Sur Debian 13, on utilise le script officiel pour garantir la compatibilité et obtenir les dernières versions du moteur Docker et du plugin Compose.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg ufw
curl -fsSL https://get.docker.com | sudo sh
```

Activation et démarrage du service Docker :

```bash
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl status docker
```

### 2.2. Configuration du pare-feu UFW

Conformément au principe du moindre privilège, les communications réseau sont limitées au strict nécessaire.

```bash
sudo ufw reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 8443/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

!!! warning "Attention - Routage Docker"
    Docker gère ses propres règles réseau. Le port 8080 de l'application Guacamole ne sera pas exposé publiquement sur l'hôte, seul le proxy Nginx (8443) sera accessible de l'extérieur.

---

## 3. Préparation de l'environnement de travail

### 3.1. Création de l'arborescence

On crée les dossiers nécessaires pour la persistance des données et les certificats Nginx.

```bash
sudo mkdir -p /opt/guacamole/initdb
sudo mkdir -p /opt/guacamole/data
sudo mkdir -p /opt/guacamole/drive
sudo mkdir -p /opt/guacamole/nginx/ssl
sudo mkdir -p /opt/guacamole/nginx/templates
sudo chown -R $USER:$USER /opt/guacamole
cd /opt/guacamole
```

### 3.2. Initialisation de la base de données

On génère le script SQL d'initialisation (version 1.6.0) pour créer les tables nécessaires dans PostgreSQL.

```bash
sudo docker run --rm 'guacamole/guacamole:1.6.0' /opt/guacamole/bin/initdb.sh --postgresql > ./initdb/initdb.sql
```

### 3.3. Génération du certificat SSL

Création d'un certificat auto-signé pour sécuriser l'accès web via HTTPS.

```bash
sudo openssl req -nodes -newkey rsa:2048 -new -x509  -keyout nginx/ssl/self-ssl.key  -out nginx/ssl/self.cert  -subj '/C=FR/ST=Centre-Val-de-Loire/L=Tours/O=CUB/CN=guac.cub.local'
```

---

## 4. Fichiers de configuration

### 4.1. Fichier d'environnement (.env)

Afin de ne pas stocker les mots de passe en clair dans le fichier de déploiement principal, on crée un fichier d'environnement.

```bash
nano .env
```

```text
POSTGRES_DB=guacamole
POSTGRES_USER=guacamole
POSTGRES_PASSWORD=MotDePasseRootFort!
```

### 4.2. Configuration du reverse proxy (Nginx)

Création de la configuration Nginx chargée d'intercepter les requêtes HTTPS (port 443 interne) et de les rediriger vers le conteneur Guacamole (port 8080).

```bash
nano nginx/templates/guacamole.conf.template
```

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name localhost;
    ssl_certificate /etc/nginx/ssl/self.cert;
    ssl_certificate_key /etc/nginx/ssl/self-ssl.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
    ssl_ecdh_curve secp384r1;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    ssl_stapling off;
    ssl_stapling_verify off;

    location / {
        proxy_pass http://guacamole:8080/guacamole/;
        proxy_buffering off;
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $http_connection;
        proxy_cookie_path /guacamole/ /;
        access_log off;
        client_max_body_size 4096m;
    }

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

### 4.3. Fichier Docker Compose

Création de l'orchestration des quatre services.

```bash
nano docker-compose.yml
```

```yaml
services:
  # guacd (proxy protocolaire RDP/SSH)
  guacd:
    container_name: guacd_cub
    image: guacamole/guacd:1.6.0
    networks:
      - guacnetwork
    restart: always
    volumes:
      - ./drive:/drive:rw

  # postgres (base de données)
  postgres:
    container_name: postgres_cub
    environment:
      PGDATA: /var/lib/postgresql/data/guacamole
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_USER: ${POSTGRES_USER}
    image: postgres:15.2-alpine
    networks:
      - guacnetwork
    restart: always
    volumes:
      - ./initdb:/docker-entrypoint-initdb.d:z
      - ./data:/var/lib/postgresql/data:Z

  # guacamole (interface web)
  guacamole:
    container_name: guacamole_cub
    depends_on:
      - guacd
      - postgres
    environment:
      GUACD_HOSTNAME: guacd
      POSTGRESQL_ENABLED: "true"
      REMOTE_IP_VALVE_ENABLED: "true"
      POSTGRESQL_DATABASE: ${POSTGRES_DB}
      POSTGRESQL_HOSTNAME: postgres
      POSTGRESQL_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRESQL_USERNAME: ${POSTGRES_USER}
    image: guacamole/guacamole:1.6.0
    networks:
      - guacnetwork
    restart: always

  # nginx (reverse proxy HTTPS)
  nginx:
    container_name: nginx_cub
    restart: always
    image: nginx:latest
    volumes:
      - ./nginx/templates:/etc/nginx/templates:ro
      - ./nginx/ssl/self.cert:/etc/nginx/ssl/self.cert:ro
      - ./nginx/ssl/self-ssl.key:/etc/nginx/ssl/self-ssl.key:ro
    ports:
      - 8443:443
    networks:
      - guacnetwork

networks:
  guacnetwork:
    driver: bridge
```

---

## 5. Déploiement final et Recette

On lance l'ensemble de l'infrastructure en arrière-plan :

```bash
sudo docker compose up -d
sudo docker ps
```
*(Le statut des 4 conteneurs doit indiquer Up).*

**Accès à l'application :**

Ouvrir un navigateur web et accéder à l'adresse chiffrée :
`https://[IP_DU_BASTION]:8443/`

**Identifiants par défaut :**

- Utilisateur : `guacadmin`
- Mot de passe : `guacadmin`

!!! tip "Dépannage - Erreur d'authentification BDD"
    Si la page affiche une erreur générique au démarrage, c'est généralement que PostgreSQL n'a pas lu correctement le fichier d'initialisation ou a conservé d'anciennes données corrompues.
    Pour forcer une réinstallation propre de la base :
    ```bash
    sudo docker compose down
    sudo rm -rf /opt/guacamole/data
    sudo docker compose up -d
    ```

!!! warning "Sécurité"
    À la première connexion, modifier immédiatement le mot de passe du compte `guacadmin` et créer des accès délégués selon les recommandations de l'ANSSI.
