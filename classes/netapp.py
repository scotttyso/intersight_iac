#!/usr/bin/env python3

from copy import deepcopy
from dotmap import DotMap
import ezfunctions
import json
import os
import pexpect
import re
import requests
import socket
import sys
import time
import urllib3
import validating
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global options for debugging
print_payload = False
print_response_always = True
print_response_on_fail = True

# Log levels 0 = None, 1 = Class only, 2 = Line
log_level = 2

# Exception Classes
class InsufficientArgs(Exception): pass
class ErrException(Exception): pass
class InvalidArg(Exception): pass
class LoginFailed(Exception): pass

# NetApp - Policies
# Class must be instantiated with Variables
class api(object):
    def __init__(self, type):
        self.type = type
    #=====================================================
    # NetApp AutoSupport Creation
    #=====================================================
    def autosupport(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section(self.type, 'netapp')
        apiBody = json.dumps(pargs.apiBody)
        if print_payload: print(json.dumps(pargs.apiBody, indent=4))
        uri = 'support/autosupport'
        patch(uri, pargs, apiBody, **kwargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


    #=====================================================
    # NetApp Broadcast Domain Creation
    #=====================================================
    def broadcast_domain(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section(self.type, 'netapp')
        #=====================================================
        # Create/Patch the Broadcast Domains
        #=====================================================
        uri = '/network/ethernet/broadcast-domains'
        bDomains = get(uri, pargs, **kwargs)
        pargs.netapp.broadcast_domains = {}
        for i in pargs.item:
            polVars = deepcopy(i)
            i = DotMap(deepcopy(i))
            method = 'post'
            for r in bDomains['records']:
                r = DotMap(deepcopy(r))
                if i.name == r.name:
                    method = 'patch'
                    uri = f'network/ethernet/broadcast-domains/{r["uuid"]}'
                    polVars.pop('name')
            if method == 'post': uri = 'network/ethernet/broadcast-domains'
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            print(f"\n    Configuring Broadcast Domain {i.name}")
            eval(f"{method}(uri, pargs, payload, **kwargs)")
        uri = '/network/ethernet/broadcast-domains'
        bDomains = get(uri, pargs, **kwargs)
        for i in pargs.item:
            i = DotMap(deepcopy(i))
            for r in bDomains['records']:
                r = DotMap(deepcopy(r))
                if i.name == r.name or 'Default' in r.name:
                    pargs.netapp.broadcast_domains.update({r.name:r.uuid})
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


    #=====================================================
    # NetApp Cluster Initialization
    #=====================================================
    def cluster_init(self, pargs, **kwargs):
        #=====================================================
        # Send Begin Notification
        #=====================================================
        validating.begin_section(self.type, 'netapp')
        time.sleep(2)
        #=====================================================
        # Load Variables and Login to Storage Array
        #=====================================================
        pargs.hostname     = pargs.netapp.node01
        pargs.hostPassword = 'netapp_password'
        pargs.hostPrompt   = deepcopy(pargs.netapp.hostPrompt)
        pargs.username     = pargs.netapp.user
        child, kwargs      = child_login(pargs, **kwargs)
        #=====================================================
        # Enable CDP, LLDP, and SNMP
        #=====================================================
        cmds = [
            'node run -node * options cdpd.enable on',
            'node run -node * options lldp.enable on',
            'snmp init 1'
        ]
        for cmd in cmds:
            child.sendline(cmd)
            child.expect(pargs.hostPrompt)
        #=====================================================
        # Storage Failover Check
        #=====================================================
        pargs.count = 2
        pargs.show  = "storage failover show"
        pargs.regex = "true[ ]+Connected to"
        pargs.cmds  = ["storage failover modify -node * -enabled true"]
        config_function(child, pargs)
        #=====================================================
        # Validate Cluster High Availability
        #=====================================================
        pargs.count = 1
        pargs.show  = "cluster ha show"
        pargs.regex = "High-Availability Configured: true"
        pargs.cmds  = ['cluster ha modify -configured true']
        config_function(child, pargs)
        #=====================================================
        # Validate Storage Failover Hardware Assist
        #=====================================================
        controller_ips = pargs.ooband['controller']
        pargs.count = 2
        pargs.show  = "storage failover hwassist show"
        pargs.regex = "Monitor Status: active"
        pargs.cmds = [
            f"storage failover modify -hwassist-partner-ip {controller_ips[2]} -node {pargs.netapp.node01}",
            f"storage failover modify -hwassist-partner-ip {controller_ips[1]} -node {pargs.netapp.node02}",
        ]
        config_function(child, pargs)
        #=====================================================
        # Configure Service Processors
        #=====================================================
        ipcount = 3
        gw   = pargs.ooband.gateway
        mask = pargs.ooband.netmask
        for node in pargs.netapp.node_list:
            spip = pargs.ooband.controller[ipcount]
            pargs.count = 1
            pargs.show  = "system service-processor show"
            pargs.regex = f"online[ ]+true[ ]+[\\d\\.]+[ ]+{spip}"
            pargs.cmds = [f"system service-processor network modify -node {node} -address-family IPv4 -enable true "\
                f"-dhcp none -ip-address {spip} -netmask {mask} -gateway {gw}"]
            config_function(child, pargs)
            ipcount += 1
            #===========================================================
            # Disable Flow Control on Data Ports
            #===========================================================
            for dp in pargs.netapp.data_ports:
                pargs.count = 1
                pargs.show  = f"network port show -node {node} -port {dp}"
                pargs.regex = f"Flow Control Administrative: none"
                pargs.cmds = [f"network port modify -node {node} -port {dp} -flowcontrol-admin none"]
                config_function(child, pargs)
        #=====================================================
        # Change Fibre-Channel Port Speeds
        #=====================================================
        for fca in pargs.netapp.fcp_ports:
            for node in pargs.netapp.node_list:
                cmdp1 = f'fcp adapter modify -node {node} -adapter {fca}'
                cmds = [
                    f'{cmdp1} -status-admin down',
                    'sleep',
                    f'{cmdp1} -speed {pargs.netapp.fcp_speed} -status-admin up'
                ]
            child.sendline(f'network interface show -curr-port {fca}')
            check = False
            cmd_check = False
            while cmd_check == False:
                i = child.expect(['There are no entries', 'were displayed', pargs.hostPrompt])
                if i == 0: check = False
                elif i == 1: check = True
                elif i == 2: cmd_check = True
            if check == False:
                for cmd in cmds:
                    if 'sleep' in cmd: time.sleep(3)
                    else: 
                        child.sendline(cmd)
                        child.expect(pargs.hostPrompt)
        #=====================================================
        # Disk Zero Spares
        #=====================================================
        cmd = 'disk zerospares'
        child.sendline(cmd)
        child.expect(pargs.hostPrompt)
        cmd = 'disk show -fields zeroing-percent'
        child.sendline(cmd)
        dcount = 0
        zerospares = False
        while zerospares == False:
            i = child.expect([r'\d.\d.[\d]+ [\d]', 'to page down', pargs.hostPrompt])
            if i == 0:
                if dcount == 10: print(f'\n**failed on "{cmd}".  Please Check for any issues and restart the wizard.')
                time.sleep(60)
                dcount =+ 1
                child.sendline(cmd)
            elif i == 1: child.send(' ')
            elif i == 2: zerospares = True
        child.sendline('exit')
        child.expect('closed')
        child.close()
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


    #=====================================================
    # NetApp Cluster Creation
    #=====================================================
    def cluster(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section(self.type, 'netapp')
        i = DotMap(deepcopy(pargs.item))
        uri = 'cluster/ntp/servers'
        jData = get(uri, pargs, **kwargs)
        for ntp in i.ntp_servers:
            method = 'post'
            uri = 'cluster/ntp/servers'
            for r in jData['records']:
                r = DotMap(deepcopy(r))
                if r.server == ntp:
                    method = 'patch'
                    uri = uri + '/' + ntp
            polVars = {"server": ntp}
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            if method == 'post':
                eval(f"{method}(uri, pargs, payload, **kwargs)")
        uri = 'network/ip/interfaces'
        jData = get(uri, pargs, **kwargs)
        method = 'post'
        for r in jData['records']:
            r = DotMap(deepcopy(r))
            if r.name == i.management_interfaces[0].name:
                method = 'patch'
                uri = uri + '/' + r.uuid
            polVars.update({"location": {"auto_revert": True}})                    
        polVars = {
            "name": "cluster-mgmt",
            "ip": {
                "address": i.management_interfaces[0].ip.address,
                "netmask": 24
            },
            "location": {"auto_revert": True}
        }
        if method == 'post': polVars.update({"ipspace": "Default"})
        payload = json.dumps(polVars)
        if print_payload: print(json.dumps(polVars, indent=4))
        print(f"  Configuring Cluster {polVars['name']}")
        eval(f"{method}(uri, pargs, payload, **kwargs)")
        #=====================================================
        # Perform License Validation
        #=====================================================
        uri = 'cluster/licensing/licenses'
        licenseData = get(uri, pargs, **kwargs)
        #=====================================================
        # Validate Licenses Exist for Each Protocol
        #=====================================================
        for p in pargs.netapp.protocols:
            license_installed = False
            for r in licenseData['records']:
                r = DotMap(deepcopy(r))
                if r.name == p: license_installed = True
            if license_installed == False:
                print(f'\n!!! ERROR !!!\nNo License was found for protocol {p}\n')
                sys.exit()
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


    #=====================================================
    # NetApp Node Creation
    #=====================================================
    def nodes(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section(self.type, 'netapp')
        #=====================================================
        # Get Existing Storage Aggregates
        #=====================================================
        for i in pargs.item:
            i = DotMap(deepcopy(i))
            pargs.netapp[i.name].interfaces = {}
            pargs.netapp[i.name]['aggregates'] = {}
            #=====================================================
            # Create/Patch Storage Aggregates
            #=====================================================
            aggregate   = i['storage_aggregates'][0]['name']
            method = 'post'
            print(f"\n    Get Existing Storage Aggregates")
            uri = 'storage/aggregates'
            storageAggs = get(uri, pargs, **kwargs)
            if storageAggs.get('records'):
                for r in storageAggs['records']:
                    r = DotMap(deepcopy(r))
                    if r.name == aggregate:
                        method = 'patch'
                        uri = f'storage/aggregates/{r.uuid}'
            polVars = deepcopy(i.storage_aggregates[0])
            polVars.update({"node": {"name": i.name}})
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            print(f"\n    Configuring Storage Aggregate {aggregate}")
            eval(f"{method}(uri, pargs, payload, **kwargs)")
            print(f"\n    Add Storage Aggregate to Dictionaries")
            uri = 'storage/aggregates'
            storageAggs = get(uri, pargs, **kwargs)
            for r in storageAggs['records']:
                r = DotMap(deepcopy(r))
                if r.name == aggregate:
                    pargs.netapp[i.name]['aggregates'].update({"name":aggregate,"uuid":r.uuid})
            #=====================================================
            # Update Interfaces on the Nodes
            #=====================================================
            print(f"\n    Get Existing Ethernet Port Records.")
            uri = f'network/ethernet/ports?node.name={i.name}'
            ethernetPorts = get(uri, pargs, **kwargs)
            method = 'post'
            #=====================================================
            # See if LAG and Data Ports already exists
            #=====================================================
            for r in ethernetPorts['records']:
                r = DotMap(deepcopy(r))
                if r.name == 'a0a':
                    method = 'patch'
                    pargs.netapp[i.name].interfaces.update({r.name:r.uuid})
                for dp in pargs.netapp.data_ports:
                    if r.name == dp: pargs.netapp[i.name].interfaces.update({dp:r.uuid})
            #=====================================================
            # Create/Patch the LAG - a0a
            #=====================================================
            uri = 'network/ethernet/ports'
            if method == 'patch': uri = f'network/ethernet/ports/{pargs.netapp[i.name].interfaces["a0a"]}'
            else: 'network/ethernet/ports'
            polVars = deepcopy(i['interfaces']['lacp'][0])
            polVars.update({"node": {"name":i.name}})
            polVars['broadcast_domain'].update({"uuid": pargs.netapp.broadcast_domains[polVars['broadcast_domain']['name']]})
            for dp in polVars['lag']['member_ports']:
                dp.update({
                    "uuid": pargs.netapp[i.name].interfaces[dp['name']],
                    "node": {"name": i.name}
                })
            if method == 'patch':
                pop_list = ['distribution_policy', 'mode']
                for p in pop_list: polVars['lag'].pop(p)
                pop_list = ['node', 'type']
                for p in pop_list: polVars.pop(p)
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, pargs, payload, **kwargs)")
            uri = f'network/ethernet/ports?node.name={i.name}'
            #=====================================================
            # Get UUID For the LAG
            #=====================================================
            ethernetPorts = get(uri, pargs, **kwargs)
            method = 'post'
            for r in ethernetPorts['records']:
                r = DotMap(deepcopy(r))
                if r.name == 'a0a': pargs.netapp[i.name].interfaces.update({'a0a': r.uuid})
            #=====================================================
            # Create/Patch the VLAN Interfaces for the LAG
            #=====================================================
            uri = f'network/ethernet/ports?fields=node,type,vlan&node.name={i.name}'
            ethernetPorts = get(uri, pargs, **kwargs)
            for x in i['interfaces']['vlan']:
                polVars = deepcopy(x)
                x = DotMap(deepcopy(x))
                uri = 'network/ethernet/ports'
                method = 'post'
                polVars['broadcast_domain'].update({
                    "uuid": pargs.netapp.broadcast_domains[x.broadcast_domain.name]
                })
                polVars.update({"node": i.name})
                polVars['vlan']['base_port'].update({
                    "node": {"name": i.name},
                    "uuid": pargs.netapp[i.name].interfaces['a0a']
                })
                for r in ethernetPorts['records']:
                    r = DotMap(deepcopy(r))
                    if r.type == 'vlan':
                        if r.vlan.base_port.name == 'a0a' and r.vlan.tag == x.vlan.tag:
                            method = 'patch'
                            uri = f'network/ethernet/ports/{r.uuid}'
                            polVars.pop('node')
                            polVars.pop('type')
                            polVars.pop('vlan')
                payload = json.dumps(polVars)
                if print_payload: print(json.dumps(polVars, indent=4))
                eval(f"{method}(uri, pargs, payload, **kwargs)")
            uri = f'network/ethernet/ports?fields=node,type,vlan&node.name={i.name}'
            intfData = get(uri, pargs, **kwargs)
            for x in i['interfaces']['vlan']:
                intf_name = f'a0a-{x.vlan.tag}'
                x = DotMap(deepcopy(x))
                for r in intfData['records']:
                    r = DotMap(deepcopy(r))
                    if r.type == 'vlan':
                        if r.vlan.tag == x.vlan.tag:
                            pargs.netapp[i.name].interfaces.update({intf_name:r.uuid})
        #=====================================================
        # Delete Default-* Broadcast Domains
        #=====================================================
        uri = '/network/ethernet/broadcast-domains'
        bDomains = get(uri, pargs, **kwargs)
        for r in bDomains['records']:
            r = DotMap(deepcopy(r))
            if 'Default-' in r.name:
                uri = f'network/ethernet/broadcast-domains/{r.uuid}'
                delete(uri, pargs, payload, **kwargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


    #=====================================================
    # NetApp Volumes Creation
    #=====================================================
    def schedule(self, pargs, **kwargs):
        for i in pargs.item:
            polVars = i
            i = DotMap(deepcopy(i))
            #=====================================================
            # Create/Path Volumes
            #=====================================================
            uri    = f'cluster/schedules?svm.name={i.svm.name}'
            jData  = get(uri, pargs, **kwargs)
            method = 'post'
            uri    = f'cluster/schedules'
            for r in jData['records']:
                r = DotMap(deepcopy(r))
                if r.name == i.name:
                    method = 'patch'
                    uri = uri + '/' + r.uuid
                    polVars.pop('cluster')
                    polVars.pop('name')
                    polVars.pop('svm')
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, pargs, payload, **kwargs)")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


    #=====================================================
    # NetApp SNMP Creation
    #=====================================================
    def snmp(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section(self.type, 'netapp')
        #=====================================================
        # Get Auth and Privilege Passwords
        #=====================================================
        kwargs['Variable'] = 'snmp_auth'
        kwargs = ezfunctions.sensitive_var_value(**kwargs)
        pargs.netapp.snmp_auth = kwargs['var_value']
        kwargs['Variable'] = 'snmp_priv'
        kwargs = ezfunctions.sensitive_var_value(**kwargs)
        pargs.netapp.snmp_priv = kwargs['var_value']
        #=====================================================
        # Configure SNMP Global Settings
        #=====================================================
        polVars = deepcopy(pargs.item)
        polVars.pop('users')
        polVars.pop('traps')
        payload = json.dumps(polVars)
        if print_payload: print(json.dumps(polVars, indent=4))
        uri = 'support/snmp'
        patch(uri, pargs, payload, **kwargs)
        #=====================================================
        # Configure SNMP Users
        #=====================================================
        jData = get(uri, pargs, **kwargs)
        for polVars in pargs.item['users']:
            method = 'post'
            uri = 'support/snmp/users'
            jData = get(uri, pargs, **kwargs)
            if jData.get('records'):
                for r in jData['records']:
                    r = DotMap(deepcopy(r))
                    if polVars['name'] == r.name:
                        engine_id = r.engine_id
                        #url = uri + f"/{engine_id}/{r.name}"
                        #delete(url, pargs, **kwargs)
                        method = 'patch'
            if method == 'post':
                polVars['owner'].update({"uuid": pargs.netapp.svms[pargs.netapp.data_svm]})
                if method == 'post':
                    polVars['snmpv3'].update({
                        "authentication_password": pargs.netapp.snmp_auth,
                        "privacy_password": pargs.netapp.snmp_priv,
                    })
                payload = json.dumps(polVars)
                if print_payload: print(json.dumps(polVars, indent=4))
                eval(f"{method}(uri, pargs, payload, **kwargs)")
        #=====================================================
        # Configure SNMP Trap Servers
        #=====================================================
        uri = 'support/snmp/traphosts'
        jData = get(uri, pargs, **kwargs)
        for polVars in pargs.item['traps']:
            method = 'post'
            uri = 'support/snmp/traphosts'
            jData = get(uri, pargs, **kwargs)
            for r in jData['records']:
                r = DotMap(deepcopy(r))
                traphost = ''
                if r.host == polVars['host']:
                    method = 'patch'
                    #uri = uri + '/' + r.uuid
                elif re.search('^[\\d]{1,3}\\.[\\d]{1,3}\\.[\\d]{1,3}\\.[\\d]{1,3}$', polVars['host']):
                    traphost, alias, addresslist = socket.gethostbyaddr(polVars['host'])
                    if r.host == traphost:
                        method = 'patch'
                        #uri = uri + '/' + r.uuid
            if method == 'post':
                payload = json.dumps(polVars)
                if print_payload: print(json.dumps(polVars, indent=4))
                eval(f"{method}(uri, pargs, payload, **kwargs)")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


    #=====================================================
    # NetApp Storage Virtual Machine Creation (vserver)
    #=====================================================
    def svm(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Notification
        #=====================================================
        validating.begin_section(self.type, 'netapp')
        #=====================================================
        # Load Variables and Login to Storage Array
        #=====================================================
        pargs.hostname     = pargs.netapp.node01
        pargs.hostPassword = 'netapp_password'
        pargs.hostPrompt   = deepcopy(pargs.netapp.hostPrompt)
        pargs.username     = pargs.netapp.user
        child, kwargs      = child_login(pargs, **kwargs)
        host_file = open(f'{pargs.hostname}.txt', 'r')
        #=====================================================
        # Create Storage Virtual Machine
        #=====================================================
        svm      = deepcopy(pargs.netapp.data_svm)
        svmcount = 0
        child.sendline('vserver show')
        child.expect(pargs.hostPrompt)
        for line in host_file:
            if re.search(f'{svm}[ ]+data', line): svmcount += 2
            elif re.search(svm, line): svmcount += 1
            elif re.search('data', line): svmcount += 1
        if not svmcount >= 2:
            cmd = f'vserver create -vserver {svm} -rootvolume {pargs.netapp.rootv} -rootvolume-security-style unix'
            child.sendline(cmd)
            child.expect(pargs.hostPrompt)
        #=====================================================
        # Configure Aggregates and add Login Banner
        #=====================================================
        cmds = [
            f'vserver modify {svm} -aggr-list {pargs.netapp.agg1},{pargs.netapp.agg2}',
            f'security login banner modify -vserver {pargs.netapp.cluster} -message "{pargs.netapp.banner}"'
        ]
        for cmd in cmds:
            child.sendline(cmd)
            child.expect(pargs.hostPrompt)
        child.sendline(f'vserver show -vserver RICH -protocols')
        child.expect(f'{svm}[ ]+([\\w].*[\\w])[  ]')
        protocols = (((child.match).group(1)).strip()).split(',')
        child.expect(pargs.hostPrompt)
        protos = []
        for p in pargs.netapp.protocols: protos.append(p)
        if 'nvme_of' in protos:
            protos.remove('nvme_of')
            protos.append('nvme')
        child.sendline(f'vserver add-protocols -protocols {",".join(protos)} -vserver {svm}')
        child.expect(pargs.hostPrompt)
        removep = []
        for p in protocols:
            p = p.strip()
            if not p in protos: removep.append(p)
        if len(removep) > 0:
            child.sendline(f'vserver remove-protocols -vserver {svm} -protocols {",".join(removep)}')
            child.expect(pargs.hostPrompt)
        #=====================================================
        # Function to Configure Protocols
        #=====================================================
        def config_protocols(child, pargs):
            pargs.message = f'\n{"-"*81}\n\n  !!! ERROR !!!!\n  **failed on "{pargs.show}".\n'\
                f'    Looking for regex "{pargs.regex1}".\n'\
                f'    Looking for regex "{pargs.regex2}".\n'\
                f'    Looking for regex "{pargs.regex3}".\n'\
                f'\n  Please Validate {svm} and restart this wizard.\n\n{"-"*81}\n'
            child.sendline(pargs.show)
            change = 'none'
            value  = ''
            cmd_check = False
            while cmd_check == False:
                i = child.expect(["to page down", pargs.regex1, pargs.regex2, pargs.regex3, pargs.hostPrompt], timeout=20)
                if i == 0: child.send(' ')
                elif i == 1: change = 'create'
                elif i == 2: change = 'modify'
                elif i == 3: value = (child.match).group(1)
                elif i == 4: cmd_check = True
            if not change == 'none':
                child.sendline(f"vserver {pargs.p} {change} -vserver {svm} -status-admin up",)
                cmd_check = False
                while cmd_check == False:
                    i = child.expect(["Do you want to continue", pargs.hostPrompt])
                    if i == 0: child.sendline('y')
                    elif i == 1: cmd_check = True
                time.sleep(10)
                child.sendline(pargs.show)
                change = 'none'
                cmd_check = False
                while cmd_check == False:
                    i = child.expect(["to page down", pargs.regex1, pargs.regex2, pargs.regex3, pargs.hostPrompt])
                    if i == 0: child.send(' ')
                    elif i == 1: change = 'create'
                    elif i == 2: change = 'modify'
                    elif i == 3: value = (child.match).group(1)
                    elif i == 4: cmd_check = True
            if not change == 'none' and len(value) > 0:
                print(pargs.message)
                sys.exit(1)
            return value
        #=====================================================
        # Configure Protocols
        #=====================================================
        for p in protos:
            if not 'nfs' in p:
                pargs.show   = f"vserver {p} show -vserver {svm}"
                pargs.regex1 = "There are no entries matching your query"
                pargs.regex2 = "Administrative Status: down"
                if 'fcp' in p: pargs.regex3 = "Target Name: (([\\da-f]{2}:){7}[\\da-f]{2})"
                elif 'iscsi' in p: pargs.regex3 = "(iqn\\.[\\da-z\\.:\\-]+vs\\.[\\d]+(?=[\r\n]))"
                elif 'nvme' in p: pargs.regex3 = "NQN: (nqn\\..*discovery)"
                pargs.p = p
                value = config_protocols(child, pargs)
                print(f"\n\n{value}\n\n")
                if 'iscsi' in p: pargs.netapp.iscsi.iqn = value
                elif 'nvme' in p: pargs.netapp.nvme.nqn = value
        #=====================================================
        # Configure NFS Export Policy
        #=====================================================
        cmdp = f'vserver export-policy rule METHOD -vserver {svm} -policyname default -protocol nfs -ruleindex 1'
        rules = '-rorule sys -rwrule sys -superuser sys -allow-suid true'
        pargs.count = 1
        pargs.show  = cmdp.replace('METHOD', 'show')
        pargs.regex = pargs.netapp.nfs.network
        pargs.cmds  = [f"{cmdp.replace('METHOD', 'create')} -clientmatch {pargs.netapp.nfs.network} {rules}"]
        config_function(child, pargs)
        #=====================================================
        # Close the Child Process
        #=====================================================
        child.sendline('exit')
        child.expect('closed')
        child.close()
        pargs.netapp.svms = {}
        for i in pargs.item:
            i = DotMap(deepcopy(i))
            #=====================================================
            # Get Existing SVMs
            #=====================================================
            uri = 'svm/svms'
            jData = get(uri, pargs, **kwargs)
            method = 'post'
            for r in jData['records']:
                r = DotMap(deepcopy(r))
                if r.name == i.name:
                    method = 'patch'
                    uri = uri + '/' + r.uuid
                    pargs.netapp.svms.update({i.name:r.uuid})
            uri = 'cluster'
            r = get(uri, pargs, **kwargs)
            pargs.netapp.svms.update({pargs.netapp.cluster:r['uuid']})
            #=====================================================
            # Configure Default Route
            #=====================================================
            uri    = f'network/ip/routes?fields=svm,destination&svm.name={i.name}'
            jData  = get(uri, pargs, **kwargs)
            method = 'post'
            uri    = f'network/ip/routes'
            if jData.get('records'):
                for r in jData['records']:
                    r = DotMap(deepcopy(r))
                    if r.destination.address == '0.0.0.0':
                        method = 'patch'
                        uri = uri + '/' + r.uuid
            if not method == 'patch':
                polVars = i['routes'][0].toDict()
                payload = json.dumps(polVars)
                if print_payload: print(json.dumps(polVars, indent=4))
                eval(f"{method}(uri, pargs, payload, **kwargs)")
            #=====================================================
            # Configure the vsadmin password and Unlock It
            #=====================================================
            uri = f'security/accounts/{pargs.netapp.svms[i.name]}/vsadmin'
            jData = get(uri, pargs, **kwargs)
            r = DotMap(deepcopy(jData))
            if not r.locked == False:
                uri = f'security/accounts/{pargs.netapp.svms[i.name]}/vsadmin'
                polVars = { "locked": False, "password": pargs.netapp.password }
                payload = json.dumps(polVars)
                if print_payload: print(json.dumps(polVars, indent=4))
                eval(f"{method}(uri, pargs, payload, **kwargs)")
            #=====================================================
            # Configure the SSL Certificate for the Infra SVM
            #=====================================================
            #common_name = pargs.netapp.cluster + '-inb.' + pargs.dns_domains[0]
            #uri = f'security/certificates?svm.name={i.name}&type=server&fields=common_name'
            #jData = get(uri, pargs, **kwargs)
            #common = False
            #for r in jData:
            #    r = DotMap(deepcopy(r))
            #    if not r.common_name == common_name:
            #        uri = f'security/accounts/{pargs.netapp.svms[i.name]}/vsadmin'
            #        polVars = { "locked": False, "password": pargs.netapp.password }
            #        payload = json.dumps(polVars)
            #        if print_payload: print(json.dumps(polVars, indent=4))
            #        eval(f"{method}(uri, pargs, payload, **kwargs)")
            #if common == False:
            #    polVars = {
            #        "common_name": common_name,
            #        "expiry_time": "3652",
            #        "hash_function": "sha256",
            #        "size": "2048",
            #        "type": "server",
            #        "svm": { "name": i.name }
            #    }
            #=====================================================
            # Configure NFS Settings for the SVM
            #=====================================================
            uri    = f'protocols/nfs/services/'
            jData  = get(uri, pargs, **kwargs)
            method = 'post'
            for r in jData['records']:
                r = DotMap(deepcopy(r))
                if r.svm.uuid == pargs.netapp.svms[i.name]:
                    method = 'patch'
                    uri = f'protocols/nfs/services/{pargs.netapp.svms[i.name]}'
            polVars = {
                "protocol": {"v3_enabled": True, "v41_enabled": True},
                "transport": {"udp_enabled": False},
                "vstorage_enabled": True,
                "svm":{ "name": i.name, "uuid": pargs.netapp.svms[i.name] }
            }
            if method == 'patch': polVars.pop('svm')
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, pargs, payload, **kwargs)")
             #=====================================================
            # Disable Weak Security
            # SSH Ciphers and MAC Algorithms
            #=====================================================
            uri = 'security/ssh'
            jData = get(uri, pargs, **kwargs)
            remove_ciphers = ['aes256-cbc','aes192-cbc','aes128-cbc','3des-cbc']
            remove_macs = ['hmac-md5','hmac-md5-96','hmac-md5-etm','hmac-md5-96-etm','hmac-sha1-96','hmac-sha1-96-etm']
            cipher_list = []
            mac_algorithms = []
            for r in jData['ciphers']:
                if not r in remove_ciphers: cipher_list.append(i)
            for r in jData['mac_algorithms']:
                if not r in remove_macs: mac_algorithms.append(i)
            #=====================================================
            # Disable Ciphers on Cluster
            #=====================================================
            uri = 'security/ssh'
            method = 'patch'
            polVars = {"ciphers": cipher_list, "mac_algorithms": mac_algorithms}
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, pargs, payload, **kwargs)")
            #=====================================================
            # Disable Ciphers and Configure Login Banner - SVM
            #=====================================================
            uri = f'security/ssh/svms/{pargs.netapp.svms[i.name]}'
            polVars = { "ciphers": cipher_list, "mac_algorithms": mac_algorithms }
            method = 'patch'
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, pargs, payload, **kwargs)")
            method = 'post'
            uri = f'security/login/messages?fields=svm'
            loginData = get(uri, pargs, **kwargs)
            uri = f'security/login/messages'
            for r in loginData['records']:
                r = DotMap(deepcopy(r))
                if r.get('svm'):
                    if r.svm.uuid == pargs.netapp.svms[i.name]:
                        method = 'patch'
                        uri = uri + '/' + pargs.netapp.svms[i.name]
            polVars = {
                "banner": pargs.netapp.banner,
                "scope": "svm",
                "show_cluster_message": True,
                "svm": {"name": i.name, "uuid": pargs.netapp.svms[i.name]}
            }
            if method == 'patch':
                polVars.pop('svm')
                polVars.pop('scope')
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, pargs, payload, **kwargs)")
            #=====================================================
            # Enable FIPS Security
            #=====================================================
            polVars = {"fips": {"enabled": True}}
            uri = 'security'
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            patch(uri, pargs, payload, **kwargs)
            #=====================================================
            # Configure Infra SVM Interfaces
            #=====================================================
            for intf in i['ddata_interfaces']:
                intf = DotMap(deepcopy(intf))
                polVars = deepcopy(intf.toDict())
                polVars['svm'] = {'name':i.name}
                uri = 'network/ip/interfaces'
                intfData = get(uri, pargs, **kwargs)
                method = 'post'
                for r in intfData['records']:
                    r = DotMap(deepcopy(r))
                    if r.name == intf.name:
                        uri = uri + '/' + r.uuid
                        method = 'patch'
                if method == 'patch':
                    polVars.pop('scope')
                    polVars.pop('svm')
                    if re.search('(iscsi|nvme)', polVars.name):
                        polVars['location'].pop('home_node')
                        polVars['location'].pop('home_port')
                payload = json.dumps(polVars)
                if print_payload: print(json.dumps(polVars, indent=4))
                print(f"  Configuring {svm} - {intf.name}")
                eval(f"{method}(uri, pargs, payload, **kwargs)")
            #=====================================================
            # Configure Infra SVM Interfaces
            #=====================================================
            if 'fc' in pargs.dtype:
                for intf in i['fcp_interfaces']:
                    intf = DotMap(deepcopy(intf))
                    polVars = deepcopy(intf.toDict())
                    polVars['svm'] = {'name':i.name}
                    uri = 'network/fc/interfaces'
                    intfData = get(uri, pargs, **kwargs)
                    method = 'post'
                    for r in intfData['records']:
                        r = DotMap(deepcopy(r))
                        if r.name == intf.name:
                            uri = uri + '/' + r.uuid
                            method = 'patch'
                    if method == 'patch':
                        polVars.pop('data_protocol')
                        polVars.pop('svm')
                    payload = json.dumps(polVars)
                    if print_payload: print(json.dumps(polVars, indent=4))
                    print(f"  Configuring {svm} - {intf.name}")
                    eval(f"{method}(uri, pargs, payload, **kwargs)")
            uri = 'network/fc/interfaces?fields=name,wwnn,wwpn'
            intfData = get(uri, pargs, **kwargs)
            fcp_temp = pargs.netapp.fcp_ports
            half = len(fcp_temp)//2
            pargs.netapp.wwpns.a = []
            pargs.netapp.wwpns.b = []
            for r in intfData['records']:
                r = DotMap(deepcopy(r))
                for f in fcp_temp[:half]:
                    if f in r.name:
                        pargs.netapp.wwpns.a.append({r.name:r.wwpn})
                for f in fcp_temp[half:]:
                    if f in r.name:
                        pargs.netapp.wwpns.b.append({r.name:r.wwpn})
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


    #=====================================================
    # NetApp Volumes Creation
    #=====================================================
    def volumes(self, pargs, **kwargs):
        #=====================================================
        # Send Notification
        #=====================================================
        validating.begin_section(self.type, 'netapp')
        #=====================================================
        # Load Variables and Login to Storage Array
        #=====================================================
        pargs.hostname     = pargs.netapp.node01
        pargs.hostPassword = 'netapp_password'
        pargs.hostPrompt   = deepcopy(pargs.netapp.hostPrompt)
        pargs.username     = pargs.netapp.user
        child, kwargs      = child_login(pargs, **kwargs)
        host_file          = open(f'{pargs.hostname}.txt', 'r')
        pargs.netapp.volumes = {}
        print('\n\n')
        for i in pargs.item:
            polVars = i
            polVars.pop('volume_type')
            i = DotMap(deepcopy(i))
            #=====================================================
            # Create/Patch Volumes
            #=====================================================
            uri    = f'storage/volumes/?svm.name={i.svm.name}'
            jData  = get(uri, pargs, **kwargs)
            method = 'post'
            uri    = f'storage/volumes'
            for r in jData['records']:
                r = DotMap(deepcopy(r))
                if r.name == i.name:
                    method = 'patch'
                    uri = uri + '/' + r.uuid
                    pargs.netapp.volumes.update({i.name:r.uuid})
                    pop_list = ['aggregates', 'encryption', 'style', 'svm', 'type']
                    for p in pop_list:
                        if polVars.get(p): polVars.pop(p)
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            print(f'   {method} SVM {i.svm.name} Volume {i.name}')
            eval(f"{method}(uri, pargs, payload, **kwargs)")
            if re.search('_m0[1-2]$', i.name):
                #=====================================================
                # Attach the Mirrors to the Schedule and Initialize
                #=====================================================
                dest = f"{i.svm.name}:{i.name}"
                src  = f"{i.svm.name}:{pargs.netapp.rootv}"
                pargs.count = 1
                pargs.show  = f"snapmirror show -vserver {i.svm.name} -destination-path {dest} -source-path {src}"
                pargs.regex = f"Destination Path: {pargs.netapp.cluster}://{i.svm.name}/{i.name}"
                pargs.cmds  = [
                    f"snapmirror create -vserver {i.svm.name} -destination-path {dest} -source-path {src} -type LS -schedule 15min"
                ]
                config_function(child, pargs)
            elif i.volume_type == 'swap':
                child.sendline(f'volume efficiency off -vserver {i.svm.name} -volume i.name')
                child.expect(pargs.hostPrompt)
        #=====================================================
        # Initialize the snapmirror
        #=====================================================
        src  = f"{i.svm.name}:{pargs.netapp.rootv}"
        pargs.count = 2
        pargs.show  = f"snapmirror show -vserver {i.svm.name} -source-path {src}"
        pargs.regex = "true"
        pargs.cmds  = [ f"snapmirror initialize-ls-set -source-path {src}" ]
        config_function(child, pargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


#=====================================================
# Function - API Authentication
#=====================================================
def auth(pargs, section='', **kwargs):
    url = f"https://{pargs.host}"
    user = pargs.netapp.user
    kwargs['Variable'] = 'netapp_password'
    kwargs = ezfunctions.sensitive_var_value(**kwargs)
    password = kwargs['var_value']
    s = requests.Session()
    s.auth = (user, password)
    auth = ''
    while auth == '':
        try:
            auth = s.post(url, verify=False)
        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)
    return s, url

#=====================================================
# pexpect - Login Function
#=====================================================
def child_login(pargs, **kwargs):
    hostname    = pargs.hostname
    systemShell = os.environ['SHELL']
    kwargs['Variable'] = pargs.hostPassword
    kwargs   = ezfunctions.sensitive_var_value(**kwargs)
    password = kwargs['var_value']
    #=====================================================
    # Use 
    #=====================================================
    child = pexpect.spawn(systemShell, encoding='utf-8')
    child.logfile_read = sys.stdout
    child.sendline(f'ssh {pargs.username}@{hostname} | tee {hostname}.txt')
    child.expect(f'tee {hostname}.txt')
    logged_in = False
    while logged_in == False:
        i = child.expect(['Are you sure you want to continue', 'closed', 'Password:', pargs.hostPrompt])
        if i == 0: child.sendline('yes')
        elif i == 1:
            print(f'\n**failed to connect.  '\
                f'Please Validate {hostname} is correct and username {pargs.username} is correct.')
        elif i == 2: child.sendline(password)
        elif i == 3: logged_in = True
    return child, kwargs

#=====================================================
# pexpect - Configuration Function
#=====================================================
def config_function(child, pargs):
    pargs.message = f'\n{"-"*81}\n\n  !!! ERROR !!!!\n  **failed on "{pargs.show}".\n'\
        f'    Looking for regex "{pargs.regex}".\n'\
        f'\n  Please Validate the cluster and restart this wizard.\n\n{"-"*81}\n'
    child.sendline(pargs.show)
    count = 0
    cmd_check = False
    while cmd_check == False:
        i = child.expect(["to page down", pargs.regex, pargs.hostPrompt], timeout=20)
        if i == 0: child.send(' ')
        elif i == 1: count += 1
        elif i == 2: cmd_check = True
    if not count == pargs.count:
        for cmd in pargs.cmds:
            child.sendline(cmd)
            cmd_check = False
            while cmd_check == False:
                i = child.expect(["Do you want to continue", pargs.hostPrompt])
                if i == 0: child.sendline('y')
                elif i == 1: cmd_check = True
        time.sleep(3)
        child.sendline(pargs.show)
        count = 0
        cmd_check = False
        while cmd_check == False:
            i = child.expect(["to page down", pargs.regex, pargs.hostPrompt])
            if i == 0: child.send(' ')
            if i == 1: count += 1
            elif i == 2: cmd_check = True
        if not count == pargs.count:
            print(pargs.message)
            sys.exit(1)

#=====================================================
# Function - API - delete
#=====================================================
def delete(uri, pargs, section='', **kwargs):
    s, url = auth(pargs, **kwargs)
    r = ''
    while r == '':
        try:
            r = s.delete(f'{url}/api/{uri}', verify=False)
            if print_response_always:
                print(f"delete: {r.status_code} success with {uri}")
                #print(r.text)
            if r.status_code == 200 or r.status_code == 404:
                return r.json()
            else: validating.error_request_netapp('delete', r.status_code, r.text, uri)
        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

#=====================================================
# Function - API - get
#=====================================================
def get(uri, pargs, section='', **kwargs):
    s, url = auth(pargs, **kwargs)
    r = ''
    while r == '':
        try:
            r = s.get(f'{url}/api/{uri}', verify=False)
            if print_response_always:
                print(f"     * get: {r.status_code} success with {uri}")
                #print(r.text)
            if r.status_code == 200 or r.status_code == 404:
                return r.json()
            else: validating.error_request_netapp('get', r.status_code, r.text, uri)
        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

#=====================================================
# Function - API - patch
#=====================================================
def patch(uri, pargs, payload, section='', **kwargs):
    s, url = auth(pargs, **kwargs)
    r = ''
    while r == '':
        try:
            r = s.patch(f'{url}/api/{uri}', data=payload, verify=False)
            # Use this for Troubleshooting
            if not re.search('20[0-2]', str(r.status_code)): validating.error_request_netapp('patch', r.status_code, r.text, uri)
            if print_response_always:
                print(f"     * patch: {r.status_code} success with {uri}")
            return r.json()
        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

#=====================================================
# Function - API - post
#=====================================================
def post(uri, pargs, payload, section='', **kwargs):
    s, url = auth(pargs, **kwargs)
    r = ''
    while r == '':
        try:
            r = s.post(f'{url}/api/{uri}', data=payload, verify=False)
            # Use this for Troubleshooting
            if not re.search('20[1-2]', str(r.status_code)): validating.error_request_netapp('post', r.status_code, r.text, uri)
            if print_response_always:
                print(f"     * post: {r.status_code} success with {uri}")
            return r.json()
        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)
