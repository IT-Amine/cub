![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere_cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 22/01/2026</p>
    <p><strong>Contexte :</strong> VLSM & Table de routage CUB - Situation 1</p>
</div>

---
### Calcul VLSM - Agence Dortmund

- VLAN 54 - Production - 120 Hôtes
- VLAN 10 - Clients - 32 Hôtes
- VLAN 20 - Admin Sys.Réseau - 6 Hôtes
- Adresse de sous-réseaux : 192.168.4.0/24

#### Sous-réseau 1 : Production — 120 hôtes

120 + 2 = 122 → 2⁷ = 128 → 32 - 7 = 25 → **CIDR /25**
- Réseau : 192.168.4.0 /25
- Masque : 255.255.255.128
- IP utilisables : 192.168.4.1 à 192.168.4.125
- Passerelle : 192.168.4.126
- Broadcast : 192.168.4.127

#### Sous-réseau 2 : Clients — 32 hôtes

32 + 2 = 34 → 2⁶ = 64 → 32 - 6 = 26 → **CIDR /26**
- Réseau : 192.168.4.128 /26
- Masque : 255.255.255.192
- IP utilisables : 192.168.4.129 à 192.168.4.189
- Passerelle : 192.168.4.190
- Broadcast : 192.168.4.191

#### Sous-réseau 3 : Admin Sys.Réseau — 6 hôtes

6 + 2 = 8 → 2⁴ = 16 → 32 - 4 = 28 → **CIDR /28**
- Réseau : 192.168.4.192 /28
- Masque : 255.255.255.240
- IP utilisables (hôtes) : 192.168.4.193 à 192.168.4.205
- Passerelle : 192.168.4.206
- Broadcast : 192.168.4.207

---
## Maquette de notre Agence à Dortmund - CUB 

1. Maquette logique
![Maquette logique](assets/maquette_logique.jpg)

2. Maquette physique
![Maquette physique](assets/maquette_physical.jpg)

---
## Table de routage CUB
### Table de routage coeur du réseau SW_L3_Dortmund

| **Name**                        | **Réseau de destination** | **Masque**            | **Passerelle IP (Next Hop)** | **Interface de sortie** | **Type** |
| ------------------------------- | ------------------------- | --------------------- | ---------------------------- | ----------------------- | -------- |
| **VLAN 54 - Production**        | 192.168.4.0               | 255.255.255.128 (/25) | -                            | 192.168.4.126           | **C**    |
| **VLAN 10 - Clients**           | 192.168.4.128             | 255.255.255.192 (/26) | -                            | 192.168.4.190           | **C**    |
| **VLAN 20 - Admin Sys.**        | 192.168.4.192             | 255.255.255.240 (/28) | -                            | 192.168.4.206           | **C**    |
| **VLAN 2 - Transit LAN**        | 192.168.44.248            | 255.255.255.248 (/29) | -                            | 192.168.44.253          | **C**    |
| **Route par défaut (Internet)** | 0.0.0.0                   | 0.0.0.0 (/0)          | 192.168.44.254               | 192.168.44.253          | **S**    |

### Table de routage Stormshield SNS 210 - Dortmund

| **Name**                        | **Réseau de destination** | **Masque**            | **Passerelle IP** | **Interface de sortie** | **Type** |
| ------------------------------- | ------------------------- | --------------------- | ----------------- | ----------------------- | -------- |
| **Réseau LAN**                  | 192.168.44.248            | 255.255.255.248 (/29) | -                 | 192.168.44.254          | **C**    |
| **DMZ Dortmund**                | 192.36.4.0                | 255.255.255.0 (/24)   | -                 | 192.36.4.254            | **C**    |
| **Réseau WAN**                  | 192.36.253.0              | 255.255.255.0 (/24)   | -                 | 192.36.253.40           | **C**    |
| **LANs Internes**               | 192.168.4.0               | 255.255.255.0 (/24)   | 192.168.44.253    | 192.168.44.254          | **S**    |
| **Route par défaut (Internet)** | 0.0.0.0                   | 0.0.0.0 (/0)          | 192.36.253.254    | 192.36.253.40           | **S**    |


---

## Table NAT CUB

| **Name** | **IP SRC Avant**   | **Port SRC Avant** | **IP DEST Avant** | **Port DEST Avant** |
| -------- | ------------------ | ------------------ | ----------------- | ------------------- |
| LAN      | 192.168.4.0 /24    | *                  | *                 | *                   |
| INTER CO | 192.168.44.248 /29 | *                  | *                 | *                   |

| **Name** | **IP SRC Après** | **Port SRC Après** | **IP DEST Après** | **Port DEST Après** |
| -------- | ---------------- | ------------------ | ----------------- | ------------------- |
| LAN      | 192.36.253.40    | *                  | *                 | *                   |
| INTER CO | 192.36.253.40    | *                  | *                 | *                   |
