from classes import ezfunctionsv2 as ezfunctions
from classes import validatingv2 as validating
from copy import deepcopy
from dotmap import DotMap
import datetime
import ipaddress
import os
import pytz
import re
import time

class nxos(object):
    def __init__(self, type):
        self.type = type

    #=====================================================
    # NX-OS Configuration Setup
    #=====================================================
    def config(self, network_config, sw_type, kwargs):
        #=====================================================
        # Send Start Notification
        #=====================================================
        validating.begin_section(self.type, sw_type)
        time.sleep(2)

        #=====================================================
        # Global Commands
        #=====================================================
        base_commands = base_configuration(kwargs)

        #=====================================================
        # Timezone and NTP Configuration
        #=====================================================
        base_commands.extend(timezone_conversion(kwargs))
        for ntp in  kwargs.ntp_servers:
            base_commands.append(f"ntp server {ntp} use-vrf management")
        
        #=====================================================
        # Add Management Default Route
        #=====================================================
        base_commands.extend([
            f"vrf context management",
            f"  ip route 0.0.0.0/0 {kwargs.ooband.gateway}",
            f"  exit"
        ])
        
        #=====================================================
        # Create Nexus Switch Map
        #=====================================================
        nxmap = []
        for switch in network_config.switches:
            if switch.switch_type == sw_type:
                i  = DotMap(
                    breakout_speed= switch.breakout_speed,
                    hostname      = switch.hostname,
                    sw_type       = switch.switch_type
                )
                if switch.get('vpc_config'):
                    if len(str(switch.vpc_config.domain_id)) > 0:
                        i.vpc = DotMap(
                            domain_id      = switch.vpc_config.domain_id,
                            keepalive_ip   = switch.vpc_config.keepalive_ip,
                            keepalive_ports= switch.vpc_config.keepalive_ports,
                            peer_ports     = switch.vpc_config.peer_ports,
                        )
                nxmap.append(i)

        #=====================================================
        # Loop Through the Switch Configurations
        #=====================================================
        for x in range(0,len(nxmap)):
            cmds = []
            if sw_type == 'network':
                cmds = deepcopy(base_commands)

            #================================
            # Append VPC Configuration
            #================================
            if nxmap[x].get('vpc'):
                cmds.extend(vpc_config(x, nxmap, kwargs))

            #================================
            # Append VLAN Configuration
            #================================
            if sw_type == 'network':
                cmds.extend(vlan_config(x, nxmap, kwargs))

            #================================
            # Configure Interfaces
            #================================
            if kwargs.deployment_type == 'azure_hci':
                cmds.extend(add_interfaces_standalone(x, nxmap, kwargs))
            else:
                cmds.extend(add_interfaces(x, nxmap, kwargs))
            cmds.append('end')

            #================================
            # Login to the Switch
            #================================
            kwargs.hostname   = nxmap[x].hostname + '.' + kwargs.dns_domains[0]
            kwargs.host_prompt= r'[\w\-]{3,64}(\([\w\-]+\))?#'
            kwargs.password   = 'nexus_password'
            kwargs.username   = network_config.username
            child, kwargs     = ezfunctions.child_login(kwargs)

            #=====================================================
            # Send Configuration to Switch
            #=====================================================
            prLightPurple(f'\n\n!!! Starting Configuration on {kwargs.hostname} !!!\n\n')
            time.sleep(2)
            for cmd in cmds:
                child.sendline(cmd)
                child.expect(kwargs.host_prompt)
            child.sendline('copy run start')
            child.expect('Copy complete')
            child.expect(kwargs.host_prompt)
            child.sendline('exit')
            child.expect('closed')
            child.close()
            prLightPurple(f'\n\n!!! Completed Configuration on {kwargs.hostname} !!!\n\n')

        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'nxos')
        return kwargs


#=====================================================
# Add Interface Configuration to Switch Commands
#=====================================================
def add_interfaces(x, nxmap, kwargs):
    #================================
    # Allowed VLAN Lists
    #================================
    domain_vlans = ezfunctions.vlan_list_format(kwargs.nxos.imm.allowed_vlans)
    storage_vlans= ezfunctions.vlan_list_format(kwargs.nxos.storage.allowed_vlans)
    cmds = ["!"]
    #================================
    # Loop Thru Interfaces
    #================================
    net_list = ['imm', 'storage']
    for item in net_list:
        for k, v in kwargs.network[item].items():
            if nxmap[x].sw_type == 'ooband':
                if item == 'storage': descr = f"{k}-e0M"
                elif   item == 'imm': descr = f"{k}-mgmt0"
                #==================================
                # Add Mgmt Ports for Mgmt Switches
                #==================================
                cmds.extend([
                    f"interface {v.mgmt_port}",
                    f"  description {descr}",
                    f"  switchport",
                    f"  switchport host",
                    f"  switchport access vlan {kwargs.ooband.vlan_id}",
                ])
            #===============================================
            # Configure Network Ports and VPC Port-Channels
            #===============================================
            elif nxmap[x].sw_type == 'network':
                p1 = v.network_port.split('/')
                if len(p1) == 3:
                    vpc = '1' + p1[1] + p1[2]
                    breakout_check = True
                    for cmd in cmds:
                        if f'breakout module 1 port {p1[1]}' in cmd: breakout_check = False
                    if breakout_check == False:
                        speed = nxmap[x].breakout_speed
                        cmds.append(f"interface breakout module 1 port {p1[1]} map {speed}-4x")
                        cmds.append('!')
                else: vpc = p1[-1]
                #=================================
                # Add Port Configuration Commands
                #=================================
                if item == 'storage': allowed_vlans = storage_vlans
                else: allowed_vlans = domain_vlans
                if item == 'imm':
                    dsplit = v.data_ports[x].split('/')
                    if len(dsplit) == 3: pc_id = '1' + dsplit[1] + dsplit[2]
                    else: pc_id = dsplit[-1]
                    vpc_descr = k + '-' + f'PC{pc_id}'
                else: vpc_descr = k + '-a0a'
                cmds.extend([
                    f"interface {v.network_port}",
                    f"  description {k}-{v.data_ports[x]}",
                    f"  no shutdown",
                    f"  switchport",
                    f"  channel-group {vpc} mode active",
                    f"!",
                ])
                if v.port_channel == True:
                    cmds.extend([
                        f"interface port-channel {vpc}",
                        f"  description {vpc_descr}",
                        f"  no shutdown",
                        f"  mtu 9216",
                        f"  switchport",
                        f"  spanning-tree port type edge trunk",
                        f"  switchport mode trunk",
                        f"  switchport trunk allowed vlan {allowed_vlans}",
                        f"  vpc {vpc}",
                        f"!",
                    ])
    #=====================================================
    # Return Commands
    #=====================================================
    return cmds

#=====================================================
# Add Standalone Interfaces to Switch Commands
#=====================================================
def add_interfaces_standalone(x, nxmap, kwargs):
    #================================
    # Allowed VLAN Lists
    #================================
    imm_vlans = ezfunctions.vlan_list_format(kwargs.nxos.imm.allowed_vlans)
    native_vlan = kwargs.nxos.imm.native_vlan
    cmds = ["!"]
    #================================
    # Loop Thru Interfaces
    #================================
    for k, v in kwargs.network.imm.items():
        if nxmap[x].sw_type == 'ooband':
            descr = f"{k}-cimc"
            #==================================
            # Add Mgmt Ports for Mgmt Switches
            #==================================
            cmds.extend([
                f"interface {v.mgmt_port}",
                f"  description {descr}",
                f"  switchport",
                f"  switchport host",
                f"  switchport access vlan {kwargs.ooband.vlan_id}",
            ])
        #===============================================
        # Configure Network Ports and VPC Port-Channels
        #===============================================
        elif nxmap[x].sw_type == 'network':
            p1 = v.network_port.split('/')
            if len(p1) == 3:
                breakout_check = True
                for cmd in cmds:
                    if f'breakout module 1 port {p1[1]}' in cmd: breakout_check = False
                if breakout_check == False:
                    speed = nxmap[x].breakout_speed
                    cmds.append(f"interface breakout module 1 port {p1[1]} map {speed}-4x")
                    cmds.append('!')
            #=================================
            # Add Port Configuration Commands
            #=================================
            allowed_vlans = imm_vlans
            cmds.extend([
                f"interface {v.network_port}",
                f"  description {k}-{v.data_ports[x]}",
                f"  mtu 9216",
                f"  switchport",
                f"  switchport host",
                f"  switchport mode trunk",
                f"  switchport trunk native vlan {native_vlan}",
                f"  switchport trunk allowed vlan {allowed_vlans}",
                f"  priority-flow-control mode on",
                f"  no shutdown",
                f"!",
            ])
            if kwargs.deployment_type == 'azure_hci':
                cmds.extend([
                    f"  service-policy type qos input AzS_HCI_QoS",
                    f"  service-policy type queueing output QoS_Egress_Port",
                ])

    #=====================================================
    # Return Commands
    #=====================================================
    return cmds

#=====================================================
# Base Configuration - features and global cmds
#=====================================================
def base_configuration(kwargs):
    cmds = [
        f"configure terminal",
        f"cfs eth distribute",
        f"feature interface-vlan",
        f"feature hsrp",
        f"feature lacp",
        f"feature lldp",
        f"feature nxapi",
        f"feature udld",
        f"feature vpc",
        f"spanning-tree port type network default",
        f"spanning-tree port type edge bpduguard default",
        f"spanning-tree port type edge bpdufilter default",
        f"port-channel load-balance src-dst l4port",
        f"ip name-server {' '.join(kwargs.dns_servers)}",
        f"ip domain-name {kwargs.dns_domains[0]}",
        f"ip domain-lookup",
        f"ntp master 3",
    ]
    if kwargs.deployment_type == 'azure_hci':
        cmds.extend([
            "feature bgp",
            "feature dhcp"
        ])
    return cmds

#=====================================================
# BGP Configuration
#=====================================================
def bgp_configuration(x, nxmap, kwargs):
    as_number = kwargs.network.bgp.as_number
    remote_as = kwargs.network.bgp.remote_as
    router_id = kwargs.network
    cmds = [
        f"router bgp {as_number}",
        f"  router-id {router_id}",
        f"  bestpath as-path multipath-relax",
        f"  log-neighbor-changes",
        f"  address-family ipv4 unicast",
        f"    network 192.168.101.0/24",
        f"    network 192.168.126.0/26",
        f"    network 192.168.200.41/32",
        f"    network 192.168.200.44/30",
        f"    network 192.168.200.56/30",
        f"    network 192.168.200.60/30",
        f"    maximum-paths 8",
        f"    maximum-paths ibgp 8",
        f"  template peer eBGP-{remote_as}",
        f"    remote-as {remote_as}",
        f"    address-family ipv4 unicast",
        f"      maximum-prefix 12000 warning-only",
        f"      prefix-list ExternalPrefix in",
        f"      prefix-list ExternalPrefix out",
        f"  template peer iBGP",
        f"    remote-as {as_number}",
        f"    address-family ipv4 unicast",
        f"      maximum-prefix 12000 warning-only",
        f"  neighbor 192.168.200.46",
        f"    inherit peer iBGP",
        f"  neighbor 192.168.200.50",
        f"    inherit peer eBGP-{remote_as}",
        f"  neighbor 192.168.200.54",
        f"    inherit peer eBGP-{remote_as}",
        f"  neighbor 192.168.101.0/24",
        f"    inherit peer iBGP",
        f"  neighbor 192.168.126.0/26",
        f"    inherit peer iBGP",
    ]
    return cmds

#=====================================================
# Print Color Functions
#=====================================================
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk))
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))

#=====================================================
# QoS Configuration
#=====================================================
def qos_configuration():
    cmds = [
        f"class-map type network-qos RDMA_NetQoS",
        f"  match qos-group 4",
        f"!",
        f"class-map type network-qos ClusterCommunication_NetQoS",
        f"  match qos-group 5",
        f"!",
        f"policy-map type network-qos QoS_Network",
        f"  class type network-qos RDMA_NetQoS",
        f"    pause pfc-cos 4",
        f"    mtu 9216",
        f"  class type network-qos ClusterCommunication_NetQoS",
        f"    mtu 9216",
        f"  class type network-qos class-default",
        f"    mtu 9216",
        f"!",
        f"class-map type qos match-all RDMA",
        f"  match cos 4",
        f"class-map type qos match-all ClusterCommunication",
        f"  match cos 5",
        f"!",
        f"policy-map type qos AzS_HCI_QoS",
        f"  class RDMA",
        f"    set qos-group 4",
        f"  class ClusterCommunication",
        f"    set qos-group 5",
        f"!",
        f"policy-map type queuing QoS_Egress_Port",
        f"  class type queuing c-out-8q-q-default",
        f"    bandwidth remaining percent 49",
        f"  class type queuing c-out-8q-q1",
        f"    bandwidth remaining percent 0",
        f"  class type queuing c-out-8q-q2",
        f"    bandwidth remaining percent 0",
        f"  class type queuing c-out-8q-q3",
        f"    bandwidth remaining percent 0",
        f"  class type queuing c-out-8q-q4",
        f"    bandwidth remaining percent 50",
        f"    random-detect minimum-threshold 300 kbytes maximum-threshold 300 kbytes drop-probability 100 weight 0 ecn",
        f"!",
        f"  class type queuing c-out-8q-q5",
        f"    bandwidth percent 1",
        f"  class type queuing c-out-8q-q6",
        f"    bandwidth remaining percent 0",
        f"  class type queuing c-out-8q-q7",
        f"    bandwidth remaining percent 0",
        f"!",
        f"system qos",
        f"  service-policy type queuing output QoS_Egress_Port",
        f"  service-policy type network-qos QoS_Network",
    ]
    return cmds

#======================================================
# Function - Convert Timezone to NX-OS Commands
#======================================================
def timezone_conversion(kwargs):
    cmds  = []
    tzDict= kwargs.ez_data['wizard.nxos'].allOf[1].properties
    tz    = kwargs.timezone
    time_offset = pytz.timezone(tz).localize(datetime.datetime(2023,1,25)).strftime('%z')
    tzr = tz.split('/')[0]
    timezone_countries = {timezone: country 
        for country, timezones in pytz.country_timezones.items()
        for timezone in timezones
    }
    country = timezone_countries[tz]
    if tzr == 'Etc': cmds.append('clock timezone GMT 0 0')
    elif tzr == 'America':
        if country in tzDict.NorthAmerica.enum:
            cmds.append(tzDict.timezone_map.NorthAmerica[time_offset].standard)
            cmds.append(tzDict.timezone_map.NorthAmerica[time_offset].daylight)
        elif country in tzDict.SouthAmerica.enum:
            cmds.append(tzDict.timezone_map.SouthAmerica[time_offset].standard)
            cmds.append(tzDict.timezone_map.SouthAmerica[time_offset].daylight)
        else:
            cmds.append(tzDict.timezone_map.CentralAmerica[time_offset].standard)
            cmds.append(tzDict.timezone_map.CentralAmerica[time_offset].daylight)
    elif tzDict[tzr].get(country):
        cmds.append(tzDict.timezone_map[tzr][country].standard)
        cmds.append(tzDict.timezone_map[tzr][country].daylight)
    else:
        cmds.append(tzDict.timezone_map[tzr][time_offset].standard)
        cmds.append(tzDict.timezone_map[tzr][time_offset].daylight)
    return cmds

#=====================================================
# Add VLAN Configuration to Switch Commands
#=====================================================
def vlan_config(x, nxmap, kwargs):
    kwargs.nxos.imm    = DotMap()
    kwargs.nxos.storage= DotMap()
    cmds          = ["!"]
    #=====================================================
    # Add Ranges to Network Switches
    #=====================================================
    kwargs.nxos.imm.allowed_vlans = []
    for i in kwargs.ranges:
        vlan_range = ezfunctions.vlan_list_full(i.vlan_list)
        if nxmap[x].sw_type == 'network':
            kwargs.nxos.imm.allowed_vlans.extend(vlan_range)
        if i.configure_l2 == True and nxmap[x].sw_type == 'network':
            for v in vlan_range:
                if   re.search(r'^[\d]{4}$', str(v)): vname = f"{i.name}-vl{v}"
                elif re.search(r'^[\d]{3}$', str(v)): vname = f"{i.name}-vl0{v}"
                elif re.search(r'^[\d]{2}$', str(v)): vname = f"{i.name}-vl00{v}"
                elif    re.search(r'^[\d]$', str(v)): vname = f"{i.name}-vl000{v}"
                cmds.extend([
                    f"vlan {v}",
                    f"  name {vname}",
                    f"!"
                ])

    #=====================================================
    # Add VLANs to the Appropriate Switch Types
    #=====================================================
    kwargs.nxos.storage.allowed_vlans= []
    for i in kwargs.vlans:
        if re.search('(inband|iscsi|migration|nvme|nfs|storage|tenant|transit)', i.vlan_type) and nxmap[x].sw_type == 'network':
            kwargs.nxos.imm.allowed_vlans.append(i.vlan_id)
            kwargs.nxos.storage.allowed_vlans.append(i.vlan_id)
            if i.native_vlan == True: kwargs.nxos.imm.native_vlan = i.vlan_id
        ip_network  = ipaddress.IPv4Network(i.network)
        ip_broadcast= ip_network.broadcast_address
        ip_gateway  = ipaddress.IPv4Address(i.gateway)
        if not 'transit' in i.vlan_type:
            if int(ip_broadcast) - int(ip_gateway) > 1:
                vlan_ip = ipaddress.IPv4Address(int(ip_gateway) +1 + x)
            else: vlan_ip = ipaddress.IPv4Address(int(ip_gateway) -2 + x)
        if i.switch_type == nxmap[x].sw_type and i.configure_l2 == True:
            cmds.extend([
                f"vlan {i.vlan_id}",
                f"  name {i.name}",
                f"!"
            ])
            if i.configure_l3 == True:
                if x == 0 and int(i.vlan_id) % 2 != 0: p = 40
                elif x == 1 and int(i.vlan_id) % 2 == 0: p = 40
                else: p = 20
                if 'transit' in i.vlan_type:
                    cmds.extend([
                        f'interface Vlan{i.vlan_id}',
                        f'  description {i.name}',
                        f'  no shutdown',
                        f'  mtu 9216',
                        f'  no ip redirects',
                        f'  ip address {i.gateway}/{i.prefix}',
                        f'  no ipv6 redirects',
                        f'!'
                    ])
                else:
                    cmds.extend([
                        f'interface Vlan{i.vlan_id}',
                        f'  description {i.name}',
                        f'  no shutdown',
                        f'  mtu 9216',
                        f'  no ip redirects',
                        f'  ip address {vlan_ip}/{i.prefix}',
                        f'  no ipv6 redirects',
                        f'  hsrp version 2',
                        f'  hsrp {i.vlan_id}',
                        f'    preempt delay minimum 30 reload 120',
                        f'    priority 1{p} forwarding-threshold lower 1 upper 1{p}',
                        f'    timers msec 250 msec 1000',
                        f'    ip {i.gateway}',
                    ])
                    for d in kwargs.dhcp_servers:
                        cmds.append(f'  ip dhcp relay address {d}')
                    cmds.append(f'!')
    #================================
    # Return cmds
    #================================
    return cmds

#=====================================================
# Add VPC Settings
#=====================================================
def vpc_config(x, nxmap, kwargs):
    #================================
    # Configure Global VPC Settings
    #================================
    cmds = [
        f"vpc domain {nxmap[x].vpc.domain_id}",
        f"  auto-recovery",
        f"  delay restore 150",
        f"  ip arp synchronize",
        f"  layer3 peer-router",
        f"  peer-gateway",
        f"  peer-switch",
        f"  role priority { x+1 }",
    ]
    if x == 0: a = 1; b = 0
    else: a = 0; b = 1

    #================================
    # Add Keepalive Peers
    #================================
    if nxmap[x].vpc.keepalive_ports[0] == 'mgmt0':
        cmd = f"  peer-keepalive destination {nxmap[a].vpc.keepalive_ip.split('/')[0]} source "\
            f"{nxmap[b].vpc.keepalive_ip.split('/')[0]}"
        cmds.append(cmd)
    else:
        cmd = f"  peer-keepalive destination {nxmap[a].vpc.keepalive_ip.split('/')[0]} source "\
            f"{nxmap[b].vpc.keepalive_ip.split('/')[0]} vrf default"
        cmds.append(cmd)
    cmds.append('!')
    descr = nxmap[a].hostname

    #================================
    # Add Breakout Config if Used
    #================================
    def breakout_config(x, cmds, nxmap, port):
        breakout = port.split("/")[1]
        speed = nxmap[x].breakout_speed
        breakout_check = True
        for cmd in cmds:
            if f'breakout module 1 port {breakout}' in cmd: breakout_check = False
        if breakout_check == True:
            cmds.append(f"interface breakout module 1 port {breakout} map {speed.lower()}-4x")
            cmds.append('!')
        return cmds

    for port in nxmap[x].vpc.keepalive_ports:
        if len(port.split("/")) == 3: cmds = breakout_config(x, cmds, nxmap, port)
    for port in nxmap[x].vpc.peer_ports:
        if len(port.split("/")) == 3: cmds = breakout_config(x, cmds, nxmap, port)

    #=============================================
    # Configure VPC keepalive if not mgmt0
    #=============================================
    if not nxmap[x].vpc.keepalive_ports[0] == 'mgmt0':
        psplit = nxmap[x].vpc.keepalive_ports[0].split('/')
        if len(psplit) == 3:
            t, u, v = nxmap[x].vpc.keepalive_ports[0].split('/')
            pc_id = '1' + u + v
        else: pc_id = nxmap[x].vpc.keepalive_ports[0].split('/')[-1]
        for port in nxmap[x].vpc.keepalive_ports:
            cmds.extend([
                f"interface {port}",
                f"  description {descr}-{port} peer-port",
                f"  no switchport",
                f"  channel-group {pc_id} mode active",
                f"!",
            ])
        cmds.extend([
            f"interface port-channel{pc_id}",
            f"  description {descr} keepalive",
            f"  ip address {nxmap[x].vpc.keepalive_ip}",
            f"!",
        ])

    #================================
    # Configure VPC Peer-Links
    #================================
    psplit = nxmap[x].vpc.peer_ports[0].split('/')
    if len(psplit) == 3:
        t, u, v = nxmap[x].vpc.peer_ports[0].split('/')
        pc_id = '1' + u + v
    else: pc_id = nxmap[x].vpc.peer_ports[0].split('/')[-1]
    for port in nxmap[x].vpc.peer_ports:
        cmds.extend([
            f"interface {port}",
            f"  description {descr}-{port} peer-port",
            f"  switchport",
            f"  channel-group {pc_id} mode active",
            f"!",
        ])
    cmds.extend([
        f"interface port-channel{pc_id}",
        f"  description {descr} peer-link",
        f"  switchport",
        f"  switchport mode trunk",
        f"  vpc peer-link",
        f"!",
    ])
    if kwargs.deployment_type == 'azure_hci':
        cmds.append(f" service-policy type qos input AzS_HCI_QoS")

    #================================
    # Return cmds
    #================================
    return cmds
