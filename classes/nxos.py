#!/usr/bin/env python3

from copy import deepcopy
from dotmap import DotMap
import datetime
import ezfunctions
import ipaddress
import json
import os
import pexpect
import pytz
import re
import sys
import time
import validating

timezone_countries = {timezone: country 
    for country, timezones in pytz.country_timezones.items()
    for timezone in timezones
}
class nxos(object):
    def __init__(self, type):
        self.type = type

    #=====================================================
    # NX-OS Configuration Setup
    #=====================================================
    def config(self, pargs, **kwargs):
        nDict = deepcopy(kwargs['immDict']['wizard']['nxos'])
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
            f"ntp server {pargs.ntp_servers[0]} use-vrf management",
        ]
        if len(pargs.ntp_servers) > 1:
            cmds.append(f"ntp server {pargs.ntp_servers[1]} use-vrf management")
        #=====================================================
        # Convert Timezone to NX-OS Commands
        #=====================================================
        tzDict = kwargs['ezData']['wizard.nxos']['allOf'][1]['properties']
        tz = '{}'.format(pargs.timezone)
        time_offset = pytz.timezone(tz).localize(datetime.datetime(2023,1,25)).strftime('%z')
        tzr = tz.split('/')[0]
        if tzr == 'America':
            country = timezone_countries[tz]
            if country in tzDict['NorthAmerica']['enum']:
                cmds.append(tzDict['timezone_map']['NorthAmerica'][time_offset]['standard'])
                cmds.append(tzDict['timezone_map']['NorthAmerica'][time_offset]['daylight'])
            elif country in tzDict['SouthAmerica']['enum']:
                cmds.append(tzDict['timezone_map']['SouthAmerica'][time_offset]['standard'])
                cmds.append(tzDict['timezone_map']['SouthAmerica'][time_offset]['daylight'])
            else:
                cmds.append(tzDict['timezone_map']['CentralAmerica'][time_offset]['standard'])
                cmds.append(tzDict['timezone_map']['CentralAmerica'][time_offset]['daylight'])
        elif tzr == 'Etc': cmds.append('clock timezone GMT 0')
        else:
            cmds.append(tzDict['timezone_map'][tzr][time_offset]['standard'])
            cmds.append(tzDict['timezone_map'][tzr][time_offset]['daylight'])
        cmds.extend([
            f"vrf context management",
            f"  ip route 0.0.0.0/0 {pargs.ooband.gateway}",
            f"  exit"
        ])
        #=====================================================
        # Add VLAN Configuration to Switch Commands
        #=====================================================
        def vlan_config(x, smap, pargs):
            vcmds = ["!"]
            #=====================================================
            # Add Ranges to Network Switches
            #=====================================================
            for i in pargs.ranges:
                r = DotMap(deepcopy(i))
                if r.configure == 'True' and smap.type == 'network':
                    vrange = ezfunctions.vlan_list_full(r.vlan_list)
                    for v in vrange:
                        if   re.search(r'^[\d]{4}$', str(v)): vname = f"{r.name}-vl{v}"
                        elif re.search(r'^[\d]{3}$', str(v)): vname = f"{r.name}-vl0{v}"
                        elif re.search(r'^[\d]{2}$', str(v)): vname = f"{r.name}-vl00{v}"
                        elif    re.search(r'^[\d]$', str(v)): vname = f"{r.name}-vl000{v}"
                        vcmds.extend([
                            f"vlan {v}",
                            f"  name {vname}",
                            f"!"
                        ])
            #=====================================================
            # Add VLANs to the Appropriate Switch Types
            #=====================================================
            for i in pargs.vlans:
                v = DotMap(deepcopy(i))
                if re.search('(inband|iscsi|nvme|nfs)', v.type):
                    pargs.ucs.allowed_vlans.append(v.vlan_id)
                    pargs.netapp.allowed_vlans.append(v.vlan_id)
                ipn = ipaddress.IPv4Network(v.network)
                ipnb = ipn.broadcast_address
                ipgw = ipaddress.IPv4Address(v.gateway)
                if int(ipnb) - int(ipgw) > 1:
                    vlan_ip = ipaddress.IPv4Address(int(ipgw) +1 + x)
                else: vlan_ip = ipaddress.IPv4Address(int(ipgw) -2 + x)
                if v.switch == smap.type and v.configure == 'True':
                    vcmds.extend([
                        f"vlan {v.vlan_id}",
                        f"  name {v.name}",
                        f"!"
                    ])
                    if v.config_l3 == 'True':
                        if x == 0: p = 20
                        else: p = 40
                        vcmds.extend([
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
            return vcmds
        def vpc_config(x, smap, pargs):
            cmds = [
                f"vpc domain {smap.vpc_domain_id}"
            ]
        #=====================================================
        # Setup Script Variables
        #=====================================================
        enablePrompt = r'^[\w]>$'
        hostPrompt   = r'^[\w](\(\w)\)?#$'
        host         = pargs.host
        systemShell  = os.environ['SHELL']
        kwargs['Variable'] = 'nxos_password'
        kwargs   = ezfunctions.sensitive_var_value(**kwargs)
        password = kwargs['var_value']
        nxdict = DotMap({'ooband': [], 'network': []})
        #=====================================================
        # Create Network Type Dictionary
        #=====================================================
        for nx in nDict:
            nx = DotMap(nx)
            i  = {
                'configure': nx.configure_vpc,
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
        # Spawn the environment Shell
        #=====================================================
        child = pexpect.spawn(systemShell, encoding='utf-8')
        child.logfile_read = sys.stdout
        network_list = ['ooband','network']
        pargs.netapp.allowed_vlans = []
        pargs.ucs = DotMap()
        pargs.ucs.allowed_vlans = []
        for net in network_list:
            for x in range(0,len(nxdict[net])):
                smap = DotMap(nxdict[net][x])
                cmds.extend(vlan_config(x, smap, pargs))
                if smap.configure_vpc == 'True':
                    cmds.extend(vpc_config(x, smap, pargs))
                print(f'\n!!! {smap.hostname} !!!\n')
                for cmd in cmds:
                    print(cmd)
        exit()
        for nx in nDict:
            nx = DotMap(nx)
            hostname = nx.hostname
            username = pargs.nxosuser
            kwargs['Variable'] = 'nxos_password'
            kwargs   = ezfunctions.sensitive_var_value(**kwargs)
            password = kwargs['var_value']

            child.sendline(f'ssh {pargs.netapp.user}@{host} | tee {host}.txt')
            child.expect(f'tee {host}.txt')
            
            logged_in = False
            while logged_in == False:
                i = child.expect(['Are you sure you want to continue', 'closed', 'Password:', hostPrompt])
                if i == 0: child.sendline('yes')
                elif i == 1:
                    print(f'\n**failed to connect.  Please Validate {host} is correct and username {pargs.netapp.user} is correct.')
                elif i == 2: child.sendline(pargs.netapp.password)
                elif i == 3: logged_in = True
            host_file = open(f'{host}.txt', 'r')
            pargs.host_file = host_file
            #=====================================================
            # Validate storage Failover
            #=====================================================
            cmds = ['storage failover modify -node * -enabled true', 'storage failover show']
            for x in range(0,len(cmds)):
                child.sendline(cmds[x])
                child.expect(hostPrompt)
                if x == 0: time.sleep(10)
            for line in host_file:
                if 'false' in line:
                    print(f'\n**failed on "{cmds[1]}".  Please Validate the cluster cabling and restart this wizard.')
                    sys.exit(1)
            #=====================================================
            # Validate Cluster High Availability
            #=====================================================
            cmds = ['cluster ha modify -configured true', 'cluster ha show']
            for x in range(0,len(cmds)):
                child.sendline(cmds[x])
                child_proc = False
                while child_proc == False:
                    i = child.expect(['Do you want to continue', hostPrompt])
                    if i == 0: child.sendline('y')
                    elif i == 1: child_proc = True
                if x == 0: time.sleep(10)
            for line in host_file:
                if 'false' in line:
                    print(f'\n**failed on "{cmd[1]}".  Please Validate the cluster cabling and restart the wizard.')
                    sys.exit(1)
            #=====================================================
            # Validate Storage Failover Hardware Assist
            #=====================================================
            controller_ips = pargs.ooband['controller']
            cmds = [
                f"storage failover modify -hwassist-partner-ip {controller_ips[2]} -node {pargs.netapp.node01}",
                f"storage failover modify -hwassist-partner-ip {controller_ips[1]} -node {pargs.netapp.node02}",
                'storage failover hwassist show'
            ]
            for cmd in cmds:
                child.sendline(cmd)
                child.expect(hostPrompt)
                if x == 1: time.sleep(10)
            hwassist = 0
            for line in host_file:
                if re.search('Monitor Status: active', line): hwassist += 1
            if not hwassist == 2:
                print(f'\n**failed on "{cmd[3]}".  Please Validate the cluster cabling and restart the wizard.')
                sys.exit(1)
            #=====================================================
            # Change Fibre-Channel Port Speeds
            #=====================================================
            for node in pargs.netapp.node_list:
                for fca in pargs.netapp.fcp_ports:
                    cmd = f'fcp adapter modify -node {node} -adapter {fca} -status-admin down'
                    child.sendline(cmd)
                    child.expect(hostPrompt)
            time.sleep(3)
            for node in pargs.netapp.node_list:
                for fca in pargs.netapp.fcp_ports:
                    cmd = f'fcp adapter modify -node {node} -adapter {fca} -speed {pargs.netapp.fcp_speed} -status-admin up'
                    child.sendline(cmd)
                    child.expect(hostPrompt)
                    time.sleep(2)
            #=====================================================
            # Disk Zero Spares
            #=====================================================
            cmd = 'disk zerospares'
            child.sendline(cmd)
            child.expect(hostPrompt)
            cmd = 'disk show -fields zeroing-percent'
            child.sendline(cmd)
            dcount = 0
            zerospares = False
            while zerospares == False:
                i = child.expect([r'\d.\d.[\d]+ [\d]', 'to page down', hostPrompt])
                if i == 0:
                    if dcount == 10: print(f'\n**failed on "{cmd}".  Please Check for any issues and restart the wizard.')
                    time.sleep(60)
                    dcount =+ 1
                    child.sendline(cmd)
                elif i == 1: child.send(' ')
                elif i == 2: zerospares = True
            ipcount = 3
            #=====================================================
            # Enable CDP, LLDP, and SNMP
            #=====================================================
            cmds = [
                'node run -node * options cdpd.enable on',
                'node run -node * options lldp.enable on',
                'snmp init 1'
            ]
            #===========================================================
            # Configure Node Service Processors and disable FlowControl
            #===========================================================
            for node in pargs.netapp.node_list:
                gw  = pargs.ooband['gateway']
                cmds.append(f"system service-processor network modify -node {node} -address-family IPv4 -enable true -dhcp none "\
                    f"-ip-address {pargs.ooband['controller'][ipcount]} -netmask {pargs.ooband['netmask']} -gateway {gw}")
                cmds.append(f"network port modify -node {node} -port {','.join(pargs.netapp.data_ports)} -flowcontrol-admin none")
                ipcount += 1
            for cmd in cmds:
                child.sendline(cmd)
                child.expect(hostPrompt)
            host_file.close()
            os.remove(f'{host}.txt')
            child.close()
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


