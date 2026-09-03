![Bannière CUB](assets/banniere_cub.png)
---

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 22/01/2026</p>
    <p><strong>Contexte :</strong> Question bases SOC - Situation 1</p>
</div>

---

### Schéma OSI

![Schéma réseau ou description](https://datasave.qsfptek.com/resources/image/2023-03-25177434.png)

---

#### 2. Expliquer ce qui a poussé le service RSSI à opter pour une solution UTM Stormshield par rapport à ceux à un simple pare-feu stateful traditionnel ?

- **Manque de visibilité du stateful (Couche 4) :** *Un pare-feu stateful traditionnel filtre uniquement les adresses IP, les ports et l'état des connexions TCP/UDP. Il est incapable d'analyser le contenu réel des paquets. Si une attaque ou un malware transite via un port légitime et autorisé (comme le port 443 en HTTPS), le stateful le laissera passer sans rien détecter.*

- **Sécurité globale et analyse applicative (Couche 7) avec l'UTM :** *L'UTM apporte une inspection en profondeur jusqu'au niveau applicatif. Il regroupe en un seul équipement plusieurs briques essentielles : antivirus de flux, filtrage web, antispam, prévention des fuites de données et système de prévention d'intrusions.*

- **Simplification et réduction des coûts :** *Pour le RSSI, déployer un UTM permet de centraliser la gestion de la sécurité sur une seule interface au lieu d'empiler plusieurs outils distincts, ce qui facilite la supervision des logs et réduit le coût d'administration.*

#### 3. Donner 2 arguments en faveur d'un boîtier UTM Stormshield par rapport à ceux proposés par des entreprises concurrentes telles que Palo Alto ou CheckPoint ?

- *Stormshield est une entreprise française, filiale d'Airbus. Contrairement aux solutions américaines (Palo Alto) ou israéliennes (Check Point), Stormshield garantit que le traitement et les logs réseau ne sont pas soumis aux lois extraterritoriales américaines. C'est un argument déterminant pour garantir une stricte conformité au RGPD et préserver la souveraineté des données sensibles de l'organisation.*

#### 4. Dans le schéma proposé dans le contexte CUB, expliquer pourquoi la présence d'un réseau local unique au sein des agences pose des problèmes de sécurité. Puis proposer une solution qui prenne en compte les différents services recensés dans le document 1.1 du dossier documentaire

- *Le problème d'avoir tout le monde sur un réseau unique, c'est l'absence de cloisonnement : si un poste client est infecté, la menace peut se propager directement à la production ou à l'administration. La solution est de segmenter l'infrastructure en créant un VLAN par service, couplé à un adressage VLSM pour adapter la taille de chaque sous-réseau au nombre exact d'hôtes (60 pour la Prod, 16 pour les Clients et 3 pour l'Admin).*

---
