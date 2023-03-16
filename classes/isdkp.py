from copy import deepcopy
import ezfunctions
import isdk
import json
import os
import re
import sys
import time
import validating

serial_regex = re.compile('^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$')
part1 = '(ethernet|fibre_channel)_qos|fc_zone|flow_control|link_aggregation'
part2 = 'multicast|ntp|port|power|serial_over_lan|thermal|virtual_kvm'
skip_regex = re.compile(f'^({part1}|{part2})$')

#=======================================================
# Policies Class
#=======================================================
class api_policies(object):
    def __init__(self, type):
        self.type = type

    #=======================================================
    # BIOS Policy Modification
    #=======================================================
    def bios(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['bios']['template_tuning']
        for k, v in apiBody.items():
            if type(v) == int or type(v) == float: apiBody[k] = str(v)
        if item.get('bios_template'):
            template = item['bios_template']
            if '_tpm' in template:
                btemplate = template.replace('_tpm', '')
                apiBody = dict(apiBody, **jsonVars[btemplate])
                apiBody = dict(apiBody, **jsonVars['tpm'])
            else:
                apiBody = dict(apiBody, **jsonVars[template])
                apiBody = dict(apiBody, **jsonVars['tpm_disabled'])
        return apiBody

    #=======================================================
    # Boot Order Policy Modification
    #=======================================================
    def boot_order(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['boot_order']
        if item.get('boot_devices'):
            apiBody['boot_devices'] = []
            for i in item['boot_devices']:
                boot_dev = {'class_id':i['object_type'],'name':i['name'],'object_type':i['object_type']}
                if re.search('(Iscsi|LocalDisk|Nvme|PchStorage|San|SdCard)', i['object_type']
                             ) and apiBody['configured_boot_mode'] == 'Uefi':
                    boot_dev['Bootloader'] = {'class_id':'boot.Bootloader','object_type':'boot.Bootloader'}
                    if 'bootloader' in i:
                        jVars1 = jsonVars['key_map_loader']
                        for k, v in i.items():
                            if k in jVars1: boot_dev['Bootloader'].update({jVars1[k]:v})
                    else: boot_dev['Bootloader'].update({'Name':'BOOTx64.EFI','Path':"\\EFI\\BOOT\\"})
                jVars1 = jsonVars['key_map_boot']
                for k, v in i.items():
                    if k in jVars1:
                        boot_dev.update({jVars1[k]:v})
                apiBody['boot_devices'].append(boot_dev)
        return apiBody

    #=======================================================
    # Ethernet Adapter Policy Modification
    #=======================================================
    def ethernet_adapter(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['ethernet_adapter']['template_tuning']
        if item.get('adapter_template'):
            template = item['adapter_template']
            apiBody = dict(apiBody, **jsonVars[template])
        return apiBody

    #=======================================================
    # Ethernet Network Control Policies Policy Modification
    #=======================================================
    def ethernet_network_control(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['ethernet_network_control']['key_map']
        for k, v in item.items():
            if 'lldp' in k:
                if not apiBody.get('lldp_settings'): apiBody['lldp_settings'] = {}
                apiBody['lldp_settings'].update({jsonVars[k]:v})
                apiBody.pop(jsonVars[k])
        return apiBody

    #=======================================================
    # Ethernet Network Group Policies Policy Modification
    #=======================================================
    def ethernet_network_group(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['bios']['template_tuning']
        apiBody.update({'vlan_settings':{'object_type':'fabric.VlanSettings'}})
        klist = ['allowed_vlans','native_vlan']
        for i in klist:
            if i in item:
                if i == 'native_vlan':
                    apiBody['vlan_settings'].update({i:int(item[i])})
                else: apiBody['vlan_settings'].update({i:item[i]})
        return apiBody

    #=======================================================
    # Fibre-Channel Adapter Policy Modification
    #=======================================================
    def fibre_channel_adapter(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['fibre_channel_adapter']['template_tuning']
        if item.get('adapter_template'):
            template = item['adapter_template']
            apiBody = dict(apiBody, **jsonVars[template])
        return apiBody

    #=======================================================
    # Fibre-Channel Network Policies Policy Modification
    #=======================================================
    def fibre_channel_network(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['fibre_channel_network']['key_map']
        apiBody.update({'vsan_settings':{'object_type':'vnic.VsanSettings'}})
        for k, v in item.items():
            if re.search('(default_)?(v(l|s)an(_id)?)', k) and k in jsonVars:
                apiBody['vsan_settings'].update({jsonVars[k]:v})
                apiBody.pop(jsonVars[k])
        return apiBody

    #=======================================================
    # IMC Access Policy Modification
    #=======================================================
    def imc_access(apiBody, item, pargs, **kwargs):
        kwargs = kwargs
        apiBody.update({'address_type':{'enable_ip_v4':True,'enable_ip_v6':False,}})
        addfam = ['v4', 'v6']
        for i in addfam:
            add_config = f'ip{i}_address_configuration'
            if add_config in item:
                apiBody['address_type'].update({f'enable_ip_{i}':item[add_config]})
        #=====================================================
        # Attach Pools to the API Body
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.policy = 'ip'
        pargs.names = []
        ptype = ['inband_ip_pool', 'out_of_band_ip_pool']
        for i in ptype:
            if i in item: pargs.names.append(item[i])
        kwargs = isdk.api('ip').calls(pargs, **kwargs)
        for i in ptype:
            if i in item:
                apiBody.update({i:{
                    'class_id':'mo.MoRef','moid':kwargs['pmoids'][item[i]]['Moid'],'object_type':'ippool.Pool'
                }})
        return apiBody

    #=======================================================
    # IPMI over LAN Policy Modification
    #=======================================================
    def ipmi_over_lan(apiBody, item, pargs, **kwargs):
        item = item
        pargs = pargs
        if not os.environ.get('TF_VAR_ipmi_key') == None:
            apiBody.update({'encryption_key':os.environ.get('TF_VAR_ipmi_key')})
        else:
            kwargs['Variable'] = f"ipmi_key"
            kwargs = ezfunctions.sensitive_var_value(**kwargs)
            apiBody.update({'encryption_key':kwargs['var_value']})
        return apiBody

    #=======================================================
    # LAN Connectivity Policy Modification
    #=======================================================
    def lan_connectivity(apiBody, item, pargs, **kwargs):
        item   = item
        kwargs = kwargs
        if not apiBody.get('vnic_placement_mode'): apiBody.update({'placement_mode':'custom'})
        else: apiBody.pop('vnic_placement_mode')
        return apiBody

    #=======================================================
    # Link Control Policy Modification
    #=======================================================
    def link_control(apiBody, item, pargs, **kwargs):
        kwargs = kwargs
        if item.get('admin_state'): apiBody['udld_settings'] = {'admin_state':item['admin_state']}
        if item.get('mode'):
            if not apiBody.get('udld_settings'): apiBody['udld_settings']
            apiBody['udld_settings'].update({'mode':item['mode']})
        return apiBody

    #=======================================================
    # Local User Policy Modification
    #=======================================================
    def local_user(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['local_user']['key_map_password']
        for k, v in item.items():
            if k in jsonVars:
                if not apiBody.get('password_properties'): apiBody['password_properties'] = {}
                apiBody['password_properties'].update({jsonVars[k]:v})
        return apiBody

    #=====================================================
    # Assign Users to Local User Policies
    #=====================================================
    def local_users(self, pargs, **kwargs):
        #=====================================================
        # Get Existing Users
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.names = []
        pargs.policy = 'local_users'
        for i in pargs.item: pargs.names.append(i['username'])
        kwargs = isdk.api('local_users').calls(pargs, **kwargs)
        user_moids = kwargs['pmoids']
        pargs.names  = []
        pargs.policy = 'iamrole'
        for i in pargs.item: pargs.names.append(i['role'])
        rnames = "', '".join(pargs.names).strip("', '")
        pargs.apiQuery = f"Name in ('{rnames}') and Type eq 'IMC'"
        kwargs = isdk.api('iamrole').calls(pargs, **kwargs)
        role_moids = kwargs['pmoids']
        pargs.names  = []
        pargs.policy = 'user_role'
        umoids = []
        for k, v in user_moids.items(): umoids.append(v['Moid'])
        umoids = "', '".join(umoids).strip("', '")
        pargs.apiQuery = f"EndPointUser.Moid in ('{umoids}')"
        kwargs = isdk.api('user_role').calls(pargs, **kwargs)
        urole_moids = kwargs['pmoids']
        pargs.pop('apiQuery')
        local_user_moid = pargs.pmoid
        #=====================================================
        # Construct API Body Users
        #=====================================================
        for i in pargs.item:
            apiBody = {'name':i['username']}
            apiBody = org_map(apiBody, pargs.org_moid)
            if not user_moids.get(i['username']):
                pargs.apiMethod = 'create'
                pargs.apiBody = apiBody
                kwargs = isdk.api(self.type).calls(pargs, **kwargs)
                user_moid = kwargs['pmoid']
            else: user_moid = user_moids[i['username']]['Moid']
            kwargs['Variable'] = f"local_user_password_{i['password']}"
            kwargs = ezfunctions.sensitive_var_value(**kwargs)
            #=====================================================
            # Create API Body for User Role
            #=====================================================
            if i.get('enabled'): apiBody = {'enabled':i['enabled']}
            else: apiBody = {}
            apiBody['password'] = kwargs['var_value']
            apiBody.update({'end_point_role':[{
                'class_id':'mo.MoRef','moid':role_moids[i['role']]['Moid'],'object_type':'iam.EndPointRole'
            }]})
            apiBody.update({'end_point_user':{
                'class_id':'mo.MoRef','moid':user_moid,'object_type':'iam.EndPointUser'
            }})
            apiBody.update({'end_point_user_policy':{
                'class_id':'mo.MoRef','moid':local_user_moid,'object_type':'iam.EndPointUserPolicy'
            }})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            if not urole_moids.get(user_moid): pargs.apiMethod = 'create'
            else:
                pargs.apiMethod = 'patch'
                pargs.pmoid = urole_moids[user_moid]['Moid']
            pargs.policy = 'user_role'
            pargs.purpose = i['username']
            pargs.apiBody = apiBody
            kwargs = isdk.api('user_role').calls(pargs, **kwargs)
        return kwargs

    #=======================================================
    # Network Connectivity Policy Modification
    #=======================================================
    def network_connectivity(apiBody, item, pargs, **kwargs):
        dns_list = ['v4', 'v6']
        kwargs   = kwargs
        for i in dns_list:
            if f'dns_servers_{i}' in item:
                if len(item[f'dns_servers_{i}']) > 0:
                    apiBody.update({f'preferred_ip{i}dns_server':item[f'dns_servers_{i}'][0]})
                if len(item[f'dns_servers_{i}']) > 1:
                    apiBody.update({f'alternate_ip{i}dns_server':item[f'dns_servers_{i}'][1]})
        return apiBody

    #=====================================================
    #  Policies Function
    #=====================================================
    def policies(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['key_map']
        policies = kwargs['immDict']['orgs'][kwargs['org']]['policies'][self.type]
        validating.begin_section(self.type, 'policies')
        #=====================================================
        # Get Existing Policies
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.org_moid  = kwargs['org_moids'][kwargs['org']]['Moid']
        pargs.policy    = self.type
        pargs.purpose   = self.type
        pargs.names = []
        for i in policies:
            if self.type == 'port':
                for x in range(0,len(i['names'])): pargs.names.append(i['names'][x])
            else: pargs.names.append(i['name'])
        kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        policy_moids = kwargs['pmoids']
        #=====================================================
        # Add Attributes to the apiBody
        #=====================================================
        def build_apiBody(apiBody, jsonVars, pargs, **kwargs):
            for k, v in item.items():
                if k in jsonVars: apiBody.update({jsonVars[k]:v})
            apiBody = org_map(apiBody, pargs.org_moid)
            if apiBody.get('tags'): apiBody['tags'].append(kwargs['ezData']['tags'])
            else: apiBody.update({'tags':[kwargs['ezData']['tags']]})
            return apiBody

        #=====================================================
        # Create/Patch the Policy via the Intersight API
        #=====================================================
        def policies_to_api(apiBody, pargs, **kwargs):
            pargs.apiBody = apiBody
            if policy_moids.get(apiBody['name']):
                pargs.apiMethod = 'patch'
                pargs.pmoid = policy_moids[apiBody['name']]['Moid']
            else: pargs.apiMethod = 'create'
            kwargs = isdk.api(self.type).calls(pargs, **kwargs)
            pargs.pmoid = kwargs['pmoid']
            return kwargs

        #=====================================================
        # Loop through Items
        #=====================================================
        for item in policies:
            if self.type == 'port':
                for x in range(0,len(i['names'])):
                    #=====================================================
                    # Construct apiBody Payload
                    #=====================================================
                    apiBody = {'name':item['names'][x]}
                    apiBody = build_apiBody(apiBody, jsonVars, pargs, **kwargs)
                    #kwargs = policies_to_api(apiBody, pargs, **kwargs)
            else:
                #=====================================================
                # Construct apiBody Payload
                #=====================================================
                apiBody = {}
                apiBody = build_apiBody(apiBody, jsonVars, pargs, **kwargs)
                #=====================================================
                # Add Policy Specific Settings
                #=====================================================
                if not re.search(skip_regex, self.type):
                    apiBody = eval(f'api_policies.{self.type}')(apiBody, item, pargs, **kwargs)
                pargs.policy = self.type
                kwargs = policies_to_api(apiBody, pargs, **kwargs)
            #=====================================================
            # Loop Thru Sub-Items
            #=====================================================
            if 'lan_connectivity' == self.type:
                if item.get('vnics'):
                    pargs.item = item['vnics']
                    kwargs = api_policies('vnics').vnics(pargs, **kwargs)
            elif 'local_user' == self.type:
                if item.get('users'):
                    pargs.item = item['users']
                    kwargs = api_policies('local_users').local_users(pargs, **kwargs)
            elif 'port' == self.type:
                #if item.get('port_modes'):
                #    pargs.item = item
                #    kwargs = api_policies('port_mode').port_mode(pargs, **kwargs)
                pargs.item = item
                kwargs = api_policies('ports').ports(pargs, **kwargs)
            elif 'san_connectivity' == self.type:
                if item.get('vhbas'):
                    pargs.item = item['vhbas']
                    kwargs = api_policies('vhbas').vhbas(pargs, **kwargs)
            elif 'storage' == self.type:
                if item.get('drive_groups'):
                    pargs.item = item['drive_groups']
                    kwargs = api_policies('storage_drive_group').storage_drive_group(pargs, **kwargs)
            elif 'vlan' == self.type:
                if item.get('vlans'):
                    pargs.item = item['vlans']
                    kwargs = api_policies('vlans').vlans(pargs, **kwargs)
            elif 'vsan' == self.type:
                if item.get('vsans'):
                    pargs.item = item['vsans']
                    kwargs = api_policies('vsans').vsans(pargs, **kwargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'policies')
        return kwargs

    #=====================================================
    # Port Modes for Port Policies
    #=====================================================
    def port_mode(self, pargs, **kwargs):
        #=====================================================
        # Get Port Policy
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.names  = []
        pargs.policy = 'port'
        pargs.names.extend(pargs.item['names'])
        kwargs = isdk.api('port').calls(pargs, **kwargs)
        port_moids = kwargs['pmoids']
        for x in range(0,len(pargs.item['names'])):
            #=====================================================
            # Confirm if the vHBAs are already Attached
            #=====================================================
            pargs.pmoid = port_moids[pargs.item['names'][x]]['Moid']
            port_moid = pargs.pmoid
            for i in pargs.item['port_modes']:
                pargs.apiMethod = 'get'
                pargs.policy = 'port_mode'
                pargs.apiQuery = f"PortIdStart eq {i['port_list'][0]} and PortPolicy.Moid eq '{port_moid}'"
                kwargs = isdk.api('port_mode').calls(pargs, **kwargs)
                pargs.pop('apiQuery')
                pm_moids = kwargs['pmoids']
                apiBody = {'object_type':'fabric.PortMode'}
                plist = i['port_list']
                apiBody.update({
                    'custom_mode':i['custom_mode'],'port_id_start':plist[0],'port_id_end':plist[1]
                })
                apiBody.update({'port_policy':{
                    'class_id':'mo.MoRef','moid':port_moid,'object_type':'fabric.PortPolicy'}})
                if i.get('slot_id'): apiBody.update({'slot_id':i['port_modes']['slot_id']})
                else: apiBody.update({'slot_id':1})
                #=====================================================
                # Create or Patch the Policy via the Intersight API
                #=====================================================
                if pm_moids.get(port_moid):
                    if pm_moids[port_moid].get(i['port_list'][0]):
                        pargs.apiMethod = 'patch'
                        pargs.pmoid = pm_moids[port_moid][i['port_list'][0]]['Moid']
                    else: pargs.apiMethod = 'create'
                else: pargs.apiMethod = 'create'
                pargs.apiMethod = 'create'
                pargs.policy = 'port_mode'
                pargs.purpose = 'port_mode'
                pargs.apiBody = apiBody
                kwargs = isdk.api('port_mode').calls(pargs, **kwargs)
        return kwargs

    #=====================================================
    # Assign Port Types to Port Policies
    #=====================================================
    def ports(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['port']
        #=====================================================
        # Create/Patch the Port Policy Port Types
        #=====================================================
        def api_calls(apiBody, pargs, **kwargs):
            #=====================================================
            # Check if the Port Policy Port Type Exists
            #=====================================================
            pargs.apiMethod = 'get'
            pargs.policy = pargs.type
            if re.search('port_channel', pargs.type):
                policy_name = int(apiBody['pc_id'])
                pargs.apiQuery = f"PcId eq {int(apiBody['pc_id'])} and PortPolicy.Moid eq '{pargs.port_policy}'"
            else:
                policy_name = int(apiBody['port_id'])
                pargs.apiQuery = f"PortId eq {int(apiBody['port_id'])} and PortPolicy.Moid eq '{pargs.port_policy}'"
            kwargs = isdk.api(pargs.policy).calls(pargs, **kwargs)
            pargs.pop('apiQuery')
            pargs.moids[pargs.type] = kwargs['pmoids']
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            if pargs.moids[pargs.type].get(pargs.port_policy):
                if pargs.moids[pargs.type][pargs.port_policy].get(policy_name):
                    pargs.apiMethod = 'patch'
                    pargs.pmoid = pargs.moids[pargs.type][pargs.port_policy][policy_name]['Moid']
                else: pargs.apiMethod = 'create'
            else: pargs.apiMethod = 'create'
            pargs.policy = pargs.type
            pargs.purpose = pargs.type
            pargs.apiBody = apiBody
            kwargs = isdk.api(pargs.type).calls(pargs, **kwargs)
            return kwargs
        #=====================================================
        # Create API Body for Port Policies
        #=====================================================
        def port_type_call(item, x, pargs, **kwargs):
            pargs.port_policy = pargs.pmoid
            for i in item[pargs.type]:
                apiBody = deepcopy(jsonVars['classes'][pargs.type])
                apiBody.update({'port_policy':{
                    'class_id':'mo.MoRef','moid':pargs.port_policy,'object_type':'fabric.PortPolicy'}})
                for z in pargs.policy_list:
                    if i.get(f'{z}_policy'):
                        if 'network_control' in z:
                            pkey = 'eth_network_control_policy'
                            otype = 'fabric.EthNetworkControlPolicy'
                        elif 'group' in z:
                            pkey = 'eth_network_group_policy'
                            otype = 'fabric.EthNetworkGroupPolicy'
                        elif 'flow' in z:
                            pkey = f'{z}_policy'
                            otype = 'fabric.FlowControlPolicy'
                        elif 'link_agg' in z:
                            pkey = f'{z}_policy'
                            otype = 'fabric.LinkAggregationPolicy'
                        elif 'link_control' in z:
                            pkey = f'{z}_policy'
                            otype = 'fabric.LinkControlPolicy'
                        if pargs.moids[z].get(i[f'{z}_policy']):
                            pmoid = pargs.moids[z][i[f'{z}_policy']]['Moid']
                        else:
                            ppname = pargs.port_policy_name
                            validating.error_policy_exist(pkey, i[f'{z}_policy'], pargs.type, 'Port Policy', ppname)
                        if not 'network_group' in pkey:
                            apiBody.update({pkey:{'class_id':'mo.MoRef','moid':pmoid,'object_type':otype}})
                        else: apiBody.update({pkey:[{'class_id':'mo.MoRef','moid':pmoid,'object_type':otype}]})
                if i.get('admin_speed'): apiBody.update({'admin_speed':i['admin_speed']})
                if i.get('fec'): apiBody.update({'fec':i['fec']})
                if i.get('mode'): apiBody.update({'mode':i['mode']})
                if i.get('priority'): apiBody.update({'priority':i['priority']})
                if re.search('port_channel', pargs.type):
                    if len(i['pc_ids']) > 1: apiBody.update({'pc_id':i['pc_ids'][x]})
                    else: apiBody.update({'pc_id':i['pc_id'][0]})
                    if i.get('vsan_ids'):
                        if len(i['vsan_ids']) > 1: apiBody.update({'vsan_id':i['vsan_ids'][x]})
                        else: apiBody.update({'vsan_id':i['vsan_ids'][0]})
                    apiBody['ports'] = []
                    for intf in i['interfaces']:
                        intfBody = {'class_id':'fabric.PortIdentifier','object_type':'fabric.PortIdentifier'}
                        intfBody.update({'port_id':intf['port_id']})
                        if intf.get('breakout_port_id'): intfBody.update(
                                {'aggregate_port_id':intf['breakout_port_id']})
                        else: intfBody.update({'aggregate_port_id':0})
                        if intf.get('slot_id'): intfBody.update({'slot_id':intf['slot_id']})
                        else: intfBody.update({'slot_id':1})
                        apiBody['ports'].append(intfBody)
                    kwargs = api_calls(apiBody, pargs, **kwargs)
                elif re.search('role', pargs.type):
                    interfaces = ezfunctions.vlan_list_full(i['port_list'])
                    for intf in interfaces:
                        intfBody = deepcopy(apiBody)
                        if i.get('breakout_port_id'): intfBody.update(
                                {'aggregate_port_id':intf['breakout_port_id']})
                        else: intfBody.update({'aggregate_port_id':0})
                        intfBody.update({'port_id':int(intf)})
                        if i.get('device_number'): intfBody.update({'preferred_device_id':i['device_number']})
                        if i.get('connected_device_type'): intfBody.update(
                                {'preferred_device_type':i['connected_device_type']})
                        if i.get('slot_id'): intfBody.update({'slot_id':intf['slot_id']})
                        else: intfBody.update({'slot_id':1})
                        kwargs = api_calls(intfBody, pargs, **kwargs)
            return kwargs

        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['port']
        #=====================================================
        # Get Policies
        #=====================================================
        pargs.policy_list = [
            'ethernet_network_control',
            'ethernet_network_group',
            'flow_control',
            'link_aggregation',
            'link_control'
        ]
        item = pargs.item
        pargs.apiMethod = 'get'
        pargs.names = pargs.item['names']
        pargs.policy = 'port'
        kwargs = isdk.api('port').calls(pargs, **kwargs)
        pargs.moids['port'] = kwargs['pmoids']
        for i in pargs.policy_list:
            pargs.names  = []
            pargs.policy = i
            for z in jsonVars['port_type_list']:
                if item.get(z):
                    for y in item[z]:
                        if y.get(f'{i}_policy'): pargs.names.append(y[f'{i}_policy'])
            kwargs = isdk.api(i).calls(pargs, **kwargs)
            pargs.moids[i] = kwargs['pmoids']
        #=====================================================
        # Create API Body for Port Types
        #=====================================================
        for x in range(0,len(item['names'])):
            for z in jsonVars['port_type_list']:
                if item.get(z):
                    #print(item)
                    pargs.port_policy_name = item['names'][x]
                    pargs.pmoid = pargs.moids['port'][item['names'][x]]['Moid']
                    pargs.type = z
                    port_type_call(item, x, pargs, **kwargs)
        return kwargs

    #=======================================================
    # SAN Connectivity Policy Modification
    #=======================================================
    def san_connectivity(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['san_connectivity']['key_map']
        pargs.names = []
        if item.get('wwnn_pool'): pargs.names.append(item['wwnn_pool'])
        pargs.apiMethod = 'get'
        pargs.policy = 'wwnn'
        kwargs = isdk.api('wwnn').calls(pargs, **kwargs)
        wwnn_moids = kwargs['pmoids']
        if not apiBody.get('vhba_placement_modes'): apiBody.update({'placement_mode':'custom'})
        if item.get('wwnn_pool'):
            fc_moid = wwnn_moids[item['wwnn_pool']]['Moid']
            apiBody.update({'wwnn_pool':{'class_id':'mo.MoRef','moid':fc_moid,'object_type':'fcpool.Pool'}})
        return apiBody

    #=======================================================
    # SNMP Policy Modification
    #=======================================================
    def snmp(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['bios']['template_tuning']
        for k, v in apiBody.items():
            if type(v) == int or type(v) == float: apiBody[k] = str(v)
        if item.get('bios_template'):
            template = item['bios_template']
            if '_tpm' in template:
                btemplate = template.replace('_tpm', '')
                apiBody = dict(apiBody, **jsonVars[btemplate])
                apiBody = dict(apiBody, **jsonVars['tpm'])
            else:
                apiBody = dict(apiBody, **jsonVars[template])
                apiBody = dict(apiBody, **jsonVars['tpm_disabled'])
        return apiBody

    #=======================================================
    # Storage Policy Modification
    #=======================================================
    def storage(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['bios']['template_tuning']
        for k, v in apiBody.items():
            if type(v) == int or type(v) == float: apiBody[k] = str(v)
        if item.get('bios_template'):
            template = item['bios_template']
            if '_tpm' in template:
                btemplate = template.replace('_tpm', '')
                apiBody = dict(apiBody, **jsonVars[btemplate])
                apiBody = dict(apiBody, **jsonVars['tpm'])
            else:
                apiBody = dict(apiBody, **jsonVars[template])
                apiBody = dict(apiBody, **jsonVars['tpm_disabled'])
        return apiBody

    #=====================================================
    # Assign Drive Groups to Storage Policies
    #=====================================================
    def storage_drive_group(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['storage']['virtual_drive_map']
        #=====================================================
        # Get Storage Policies
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.names = []
        pargs.policy = 'storage_drive_group'
        for i in pargs.item: pargs.names.append(i['name'])
        kwargs = isdk.api('storage_drive_group').calls(pargs, **kwargs)
        dg_moids = kwargs['pmoids']
        #=====================================================
        # Create API Body for Storage Drive Groups
        #=====================================================
        for i in pargs.item:
            #=====================================================
            # Create API Body for VLANs
            #=====================================================
            apiBody = {
                'class_id':'storage.DriveGroup', 'name':i['name'],
                'object_type':'storage.DriveGroup', 'raid_level':i['raid_level']
                }
            apiBody.update({'storage_policy':{
                'class_id':'mo.MoRef','moid':pargs.pmoid,'object_type':'storage.StoragePolicy'
            }})
            if i.get('manual_drive_group'):
                apiBody['manual_drive_group'] = {
                    'class_id':'storage.ManualDriveGroup','object_type':'storage.ManualDriveGroup'
                }
                if i['manual_drive_group'][0].get('dedicated_hot_spares'):
                    apiBody['manual_drive_group']['dedicated_hot_spares'] = i[
                        'manual_drive_group']['dedicated_hot_spares']
                apiBody['manual_drive_group']['span_groups'] = []
                for x in i['manual_drive_group'][0]['drive_array_spans']:
                    apiBody['manual_drive_group']['span_groups'].append({
                        'class_id':'storage.SpanDrives','object_type':'storage.SpanDrives','slots':x['slots']
                    })
            if i.get('virtual_drives'):
                apiBody['virtual_drives'] = []
                for x in i['virtual_drives']:
                    vdBody = {}
                    for k, v in x.items():
                        if k in jsonVars: vdBody.update({jsonVars[k]:v})
                    vdBody.update({'object_type':'storage.VirtualDriveConfiguration'})
                    if vdBody.get('virtual_drive_policy'):
                        vdBody['virtual_drive_policy'].update({'object_type':'storage.VirtualDrivePolicy'})
                    apiBody['virtual_drives'].append(vdBody)
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            if not dg_moids.get(i['name']): pargs.apiMethod = 'create'
            else:
                pargs.apiMethod = 'patch'
                pargs.pmoid = dg_moids[i['name']]['Moid']
            pargs.policy = 'storage_drive_group'
            pargs.purpose = 'storage_drive_group'
            pargs.apiBody = apiBody
            kwargs = isdk.api('storage_drive_group').calls(pargs, **kwargs)
        return kwargs

    #=======================================================
    # Switch Control Policy Modification
    #=======================================================
    def switch_control(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['switch_control']['mac_and_udld']
        apiBody.update({
            'mac_aging_settings':{
                'mac_aging_option':'Default', 'mac_aging_time':14500, 'object_type':'fabric.MacAgingSettings'
            },
            'udld_settings':{
                'message_interval':15,'recovery_action':'reset','object_type':'fabric.UdldGlobalSettings'
            }
        })
        for k, v in item.items():
            if k in jsonVars:
                if 'mac_' in k: apiBody['mac_aging_settings'].update({jsonVars[k]:v})
                elif 'udld_' in k: apiBody['udld_settings'].update({jsonVars[k]:v})
        return apiBody

    #=======================================================
    # Syslog Policy Modification
    #=======================================================
    def syslog(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['syslog']['remote_logging']
        if 'local_logging' in item:
            apiBody.update({'local_clients':[{
                'class_id':'syslog.LocalFileLoggingClient',
                'object_type':'syslog.LocalFileLoggingClient',
                'min_severity':item['local_logging']['minimum_severity']
            }]})
        if item.get('remote_logging'):
            apiBody['remote_clients'] = []
            for i in item['remote_logging']:
                rsyslog = {'class_id':'syslog.RemoteLoggingClient','object_type':'syslog.RemoteLoggingClient'}
                for k, v in i.items():
                    if k in jsonVars: rsyslog.update({jsonVars[k]:v})
                if not '0.0.0.0' in rsyslog: apiBody['remote_clients'].append(rsyslog)
            if len(apiBody['remote_clients']) == 0: apiBody.pop('remote_clients')
        return apiBody

    #=======================================================
    # System QoS Policy Modification
    #=======================================================
    def system_qos(apiBody, item, pargs, **kwargs):
        item   = item
        kwargs = kwargs
        for i in apiBody['classes']:
            i.update({'admin_state':i['state'],'name':i['priority'],'object_type':'fabric.QosClass'})
            i.pop('priority')
            i.pop('state')
        return apiBody

    #=====================================================
    # Assign VNICs to LAN Connectivity Policies
    #=====================================================
    def vhbas(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['key_map']
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        scp_moid = pargs.pmoid
        policy_list = [
            'fc_zone', 'fibre_channel_adapter', 'fibre_channel_network',
            'fibre_channel_qos', 'wwpn', 'vhbas'
        ]
        pargs.apiMethod = 'get'
        for item in policy_list:
            pargs.names  = []
            pargs.policy = item
            for i in pargs.item:
                if i.get(f'{item}_policy'): pargs.names.append(i[f'{item}_policy'])
                elif i.get(f'{item}_policies'): pargs.names.extend(i[f'{item}_policies'])
                elif i.get('names') and item == 'vhbas': pargs.names.extend(i['names'])
                elif i.get('wwpn_pools') and item == 'wwpn': pargs.names.extend(i['wwpn_pools'])
            kwargs = isdk.api(item).calls(pargs, **kwargs)
            pargs.moids[item] = kwargs['pmoids']
        #=====================================================
        # Create API Body for VNICs
        #=====================================================
        for i in pargs.item:
            vnic_count = len(i['names'])
            for x in range(0,vnic_count):
                fcap = pargs.moids['fibre_channel_adapter'][i['fibre_channel_adapter_policy']]['Moid']
                fcnp = pargs.moids['fibre_channel_network'][i['fibre_channel_network_policies'][x]]['Moid']
                fcqp = pargs.moids['fibre_channel_qos'][i['fibre_channel_qos_policy']]['Moid']
                apiBody = {'name':i['names'][x],'order':i['placement_pci_order'][x]}
                for k, v in i.items():
                    if k in jsonVars:
                        apiBody.update({jsonVars[k]:v})
                apiBody.update({'object_type':'vnic.FcIf'})
                apiBody.update({
                    'placement':{
                        'id':'MLOM','object_type':'vnic.PlacementSettings','pci_link':0,'uplink':0
                    }
                })
                if i.get('fc_zone_policies'):
                    apiBody.update({'fc_zone_policies':[]})
                    zcount = 0
                    for z in i['fc_zone_policies']:
                        fcz_moid = pargs.moids['fc_zone'][i['fc_zone_policies'][zcount]]['Moid']
                        zcount += 1
                        apiBody['fc_zone_policies'].append(
                            {'moid':fcz_moid,'object_type':'fabric.FcZonePolicy'}
                        )
                if i.get('placement_switch_id'):
                    apiBody['placement'].update({'switch_id':i['placement_switch_id']})
                else:
                    if x == 0: side = 'A'
                    else: side = 'B'
                    apiBody['placement'].update({'switch_id':side})
                place_list = ['placement_pci_links', 'placement_slot_ids', 'placement_uplink_ports']
                for p in place_list:
                    count = 0
                    if i.get(p): apiBody.pop(p); count += 1
                    if count == 1:
                        if len(item[p]) == 2: pval = item[p][x]
                        else: pval = item[p][0]
                        if 'slot' in p: pvar = 'id'
                        pvar = p.replace('placement_', '')
                        pvar = pvar.replace('s', '')
                        apiBody['placement'][pvar] = pval
                apiBody.update({
                    'fc_adapter_policy':{'class_id':'mo.MoRef','moid':fcap,'object_type':'vnic.FcAdapterPolicy'},
                    'fc_network_policy':{'class_id':'mo.MoRef','moid':fcnp,'object_type':'vnic.FcNetworkPolicy'},
                    'fc_qos_policy':{'class_id':'mo.MoRef','moid':fcqp,'object_type':'vnic.FcQosPolicy'},
                    'san_connectivity_policy':{
                        'class_id':'mo.MoRef','moid':scp_moid,'object_type':'vnic.SanConnectivityPolicy'
                    }
                })
                if i.get('vhba_type'):
                    apiBody.update({'type':i['vhba_type']})
                    apiBody.pop('vhba_type')
                else: apiBody.update({'type':'fc-initiator'})
                if i.get('wwpn_pools'):
                    wwpnpool = pargs.moids['wwpn'][i['wwpn_pools'][x]]['Moid']
                    apiBody.update({
                        'wwpn_address_type':'POOL',
                        'wwpn_pool':{'class_id':'mo.MoRef','moid':wwpnpool,'object_type':'fcpool.Pool'}
                    })
                #=====================================================
                # Create or Patch the VLANs via the Intersight API
                #=====================================================
                if not pargs.moids.vhbas.get(i['names'][x]): pargs.apiMethod = 'create'
                else:
                    pargs.apiMethod = 'patch'
                    pargs.pmoid = pargs.moids.vhbas[i['names'][x]]['Moid']
                pargs.policy = 'vhbas'
                pargs.purpose = 'vhbas'
                pargs.apiBody = apiBody
                kwargs = isdk.api('vhbas').calls(pargs, **kwargs)
        return kwargs

    #=======================================================
    # Virtual Media Policy Modification
    #=======================================================
    def virtual_media(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['virtual_media']['add_key_map']
        if item.get('add_virtual_media'):
            apiBody.update({'mappings':[]})
            for i in item['add_virtual_media']:
                vmedia_add = {}
                for k, v in i.items():
                    if k in jsonVars: vmedia_add.update({jsonVars[k]:v})
                vmedia_add.update({'object_type':'vmeida.Mapping'})
                apiBody['mappings'].append(vmedia_add)
        return apiBody

    #=======================================================
    # VLAN Policy Modification
    #=======================================================
    def vlan(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['bios']['template_tuning']
        for k, v in apiBody.items():
            if type(v) == int or type(v) == float: apiBody[k] = str(v)
        if item.get('bios_template'):
            template = item['bios_template']
            if '_tpm' in template:
                btemplate = template.replace('_tpm', '')
                apiBody = dict(apiBody, **jsonVars[btemplate])
                apiBody = dict(apiBody, **jsonVars['tpm'])
            else:
                apiBody = dict(apiBody, **jsonVars[template])
                apiBody = dict(apiBody, **jsonVars['tpm_disabled'])
        return apiBody

    #=====================================================
    # Assign VLANs to VLAN Policies
    #=====================================================
    def vlans(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['key_map']
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.names  = []
        pargs.policy = 'multicast'
        for i in pargs.item: pargs.names.append(i['multicast_policy'])
        kwargs = isdk.api('multicast').calls(pargs, **kwargs)
        mcast_moids = kwargs['pmoids']
        pargs.names  = []
        pargs.policy = 'vlans'
        for item in pargs.item:
            vlan_list = ezfunctions.vlan_list_full(item['vlan_list'])
            for i in vlan_list: pargs.names.append(i)
        kwargs = isdk.api('vlan').calls(pargs, **kwargs)
        vlans_moids = kwargs['pmoids']
        vlan_moid = pargs.pmoid
        #=====================================================
        # Create API Body for VNICs
        #=====================================================
        for i in pargs.item:
            vlan_list = ezfunctions.vlan_list_full(i['vlan_list'])
            for x in vlan_list:
                if type(x) == str: x = int(x)
                if re.search('^[\d]$', str(x)): zeros = '000'
                elif re.search('^[\d]{2}$', str(x)): zeros = '00'
                elif re.search('^[\d]{3}$', str(x)): zeros = '0'
                elif re.search('^[\d]{4}$', str(x)): zeros = ''
                if i['name'] == 'vlan': apiBody = {'name':f"{i['name']}{zeros}{x}"}
                else: apiBody = {'name':f"{i['name']}-vl{zeros}{x}"}
                for k, v in item.items():
                    if k in jsonVars: apiBody.update({jsonVars[k]:v})
                apiBody.update({'vlan_id':x})
                apiBody.update({'eth_network_policy':{
                    'class_id':'mo.MoRef','moid':vlan_moid, 'object_type':'fabric.EthNetworkPolicy'
                }})
                mcast_moid = mcast_moids[i['multicast_policy']]['Moid']
                apiBody.update({'multicast_policy':{
                    'class_id':'mo.MoRef', 'moid':mcast_moid, 'object_type':'fabric.MulticastPolicy'
                }})
                #=====================================================
                # Create or Patch the VLANs via the Intersight API
                #=====================================================
                if not vlans_moids.get(x): pargs.apiMethod = 'create'
                else:
                    pargs.apiMethod = 'patch'
                    pargs.pmoid = vlans_moids[x]['Moid']
                pargs.policy = 'vlans'
                pargs.purpose = 'vlans'
                pargs.apiBody = apiBody
                kwargs = isdk.api('vlans').calls(pargs, **kwargs)
        return kwargs

    #=====================================================
    # Assign VNICs to LAN Connectivity Policies
    #=====================================================
    def vnics(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['key_map']
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        lcp_moid = pargs.pmoid
        policy_list = [
            'ethernet_adapter',
            'ethernet_network_control',
            'ethernet_network_group',
            'ethernet_qos',
            'mac',
            'vnics'
        ]
        pargs.apiMethod = 'get'
        for item in policy_list:
            pargs.names  = []
            pargs.policy = item
            for i in pargs.item:
                if i.get(f'{item}_policy'): pargs.names.append(i[f'{item}_policy'])
                elif i.get('names') and item == 'vnics': pargs.names.extend(i['names'])
                elif i.get('mac_address_pools') and item == 'mac': pargs.names.extend(i['mac_address_pools'])
            kwargs = isdk.api(item).calls(pargs, **kwargs)
            pargs.moids[item] = kwargs['pmoids']
        #=====================================================
        # Create API Body for vNICs
        #=====================================================
        for i in pargs.item:
            vnic_count = len(i['names'])
            for x in range(0,vnic_count):
                ethap = pargs.moids['ethernet_adapter'][i['ethernet_adapter_policy']]['Moid']
                ethcp = pargs.moids['ethernet_network_control'][i['ethernet_network_control_policy']]['Moid']
                ethgp = pargs.moids['ethernet_network_group'][i['ethernet_network_group_policy']]['Moid']
                ethqp = pargs.moids['ethernet_qos'][i['ethernet_qos_policy']]['Moid']
                apiBody = {'name':i['names'][x],'order':i['placement_pci_order'][x]}
                apiBody.update({'class_id':'vnic.EthIf','object_type':'vnic.EthIf'})
                if not i.get('cdn_values'):
                    apiBody.update({'cdn':{'value':i['names'][x],'source':'vnic','object_type':'vnic.Cdn'}})
                else:
                    apiBody.update({
                        'cdn':{'value':i['cdn_values'][x],'source':i['cdn_source'],'object_type':'vnic.Cdn'}
                    })
                if i.get('enable_failover'): apiBody.update({'failover_enabled',apiBody['enable_failover']})
                apiBody.update({
                    'placement':{'id':'MLOM','object_type':'vnic.PlacementSettings','pci_link':0,'uplink':0}
                })
                if i.get('placement_switch_id'):
                    apiBody['placement'].update({'switch_id':i['placement_switch_id']})
                    apiBody.pop('placement_switch_id')
                else:
                    if x == 0: side = 'A'
                    else: side = 'B'
                    apiBody['placement'].update({'switch_id':side})
                place_list = ['placement_pci_links', 'placement_slot_ids', 'placement_uplink_ports']
                for p in place_list:
                    count = 0
                    if i.get(p): apiBody.pop(p); count += 1
                    if count == 1:
                        if len(item[p]) == 2: pval = item[p][x]
                        else: pval = item[p][0]
                        if 'slot' in p: pvar = 'id'
                        pvar = p.replace('placement_', '')
                        pvar = pvar.replace('s', '')
                        apiBody['placement'][pvar] = pval
                apiBody.update({
                    'eth_adapter_policy':{
                        'class_id':'mo.MoRef','moid':ethap,'object_type':'vnic.EthAdapterPolicy'
                    },
                    'fabric_eth_network_control_policy':{
                        'class_id':'mo.MoRef','moid':ethcp,'object_type':'fabric.EthNetworkControlPolicy'
                    },
                    'fabric_eth_network_group_policy':[{
                        'class_id':'mo.MoRef','moid':ethgp,'object_type':'fabric.EthNetworkGroupPolicy'
                    }],
                    'eth_qos_policy':{
                        'class_id':'mo.MoRef','moid':ethqp,'object_type':'vnic.EthQosPolicy'
                    },
                    'lan_connectivity_policy':{
                        'class_id':'mo.MoRef','moid':lcp_moid,'object_type':'vnic.LanConnectivityPolicy'
                    }
                })
                if i.get('mac_address_pools'):
                    macpool = pargs.moids['mac'][i['mac_address_pools'][x]]['Moid']
                    apiBody.update({
                        'mac_address_type':'POOL',
                        'mac_pool':{
                            'class_id':'mo.MoRef','moid':macpool,'object_type':'macpool.Pool'
                        }
                    })
                #=====================================================
                # Create or Patch the VLANs via the Intersight API
                #=====================================================
                if not pargs.moids.vnics.get(i['names'][x]): pargs.apiMethod = 'create'
                else:
                    pargs.apiMethod = 'patch'
                    pargs.pmoid = pargs.moids.vnics[i['names'][x]]['Moid']
                pargs.policy = 'vnics'
                pargs.purpose = 'vnics'
                pargs.apiBody = apiBody
                kwargs = isdk.api('vnics').calls(pargs, **kwargs)
        return kwargs

    #=======================================================
    # VSAN Policy Modification
    #=======================================================
    def vsan(apiBody, item, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['bios']['template_tuning']
        for k, v in apiBody.items():
            if type(v) == int or type(v) == float: apiBody[k] = str(v)
        if item.get('bios_template'):
            template = item['bios_template']
            if '_tpm' in template:
                btemplate = template.replace('_tpm', '')
                apiBody = dict(apiBody, **jsonVars[btemplate])
                apiBody = dict(apiBody, **jsonVars['tpm'])
            else:
                apiBody = dict(apiBody, **jsonVars[template])
                apiBody = dict(apiBody, **jsonVars['tpm_disabled'])
        return apiBody

    #=====================================================
    # Assign VSANs to VSAN Policies
    #=====================================================
    def vsans(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['key_map']
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.names  = []
        pargs.policy = 'vsans'
        vsan_moid = pargs.pmoid
        for i in pargs.item: pargs.names.append(str(i['vsan_id']))
        kwargs = isdk.api('vsans').calls(pargs, **kwargs)
        vsans_moids = kwargs['pmoids']
        for i in pargs.item:
                #=====================================================
                # Create API Body for the VSANs
                #=====================================================
                apiBody = {'fc_network_policy':{
                    'class_id':'mo.MoRef','moid':vsan_moid,'object_type':'fabric.FcNetworkPolicy'}}
                for k, v in i.items():
                    if k in jsonVars: apiBody.update({jsonVars[k]:v})
                if not apiBody.get('fcoe_vlan'): apiBody.update({'fcoe_vlan':i['vsan_id']})
                #=====================================================
                # Create or Patch the VSANs via the Intersight API
                #=====================================================
                if not vsans_moids.get(i['vsan_id']): pargs.apiMethod = 'create'
                else:
                    pargs.apiMethod = 'patch'
                    pargs.pmoid = vsans_moids[i['vsan_id']]['Moid']
                pargs.policy = 'vsans'
                pargs.purpose = 'vsans'
                pargs.apiBody = apiBody
                kwargs = isdk.api('vsans').calls(pargs, **kwargs)
        return kwargs

#=======================================================
# Pools Class
#=======================================================
class api_pools(object):
    def __init__(self, type):
        self.type = type
    #=======================================================
    # WWNN/WWPN ID Block Modification
    #=======================================================
    def fc(item, apiBody):
        if item.get('id_blocks'):
            apiBody.update({'IdBlocks':[]})
            for i in item['id_blocks']:
                apiBody['IdBlocks'].append({
                    'From':i['from'], 'ObjectType':'fcpool.Block', 'Size':i['size']
                })
        return apiBody

    #=======================================================
    # IP Block(s)/Configuration Modification
    #=======================================================
    def ip(item, apiBody):
        ip_list = ['IpV4', 'IpV6']
        for x in ip_list:
            xlower = x.lower()
            if item.get(f'{xlower}_blocks'):
                apiBody.update({f'{x}Blocks':[]})
                for i in item[f'{xlower}_blocks']:
                    apiBody[f'{x}Blocks'].append({
                        'From':i['from'], 'ObjectType':f'ippool.{x}Block', 'Size':i['size']
                    })
            if item.get(f'{xlower}_configuration'):
                ipcfg = item[f'{xlower}_configuration'][0]
                apiBody.update({f'{x}Config':{
                    'Gateway':ipcfg['gateway'], 'ObjectType':f'ippool.{x}Config',
                    'PrimaryDns':ipcfg['primary_dns'], 'SecondaryDns':ipcfg['secondary_dns']
                }})
                if '4' in xlower: apiBody[f'{x}Config'].update({'Netmask':ipcfg['netmask']})
                else: apiBody[f'{x}Config'].update({'Prefix':ipcfg['prefix']})
        return apiBody

    #=======================================================
    # MAC Block Modification
    #=======================================================
    def mac(item, apiBody):
        if item.get('mac_blocks'):
            apiBody.update({'MacBlocks':[]})
            for i in item['mac_blocks']:
                apiBody['MacBlocks'].append({
                    'From':i['from'], 'ObjectType':'macpool.Block', 'Size':i['size']
                })
        return apiBody

    #=====================================================
    #  Pools Function
    #=====================================================
    def pools(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        if re.search('ww(n|p)n', self.type):
            jsonVars = kwargs['ezData']['pools']['allOf'][1]['properties']['fc']['key_map']
        else:
            jsonVars = kwargs['ezData']['pools']['allOf'][1]['properties'][self.type]['key_map']
        pools = kwargs['immDict']['orgs'][kwargs['org']]['pools'][self.type]
        org_moid = kwargs['org_moids'][kwargs['org']]['Moid']
        validating.begin_section(self.type, 'pool')
        #=====================================================
        # Get Existing Pools
        #=====================================================
        pargs.names = []
        for i in pools: pargs.names.append(i['name'])
        pargs.apiMethod = 'get'
        pargs.policy    = self.type
        pargs.purpose   = self.type
        kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        #=====================================================
        # Loop through Items
        #=====================================================
        for item in pools:
            #=====================================================
            # Construct apiBody Payload
            #=====================================================
            apiBody = {}
            for k, v in item.items():
                if k in jsonVars: apiBody.update({jsonVars[k]:v})
            if not apiBody.get('assignment_order'): apiBody.update({'assignment_order':'sequential'})
            apiBody = org_map(apiBody, org_moid)
            if apiBody.get('tags'): apiBody['tags'].append(kwargs['ezData']['tags'])
            else: apiBody.update({'tags':[kwargs['ezData']['tags']]})
            #=====================================================
            # Add Pool Specific Attributes
            #=====================================================
            if re.search('ww(n|p)n', self.type): 
                apiBody.update({'pool_purpose':self.type.upper()})
                apiBody = api_pools.fc(item, apiBody)
            else: apiBody = eval(self.type)(item, apiBody)
            #=====================================================
            # Create/Patch the Pool via the Intersight API
            #=====================================================
            pargs.apiBody = apiBody
            if kwargs['pmoids'].get(apiBody['name']):
                pargs.apiMethod = 'patch'
                pargs.pmoid = kwargs['pmoids'][apiBody['name']]['Moid']
            else: pargs.apiMethod = 'create'
            kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'pool')
        return kwargs

    #=======================================================
    # UUID Block Modification
    #=======================================================
    def uuid(item, apiBody):
        if item.get('uuid_blocks'):
            apiBody.update({'UuidSuffixBlocks':[]})
            for i in item['uuid_blocks']:
                apiBody['UuidSuffixBlocks'].append({
                    'From':i['from'], 'ObjectType':'uuidpool.UuidBlock', 'Size':i['size']
                })
        return apiBody

#=======================================================
# Profiles Class
#=======================================================
class api_profiles(object):
    def __init__(self, type):
        self.type = type

    #=====================================================
    #  Profiles Function
    #=====================================================
    def profiles(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['policy_list']
        profiles  = kwargs['immDict']['orgs'][kwargs['org']]['profiles'][self.type]
        org_moid = kwargs['org_moids'][kwargs['org']]['Moid']
        validating.begin_section(self.type, 'profiles')
        #=====================================================
        # Setup Arguments
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.jsonVars  = jsonVars
        pargs.names     = []
        pargs.org_moid  = org_moid
        pargs.purpose   = self.type
        pargs.serials   = []
        pargs.templates = []
        #=================================
        # Compile List of Serial Numbers
        #=================================
        for item in profiles:
            if re.search('^(chassis|server)$', self.type):
                if 'server' == self.type:
                    if item.get['ucs_server_profile_template']:
                        pargs.templates.append(item['ucs_server_profile_template'])
                for i in item['targets']:
                    pargs.names.append(i['name'])
                    if i.get['serial_number']: pargs.serials.append(i['serial_number'])
            else:
                pargs.names.append(item['name'])
                if item.get('serial_numbers'): pargs.serials.append(item['serial_numbers'])
        #=================================
        # Compile List of Policies
        #=================================
        pargs.moids = {}
        for p in jsonVars['policy_list']:
            for item in profiles:
                if item.get[p]:
                    if not pargs.moids.get(p):
                        kwargs = isdk.api(p).calls(pargs, **kwargs)
                        pargs.moids[p] = kwargs['pmoids']
        #========================================
        # Get Existing Profiles and Serial Moids
        #========================================
        if len(pargs.serials) > 0:
            kwargs = isdk.api('serial_number').calls(pargs, **kwargs)
            pargs.serial_moids = kwargs['pmoids']
        if len(pargs.templates) > 0:
            kwargs = isdk.api('server_tempalte').calls(pargs, **kwargs)
            pargs.template_moids = kwargs['pmoids']
        kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        pargs.profile_moids = kwargs['pmoids']
        #=====================================================
        # Create the Profiles with the Profile Function
        #=====================================================
        pargs.type = self.type
        for item in profiles:
            if re.search('^(chassis|server)$', self.type):
                for i in item['targets']:
                    if pargs.description: pargs.remove('description')
                    if pargs.serial_number: pargs.remove('serial_number')
                    pargs.name = i['name']
                    if i.get('desription'): pargs.description = i['description']
                    if i.get('serial_number'): pargs.serial_number = i['serial_number']
                    kwargs, pargs = profile_function(item, pargs, **kwargs)
            elif re.search('^(domain)$', self.type):
                if pargs.description: pargs.remove('description')
                if pargs.serial_number: pargs.remove('serial_number')
                pargs.name = i['name']
                if item.get('desription'): pargs.description = i['description']
                if item.get('serial_numbers'): pargs.serial_numbers = item['serial_numbers']
                #profile_domain(item, pargs, **kwargs)
            else:
                pargs.description = ''
                pargs.serial_number = ''
                pargs.name = item['name']
                if item.get('desription'): pargs.description = item['description']
                if item.get('serial_number'): pargs.serial_number = item['serial_number']
                profile_function(item, pargs, **kwargs)
        #========================================================
        # If chassis or Server Watch Results if action is Deploy
        #========================================================
        if re.search('^(chassis|server)$', self.type):
            for item in profiles:
                for i in item['targets']:
                    if item.get('action'):
                        if item['action'] == 'Deploy':
                            pname = i['name']
                            print(f'Beginning Profile Deployment for {pname}')
                            pargs.pmoid = pargs.moids.profile[i['name']]
                            time.sleep(120)
                            deploy_complete = False
                            while deploy_complete == False:
                                pargs.apiMethod = 'by_moid'
                                kwargs = isdk.api(self.type).calls(pargs, **kwargs)
                                if kwargs['results']['ConfigContext']['ControlAction'] == 'No-op':
                                    deploy_complete = True
                                else: 
                                    validating.deploy_notification(self.type, pname)
                                    time.sleep(120)
        #========================================================
        # End Function and return kwargs
        #========================================================
        validating.end_section(f'{self.type} Profiles')
        return kwargs

#=======================================================
# Add Organization Key Map to Dictionaries
#=======================================================
def org_map(apiBody, org_moid):
    apiBody.update({
        'organization':{
            'class_id':'mo.MoRef',
            'moid':org_moid,
            'object_type':'organization.Organization'
            }
        })
    return apiBody

#=======================================================
# Profile Creation Function
#=======================================================
def profile_function(item, pargs, **kwargs):
    if pargs.type == 'server_template': apiBody = {'object_type':'server.ProfileTemplate'}
    elif pargs.type == 'server':        apiBody = {'object_type':'server.Profile'}
    elif pargs.type == 'chassis':       apiBody = {'object_type':'chassis.Profile'}
    if pargs.get('description'): apiBody.update({'description':pargs.get('description')})
    apiBody.update({'name':pargs.name})
    if pargs.get('serial_number'):
        if re.search(serial_regex, pargs.serial_number): serial_true = True
        else: serial_true = False
    if serial_true == True:
        apiBody.update({f'assigned_{pargs.type}':{
            'moid':pargs.serial_moids[pargs.serial_number]['Moid'],
            'object_type':pargs.serial_moids[pargs.serial_number]['object_type']
        }})
    #=====================================================
    # Add Policies to the Policy Bucket
    #=====================================================
    policy_bucket = False
    if pargs.type == 'chassis': policy_bucket = True
    elif pargs.type == 'server_template':
        policy_bucket = True
        apiBody.update({'target_platform':item['target_platform']})
    elif pargs.type == 'server':
        create_from_template = False
        if item.get('create_from_template'):
            if item['create_from_template'] == False: policy_bucket = True
        else: policy_bucket = True
        if item.get('ucs_server_profile_template'):
            template = item['ucs_server_profile_template']

    if policy_bucket == True:
        for p in pargs.jsonVars['policy_list']:
            pshort = p.replace('_policy', '')
            pData = kwargs['ezData']['policies']['allOf'][1]['properties'][pshort]['object_type']
            pObject = pData[p.replace('_policy', '')]['object_type']
            add_policy = False
            if item.get(p):
                if len(item[p]) > 0: add_policy = True
            if add_policy == True:
                if not apiBody.get('policy_bucket'): apiBody.update({'policy_bucket':[]})
                if not pargs.moids[p].get(item[p]):
                    validating.error_policy_exist(p, item[p], pargs.name, pargs.type, 'Profile')
                pmoid = pargs.moids[p][item[p]]['Moid']
                pbucket = {'class_id':'mo.MoRef'}
                pbucket.update({'moid':pmoid,'object_type':pObject})
                apiBody['policy_bucket'].append(pbucket)
        #=====================================================
        # Create or Patch the Profile via the Intersight API
        #=====================================================
        #try:
        #    api_args = dict(_preload_content = False)
        #    if not chassis_profiles.get(i['name']):
        #        api_method = 'create'
        #        api_call = json.loads(api_handle.create_chassis_profile(api_body, **api_args).data)
        #        pro_moid = api_call['Moid']
        #    else:
        #        api_method = 'patch'
        #        pro_moid = chassis_profiles[i['name']]['Moid']
        #        api_call = json.loads(api_handle.patch_chassis_profile(pro_moid, api_body, **api_args).data)
        #    if print_response_always == True: print(json.dumps(api_call, indent=4))
        #    validating.completed_item('Chassis Profile', i['name'], api_method, pro_moid)
        #    pmoids.update({i['name']:pro_moid})
        #except ApiException as e:
        #    print(f"Exception when calling ChassisApi->{api_method}_chassis_profile: {e}\n")
        #    sys.exit(1)
        #=====================================================
        # Deploy Chassis Profiles
        #=====================================================
        #if serial_true == 1:
        #    if item.get('action'):
        #        if item['action'] == 'Deploy':
        #            api_body = {'action':'Deploy'}
        #            try:
        #                api_call = json.loads(
        #                    api_handle.patch_chassis_profile(pro_moid, api_body, **api_args).data)
        #            except ApiException as e:
        #                print(f"Exception when Deploying Chassis Profile {i['name']}: {e}\n")
        #                sys.exit(1)
