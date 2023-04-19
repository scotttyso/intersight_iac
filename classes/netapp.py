#!/usr/bin/env python3

from classes import ezfunctions
from copy import deepcopy
from dotmap import DotMap
import ezfunctions
import json
import os
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
    def autosupport(self, i, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section('netapp', self.type)
        for item in i.autosupport:
            apiBody = item.toDict()
            apiBody = json.dumps(apiBody)
            if print_payload: prCyan(json.dumps(apiBody, indent=4))
            uri = 'support/autosupport'
        patch(uri, pargs, apiBody, **kwargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs, pargs


    #=====================================================
    # NetApp AutoSupport Test
    #=====================================================
    def autosupport_test(self, pargs, **kwargs):
        #=====================================================
        # Send Notification
        #=====================================================
        validating.begin_section(self.type, 'netapp')
        #=====================================================
        # Load Variables and Login to Storage Array
        #=====================================================
        pargs.hostname     = pargs.netapp.node01
        pargs.hostPassword = 'netapp_password'
        pargs.host_prompt   = deepcopy(pargs.netapp.host_prompt)
        pargs.username     = pargs.netapp.user
        child, kwargs      = ezfunctions.child_login(pargs, **kwargs)
        print('\n\n')
        svm = pargs.netapp.data_svm
        pargs.count = 2
        pargs.show  = f'autosupport invoke -node * -type all -message "FlexPod ONTAP storage configuration completed"'
        pargs.regex = f"The AutoSupport was successfully invoked on node"
        pargs.cmds = [f" "]
        config_function(child, pargs)
        #=====================================================
        # Close the Child Process
        #=====================================================
        child.sendline('exit')
        child.expect('closed')
        child.close()
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


    #=====================================================
    # NetApp Broadcast Domain Creation
    #=====================================================
    def broadcast_domain(self, i, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section('netapp', self.type)
        #=====================================================
        # Create/Patch the Broadcast Domains
        #=====================================================
        uri  = '/network/ethernet/broadcast-domains?fields=mtu,name'
        bdRes= get(uri, pargs, **kwargs)
        pargs.netapp.broadcast_domains = {}
        print('')
        for bd in i.broadcast_domain:
            prLightPurple(f"  Beginning Configuration for Broadcast Domain {bd.name}")
            polVars = deepcopy(bd)
            method = 'post'
            for r in bdRes['records']:
                r = DotMap(deepcopy(r))
                if bd.name == r.name:
                    if r.mtu == bd.mtu: method = 'skip'
                    else:
                        method = 'patch'
                        uri = f'network/ethernet/broadcast-domains/{r["uuid"]}'
                        polVars.pop('name')
            if method == 'skip':
                prCyan(f"    - Skipping Broadcast Domain {bd.name}.  API Matches Defined Config.")
            if method == 'post': uri = 'network/ethernet/broadcast-domains'
            if re.search('(patch|post)', method):
                payload = json.dumps(polVars)
                if print_payload: prCyan(json.dumps(polVars, indent=4))
                prGreen(f"    * Configuring Broadcast Domain {bd.name}")
                eval(f"{method}(uri, pargs, payload, **kwargs)")
            prLightPurple(f"  Completed Configuration for Broadcast Domain {bd.name}")
        print('')
        uri = '/network/ethernet/broadcast-domains'
        bdRes = get(uri, pargs, **kwargs)
        for bd in i.broadcast_domain:
            bd = DotMap(deepcopy(bd))
            for r in bdRes['records']:
                r = DotMap(deepcopy(r))
                if bd.name == r.name or 'Default' in r.name:
                    pargs.netapp.broadcast_domains.update({r.name:r.uuid})
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs, pargs


    #=====================================================
    # NetApp Cluster Initialization
    #=====================================================
    def cluster_init(self, pargs, **kwargs):
        for i in kwargs['immDict']['orgs'][kwargs['org']]['netapp']['cluster']:
            i = DotMap(deepcopy(i))
            #=====================================================
            # Send Begin Notification
            #=====================================================
            validating.begin_section('netapp', self.type)
            time.sleep(2)
            #=====================================================
            # Load Variables and Login to Storage Array
            #=====================================================
            pargs.hostname   = i.nodes[0].name + '.' + pargs.dns_domains[0]
            pargs.host_prompt= pargs.netapp.cluster[i.name].host_prompt
            pargs.password   = 'netapp_password'
            pargs.username   = pargs.netapp.cluster[i.name].username
            child, kwargs    = ezfunctions.child_login(pargs, **kwargs)
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
                child.expect(pargs.host_prompt)
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
            ctrl_ips = pargs.ooband['controller']
            pargs.count = 2
            pargs.show  = "storage failover hwassist show"
            pargs.regex = "Monitor Status: active"
            pargs.cmds = [
                f"storage failover modify -hwassist-partner-ip {ctrl_ips[2]} -node {i.nodes[0].name}",
                f"storage failover modify -hwassist-partner-ip {ctrl_ips[1]} -node {i.nodes[1].name}",
            ]
            config_function(child, pargs)
            #=====================================================
            # Configure Service Processors
            #=====================================================
            ipcount = 3
            gw   = pargs.ooband.gateway
            mask = pargs.ooband.netmask
            for node in i.nodes:
                spip = pargs.ooband.controller[ipcount]
                pargs.count = 1
                pargs.show  = "system service-processor show"
                pargs.regex = f"online[ ]+true[ ]+[\\d\\.]+[ ]+{spip}"
                pargs.cmds = [f"system service-processor network modify -node {node.name} -address-family IPv4 "\
                    f"-enable true -dhcp none -ip-address {spip} -netmask {mask} -gateway {gw}"]
                config_function(child, pargs)
                ipcount += 1
                #===========================================================
                # Disable Flow Control on Data Ports
                #===========================================================
                for dp in node.data_ports:
                    pargs.count = 1
                    pargs.show  = f"network port show -node {node} -port {dp}"
                    pargs.regex = f"Flow Control Administrative: none"
                    pargs.cmds = [f"network port modify -node {node} -port {dp} -flowcontrol-admin none"]
                    config_function(child, pargs)
                #=====================================================
                # Change Fibre-Channel Port Speeds
                #=====================================================
                for fca in node.fcp_ports:
                    cmdp1 = f'fcp adapter modify -node {node} -adapter {fca}'
                    cmds = [
                        f'{cmdp1} -status-admin down',
                        'sleep',
                        f'{cmdp1} -speed {node.fcp_speed} -status-admin up'
                    ]
                    child.sendline(f'network interface show -curr-port {fca}')
                    check = False
                    cmd_check = False
                    while cmd_check == False:
                        i = child.expect(['There are no entries', 'were displayed', pargs.host_prompt])
                        if i == 0: check = False
                        elif i == 1: check = True
                        elif i == 2: cmd_check = True
                    if check == False:
                        for cmd in cmds:
                            if 'sleep' in cmd: time.sleep(3)
                            else: 
                                child.sendline(cmd)
                                child.expect(pargs.host_prompt)
            #=====================================================
            # Disk Zero Spares
            #=====================================================
            cmd = 'disk zerospares'
            child.sendline(cmd)
            child.expect(pargs.host_prompt)
            cmd = 'disk show -fields zeroing-percent'
            child.sendline(cmd)
            dcount = 0
            zerospares = False
            while zerospares == False:
                i = child.expect([r'\d.\d.[\d]+ [\d]', 'to page down', pargs.host_prompt])
                if i == 0:
                    if dcount == 10: prRed(f'\n**failed on "{cmd}".  Please Check for any issues and restart the wizard.')
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
        validating.end_section('netapp', self.type)
        return kwargs, pargs


    #=====================================================
    # NetApp Cluster Creation
    #=====================================================
    def cluster(self, pargs, **kwargs):
        #=====================================================
        # First Initialize the Clusters
        #=====================================================
        #kwargs, pargs = api('cluster_init').cluster_init(pargs, **kwargs)
        validating.begin_section('netapp', self.type)
        #=====================================================
        # Load Variables and Send Notification
        #=====================================================
        for i in kwargs['immDict']['orgs'][kwargs['org']]['netapp']['cluster']:
            i = DotMap(deepcopy(i))
            validating.begin_loop('cluster', i.name)

            #=====================================================
            # Add NTP Servers
            #=====================================================
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
                if print_payload: prCyan(json.dumps(polVars, indent=4))
                if method == 'post':
                    eval(f"{method}(uri, pargs, payload, **kwargs)")

            #=====================================================
            # Add Cluster Interface
            #=====================================================
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
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            print(f"\n  Configuring Cluster {i.name}")
            eval(f"{method}(uri, pargs, payload, **kwargs)")

            #=====================================================
            # Validate Licenses Exist for Each Protocol
            #=====================================================
            print(f"\n  Validating Licensing for {i.name}")
            uri = 'cluster/licensing/licenses'
            licenseData = get(uri, pargs, **kwargs)
            for p in pargs.netapp.cluster[i.name].protocols:
                license_installed = False
                for r in licenseData['records']:
                    r = DotMap(deepcopy(r))
                    if r.name == p: license_installed = True
                if license_installed == False:
                    prRed(f'\n!!!ERROR!!!\nNo License was found for protocol {p}\n')
                    sys.exit()

            #=====================================================
            # Configure Sub-Sections
            #=====================================================
            item_list = ['autosupport', 'snmp', 'broadcast_domain', 'nodes', 'svm']
            for item in item_list:
                kwargs, pargs = eval(f"api(item).{item}(i, pargs, **kwargs)")

            validating.end_loop('cluster', i.name)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs, pargs


    #=====================================================
    # NetApp Lun Creation
    #=====================================================
    def lun(self, pargs, **kwargs):
        #=====================================================
        # Send Notification
        #=====================================================
        validating.begin_section(self.type, 'netapp')
        #=====================================================
        # iGroup Function
        #=====================================================
        def igroup(polVars, pargs, **kwargs):
            svm    = polVars['svm']['name']
            uri    = f'protocols/san/igroups/?svm.name={svm}'
            jData  = get(uri, pargs, **kwargs)
            method = 'post'
            uri    = 'protocols/san/igroups'
            if jData.get('records'):
                for r in jData['records']:
                    r = DotMap(deepcopy(r))
                    if r.name == polVars['name']:
                        method = 'patch'
                        uri = uri + '/' + r.uuid
                        polVars.pop('initiators')
                        polVars.pop('svm')
                        #for p in pop_list:
                        #    if polVars.get(p): polVars.pop(p)
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            print(f'   {method} SVM {svm} iGroup {polVars["name"]}')
            eval(f"{method}(uri, pargs, payload, **kwargs)")
        #=====================================================
        # Lun Map Function
        #=====================================================
        def lunmap(polVars, pargs, **kwargs):
            svm    = polVars['svm']['name']
            uri    = f'/protocols/san/lun-maps/?svm.name={svm}'
            jData  = get(uri, pargs, **kwargs)
            method = 'post'
            uri    = '/protocols/san/lun-maps'
            exists = False
            for r in jData['records']:
                r = DotMap(deepcopy(r))
                if r.lun.name == polVars['lun']['name']:
                    exists = True
            if exists == False:
                payload = json.dumps(polVars)
                if print_payload: prCyan(json.dumps(polVars, indent=4))
                print(f'   {method} SVM {svm} Lun Map {polVars["lun"]["name"]}')
                eval(f"{method}(uri, pargs, payload, **kwargs)")
        #=====================================================
        # Load Variables and Begin Loop
        #=====================================================
        lun_count = 1
        for i in pargs.items:
            polVars = deepcopy(i)
            i = DotMap(deepcopy(i))
            polVars.pop('lun_type')
            if polVars.get('profile'): polVars.pop('profile')
            if polVars.get('lun_name'): polVars.pop('lun_name')
            #=====================================================
            # Create/Patch Lun(s)
            #=====================================================
            uri    = f'storage/luns/?svm.name={i.svm.name}'
            jData  = get(uri, pargs, **kwargs)
            method = 'post'
            uri    = f'storage/luns'
            for r in jData['records']:
                r = DotMap(deepcopy(r))
                if r.name == i.name:
                    method = 'patch'
                    uri = uri + '/' + r.uuid
                    pop_list = ['name', 'os_type', 'svm']
                    for p in pop_list:
                        if polVars.get(p): polVars.pop(p)
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            print(f'   {method} SVM {i.svm.name} Lun {i.name}')
            eval(f"{method}(uri, pargs, payload, **kwargs)")
            #=====================================================
            # Assign iGroups and Lun Maps for Boot Luns
            #=====================================================
            if 'boot' in i.lun_type:
                grpVars = {
                    'name': i.profile,
                    'initiators': [],
                    'os_type': i.os_type,
                    'svm': i.svm.toDict()
                }
                for k, v in pargs.server_profiles.items():
                    v = DotMap(deepcopy(v))
                    if k == i.profile:
                        if re.search('fc-nvme|fc', pargs.dtype):
                            for x in range(0,len(v.wwpns)):
                                if x % 2 == 0: fab = 'Fabric A'
                                else: fab = 'Fabric B'
                                grpVars['initiators'].append({
                                    "comment": f"{k} {fab}", "name": v.wwpns[x]
                                })
                        else: grpVars['initiators'].append({"comment": k, "name": v.iqn})
                        igroup(grpVars, pargs, **kwargs)
                        mapVars = {
                            "igroup": {"name": k},
                            "logical_unit_number": 0,
                            "lun": {"name": i.name},
                            "svm": i.svm.toDict()
                        }
                        lunmap(mapVars, pargs, **kwargs)
            #=====================================================
            # Assign iGroups and Lun Maps for Data Luns
            #=====================================================
            elif 'data' in i.lun_type:
                grpVars = {
                    'name': i.lun_name,
                    'initiators': [],
                    'os_type': i.os_type,
                    'svm': i.svm.toDict()
                }
                for k, v in pargs.server_profiles.items():
                    v = DotMap(deepcopy(v))
                    if re.search('fc-nvme|fc', pargs.dtype):
                        for x in range(0,len(v.wwpns)):
                            if x % 2 == 0: fab = 'Fabric A'
                            else: fab = 'Fabric B'
                            grpVars['initiators'].append({
                                "comment": f"{k} {fab}", "name": v.wwpns[x]
                            })
                    else: grpVars['initiators'].append({"comment": k, "name": v.iqn})
                igroup(grpVars, pargs, **kwargs)
                mapVars = {
                    "igroup": {"name": i.lun_name},
                    "logical_unit_number": lun_count,
                    "lun": {"name": i.name},
                    "svm": i.svm.toDict()
                }
                lunmap(mapVars, pargs, **kwargs)
            lun_count += 1
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


    #=====================================================
    # NetApp Node Creation
    #=====================================================
    def nodes(self, i, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section('netapp', self.type)
        #=====================================================
        # Get Existing Storage Aggregates
        #=====================================================
        for node in i.nodes:
            validating.begin_section('node', node.name)
            node = DotMap(deepcopy(node))
            pargs.netapp[node.name].interfaces = {}
            pargs.netapp[node.name]['aggregates'] = {}
            #=====================================================
            # Create/Patch Storage Aggregates
            #=====================================================
            prLightPurple(f"\n    Get Existing Storage Aggregates")
            aggregate= node.storage_aggregates[0].name
            method   = 'post'
            uri      = 'storage/aggregates'
            storageAggs = get(uri, pargs, **kwargs)
            if storageAggs.get('records'):
                for r in storageAggs['records']:
                    r = DotMap(deepcopy(r))
                    if r.name == aggregate:
                        method = 'patch'
                        uri = f'storage/aggregates/{r.uuid}'
            polVars = deepcopy(node.storage_aggregates[0])
            polVars.update({"node": {"name": node.name}})
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            prLightPurple(f"\n    Configuring Storage Aggregate {aggregate}")
            eval(f"{method}(uri, pargs, payload, **kwargs)")
            prLightPurple(f"\n    Add Storage Aggregate to Dictionaries")
            uri = 'storage/aggregates'
            storageAggs = get(uri, pargs, **kwargs)
            for r in storageAggs['records']:
                r = DotMap(deepcopy(r))
                if r.name == aggregate:
                    pargs.netapp[node.name]['aggregates'].update({"name":aggregate,"uuid":r.uuid})
            #=====================================================
            # Update Interfaces on the Nodes
            #=====================================================
            prLightPurple(f"\n    Get Existing Ethernet Port Records.")
            uri       = f'network/ethernet/ports?node.name={node.name}'
            ethResults= get(uri, pargs, **kwargs)
            method    = 'post'
            for lacp in node.interfaces.lacp:
                #=====================================================
                # See if LAG and Data Ports already exists
                #=====================================================
                polVars = deepcopy(lacp.toDict())
                for r in ethResults['records']:
                    r = DotMap(deepcopy(r))
                    if r.name == 'a0a':
                        method = 'patch'
                        pargs.netapp[node.name].interfaces.update({r.name:r.uuid})
                    for dp in lacp.lag.member_ports:
                        if r.name == dp.name: pargs.netapp[node.name].interfaces.update({r.name:r.uuid})
                #=====================================================
                # Create/Patch the LAG - a0a
                #=====================================================
                uri = 'network/ethernet/ports'
                if method == 'patch': uri = f'network/ethernet/ports/{pargs.netapp[node.name].interfaces["a0a"]}'
                polVars.update({"node": {"name":node.name}})
                polVars['broadcast_domain'].update(
                    {"uuid": pargs.netapp.broadcast_domains[lacp.broadcast_domain.name]}
                )
                for dp in polVars['lag']['member_ports']:
                    dp.update({
                        "uuid": pargs.netapp[node.name].interfaces[dp['name']],
                        "node": {"name": node['name']}
                    })
                if method == 'patch':
                    pop_list = ['distribution_policy', 'mode']
                    for p in pop_list: polVars['lag'].pop(p)
                    pop_list = ['node', 'type']
                    for p in pop_list: polVars.pop(p)
                payload = json.dumps(polVars)
                if print_payload: prCyan(json.dumps(polVars, indent=4))
                eval(f"{method}(uri, pargs, payload, **kwargs)")
                uri = f'network/ethernet/ports?node.name={node.name}'
                #=====================================================
                # Get UUID For the LAG
                #=====================================================
                ethResults = get(uri, pargs, **kwargs)
                method = 'post'
                for r in ethResults['records']:
                    r = DotMap(deepcopy(r))
                    if r.name == 'a0a': pargs.netapp[node.name].interfaces.update({'a0a': r.uuid})
            #=====================================================
            # Create/Patch the VLAN Interfaces for the LAG
            #=====================================================
            uri = f'network/ethernet/ports?fields=broadcast_domain,node,type,vlan&node.name={node.name}'
            ethResults = get(uri, pargs, **kwargs)
            for v in node.interfaces.vlan:
                intf_name = f'a0a-{v.vlan.tag}'
                prLightPurple(f"\n    Beginning Configuration for VLAN Interface {intf_name}.")
                polVars = deepcopy(v.toDict())
                uri = 'network/ethernet/ports'
                method = 'post'
                polVars['broadcast_domain'].update({
                    "uuid": pargs.netapp.broadcast_domains[v.broadcast_domain.name]
                })
                polVars.update({"node": node.name})
                polVars['vlan']['base_port'].update({
                    "node": {"name": node.name},
                    "uuid": pargs.netapp[node.name].interfaces['a0a']
                })
                for r in ethResults['records']:
                    r = DotMap(deepcopy(r))
                    if r.type == 'vlan':
                        if r.vlan.base_port.name == 'a0a' and r.vlan.tag == v.vlan.tag:
                            method = 'patch'
                            uri = f'network/ethernet/ports/{r.uuid}'
                            polVars.pop('node')
                            polVars.pop('type')
                            polVars.pop('vlan')
                        if r.broadcast_domain.name == v.broadcast_domain.name:
                            if r.vlan.base_port.name == v.vlan.base_port.name:
                                if r.vlan.tag == v.vlan.tag:
                                    method = 'skip'
                if method == 'skip':
                    prCyan(f"      * Skipping VLAN Interface {intf_name}.  API Matches Defined Config.")
                elif re.search('patch|post', method):
                    payload = json.dumps(polVars)
                    if print_payload: prCyan(json.dumps(polVars, indent=4))
                    prGreen(f"    * Configuring VLAN Interface {intf_name}.")
                    eval(f"{method}(uri, pargs, payload, **kwargs)")
                prLightPurple(f"    Completed Configuration for VLAN Interface {intf_name}.")
            print('')
            uri = f'network/ethernet/ports?fields=node,type,vlan&node.name={node.name}'
            intfData = get(uri, pargs, **kwargs)
            for v in node.interfaces.vlan:
                intf_name = f'a0a-{v.vlan.tag}'
                for r in intfData['records']:
                    r = DotMap(deepcopy(r))
                    if r.type == 'vlan':
                        if r.vlan.tag == v.vlan.tag:
                            pargs.netapp[node.name].interfaces.update({intf_name:r.uuid})
            validating.end_section('node', node.name)
        #=====================================================
        # Delete Default-* Broadcast Domains
        #=====================================================
        uri = '/network/ethernet/broadcast-domains'
        bdResults = get(uri, pargs, **kwargs)
        for r in bdResults['records']:
            r = DotMap(deepcopy(r))
            if 'Default-' in r.name:
                uri = f'network/ethernet/broadcast-domains/{r.uuid}'
                delete(uri, pargs, payload, **kwargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs, pargs


    #=====================================================
    # NetApp Schedule Creation
    #=====================================================
    def schedule(self, pargs, svm, **kwargs):
        #=====================================================
        # Load Variables and Send Notification
        #=====================================================
        validating.begin_section('netapp', self.type)
        for e in svm.schedule:
            polVars = deepcopy(e.toDict())
            #=====================================================
            # Create/Patch Schedule
            #=====================================================
            uri    = f'cluster/schedules?svm.name={svm.name}&fields=cluster,cron,svm'
            jData  = get(uri, pargs, **kwargs)
            method = 'post'
            uri    = f'cluster/schedules'
            match_count = 0
            for r in jData['records']:
                r = DotMap(deepcopy(r))
                if r.name == e.name:
                    method = 'patch'
                    uri = uri + '/' + r.uuid
                    polVars.pop('cluster')
                    polVars.pop('name')
                    polVars.pop('svm')
                    if r.cron.minutes[0] == e.cron.minutes[0]: match_count += 1
                    if r.cluster.name == e.cluster: match_count += 1
                    if r.svm.name == e.svm.name: match_count += 1
                    if match_count == 3: method = 'skip'
            if method == 'skip':
                prCyan(f"  - Skipping {svm.name}'s Schedule.")
            else:
                payload = json.dumps(polVars)
                if print_payload: prCyan(json.dumps(polVars, indent=4))
                prGreen(f"  * Configuring {svm.name}'s Schedule.")
                eval(f"{method}(uri, pargs, payload, **kwargs)")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs, pargs


    #=====================================================
    # NetApp SNMP Creation
    #=====================================================
    def snmp(self, i, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section('netapp', self.type)
        #=====================================================
        # Get Auth and Privilege Passwords
        #=====================================================
        kwargs['Variable'] = 'snmp_auth_password'
        kwargs = ezfunctions.sensitive_var_value(**kwargs)
        snmp_auth_password = kwargs['var_value']
        kwargs['Variable'] = 'snmp_priv_password'
        kwargs = ezfunctions.sensitive_var_value(**kwargs)
        snmp_priv_password = kwargs['var_value']
        for snmp in i.snmp:
            #=====================================================
            # Configure SNMP Global Settings
            #=====================================================
            polVars = deepcopy(snmp.toDict())
            polVars.pop('users')
            polVars.pop('traps')
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            uri = 'support/snmp'
            patch(uri, pargs, payload, **kwargs)
            #=====================================================
            # Configure SNMP Users
            #=====================================================
            jData = get(uri, pargs, **kwargs)
            for user in snmp.users:
                userVars = deepcopy(user.toDict())
                method = 'post'
                uri = 'support/snmp/users'
                jData = get(uri, pargs, **kwargs)
                if jData.get('records'):
                    for r in jData['records']:
                        r = DotMap(deepcopy(r))
                        if userVars['name'] == r.name:
                            engine_id = r.engine_id
                            #url = uri + f"/{engine_id}/{r.name}"
                            #delete(url, pargs, **kwargs)
                            method = 'patch'
                if method == 'post':
                    userVars['snmpv3'].update({
                        "authentication_password": snmp_auth_password,
                        "privacy_password": snmp_priv_password,
                    })
                    payload = json.dumps(userVars)
                    if print_payload: print(json.dumps(userVars, indent=4))
                    eval(f"{method}(uri, pargs, payload, **kwargs)")
            #=====================================================
            # Configure SNMP Trap Servers
            #=====================================================
            uri = 'support/snmp/traphosts'
            jData = get(uri, pargs, **kwargs)
            for trap in snmp.traps:
                trapVars = deepcopy(trap.toDict())
                method = 'post'
                uri = 'support/snmp/traphosts'
                jData = get(uri, pargs, **kwargs)
                for r in jData['records']:
                    r = DotMap(deepcopy(r))
                    traphost = ''
                    if r.host == trapVars['host']:
                        method = 'patch'
                        #uri = uri + '/' + r.uuid
                    elif re.search('^[\\d]{1,3}\\.[\\d]{1,3}\\.[\\d]{1,3}\\.[\\d]{1,3}$', trapVars['host']):
                        traphost, alias, addresslist = socket.gethostbyaddr(trapVars['host'])
                        if r.host == traphost:
                            method = 'patch'
                            #uri = uri + '/' + r.uuid
                if method == 'post':
                    payload = json.dumps(trapVars)
                    if print_payload: print(json.dumps(trapVars, indent=4))
                    eval(f"{method}(uri, pargs, payload, **kwargs)")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs, pargs


    #=====================================================
    # NetApp Storage Virtual Machine Creation (vserver)
    #=====================================================
    def svm(self, i, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Notification
        #=====================================================
        validating.begin_section('netapp', self.type)
        #=====================================================
        # Load Variables and Login to Storage Array
        #=====================================================
        pargs.hostname   = i.nodes[0].name + '.' + pargs.dns_domains[0]
        pargs.host_prompt= pargs.netapp.cluster[i.name].host_prompt
        pargs.password   = 'netapp_password'
        pargs.username   = pargs.netapp.cluster[i.name].username
        child, kwargs    = ezfunctions.child_login(pargs, **kwargs)
        host_file = open(f'{pargs.hostname}.txt', 'r')
        
        #=====================================================
        # Using pexpect, configure SVM
        #=====================================================
        for svm in i.svm:
            svm_pexpect(child, host_file, i, pargs, svm)
        
        #=====================================================
        # Close the Child Process and Cleanup Environment
        #=====================================================
        child.sendline('exit')
        child.expect('closed')
        child.close()
        host_file.close()
        os.remove(f'{pargs.hostname}.txt')

        #=====================================================
        # Configure the SVM Through the API
        #=====================================================
        for svm in i.svm:
            #=====================================================
            # Get Existing SVMs
            #=====================================================
            prLightPurple(f"  Obtaining UUID for {svm.name}")
            uri = 'svm/svms'
            jData = get(uri, pargs, **kwargs)
            for r in jData['records']:
                r = DotMap(deepcopy(r))
                if r.name == svm.name:
                    pargs.netapp.cluster[svm.cluster].svm.moid = r.uuid

            #=====================================================
            # Configure Default Route
            #=====================================================
            print('')
            prLightPurple(f"  Beginning {svm.name} Default Route Configuration.")
            uri    = f'network/ip/routes?fields=svm,destination&svm.name={svm.name}'
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
                polVars = svm.routes[0].toDict()
                payload = json.dumps(polVars)
                if print_payload: prCyan(json.dumps(polVars, indent=4))
                prGreen(f"  Configuring {svm.name}'s Default Route.")
                eval(f"{method}(uri, pargs, payload, **kwargs)")
            prLightPurple(f"  Completed {svm.name} Default Route Configuration.")
            print('')

            #=====================================================
            # Configure the vsadmin password and Unlock It
            #=====================================================
            print('')
            prLightPurple(f"  Beginning {svm.name} vsadmin Configuration.")
            kwargs['Variable'] = 'netapp_password'
            kwargs = ezfunctions.sensitive_var_value(**kwargs)
            password = kwargs['var_value']

            uri = f'security/accounts/{pargs.netapp.cluster[svm.cluster].svm.moid}/vsadmin'
            jData = get(uri, pargs, **kwargs)
            r = DotMap(deepcopy(jData))
            if not r.locked == False:
                uri = f'security/accounts/{pargs.netapp.svms[svm.name]}/vsadmin'
                polVars = { "locked": False, "password": password }
                payload = json.dumps(polVars)
                if print_payload: prCyan(json.dumps(polVars, indent=4))
                eval(f"{method}(uri, pargs, payload, **kwargs)")
            prLightPurple(f"  Completed {svm.name} vsadmin Configuration.")
            print('')

            #=====================================================
            # Configure NFS Settings for the SVM
            #=====================================================
            print('')
            prLightPurple(f"  Beginning {svm.name} NFS Settings Configuration.")
            uri    = f'protocols/nfs/services/'
            jData  = get(uri, pargs, **kwargs)
            method = 'post'
            for r in jData['records']:
                r = DotMap(deepcopy(r))
                if r.svm.uuid == pargs.netapp.cluster[svm.cluster].svm.moid:
                    method = 'patch'
                    uri = f'protocols/nfs/services/{pargs.netapp.cluster[svm.cluster].svm.moid}'
            polVars = {
                "protocol": {"v3_enabled": True, "v41_enabled": True},
                "transport": {"udp_enabled": False},
                "vstorage_enabled": True,
                "svm":{ "name": svm.name, "uuid": pargs.netapp.cluster[svm.cluster].svm.moid }
            }
            if method == 'patch': polVars.pop('svm')
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, pargs, payload, **kwargs)")
            prLightPurple(f"  Completed {svm.name} NFS Settings Configuration.")
            print('')

            #=====================================================
            # Disable Weak Security
            # SSH Ciphers and MAC Algorithms
            #=====================================================
            print('')
            prLightPurple(f"  Beginning {svm.name} Security Configuration.")
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
            # Disable Ciphers on Cluster and SVM
            #=====================================================
            uri = 'security/ssh'
            method = 'patch'
            polVars = {"ciphers": cipher_list, "mac_algorithms": mac_algorithms}
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, pargs, payload, **kwargs)")
            uri = f'security/ssh/svms/{pargs.netapp.cluster[svm.cluster].svm.moid}'
            polVars = { "ciphers": cipher_list, "mac_algorithms": mac_algorithms }
            method = 'patch'
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, pargs, payload, **kwargs)")

            #=====================================================
            # Enable FIPS Security
            #=====================================================
            polVars = {"fips": {"enabled": True}}
            uri = 'security'
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            patch(uri, pargs, payload, **kwargs)
            prLightPurple(f"  Completed {svm.name} Security Configuration.")
            print('')
            
            #=====================================================
            # Disable Ciphers and Configure Login Banner - SVM
            #=====================================================
            print('')
            prLightPurple(f"  Beginning {svm.name} Login Banner Configuration.")
            method = 'post'
            uri = f'security/login/messages?fields=svm'
            loginData = get(uri, pargs, **kwargs)
            uri = f'security/login/messages'
            for r in loginData['records']:
                r = DotMap(deepcopy(r))
                if r.get('svm'):
                    if r.svm.uuid == pargs.netapp.cluster[svm.cluster].svm.moid:
                        method = 'patch'
                        uri = uri + '/' + pargs.netapp.cluster[svm.cluster].svm.moid
            polVars = {
                "banner": svm.banner,
                "scope": "svm",
                "show_cluster_message": True,
                "svm": {"name": svm.name, "uuid": pargs.netapp.cluster[svm.cluster].svm.moid}
            }
            if method == 'patch':
                polVars.pop('svm')
                polVars.pop('scope')
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, pargs, payload, **kwargs)")
            prLightPurple(f"  Completed {svm.name} Login Banner Configuration.")
            print('')

            #=====================================================
            # Configure SVM Data Interfaces
            #=====================================================
            uri      = 'network/ip/interfaces?fields=enabled,dns_zone,ip,location,service_policy,svm'
            intfData = get(uri, pargs, **kwargs)
            for intf in svm.data_interfaces:
                intf = DotMap(deepcopy(intf))
                print('')
                prLightPurple(f"  Beginning SVM {svm.name} Interface - {intf.name} Configuration.")
                polVars = deepcopy(intf.toDict())
                polVars['svm'] = {'name':svm.name}
                method   = 'post'
                uri      = 'network/ip/interfaces'
                for r in intfData['records']:
                    r = DotMap(deepcopy(r))
                    if r.name == intf.name:
                        match_count = 0
                        uri = uri + '/' + r.uuid
                        method = 'patch'
                        polVars.pop('scope')
                        polVars.pop('svm')
                        if re.search('(iscsi|nvme)', polVars['name']):
                            polVars['location'].pop('home_node')
                            polVars['location'].pop('home_port')
                        if r.dns_zone == intf.dns_zone: match_count += 1
                        if r.enabled == intf.enabled: match_count += 1
                        if r.ip.address == intf.ip.address: match_count += 1
                        if r.ip.netmask == intf.ip.netmask: match_count += 1
                        if r.location.auto_revert == intf.location.auto_revert: match_count += 1
                        if r.location.failover == intf.location.failover: match_count += 1
                        if r.location.home_node.name == intf.location.home_node.name: match_count += 1
                        if r.location.home_port.name == intf.location.home_port.name: match_count += 1
                        if r.name == intf.name: match_count += 1
                        if r.service_policy.name == intf.service_policy: match_count += 1
                        if r.svm.name == svm.name: match_count += 1
                        if match_count == 11: method = 'skip'
                        if re.search('iscsi|nvme', intf.name):
                            if match_count == 9: method = 'skip'
                if method == 'skip':
                    prCyan(f"    - Skipping {svm.name} Interface - {intf.name}.  Configuration Matches the API.")
                else:
                    payload = json.dumps(polVars)
                    if print_payload: prCyan(json.dumps(polVars, indent=4))
                    prGreen(f"      - Configuring {svm.name} Interface - {intf.name}")
                    eval(f"{method}(uri, pargs, payload, **kwargs)")
                prLightPurple(f"  Completed SVM {svm.name} Interface - {intf.name} Configuration.")
                print('')

            #=====================================================
            # Configure SVM FCP Interfaces
            #=====================================================
            if 'fc' in pargs.dtype:
                uri = 'network/fc/interfaces?fields=enabled,data_protocol,location,svm'
                intfData = get(uri, pargs, **kwargs)
                for intf in svm.fcp_interfaces:
                    intf = DotMap(deepcopy(intf))
                    print('')
                    prLightPurple(f"  Beginning {svm.name} Interface - {intf.name} Configuration.")
                    polVars = deepcopy(intf.toDict())
                    polVars['svm'] = {'name':svm.name}
                    method = 'post'
                    uri = 'network/fc/interfaces'
                    for r in intfData['records']:
                        r = DotMap(deepcopy(r))
                        if r.name == intf.name:
                            match_count = 0
                            uri = uri + '/' + r.uuid
                            method = 'patch'
                            polVars.pop('data_protocol')
                            polVars.pop('svm')
                            if r.data_protocol == intf.data_protocol: match_count += 1
                            if r.enabled == intf.enabled: match_count += 1
                            if r.location.home_port.name == intf.location.home_port.name: match_count += 1
                            if r.location.home_node.name == intf.location.home_port.node.name: match_count += 1
                            if r.name == intf.name: match_count += 1
                            if r.svm.name == svm.name: match_count += 1
                            if match_count == 6: method = 'skip'
                    if method == 'skip':
                        prCyan(f"    - Skipping {svm.name} Interface - {intf.name}.  Configuration Matches the API.")
                    else:
                        payload = json.dumps(polVars)
                        if print_payload: prCyan(json.dumps(polVars, indent=4))
                        prGreen(f"   - Configuring {svm.name} Interface - {intf.name}")
                        eval(f"{method}(uri, pargs, payload, **kwargs)")
                    prLightPurple(f"  Completed {svm.name} Interface - {intf.name} Configuration.")
                    print('')

            #=====================================================
            # Obtain Target Identifier Information
            #=====================================================
            uri = 'network/fc/interfaces?fields=name,wwnn,wwpn'
            intfData = get(uri, pargs, **kwargs)
            fcp_temp = deepcopy(pargs.netapp.cluster[svm.cluster].nodes.fcp_ports)
            half = len(fcp_temp)//2
            pargs.storage[svm.cluster][svm.name].wwpns.a = []
            pargs.storage[svm.cluster][svm.name].wwpns.b = []
            for r in intfData['records']:
                r = DotMap(deepcopy(r))
                for f in fcp_temp[:half]:
                    if f in r.name:
                        pargs.storage[svm.cluster][svm.name].wwpns.a.append({
                            'interface': r.name,
                            'wwpn': r.wwpn
                        })
                for f in fcp_temp[half:]:
                    if f in r.name:
                        pargs.storage[svm.cluster][svm.name].wwpns.b.append({
                            'interface': r.name,
                            'wwpn': r.wwpn
                        })

            #=====================================================
            # Send End Notification and return kwargs
            #=====================================================
            validating.end_loop('svm', svm.name)

            #=====================================================
            # Run Schedule and Volume Loops
            #=====================================================
            sub_list = ['schedule', 'volumes']
            for sub in sub_list:
                kwargs, pargs = eval(f"api(sub).{sub}(pargs, svm, **kwargs)")

        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs, pargs


    #=====================================================
    # NetApp Volumes Creation
    #=====================================================
    def volumes(self, pargs, svm, **kwargs):
        #=====================================================
        # Send Notification
        #=====================================================
        validating.begin_section('netapp', self.type)
        #=====================================================
        # Load Variables and Login to Storage Array
        #=====================================================
        child, kwargs    = ezfunctions.child_login(pargs, **kwargs)
        print('\n\n')
        #=====================================================
        # Loop Thru Volumes
        #=====================================================
        uri    = f'storage/volumes/?svm.name={svm.name}&fields=aggregates,encryption,guarantee,name,nas,size,snapshot_policy,state,style'
        jData  = get(uri, pargs, **kwargs)
        for i in svm.volumes:
            print('')
            prLightPurple(f"  Beginning SVM {svm.name} Volume - {i.name} Configuration.")
            polVars = deepcopy(i.toDict())
            polVars.pop('os_type')
            polVars.pop('volume_type')
            #=====================================================
            # Create/Patch Volumes
            #=====================================================
            method = 'post'
            uri    = f'storage/volumes'
            for r in jData['records']:
                r = DotMap(r)
                if r.name == i.name:
                    method = 'patch'
                    uri = uri + '/' + r.uuid
                    pargs.netapp.volumes[i.name].update({'uuid':r.uuid})
                    pop_list = ['aggregates', 'encryption', 'style', 'svm', 'type']
                    for p in pop_list:
                        if polVars.get(p): polVars.pop(p)
            prGreen(f"    - Configuring Volume {i.name} on {svm.name}.")
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, pargs, payload, **kwargs)")

            #=====================================================
            # Configure Volume Properties from CLI if Needed
            #=====================================================
            volume_pexpect(child, i, pargs, svm)

            prLightPurple(f"  Completed SVM {svm.name} Volume - {i.name} Configuration.")
            print('')
        #=====================================================
        # Initialize the snapmirror
        #=====================================================
        src  = f"{svm.name}:{svm.root_volume.name}"
        pargs.count = 2
        pargs.show  = f"snapmirror show -vserver {svm.name} -source-path {src}"
        pargs.regex = "true"
        pargs.cmds  = [ f"snapmirror initialize-ls-set -source-path {src}" ]
        config_function(child, pargs)
        #=====================================================
        # Close the Child Process
        #=====================================================
        child.sendline('exit')
        child.expect('closed')
        child.close()
        os.remove(f'{pargs.hostname}.txt')

        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs, pargs


#=======================================================
# Build Storage Class
#=======================================================
class build(object):
    def __init__(self, type):
        self.type = type
    #=============================================================================
    # Function - NetApp - AutoSupport
    #=============================================================================
    def autosupport(self, pargs, items, **kwargs):
        #=====================================================
        # Build AutoSupport Dictionary
        #=====================================================
        polVars = {
            'contact_support':True,
            'enabled':True,
            'from':items.autosupport.from_address,
            'is_minimal':False,
            'mail_hosts':items.autosupport.mail_hosts,
            'transport':items.autosupport.transport,
            'to':items.autosupport.to_addresses,
        }
        if items.autosupport.get('proxy_url'):
            if len(items.autosupport.proxy_url) > 5:
                polVars.update({'proxy_url':items.autosupport.proxy_url})

        #=====================================================
        # Return polVars
        #=====================================================
        return [polVars]


    #=============================================================================
    # Function - NetApp - Broadcast Domains
    #=============================================================================
    def broadcast_domain(self, pargs, items, **kwargs):
        #=====================================================
        # Build Broadcast Domain Dictionary
        #=====================================================
        bdomains = []
        for i in pargs.vlans:
            if re.search('(inband|iscsi|nvme|nfs)', i.vlan_type):
                if i.vlan_type == 'inband': mtu = 1500
                else: mtu = 9000
                polVars = { "name": i.name, "mtu": mtu }
                bdomains.append(polVars)
        
        #=====================================================
        # Add Default Policy Variables to immDict
        #=====================================================
        polVars = { "name": "Default", "mtu": 9000}
        bdomains.append(polVars)
        polVars = bdomains

        #=====================================================
        # Return polVars
        #=====================================================
        return polVars


    #=============================================================================
    # Function - NetApp - Cluster
    #=============================================================================
    def cluster(self, pargs, name, items, **kwargs):
        items.name = name
        #=====================================================
        # Build Cluster Dictionary
        #=====================================================
        polVars = dict(
            contact     = items.snmp.contact,
            dns_domains = pargs.dns_domains,
            license     = dict(keys = []),
            location    = items.snmp.location,
            management_interfaces = [
                dict(
                    name = "cluster-mgmt",
                    ip = dict(
                        address = pargs.ooband.controller[0]
                ))
            ],
            name = name,
            name_servers = pargs.dns_servers,
            ntp_servers  = pargs.ntp_servers,
            timezone     = pargs.timezone
        )
        if items.get('licenses'):
            polVars.update({'license':{'keys':[items.licenses]}})

        pargs.netapp.hostname= items.nodes.node01 + '.' + pargs.dns_domains[0]
        pargs.netapp.username= items.username
        ilist = ['autosupport', 'broadcast_domain', 'nodes', 'snmp', 'svm']
        for i in ilist:
            idict = eval(f"build(i).{i}(pargs, items, **kwargs)")
            polVars.update(deepcopy({i:idict}))

        #=====================================================
        # Add Policy Variables to immDict
        #=====================================================
        kwargs['class_path'] = f'netapp,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)

        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - NetApp - Storage Volumes
    #=============================================================================
    def lun(self, pargs, items, **kwargs):
        #=====================================================
        # Build Lun Dictionary
        #=====================================================
        boot_volume = ''
        for k,v in items.svm.volumes:
            if v.type == 'boot': boot_volume = k
        if boot_volume == '':
            prRed('\n\n!!!ERROR!!!\nCould not determine the boot volume.  No Boot Volume found in:\n')
            for k, v in items.svm.volumes: print(f'{k}:{v}')
            sys.exit(1)
        #=====================================================
        # Boot Luns
        #=====================================================
        for k,v in pargs.netapp.volumes.items():
            if v.type == 'boot':
                for i in pargs.server_profiles:
                    polVars = {
                        "name": f"/vol/{k}/{i}",
                        "os_type": f"{v.os_type}",
                        "space":{"guarantee":{"requested": False}, "size":f"128GB"},
                        "svm":{"name":pargs.netapp.data_svm},
                        "lun_type": "boot",
                        "profile": i
                    }
                    #=====================================================
                    # Add Policy Variables to immDict
                    #=====================================================
                    kwargs['class_path'] = f'netapp,{self.type}'
                    kwargs = ezfunctions.ez_append(polVars, **kwargs)
                break
        #=====================================================
        # Build Data Luns
        #=====================================================
        for k, v in pargs.netapp.volumes.items():
            if re.search('(data|swap)', str(v.type)):
                polVars = {
                    "name": f"/vol/{k}/{k}",
                    "os_type": f"{v.os_type}",
                    "space":{"guarantee":{"requested": False}, "size":f"{v.size}GB"},
                    "svm":{"name":pargs.netapp.data_svm},
                    "lun_type": v.type,
                    "lun_name": k
                }

                #=====================================================
                # Add Policy Variables to immDict
                #=====================================================
                kwargs['class_path'] = f'netapp,{self.type}'
                kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs

    #=============================================================================
    # Function - NetApp - Nodes
    #=============================================================================
    def nodes(self, pargs, items, **kwargs):
        #==================================
        # Get Disk Information
        #==================================
        uri       = 'storage/disks'
        jData     = get(uri, pargs, **kwargs)
        disk_count= jData['num_records'] - 1
        #disk_name = jData['records'][0]['name']
        #uri   = f'storage/disks/{disk_name}'
        #jData = get(uri, pargs, **kwargs)
        #pargs.netapp.disk_type = jData['type'].upper()

        #=====================================================
        # Build Node Dictionary
        #=====================================================
        node_list = items.nodes.node_list
        nodes = []
        for x in range(0,len(node_list)):
            aggr = items.svm[f'agg{x+1}']
            polVars = {'interfaces': {'lacp':[], 'vlan':[]}, 'name': node_list[x], 'storage_aggregates': []}
            aggregate = { "block_storage": {"primary": {"disk_count": disk_count}}, "name": aggr }
            polVars['storage_aggregates'].append(aggregate)

            #=====================================================
            # Add Data Port-Channel
            #=====================================================
            aggPort = {
                "broadcast_domain": {"name": "Default"},
                "enabled": True,
                "lag": { "mode": "multimode_lacp", "distribution_policy": "mac", "member_ports": []},
                "type": "lag"
            }
            for i in items.nodes.data_ports:
                aggPort['lag']['member_ports'].append({"name": i})
            polVars['interfaces']['lacp'].append(aggPort)

            #=====================================================
            # Add FCP Ports if used
            #=====================================================
            if re.search('(fc|fc-nvme)', pargs.dtype):
                polVars['interfaces'].update({'fcp':[]})
                for i in items.nodes.fcp_ports:
                    fcpPort = { "enabled": True, "name": i, "speed": {"configured": items.nodes.fcp_speed} }
                    polVars['interfaces']['fcp'].append(fcpPort)
            for i in pargs.vlans:
                if re.search('(inband|nfs|iscsi|nvme)', i.vlan_type):
                    vlanPort = {
                        "broadcast_domain": {"name": i.name},
                        "type": "vlan",
                        "vlan": { "base_port": {"name": 'a0a'}, "tag": i.vlan_id }
                    }
                    polVars['interfaces']['vlan'].append(vlanPort)
            nodes.append(polVars)
            polVars = nodes

        #=====================================================
        # Return polVars
        #=====================================================
        return polVars


    #=============================================================================
    # Function - NetApp - Schedulers
    #=============================================================================
    def schedule(self, items):
        #=====================================================
        # Build Schedule Dictionary
        #=====================================================
        polVars = [{
            "cluster": items.name,
            "cron": {"minutes":[15]},
            "name": "15min",
            "svm":{"name":items.svm.name}
        }]
        return polVars


    #=============================================================================
    # Function - NetApp - SNMP
    #=============================================================================
    def snmp(self, pargs, items, **kwargs):
        #=====================================================
        # Build SNMP Dictionary
        #=====================================================
        polVars = {
            "auth_traps_enabled": True,
            "enabled": True,
            "traps_enabled": True,
            "trigger_test_trap": True,
            "traps": [{
                "host": items.snmp.trap_server,
                "user": { "name": items.snmp.username }
            }],
            "users": [{
                "authentication_method": "usm",
                "name": items.snmp.username,
                "owner": {"name": items.name},
                "snmpv3": {
                    "authentication_protocol": "sha",
                    "privacy_protocol": "aes128"
                }
            }]
        }

        #=====================================================
        # Return polVars
        #=====================================================
        return [polVars]


    #=============================================================================
    # Function - NetApp - SVM
    #=============================================================================
    def svm(self, pargs, items, **kwargs):
        #=====================================================
        # Create Infra SVM
        #=====================================================
        polVars = {
            "aggregates": [ {"name": items.svm.agg1}, {"name": items.svm.agg2} ],
            "banner": items.banner,
            "cluster": items.name,
            "name": items.svm.name,
            "dns":{"domains": pargs.dns_domains, "servers": pargs.dns_servers},
            "root_volume": {
                "name": items.svm.rootv,
                'mirrors':[
                    items.svm.m01,
                    items.svm.m02
                ]
            },
            "routes": [{
                "destination": {
                    "address":'0.0.0.0',
                    "netmask": 0
                },
                "gateway": pargs.inband.gateway,
                "svm": {"name": items.svm.name}
            }]
        }
        polVars['protocols'] = {}
        for p in items.protocols: polVars['protocols'].update({p:{"allowed": True, "enabled": True}})

        #=====================================================
        # Configure Ethernet Interfaces
        #=====================================================
        polVars['data_interfaces'] = []
        for v in pargs.vlans:
            for x in range(0,len(items.nodes.node_list)):
                if re.search('(inband|iscsi|nfs|nvme)', v.vlan_type):
                    if re.search('(inband|nfs)', v.vlan_type):
                        pargs.netapp.intf_name = f"{v.vlan_type}-lif-0{x+1}-a0a-{v.vlan_id}"
                    elif re.search('(iscsi|nvme)', v.vlan_type):
                        pargs.netapp.intf_name = f"{v.vlan_type}-lif-0{x+1}-a0a-{v.vlan_id}"
                    pargs.vlan_settings = deepcopy(v)
                    pargs = configure_interfaces(x, items, pargs)
                    if len(pargs.polVars) > 0:
                        polVars['data_interfaces'].append(pargs.polVars)

        #=====================================================
        # Configure Fibre-Channel if in Use
        #=====================================================
        if re.search('fc(-nvme)?', pargs.dtype):
            polVars['fcp_interfaces'] = []
            if pargs.dtype == 'fc':
                pargs.netapp.data_protocol = 'fcp'
                pargs = configure_fcports(x, items, pargs)
                polVars['fcp_interfaces'].extend(pargs.polVars)
            else:
                fcp_temp = pargs.netapp.fcp_ports
                half = len(fcp_temp)//2
                pargs.netapp.fcp_ports = fcp_temp[:half]
                pargs.netapp.data_protocol = 'fcp'
                pargs = configure_fcports(x, items, pargs)
                polVars['fcp_interfaces'].extend(pargs.polVars)
                pargs.netapp.fcp_ports = fcp_temp[half:]
                pargs.netapp.data_protocol = pargs.dtype
                pargs = configure_fcports(x, items, pargs)
                polVars['fcp_interfaces'].extend(pargs.polVars)

        #=====================================================
        # Add Schedule and Volumes to SVM
        #=====================================================
        ilist = ['schedule', 'volumes']
        for i in ilist:
            idict = eval(f"build(i).{i}(items)")
            polVars.update({i:idict})

        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return [polVars]


    #=============================================================================
    # Function - NetApp - Storage Volumes
    #=============================================================================
    def volumes(self, items):
        #=====================================================
        # Add Mirror Volumes
        #=====================================================
        volList = []
        for x in range(0,len(items.nodes.node_list)):
            name =items.svm[f'm0{x+1}']
            volList.append({
                "aggregate": items.svm[f'agg{x+1}'],
                "name": name,
                "size": 1,
                "os_type": "netapp",
                "type": "DP",
                "volume_type": "mirror"
            })
        #=====================================================
        # Volume Input Dictionary
        #=====================================================
        jDict = sorted(items.svm.volumes, key=lambda ele: ele.size, reverse=True)
        for x in range(0,len(jDict)):
            volDict = DotMap(jDict[x])
            if x % 2 == 0: agg = items.svm.agg1
            else: agg = items.svm.agg2
            volList.append({
                "aggregate": agg,
                "name": volDict.name,
                "os_type": volDict.os_type,
                "size": volDict.size,
                "type": "rw",
                "volume_type": volDict.volume_type
            })

        #=====================================================
        # Build Volume Dictionary
        #=====================================================
        volumeList = []
        for i in volList:
            i = DotMap(deepcopy(i))
            if 'm0' in i.name: path = ''
            else: path = i.name
            polVars = {
                "aggregates": [{"name": i.aggregate}],
                "encryption": {"enabled": False},
                "name": i.name,
                "guarantee": {"type": "none"},
                "nas": {
                    "path": f"/{path}",
                    "security_style": "unix",
                },
                "os_type": i.os_type,
                "size": f"{i.size}GB",
                "snapshot_policy": "none",
                "state": "online",
                "style": "flexvol",
                "svm":{"name":items.svm.name},
                "type":i.type,
                "volume_type":i.volume_type
            }
            volumeList.append(polVars)
        polVars = volumeList

        #=====================================================
        # Return polVars
        #=====================================================
        return polVars


#=====================================================
# Function - API Authentication
#=====================================================
def auth(pargs, section='', **kwargs):
    url      = f"https://{pargs.netapp.hostname}"
    username = pargs.netapp.username
    kwargs['Variable'] = 'netapp_password'
    kwargs = ezfunctions.sensitive_var_value(**kwargs)
    password = kwargs['var_value']
    s = requests.Session()
    s.auth = (username, password)
    auth = ''
    while auth == '':
        try:
            auth = s.post(url, verify=False)
        except requests.exceptions.ConnectionError as e:
            prRed("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            prRed("!!!ERROR!!! Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)
    return s, url

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
        i = child.expect(["to page down", pargs.regex, pargs.host_prompt], timeout=20)
        if i == 0: child.send(' ')
        elif i == 1: count += 1
        elif i == 2: cmd_check = True
    if not count == pargs.count:
        for cmd in pargs.cmds:
            child.sendline(cmd)
            cmd_check = False
            while cmd_check == False:
                i = child.expect(["Do you want to continue", pargs.host_prompt])
                if i == 0: child.sendline('y')
                elif i == 1: cmd_check = True
        time.sleep(3)
        child.sendline(pargs.show)
        count = 0
        cmd_check = False
        while cmd_check == False:
            i = child.expect(["to page down", pargs.regex, pargs.host_prompt])
            if i == 0: child.send(' ')
            if i == 1: count += 1
            elif i == 2: cmd_check = True
        if not count == pargs.count:
            print(pargs.message)
            sys.exit(1)

#=====================================================
# Configure FCP Ports
#=====================================================
def configure_fcports(x, items, pargs):
    pargs.polVars = []
    for i in items.nodes.fcp_ports:
        for x in range(0,len(items.nodes.node_list)):
            if pargs.netapp.data_protocol == 'fc-nvme': name = f'fcp-nvme-lif-0{x+1}-{i}'
            else: name = f'fcp-lif-0{x+1}-{i}'
            pVars = {
                "data_protocol": pargs.netapp.data_protocol,
                "enabled": True,
                "location": {
                    "home_port": {"name":i, "node":{"name": items.nodes.node_list[x]}},
                },
                "name": name,
            }
            pargs.polVars.append(pVars)

    return pargs

#=====================================================
# Function - Configure Infra SVM Interfaces
#=====================================================
def configure_interfaces(x, items, pargs):
    ip_address = pargs.vlan_settings['controller'][x]
    if 'inband'  == pargs.vlan_settings.vlan_type: servicePolicy = 'default-management'
    elif 'iscsi' == pargs.vlan_settings.vlan_type: servicePolicy = 'default-data-iscsi'
    elif 'nfs'   == pargs.vlan_settings.vlan_type: servicePolicy = 'default-data-files'
    elif 'nvme'  == pargs.vlan_settings.vlan_type: servicePolicy = 'default-data-nvme-tcp'
    home_port = f"a0a-{pargs.vlan_settings.vlan_id}"
    services = 'data_nfs'
    if 'inband' == pargs.vlan_settings.vlan_type and x == 1: proceed = False
    else: proceed = True
    if proceed == True:
        pargs.polVars = {
            "enabled": True,
            "dns_zone": pargs.dns_domains[0],
            "ip": { "address": ip_address, "netmask": pargs.vlan_settings.prefix },
            "location": {
                "auto_revert": True,
                "failover": "home_port_only",
                "home_node": {"name": items.nodes.node_list[x]},
                "home_port": {"name": home_port, "node":{"name": items.nodes.node_list[x]}},
            },
            "name": pargs.netapp.intf_name,
            "scope": "svm",
            "service_policy": servicePolicy,
        }
        if re.search('iscsi|nfs|nvme', pargs.vlan_settings.vlan_type):
            vtype = pargs.vlan_settings.vlan_type
            if not pargs.storage[items.name][items.svm.name].get(vtype):
                pargs.storage[items.name][items.svm.name][vtype]['interfaces'] = []
            pargs.storage[items.name][items.svm.name][vtype]['interfaces'].append(DotMap(
                interface = pargs.netapp.intf_name,
                ip_address= ip_address,
            ))
    if re.search('(iscsi|nvme)', pargs.vlan_settings.vlan_type):
        pargs.polVars['location'].pop('auto_revert')
        pargs.polVars['location'].pop('failover')
    return pargs

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
                prRed(f"delete: {r.status_code} success with {uri}")
                #print(r.text)
            if r.status_code == 200 or r.status_code == 404:
                return r.json()
            else: validating.error_request_netapp('delete', r.status_code, r.text, uri)
        except requests.exceptions.ConnectionError as e:
            prRed("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            prRed("!!!ERROR!!! Method %s Failed. Exception: %s" % (section[:-5], e))
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
                prPurple(f"     * get: {r.status_code} success with {uri}")
                #print(r.text)
            if r.status_code == 200 or r.status_code == 404:
                return r.json()
            else: validating.error_request_netapp('get', r.status_code, r.text, uri)
        except requests.exceptions.ConnectionError as e:
            prRed("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            prRed("!!!ERROR!!! Method %s Failed. Exception: %s" % (section[:-5], e))
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
                prPurple(f"     * patch: {r.status_code} success with {uri}")
            return r.json()
        except requests.exceptions.ConnectionError as e:
            prRed("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            prRed("!!!ERROR!!! Method %s Failed. Exception: %s" % (section[:-5], e))
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
                prPurple(f"     * post: {r.status_code} success with {uri}")
            return r.json()
        except requests.exceptions.ConnectionError as e:
            prRed("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            prRed("!!!ERROR!!! Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

#=====================================================
# Function - SVM pexpect Process
#=====================================================
def svm_pexpect(child, host_file, i, pargs, svm):
    svmcount = 0
    child.sendline('vserver show')
    child.expect(pargs.host_prompt)
    for line in host_file:
        if re.search(f'{svm.name}[ ]+data', line): svmcount += 2
        elif re.search(svm.name, line): svmcount += 1
        elif re.search('data', line): svmcount += 1
    if not svmcount >= 2:
        cmd = f'vserver create -vserver {svm.name} -rootvolume {svm.root_volume.name} -rootvolume-security-style unix'
        child.sendline(cmd)
        child.expect(pargs.host_prompt)

    #=====================================================
    # Configure Aggregates and add Login Banner
    #=====================================================
    cmds = [
        f'vserver modify {svm.name} -aggr-list {svm.aggregates[0].name},{svm.aggregates[1].name}',
        f'security login banner modify -vserver {svm.name} -message "{i.banner}"'
    ]
    for cmd in cmds:
        child.sendline(cmd)
        child.expect(pargs.host_prompt)

    #=====================================================
    # Limit the Protocols assigned to the SVM
    #=====================================================
    child.sendline(f'vserver show -vserver {svm.name} -protocols')
    child.expect(f'{svm.name}[ ]+([\\w].*[\\w])[  ]')
    protocols = (((child.match).group(1)).strip()).split(',')
    child.expect(pargs.host_prompt)
    protos = list(svm.protocols.keys())
    if 'nvme_of' in protos:
        protos.remove('nvme_of')
        protos.append('nvme')
    child.sendline(f'vserver add-protocols -protocols {",".join(protos)} -vserver {svm.name}')
    child.expect(pargs.host_prompt)
    removep = []
    for p in protocols:
        p = p.strip()
        if not p in protos: removep.append(p)
    if len(removep) > 0:
        child.sendline(f'vserver remove-protocols -vserver {svm.name} -protocols {",".join(removep)}')
        child.expect(pargs.host_prompt)

    #=====================================================
    # Function to Configure Protocols
    #=====================================================
    def config_protocols(child, pargs):
        pargs.message = f'\n{"-"*81}\n\n  !!! ERROR !!!!\n  **failed on "{pargs.show}".\n'\
            f'    Looking for regex "{pargs.regex1}".\n'\
            f'    Looking for regex "{pargs.regex2}".\n'\
            f'    Looking for regex "{pargs.regex3}".\n'\
            f'\n  Please Validate {svm.name} and restart this wizard.\n\n{"-"*81}\n'
        child.sendline(pargs.show)
        change = 'none'
        value  = ''
        cmd_check = False
        while cmd_check == False:
            i = child.expect(["to page down", pargs.regex1, pargs.regex2, pargs.regex3, pargs.host_prompt], timeout=20)
            if i == 0: child.send(' ')
            elif i == 1: change = 'create'
            elif i == 2: change = 'modify'
            elif i == 3: value = (child.match).group(1)
            elif i == 4: cmd_check = True
        if not change == 'none':
            child.sendline(f"vserver {pargs.p} {change} -vserver {svm.name} -status-admin up",)
            cmd_check = False
            while cmd_check == False:
                i = child.expect(["Do you want to continue", pargs.host_prompt])
                if i == 0: child.sendline('y')
                elif i == 1: cmd_check = True
            time.sleep(10)
            child.sendline(pargs.show)
            change = 'none'
            cmd_check = False
            while cmd_check == False:
                i = child.expect(["to page down", pargs.regex1, pargs.regex2, pargs.regex3, pargs.host_prompt])
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
            pargs.show   = f"vserver {p} show -vserver {svm.name}"
            pargs.regex1 = "There are no entries matching your query"
            pargs.regex2 = "Administrative Status: down"
            if 'fcp' in p: pargs.regex3 = "Target Name: (([\\da-f]{2}:){7}[\\da-f]{2})"
            elif 'iscsi' in p: pargs.regex3 = "(iqn\\.[\\da-z\\.:\\-]+vs\\.[\\d]+(?=[\r\n]))"
            elif 'nvme' in p: pargs.regex3 = "NQN: (nqn\\..*discovery)"
            pargs.p = p
            value = config_protocols(child, pargs)
            if 'iscsi' in p: pargs.storage[svm.cluster][svm.name]['iscsi'].iqn = value
            elif 'nvme' in p: pargs.storage[svm.cluster][svm.name]['nvme'].nqn = value

    #=====================================================
    # Configure NFS Export Policy
    #=====================================================
    cmdp = f'vserver export-policy rule METHOD -vserver {svm.name} -policyname default -protocol nfs -ruleindex 1'
    rules = '-rorule sys -rwrule sys -superuser sys -allow-suid true'
    pargs.count = 1
    pargs.show  = cmdp.replace('METHOD', 'show')
    pargs.regex = pargs.nfs.network
    pargs.cmds  = [f"{cmdp.replace('METHOD', 'create')} -clientmatch {pargs.nfs.network} {rules}"]
    config_function(child, pargs)


#=====================================================
# Function - Volume pexpect Process
#=====================================================
def volume_pexpect(child, i, pargs, svm):
    if i.volume_type == 'audit':
        pargs.count = 1
        pargs.show  = f"vserver audit show -vserver {i.svm.name}"
        pargs.regex = f"Log Destination Path"
        pargs.cmds = [f"vserver audit create -vserver {i.svm.name} -destination /{i.name}"]
        config_function(child, pargs)
        pargs.count = 1
        pargs.show  = f"vserver audit show -vserver {i.svm.name}"
        pargs.regex = f"Auditing State: true"
        pargs.cmds = [f"vserver audit enable -vserver {i.svm.name}"]
        config_function(child, pargs)
    elif re.search('_m0[1-2]$', i.name):
        #=====================================================
        # Attach the Mirrors to the Schedule and Initialize
        #=====================================================
        dest = f"{i.svm.name}:{i.name}"
        src  = f"{i.svm.name}:{svm.root_volume.name}"
        pargs.count = 1
        pargs.show  = f"snapmirror show -vserver {i.svm.name} -destination-path {dest} -source-path {src}"
        pargs.regex = f"Destination Path: {svm.cluster}://{i.svm.name}/{i.name}"
        pargs.cmds  = [
            f"snapmirror create -vserver {i.svm.name} -destination-path {dest} -source-path {src} -type LS -schedule 15min"
        ]
        config_function(child, pargs)
    elif i.volume_type == 'nvme':
        pargs.count = 1
        pargs.show  = f"vserver nvme namespace show -vserver {i.svm.name} -path /vol/{i.name}/{i.name}"
        pargs.regex = f"online"
        pargs.cmds = [f"vserver nvme namespace create -vserver {i.svm.name} -path /vol/{i.name}/{i.name}"]
        config_function(child, pargs)
        pargs.count = 1
        pargs.show  = f"vserver nvme subsystem show -vserver {i.svm.name} -subsystem {i.os_type}-hosts"
        pargs.regex = f"OS Type: {i.os_type}"
        pargs.cmds = [
            f"vserver nvme subsystem create -vserver {i.svm.name} -subsystem {i.os_type}-hosts -ostype {i.os_type}"
        ]
        config_function(child, pargs)
        pargs.count = 1
        pargs.show  = f"vserver nvme subsystem map show -vserver {i.svm.name} -path /vol/{i.name}/{i.name} -subsystem {i.os_type}-hosts"
        pargs.regex = f"NSID"
        pargs.cmds = [
            f"vserver nvme subsystem map add -vserver {i.svm.name} -path /vol/{i.name}/{i.name} -subsystem {i.os_type}-hosts"
        ]
        config_function(child, pargs)
    elif i.volume_type == 'swap':
        pargs.count = 1
        pargs.show  = f"volume efficiency show -vserver {i.svm.name} -volume {i.name}"
        pargs.regex = f"Disabled"
        pargs.cmds = [f"volume efficiency off -vserver {i.svm.name} -volume {i.name}"]
        config_function(child, pargs)

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
