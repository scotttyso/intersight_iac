from copy import deepcopy
from dotmap import DotMap
import ezfunctions
import isdk
import json
import os
import re
import sys
import time
import validating

serial_regex = re.compile('^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$')

#=======================================================
# Pools Class
#=======================================================
class api(object):
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

    #=====================================================
    # Assign Users to Local User Policies
    #=====================================================
    def local_users(self, pargs, **kwargs):
        #=====================================================
        # Get Existing Users
        #=====================================================
        pargs.apiMethod = 'get'
        pargs.names = []
        for item in pargs.item: pargs.names.append(item['name'])
        pargs.names = []
        kwargs = isdk.api('local_user').calls(pargs, **kwargs)
        luser_moids = kwargs['pmoids']
        unames = []
        rnames = []
        users_check = False
        for item in pargs.item:
            if item.get('users'):
                users_check = True
                for i in item['users']:
                    unames.append(i['name'])
                    rnames.append(i['role'])
        if users_check == True:
            pargs.names = unames
            kwargs = isdk.api(self.type).calls(pargs, **kwargs)
            user_moids = kwargs['pmoids']
            pargs.names = rnames
            kwargs = isdk.api('user_role').calls(pargs, **kwargs)
            role_moids = kwargs['pmoids']
            #=====================================================
            # Create API Body for Users
            #=====================================================
            for item in pargs.item:
                if item.get('users'):
                    for i in item['users']:
                        #=====================================================
                        # Construct API Body User
                        #=====================================================
                        api_body = {'name':i['name']}
                        apiBody = org_map(apiBody, pargs.org_moid)
                        if not user_moids.get(i['name']):
                            pargs.apiMethod = 'create'
                            pargs.apiBody = apiBody
                            kwargs = isdk.api(self.type).calls(pargs, **kwargs)
                            user_moid = kwargs['pmoid']
                        else: user_moid = user_moids[i['name']]['Moid']
                        kwargs['Variable'] = f"local_user_password_{i['password']}"
                        kwargs = ezfunctions.sensitive_var_value(**kwargs)
                        #=====================================================
                        # Create API Body for User Role
                        #=====================================================
                        if i.get('enabled'): api_body = {'enabled':i['enabled']}
                        else: api_body = {}
                        api_body['password'] = kwargs['var_value']
                        api_body.update({'end_point_role':[{
                            'moid':role_moids[i['role']],'object_type':'iam.EndPointRole'
                        }]})
                        api_body.update({'end_point_user':{
                            'moid':user_moid,'object_type':'iam.EndPointUser'
                        }})
                        api_body.update({'end_point_user_policy':{
                            'moid':luser_moids[item['name']],'object_type':'iam.EndPointUserPolicy'
                        }})
                        #=====================================================
                        # Create or Patch the Policy via the Intersight API
                        #=====================================================
                        if not user_moids.get(i['name']): pargs.apiMethod = 'create'
                        else: pargs.apiMethod = 'patch'
                        pargs.policy = self.type
                        pargs.apiBody = apiBody
                        kwargs = isdk.api('local_users').calls(pargs, **kwargs)

    #=====================================================
    #  Policies Function
    #=====================================================
    def policies(self, pargs, **kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['key_map']
        policies = kwargs['immDict']['orgs'][kwargs['org']]['policies'][self.type]
        org_moid = kwargs['org_moids'][kwargs['org']]['Moid']
        validating.begin_section(self.type, 'policies')
        #=====================================================
        # Get Existing Policies
        #=====================================================
        pargs.names = []
        for i in policies: pargs.names.append(i['name'])
        pargs.purpose = self.type
        pargs.apiMethod = 'get'
        kwargs = isdk.api(self.type).calls(pargs, **kwargs)
        #=====================================================
        # Loop through Items
        #=====================================================
        for item in policies:
            #=====================================================
            # Construct apiBody Payload
            #=====================================================
            apiBody = {}
            for k, v in item.items():
                if k in jsonVars: apiBody.update({jsonVars[k]:v})
            apiBody = org_map(apiBody, org_moid)
            if apiBody.get('tags'): apiBody['tags'].append(kwargs['ezData']['tags'])
            else: apiBody.update({'tags':[kwargs['ezData']['tags']]})
            #=====================================================
            # Add Policy Specific Settings
            #=====================================================
            apiBody = eval(self.type)(item, apiBody, **kwargs)
            #=====================================================
            # Create/Patch the Policy via the Intersight API
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
        validating.end_section(self.type, 'policies')
        #=====================================================
        # Loop Thru Sub-Items
        #=====================================================
        if 'local_user' == self.type:
            local_users = False
            for item in policies:
                if item.get('users'): local_users = True
            if local_users == True:
                pargs.item = item
                pargs.org_moid = org_moid
                kwargs = api('local_users').local_users(pargs, **kwargs)
        elif 'lan_connectivity' == self.type:
            vnics_check = False
            for item in policies:
                if item.get('vnics'): vnics_check = True
            if vnics_check == True:
                pargs.item = item
                pargs.org_moid = org_moid
                kwargs = api('vnics').vnics(pargs, **kwargs)
        elif 'port' == self.type:
            ports_check = False
            pmode_check = False
            for item in policies:
                if item.get('port_modes'): pmode_check = True
                elif 'port_channel' in item: ports_check = True
                elif 'port_role' in item: ports_check = True
            pargs.item = item
            pargs.org_moid = org_moid
            if pmode_check == True:
                kwargs = api('port_mode').port_mode(pargs, **kwargs)
            if ports_check == True:
                kwargs = api('ports').ports(pargs, **kwargs)
        elif 'san_connectivity' == self.type:
            vhbas_check = False
            for item in policies:
                if item.get('vhbas'): vhbas_check = True
            if vhbas_check == True:
                pargs.item = item
                pargs.org_moid = org_moid
                kwargs = api('vhbas').vhbas(pargs, **kwargs)
        elif 'vlan' == self.type:
            vlans_check = False
            for item in policies:
                if item.get('vlans'): vlans_check = True
            if vlans_check == True:
                pargs.item = item
                pargs.org_moid = org_moid
                kwargs = api('vlans').vlans(pargs, **kwargs)
        elif 'vsan' == self.type:
            vsans_check = False
            for item in policies:
                if item.get('vsans'): vsans_check = True
            if vsans_check == True:
                pargs.item = item
                pargs.org_moid = org_moid
                kwargs = api('vsans').vsans(pargs, **kwargs)
        return kwargs

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
        pargs.purpose = self.type
        pargs.apiMethod = 'get'
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
                apiBody = fc(item, apiBody)
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

    #=====================================================
    # Port Modes for Port Policies
    #=====================================================
    def port_mode(self, pargs, **kwargs):
        #=====================================================
        # Get Port Policy
        #=====================================================
        pargs.apiMethod = 'get'
        kwargs = api('port').calls(pargs, **kwargs)
        port_moids = kwargs['pmoids']
        for item in pargs.item:
            if item.get('port_modes'):
                #=====================================================
                # Confirm if the vHBAs are already Attached
                #=====================================================
                pargs.pmoid = port_moids[item['name']]['Moid']
                kwargs = api('port_mode').calls(pargs, **kwargs)
                pm_moids = kwargs['pmoids']
                for i in item['port_modes']:
                    apiBody = {'object_type':'fabric.PortMode'}
                    apiBody.update({
                        'custom_mode':i['custom_mode'],
                        'port_id_start':i['port_list'][0],
                        'port_id_end':i['port_list'][1]
                    })
                    apiBody.update({'port_policy':{'moid':pargs.pmoid,'object_type':'fabric.PortPolicy'}})
                    if i.get('slot_id'): apiBody.update({'slot_id':i['port_modes']['slot_id']})
                    else: apiBody.update({'slot_id':1})
                    #=====================================================
                    # Create or Patch the Policy via the Intersight API
                    #=====================================================

    #=====================================================
    # Assign Port Types to Port Policies
    #=====================================================
    def ports(self, pargs, **kwargs):
        #=====================================================
        # Create API Body for Port Policies
        #=====================================================
        def port_type_call(item, pargs, **kwargs):
            name_count = len(item['names'])
            for i in item[pargs.type]:
                apiBody = deepcopy(jsonVars['port']['classes'][pargs.type])
                apiBody.update({'port_policy':{'moid':pargs.pmoid,'object_type':'fabric.PortPolicy'}})
                if i.get('ethernet_network_control_policy'):
                    pol_type = 'ethernet_network_control_policy'
                    apiBody.update({'eth_network_control_policy':{
                        'moid':pargs.moids[pol_type][i[pol_type]]['Moid'],
                        'object_type':'fabric.EthNetworkControlPolicy'
                    }})
                if i.get('ethernet_network_group_policy'):
                    pol_type = 'ethernet_network_group_policy'
                    apiBody.update({'eth_network_group_policy':[{
                        'moid':pargs.moids[pol_type][i[pol_type]]['Moid'],
                        'object_type':'fabric.EthNetworkGroupPolicy'
                    }]})
                if i.get('flow_control_policy'):
                    pol_type = 'flow_control_policy'
                    apiBody.update({pol_type:{
                        'moid':pargs.moids[pol_type][i[pol_type]]['Moid'],
                        'object_type':'fabric.FlowControlPolicy'
                    }})
                if i.get('link_aggregation_policy'):
                    pol_type = 'link_aggregation_policy'
                    apiBody.update({pol_type:{
                        'moid':pargs.moids[pol_type][i[pol_type]]['Moid'],
                        'object_type':'fabric.LinkAggregationPolicy'
                    }})
                if i.get('link_control_policy'):
                    pol_type = 'link_control_policy'
                    apiBody.update({pol_type:{
                        'moid':pargs.moids[pol_type][i[pol_type]]['Moid'],
                        'object_type':'fabric.LinkControlPolicy'
                    }})
                if i.get('admin_speed'): apiBody.update({'admin_speed':i['admin_speed']})
                if i.get('fec'): apiBody.update({'fec':i['fec']})
                if i.get('mode'): apiBody.update({'mode':i['mode']})
                if i.get('priority'): apiBody.update({'priority':i['priority']})
                if re.search('port_channel', pargs.type):
                    if len(i['pc_ids']) > 1: apiBody.update({'pc_id':i['pc_ids'][name_count]})
                    else: apiBody.update({'pc_id':item['pc_id'][0]})
                    if i.get('vsan_ids'):
                        if len(i['vsan_ids']) > 1: apiBody.update({'vsan_id':i['vsan_ids'][name_count]})
                        else: apiBody.update({'vsan_id':i['vsan_ids'][0]})
                    apiBody['ports'] = []
                    for intf in i['interfaces']:
                        intf_body = {'class_id':'fabric.PortIdentifier','object_type':'fabric.PortIdentifier'}
                        intf_body.update({'port_id':intf['port_id']})
                        if intf.get('breakout_port_id'): intf_body.update(
                                {'aggregate_port_id':intf['breakout_port_id']})
                        else: intf_body.update({'aggregate_port_id':0})
                        if intf.get('slot_id'): intf_body.update({'slot_id':intf['slot_id']})
                        else: intf_body.update({'slot_id':1})
                        apiBody['ports'].append(intf_body)
                elif re.search('role', self.type):
                    interfaces = ezfunctions.vlan_list_full(i['port_list'])
                    for intf in interfaces:
                        intf_body = deepcopy(apiBody)
                        if i.get('breakout_port_id'): intf_body.update(
                                {'aggregate_port_id':intf['breakout_port_id']})
                        else: intf_body.update({'aggregate_port_id':0})
                        intf_body.update({'port_id':int(intf)})
                        if i.get('device_number'): intf_body.update({'preferred_device_id':i['device_number']})
                        if i.get('connected_device_type'): intf_body.update(
                                {'preferred_device_type':i['connected_device_type']})
                        if i.get('slot_id'): intf_body.update({'slot_id':intf['slot_id']})
                        else: intf_body.update({'slot_id':1})
                #api_tasks(api_handle, intf_body, port_moid, self.type)
                #api_tasks(api_handle, api_body, port_moid, self.type)
            return kwargs

        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['port']
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        pargs.apiMethod = 'get'
        kwargs = api('ethernet_network_control').calls(pargs, **kwargs)
        pargs.moids.ethernet_network_control = kwargs['pmoids']
        kwargs = api('ethernet_network_group').calls(pargs, **kwargs)
        pargs.moids.ethernet_network_group = kwargs['pmoids']
        kwargs = api('flow_control').calls(pargs, **kwargs)
        pargs.moids.flow_control = kwargs['pmoids']
        kwargs = api('link_aggregation').calls(pargs, **kwargs)
        pargs.moids.link_aggregation = kwargs['pmoids']
        kwargs = api('link_control').calls(pargs, **kwargs)
        pargs.moids.link_control = kwargs['pmoids']
        kwargs = api('port').calls(pargs, **kwargs)
        port_moids = kwargs['pmoids']
        #=====================================================
        # Create API Body for Port Types
        #=====================================================
        for item in pargs.item:
            for z in jsonVars['port_type_list']:
                if item.get(z):
                    pargs.pmoid = port_moids[item['name']]['Moid']
                    kwargs = api(z).calls(pargs, **kwargs)
                    pargs.moids[z] = kwargs['pmoids']
                    pargs.type = z
                    port_type_call(item, pargs, **kwargs)
        return kwargs

    #=====================================================
    # Assign Drive Groups to Storage Policies
    #=====================================================
    def storage_drive_group(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['storage']['virtual_drive_map']
        #=====================================================
        # Get Storage Policies
        #=====================================================
        pargs.apiMethod = 'get'
        kwargs = api('storage').calls(pargs, **kwargs)
        storage_moids = kwargs['pmoids']
        #=====================================================
        # Create API Body for Storage Drive Groups
        #=====================================================
        for item in pargs.item:
            if item.get('drive_groups'):
                #=====================================================
                # Confirm if the vHBAs are already Attached
                #=====================================================
                pargs.pmoid = storage_moids[item['name']]['Moid']
                kwargs = api('storage_drive_group').calls(pargs, **kwargs)
                dg_moids = kwargs['pmoids']
                for i in item['drive_groups']:
                    #=====================================================
                    # Create API Body for VLANs
                    #=====================================================
                    apiBody = deepcopy({
                        'name':i['name'],'object_type':'storage.DriveGroup','raid_level':i['raid_level']
                        })
                    apiBody.update({'storage_policy':{'moid':pargs.pmoid,'object_type':'storage.StoragePolicy'}})
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

    #=====================================================
    # Assign VNICs to LAN Connectivity Policies
    #=====================================================
    def vhbas(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['key_map']
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        pargs.apiMethod = 'get'
        kwargs = api('fc_zone').calls(pargs, **kwargs)
        fcz_moids = kwargs['pmoids']
        kwargs = api('fibre_channel_adapter').calls(pargs, **kwargs)
        fca_moids = kwargs['pmoids']
        kwargs = api('fibre_channel_network').calls(pargs, **kwargs)
        fcn_moids = kwargs['pmoids']
        kwargs = api('fibre_channel_qos').calls(pargs, **kwargs)
        fcq_moids = kwargs['pmoids']
        kwargs = api('san_connectivity').calls(pargs, **kwargs)
        scp_moids = kwargs['pmoids']
        kwargs = api('wwpn').calls(pargs, **kwargs)
        wwpn_moids = kwargs['pmoids']
        #=====================================================
        # Create API Body for VNICs
        #=====================================================
        for item in pargs.item:
            if item.get('vhbas'):
                #=====================================================
                # Confirm if the vHBAs are already Attached
                #=====================================================
                pargs.pmoid = scp_moids[item['name']]['Moid']
                kwargs = api('vhbas').calls(pargs, **kwargs)
                vhba_moids = kwargs['pmoids']
                for i in item['vhbas']:
                    vnic_count = len(i['names'])
                    for x in range(0,vnic_count):
                        fcap = fca_moids[i['fibre_channel_adapter_policy']]['Moid']
                        fcnp = fcn_moids[i['fibre_channel_network_policies'][x]]['Moid']
                        fcqp = fcq_moids[i['fibre_channel_qos_policy']]['Moid']
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
                                fcz_moid = fcz_moids[i['fc_zone_policies'][zcount]]['Moid']
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
                            'fc_adapter_policy':{'moid':fcap,'object_type':'vnic.FcAdapterPolicy'},
                            'fc_network_policy':{'moid':fcnp,'object_type':'vnic.FcNetworkPolicy'},
                            'fc_qos_policy':{'moid':fcqp,'object_type':'vnic.FcQosPolicy'},
                            'san_connectivity_policy':{
                                'moid':scp_moids[item['name']],'object_type':'vnic.SanConnectivityPolicy'
                            }
                        })
                        if i.get('vhba_type'):
                            apiBody.update({'type':i['vhba_type']})
                            apiBody.pop('vhba_type')
                        else: apiBody.update({'type':'fc-initiator'})
                        if i.get('wwpn_pools'):
                            wwpnpool = wwpn_moids[i['wwpn_pools'][x]]['Moid']
                            apiBody.update({
                                'wwpn_address_type':'POOL',
                                'wwpn_pool':{'moid':wwpnpool,'object_type':'fcpool.Pool'}
                            })

    #=====================================================
    # Assign VLANs to VLAN Policies
    #=====================================================
    def vlans(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['key_map']
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        pargs.apiMethod = 'get'
        kwargs = api('multicast').calls(pargs, **kwargs)
        mcast_moids = kwargs['pmoids']
        kwargs = api('vlan').calls(pargs, **kwargs)
        vlan_moids = kwargs['pmoids']
        #=====================================================
        # Create API Body for VNICs
        #=====================================================
        for item in pargs.item:
            if item.get('vlans'):
                #=====================================================
                # Confirm if the VLANs are already Attached
                #=====================================================
                pargs.pmoid = vlan_moids[item['name']]['Moid']
                kwargs = api('fibre_channel_network').calls(pargs, **kwargs)
                vlans_moids = kwargs['pmoids']
                #=====================================================
                # Create API Body for VLANs
                #=====================================================
                for i in item['vlans']:
                    vlan_list = ezfunctions.vlan_list_full(i['vlan_list'])
                    for x in vlan_list:
                        if type(x) == str: x = int(x)
                        if re.search('^[\d]$', str(x)): zeros = '000'
                        elif re.search('^[\d]{2}$', str(x)): zeros = '00'
                        elif re.search('^[\d]{3}$', str(x)): zeros = '0'
                        elif re.search('^[\d]{4}$', str(x)): zeros = ''
                        if i['name'] == 'vlan': apiBody = {'name':f"{i['name']}{zeros}{x}"}
                        else: apiBody = {'name':f"{i['name']}-vl{zeros}{x}"}
                        if i.get('auto_allow_on_uplinks'):
                            apiBody.update({'auto_allow_on_uplinks':i['auto_allow_on_uplinks']})
                        apiBody.update({'vlan_id':x})
                        if i.get('native_vlan'):
                            apiBody.update({'is_native':i['native_vlan']})
                            apiBody.pop('native_vlan')
                        apiBody.update({'eth_network_policy':{
                            'moid':pargs.pmoid, 'object_type':'fabric.EthNetworkPolicy'
                        }})
                        apiBody.update({'multicast_policy':{
                            'moid':mcast_moids[i['multicast_policy']]['Moid'],
                            'object_type':'fabric.MulticastPolicy'
                        }})

    #=====================================================
    # Assign VNICs to LAN Connectivity Policies
    #=====================================================
    def vnics(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['key_map']
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        pargs.apiMethod = 'get'
        kwargs = api('ethernet_adapter').calls(pargs, **kwargs)
        etha_moids = kwargs['pmoids']
        #kwargs = api('ethernet_network').calls(pargs, **kwargs)
        #ethn_moids = kwargs['pmoids']
        kwargs = api('ethernet_network_control').calls(pargs, **kwargs)
        ethnc_moids = kwargs['pmoids']
        kwargs = api('ethernet_network_group').calls(pargs, **kwargs)
        ethng_moids = kwargs['pmoids']
        kwargs = api('ethernet_qos').calls(pargs, **kwargs)
        ethq_moids = kwargs['pmoids']
        kwargs = api('lan_connectivity').calls(pargs, **kwargs)
        lcp_moids = kwargs['pmoids']
        kwargs = api('mac').calls(pargs, **kwargs)
        mac_moids = kwargs['pmoids']
        #=====================================================
        # Create API Body for vNICs
        #=====================================================
        for item in pargs.item:
            if item.get('vnics'):
                #=====================================================
                # Confirm if the vNICs are already Attached
                #=====================================================
                pargs.pmoid = lcp_moids[item['name']]['Moid']
                kwargs = api('vnics').calls(pargs, **kwargs)
                vnic_moids = kwargs['pmoids']
                for i in item['vnics']:
                    vnic_count = len(i['names'])
                    for x in range(0,vnic_count):
                        ethap = etha_moids[i['ethernet_adapter_policy']]['Moid']
                        ethcp = ethnc_moids[i['ethernet_network_control_policy']]['Moid']
                        ethgp = ethng_moids[i['ethernet_network_group_policy']]['Moid']
                        ethqp = ethq_moids[i['ethernet_qos_policy']]['Moid']
                        apiBody = {'name':i['names'][x],'order':i['placement_pci_order'][x]}
                        apiBody.update({'class_id':'vnic.EthIf','object_type':'vnic.EthIf'})
                        if not apiBody.get('cdn_values'):
                            apiBody.update({'cdn':{'value':i['names'][x],'source':'vnic','object_type':'vnic.Cdn'}})
                        else:
                            apiBody.update({
                                'cdn':{'value':i['cdn_values'][x],'source':i['cdn_source'],'object_type':'vnic.Cdn'}
                            })
                        if apiBody.get('enable_failover'): apiBody.update({'failover_enabled',apiBody['enable_failover']})
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
                                'moid':ethap,'object_type':'vnic.EthAdapterPolicy'
                            },
                            'fabric_eth_network_control_policy':{
                                'moid':ethcp,'object_type':'fabric.EthNetworkControlPolicy'
                            },
                            'fabric_eth_network_group_policy':[{
                                'moid':ethgp,'object_type':'fabric.EthNetworkGroupPolicy'
                            }],
                            'eth_qos_policy':{
                                'moid':ethqp,'object_type':'vnic.EthQosPolicy'
                            },
                            'lan_connectivity_policy':{
                                'moid':pargs.pmoid,'object_type':'vnic.LanConnectivityPolicy'
                            }
                        })
                        if i.get('mac_address_pools'):
                            macpool = mac_moids[i['mac_address_pools'][x]]['Moid']
                            apiBody.update({
                                'mac_address_type':'POOL',
                                'mac_pool':{
                                    'moid':macpool,'object_type':'macpool.Pool'
                                }
                            })
                        pop_list = jsonVars['vnics']['pop_list']
                        for p in pop_list:
                            if apiBody.get(p): apiBody.pop(p)
        return kwargs

    #=====================================================
    # Assign VSANs to VSAN Policies
    #=====================================================
    def vsans(self, pargs, **kwargs):
        jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties'][self.type]['key_map']
        #=====================================================
        # Get Policies and Pools
        #=====================================================
        pargs.apiMethod = 'get'
        kwargs = api('vlan').calls(pargs, **kwargs)
        vsan_moids = kwargs['pmoids']
        #=====================================================
        # Create API Body for VNICs
        #=====================================================
        for item in pargs.item:
            if item.get('vsans'):
                #=====================================================
                # Confirm if the VSANs are already Attached
                #=====================================================
                pargs.pmoid = vsan_moids[item['name']]['Moid']
                kwargs = api('vsans').calls(pargs, **kwargs)
                vsans_moids = kwargs['pmoids']
                for i in item['vsans']:
                    #=====================================================
                    # Create API Body for VLANs
                    #=====================================================
                    apiBody = {'fc_network_policy':{'moid':pargs.pmoid,'object_type':'fabric.FcNetworkPolicy'}}
                    for k, v in i:
                        if k in jsonVars: apiBody.update({jsonVars[k]:v})
                    if not apiBody.get('fcoe_vlan'): apiBody.update({'fcoe_vlan':i['vsan_id']})
                    #=====================================================
                    # Create or Patch the Policy via the Intersight API
                    #=====================================================

#=======================================================
# BIOS Policy Modification
#=======================================================
def bios(item, apiBody, **kwargs):
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
def boot_order(item, apiBody, **kwargs):
    jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['boot_order']
    if item.get('boot_devices'):
        apiBody['boot_devices'] = []
        for i in item['boot_devices']:
            boot_dev = {'class_id':i['object_type'],'name':i['name'],'object_type':i['object_type']}
            if re.search(
                '(Iscsi|LocalDisk|Nvme|PchStorage|San|SdCard)', i['object_type']
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
def ethernet_adapter(item, apiBody, **kwargs):
    jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['ethernet_adapter']['template_tuning']
    if item.get('adapter_template'):
        template = item['adapter_template']
        apiBody = dict(apiBody, **jsonVars[template])
    return apiBody

#=======================================================
# Ethernet Network Control Policies Policy Modification
#=======================================================
def ethernet_network_control(item, apiBody, **kwargs):
    jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['ethernet_network_control']
    for k, v in item.items():
        if 'lldp' in k:
            apiBody['lldp_settings'].apiBody({jsonVars[k]:v})
            apiBody.pop(k)
    return apiBody

#=======================================================
# Ethernet Network Group Policies Policy Modification
#=======================================================
def ethernet_network_group(item, apiBody, **kwargs):
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
# Ethernet QoS Policy Modification
#=======================================================
def ethernet_qos(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    return apiBody

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
# FC Zone Policies Policy Modification
#=======================================================
def fc_zone(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    return apiBody

#=======================================================
# Fibre-Channel Adapter Policy Modification
#=======================================================
def fibre_channel_adapter(item, apiBody, **kwargs):
    jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['fibre_channel_adapter']['template_tuning']
    if item.get('adapter_template'):
        template = item['adapter_template']
        apiBody = dict(apiBody, **jsonVars[template])
    return apiBody

#=======================================================
# Fibre-Channel Network Policies Policy Modification
#=======================================================
def fibre_channel_network(item, apiBody, **kwargs):
    jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['fibre_channel_network']['key_map']
    apiBody.update({'vsan_settings':{'object_type':'vnic.VsanSettings'}})
    for k, v in item.items():
        if re.search('(v(l|s)an_id)', k) and k in jsonVars:
            apiBody['vsan_settings'].update({jsonVars[k]:v})
            apiBody.pop(k)
    return apiBody

#=======================================================
# Fibre-Channel QoS Policy Modification
#=======================================================
def fibre_channel_qos(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    return apiBody

#=======================================================
# Flow Control Policy Modification
#=======================================================
def flow_control(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    return apiBody

#=======================================================
# IMC Access Policy Modification
#=======================================================
def imc_access(item, apiBody, **kwargs):
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
    pargs = DotMap()
    pargs.apiMethod = 'get'
    pargs.policy = 'ip'
    pargs.names = []
    ptype = ['inband_ip_pool', 'out_of_band_ip_pool']
    for i in ptype:
        if i in item: pargs.names.append(item[i])
    kwargs = isdk.api('ip').calls(pargs, **kwargs)
    for i in ptype:
        if i in item: apiBody.update({i:{
                        'moid':kwargs['pmoids'][item[i]]['Moid'],'object_type':'ippool.Pool'
                    }})
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
# IPMI over LAN Policy Modification
#=======================================================
def ipmi_over_lan(item, apiBody, **kwargs):
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
def lan_connectivity(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    if not apiBody.get('vnic_placement_mode'): apiBody.update({'placement_mode':'custom'})
    else: apiBody.pop('vnic_placement_mode')
    return apiBody

#=======================================================
# Link Aggregation Policy Modification
#=======================================================
def link_aggregation(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    return apiBody

#=======================================================
# Link Control Policy Modification
#=======================================================
def link_control(item, apiBody, **kwargs):
    kwargs = kwargs
    if item.get('admin_state'): apiBody['udld_settings'] = {'admin_state':item['admin_state']}
    if item.get('mode'):
        if not apiBody.get('udld_settings'): apiBody['udld_settings']
        apiBody['udld_settings'].update({'mode':item['mode']})
    return apiBody

#=======================================================
# Local User Policy Modification
#=======================================================
def local_user(item, apiBody, **kwargs):
    jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['local_user']['key_map_password']
    for k, v in item.items():
        if k in jsonVars['local_user']['key_map_password']:
            apiBody['password_properties'].update({jsonVars[k]:v})
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

#=======================================================
# Multicast Policy Modification
#=======================================================
def multicast(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    return apiBody

#=======================================================
# Network Connectivity Policy Modification
#=======================================================
def network_connectivity(item, apiBody, **kwargs):
    dns_list = ['v4', 'v6']
    kwargs   = kwargs
    for i in dns_list:
        if f'dns_servers_{i}' in item:
            if len(item[f'dns_servers_{i}']) > 0:
                apiBody.update({f'preferred_ip{i}dns_server':item[f'dns_servers_{i}'][0]})
            if len(item[f'dns_servers_{i}']) > 1:
                apiBody.update({f'alternate_ip{i}dns_server':item[f'dns_servers_{i}'][1]})
    return apiBody

#=======================================================
# NTP Policy Modification
#=======================================================
def ntp(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    return apiBody

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
# Port Policy Modification
#=======================================================
def port(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    return apiBody

#=======================================================
# Power Policy Modification
#=======================================================
def power(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    return apiBody

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


#=======================================================
# SAN Connectivity Policy Modification
#=======================================================
def san_connectivity(item, apiBody, **kwargs):
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
# Serial over LAN Policy Modification
#=======================================================
def serial_over_lan(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    return apiBody

#=======================================================
# SNMP Policy Modification
#=======================================================
def snmp(item, apiBody, **kwargs):
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
def storage(item, apiBody, **kwargs):
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
# Switch Control Policy Modification
#=======================================================
def switch_control(item, apiBody, **kwargs):
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
def syslog(item, apiBody, **kwargs):
    jsonVars = kwargs['ezData']['policies']['allOf'][1]['properties']['syslog']['remote_logging']
    if 'local_logging' in item:
        apiBody.update({'local_clients':[{
            'object_type':'syslog.LocalFileLoggingClient',
            'min_severity':item['local_logging']['minimum_severity']
        }]})
        apiBody.pop('local_logging')
    if item.get('remote_logging'):
        apiBody['remote_clients'] = []
        rsyslog = {'object_type':'syslog.RemoteLoggingClient'}
        for key, value in item['remote_logging'].items():
            for k, v in value.items():
                if k in jsonVars: rsyslog.update({jsonVars[k]:v})
            apiBody['remote_clients'][key].update(rsyslog)
        for key, value in item['remote_logging'].items():
            if value['hostname'] == '0.0.0.0': apiBody['remote_clients'].pop(key)
        if len(apiBody['remote_logging']) == 0: apiBody.pop('remote_clients')
    return apiBody

#=======================================================
# System QoS Policy Modification
#=======================================================
def system_qos(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    for i in apiBody['classes']:
        i.update({'admin_state':i['state'],'name':i['priority'],'object_type':'fabric.QosClass'})
        i.pop('priority')
        i.pop('state')
    return apiBody

#=======================================================
# Thermal Policy Modification
#=======================================================
def thermal(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    return apiBody

#=======================================================
# Virtual KVM Policy Modification
#=======================================================
def virtual_kvm(item, apiBody, **kwargs):
    item   = item
    kwargs = kwargs
    return apiBody

#=======================================================
# Virtual Media Policy Modification
#=======================================================
def virtual_media(item, apiBody, **kwargs):
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
def vlan(item, apiBody, **kwargs):
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
# VSAN Policy Modification
#=======================================================
def vsan(item, apiBody, **kwargs):
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
