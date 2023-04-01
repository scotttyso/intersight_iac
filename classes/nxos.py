#!/usr/bin/env python3

from copy import deepcopy
from dotmap import DotMap
import datetime
import ezfunctions
import ipaddress
import os
import pexpect
import pytz
import re
import sys
import time
import validating

class nxos(object):
    def __init__(self, type):
        self.type = type

    #=====================================================
    # NX-OS Configuration Setup
    #=====================================================
    def config(self, pargs, **kwargs):
        #=====================================================
        # Send Start Notification
        #=====================================================
        validating.begin_section(self.type, 'nxos')
        time.sleep(2)
        #=====================================================
        # Global Commands
        #=====================================================
        cmds = [
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
            f"ip name-server {' '.join(pargs.dns_servers)}",
            f"ip domain-name {pargs.dns_domains[0]}",
            f"ip domain-lookup",
            f"ntp master 3",
        ]
        for ntp in  pargs.ntp_servers:
            cmds.append(f"ntp server {ntp} use-vrf management")
        #=====================================================
        # Convert Timezone to NX-OS Commands
        #=====================================================
        tzDict = DotMap(deepcopy(kwargs['ezData']['wizard.nxos']['allOf'][1]['properties']))
        tz = deepcopy(pargs.timezone)
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
        cmds.extend([
            f"vrf context management",
            f"  ip route 0.0.0.0/0 {pargs.ooband.gateway}",
            f"  exit"
        ])
        #=====================================================
        # Add VLAN Configuration to Switch Commands
        #=====================================================
        def add_interfaces(x, smap, pargs, **kwargs):
            #================================
            # Allowed VLAN Lists
            #================================
            storage_vlans = ezfunctions.vlan_list_format(pargs.netapp.allowed_vlans)
            ucs_pc_vlans  = ezfunctions.vlan_list_format(pargs.ucs.allowed_vlans)
            cmds = ["!"]
            #================================
            # Loop Thru Interfaces
            #================================
            for i in kwargs['immDict']['wizard']['interfaces']:
                i = DotMap(deepcopy(i))
                if smap.type == 'ooband':
                    if i.device == 'domain' and x == 0: descr = f"{pargs.name}-A-mgmt0"
                    elif i.device == 'domain': descr = f"{pargs.name}-B-mgmt0"
                    elif i.device == 'controller' and x == 0: descr = f"{pargs.netapp.node01}-e0M"
                    elif i.device == 'controller': descr = f"{pargs.netapp.node02}-e0M"
                    #==================================
                    # Add Mgmt Ports for Mgmt Switches
                    #==================================
                    cmds.extend([
                        f"interface {i.mgmt}",
                        f"  description {descr}",
                        f"  switchport",
                        f"  switchport host",
                        f"  switchport access vlan {pargs.ooband.vlan_id}",
                    ])
                #===============================================
                # Configure Network Ports and VPC Port-Channels
                #===============================================
                elif smap.type == 'network':
                    ptype = ['fabric_a_ports', 'fabric_b_ports']
                    u1 = deepcopy(pargs.uplinks).split('/')
                    if len(u1) == 3: uprefix = u1[0] + '/' + u1[1]
                    else: uprefix = u1[0]
                    #================================
                    # Configure A/B Ports
                    #================================
                    for p in ptype:
                        p1 = i[p].split('/')
                        if len(p1) == 3:
                            pprefix = p1[0] + '/' + p1[1]
                            btrue = False
                            for y in cmds:
                                if 'breakout module 1' in y:
                                    if f'port {p1[1]}' in y: btrue = True
                            if btrue == False:
                                speed = deepcopy(pargs.breakout_speed.eth).lower()
                                cmds.append(f"interface breakout module 1 port {p1[1]} map {speed}-4x")
                                cmds.append('!')
                        else: pprefix = p1[0]
                        ports = i[p].split('/')[-1]
                        if '-' in i[p]:
                            pstart = ports.split('-')[0]
                            plast = ports.split('-')[1]
                            plist = []
                            for x in range(int(pstart),int(plast)+1):
                                plist.append(x)
                            pargs[p] = plist
                        else: pargs[p] = ports.split(',')
                    #================================
                    # Configure Global VPC Settings
                    #================================
                    a = deepcopy(pargs['fabric_a_ports'])
                    b = deepcopy(pargs['fabric_b_ports'])
                    swports = a + b
                    #================================
                    # Validate Port Counts Match
                    #================================
                    if i.device == 'controller':
                        if not len(swports) == len(pargs.netapp.data_ports):
                            print(f"\n!!! ERROR !!!\n The Ports are not the same.")
                            print(f"\n  * Controller Ports: {pargs.netapp.data_ports}")
                            print(f"\n  * Switch Ports: {pprefix}/{swports}")
                            print(f"Exiting...")
                            sys.exit(1)
                    if i.device == 'domain':
                        if not len(swports) == len(pargs.uplink_list):
                            print(f"\n!!! ERROR !!!\n The Ports are not the same.")
                            print(f"\n  * Domain Ports: {uprefix}/{pargs.uplink_list}")
                            print(f"\n  * Switch Ports: {pprefix}/{swports}")
                            print(f"Exiting...")
                            sys.exit(1)
                    #=================================
                    # Add Port Configuration Commands
                    #=================================
                    def port_config(ports, cmds, pargs):
                        for z in range(0,len(ports)):
                            if i.device == 'controller' and z % 2 == 0:
                                descr = f"{pargs.netapp.node01}-{pargs.netapp.data_ports[z]}"
                            elif i.device == 'controller':
                                descr = f"{pargs.netapp.node02}-{pargs.netapp.data_ports[z]}"
                            elif i.device == 'domain' and z % 2 == 0:
                                descr = f"{pargs.name}-A-{uprefix}/{pargs.uplinks[z]}"
                            elif i.device == 'domain': descr = f"{pargs.name}-B-{uprefix}/{pargs.uplinks[z]}"
                            if '/' in pprefix: vpc = '1' + pprefix.split('/')[-1] + ports[0]
                            else: vpc = ports[0]
                            if i.device == 'controller':
                                allowed_vlans = storage_vlans
                                pcdescr = f"{pargs.netapp.cluster}-vpc{vpc}"
                            else:
                                allowed_vlans = ucs_pc_vlans
                                pcdescr = f"{pargs.name}-vpc{vpc}"
                            cmds.extend([
                                f"interface {pprefix}/{ports[z]}",
                                f"  description {descr}",
                                f"  no shutdown",
                                f"  switchport",
                                f"  channel-group {vpc} mode active",
                                f"!",
                            ])
                        cmds.extend([
                            f"interface port-channel {vpc}",
                            f"  description {pcdescr}",
                            f"  no shutdown",
                            f"  mtu 9216",
                            f"  switchport",
                            f"  spanning-tree port type edge trunk",
                            f"  switchport mode trunk",
                            f"  switchport trunk allowed vlan {allowed_vlans}",
                            f"  vpc {vpc}",
                            f"!",
                        ])
                        return cmds
                    cmds = port_config(a, cmds, pargs)
                    cmds = port_config(b, cmds, pargs)
            #=====================================================
            # Return Commands
            #=====================================================
            return cmds
        #=====================================================
        # Add VLAN Configuration to Switch Commands
        #=====================================================
        def vlan_config(x, smap, pargs):
            cmds = ["!"]
            #=====================================================
            # Add Ranges to Network Switches
            #=====================================================
            for i in pargs.ranges:
                r = DotMap(deepcopy(i))
                vrange = ezfunctions.vlan_list_full(r.vlan_list)
                if smap.type == 'network': pargs.ucs.allowed_vlans.extend(vrange)
                if r.configure == 'True' and smap.type == 'network':
                    for v in vrange:
                        if   re.search(r'^[\d]{4}$', str(v)): vname = f"{r.name}-vl{v}"
                        elif re.search(r'^[\d]{3}$', str(v)): vname = f"{r.name}-vl0{v}"
                        elif re.search(r'^[\d]{2}$', str(v)): vname = f"{r.name}-vl00{v}"
                        elif    re.search(r'^[\d]$', str(v)): vname = f"{r.name}-vl000{v}"
                        cmds.extend([
                            f"vlan {v}",
                            f"  name {vname}",
                            f"!"
                        ])
            #=====================================================
            # Add VLANs to the Appropriate Switch Types
            #=====================================================
            for i in pargs.vlans:
                v = DotMap(deepcopy(i))
                if re.search('(inband|iscsi|nvme|nfs)', v.type) and smap.type == 'network':
                    pargs.ucs.allowed_vlans.append(v.vlan_id)
                    pargs.netapp.allowed_vlans.append(v.vlan_id)
                ipn = ipaddress.IPv4Network(v.network)
                ipnb = ipn.broadcast_address
                ipgw = ipaddress.IPv4Address(v.gateway)
                if int(ipnb) - int(ipgw) > 1:
                    vlan_ip = ipaddress.IPv4Address(int(ipgw) +1 + x)
                else: vlan_ip = ipaddress.IPv4Address(int(ipgw) -2 + x)
                if v.switch == smap.type and v.configure == 'True':
                    cmds.extend([
                        f"vlan {v.vlan_id}",
                        f"  name {v.name}",
                        f"!"
                    ])
                    if smap.configure_l3 == 'True':
                        if x == 0 and int(v.vlan_id) % 2 != 0: p = 40
                        elif x == 1 and int(v.vlan_id) % 2 == 0: p = 40
                        else: p = 20
                        cmds.extend([
                            f'interface Vlan{v.vlan_id}',
                            f'  description {v.name}',
                            f'  no shutdown',
                            f'  mtu 9216',
                            f'  no ip redirects',
                            f'  ip address {vlan_ip}/{v.prefix}',
                            f'  no ipv6 redirects',
                            f'  hsrp version 2',
                            f'  hsrp {v.vlan_id}',
                            f'    preempt delay minimum 30 reload 120',
                            f'    priority 1{p}',
                            f'    timers msec 250 msec 1000',
                            f'    ip {v.gateway}',
                            f"!"
                        ])
            return cmds
        #=====================================================
        # Add VPC Settings
        #=====================================================
        def vpc_config(x, nxdict, smap, pargs):
            #================================
            # Configure Global VPC Settings
            #================================
            cmds = [
                f"vpc domain {smap.vpc_domain_id}",
                f"  auto-recovery",
                f"  delay restore 150",
                f"  ip arp synchronize",
                f"  layer3 peer-router",
                f"  peer-gateway",
                f"  peer-switch",
                f"  role priority {x+1}",
            ]
            if x == 0:
                a = 1
                b = 0
            else:
                a = 0
                b = 1
            #================================
            # Add Keepalive Peers
            #================================
            if smap.vpc_keepalive_ports == 'mgmt0':
                cmd = f"  peer-keepalive destination {nxdict[smap.type][a]['keepalive_ip']} source "\
                    f"{nxdict[smap.type][b]['keepalive_ip']} use vrf-management"
                cmds.append(cmd)
            else:
                cmd = f"  peer-keepalive destination {nxdict[smap.type][a]['keepalive_ip']} source "\
                    f"{nxdict[smap.type][b]['keepalive_ip']}"
                cmds.append(cmd)
            cmds.append('!')
            ports = deepcopy(smap.vpc_peer_ports)
            descr = nxdict[smap.type][a]['descriptions']
            #================================
            # Add Breakout Config if Used
            #================================
            if len(ports.split("/")) == 3:
                breakout = ports.split("/")[1]
                speed = deepcopy(nxdict[smap.type][b]['breakout_speed'])
                if not f'breakout module 1 port {breakout}' in cmds:
                    cmds.append(f"interface breakout module 1 port {breakout} map {speed.lower()}-4x")
                    cmds.append('!')
            #================================
            # Configure VPC Peer-Links
            #================================
            if '-' in ports:
                z = (ports.split("/")[-1]).split("-")
                pc_id = z[0]
                last = z[1]
                for x in range(int(pc_id), int(last)+1):
                    cmds.extend([
                        f"interface eth1/{x}",
                        f"  description {descr}-eth1/{x} peer-port",
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
            elif ',' in ports:
                port_list = (ports.split("/")[-1]).split(",")
                pc_id = port_list[0]
                for x in port_list:
                    cmds.extend([
                        f"interface eth1/{x}",
                        f"  description {descr}-eth1/{x} peer-port",
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
            return cmds
        #=====================================================
        # Create Dictionaries
        #=====================================================
        nxdict = DotMap({'ooband': [], 'network': []})
        nDict  = deepcopy(kwargs['immDict']['wizard']['nxos'])
        for nx in nDict:
            nx = DotMap(nx)
            i  = {
                'configure_vpc': nx.configure_vpc,
                'configure_l3': nx.configure_l3,
                'descriptions': f'{nx.hostname}'.split('.')[0],
                'hostname':  nx.hostname,
                'type': nx.switch_type
            }
            if nx.configure_vpc == 'True':
                i.update({
                    'keepalive_ip':    nx.keepalive_ip,
                    'keepalive_ports': nx.keepalive_ports,
                    'vpc_domain_id':   nx.vpc_domain_id,
                    'vpc_peer_ports':  nx.vpc_peer_ports,
                })
            nxdict[nx.switch_type].append(i)
        #=====================================================
        # Setup Script Variables
        #=====================================================
        enablePrompt = r'^[\w\-]{3,64}>$'
        hostPrompt   = r'^[\w\-]+(\([\w\-]+\))?#$'
        hostPrompt   = r'[\w\-]{3,64}(\([\w\-]+\))?#'
        systemShell  = os.environ['SHELL']
        kwargs['Variable'] = 'nxos_password'
        kwargs   = ezfunctions.sensitive_var_value(**kwargs)
        password = kwargs['var_value']
        #=====================================================
        # Spawn the environment Shell
        #=====================================================
        child = pexpect.spawn(systemShell, encoding='utf-8')
        child.logfile_read = sys.stdout
        network_list = ['ooband','network']
        pargs.ucs = DotMap()
        #=====================================================
        # Loop Through the Device Configurations
        #=====================================================
        base_commands = cmds
        for net in network_list:
            for x in range(0,len(nxdict[net])):
                pargs.netapp.allowed_vlans = []
                pargs.ucs.allowed_vlans = []
                smap = DotMap(nxdict[net][x])
                cmds = []
                if smap.type == 'network':
                    cmds = deepcopy(base_commands)
                #================================
                # Append VPC Configuration
                #================================
                if smap.configure_vpc == 'True':
                    cmds.extend(vpc_config(x, nxdict, smap, pargs))
                #================================
                # Append VLAN Configuration
                #================================
                cmds.extend(vlan_config(x, smap, pargs))
                #================================
                # Configure Port-Channels as VPC
                #================================
                if smap.type == 'network':
                    cmds.extend(add_interfaces(x, smap, pargs, **kwargs))
                for cmd in cmds:
                    print(cmd)
                #================================
                # Open SSH Session
                #================================
                print(smap.hostname)
                child.sendline(f'ssh {pargs.nxosuser}@{smap.hostname} | tee {smap.hostname}.txt')
                child.expect(f'tee {smap.hostname}.txt')
                #================================
                # Login to the NX-OS Device
                #================================
                logged_in = False
                while logged_in == False:
                    i = child.expect(['Are you sure you want to continue', 'closed', 'Password:', enablePrompt, hostPrompt])
                    if i == 0: child.sendline('yes')
                    elif i == 1:
                        print(f'\n**failed to connect.  Please Validate {smap.hostname} is correct and '\
                              'username {pargs.nxosuser} is correct.')
                    elif i == 2: child.sendline(password)
                    elif i == 3:
                        child.sendline('enable')
                        child.expect('enable')
                    elif i == 4: logged_in = True
                host_file = open(f'{smap.hostname}.txt', 'r')
                #=====================================================
                # Send Configuration to Device
                #=====================================================
                print(f'\n\n!!! Starting Configuration on {smap.hostname} !!!\n\n')
                time.sleep(2)
                child.sendline('config t')
                child.expect(hostPrompt)
                for cmd in cmds:
                    child.sendline(cmd)
                    child.expect(hostPrompt)
                child.sendline('end')
                child.expect(hostPrompt)
                child.sendline('copy run start')
                child.expect('Copy complete')
                child.expect(hostPrompt)
                child.sendline('exit')
                child.expect('closed')
                host_file.close()
                os.remove(f'{smap.hostname}.txt')
        child.close()
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'nxos')
        return kwargs, pargs
