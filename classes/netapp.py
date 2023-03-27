#!/usr/bin/env python3

from copy import deepcopy
from dotmap import DotMap
import ezfunctions
import json
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
                if i.name == s['name']:
                    method = 'patch'
                    uri = f'network/ethernet/broadcast-domains/{s["uuid"]}'
                    polVars.pop('name')
            if method == 'post': uri = 'network/ethernet/broadcast-domains'
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
        uri = '/network/ethernet/broadcast-domains'
        bDomains = get(uri, pargs, **kwargs)
        for i in pargs.item:
            i = DotMap(deepcopy(i))
            for s in bDomains['records']:
                if i.name == s['name']:
                    pargs.netapp.broadcast_domains.update({i['name']:s['uuid']})
                elif s['name'] == 'Default':
                    pargs.netapp.broadcast_domains.update({'Default':s['uuid']})
                elif 'Default-' in s['name']:
                    pargs.netapp.broadcast_domains.update({s['name']:s['uuid']})
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
        # Setup Variables
        #=====================================================
        hostPrompt  = deepcopy(pargs.netapp.hostPrompt)
        host        = pargs.host
        systemShell = os.environ['SHELL']
        kwargs['Variable'] = 'netapp_password'
        kwargs = ezfunctions.sensitive_var_value(**kwargs)
        pargs.netapp.password = kwargs['var_value']
        #=====================================================
        # Connect to Array
        #=====================================================
        child = pexpect.spawn(systemShell, encoding='utf-8')
        child.logfile_read = sys.stdout
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
        child.sendline('exit')
        child.expect('closed')
        os.remove(f'{host}.txt')
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
        polVars = deepcopy(pargs.item)
        polVars.pop('license')
        polVars.pop('management_interfaces')
        polVars.pop('ntp_servers')
        uri = 'cluster'
        payload = json.dumps(polVars)
        if print_payload: print(json.dumps(polVars, indent=4))
        #jsonData = patch(uri, pargs, payload, **kwargs)
        jsonData = get(uri, pargs, **kwargs)
        pargs.netapp.cluster = jsonData['uuid']
        uri = 'cluster/ntp/servers'
        jsonData = get(uri, pargs, **kwargs)
        for server in pargs.item['ntp_servers']:
            method = 'post'
            uri = 'cluster/ntp/servers'
            for i in jsonData['records']:
                if i['server'] == server:
                    method = 'patch'
                    uri = uri + '/' + server
            polVars = {"server": server}
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            if method == 'post':
                jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
        uri = 'network/ip/interfaces'
        jsonData = get(uri, pargs, **kwargs)
        method = 'post'
        for i in jsonData['records']:
            if i['name'] == pargs.item['management_interfaces'][0]['name']:
                method = 'patch'
                uri = uri + '/' + i['uuid']
        
            polVars.update({"location": {"auto_revert": True}})                    
        polVars = {
            "name": "cluster-mgmt",
            "ip": {
                "address": pargs.item['management_interfaces'][0]['ip']["address"],
                "netmask": 24
            },
            "location": {"auto_revert": True}
        }
        if method == 'post': polVars.update({"ipspace": "Default"})
        payload = json.dumps(polVars)
        if print_payload: print(json.dumps(polVars, indent=4))
        jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
            
        #=====================================================
        # Perform License Validation
        #=====================================================
        pargs.netapp.protocols = ['nfs']
        if pargs.dtype == 'fc': pargs.netapp.protocols.append('fcp')
        elif pargs.dtype == 'fc-nvme': pargs.netapp.protocols.extend(['fcp', 'nvme_of'])
        elif pargs.dtype == 'iscsi': pargs.netapp.protocols.append('iscsi')
        elif pargs.dtype == 'nvme': pargs.netapp.protocols.extend(['iscsi', 'nvme_of'])
        uri = 'cluster/licensing/licenses'
        licenseData = get(uri, pargs, **kwargs)
        #=====================================================
        # Validate Licenses Exist for Each Protocol
        #=====================================================
        for s in pargs.netapp.protocols:
            p = s
            license_installed = False
            for i in licenseData['records']:
                if i['name'] == p: license_installed = True
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
        uri = 'storage/aggregates'
        storageAggs = get(uri, pargs, **kwargs)
        for i in pargs.item:
            i = DotMap(deepcopy(i))
            pargs.netapp[i.name].interfaces = {}
            pargs.netapp[i.name]['aggregates'] = {}
            #=====================================================
            # Create/Patch Storage Aggregates
            #=====================================================
            uri = 'storage/aggregates'
            storageAggs = get(uri, pargs, **kwargs)
            agg         = deepcopy(i.name)
            aggregate   = agg.replace('-', '_') + '_1'
            method = 'post'
            if storageAggs.get('records'):
                for s in storageAggs['records']:
                    if s['name'] == aggregate:
                        agg_uuid = s['uuid']
                        method = 'patch'
            if method == 'patch': uri = f'storage/aggregates/{agg_uuid}'
            else: 'storage/aggregates'
            polVars = deepcopy(i['storage_aggregates'][0])
            polVars.update({"node": {"name": i['name']}})
            payload = json.dumps(polVars)
            if print_payload: print(json.dumps(polVars, indent=4))
            jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
            uri = 'storage/aggregates'
            storageAggs = get(uri, pargs, **kwargs)
            for s in storageAggs['records']:
                if s['name'] == aggregate:
                    pargs.netapp[i['name']]['aggregates'].update({"name":aggregate,"uuid":s['uuid']})
            #=====================================================
            # Update Interfaces on the Nodes
            #=====================================================
            uri = f'network/ethernet/ports?node.name={i.name}'
            ethernetPorts = get(uri, pargs, **kwargs)
            method = 'post'
            #=====================================================
            # See if LAG already exists
            #=====================================================
            for s in ethernetPorts['records']:
                if s['name'] == 'a0a':
                    method = 'patch'
                    pargs.netapp[i['name']].interfaces.update({s['name']:s['uuid']})
            #=====================================================
            # Lookup the Data Ports
            #=====================================================
            for dp in pargs.netapp.data_ports:
                for s in ethernetPorts['records']:
                    if s['name'] == dp: pargs.netapp[i['name']].interfaces.update({dp:s['uuid']})
            #=====================================================
            # Create/Patch the LAG - a0a
            #=====================================================
            uri = 'network/ethernet/ports'
            if method == 'patch': uri = f'network/ethernet/ports/{pargs.netapp[i.name].interfaces["a0a"]}'
            else: 'network/ethernet/ports'
            polVars = deepcopy(i['interfaces']['lacp'][0])
            polVars.update({"node": {"name":i['name']}})
            polVars['broadcast_domain'].update({"uuid": pargs.netapp.broadcast_domains[polVars['broadcast_domain']['name']]})
            for dp in polVars['lag']['member_ports']:
                dp.update({
                    "uuid": pargs.netapp[i['name']].interfaces[dp['name']],
                    "node": {"name": i['name']}
                })
            if method == 'patch':
                polVars['lag'].pop('distribution_policy')
                polVars['lag'].pop('mode')
                polVars.pop('node')
                polVars.pop('type')
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
                if s['name'] == 'a0a':
                    s['uuid']
                    pargs.netapp[i['name']].interfaces.update({'a0a': s['uuid']})
            #=====================================================
            # Create/Patch the VLAN Interfaces for the LAG
            #=====================================================
            uri = f'network/ethernet/ports?fields=node,type,vlan&node.name={i.name}'
            ethernetPorts = get(uri, pargs, **kwargs)
            for x in i['interfaces']['vlan']:
                uri = 'network/ethernet/ports'
                method = 'post'
                polVars = deepcopy(x)
                polVars['broadcast_domain'].update({
                    "uuid": pargs.netapp.broadcast_domains[polVars['broadcast_domain']['name']]
                })
                polVars.update({"node": i['name']})
                polVars['vlan']['base_port'].update({
                    "node": {"name": i['name']},
                    "uuid": pargs.netapp[i['name']].interfaces['a0a']
                })
                for s in ethernetPorts['records']:
                    if s['type'] == 'vlan':
                        if s['vlan']['base_port']['name'] == 'a0a' and s['vlan']['tag'] == x['vlan']['tag']:
                            method = 'patch'
                            uri = f'network/ethernet/ports/{s["uuid"]}'
                            polVars.pop('node')
                            polVars.pop('type')
                            polVars.pop('vlan')
                payload = json.dumps(polVars)
                if print_payload: print(json.dumps(polVars, indent=4))
                intf_name = f'a0a-{x["vlan"]["tag"]}'
            uri = f'network/ethernet/ports?fields=node,type,vlan&node.name={i.name}'
            intfData = get(uri, pargs, **kwargs)
            for x in i['interfaces']['vlan']:
                for s in intfData['records']:
                    if s['type'] == 'vlan':
                        if s['vlan']['tag'] == x['vlan']['tag']:
                            pargs.netapp[i['name']].interfaces.update({intf_name:s['uuid']})
        #=====================================================
        # Delete Default-* Broadcast Domains
        #=====================================================
        uri = '/network/ethernet/broadcast-domains'
        bDomains = get(uri, pargs, **kwargs)
        for i in bDomains['records']:
            if 'Default-' in i['name']:
                uri = f'network/ethernet/broadcast-domains/{i["uuid"]}'
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
        uri = 'support/snmp/users'
        jsonData = get(uri, pargs, **kwargs)
        for polVars in pargs.item['users']:
            patch_user = False
            if jsonData.get('records'):
                for s in jsonData['records']:
                    if polVars['name'] == s['name']:
                        engine_id = s['engine_id']
                        patch_user = True
            if patch_user == True:
                uri = uri + f"/{engine_id}/{s['name']}"
                method = 'patch'
            else: method = 'post'
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
            for s in jsonData['records']:
                if s['host'] == polVars['host']:
                    method = 'patch'
                    uri = uri + f"/{s['uuid']}"
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
        config_vserver = False
        if config_vserver == True:
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
            node01  = deepcopy(pargs.netapp.node01)
            rootv   = (svm.replace('-', '_')) + '_root'
            svmcount = 0
            child.sendline('vserver show')
            child.expect(hostPrompt)
            for line in host_file:
                if re.search(f'{svm}[ ]+data', line): svmcount += 2
                elif re.search(svm, line): svmcount += 1
                elif re.search('data', line): svmcount += 1
            if not svmcount < 2:
                cmd = f'vserver create -vserver {svm} -rootvolume {rootv} -rootvolume-security-style unix'
                child.sendline(cmd)
                child.expect(hostPrompt)
            #=====================================================
            # Configure Aggregates
            #=====================================================
            agg1 = deepcopy(pargs.netapp.node01).replace('-', '_') + '_1'
            agg2 = deepcopy(pargs.netapp.node02).replace('-', '_') + '_1'
            cmd = f'vserver modify {svm} -aggr-list {agg1},{agg2}'
            cmd = f'security login banner modify -vserver {svm} -message "{pargs.netapp.banner}"'
            child.expect(hostPrompt)
            child.sendline('exit')
            child.expect('closed')
        for i in pargs.item:
            i = DotMap(deepcopy(i))
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
                for d in intfData['records']:
                    if d['name'] == intf.name:
                        uri = uri + '/' + d['uuid']
                        method = 'patch'
                if method == 'patch':
                    polVars.pop('scope')
                    polVars.pop('svm')
                    if re.search('(iscsi|nvme)', polVars['name']):
                        polVars['location'].pop('home_node')
                        polVars['location'].pop('home_port')
                payload = json.dumps(polVars)
                if print_payload: print(json.dumps(polVars, indent=4))
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
                    for d in intfData['records']:
                        if d['name'] == intf.name:
                            uri = uri + '/' + d['uuid']
                            method = 'patch'
                    if method == 'patch':
                        polVars.pop('data_protocol')
                        polVars.pop('svm')
                    payload = json.dumps(polVars)
                    if print_payload: print(json.dumps(polVars, indent=4))
                    jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
            uri = 'network/fc/interfaces?fields=wwnn,wwpn'
            intfData = get(uri, pargs, **kwargs)
            fcp_temp = pargs.netapp.fcp_ports
            half = len(fcp_temp)//2
            pargs.netapp['a']['wwpns'] = []
            pargs.netapp['b']['wwpns'] = []
            for d in intfData['records']:
                for s in fcp_temp[:half]:
                    print(s)
                    print(d['name'])
                    if s in d['name']:
                        pargs.netapp['a']['wwpns'].append(d['wwpn'])
                for s in fcp_temp[half:]:
                    if s in d['name']:
                        pargs.netapp['b']['wwpns'].append(d['wwpn'])
            print(pargs.netapp['a'])
            print(pargs.netapp['b'])
            exit()
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
            svmData = get(uri, pargs, **kwargs)
            pargs.netapp.svms.update({pargs.netapp.cluster:svmData['uuid']})
            #=====================================================
            # Create/Patch Infra SVM
            #=====================================================
            #polVars = deepcopy(i.toDict())
            #polVars.pop('data_interfaces')
            #polVars.pop('dns')
            #polVars.pop('routes')
            #if polVars.get('fcp_interfaces'): polVars.pop('fcp_interfaces')
            #payload = json.dumps(polVars)
            #if print_payload: print(json.dumps(polVars, indent=4))
            #jsonData = eval(f"{method}(uri, pargs, payload, **kwargs)")
            #uri = 'svm/svms'
            #svmData = get(uri, pargs, **kwargs)
            #for s in svmData['records']:
            #    s = DotMap(deepcopy(s))
            #    if s.name == i.name:
            #        pargs.netapp.svms.update({i.name:s.uuid})
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
                "vstorage_enabled": False,
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
                if s.get('svm'):
                    if s['svm']['uuid'] == pargs.netapp.svms[i.name]:
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
            for intf in i['data_interfaces']:
                intf = DotMap(deepcopy(intf))
                print(intf)
                exit()
            def configure_interfaces(x, pargs, **kwargs):
                if pargs.method == 'post':
                    if re.search('(iscsi|nvme)', pargs.vconfig['type']):
                        pargs.netapp.name = f"{pargs.vconfig['type']}-lif-0{x}{pargs.letter[pargs.vconfig['type']]}"
                if re.search('inband|nfs', pargs.vconfig['type']): ip_address = pargs.vconfig['controller'][x]
                elif re.search('(iscsi|nvme)', pargs.vconfig['type']):
                    if pargs.letter[pargs.vconfig['type']] == 'a':
                        ip_address = pargs.vconfig['controller'][x]
                    else: ip_address = pargs.vconfig['controller'][x+2]
                    if ':' in ip_address: ifamily = 'ipv6'
                    else: ifamily = 'ipv4'
                if 'inband'  == pargs.vconfig['type']: servicePolicy = 'default-management'
                elif 'iscsi' == pargs.vconfig['type']: servicePolicy = 'default-data-iscsi'
                elif 'nfs'   == pargs.vconfig['type']: servicePolicy = 'default-data-files'
                elif 'nvme'  == pargs.vconfig['type']: servicePolicy = 'default-data-nvme-tcp'
                home_port = pargs.netapp.interfaces[node_list[x]][f"a0a-{pargs.vconfig['vlan_id']}"]
                services = 'data_nfs'
                # data-iscsi,data-nfs,data-cifs,data-flexcache,data-nvme-tcp
                if 'inband' == pargs.config['type'] and x == 1: proceed = False
                else: proceed = True
                if proceed == True:
                    polVars = {
                        "enabled": True,
                        "dns_zone": pargs.dns_domains[0],
                        "ip": {
                            "address": ip_address,
                            "family": ifamily,
                            "netmask": pargs.vconfig['prefix']
                        },
                        "location": {
                            "auto_revert": True,
                            "failover": "home_port_only",
                            "home_node": {"name":pargs.node_list[x]},
                            "home_port": {"node":{"name":pargs.node_list[x]},"uuid":home_port},
                        },
                        "name": pargs.netapp.name,
                        "scope": "svm",
                        "services": [services],
                        "svm": {
                            "name": pargs.netapp.data_svm,
                            "uuid": pargs.vserver[pargs.netapp.data_svm]
                        }
                    }
                    payload = json.dumps(polVars)
                    if print_payload: print(json.dumps(polVars, indent=4))
                    jsonData = eval(f'{method}(uri, pargs, payload, **kwargs)')
                if re.search('(iscsi|nvme)', pargs.vconfig['type']):
                    pargs.letter[pargs.vconfig['type']] = chr(ord(pargs.letter[pargs.vconfig['type']])+1)
                return kwargs, pargs
            #=====================================================
            # Configure Infra SVM Interfaces
            #=====================================================
            for x in range(0,len(node_list)):
                pargs.node_list = node_list
                uri = f'network/ip/interfaces?location.home_node.name={node_list[x]}'
                pargs.letter = {'iscsi':'a','nvme':'a'}
                jIntfs = get(uri, pargs, **kwargs)
                for v in pargs.vlans:
                    if re.search('(inband|iscsi|nfs|nvme)', v['type']):
                        pargs.method = 'post'
                        for i in jIntfs['records']:
                            if re.search(f"^{v['type']}-lif-0{x}(a|b)?$", i['name']):
                                pargs.method = 'patch'
                                pargs.netapp.name = i['name']
                                pargs.netapp.interfaces[node_list[x]].update({i['name']:i['uuid']})
                                pargs.uri = f'network/ip/interfaces/{i["uuid"]}'
                                pargs.vconfig = v
                                kwargs, pargs = configure_interfaces(x, pargs, **kwargs)
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

