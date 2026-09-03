<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 22/01/2026</p>
    <p><strong>Contexte :</strong> Commande Cisco Packet Tracer</p>
</div>

---

1. Commutateur d'Accès Layer 2 (SW_L2_Dortmund)

```
! Passage en mode configuration
enable
configure terminal
hostname SW_L2_Dortmund

! Sécurisation 
no ip domain-lookup
service password-encryption
enable secret @dmin
banner motd # ACCES ADMINISTRATEUR SWITCH #

! Création des VLANs locaux
vlan 10
 name Clients
vlan 20
 name Admin_Sys
vlan 54
 name Production
exit

! Configuration du lien Trunk vers le SW L3
interface GigabitEthernet0/2
 switchport mode trunk
 exit

! Affectation du PC Production (VLAN 54)
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 54
 exit

! Affectation du PC Client (VLAN 10)
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 10
 exit

! Sauvegarde de la configuration
end
write
```

2. Cœur de Réseau Layer 3 (SW_L3_Dortmund)

```
! Passage en mode configuration
enable
configure terminal
hostname SW_L3_Dortmund

! ACTIVATION DU ROUTAGE (Étape cruciale)
ip routing

! Sécurisation 
no ip domain-lookup
service password-encryption
enable secret @dmin
banner motd # ACCES ADMINISTRATEUR SWITCH #

! Création des VLANs locaux
vlan 2
 name Transit_LAN
vlan 10
 name Clients
vlan 20
 name Admin_Sys
vlan 54
 name Production
exit

! Configuration des interfaces virtuelles (Passerelles des PC)
interface Vlan10
 ip address 192.168.4.190 255.255.255.192
 no shutdown
interface Vlan20
 ip address 192.168.4.206 255.255.255.240
 no shutdown
interface Vlan54
 ip address 192.168.4.126 255.255.255.128
 no shutdown
interface Vlan2
 ip address 192.168.44.252 255.255.255.248
 no shutdown
exit

! Configuration du lien Trunk vers le SW L2
interface GigabitEthernet0/2
 switchport trunk encapsulation dot1q
 switchport mode trunk
 exit

! Affectation du Serveur AD Production en direct (VLAN 54)
interface FastEthernet0/20
 switchport mode access
 switchport access vlan 54
 exit

! Configuration du port de Transit (vers le Routeur)
! Si le routeur est sur Gig0/1
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 2
 exit

! Route par défaut vers le Pare-feu
ip route 0.0.0.0 0.0.0.0 192.168.44.254

! Sauvegarde
end
write
```

3. Pare-feu / Routeur (Stormshield SNS 210 - Dortmund)

```
! Passage en mode configuration
enable
configure terminal
hostname RTE-Stormshield

! Sécurisation 
no ip domain-lookup
service password-encryption
enable secret @dmin
banner motd # ACCES ADMINISTRATEUR FIREWALL #

! Configuration des interfaces physiques et zones NAT
! Interface LAN (Transit vers le SW_L3)
interface GigabitEthernet0/0
 ip address 192.168.44.254 255.255.255.248
 ip nat inside
 no shutdown
 exit

! Interface WAN (Vers Internet / Siège CUB)
interface GigabitEthernet0/1
 ip address 192.36.253.40 255.255.255.0
 ip nat outside
 no shutdown
 exit

! Interface DMZ (Vers les serveurs Web et DNS)
interface GigabitEthernet0/2
 ip address 192.36.4.254 255.255.255.0
 ip nat inside
 no shutdown
 exit

! Route de retour vers les LANs (Résumé)
ip route 192.168.4.0 255.255.255.0 192.168.44.252

! Route par défaut vers le WAN CUB
ip route 0.0.0.0 0.0.0.0 192.36.253.254

! --- CONFIGURATION DU NAT ---

! ACL pour définir qui a le droit d'aller sur Internet
access-list 1 permit 192.168.4.0 0.0.0.255
access-list 1 permit host 192.168.44.252

! NAT Dynamique : Accès Internet pour les PC clients & Administrateur
ip nat inside source list 1 interface GigabitEthernet0/1 overload

! Sauvegarde
end
write
```

---
