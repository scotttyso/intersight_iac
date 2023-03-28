#!/usr/bin/env python3

from copy import deepcopy
from dotmap import DotMap
import ezfunctions
import json
import numpy
import os
import pexpect
import re
import requests
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
        uri = 'support/autosupport?return_records=true'
        pargs.method = 'patch'
        jsonData = patch(uri, pargs, apiBody, **kwargs)
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
            for s in bDomains['records']:
                s = DotMap(deepcopy(s))
                if i.name == s.name:
                    method = 'patch'
                    uri = f'network/ethernet/broadcast-domains/{s["uuid"]}'
                    polVars.pop('name')
            if method == 'post': uri = 'network/ethernet/broadcast-domains'
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            print(f"\n    Configuring Broadcast Domain {i.name}")
            jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
        uri = '/network/ethernet/broadcast-domains'
        bDomains = get(uri, pargs, **kwargs)
        for i in pargs.item:
            i = DotMap(deepcopy(i))
            for s in bDomains['records']:
                s = DotMap(deepcopy(s))
                if i.name == s.name or 'Default' in s.name:
                    pargs.netapp.broadcast_domains.update({s.name:s.uuid})
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
        # Setup Variables
        #=====================================================
        hostPrompt  = deepcopy(pargs.netapp.hostPrompt)
        host        = pargs.host
        systemShell = os.environ['SHELL']
        kwargs['Variable'] = 'netapp_password'
        kwargs = ezfunctions.sensitive_var_value(**kwargs)
        pargs.netapp.password = kwargs['var_value']
        #=====================================================
        # Connect to the Storage Array
        #=====================================================
        child = pexpect.spawn(systemShell, encoding='utf-8')
        child.logfile_read = sys.stdout
        child.sendline(f'ssh {pargs.netapp.user}@{host}')
        child.expect(host)
        logged_in = False
        while logged_in == False:
            i = child.expect(['Are you sure you want to continue', 'closed', 'Password:', hostPrompt])
            if i == 0: child.sendline('yes')
            elif i == 1:
                print(f'\n**failed to connect.  Please Validate {host} is correct and username {pargs.netapp.user} is correct.')
            elif i == 2: child.sendline(pargs.netapp.password)
            elif i == 3: logged_in = True
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
            child.expect(hostPrompt)
        #=====================================================
        # Validation Function
        #=====================================================
        def config_validation(child, pargs):
            pargs.message = f'\n{"-"*81}\n\n  !!! ERROR !!!!\n  **failed on "{pargs.show}".\n'\
                f'    Looking for regex "{pargs.regex}".\n'\
                f'\n  Please Validate the cluster and cabling and restart this wizard.\n\n{"-"*81}\n'
            child.sendline(pargs.show)
            count = 0
            cmd_check = False
            while cmd_check == False:
                i = child.expect(["to page down", pargs.regex, hostPrompt], timeout=20)
                if i == 0: child.send(' ')
                elif i == 1: count += 1
                elif i == 2: cmd_check = True
            if not count == pargs.count:
                for cmd in pargs.cmds:
                    child.sendline(cmd)
                    cmd_check = False
                    while cmd_check == False:
                        i = child.expect(["Do you want to continue", hostPrompt])
                        if i == 0: child.sendline('y')
                        elif i == 1: cmd_check = True
                time.sleep(10)
                child.sendline(pargs.show)
                count = 0
                cmd_check = False
                while cmd_check == False:
                    i = child.expect(["to page down", pargs.regex, hostPrompt])
                    if i == 0: child.send(' ')
                    if i == 1: count += 1
                    elif i == 2: cmd_check = True
                if not count == pargs.count:
                    print(pargs.message)
                    sys.exit(1)
        #=====================================================
        # Storage Failover Check
        #=====================================================
        pargs.count = 2
        pargs.show  = "storage failover show"
        pargs.regex = "true[ ]+Connected to"
        pargs.cmds  = ["storage failover modify -node * -enabled true"]
        config_validation(child, pargs)
        #=====================================================
        # Validate Cluster High Availability
        #=====================================================
        pargs.count = 1
        pargs.show  = "cluster ha show"
        pargs.regex = "High-Availability Configured: true"
        pargs.cmds  = ['cluster ha modify -configured true']
        config_validation(child, pargs)
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
        config_validation(child, pargs)
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
            config_validation(child, pargs)
            ipcount += 1
            #===========================================================
            # Disable Flow Control on Data Ports
            #===========================================================
            for dp in pargs.netapp.data_ports:
                pargs.count = 1
                pargs.show  = f"network port show -node {node} -port {dp}"
                pargs.regex = f"Flow Control Administrative: none"
                pargs.cmds = [f"network port modify -node {node} -port {dp} -flowcontrol-admin none"]
                config_validation(child, pargs)
        #=====================================================
        # Change Fibre-Channel Port Speeds
        #=====================================================
        for fca in pargs.netapp.fcp_ports:
            child.sendline(f'network interface show -curr-port {fca}')
            check = False
            cmd_check = False
            while cmd_check == False:
                i = child.expect(['There are no entries', 'were displayed', hostPrompt])
                if i == 0: check = False
                elif i == 1: check = True
                elif i == 2: cmd_check = True
            if check == False:
                for node in pargs.netapp.node_list:
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
        jsonData = get(uri, pargs, **kwargs)
        for ntp in i.ntp_servers:
            method = 'post'
            uri = 'cluster/ntp/servers'
            for s in jsonData['records']:
                s = DotMap(deepcopy(s))
                if s.server == ntp:
                    method = 'patch'
                    uri = uri + '/' + ntp
            polVars = {"server": ntp}
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            if method == 'post':
                jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
        uri = 'network/ip/interfaces'
        jData = get(uri, pargs, **kwargs)
        method = 'post'
        for s in jData['records']:
            s = DotMap(deepcopy(s))
            if s.name == i.management_interfaces[0].name:
                method = 'patch'
                uri = uri + '/' + s.uuid
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
        jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
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
            for s in licenseData['records']:
                s = DotMap(deepcopy(s))
                if s.name == p: license_installed = True
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
            agg         = deepcopy(i.name)
            aggregate   = agg.replace('-', '_') + '_1'
            method = 'post'
            print(f"\n    Get Existing Storage Aggregates")
            uri = 'storage/aggregates'
            storageAggs = get(uri, pargs, **kwargs)
            if storageAggs.get('records'):
                for s in storageAggs['records']:
                    s = DotMap(deepcopy(s))
                    if s.name == aggregate:
                        agg_uuid = s.uuid
                        method = 'patch'
                        uri = f'storage/aggregates/{s.uuid}'
            polVars = deepcopy(i.storage_aggregates[0])
            polVars.update({"node": {"name": i.name}})
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            print(f"\n    Configuring Storage Aggregate {aggregate}")
            jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
            print(f"\n    Add Storage Aggregate to Dictionaries")
            uri = 'storage/aggregates'
            storageAggs = get(uri, pargs, **kwargs)
            for s in storageAggs['records']:
                s = DotMap(deepcopy(s))
                if s.name == aggregate:
                    pargs.netapp[i.name]['aggregates'].update({"name":aggregate,"uuid":s.uuid})
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
            for s in ethernetPorts['records']:
                s = DotMap(deepcopy(s))
                if s.name == 'a0a':
                    method = 'patch'
                    pargs.netapp[i.name].interfaces.update({s.name:s.uuid})
                for dp in pargs.netapp.data_ports:
                    if s.name == dp: pargs.netapp[i.name].interfaces.update({dp:s.uuid})
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
            jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
            uri = f'network/ethernet/ports?node.name={i.name}'
            #=====================================================
            # Get UUID For the LAG
            #=====================================================
            ethernetPorts = get(uri, pargs, **kwargs)
            method = 'post'
            for s in ethernetPorts['records']:
                s = DotMap(deepcopy(s))
                if s.name == 'a0a': pargs.netapp[i.name].interfaces.update({'a0a': s.uuid})
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
                for s in ethernetPorts['records']:
                    s = DotMap(deepcopy(s))
                    if s.type == 'vlan':
                        if s.vlan.base_port.name == 'a0a' and s.vlan.tag == x.vlan.tag:
                            method = 'patch'
                            uri = f'network/ethernet/ports/{s.uuid}'
                            polVars.pop('node')
                            polVars.pop('type')
                            polVars.pop('vlan')
                payload = json.dumps(polVars)
                if print_payload: print(json.dumps(polVars, indent=4))
                intf_name = f'a0a-{x.vlan.tag}'
            uri = f'network/ethernet/ports?fields=node,type,vlan&node.name={i.name}'
            intfData = get(uri, pargs, **kwargs)
            for x in i['interfaces']['vlan']:
                x = DotMap(deepcopy(x))
                for s in intfData['records']:
                    s = DotMap(deepcopy(s))
                    if s.type == 'vlan':
                        if s.vlan.tag == x.vlan.tag:
                            pargs.netapp[i.name].interfaces.update({intf_name:s.uuid})
        #=====================================================
        # Delete Default-* Broadcast Domains
        #=====================================================
        uri = '/network/ethernet/broadcast-domains'
        bDomains = get(uri, pargs, **kwargs)
        for s in bDomains['records']:
            s = DotMap(deepcopy(s))
            if 'Default-' in s.name:
                uri = f'network/ethernet/broadcast-domains/{s.uuid}'
                jsonData = delete(uri, pargs, payload, **kwargs)
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
        jsonData = patch(uri, pargs, payload, **kwargs)
        #=====================================================
        # Configure SNMP Users
        #=====================================================
        jsonData = get(uri, pargs, **kwargs)
        for polVars in pargs.item['users']:
            method = 'post'
            uri = 'support/snmp/users'
            if jsonData.get('records'):
                for s in jsonData['records']:
                    s = DotMap(deepcopy(s))
                    if polVars['name'] == s.name:
                        engine_id = s.engine_id
                        uri = uri + f"/{engine_id}/{s.name}"
                        method = 'patch'
            polVars['owner'].uddate({"uuid": pargs.netapp.svms[pargs.netapp.data_svm]})
            polVars['snmpv3'].update({
                "authentication_password": pargs.netapp.snmp_auth,
                "privacy_password": pargs.netapp.snmp_priv,
            })
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
        #=====================================================
        # Configure SNMP Trap Servers
        #=====================================================
        uri = 'support/snmp/traphosts'
        jsonData = get(uri, pargs, **kwargs)
        for polVars in pargs.item['traps']:
            method = 'post'
            uri = 'support/snmp/traphosts'
            for s in jsonData['records']:
                s = DotMap(deepcopy(s))
                if s.host == polVars['host']:
                    method = 'patch'
                    uri = uri + '/' + s.uuid
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


    #=====================================================
    # NetApp SVM Creation
    #=====================================================
    def svm(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Notification
        #=====================================================
        validating.begin_section(self.type, 'netapp')
        host        = pargs.netapp.node01
        hostPrompt  = deepcopy(pargs.netapp.hostPrompt)
        systemShell = os.environ['SHELL']
        kwargs['Variable'] = 'netapp_password'
        kwargs = ezfunctions.sensitive_var_value(**kwargs)
        pargs.netapp.password = kwargs['var_value']
        #=====================================================
        # Connect to Array
        #=====================================================
        #config_vserver = False
        #if config_vserver == True:
        child = pexpect.spawn(systemShell, encoding='utf-8')
        child.logfile_read = sys.stdout
        child.sendline(f'ssh {pargs.netapp.user}@{host} | tee {host}.txt')
        child.expect(f'tee {host}.txt')
        logged_in = False
        while logged_in == False:
            i = child.expect(['Are you sure you want to continue', 'closed', 'Password:', hostPrompt])
            if i == 0: child.sendline('yes')
            elif i == 1:
                print(f'\n**failed to connect.  '\
                    f'Please Validate {host} is correct and username {pargs.netapp.user} is correct.')
            elif i == 2: child.sendline(pargs.netapp.password)
            elif i == 3: logged_in = True
        host_file = open(f'{host}.txt', 'r')
        node_list = pargs.node_list
        # Create SVM
        svm     = deepcopy(pargs.netapp.data_svm)
        rootv   = (svm.replace('-', '_')) + '_root'
        svmcount = 0
        child.sendline('vserver show')
        child.expect(hostPrompt)
        for line in host_file:
            if re.search(f'{svm}[ ]+data', line): svmcount += 2
            elif re.search(svm, line): svmcount += 1
            elif re.search('data', line): svmcount += 1
        if not svmcount >= 2:
            cmd = f'vserver create -vserver {svm} -rootvolume {rootv} -rootvolume-security-style unix'
            child.sendline(cmd)
            child.expect(hostPrompt)
        #=====================================================
        # Configure Aggregates
        #=====================================================
        agg1 = deepcopy(pargs.netapp.node01).replace('-', '_') + '_1'
        agg2 = deepcopy(pargs.netapp.node02).replace('-', '_') + '_1'
        cmds = [
            f'vserver modify {svm} -aggr-list {agg1},{agg2}',
            f'security login banner modify -vserver {pargs.netapp.cluster} -message "{pargs.netapp.banner}"'
        ]
        for cmd in cmds:
            child.sendline(cmd)
            child.expect(hostPrompt)
        child.sendline(f'vserver show -vserver RICH -protocols')
        child.expect(f'{svm}[ ]+([\\w].*[\\w])[  ]')
        protocols = (((child.match).group(1)).strip()).split(',')
        child.expect(hostPrompt)
        p2 = []
        for s in pargs.netapp.protocols: p2.append(s)
        if 'nvme_of' in p2:
            p2.remove('nvme_of')
            p2.append('nvme')
        child.sendline(f'vserver add-protocols -protocols {",".join(p2)} -vserver {svm}')
        child.expect(hostPrompt)
        removep = []
        for p in protocols:
            p = p.strip()
            if not p in p2: removep.append(p)
        if len(removep) > 0:
            child.sendline(f'vserver remove-protocols -vserver {svm} -protocols {",".join(removep)}')
            child.expect(hostPrompt)
        child.sendline('exit')
        child.expect('closed')
        for i in pargs.item:
            i = DotMap(deepcopy(i))
            #=====================================================
            # Get Existing SVMs
            #=====================================================
            uri = 'svm/svms'
            svmData = get(uri, pargs, **kwargs)
            method = 'post'
            pargs.netapp.svms = {}
            for s in svmData['records']:
                s = DotMap(deepcopy(s))
                if s.name == i.name:
                    method = 'patch'
                    uri = uri + '/' + s.uuid
                    pargs.netapp.svms.update({i.name:s.uuid})
            uri = 'cluster'
            s = get(uri, pargs, **kwargs)
            pargs.netapp.svms.update({pargs.netapp.cluster:s['uuid']})
            #=====================================================
            # Configure NFS Settings for the SVM
            #=====================================================
            method = 'post'
            uri = f'protocols/nfs/services/'
            nfsData = get(uri, pargs, **kwargs)
            for s in nfsData['records']:
                s = DotMap(deepcopy(s))
                if s.svm.uuid == pargs.netapp.svms[i.name]:
                    method = 'patch'
                    uri = f'protocols/nfs/services/{pargs.netapp.svms[i.name]}'
            polVars = {
                "protocol": {"v3_enabled": True, "v41_enabled": True},
                "transport": {"udp_enabled": False},
                "vstorage_enabled": True,
                "svm":{
                    "name": i.name,
                    "uuid": pargs.netapp.svms[i.name]
                }
            }
            if method == 'patch':
                polVars.pop('svm')
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
            #=====================================================
            # Disable Weak Security
            # SSH Ciphers and MAC Algorithms
            #=====================================================
            uri = 'security/ssh'
            jsonData = get(uri, pargs, **kwargs)
            remove_ciphers = ['aes256-cbc','aes192-cbc','aes128-cbc','3des-cbc']
            remove_macs = ['hmac-md5','hmac-md5-96','hmac-md5-etm','hmac-md5-96-etm','hmac-sha1-96','hmac-sha1-96-etm']
            cipher_list = []
            mac_algorithms = []
            for s in jsonData['ciphers']:
                if not s in remove_ciphers: cipher_list.append(i)
            for s in jsonData['mac_algorithms']:
                if not s in remove_macs: mac_algorithms.append(i)
            #=====================================================
            # Disable Ciphers on Cluster
            #=====================================================
            uri = 'security/ssh'
            method = 'patch'
            polVars = {"ciphers": cipher_list, "mac_algorithms": mac_algorithms}
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
            #=====================================================
            # Disable Ciphers and Configure Login Banner - SVM
            #=====================================================
            uri = f'security/ssh/svms/{pargs.netapp.svms[i.name]}'
            polVars = { "ciphers": cipher_list, "mac_algorithms": mac_algorithms }
            method = 'patch'
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
            method = 'post'
            uri = f'security/login/messages?fields=svm'
            loginData = get(uri, pargs, **kwargs)
            uri = f'security/login/messages'
            for s in loginData['records']:
                s = DotMap(deepcopy(s))
                if s.get('svm'):
                    if s.svm.uuid == pargs.netapp.svms[i.name]:
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
            jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
            #=====================================================
            # Enable FIPS Security
            #=====================================================
            polVars = {"fips": {"enabled": True}}
            uri = 'security'
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            jsonData = patch(uri, pargs, payload, **kwargs)
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
                for s in intfData['records']:
                    s = DotMap(deepcopy(s))
                    if s.name == intf.name:
                        uri = uri + '/' + s.uuid
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
                jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
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
                    for s in intfData['records']:
                        s = DotMap(deepcopy(s))
                        if s.name == intf.name:
                            uri = uri + '/' + s.uuid
                            method = 'patch'
                    if method == 'patch':
                        polVars.pop('data_protocol')
                        polVars.pop('svm')
                    payload = json.dumps(polVars)
                    if print_payload: print(json.dumps(polVars, indent=4))
                    print(f"  Configuring {svm} - {intf.name}")
                    jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
            uri = 'network/fc/interfaces?fields=wwnn,wwpn'
            intfData = get(uri, pargs, **kwargs)
            fcp_temp = pargs.netapp.fcp_ports
            half = len(fcp_temp)//2
            pargs.netapp.a.wwpns = []
            pargs.netapp.b.wwpns = []
            for s in intfData['records']:
                s = DotMap(deepcopy(s))
                for f in fcp_temp[:half]:
                    if f in s.name:
                        pargs.netapp.a.wwpns.append(s.wwpn)
                for f in fcp_temp[half:]:
                    if f in s.name:
                        pargs.netapp.b.wwpns.append(s.wwpn)
            print(pargs.netapp['a'])
            print(pargs.netapp['b'])
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


# Function to get contents from URL
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

# Function to get contents from URL
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

# Function to get contents from URL
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

# Function to PATCH Contents to URL
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

# Function to POST Contents to URL
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

