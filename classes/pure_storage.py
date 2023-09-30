#=============================================================================
# Source Modules
#=============================================================================
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
import sys
try:
    from classes import ezfunctions, pcolor, validating
    from copy import deepcopy
    from datetime import datetime, timedelta
    from dotmap import DotMap
    import json, os, platform, re, requests, socket, subprocess, time, urllib3
except ImportError as e:
    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
    prRed(f" Module {e.name} is required to run this script")
    prRed(f" Install the module using the following: `pip install {e.name}`")
    sys.exit(1)
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

# Pure Storage - Policies
# Class must be instantiated with Variables
class api(object):
    def __init__(self, type):
        self.type = type

    #=============================================================================
    # Function: Pure Storage - Alert Routing Configuration
    #=============================================================================
    def alert_routing(self, i, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        imap = DotMap(
            relay_host = 'relay_host',
            sender_domain = 'sender_domain',
            username = 'user_name')
        validating.begin_section('pure_storage', self.type)
        uri  = 'smtp-servers'
        rdata = DotMap((get(uri, kwargs))['items'][0])
        method = ''
        payload = {}
        for k, v in i.items():
            if not rdata[imap[k]] == v:
                if k == 'username' and not v == '':
                    method = 'patch'
                    payload.update({imap[k]:v})
                else:
                    method = 'patch'
                    payload.update({imap[k]:v})
        if payload.get('username'): method = 'patch'
        if method == 'patch':
            if payload.get('username'):
                kwargs.sensitive_var = 'smtp_server_password'
                kwargs  = ezfunctions.sensitive_var_value(kwargs)
                payload['password'] = kwargs.var_value
            if print_payload: pcolor.Cyan(json.dumps(payload, indent=4))
            patch(uri, kwargs, json.dumps(payload))
        else: pcolor.Cyan(f"    - Skipping Alert Routing Configuration.  API Matches Defined Config.")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('pure_storage', self.type)
        return kwargs


    #=============================================================================
    # Function: Pure Storage - Alert Watchers Configuration
    #=============================================================================
    def alert_watchers(self, i, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section('pure_storage', self.type)
        uri  = 'alert-watchers'
        rdata = DotMap((get(uri, kwargs))['items'])
        payload = {}
        for e in i:
            indx = next((index for (index, d) in enumerate(rdata) if d['name'] == e), None)
            method = 'blank'
            payload = {'enabled':True}
            if indx == None: method = 'post'
            else:
                if not rdata[indx]['enabled'] == True: method = 'patch'
            if re.search('patch|post', method):
                if print_payload: pcolor.Cyan(json.dumps(payload, indent=4))
                uri = f'alert-watchers?names=[{e}]'
                eval(f'{method}(uri, kwargs, json.dumps(payload))')
            else: pcolor.Cyan(f"    - Skipping Alert Watcher {e}.  API Matches Defined Config.")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('pure_storage', self.type)
        return kwargs


    #=====================================================
    # Pure Storage Cluster Creation
    #=====================================================
    def array(self, kwargs):
        #=====================================================
        # First Initialize the Clusters
        #=====================================================
        #kwargs = api('cluster_init').cluster_init(kwargs)
        validating.begin_section('pure_storage', self.type)
        #=====================================================
        # Load Variables and Send Notification
        #=====================================================
        pure_storage = kwargs.imm_dict.orgs[kwargs.org].pure_storage
        for i in list({v['name']:v for v in pure_storage}.values()):
            validating.begin_loop('array', i.name)
            #=====================================================
            # Configure Array Settings
            #=====================================================
            uri  = 'arrays'
            rdata = DotMap((get(uri, kwargs))['items'][0])
            method = 'blank'
            if len(i.ntp_servers) > 4: ntp_servers = i.ntp_servers[:4]
            else: ntp_servers = i.ntp_servers
            payload = {'banner':i.ui.login_banner,'idle_timeout': i.ui.gui_idle_timeout, 'ntp_servers':ntp_servers}
            for k, v in payload.items():
                if k == 'ntp_servers':
                    if not sorted(rdata[k]) == sorted(v): method = 'patch'
                if not rdata[k] == v: method = 'patch'
            if method == 'patch':
                if print_payload: pcolor.Cyan(json.dumps(payload, indent=4))
                patch(uri, kwargs, json.dumps(payload))
            else: pcolor.Cyan(f"    - Skipping Array UI Settings Configuration.  API Matches Defined Config.")
            #=====================================================
            # Configure DNS Settings
            #=====================================================
            uri  = 'dns'
            rdata = DotMap((get(uri, kwargs))['items'][0])
            method = 'blank'
            if len(i.dns_servers) > 3: dns_servers = i.dns_servers[:3]
            else: dns_servers = i.dns_servers
            payload = {'domain':i.dns_domains[0],'nameservers': dns_servers}
            for k, v in payload.items():
                if k == 'nameservers':
                    if not sorted(rdata[k]) == sorted(v): method = 'patch'
                if not rdata[k] == v: method = 'patch'
            if method == 'patch':
                if print_payload: pcolor.Cyan(json.dumps(payload, indent=4))
                patch(uri, kwargs, json.dumps(payload))
            else: pcolor.Cyan(f"    - Skipping DNS Configuration.  API Matches Defined Config.")
            #=====================================================
            # Configure Additional Settings
            #=====================================================
            for e in ['alert_routing', 'alert_watchers', 'pure1_support', 'smi_s', 'snmp', 'syslog']:
                kwargs = eval(f'api(e).{e}(i.system[e], kwargs)')
            #=====================================================
            # Configure Network and Volumes
            #=====================================================
            for e in ['network', 'volumes']:
                if i.get(e): kwargs = eval(f'api(e).{e}(i[e], kwargs)')
            validating.end_loop('cluster', i.name)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('pure_storage', self.type)
        return kwargs


    #=====================================================
    # Pure Storage Node Creation
    #=====================================================
    def network(self, i, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section('pure_storage', self.type)
        #=====================================================
        # Get Existing Storage Aggregates
        #=====================================================
        for node in i.nodes:
            validating.begin_section('node', node.name)
            node = DotMap(deepcopy(node))
            kwargs.pure_storage[node.name].interfaces = {}
            kwargs.pure_storage[node.name]['aggregates'] = {}
            #=====================================================
            # Create/Patch Storage Aggregates
            #=====================================================
            pcolor.LightPurple(f"\n    Get Existing Storage Aggregates")
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
            if print_payload: pcolor.Cyan(json.dumps(polVars, indent=4))
            pcolor.LightPurple(f"\n    Configuring Storage Aggregate {aggregate}")
            eval(f"{method}(uri, kwargs, payload)")
            pcolor.LightPurple(f"\n    Add Storage Aggregate to Dictionaries")
            uri = 'storage/aggregates'
            storageAggs = get(uri, kwargs)
            for r in storageAggs['records']:
                r = DotMap(deepcopy(r))
                if r.name == aggregate:
                    kwargs.pure_storage[node.name]['aggregates'].update({"name":aggregate,"uuid":r.uuid})
            #=====================================================
            # Update Interfaces on the Nodes
            #=====================================================
            pcolor.LightPurple(f"\n    Get Existing Ethernet Port Records.")
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
                        kwargs.pure_storage[node.name].interfaces.update({r.name:r.uuid})
                    for dp in lacp.lag.member_ports:
                        if r.name == dp.name: kwargs.pure_storage[node.name].interfaces.update({r.name:r.uuid})
                #=====================================================
                # Create/Patch the LAG - a0a
                #=====================================================
                uri = 'network/ethernet/ports'
                if method == 'patch': uri = f'network/ethernet/ports/{kwargs.pure_storage[node.name].interfaces["a0a"]}'
                polVars.update({"node": {"name":node.name}})
                polVars['broadcast_domain'].update(
                    {"uuid": kwargs.pure_storage.broadcast_domains[lacp.broadcast_domain.name]})
                for dp in polVars['lag']['member_ports']:
                    dp.update({
                        "uuid": kwargs.pure_storage[node.name].interfaces[dp['name']],
                        "node": {"name": node['name']}})
                if method == 'patch':
                    pop_list = ['distribution_policy', 'mode']
                    for p in pop_list: polVars['lag'].pop(p)
                    pop_list = ['node', 'type']
                    for p in pop_list: polVars.pop(p)
                payload = json.dumps(polVars)
                if print_payload: pcolor.Cyan(json.dumps(polVars, indent=4))
                eval(f"{method}(uri, kwargs, payload)")
                uri = f'network/ethernet/ports?node.name={node.name}'
                #=====================================================
                # Get UUID For the LAG
                #=====================================================
                ethResults = get(uri, kwargs)
                method = 'post'
                for r in ethResults['records']:
                    r = DotMap(deepcopy(r))
                    if r.name == 'a0a': kwargs.pure_storage[node.name].interfaces.update({'a0a': r.uuid})
            #=====================================================
            # Create/Patch the VLAN Interfaces for the LAG
            #=====================================================
            uri = f'network/ethernet/ports?fields=broadcast_domain,node,type,vlan&node.name={node.name}'
            ethResults = get(uri, kwargs)
            for v in node.interfaces.vlan:
                intf_name = f'a0a-{v.vlan.tag}'
                pcolor.LightPurple(f"\n    Beginning Configuration for VLAN Interface {intf_name}.")
                polVars = deepcopy(v.toDict())
                uri = 'network/ethernet/ports'
                method = 'post'
                polVars['broadcast_domain'].update({
                    "uuid": kwargs.pure_storage.broadcast_domains[v.broadcast_domain.name]})
                polVars.update({"node": node.name})
                polVars['vlan']['base_port'].update({
                    "node": {"name": node.name},
                    "uuid": kwargs.pure_storage[node.name].interfaces['a0a']})
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
                                if r.vlan.tag == v.vlan.tag: method = 'skip'
                if method == 'skip':
                    pcolor.Cyan(f"      * Skipping VLAN Interface {intf_name}.  API Matches Defined Config.")
                elif re.search('patch|post', method):
                    payload = json.dumps(polVars)
                    if print_payload: pcolor.Cyan(json.dumps(polVars, indent=4))
                    pcolor.Green(f"    * Configuring VLAN Interface {intf_name}.")
                    eval(f"{method}(uri, kwargs, payload)")
                pcolor.LightPurple(f"    Completed Configuration for VLAN Interface {intf_name}.")
            pcolor.Cyan('')
            uri = f'network/ethernet/ports?fields=node,type,vlan&node.name={node.name}'
            intfData = get(uri, kwargs)
            for v in node.interfaces.vlan:
                intf_name = f'a0a-{v.vlan.tag}'
                for r in intfData['records']:
                    r = DotMap(deepcopy(r))
                    if r.type == 'vlan':
                        if r.vlan.tag == v.vlan.tag:
                            kwargs.pure_storage[node.name].interfaces.update({intf_name:r.uuid})
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
        validating.end_section('pure_storage', self.type)
        return kwargs


    #=============================================================================
    # Function: Pure Storage - Pure1 Support Configuration
    #=============================================================================
    def pure1_support(self, i, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        imap = DotMap(
            phone_home = 'phonehome_enabled',
            proxy_server = 'proxy')
        validating.begin_section('pure_storage', self.type)
        uri  = 'support'
        rdata = DotMap((get(uri, kwargs))['items'][0])
        method = 'blank'
        payload = {}
        for k, v in i.items():
            if not rdata[imap[k]] == v:
                method = 'patch'
                payload.update({imap[k]:v})
        if method == 'patch':
            if 'PASSWORD' in payload['proxy']:
                kwargs.sensitive_var = 'proxy_server_password'
                kwargs  = ezfunctions.sensitive_var_value(kwargs)
                payload['proxy'] = payload['proxy'].replace('PASSWORD', kwargs.var_value)
            if print_payload: pcolor.Cyan(json.dumps(payload, indent=4))
            patch(uri, kwargs, json.dumps(payload))
        else: pcolor.Cyan(f"    - Skipping Pure1 Support Configuration.  API Matches Defined Config.")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('pure_storage', self.type)
        return kwargs


    #=============================================================================
    # Function: Pure Storage - SMI-S Configuration
    #=============================================================================
    def smi_s(self, i, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        imap = DotMap(
            service_location_protocol = 'slp_enabled',
            smi_s_provider = 'wbem_https_enabled')
        validating.begin_section('pure_storage', self.type)
        uri  = 'smi-s'
        rdata = DotMap((get(uri, kwargs))['items'][0])
        method = 'blank'
        payload = {}
        for k, v in i.items():
            if not rdata[imap[k]] == v:
                method = 'patch'
                payload.update({imap[k]:v})
        if method == 'patch':
            if print_payload: pcolor.Cyan(json.dumps(payload, indent=4))
            patch(uri, kwargs, json.dumps(payload))
        else: pcolor.Cyan(f"    - Skipping SMI-S Configuration.  API Matches Defined Config.")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('pure_storage', self.type)
        return kwargs


    #=====================================================
    # Pure Storage SNMP Creation
    #=====================================================
    def snmp(self, i, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section('pure_storage', self.type)
        #=====================================================
        # Get Auth and Privilege Passwords
        #=====================================================
        kwargs.sensitive_var = 'pure_storage_snmp_auth'
        kwargs = ezfunctions.sensitive_var_value(kwargs)
        pure_storage_snmp_auth = kwargs['var_value']
        kwargs.sensitive_var = 'pure_storage_snmp_priv'
        kwargs = ezfunctions.sensitive_var_value(kwargs)
        pure_storage_snmp_priv = kwargs['var_value']
        for snmp in i.snmp:
            #=====================================================
            # Configure SNMP Global Settings
            #=====================================================
            polVars = deepcopy(snmp.toDict())
            polVars.pop('users')
            polVars.pop('traps')
            payload = json.dumps(polVars)
            if print_payload: pcolor.Cyan(json.dumps(polVars, indent=4))
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
                        "authentication_password": pure_storage_snmp_auth,
                        "privacy_password": pure_storage_snmp_priv})
                    payload = json.dumps(userVars)
                    if print_payload: pcolor.Purple(json.dumps(userVars, indent=4))
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
                    if print_payload: pcolor.Purple(json.dumps(trapVars, indent=4))
                    eval(f"{method}(uri, kwargs, payload)")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('pure_storage', self.type)
        return kwargs


    #=============================================================================
    # Function: Pure Storage - Syslog Configuration
    #=============================================================================
    def syslog(self, i, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section('pure_storage', self.type)
        uri  = 'syslog-servers'
        rdata = DotMap((get(uri, kwargs))['items'])
        for e in i.servers:
            indx = next((index for (index, d) in enumerate(rdata) if d['name'] == e), None)
            method = 'blank'
            payload = {'name':e,'uri':f'{i.protocol}://{e}:{i.port}',}
            if indx == None: method = 'post'
            else:
                for k,v in payload.items():
                    if not rdata[indx][k] == v: method = 'patch'
            if re.search('patch|post', method):
                if print_payload: pcolor.Cyan(json.dumps(payload, indent=4))
                eval(f'{method}(uri, kwargs, json.dumps(payload))')
            else: pcolor.Cyan(f"    - Skipping Syslog {e}.  API Matches Defined Config.")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('pure_storage', self.type)
        return kwargs


    #=============================================================================
    # Function: Pure Storage - SMI-S Configuration
    #=============================================================================
    def smi_s(self, i, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        imap = DotMap(
            gui_idle_timeout = 'slp_enabled',
            login_banner = 'wbem_https_enabled')
        validating.begin_section('pure_storage', self.type)
        uri  = 'smi-s'
        rdata = DotMap((get(uri, kwargs))['items'][0])
        method = 'blank'
        payload = {}
        for k, v in i.items():
            if not rdata[imap[k]] == v:
                method = 'patch'
                payload.update({imap[k]:v})
        if method == 'patch':
            if print_payload: pcolor.Cyan(json.dumps(payload, indent=4))
            patch(uri, kwargs, json.dumps(payload))
        else: pcolor.Cyan(f"    - Skipping SMI-S Configuration.  API Matches Defined Config.")
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('pure_storage', self.type)
        return kwargs


    #=====================================================
    # Pure Storage Volumes Creation
    #=====================================================
    def volumes(self, i, kwargs):
        #=====================================================
        # Send Notification
        #=====================================================
        validating.begin_section('pure_storage', self.type)
        pcolor.Cyan('\n\n')
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'pure_storage')
        return kwargs


#=======================================================
# Build Storage Class
#=======================================================
class build(object):
    def __init__(self, type):
        self.type = type

    #=============================================================================
    # Function: Pure Storage - Cluster
    #=============================================================================
    def array(self, item, name, kwargs):
        item.name = name
        #=====================================================
        # Build Cluster Dictionary
        #=====================================================
        polVars = dict(
            dns_domains  = kwargs.dns_domains,
            hostname     = name + '.' + kwargs.dns_domains[0],
            host_prompt  = item.host_prompt,
            management_interfaces = [dict(name= "management", ip  = dict( address = kwargs.ooband.controller[0] ))],
            name         = name,
            name_servers = kwargs.dns_servers,
            ntp_servers  = kwargs.ntp_servers,
            timezone     = kwargs.timezone,
            username     = item.username)
        if item.get('system'):
            #=====================================================
            # Add Policy Variables to imm_dict
            #=====================================================
            polVars = dict(polVars, **item.system.toDict())
            kwargs.class_path = f'pure_storage,system'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        kwargs.pure_storage.hostname   = name + '.' + kwargs.dns_domains[0]
        kwargs.pure_storage.host_prompt= item.host_prompt
        kwargs.pure_storage.username   = item.username
        #=====================================================
        # Loop Through item List and Add to imm_dict
        #=====================================================
        #for i in ['network', 'volumes']:
        #    polVars = eval(f"build(i).{i}(item, kwargs)")
        #    kwargs.class_path = f'pure_storage,{i}'
        #    kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


     #=============================================================================

    #=============================================================================
    # Function - Pure Storage - Network Configuration
    #=============================================================================
    def network(self, i):
        #=====================================================
        # Add Mirror Volumes
        #=====================================================
        volList = []
        for x in range(0,len(i.nodes.node_list)):
            name =i.svm[f'm0{x+1}']
            volList.append({
                "aggregate": i.svm[f'agg{x+1}'],
                "name": name,
                "os_type": "pure_storage",
                "protocol": "local",
                "size": 1,
                "type": "DP",
                "volume_type": "mirror"})
        #=====================================================
        # Volume Input Dictionary
        #=====================================================
        jDict = sorted(i.svm.volumes, key=lambda ele: ele.size, reverse=True)
        for x in range(0,len(jDict)):
            volDict = DotMap(jDict[x])
            if x % 2 == 0: agg = i.svm.agg1
            else: agg = i.svm.agg2
            volList.append({
                "aggregate": agg,
                "name": volDict.name,
                "os_type": volDict.os_type,
                "protocol": volDict.protocol,
                "size": volDict.size,
                "type": "rw",
                "volume_type": volDict.volume_type})
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
                "nas": {"path": f"/{path}", "security_style": "unix",},
                "os_type": i.os_type,
                "protocol": i.protocol,
                "size": f"{i.size}GB",
                "snapshot_policy": "none",
                "state": "online",
                "style": "flexvol",
                "svm":{"name":i.svm.name},
                "type":i.type,
                "volume_type":i.volume_type}
            volumeList.append(polVars)
        polVars = volumeList
        #=====================================================
        # Return polVars
        #=====================================================
        return polVars

    #=============================================================================
    # Function - Pure Storage - Storage Volumes
    #=============================================================================
    def volumes(self, i):
        #=====================================================
        # Add Mirror Volumes
        #=====================================================
        volList = []
        for x in range(0,len(i.nodes.node_list)):
            name =i.svm[f'm0{x+1}']
            volList.append({
                "aggregate": i.svm[f'agg{x+1}'],
                "name": name,
                "os_type": "pure_storage",
                "protocol": "local",
                "size": 1,
                "type": "DP",
                "volume_type": "mirror"})
        #=====================================================
        # Volume Input Dictionary
        #=====================================================
        jDict = sorted(i.svm.volumes, key=lambda ele: ele.size, reverse=True)
        for x in range(0,len(jDict)):
            volDict = DotMap(jDict[x])
            if x % 2 == 0: agg = i.svm.agg1
            else: agg = i.svm.agg2
            volList.append({
                "aggregate": agg,
                "name": volDict.name,
                "os_type": volDict.os_type,
                "protocol": volDict.protocol,
                "size": volDict.size,
                "type": "rw",
                "volume_type": volDict.volume_type})
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
                "nas": {"path": f"/{path}", "security_style": "unix",},
                "os_type": i.os_type,
                "protocol": i.protocol,
                "size": f"{i.size}GB",
                "snapshot_policy": "none",
                "state": "online",
                "style": "flexvol",
                "svm":{"name":i.svm.name},
                "type":i.type,
                "volume_type":i.volume_type}
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
    ##=====================================================
    ## Generate API Token if Undefined
    ##=====================================================
    #if not kwargs.pure_storage.get('api_token'):
    #    #=====================================================
    #    # Add Sensitive Passwords to env
    #    #=====================================================
    #    kwargs.sensitive_var = 'pure_storage_password'
    #    kwargs = ezfunctions.sensitive_var_value(kwargs)
    #    #=====================================================
    #    # Run the PowerShell Script
    #    #=====================================================
    #    hostname = kwargs.pure_storage.hostname
    #    out_file = f'{kwargs.home}{os.sep}pure_storage.json'
    #    username = kwargs.pure_storage.username
    #    if platform.system() == 'Windows': pwsh = 'powershell.exe'
    #    else: pwsh = 'pwsh'
    #    cmd_options = [
    #        pwsh, '-ExecutionPolicy', 'Unrestricted', '-File', '/usr/bin/ezpure_login.ps1',
    #        '-e', hostname, '-o', out_file, '-u', username]
    #    results = subprocess.run(
    #        cmd_options, stdout = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True)
    #    pcolor.LightPurple(results.returncode)  # 0 = SUCCESS, NON-ZERO = FAIL  
    #    pcolor.LightPurple(results.stdout)      # Print Output
    #    pcolor.LightPurple(results.stderr)      # Print any Error Output
    #    jdata = DotMap(json.load(open(out_file, 'r')))
    #    os.remove(out_file)
    #    kwargs.pure_storage.api_token = jdata.api_token
    jdata = DotMap(api_version = '2.17')
    kwargs.pure_storage.api_token = '60c2115f-dd54-17e0-45c8-96c039e1c111'
    def login_to_pure_api(kwargs):
        kwargs.pure_storage.time = datetime.now()
        r = ''
        while r == '':
            url = f"https://{kwargs.pure_storage.hostname}"
            api_token = kwargs.pure_storage.api_token
            try: r = requests.post(url=f'{url}/api/2.0/login', headers={'api-token':api_token}, verify=False)
            except requests.exceptions.ConnectionError as e:
                pcolor.Red("Connection error, pausing before retrying. Error: %s" % (e))
                time.sleep(5)
            except Exception as e:
                pcolor.Red(f'{url}/api/2.0/login')
                pcolor.Red(f"!!! ERROR !!! Method {section[:-5]} Failed. Exception: {e}")
                sys.exit(1)
        if r.status_code != 200: pcolor.Red(f"!!! ERROR !!! Login to {kwargs.url} Failed."); sys.exit(1)
        else: kwargs.pure_storage.x_auth_token = r.headers['x-auth-token']
        kwargs.pure_storage.url = f"https://{kwargs.pure_storage.hostname}/api/{jdata.api_version}/"
        return kwargs
    if not kwargs.pure_storage.get('time'): kwargs = login_to_pure_api(kwargs)
    else:
        if kwargs.pure_storage.time + timedelta(minutes=30) < datetime.now(): kwargs = login_to_pure_api(kwargs)
    return kwargs

#=====================================================
# Function - API - delete
#=====================================================
def delete(uri, kwargs, section=''):
    kwargs = auth(kwargs)
    r = ''
    while r == '':
        try:
            x_auth_token = kwargs.pure_storage.x_auth_token
            url = kwargs.pure_storage.url
            pcolor.Cyan(f"     * delete: {f'{url}{uri}'}")
            r = requests.delete(f'{url}{uri}', headers={'x-auth-token':x_auth_token}, verify=False)
            if print_response_always: pcolor.Red(f"delete: {url}{uri} status_code: {r.status_code}")
            if r.status_code == 200: return r.json()
            else: validating.error_request_pure_storage('delete', r.status_code, r.text, uri)
        except requests.exceptions.ConnectionError as e:
            pcolor.Red(f'{url}{uri}')
            pcolor.Red("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            pcolor.Red(f'{url}{uri}')
            pcolor.Red("!!! ERROR !!! Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

#=====================================================
# Function - API - get
#=====================================================
def get(uri, kwargs, section=''):
    kwargs = auth(kwargs)
    r = ''
    while r == '':
        try:
            x_auth_token = kwargs.pure_storage.x_auth_token
            url = kwargs.pure_storage.url
            pcolor.Cyan(f"     * get: {f'{url}{uri}'}")
            r = requests.get(f'{url}{uri}', headers={'x-auth-token':x_auth_token}, verify=False)
            if print_response_always: pcolor.Purple(f"     * get: {url}{uri} status_code: {r.status_code}")
            if r.status_code == 200: return r.json()
            else: validating.error_request_pure_storage('get', r.status_code, r.text, uri)
        except requests.exceptions.ConnectionError as e:
            pcolor.Red(f'{url}{uri}')
            pcolor.Red("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            pcolor.Red(f'{url}{uri}')
            pcolor.Red("!!! ERROR !!! Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

#=====================================================
# Function - API - patch
#=====================================================
def patch(uri, kwargs, payload, section=''):
    kwargs = auth(kwargs)
    r = ''
    while r == '':
        try:
            x_auth_token = kwargs.pure_storage.x_auth_token
            url = kwargs.pure_storage.url
            pcolor.Cyan(f"     * patch: {f'{url}{uri}'}")
            r = requests.patch(f'{url}{uri}', data=payload, headers={'x-auth-token':x_auth_token}, verify=False)
            if print_response_always: pcolor.Purple(f"     * patch: {url}{uri} status_code: {r.status_code}")
            if re.search('20[0-2]', str(r.status_code)): return r.json()
            else: validating.error_request_pure_storage('patch', r.status_code, r.text, uri)
        except requests.exceptions.ConnectionError as e:
            pcolor.Red(f'{url}{uri}')
            pcolor.Red("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            pcolor.Red(f'{url}{uri}')
            pcolor.Red("!!! ERROR !!! Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)

#=====================================================
# Function - API - post
#=====================================================
def post(uri, kwargs, payload, section=''):
    kwargs = auth(kwargs)
    r = ''
    while r == '':
        try:
            x_auth_token = kwargs.pure_storage.x_auth_token
            url = kwargs.pure_storage.url
            pcolor.Cyan(f"     * post: {f'{url}{uri}'}")
            r = requests.post(f'{url}{uri}', data=payload, headers={'x-auth-token':x_auth_token}, verify=False)
            if print_response_always: pcolor.Red(f"     * post: {url}{uri} status_code: {r.status_code}")
            if re.search('20[0-2]', str(r.status_code)): return r.json()
            else: validating.error_request_pure_storage('post', r.status_code, r.text, uri)
        except requests.exceptions.ConnectionError as e:
            pcolor.Red(f'{url}{uri}')
            pcolor.Red("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            pcolor.Red(f'{url}{uri}')
            pcolor.Red("!!! ERROR !!! Method %s Failed. Exception: %s" % (section[:-5], e))
            sys.exit(1)
