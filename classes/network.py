from classes import ezfunctionsv2 as ezfunctions
from classes import validatingv2 as validating
from copy import deepcopy
from dotmap import DotMap
import datetime
import ipaddress
import os
import pexpect
import pytz
import re
import sys
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
                    i.vpc = DotMap(
                        domain_id      = switch.vpc_config.domain_id,
                        keepalive_ip   = switch.vpc_config.keepalive_ip,
                        keepalive_ports= switch.vpc_config.keepalive_ports,
                        peer_ports     = switch.vpc_config.peer_ports,
                    )
                nxmap.append(i)
        #=====================================================
        # Setup Base Variables
        #=====================================================
        enablePrompt= r'^[\w\-]{3,64}>$'
        hostPrompt  = r'^[\w\-]+(\([\w\-]+\))?#$'
        hostPrompt  = r'[\w\-]{3,64}(\([\w\-]+\))?#'
        sshQuestion = 'Are you sure you want to continue'
        systemShell = os.environ['SHELL']
        kwargs.sensitive_var= 'nexus_password'
        kwargs = ezfunctions.sensitive_var_value(kwargs)
        #=====================================================
        # Spawn the environment Shell
        #=====================================================
        child = pexpect.spawn(systemShell, encoding='utf-8')
        child.logfile_read = sys.stdout
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
                cmds.extend(vpc_config(x, nxmap))

            #================================
            # Append VLAN Configuration
            #================================
            if sw_type == 'network':
                cmds.extend(vlan_config(x, nxmap, kwargs))

            #================================
            # Configure Port-Channels as VPC
            #================================
            cmds.extend(add_interfaces(x, nxmap, kwargs))
            cmds.append('end')
            #================================
            # Open SSH Session
            #================================
            hostname= nxmap[x].hostname + '.' + kwargs.dns_domains[0]
            password= kwargs['var_value']
            username= network_config.username
            child.sendline(f'ssh {username}@{hostname}')
            child.expect(f'ssh {username}@{hostname}')
            
            #================================
            # Login to the NX-OS Device
            #================================
            logged_in = False
            while logged_in == False:
                i = child.expect([sshQuestion, 'closed', 'Password:', enablePrompt, hostPrompt])
                if i == 0: child.sendline('yes')
                elif i == 1:
                    prRed(f'\n!!!ERROR!!! failed to connect.')
                    prRed(f'Please Validate {hostname} and username {username} is correct.')
                    sys.exit()
                elif i == 2: child.sendline(password)
                elif i == 3:
                    child.sendline('enable')
                    child.expect('enable')
                elif i == 4: logged_in = True
            
            #=====================================================
            # Send Configuration to Switch
            #=====================================================
            prLightPurple(f'\n\n!!! Starting Configuration on {hostname} !!!\n\n')
            time.sleep(2)
            for cmd in cmds:
                child.sendline(cmd)
                child.expect(hostPrompt)
            child.sendline('copy run start')
            child.expect('Copy complete')
            child.expect(hostPrompt)
            child.sendline('exit')
            child.expect('closed')
            prLightPurple(f'\n\n!!! Completed Configuration on {hostname} !!!\n\n')
        child.close()

        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'nxos')
        return kwargs


#=====================================================
# Add VLAN Configuration to Switch Commands
#=====================================================
def add_interfaces(x, nxmap, kwargs):
    #================================
    # Allowed VLAN Lists
    #================================
    storage_vlans= ezfunctions.vlan_list_format(kwargs.nxos.storage.allowed_vlans)
    domain_vlans = ezfunctions.vlan_list_format(kwargs.nxos.imm.allowed_vlans)
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
                        speed = nxmap[x]['breakout_speed']
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
# Base Configuration - features and global cmds
#=====================================================
def base_configuration(kwargs):
    cmds = [
        f"configure terminal",
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
        if re.search('(inband|iscsi|nvme|nfs)', i.vlan_type) and nxmap[x].sw_type == 'network':
            kwargs.nxos.imm.allowed_vlans.append(i.vlan_id)
            kwargs.nxos.storage.allowed_vlans.append(i.vlan_id)
        ip_network  = ipaddress.IPv4Network(i.network)
        ip_broadcast= ip_network.broadcast_address
        ip_gateway  = ipaddress.IPv4Address(i.gateway)
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
                    f'    priority 1{p}',
                    f'    timers msec 250 msec 1000',
                    f'    ip {i.gateway}',
                    f"!"
                ])
    #================================
    # Return cmds
    #================================
    return cmds

#=====================================================
# Add VPC Settings
#=====================================================
def vpc_config(x, nxmap):
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
        speed = nxmap[x]['breakout_speed']
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

    #================================
    # Return cmds
    #================================
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
