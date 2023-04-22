from classes import ezfunctionsv2 as ezfunctions
from classes import validatingv2 as validating
from copy import deepcopy
from dotmap import DotMap
import json
import os
import re
import requests
import socket
import sys
import time
import urllib3
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
    def autosupport(self, i, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section('netapp', self.type)
        for item in i.autosupport:
            payload = item.toDict()
            payload = json.dumps(payload)
            if print_payload: prCyan(json.dumps(payload, indent=4))
            uri = 'support/autosupport'
        patch(uri, kwargs, payload)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs


    #=====================================================
    # NetApp AutoSupport Test
    #=====================================================
    def autosupport_test(self, kwargs):
        #=====================================================
        # Send Notification
        #=====================================================
        validating.begin_section(self.type, 'netapp')
        #=====================================================
        # Load Variables and Login to Storage Array
        #=====================================================
        kwargs.hostname    = kwargs.netapp.node01 + '.' + kwargs.dns_domains[0]
        kwargs.hostPassword= 'netapp_password'
        kwargs.host_prompt = deepcopy(kwargs.netapp.host_prompt)
        kwargs.username    = kwargs.netapp.user
        child, kwargs      = ezfunctions.child_login(kwargs)
        prCyan('\n\n')
        kwargs.count = 2
        kwargs.show  = f'autosupport invoke -node * -type all -message "FlexPod ONTAP storage configuration completed"'
        kwargs.regex = f"The AutoSupport was successfully invoked on node"
        kwargs.cmds = [f" "]
        config_function(child, kwargs)
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
        return kwargs


    #=====================================================
    # NetApp Broadcast Domain Creation
    #=====================================================
    def broadcast_domain(self, i, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section('netapp', self.type)
        #=====================================================
        # Create/Patch the Broadcast Domains
        #=====================================================
        uri  = '/network/ethernet/broadcast-domains?fields=mtu,name'
        bdRes= get(uri, kwargs)
        kwargs.netapp.broadcast_domains = {}
        prCyan('')
        for bd in i.broadcast_domain:
            prLightPurple(f"  Beginning Configuration for Broadcast Domain {bd.name}")
            payload= deepcopy(bd)
            method = 'post'
            for r in bdRes['records']:
                r = DotMap(deepcopy(r))
                if bd.name == r.name:
                    if r.mtu == bd.mtu: method = 'skip'
                    else:
                        method= 'patch'
                        uri   = f'network/ethernet/broadcast-domains/{r["uuid"]}'
                        payload.pop('name')
            if method == 'skip':
                prCyan(f"    - Skipping Broadcast Domain {bd.name}.  API Matches Defined Config.")
            if method == 'post': uri = 'network/ethernet/broadcast-domains'
            if re.search('(patch|post)', method):
                payload = json.dumps(payload)
                if print_payload: prCyan(json.dumps(payload, indent=4))
                prGreen(f"    * Configuring Broadcast Domain {bd.name}")
                eval(f"{method}(uri, kwargs, payload)")
            prLightPurple(f"  Completed Configuration for Broadcast Domain {bd.name}")
        prCyan('')
        uri = '/network/ethernet/broadcast-domains'
        bdRes = get(uri, kwargs)
        for bd in i.broadcast_domain:
            for r in bdRes['records']:
                r = DotMap(deepcopy(r))
                if bd.name == r.name or 'Default' in r.name:
                    kwargs.netapp.broadcast_domains.update({r.name:r.uuid})
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs


    #=====================================================
    # NetApp Cluster Initialization
    #=====================================================
    def cluster_init(self, kwargs):
        for i in kwargs.immDict.orgs[kwargs.org].netapp.cluster:
            i = DotMap(deepcopy(i))
            #=====================================================
            # Send Begin Notification
            #=====================================================
            validating.begin_section('netapp', self.type)
            time.sleep(2)
            #=====================================================
            # Load Variables and Login to Storage Array
            #=====================================================
            kwargs.hostname   = i.nodes[0].name + '.' + kwargs.dns_domains[0]
            kwargs.host_prompt= kwargs.netapp.cluster[i.name].host_prompt
            kwargs.password   = 'netapp_password'
            kwargs.username   = kwargs.netapp.cluster[i.name].username
            child, kwargs     = ezfunctions.child_login(kwargs)
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
                child.expect(kwargs.host_prompt)
            #=====================================================
            # Storage Failover Check
            #=====================================================
            kwargs.count= 2
            kwargs.show = "storage failover show"
            kwargs.regex= "true[ ]+Connected to"
            kwargs.cmds = ["storage failover modify -node * -enabled true"]
            config_function(child, kwargs)
            #=====================================================
            # Validate Cluster High Availability
            #=====================================================
            kwargs.count= 1
            kwargs.show = "cluster ha show"
            kwargs.regex= "High-Availability Configured: true"
            kwargs.cmds = ['cluster ha modify -configured true']
            config_function(child, kwargs)
            #=====================================================
            # Validate Storage Failover Hardware Assist
            #=====================================================
            ctrl_ips = kwargs.ooband['controller']
            kwargs.count= 2
            kwargs.show = "storage failover hwassist show"
            kwargs.regex= "Monitor Status: active"
            kwargs.cmds = [
                f"storage failover modify -hwassist-partner-ip {ctrl_ips[2]} -node {i.nodes[0].name}",
                f"storage failover modify -hwassist-partner-ip {ctrl_ips[1]} -node {i.nodes[1].name}",
            ]
            config_function(child, kwargs)
            #=====================================================
            # Configure Service Processors
            #=====================================================
            ipcount = 3
            gw   = kwargs.ooband.gateway
            mask = kwargs.ooband.netmask
            for node in i.nodes:
                spip = kwargs.ooband.controller[ipcount]
                kwargs.count= 1
                kwargs.show = "system service-processor show"
                kwargs.regex= f"online[ ]+true[ ]+[\\d\\.]+[ ]+{spip}"
                kwargs.cmds = [f"system service-processor network modify -node {node.name} -address-family IPv4 "\
                    f"-enable true -dhcp none -ip-address {spip} -netmask {mask} -gateway {gw}"]
                config_function(child, kwargs)
                ipcount += 1
                #===========================================================
                # Disable Flow Control on Data Ports
                #===========================================================
                for dp in node.data_ports:
                    kwargs.count= 1
                    kwargs.show = f"network port show -node {node} -port {dp}"
                    kwargs.regex= f"Flow Control Administrative: none"
                    kwargs.cmds = [f"network port modify -node {node} -port {dp} -flowcontrol-admin none"]
                    config_function(child, kwargs)
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
                        i = child.expect(['There are no entries', 'were displayed', kwargs.host_prompt])
                        if   i == 0: check = False
                        elif i == 1: check = True
                        elif i == 2: cmd_check = True
                    if check == False:
                        for cmd in cmds:
                            if 'sleep' in cmd: time.sleep(3)
                            else: 
                                child.sendline(cmd)
                                child.expect(kwargs.host_prompt)
            #=====================================================
            # Disk Zero Spares
            #=====================================================
            cmd = 'disk zerospares'
            child.sendline(cmd)
            child.expect(kwargs.host_prompt)
            cmd = 'disk show -fields zeroing-percent'
            child.sendline(cmd)
            dcount = 0
            zerospares = False
            while zerospares == False:
                i = child.expect([r'\d.\d.[\d]+ [\d]', 'to page down', kwargs.host_prompt])
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
        return kwargs


    #=====================================================
    # NetApp Cluster Creation
    #=====================================================
    def cluster(self, kwargs):
        #=====================================================
        # First Initialize the Clusters
        #=====================================================
        #kwargs = api('cluster_init').cluster_init(kwargs)
        validating.begin_section('netapp', self.type)
        #=====================================================
        # Load Variables and Send Notification
        #=====================================================
        netapp = kwargs.immDict.orgs[kwargs.org].netapp.cluster
        netapp = list({v['name']:v for v in netapp}.values())
        for i in netapp:
            i = DotMap(deepcopy(i))
            validating.begin_loop('cluster', i.name)

            #=====================================================
            # Add NTP Servers
            #=====================================================
            uri = 'cluster/ntp/servers'
            jData = get(uri, kwargs)
            for ntp in i.ntp_servers:
                method = 'post'
                uri = 'cluster/ntp/servers'
                for r in jData['records']:
                    r = DotMap(deepcopy(r))
                    if r.server == ntp:
                        method= 'patch'
                        uri   = uri + '/' + ntp
                polVars= {"server": ntp}
                payload= json.dumps(polVars)
                if print_payload: prCyan(json.dumps(polVars, indent=4))
                if method == 'post':
                    eval(f"{method}(uri, kwargs, payload)")

            #=====================================================
            # Add Cluster Interface
            #=====================================================
            uri = 'network/ip/interfaces'
            jData = get(uri, kwargs)
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
            prLightPurple(f"\n    Configuring Cluster {i.name}")
            eval(f"{method}(uri, kwargs, payload)")

            #=====================================================
            # Validate Licenses Exist for Each Protocol
            #=====================================================
            prLightPurple(f"\n    Validating Licensing for {i.name}")
            uri = 'cluster/licensing/licenses'
            licenseData = get(uri, kwargs)
            for p in kwargs.netapp.cluster[i.name].protocols:
                license_installed = False
                for r in licenseData['records']:
                    r = DotMap(deepcopy(r))
                    if r.name == p: license_installed = True
                if license_installed == False:
                    prRed(f'\n!!! ERROR !!!\nNo License was found for protocol {p}\n')
                    sys.exit()

            #=====================================================
            # Configure Sub-Sections
            #=====================================================
            item_list = ['autosupport', 'snmp', 'broadcast_domain', 'nodes', 'svm']
            for item in item_list:
                kwargs = eval(f"api(item).{item}(i, kwargs)")

            validating.end_loop('cluster', i.name)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs


    #=====================================================
    # NetApp Lun Creation
    #=====================================================
    def lun(self, polVars, kwargs):
        #=====================================================
        # Send Notification
        #=====================================================
        validating.begin_section(self.type, 'netapp')

        #=====================================================
        # Load Variables and Begin Loop
        #=====================================================
        i = DotMap(deepcopy(polVars))
        polVars.pop('lun_type')
        if polVars.get('profile'): polVars.pop('profile')
        if polVars.get('lun_name'): polVars.pop('lun_name')
        method = 'post'
        uri    = f'storage/luns'
        for r in kwargs.lun_results['records']:
            r = DotMap(deepcopy(r))
            if r.name == i.name:
                method = 'patch'
                uri = uri + '/' + r.uuid
                pop_list = ['name', 'os_type', 'svm']
                for p in pop_list:
                    if polVars.get(p): polVars.pop(p)
        payload = json.dumps(polVars)
        if print_payload: prCyan(json.dumps(polVars, indent=4))
        prLightPurple(f'   {method} SVM {kwargs.svm} Lun {i.name}')
        eval(f"{method}(uri, kwargs, payload)")
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
            if re.search('fc-nvme|fc', kwargs.dtype):
                for w in kwargs.server_profiles[i.profile].wwpns:
                    e = DotMap(w)
                    grpVars['initiators'].append({
                        "comment": f"{i.profile}-{e.name}", "name": e.wwpn
                    })
            else:
                iqn = kwargs.server_profiles[i.profile].iqn
                grpVars['initiators'].append({"comment": i.profile, "name": iqn})
            igroup(grpVars, kwargs)
            mapVars = {
                "igroup": {"name": i.profile},
                "logical_unit_number": 0,
                "lun": {"name": i.name},
                "svm": i.svm.toDict()
            }
            lunmap(mapVars, kwargs)
        #=====================================================
        # Assign iGroups and Lun Maps for Data Luns
        #=====================================================
        elif re.search('(data|swap|vcls)', i.lun_type):
            grpVars = {
                'name': i.lun_name,
                'initiators': [],
                'os_type': i.os_type,
                'svm': i.svm.toDict()
            }
            for k, v in kwargs.server_profiles.items():
                if re.search('fc-nvme|fc', kwargs.dtype):
                    for w in v.wwpns:
                        e = DotMap(w)
                        grpVars['initiators'].append({
                            "comment": f"{k}-{e.name}", "name": e.wwpn
                        })
                else: grpVars['initiators'].append({"comment": k, "name": v.iqn})
            igroup(grpVars, kwargs)
            mapVars = {
                "igroup": {"name": i.lun_name},
                "logical_unit_number": kwargs.lun_count,
                "lun": {"name": i.name},
                "svm": i.svm.toDict()
            }
            lunmap(mapVars, kwargs)
            kwargs.lun_count += 1

        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs


    #=====================================================
    # NetApp Node Creation
    #=====================================================
    def nodes(self, i, kwargs):
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
            kwargs.netapp[node.name].interfaces = {}
            kwargs.netapp[node.name]['aggregates'] = {}
            #=====================================================
            # Create/Patch Storage Aggregates
            #=====================================================
            prLightPurple(f"\n    Get Existing Storage Aggregates")
            aggregate= node.storage_aggregates[0].name
            method   = 'post'
            uri      = 'storage/aggregates'
            storageAggs = get(uri, kwargs)
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
            eval(f"{method}(uri, kwargs, payload)")
            prLightPurple(f"\n    Add Storage Aggregate to Dictionaries")
            uri = 'storage/aggregates'
            storageAggs = get(uri, kwargs)
            for r in storageAggs['records']:
                r = DotMap(deepcopy(r))
                if r.name == aggregate:
                    kwargs.netapp[node.name]['aggregates'].update({"name":aggregate,"uuid":r.uuid})
            #=====================================================
            # Update Interfaces on the Nodes
            #=====================================================
            prLightPurple(f"\n    Get Existing Ethernet Port Records.")
            uri       = f'network/ethernet/ports?node.name={node.name}'
            ethResults= get(uri, kwargs)
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
                        kwargs.netapp[node.name].interfaces.update({r.name:r.uuid})
                    for dp in lacp.lag.member_ports:
                        if r.name == dp.name: kwargs.netapp[node.name].interfaces.update({r.name:r.uuid})
                #=====================================================
                # Create/Patch the LAG - a0a
                #=====================================================
                uri = 'network/ethernet/ports'
                if method == 'patch': uri = f'network/ethernet/ports/{kwargs.netapp[node.name].interfaces["a0a"]}'
                polVars.update({"node": {"name":node.name}})
                polVars['broadcast_domain'].update(
                    {"uuid": kwargs.netapp.broadcast_domains[lacp.broadcast_domain.name]}
                )
                for dp in polVars['lag']['member_ports']:
                    dp.update({
                        "uuid": kwargs.netapp[node.name].interfaces[dp['name']],
                        "node": {"name": node['name']}
                    })
                if method == 'patch':
                    pop_list = ['distribution_policy', 'mode']
                    for p in pop_list: polVars['lag'].pop(p)
                    pop_list = ['node', 'type']
                    for p in pop_list: polVars.pop(p)
                payload = json.dumps(polVars)
                if print_payload: prCyan(json.dumps(polVars, indent=4))
                eval(f"{method}(uri, kwargs, payload)")
                uri = f'network/ethernet/ports?node.name={node.name}'
                #=====================================================
                # Get UUID For the LAG
                #=====================================================
                ethResults = get(uri, kwargs)
                method = 'post'
                for r in ethResults['records']:
                    r = DotMap(deepcopy(r))
                    if r.name == 'a0a': kwargs.netapp[node.name].interfaces.update({'a0a': r.uuid})
            #=====================================================
            # Create/Patch the VLAN Interfaces for the LAG
            #=====================================================
            uri = f'network/ethernet/ports?fields=broadcast_domain,node,type,vlan&node.name={node.name}'
            ethResults = get(uri, kwargs)
            for v in node.interfaces.vlan:
                intf_name = f'a0a-{v.vlan.tag}'
                prLightPurple(f"\n    Beginning Configuration for VLAN Interface {intf_name}.")
                polVars = deepcopy(v.toDict())
                uri = 'network/ethernet/ports'
                method = 'post'
                polVars['broadcast_domain'].update({
                    "uuid": kwargs.netapp.broadcast_domains[v.broadcast_domain.name]
                })
                polVars.update({"node": node.name})
                polVars['vlan']['base_port'].update({
                    "node": {"name": node.name},
                    "uuid": kwargs.netapp[node.name].interfaces['a0a']
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
                    eval(f"{method}(uri, kwargs, payload)")
                prLightPurple(f"    Completed Configuration for VLAN Interface {intf_name}.")
            prCyan('')
            uri = f'network/ethernet/ports?fields=node,type,vlan&node.name={node.name}'
            intfData = get(uri, kwargs)
            for v in node.interfaces.vlan:
                intf_name = f'a0a-{v.vlan.tag}'
                for r in intfData['records']:
                    r = DotMap(deepcopy(r))
                    if r.type == 'vlan':
                        if r.vlan.tag == v.vlan.tag:
                            kwargs.netapp[node.name].interfaces.update({intf_name:r.uuid})
            validating.end_section('node', node.name)
        #=====================================================
        # Delete Default-* Broadcast Domains
        #=====================================================
        uri = '/network/ethernet/broadcast-domains'
        bdResults = get(uri, kwargs)
        for r in bdResults['records']:
            r = DotMap(deepcopy(r))
            if 'Default-' in r.name:
                uri = f'network/ethernet/broadcast-domains/{r.uuid}'
                delete(uri, kwargs, payload)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs


    #=====================================================
    # NetApp Schedule Creation
    #=====================================================
    def schedule(self, kwargs, svm):
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
            jData  = get(uri, kwargs)
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
                eval(f"{method}(uri, kwargs, payload)")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs


    #=====================================================
    # NetApp SNMP Creation
    #=====================================================
    def snmp(self, i, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section('netapp', self.type)
        #=====================================================
        # Get Auth and Privilege Passwords
        #=====================================================
        kwargs.sensitive_var = 'snmp_auth_password'
        kwargs = ezfunctions.sensitive_var_value(kwargs)
        snmp_auth_password = kwargs['var_value']
        kwargs.sensitive_var = 'snmp_priv_password'
        kwargs = ezfunctions.sensitive_var_value(kwargs)
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
            patch(uri, kwargs, payload)
            #=====================================================
            # Configure SNMP Users
            #=====================================================
            jData = get(uri, kwargs)
            for user in snmp.users:
                userVars = deepcopy(user.toDict())
                method = 'post'
                uri = 'support/snmp/users'
                jData = get(uri, kwargs)
                if jData.get('records'):
                    for r in jData['records']:
                        r = DotMap(deepcopy(r))
                        if userVars['name'] == r.name:
                            engine_id = r.engine_id
                            #url = uri + f"/{engine_id}/{r.name}"
                            #delete(url, kwargs)
                            method = 'patch'
                if method == 'post':
                    userVars['snmpv3'].update({
                        "authentication_password": snmp_auth_password,
                        "privacy_password": snmp_priv_password,
                    })
                    payload = json.dumps(userVars)
                    if print_payload: prPurple(json.dumps(userVars, indent=4))
                    eval(f"{method}(uri, kwargs, payload)")
            #=====================================================
            # Configure SNMP Trap Servers
            #=====================================================
            uri = 'support/snmp/traphosts'
            jData = get(uri, kwargs)
            for trap in snmp.traps:
                trapVars = deepcopy(trap.toDict())
                method = 'post'
                uri = 'support/snmp/traphosts'
                jData = get(uri, kwargs)
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
                    if print_payload: prPurple(json.dumps(trapVars, indent=4))
                    eval(f"{method}(uri, kwargs, payload)")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs


    #=====================================================
    # NetApp Storage Virtual Machine Creation (vserver)
    #=====================================================
    def svm(self, i, kwargs):
        #=====================================================
        # Load Variables and Send Notification
        #=====================================================
        validating.begin_section('netapp', self.type)
        #=====================================================
        # Load Variables and Login to Storage Array
        #=====================================================
        kwargs.hostname   = i.nodes[0].name + '.' + kwargs.dns_domains[0]
        kwargs.host_prompt= kwargs.netapp.cluster[i.name].host_prompt
        kwargs.password   = 'netapp_password'
        kwargs.username   = kwargs.netapp.cluster[i.name].username
        child, kwargs    = ezfunctions.child_login(kwargs)
        host_file = open(f'{kwargs.hostname}.txt', 'r')
        
        #=====================================================
        # Using pexpect, configure SVM
        #=====================================================
        for svm in i.svm:
            svm_pexpect(child, host_file, i, kwargs, svm)
        
        #=====================================================
        # Close the Child Process and Cleanup Environment
        #=====================================================
        child.sendline('exit')
        child.expect('closed')
        child.close()
        host_file.close()
        os.remove(f'{kwargs.hostname}.txt')

        #=====================================================
        # Configure the SVM Through the API
        #=====================================================
        for svm in i.svm:
            #=====================================================
            # Get Existing SVMs
            #=====================================================
            prLightPurple(f"  Obtaining UUID for {svm.name}")
            uri = 'svm/svms'
            jData = get(uri, kwargs)
            for r in jData['records']:
                r = DotMap(deepcopy(r))
                if r.name == svm.name:
                    kwargs.netapp.cluster[svm.cluster].svm.moid = r.uuid

            #=====================================================
            # Configure Default Route
            #=====================================================
            prCyan('')
            prLightPurple(f"  Beginning {svm.name} Default Route Configuration.")
            uri    = f'network/ip/routes?fields=svm,destination&svm.name={svm.name}'
            jData  = get(uri, kwargs)
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
                eval(f"{method}(uri, kwargs, payload)")
            prLightPurple(f"  Completed {svm.name} Default Route Configuration.")
            prCyan('')

            #=====================================================
            # Configure the vsadmin password and Unlock It
            #=====================================================
            prCyan('')
            prLightPurple(f"  Beginning {svm.name} vsadmin Configuration.")
            kwargs.sensitive_var = 'netapp_password'
            kwargs = ezfunctions.sensitive_var_value(kwargs)
            password = kwargs['var_value']

            uri = f'security/accounts/{kwargs.netapp.cluster[svm.cluster].svm.moid}/vsadmin'
            jData = get(uri, kwargs)
            r = DotMap(deepcopy(jData))
            if not r.locked == False:
                uri = f'security/accounts/{kwargs.netapp.svms[svm.name]}/vsadmin'
                polVars = { "locked": False, "password": password }
                payload = json.dumps(polVars)
                if print_payload: prCyan(json.dumps(polVars, indent=4))
                eval(f"{method}(uri, kwargs, payload)")
            prLightPurple(f"  Completed {svm.name} vsadmin Configuration.")
            prCyan('')

            #=====================================================
            # Configure NFS Settings for the SVM
            #=====================================================
            prCyan('')
            prLightPurple(f"  Beginning {svm.name} NFS Settings Configuration.")
            uri    = f'protocols/nfs/services/'
            jData  = get(uri, kwargs)
            method = 'post'
            for r in jData['records']:
                r = DotMap(deepcopy(r))
                if r.svm.uuid == kwargs.netapp.cluster[svm.cluster].svm.moid:
                    method = 'patch'
                    uri = f'protocols/nfs/services/{kwargs.netapp.cluster[svm.cluster].svm.moid}'
            polVars = {
                "protocol": {"v3_enabled": True, "v41_enabled": True},
                "transport": {"udp_enabled": False},
                "vstorage_enabled": True,
                "svm":{ "name": svm.name, "uuid": kwargs.netapp.cluster[svm.cluster].svm.moid }
            }
            if method == 'patch': polVars.pop('svm')
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, kwargs, payload)")
            prLightPurple(f"  Completed {svm.name} NFS Settings Configuration.")
            prCyan('')

            #=====================================================
            # Disable Weak Security
            # SSH Ciphers and MAC Algorithms
            #=====================================================
            prCyan('')
            prLightPurple(f"  Beginning {svm.name} Security Configuration.")
            uri = 'security/ssh'
            jData = get(uri, kwargs)
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
            eval(f"{method}(uri, kwargs, payload)")
            uri = f'security/ssh/svms/{kwargs.netapp.cluster[svm.cluster].svm.moid}'
            polVars = { "ciphers": cipher_list, "mac_algorithms": mac_algorithms }
            method = 'patch'
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, kwargs, payload)")

            #=====================================================
            # Enable FIPS Security
            #=====================================================
            polVars = {"fips": {"enabled": True}}
            uri = 'security'
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            patch(uri, kwargs, payload)
            prLightPurple(f"  Completed {svm.name} Security Configuration.")
            prCyan('')
            
            #=====================================================
            # Disable Ciphers and Configure Login Banner - SVM
            #=====================================================
            prCyan('')
            prLightPurple(f"  Beginning {svm.name} Login Banner Configuration.")
            method = 'post'
            uri = f'security/login/messages?fields=svm'
            loginData = get(uri, kwargs)
            uri = f'security/login/messages'
            for r in loginData['records']:
                r = DotMap(deepcopy(r))
                if r.get('svm'):
                    if r.svm.uuid == kwargs.netapp.cluster[svm.cluster].svm.moid:
                        method = 'patch'
                        uri = uri + '/' + kwargs.netapp.cluster[svm.cluster].svm.moid
            polVars = {
                "banner": svm.banner,
                "scope": "svm",
                "show_cluster_message": True,
                "svm": {"name": svm.name, "uuid": kwargs.netapp.cluster[svm.cluster].svm.moid}
            }
            if method == 'patch':
                polVars.pop('svm')
                polVars.pop('scope')
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, kwargs, payload)")
            prLightPurple(f"  Completed {svm.name} Login Banner Configuration.")
            prCyan('')

            #=====================================================
            # Configure SVM Data Interfaces
            #=====================================================
            uri      = 'network/ip/interfaces?fields=enabled,dns_zone,ip,location,service_policy,svm'
            intfData = get(uri, kwargs)
            for intf in svm.data_interfaces:
                intf = DotMap(deepcopy(intf))
                prCyan('')
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
                    eval(f"{method}(uri, kwargs, payload)")
                prLightPurple(f"  Completed SVM {svm.name} Interface - {intf.name} Configuration.")
                prCyan('')

            #=====================================================
            # Configure SVM FCP Interfaces
            #=====================================================
            if 'fc' in kwargs.dtype:
                uri = 'network/fc/interfaces?fields=enabled,data_protocol,location,svm'
                intfData = get(uri, kwargs)
                for intf in svm.fcp_interfaces:
                    intf = DotMap(deepcopy(intf))
                    prCyan('')
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
                        eval(f"{method}(uri, kwargs, payload)")
                    prLightPurple(f"  Completed {svm.name} Interface - {intf.name} Configuration.")
                    prCyan('')

            #=====================================================
            # Obtain Target Identifier Information
            #=====================================================
            uri = 'network/fc/interfaces?fields=name,wwnn,wwpn'
            intfData = get(uri, kwargs)
            fcp_temp = deepcopy(kwargs.netapp.cluster[svm.cluster].nodes.fcp_ports)
            half = len(fcp_temp)//2
            kwargs.storage[svm.cluster][svm.name].wwpns.a = []
            kwargs.storage[svm.cluster][svm.name].wwpns.b = []
            for r in intfData['records']:
                r = DotMap(deepcopy(r))
                for f in fcp_temp[:half]:
                    if f in r.name:
                        kwargs.storage[svm.cluster][svm.name].wwpns.a.append({
                            'interface': r.name,
                            'wwpn': r.wwpn
                        })
                for f in fcp_temp[half:]:
                    if f in r.name:
                        kwargs.storage[svm.cluster][svm.name].wwpns.b.append({
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
                kwargs = eval(f"api(sub).{sub}(kwargs, svm)")

        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('netapp', self.type)
        return kwargs


    #=====================================================
    # NetApp Volumes Creation
    #=====================================================
    def volumes(self, kwargs, svm):
        #=====================================================
        # Send Notification
        #=====================================================
        validating.begin_section('netapp', self.type)
        #=====================================================
        # Load Variables and Login to Storage Array
        #=====================================================
        child, kwargs = ezfunctions.child_login(kwargs)
        prCyan('\n\n')
        #=====================================================
        # Loop Thru Volumes
        #=====================================================
        uri    = f'storage/volumes/?svm.name={svm.name}&fields=aggregates,encryption,guarantee,name,nas,size,snapshot_policy,state,style'
        jData  = get(uri, kwargs)
        for i in svm.volumes:
            prCyan('')
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
                    kwargs.netapp.volumes[i.name].update({'uuid':r.uuid})
                    pop_list = ['aggregates', 'encryption', 'style', 'svm', 'type']
                    for p in pop_list:
                        if polVars.get(p): polVars.pop(p)
            prGreen(f"    - Configuring Volume {i.name} on {svm.name}.")
            payload = json.dumps(polVars)
            if print_payload: prCyan(json.dumps(polVars, indent=4))
            eval(f"{method}(uri, kwargs, payload)")

            #=====================================================
            # Configure Volume Properties from CLI if Needed
            #=====================================================
            volume_pexpect(child, i, kwargs, svm)

            prLightPurple(f"  Completed SVM {svm.name} Volume - {i.name} Configuration.")
            prCyan('')
        #=====================================================
        # Initialize the snapmirror
        #=====================================================
        src  = f"{svm.name}:{svm.root_volume.name}"
        kwargs.count = 2
        kwargs.show  = f"snapmirror show -vserver {svm.name} -source-path {src}"
        kwargs.regex = "true"
        kwargs.cmds  = [ f"snapmirror initialize-ls-set -source-path {src}" ]
        config_function(child, kwargs)
        #=====================================================
        # Close the Child Process
        #=====================================================
        child.sendline('exit')
        child.expect('closed')
        child.close()
        os.remove(f'{kwargs.hostname}.txt')

        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'netapp')
        return kwargs


#=======================================================
# Build Storage Class
#=======================================================
class build(object):
    def __init__(self, type):
        self.type = type
    #=============================================================================
    # Function - NetApp - AutoSupport
    #=============================================================================
    def autosupport(self, items, kwargs):
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
    def broadcast_domain(self, items, kwargs):
        #=====================================================
        # Build Broadcast Domain Dictionary
        #=====================================================
        bdomains = []
        for i in kwargs.vlans:
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
    def cluster(self, items, name, kwargs):
        items.name = name
        #=====================================================
        # Build Cluster Dictionary
        #=====================================================
        polVars = dict(
            contact     = items.snmp.contact,
            dns_domains = kwargs.dns_domains,
            license     = dict(keys = []),
            location    = items.snmp.location,
            management_interfaces = [dict(
                name= "cluster-mgmt",
                ip  = dict( address = kwargs.ooband.controller[0] ))
            ],
            name = name,
            name_servers = kwargs.dns_servers,
            ntp_servers  = kwargs.ntp_servers,
            timezone     = kwargs.timezone,
            username     = items.username
        )
        if items.get('licenses'):
            polVars.update({'license':{'keys':[items.licenses]}})

        kwargs.netapp.hostname= items.nodes.node01 + '.' + kwargs.dns_domains[0]
        kwargs.netapp.username= items.username
        ilist = ['autosupport', 'broadcast_domain', 'nodes', 'snmp', 'svm']
        for i in ilist:
            idict = eval(f"build(i).{i}(items, kwargs)")
            polVars.update(deepcopy({i:idict}))

        #=====================================================
        # Add Policy Variables to immDict
        #=====================================================
        kwargs.class_path = f'netapp,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - NetApp - Storage Volumes
    #=============================================================================
    def lun(self, kwargs):
        kwargs.lun_count = 1
        def create_lun_list(kwargs):
            kwargs.lun_list = []
            #=====================================================
            # Boot Luns
            #=====================================================
            for k, v in kwargs.server_profiles.items():
                for e in kwargs.volumes:
                    if e.volume_type == 'boot':
                        polVars = {
                            "name": f"/vol/{e.name}/{k}",
                            "os_type": f"{e.os_type}",
                            "space":{"guarantee":{"requested": False}, "size":f"128GB"},
                            "svm":{"name":kwargs.svm},
                            "lun_type": "boot",
                            "profile": k
                        }
                        kwargs.lun_list.append(polVars)
                        kwargs = api('lun').lun(polVars, kwargs)

            for e in kwargs.volumes:
                #=====================================================
                # Build Data Luns
                #=====================================================
                if re.search('(data|swap|vcls)', str(e.volume_type)):
                    polVars = {
                        "name": f"/vol/{e.name}/{e.name}",
                        "os_type": f"{e.os_type}",
                        "space":{"guarantee":{"requested": False}, "size":f"{e.size}"},
                        "svm":{"name":kwargs.svm},
                        "lun_type": e.volume_type,
                        "lun_name": e.name,
                    }
                    kwargs.lun_list.append(polVars)
                    api('lun').lun(polVars, kwargs)

            return kwargs

        cluster = deepcopy(kwargs.immDict.orgs[kwargs.org].netapp.cluster)
        for i in cluster:
            for s in i.svm:
                kwargs.netapp.hostname = i.nodes[0].name + '.' + kwargs.dns_domains[0]
                kwargs.netapp.username = i.username
                kwargs.cluster = i.name
                kwargs.svm     = s.name
                kwargs.volumes = s.volumes
                check_for_boot_lun(kwargs)
                #=====================================================
                # Get Existing Luns
                #=====================================================
                uri    = f'storage/luns/?svm.name={kwargs.svm}'
                kwargs.lun_results = get(uri, kwargs)
                kwargs = create_lun_list(kwargs)
                cx = [e for e, d in enumerate(cluster) if i.name in d.values()][0]
                sx = [e for e, d in enumerate(cluster[cx].svm) if s.name in d.values()][0]
                kwargs.immDict.orgs[kwargs.org].netapp.cluster[cx].svm[sx].luns = kwargs.lun_list
        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs

    #=============================================================================
    # Function - NetApp - Nodes
    #=============================================================================
    def nodes(self, items, kwargs):
        #==================================
        # Get Disk Information
        #==================================
        uri       = 'storage/disks'
        jData     = get(uri, kwargs)
        disk_count= jData['num_records'] - 1
        #disk_name = jData['records'][0]['name']
        #uri   = f'storage/disks/{disk_name}'
        #jData = get(uri, kwargs)
        #kwargs.netapp.disk_type = jData['type'].upper()

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
            if re.search('(fc|fc-nvme)', kwargs.dtype):
                polVars['interfaces'].update({'fcp':[]})
                for i in items.nodes.fcp_ports:
                    fcpPort = { "enabled": True, "name": i, "speed": {"configured": items.nodes.fcp_speed} }
                    polVars['interfaces']['fcp'].append(fcpPort)
            for i in kwargs.vlans:
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
    def snmp(self, items, kwargs):
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
    def svm(self, items, kwargs):
        #=====================================================
        # Create Infra SVM
        #=====================================================
        polVars = {
            "aggregates": [ {"name": items.svm.agg1}, {"name": items.svm.agg2} ],
            "banner": items.banner,
            "cluster": items.name,
            "name": items.svm.name,
            "dns":{"domains": kwargs.dns_domains, "servers": kwargs.dns_servers},
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
                "gateway": kwargs.inband.gateway,
                "svm": {"name": items.svm.name}
            }]
        }
        polVars['protocols'] = {}
        for p in items.protocols: polVars['protocols'].update({p:{"allowed": True, "enabled": True}})

        #=====================================================
        # Configure Ethernet Interfaces
        #=====================================================
        polVars['data_interfaces'] = []
        for v in kwargs.vlans:
            for x in range(0,len(items.nodes.node_list)):
                if re.search('(inband|iscsi|nfs|nvme)', v.vlan_type):
                    if re.search('(inband|nfs)', v.vlan_type):
                        kwargs.netapp.intf_name = f"{v.vlan_type}-lif-0{x+1}-a0a-{v.vlan_id}"
                    elif re.search('(iscsi|nvme)', v.vlan_type):
                        kwargs.netapp.intf_name = f"{v.vlan_type}-lif-0{x+1}-a0a-{v.vlan_id}"
                    kwargs.vlan_settings = deepcopy(v)
                    kwargs = configure_interfaces(x, items, kwargs)
                    if len(kwargs.polVars) > 0:
                        polVars['data_interfaces'].append(kwargs.polVars)

        #=====================================================
        # Configure Fibre-Channel if in Use
        #=====================================================
        if re.search('fc(-nvme)?', kwargs.dtype):
            polVars['fcp_interfaces'] = []
            if kwargs.dtype == 'fc':
                kwargs.netapp.data_protocol = 'fcp'
                kwargs = configure_fcports(x, items, kwargs)
                polVars['fcp_interfaces'].extend(kwargs.polVars)
            else:
                fcp_temp = kwargs.netapp.fcp_ports
                half = len(fcp_temp)//2
                kwargs.netapp.fcp_ports = fcp_temp[:half]
                kwargs.netapp.data_protocol = 'fcp'
                kwargs = configure_fcports(x, items, kwargs)
                polVars['fcp_interfaces'].extend(kwargs.polVars)
                kwargs.netapp.fcp_ports = fcp_temp[half:]
                kwargs.netapp.data_protocol = kwargs.dtype
                kwargs = configure_fcports(x, items, kwargs)
                polVars['fcp_interfaces'].extend(kwargs.polVars)

        #=====================================================
        # Add Schedule and Volumes to SVM
        #=====================================================
        ilist = ['schedule', 'volumes']
        for i in ilist:
            idict = eval(f"build(i).{i}(items)")
            polVars.update({i:idict})

        #=====================================================
        # Return kwargs and kwargs
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
def auth(kwargs, section=''):
    url      = f"https://{kwargs.netapp.hostname}"
    username = kwargs.netapp.username
    kwargs.sensitive_var = 'netapp_password'
    kwargs = ezfunctions.sensitive_var_value(kwargs)
    password = kwargs.var_value
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
            prRed("!!! ERROR !!! Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)
    return s, url

#=====================================================
# Build Lun Dictionary
#=====================================================
def check_for_boot_lun(kwargs):
    boot_volume = False
    for v in kwargs.volumes:
        if v.volume_type == 'boot': boot_volume = True
    if boot_volume == False:
        prRed('\n\n!!! ERROR !!!\nCould not determine the boot volume.  No Boot Volume found in:\n')
        for v in kwargs.volumes: prRed(f'  *  Type =\t"{v.volume_type}"\tVolume Name:"{v.name}"')
        sys.exit(1)

#=====================================================
# pexpect - Configuration Function
#=====================================================
def config_function(child, kwargs):
    kwargs.message = f'\n{"-"*81}\n\n  !!! ERROR !!!!\n  **failed on "{kwargs.show}".\n'\
        f'    Looking for regex "{kwargs.regex}".\n'\
        f'\n  Please Validate the cluster and restart this wizard.\n\n{"-"*81}\n'
    child.sendline(kwargs.show)
    count = 0
    cmd_check = False
    while cmd_check == False:
        i = child.expect(["to page down", kwargs.regex, kwargs.host_prompt], timeout=20)
        if i == 0: child.send(' ')
        elif i == 1: count += 1
        elif i == 2: cmd_check = True
    if not count == kwargs.count:
        for cmd in kwargs.cmds:
            child.sendline(cmd)
            cmd_check = False
            while cmd_check == False:
                i = child.expect(["Do you want to continue", kwargs.host_prompt])
                if i == 0: child.sendline('y')
                elif i == 1: cmd_check = True
        time.sleep(3)
        child.sendline(kwargs.show)
        count = 0
        cmd_check = False
        while cmd_check == False:
            i = child.expect(["to page down", kwargs.regex, kwargs.host_prompt])
            if i == 0: child.send(' ')
            if i == 1: count += 1
            elif i == 2: cmd_check = True
        if not count == kwargs.count:
            prRed(kwargs.message)
            sys.exit(1)

#=====================================================
# Configure FCP Ports
#=====================================================
def configure_fcports(x, items, kwargs):
    kwargs.polVars = []
    for i in items.nodes.fcp_ports:
        for x in range(0,len(items.nodes.node_list)):
            if kwargs.netapp.data_protocol == 'fc-nvme': name = f'fcp-nvme-lif-0{x+1}-{i}'
            else: name = f'fcp-lif-0{x+1}-{i}'
            pVars = {
                "data_protocol": kwargs.netapp.data_protocol,
                "enabled": True,
                "location": {
                    "home_port": {"name":i, "node":{"name": items.nodes.node_list[x]}},
                },
                "name": name,
            }
            kwargs.polVars.append(pVars)

    return kwargs

#=====================================================
# Function - Configure Infra SVM Interfaces
#=====================================================
def configure_interfaces(x, items, kwargs):
    ip_address = kwargs.vlan_settings['controller'][x]
    if 'inband'  == kwargs.vlan_settings.vlan_type: servicePolicy = 'default-management'
    elif 'iscsi' == kwargs.vlan_settings.vlan_type: servicePolicy = 'default-data-iscsi'
    elif 'nfs'   == kwargs.vlan_settings.vlan_type: servicePolicy = 'default-data-files'
    elif 'nvme'  == kwargs.vlan_settings.vlan_type: servicePolicy = 'default-data-nvme-tcp'
    home_port = f"a0a-{kwargs.vlan_settings.vlan_id}"
    services = 'data_nfs'
    if 'inband' == kwargs.vlan_settings.vlan_type and x == 1: proceed = False
    else: proceed = True
    if proceed == True:
        kwargs.polVars = {
            "enabled": True,
            "dns_zone": kwargs.dns_domains[0],
            "ip": { "address": ip_address, "netmask": kwargs.vlan_settings.prefix },
            "location": {
                "auto_revert": True,
                "failover": "home_port_only",
                "home_node": {"name": items.nodes.node_list[x]},
                "home_port": {"name": home_port, "node":{"name": items.nodes.node_list[x]}},
            },
            "name": kwargs.netapp.intf_name,
            "scope": "svm",
            "service_policy": servicePolicy,
        }
        if re.search('iscsi|nfs|nvme', kwargs.vlan_settings.vlan_type):
            vtype = kwargs.vlan_settings.vlan_type
            if not kwargs.storage[items.name][items.svm.name].get(vtype):
                kwargs.storage[items.name][items.svm.name][vtype]['interfaces'] = []
            kwargs.storage[items.name][items.svm.name][vtype]['interfaces'].append(DotMap(
                interface = kwargs.netapp.intf_name,
                ip_address= ip_address,
            ))
    if re.search('(iscsi|nvme)', kwargs.vlan_settings.vlan_type):
        kwargs.polVars['location'].pop('auto_revert')
        kwargs.polVars['location'].pop('failover')
    return kwargs

#=====================================================
# Function - API - delete
#=====================================================
def delete(uri, kwargs, section=''):
    s, url = auth(kwargs)
    r = ''
    while r == '':
        try:
            prCyan(f"     * delete: {f'{url}/api/{uri}'}")
            r = s.delete(f'{url}/api/{uri}', verify=False)
            if print_response_always:
                prRed(f"delete: {r.status_code} success with {uri}")
            if r.status_code == 200 or r.status_code == 404:
                return r.json()
            else: validating.error_request_netapp('delete', r.status_code, r.text, uri)
        except requests.exceptions.ConnectionError as e:
            prRed("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            prRed("!!! ERROR !!! Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

#=====================================================
# Function - API - get
#=====================================================
def get(uri, kwargs, section=''):
    s, url = auth(kwargs)
    r = ''
    while r == '':
        try:
            prCyan(f"     * get: {f'{url}/api/{uri}'}")
            r = s.get(f'{url}/api/{uri}', verify=False)
            if print_response_always:
                prPurple(f"     * get: {r.status_code} success with {uri}")
            if r.status_code == 200 or r.status_code == 404:
                return r.json()
            else: validating.error_request_netapp('get', r.status_code, r.text, uri)
        except requests.exceptions.ConnectionError as e:
            prRed("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            prRed("!!! ERROR !!! Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

#=====================================================
# iGroup Function
#=====================================================
def igroup(polVars, kwargs):
    ig     = DotMap(deepcopy(polVars))
    uri    = f'protocols/san/igroups/?svm.name={ig.svm.name}'
    jData  = get(uri, kwargs)
    method = 'post'
    uri    = 'protocols/san/igroups'
    if jData.get('records'):
        for r in jData['records']:
            r = DotMap(deepcopy(r))
            if r.name == ig.name:
                method = 'patch'
                uri = uri + '/' + r.uuid
                polVars.pop('initiators')
                polVars.pop('svm')
                ig.uuid = r.uuid
    payload = json.dumps(polVars)
    if print_payload: prCyan(json.dumps(polVars, indent=4))
    prLightPurple(f'   {method} SVM {ig.svm.name} iGroup {ig.name}')
    eval(f"{method}(uri, kwargs, payload)")
    if method == 'patch': patch_lun_initiators(ig, kwargs)

#=====================================================
# Lun Map Function
#=====================================================
def lunmap(polVars, kwargs):
    lm     = DotMap(deepcopy(polVars))
    svm    = polVars['svm']['name']
    uri    = f'/protocols/san/lun-maps/?svm.name={svm}'
    jData  = get(uri, kwargs)
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
        prLightPurple(f'   {method} SVM {lm.svm.name} Lun Map {lm.lun.name}')
        eval(f"{method}(uri, kwargs, payload)")

#=====================================================
# Function - API - patch
#=====================================================
def patch(uri, kwargs, payload, section=''):
    s, url = auth(kwargs)
    r = ''
    while r == '':
        try:
            prCyan(f"     * patch: {f'{url}/api/{uri}'}")
            r = s.patch(f'{url}/api/{uri}', data=payload, verify=False)
            # Use this for Troubleshooting
            if not re.search('20[0-2]', str(r.status_code)):
                validating.error_request_netapp('patch', r.status_code, r.text, uri)
            if print_response_always:
                prPurple(f"     * patch: {r.status_code} success with {uri}")
            return r.json()
        except requests.exceptions.ConnectionError as e:
            prRed("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            prRed("!!! ERROR !!! Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

#=====================================================
# iGroup Function
#=====================================================
def patch_lun_initiators(ig, kwargs):
    uri = f'protocols/san/igroups/{ig.uuid}'
    jData = DotMap(get(uri, kwargs))
    for i in ig.initiators:
        indx = [e for e, d in enumerate(ig.initiators) if i.name in d.values()]
        #if not r.name in ig.initiators:
        #    uri = f'protocols/san/igroups/{ig.uuid}/initators/{r.name}'
        #    delete(uri, kwargs)
        if i.name in jData:
            uri = f'protocols/san/igroups/{ig.uuid}/initators/{i.name}'
            payload = json.dumps({
                'igroup': {'name': ig.name,'uuid': ig.uuid},
                'records': [{'comment': ig.initiators[indx[0]].comment}]
            })
            patch(uri, kwargs, payload)
        else:
            payload = json.dumps({
                #'igroup': {'name': ig.name,'uuid': ig.uuid},
                'records': [{
                    'name': ig.initiators[indx[0]].name,
                    'comment': ig.initiators[indx[0]].comment
                }]
            })
            uri = f'protocols/san/igroups/{ig.uuid}'
            post(uri, kwargs, payload)

#=====================================================
# Function - API - post
#=====================================================
def post(uri, kwargs, payload, section=''):
    s, url = auth(kwargs)
    r = ''
    while r == '':
        try:
            prCyan(f"     * post: {f'{url}/api/{uri}'}")
            r = s.post(f'{url}/api/{uri}', data=payload, verify=False)
            # Use this for Troubleshooting
            if not re.search('20[1-2]', str(r.status_code)):
                validating.error_request_netapp('post', r.status_code, r.text, uri)
            if print_response_always:
                prGreen(f"     * post: {r.status_code} success with {uri}")
            return r.json()
        except requests.exceptions.ConnectionError as e:
            prRed("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            prRed("!!! ERROR !!! Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

#=====================================================
# Function - SVM pexpect Process
#=====================================================
def svm_pexpect(child, host_file, i, kwargs, svm):
    svmcount = 0
    child.sendline('vserver show')
    child.expect(kwargs.host_prompt)
    for line in host_file:
        if re.search(f'{svm.name}[ ]+data', line): svmcount += 2
        elif re.search(svm.name, line): svmcount += 1
        elif re.search('data', line): svmcount += 1
    if not svmcount >= 2:
        cmd = f'vserver create -vserver {svm.name} -rootvolume {svm.root_volume.name} -rootvolume-security-style unix'
        child.sendline(cmd)
        child.expect(kwargs.host_prompt)

    #=====================================================
    # Configure Aggregates and add Login Banner
    #=====================================================
    cmds = [
        f'vserver modify {svm.name} -aggr-list {svm.aggregates[0].name},{svm.aggregates[1].name}',
        f'security login banner modify -vserver {svm.name} -message "{i.banner}"'
    ]
    for cmd in cmds:
        child.sendline(cmd)
        child.expect(kwargs.host_prompt)

    #=====================================================
    # Limit the Protocols assigned to the SVM
    #=====================================================
    child.sendline(f'vserver show -vserver {svm.name} -protocols')
    child.expect(f'{svm.name}[ ]+([\\w].*[\\w])[  ]')
    protocols = (((child.match).group(1)).strip()).split(',')
    child.expect(kwargs.host_prompt)
    protos = list(svm.protocols.keys())
    if 'nvme_of' in protos:
        protos.remove('nvme_of')
        protos.append('nvme')
    child.sendline(f'vserver add-protocols -protocols {",".join(protos)} -vserver {svm.name}')
    child.expect(kwargs.host_prompt)
    removep = []
    for p in protocols:
        p = p.strip()
        if not p in protos: removep.append(p)
    if len(removep) > 0:
        child.sendline(f'vserver remove-protocols -vserver {svm.name} -protocols {",".join(removep)}')
        child.expect(kwargs.host_prompt)

    #=====================================================
    # Function to Configure Protocols
    #=====================================================
    def config_protocols(child, kwargs):
        kwargs.message = f'\n{"-"*81}\n\n  !!! ERROR !!!!\n  **failed on "{kwargs.show}".\n'\
            f'    Looking for regex "{kwargs.regex1}".\n'\
            f'    Looking for regex "{kwargs.regex2}".\n'\
            f'    Looking for regex "{kwargs.regex3}".\n'\
            f'\n  Please Validate {svm.name} and restart this wizard.\n\n{"-"*81}\n'
        child.sendline(kwargs.show)
        change   = 'none'
        value    = ''
        cmd_check= False
        while cmd_check == False:
            i = child.expect(
                ["to page down", kwargs.regex1, kwargs.regex2, kwargs.regex3, kwargs.host_prompt], timeout=20
            )
            if   i == 0: child.send(' ')
            elif i == 1: change    = 'create'
            elif i == 2: change    = 'modify'
            elif i == 3: value     = (child.match).group(1)
            elif i == 4: cmd_check = True
        if not change == 'none':
            child.sendline(f"vserver {kwargs.p} {change} -vserver {svm.name} -status-admin up",)
            cmd_check = False
            while cmd_check == False:
                i = child.expect(["Do you want to continue", kwargs.host_prompt])
                if   i == 0: child.sendline('y')
                elif i == 1: cmd_check = True
            time.sleep(10)
            child.sendline(kwargs.show)
            change = 'none'
            cmd_check = False
            while cmd_check == False:
                i = child.expect(["to page down", kwargs.regex1, kwargs.regex2, kwargs.regex3, kwargs.host_prompt])
                if   i == 0: child.send(' ')
                elif i == 1: change    = 'create'
                elif i == 2: change    = 'modify'
                elif i == 3: value     = (child.match).group(1)
                elif i == 4: cmd_check = True
        if not change == 'none' and len(value) > 0:
            prRed(kwargs.message)
            sys.exit(1)
        return value
    #=====================================================
    # Configure Protocols
    #=====================================================
    for p in protos:
        if not 'nfs' in p:
            kwargs.show  = f"vserver {p} show -vserver {svm.name}"
            kwargs.regex1= "There are no entries matching your query"
            kwargs.regex2= "Administrative Status: down"
            if 'fcp' in p: kwargs.regex3 = "Target Name: (([\\da-f]{2}:){7}[\\da-f]{2})"
            elif 'iscsi' in p: kwargs.regex3 = "(iqn\\.[\\da-z\\.:\\-]+vs\\.[\\d]+(?=[\r\n]))"
            elif 'nvme' in p: kwargs.regex3 = "NQN: (nqn\\..*discovery)"
            kwargs.p = p
            value = config_protocols(child, kwargs)
            if 'iscsi' in p: kwargs.storage[svm.cluster][svm.name]['iscsi'].iqn = value
            elif 'nvme' in p: kwargs.storage[svm.cluster][svm.name]['nvme'].nqn = value

    #=====================================================
    # Configure NFS Export Policy
    #=====================================================
    cmdp = f'vserver export-policy rule METHOD -vserver {svm.name} -policyname default -protocol nfs -ruleindex 1'
    rules = '-rorule sys -rwrule sys -superuser sys -allow-suid true'
    kwargs.count= 1
    kwargs.show = cmdp.replace('METHOD', 'show')
    kwargs.regex= kwargs.nfs.network
    kwargs.cmds = [f"{cmdp.replace('METHOD', 'create')} -clientmatch {kwargs.nfs.network} {rules}"]
    config_function(child, kwargs)


#=====================================================
# Function - Volume pexpect Process
#=====================================================
def volume_pexpect(child, i, kwargs, svm):
    if i.volume_type == 'audit':
        kwargs.count= 1
        kwargs.show = f"vserver audit show -vserver {i.svm.name}"
        kwargs.regex= f"Log Destination Path"
        kwargs.cmds = [f"vserver audit create -vserver {i.svm.name} -destination /{i.name}"]
        config_function(child, kwargs)
        kwargs.count= 1
        kwargs.show = f"vserver audit show -vserver {i.svm.name}"
        kwargs.regex= f"Auditing State: true"
        kwargs.cmds = [f"vserver audit enable -vserver {i.svm.name}"]
        config_function(child, kwargs)
    elif re.search('_m0[1-2]$', i.name):
        #=====================================================
        # Attach the Mirrors to the Schedule and Initialize
        #=====================================================
        dest = f"{i.svm.name}:{i.name}"
        src  = f"{i.svm.name}:{svm.root_volume.name}"
        kwargs.count= 1
        kwargs.show = f"snapmirror show -vserver {i.svm.name} -destination-path {dest} -source-path {src}"
        kwargs.regex= f"Destination Path: {svm.cluster}://{i.svm.name}/{i.name}"
        kwargs.cmds = [
            f"snapmirror create -vserver {i.svm.name} -destination-path {dest} -source-path {src} -type LS -schedule 15min"
        ]
        config_function(child, kwargs)
    elif i.volume_type == 'nvme':
        kwargs.count= 1
        kwargs.show = f"vserver nvme namespace show -vserver {i.svm.name} -path /vol/{i.name}/{i.name}"
        kwargs.regex= f"online"
        kwargs.cmds = [f"vserver nvme namespace create -vserver {i.svm.name} -path /vol/{i.name}/{i.name}"]
        config_function(child, kwargs)
        kwargs.count= 1
        kwargs.show = f"vserver nvme subsystem show -vserver {i.svm.name} -subsystem {i.os_type}-hosts"
        kwargs.regex= f"OS Type: {i.os_type}"
        kwargs.cmds = [
            f"vserver nvme subsystem create -vserver {i.svm.name} -subsystem {i.os_type}-hosts -ostype {i.os_type}"
        ]
        config_function(child, kwargs)
        kwargs.count= 1
        kwargs.show = f"vserver nvme subsystem map show -vserver {i.svm.name} -path /vol/{i.name}/{i.name} -subsystem {i.os_type}-hosts"
        kwargs.regex= f"NSID"
        kwargs.cmds = [
            f"vserver nvme subsystem map add -vserver {i.svm.name} -path /vol/{i.name}/{i.name} -subsystem {i.os_type}-hosts"
        ]
        config_function(child, kwargs)
    elif i.volume_type == 'swap':
        kwargs.count= 1
        kwargs.show = f"volume efficiency show -vserver {i.svm.name} -volume {i.name}"
        kwargs.regex= f"Disabled"
        kwargs.cmds = [f"volume efficiency off -vserver {i.svm.name} -volume {i.name}"]
        config_function(child, kwargs)

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
