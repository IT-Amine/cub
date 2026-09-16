---
description: Documentation et procédure technique.
---

# BLOC 2 - Commande Cub

![CUB](https://github.com/IT-Amine/cub/blob/main/docs/assets/banniere-cub.png?raw=true)

<div style="margin-top: 70px; border: 1px solid #ccc; padding: 20px; border-radius: 10px;">
    <p><strong>Auteur :</strong> KADA Amine</p>
    <p><strong>Classe :</strong> BTS SIO 2 - Option SISR</p>
    <p><strong>Date :</strong> 22/01/2026</p>
    <p><strong>Contexte :</strong> Commande Cisco Packet Tracer</p>
</div>

---

1. Commutateur d'Accès Layer 2 (SW_L2_Dortmund)

```
hostname SW_L2_Dortmund
no ip domain-lookup
vlan 2
name TRANSIT_LAN
vlan 10
name CLIENTS
vlan 20
name ADMIN_SYS
vlan 54
name PRODUCTION
!
!
!
!
!
!
interface GigabitEthernet0/1
description Uplink Trunk vers SW_L3_Dortmund Gi0/2
switchport mode trunk
switchport trunk native vlan 999
switchport trunk allowed vlan 2,10,20,54
!
interface FastEthernet0/1
description PC_Client_01 - VLAN 10
switchport mode access
switchport access vlan 10
spanning-tree portfast
spanning-tree bpduguard enable
!
interface FastEthernet0/2
description PC_Client_02 - VLAN 10
switchport mode access
switchport access vlan 10
spanning-tree portfast
spanning-tree bpduguard enable
!
interface FastEthernet0/3
description PC_Admin_01 - VLAN 20
switchport mode access
switchport access vlan 20
spanning-tree portfast
spanning-tree bpduguard enable
!
interface range FastEthernet0/4-24
description Ports libres - desactives
switchport mode access
shutdown
!
end
write
```

2. Cœur de Réseau Layer 3 (SW_L3_Dortmund)

```
hostname SW_L3_Dortmund
!
no ip domain-lookup
ip routing
!
vlan 2
name TRANSIT_LAN
!
vlan 10
name CLIENTS
!
vlan 20
name ADMIN_SYS
!
vlan 54
name PRODUCTION
!
interface GigabitEthernet0/1
description Lien Transit vers RTE-Stormshield Gi0/0 - VLAN 2
switchport mode access
switchport access vlan 2
spanning-tree portfast
!
interface GigabitEthernet0/2
description Trunk 802.1Q vers SW_L2_Dortmund Gi0/1
switchport trunk encapsulation dot1q
switchport mode trunk
switchport trunk native vlan 999
switchport trunk allowed vlan 2,10,20,54
!
interface FastEthernet0/1
description SRV_AD_Dortmund - VLAN 54 Production
switchport mode access
switchport access vlan 54
spanning-tree portfast
spanning-tree bpduguard enable
!
interface range FastEthernet0/2-24
description Ports libres - desactives
switchport mode access
shutdown
!
interface Vlan2
description Transit LAN vers Pare-feu
ip address 192.168.44.252 255.255.255.248
no shutdown
!
interface Vlan10
description Passerelle VLAN 10 Clients
ip address 192.168.4.190 255.255.255.192
no shutdown
!
interface Vlan20
description Passerelle VLAN 20 Admin_Sys
ip address 192.168.4.206 255.255.255.240
no shutdown
!
interface Vlan54
description Passerelle VLAN 54 Production
ip address 192.168.4.126 255.255.255.128
no shutdown
ip route 0.0.0.0 0.0.0.0 192.168.44.254
!
!
spanning-tree mode rapid-pvst
spanning-tree vlan 2,10,20,54 priority 4096
!
end
write
```

3. Pare-feu / Routeur (Stormshield SNS 210 - Dortmund)

```
hostname SW_DMZ_Dortmund
!
no ip domain-lookup
!
interface GigabitEthernet0/1
description Uplink vers RTE-Stormshield Gi0/2 - ZONE DMZ
switchport mode access
!
interface FastEthernet0/1
description SRV_WEB_D
switchport mode access
spanning-tree portfast
!
interface FastEthernet0/2
description SRV_DNS_DMZ
switchport mode access
spanning-tree portfast
!
interface range FastEthernet0/3-24
description Ports libres - desactives
switchport mode access
shutdown
!
end
```

4. Pare-feu / Routeur (Stormshield SNS 210 - Dortmund)

```
enable
configure terminal
hostname RTE-Stormshield
!
no access-list 1
no access-list 110
no access-list 120
no ip nat inside source list 1 interface GigabitEthernet0/1 overload
no ip nat inside source list 1 interface GigabitEthernet0/0 overload
no ip nat inside source list 1 interface GigabitEthernet0/0/0 overload
!
interface GigabitEthernet0/1
description ZONE IN - Transit LAN
ip address 192.168.44.254 255.255.255.248
ip nat inside
no shutdown
exit
!
interface GigabitEthernet0/2
description ZONE DMZ - Serveurs Publics
ip address 192.36.4.254 255.255.255.0
no ip nat inside
no shutdown
exit
!
interface GigabitEthernet0/0/0
description ZONE OUT - WAN FAI
ip address 192.36.253.40 255.255.255.0
ip nat outside
no shutdown
exit
!
interface GigabitEthernet0/0
no ip address
no ip nat inside
shutdown
exit
! Route de retour vers les LANs
ip route 192.168.4.0 255.255.255.0 192.168.44.252
! Route par défaut vers le FAI
ip route 0.0.0.0 0.0.0.0 192.36.253.254
!
access-list 1 remark PAT - LAN vers Internet
access-list 1 permit 192.168.4.0 0.0.0.255
access-list 1 permit host 192.168.44.252
!
ip nat inside source list 1 interface GigabitEthernet0/0/0 overload
!
end
write
```

5. Routeur du Siège (RTE-Siege)

```
enable
configure terminal
hostname RTE-Siege
!
interface GigabitEthernet0/0
description Liaison RTE-Siege vers Internet
ip address 172.16.29.199 255.255.252.0
ip nat outside
no shutdown
exit
!
interface GigabitEthernet0/0/0
description Liaison WAN vers Agence Dortmund
ip address 192.36.253.254 255.255.255.0
no shutdown
exit
!
ip route 192.36.4.0 255.255.255.0 192.36.253.40
end
write
```

