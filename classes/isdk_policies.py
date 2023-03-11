from copy import deepcopy
from isdk_pools import isdk_pools
from intersight.api import access_api
from intersight.api import adapter_api
from intersight.api import bios_api
from intersight.api import boot_api
from intersight.api import fabric_api
from intersight.api import fcpool_api
from intersight.api import iam_api
from intersight.api import ipmioverlan_api
from intersight.api import ippool_api
from intersight.api import kvm_api
from intersight.api import macpool_api
from intersight.api import networkconfig_api
from intersight.api import ntp_api
from intersight.api import power_api
from intersight.api import smtp_api
from intersight.api import snmp_api
from intersight.api import sol_api
from intersight.api import ssh_api
from intersight.api import storage_api
from intersight.api import syslog_api
from intersight.api import thermal_api
from intersight.api import vmedia_api
from intersight.api import vnic_api
from intersight.exceptions import ApiException
import credentials
import ezfunctions
import json
import os
import re
import sys
import urllib3
import validating
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global options for debugging
print_payload = False
print_response_always = False
print_response_on_fail = True

serial_regex = re.compile('^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$')

class isdk_policies(object):
    def __init__(self, type):
        self.type = type

    #=====================================================
    # Create/Patch BIOS Policies
    #=====================================================
    def adapter_configuration(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies']['adapter_configuration']

        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = adapter_api.AdapterApi(api_client)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_adapter_config_policy_list
            empty, adapter_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)

    #=====================================================
    # Create/Patch BIOS Policies
    #=====================================================
    def bios(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies']['bios']
        #=====================================================
        # Grab ezData Settings from Library
        #=====================================================
        #jsonVars = ezData['policies']['allOf'][1]['properties']
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = bios_api.BiosApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_bios_policy_list
            empty, bios_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            if api_body.get('bios_template'):
                template = api_body['bios_template']
                api_body.pop('bios_template')
                for k, v in item.items():
                    if type(v) == int or type(v) == float: api_body[k] = str(v)
                if '_tpm' in template:
                    btemplate = template.replace('_tpm', '')
                    api_body = dict(api_body, **jsonVars['bios']['template_tuning'][btemplate])
                    api_body = dict(api_body, **jsonVars['bios']['template_tuning']['tpm'])
                else:
                    api_body = dict(api_body, **jsonVars['bios']['template_tuning'][template])
                    api_body = dict(api_body, **jsonVars['bios']['template_tuning']['tpm_disabled'])
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_bios_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = bios_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_bios_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when Creating BiosApi->%s_bios_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Boot Order Policies
    #=====================================================
    def boot_order(self, **kwargs):
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = boot_api.BootApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_boot_precision_policy_list
            empty, boot_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            for k, v in item.items():
                jVars1 = jsonVars['boot_order']['key_map']
                if k in jVars1:
                    api_body.update({jVars1[k]:v})
                    if not k == jVars1[k]: api_body.pop(k)
            if item.get('boot_devices'):
                api_body['boot_devices'] = []
                for i in item['boot_devices']:
                    boot_dev = {'class_id':i['object_type'],'name':i['name'],'object_type':i['object_type']}
                    if re.search(
                        '(Iscsi|LocalDisk|Nvme|PchStorage|San|SdCard)', i['object_type']
                    ) and api_body['configured_boot_mode'] == 'Uefi':
                        boot_dev['Bootloader'] = {'class_id':'boot.Bootloader','object_type':'boot.Bootloader'}
                        if 'bootloader' in i:
                            jVars1 = jsonVars['boot_order']['key_map_loader']
                            for k, v in i.items():
                                if k in jVars1: boot_dev['Bootloader'].update({jVars1[k]:v})
                        else: boot_dev['Bootloader'].update({'Name':'BOOTx64.EFI','Path':"\\EFI\\BOOT\\"})
                    jVars1 = jsonVars['boot_order']['key_map_boot']
                    for k, v in i.items():
                        if k in jVars1:
                            boot_dev.update({jVars1[k]:v})
                    api_body['boot_devices'].append(boot_dev)
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_boot_precision_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = boot_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_boot_precision_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling BootApi->%s_boot_precision_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Ethernet Adapter Policies
    #=====================================================
    def ethernet_adapter(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = vnic_api.VnicApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_vnic_eth_adapter_policy_list
            empty, eth_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            if api_body.get('adapter_template'):
                template = api_body['adapter_template']
                api_body.pop('adapter_template')
                api_body = dict(api_body, **jsonVars['ethernet_adapter']['template_tuning'][template])
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_vnic_eth_adapter_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = eth_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_vnic_eth_adapter_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling VnicApi->%s_vnic_eth_adapter_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Ethernet Network Control Policies
    #=====================================================
    def ethernet_network_control(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_fabric_eth_network_control_policy_list
            empty, eth_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            jVars1 = jsonVars['ethernet_network_control']['key_map']
            api_body = deepcopy(item)
            api_body.update({'lldp_settings':{'receive_enabled':False,'transmit_enabled':False}})
            for k, v in item.items():
                if 'lldp' in k:
                    api_body['lldp_settings'].update({jVars1[k]:v})
                    api_body.pop(k)
                elif k in jVars1:
                    api_body.update({jVars1[k]:v})
                    api_body.pop(k)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_fabric_eth_network_control_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = eth_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_fabric_eth_network_control_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_fabric_eth_network_control_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Ethernet Network Group Policies
    #=====================================================
    def ethernet_network_group(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_fabric_eth_network_group_policy_list
            empty, eth_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            api_body.update({'vlan_settings':{'object_type':'fabric.VlanSettings'}})
            klist = ['allowed_vlans','native_vlan']
            for i in klist:
                if i in item:
                    if i == 'native_vlan':
                        api_body['vlan_settings'].update({i:int(item[i])})
                    else: api_body['vlan_settings'].update({i:item[i]})
                    api_body.pop(i)
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_fabric_eth_network_group_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = eth_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_fabric_eth_network_group_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_fabric_eth_network_group_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Ethernet QoS Policies
    #=====================================================
    def ethernet_qos(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = vnic_api.VnicApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_vnic_eth_qos_policy_list
            empty, eth_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            for k, v in item.items():
                if k in jsonVars['ethernet_qos']['key_map']:
                    api_body.update({jsonVars['ethernet_qos']['key_map'][k]:v})
                    api_body.pop(k)
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_vnic_eth_qos_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = eth_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_vnic_eth_qos_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling VnicApi->%s_vnic_eth_qos_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Fibre-Channel Adapter Policies
    #=====================================================
    def fc_zone(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_fabric_fc_zone_policy_list
            empty, fc_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_fabric_fc_zone_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = fc_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_fabric_fc_zone_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling VnicApi->%s_fabric_fc_zone_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Fibre-Channel Adapter Policies
    #=====================================================
    def fibre_channel_adapter(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = vnic_api.VnicApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_vnic_fc_adapter_policy_list
            empty, fc_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            if api_body.get('adapter_template'):
                template = api_body['adapter_template']
                api_body.pop('adapter_template')
                api_body = dict(api_body, **jsonVars['fibre_channel_adapter']['template_tuning'][template])
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_vnic_fc_adapter_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = fc_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_vnic_fc_adapter_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling VnicApi->%s_vnic_fc_adapter_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Fibre-Channel Network Policies
    #=====================================================
    def fibre_channel_network(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = vnic_api.VnicApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_vnic_fc_network_policy_list
            empty, fc_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            api_body.update({'vsan_settings':{'object_type':'vnic.VsanSettings'}})
            for k, v in item.items():
                if k in jsonVars['fibre_channel_network']['key_map']:
                    api_body['vsan_settings'].update({jsonVars['fibre_channel_network']['key_map'][k]:v})
                    api_body.pop(k)
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_vnic_fc_network_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = fc_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_vnic_fc_network_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling VnicApi->%s_vnic_fc_network_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Fibre-Channel QoS Policies
    #=====================================================
    def fibre_channel_qos(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = vnic_api.VnicApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_vnic_fc_qos_policy_list
            empty, fc_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_vnic_fc_qos_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = fc_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_vnic_fc_qos_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling VnicApi->%s_vnic_fc_qos_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Flow Control Policies
    #=====================================================
    def flow_control(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_fabric_flow_control_policy_list
            empty, flow_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_fabric_flow_control_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = flow_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_fabric_flow_control_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_fabric_flow_control_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Get IMC Access Policies
    #=====================================================
    def imc_access(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = access_api.AccessApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_access_policy_list
            empty, imc_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            if item.get('inband_vlan_id'):
                api_body.update({'inband_vlan':int(item['inband_vlan_id'])})
                api_body.pop('inband_vlan_id')
            api_body.update({'address_type':{'enable_ip_v4':True,'enable_ip_v6':False,}})
            addfam = ['v4', 'v6']
            for i in addfam:
                for k, v in item.items():
                    if f'ip{i}_address_configuration' == k:
                        api_body['address_type'].update({f'enable_ip_{i}':v})
                        api_body.pop(f'ip{i}_address_configuration')
            #=====================================================
            # Attach Pools to the API Body
            #=====================================================
            ptype = ['inband_ip_pool', 'out_of_band_ip_pool']
            api_handle = ippool_api.IppoolApi(api_client)
            for i in ptype:
                for k, v in item.items():
                    if i == k:
                        pname = v
                        get_policy = api_handle.get_ippool_pool_list
                        pempty, ip_pools = isdk_pools('get').get_api(get_policy, pname, org_moid)
                        if pempty == False:
                            api_body.update({i:{
                                'class_id':'mo.MoRef','moid':ip_pools[v]['Moid'],'object_type':'ippool.Pool'
                            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            api_handle = access_api.AccessApi(api_client)
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_access_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = imc_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_access_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_access_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch IPMI over LAN Policies
    #=====================================================
    def ipmi_over_lan(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]

        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = ipmioverlan_api.IpmioverlanApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_ipmioverlan_policy_list
            empty, ipmi_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            if not os.environ.get('TF_VAR_ipmi_key') == None:
                api_body.update({'encryption_key':os.environ.get('TF_VAR_ipmi_key')})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call   = json.loads(api_handle.create_ipmioverlan_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = ipmi_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_ipmioverlan_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling IpmioverlanApi->%s_ipmioverlan_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch LAN Connectivity Policies
    #=====================================================
    def lan_connectivity(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Grab LAN Connectivity Settings from Library
        #=====================================================
        #jsonVars = ezData['policies']['allOf'][1]['properties']['lan_connectivity']
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = vnic_api.VnicApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_vnic_lan_connectivity_policy_list
            empty, lan_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if not api_body.get('vnic_placement_modes'): api_body.update({'placement_mode':'custom'})
            for k, v in item.items():
                if k in jsonVars['lan_connectivity']['key_map']:
                    api_body.update({jsonVars['lan_connectivity'][k]:v})
                    api_body.pop(k)
            api_body.pop('vnics')
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_vnic_lan_connectivity_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = lan_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_vnic_lan_connectivity_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_vnic_lan_connectivity_policy: %s\n" % (api_method, e))
                sys.exit(1)
            #=====================================================
            # Create and Attach VLANs to VLAN Policy
            #=====================================================
            if item.get('vnics'):
                isdk_policies('vnics').vnics(api_client, jsonVars, item, org_moid, pol_moid)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Link Aggregation Policies
    #=====================================================
    def link_aggregation(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_fabric_link_aggregation_policy_list
            empty, link_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_fabric_link_aggregation_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = link_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_fabric_link_aggregation_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_fabric_link_aggregation_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Link Control Policies
    #=====================================================
    def link_control(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_fabric_link_control_policy_list
            empty, link_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_fabric_link_control_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = link_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_fabric_link_control_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_fabric_link_control_policy: %s\n" % (api_method, e))
                sys.exit(1)
        validating.end_section(self.type)

    #=====================================================
    # Create/Patch Local User Policies
    #=====================================================
    def local_user(self, **kwargs):
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = iam_api.IamApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_iam_end_point_user_policy_list
            empty, local_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            #=====================================================
            # Grab Local User Settings from Library
            #=====================================================
            for k, v in item.items():
                if k in jsonVars['local_user']['key_map']:
                    api_body.update({jsonVars['local_user']['key_map'][k]:v})
                    if not k == jsonVars['local_user']['key_map'][k]: api_body.pop(k)
            api_body['password_properties'] = {'object_type':'iam.EndPointPasswordProperties'}
            for k, v in item.items():
                if k in jsonVars['local_user']['key_map_password']:
                    api_body['password_properties'].update({jsonVars['local_user']['key_map_password'][k]:v})
                    if not k == jsonVars['local_user']['key_map_password'][k]: api_body.pop(k)
            if api_body.get('users'): api_body.pop('users')
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method   = 'create'
                    api_call = json.loads(api_handle.create_iam_end_point_user_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = local_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_iam_end_point_user_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling IamApi->%s_iam_end_point_user_policy: %s\n" % (api_method, e))
                sys.exit(1)
            if item.get('users'):
                isdk_policies('vlans').local_users(api_client, item, org_moid, pol_moid, **kwargs)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Assign Users to Local User Policies
    #=====================================================
    def local_users(self, api_client, item, org_moid, pol_moid, **kwargs):
        api_handle = iam_api.IamApi(api_client)
        #=====================================================
        # Create API Body for Users
        #=====================================================
        for i in item['users']:
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = {'name':i['username']}
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            get_policy = api_handle.get_iam_end_point_user_list
            empty, users = isdk_pools('get').get_api(get_policy, i['username'], org_moid)
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_iam_end_point_user(api_body, **api_args).data)
                    user_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    user_moid = users[i['username']]['Moid']
                    api_call  = json.loads(api_handle.patch_iam_end_point_user(user_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
            except ApiException as e:
                print("Exception when calling IamApi->%s_iam_end_point_user: %s\n" % (api_method, e))
                sys.exit(1)
            get_policy   = api_handle.get_iam_end_point_role_list
            query_filter = f"Name eq '{i['role']}' and Type eq 'IMC'"
            empty, roles = isdk_pools('get').get_subtype(get_policy, query_filter)
            role_moid = roles[i['role']]['Moid']
            kwargs['Variable'] = f"local_user_password_{i['password']}"
            kwargs = ezfunctions.sensitive_var_value(**kwargs)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            if i.get('enabled'): api_body = {'enabled':i['enabled']}
            else: api_body = {}
            api_body['password'] = kwargs['var_value']
            api_body.update({'end_point_role':[{
                'class_id':'mo.MoRef','moid':role_moid,'object_type':'iam.EndPointRole'
            }]})
            api_body.update({'end_point_user':{
                'class_id':'mo.MoRef','moid':user_moid,'object_type':'iam.EndPointUser'
            }})
            api_body.update({'end_point_user_policy':{
                'class_id':'mo.MoRef','moid':pol_moid,'object_type':'iam.EndPointUserPolicy'
            }})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            empty, user_roles = isdk_pools('get').get_iam_user_role(api_client, user_moid, pol_moid)
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_iam_end_point_user_role(api_body, **api_args).data)
                else:
                    api_method = 'patch'
                    pol_moid = user_roles[user_moid]['Moid']
                    api_call = json.loads(api_handle.patch_iam_end_point_user_role(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling IamApi->%s_iam_end_point_user_role: %s\n" % (api_method, e))
                sys.exit(1)

    #=====================================================
    # Create/Patch Multicast Policies
    #=====================================================
    def multicast(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_fabric_multicast_policy_list
            empty, mcast_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            for k, v in item.items():
                if k in jsonVars['multicast']['key_map']:
                    api_body.update({jsonVars['multicast']['key_map'][k]:v})
                    api_body.pop(k)
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_fabric_multicast_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = mcast_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_fabric_multicast_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_fabric_multicast_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Network Connectivity Policies
    #=====================================================
    def network_connectivity(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        dpolicies = {}
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = networkconfig_api.NetworkconfigApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_networkconfig_policy_list
            empty, dns_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            for k, v in item.items():
                if k in jsonVars['network_connectivity']['key_map']:
                    api_body.update({jsonVars['network_connectivity']['key_map'][k]:v})
                    api_body.pop(k)
            dns_list = ['v4', 'v6']
            for i in dns_list:
                if f'dns_servers_{i}' in item:
                    if len(item[f'dns_servers_{i}']) > 0:
                        api_body.update({f'preferred_ip{i}dns_server':item[f'dns_servers_{i}'][0]})
                    if len(item[f'dns_servers_{i}']) > 1:
                        api_body.update({f'preferred_ip{i}dns_server':item[f'dns_servers_{i}'][1]})
                    api_body.pop(f'dns_servers_{i}')
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_networkconfig_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = dns_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_networkconfig_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling NetworkconfigApi->%s_networkconfig_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch NTP Policies
    #=====================================================
    def ntp(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        dpolicies = {}
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = ntp_api.NtpApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_ntp_policy_list
            empty, ntp_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = {}
            for k, v in item.items():
                if k in jsonVars['ntp']['key_map']:
                    api_body.update({jsonVars['ntp']['key_map'][k]:v})
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_ntp_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = ntp_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_ntp_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling NtpApi->%s_ntp_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({item['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Port Policies
    #=====================================================
    def port(self, **kwargs):
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moid  = kwargs['org_moids'][org]['Moid']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        dpolicies = {}
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        get_policy = api_handle.get_fabric_eth_network_control_policy_list
        e1, ethc   = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        get_policy = api_handle.get_fabric_eth_network_group_policy_list
        e2, ethg   = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        get_policy = api_handle.get_fabric_flow_control_policy_list
        e3, fctrl  = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        get_policy = api_handle.get_fabric_link_aggregation_policy_list
        e4, lagg   = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        get_policy = api_handle.get_fabric_link_control_policy_list
        e5, lctrl  = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        pargs = {
            'ethernet_network_control_policy':{'empty':e1,'moids':ethc},
            'ethernet_network_group_policy':{'empty':e2,'moids':ethg},
            'flow_control_policy':{'empty':e3,'moids':fctrl},
            'link_aggregation_policy':{'empty':e4,'moids':lagg},
            'link_control_policy':{'empty':e5,'moids':lctrl},
        }
        validating.begin_section(self.type)
        for item in policies:
            for name_count in range(0,len(item['names'])):
                pname = item['names'][name_count]
                #=====================================================
                # Confirm if the Policy Already Exists
                #=====================================================
                get_policy = api_handle.get_fabric_port_policy_list
                empty, port_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
                #=====================================================
                # Construct API Body Payload
                #=====================================================
                api_body = deepcopy({})
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
                }})
                api_body['name'] = item['names'][name_count]
                for k, v in item.items():
                    if k in jsonVars['port']['key_map']: api_body.update({jsonVars['port']['key_map'][k]:v})
                if item.get('tags'):
                    api_body.update({'tags':item['tags']})
                    api_body['tags'].append(jsonVars['tags'])
                else: api_body.update({'tags':[jsonVars['tags']]})
                #=====================================================
                # Create or Patch the Policy via the Intersight API
                #=====================================================
                try:
                    api_args = dict(_preload_content = False)
                    if empty == True:
                        api_method = 'create'
                        api_call = json.loads(api_handle.create_fabric_port_policy(api_body, **api_args).data)
                        pol_moid = api_call['Moid']
                    else:
                        api_method = 'patch'
                        pol_moid = port_policies[api_body['name']]['Moid']
                        api_call = json.loads(api_handle.patch_fabric_port_policy(pol_moid, api_body, **api_args).data)
                    if print_response_always == True: print(json.dumps(api_call, indent=4))
                    validating.completed_item(self.type, api_body['name'], api_method, pol_moid)
                except ApiException as e:
                    print("Exception when calling FabricApi->%_fabric_port_policy: %s\n" % (api_method, e))
                    sys.exit(1)
                dpolicies.update({api_body['name']:pol_moid})
                if item.get('port_modes'):
                    for i in item['port_modes']:
                        isdk_policies('mode').port_mode(api_client, i, pol_moid)
                for z in jsonVars['port']['port_type_list']:
                    if item.get(z):
                        isdk_policies(z).ports(api_client, jsonVars, item, name_count, pol_moid, **pargs)
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Assign Port Port Types to Port Policies
    #=====================================================
    def port_mode(self, api_client, i, pol_moid):
        api_handle = fabric_api.FabricApi(api_client)
        api_body = {'class_id':'fabric.PortMode','object_type':'fabric.PortMode'}
        api_body.update({'custom_mode':i['custom_mode'],'port_id_start':i['port_list'][0],'port_id_end':i['port_list'][1]})
        api_body.update({'port_policy':{'class_id':'mo.MoRef','moid':pol_moid,'object_type':'fabric.PortPolicy'}})
        if i.get('slot_id'): api_body.update({'slot_id':i['port_modes']['slot_id']})
        else: api_body.update({'slot_id':1})
        get_policy   = api_handle.get_fabric_port_mode_list
        query_filter = f"PortIdStart eq '{api_body['port_id_start']}' and PortPolicy.Moid eq '{pol_moid}'"
        empty, ports = isdk_pools('get').get_subtype(get_policy, query_filter)
        #=====================================================
        # Create or Patch the Policy via the Intersight API
        #=====================================================
        try:
            api_args = dict(_preload_content = False)
            if empty == True:
                api_method = 'create'
                api_call = json.loads(api_handle.create_fabric_port_mode(api_body, **api_args).data)
            else:
                api_method = 'patch'
                port_moid = ports[api_body['port_id_start']]['Moid']
                api_call  = json.loads(api_handle.patch_fabric_port_mode(port_moid, api_body, **api_args).data)
            if print_response_always == True: print(json.dumps(api_call, indent=4))
        except ApiException as e:
            print("Exception when calling FabricApi->%s_fabric_port_mode: %s\n" % (api_method, e))
            sys.exit(1)

    #=====================================================
    # Assign Port Port Types to Port Policies
    #=====================================================
    def ports(self, api_client, jsonVars, item, name_count, port_moid, **pargs):
        api_handle = fabric_api.FabricApi(api_client)

        def api_tasks(api_handle, api_body, port_moid, port_type):
            api_handle = fabric_api.FabricApi(api_client)
            if port_type == 'port_channel_appliances':      get_policy = api_handle.get_fabric_appliance_pc_role_list
            elif port_type == 'port_channel_ethernet_uplinks': get_policy = api_handle.get_fabric_uplink_pc_role_list
            elif port_type == 'port_channel_fc_uplinks':    get_policy = api_handle.get_fabric_fc_uplink_pc_role_list
            elif port_type == 'port_channel_fcoe_uplinks':  get_policy = api_handle.get_fabric_fcoe_uplink_pc_role_list
            elif port_type == 'port_role_appliances':       get_policy = api_handle.get_fabric_appliance_role_list
            elif port_type == 'port_role_ethernet_uplinks': get_policy = api_handle.get_fabric_uplink_role_list
            elif port_type == 'port_role_fc_storage':   get_policy = api_handle.get_fabric_fc_storage_role_list
            elif port_type == 'port_role_fc_uplinks':   get_policy = api_handle.get_fabric_fc_uplink_role_list
            elif port_type == 'port_role_fcoe_uplinks': get_policy = api_handle.get_fabric_fcoe_uplink_role_list
            elif port_type == 'port_role_servers':      get_policy = api_handle.get_fabric_server_role_list
            if re.search('port_channel', port_type):
                query_filter = f"PcId eq {int(api_body['pc_id'])} and PortPolicy.Moid eq '{port_moid}'"
            else:
                query_filter = f"PortId eq {int(api_body['port_id'])} and PortPolicy.Moid eq '{port_moid}'"
                #query_filter = f"PortPolicy.Moid eq '{port_moid}'"
            empty, ports = isdk_pools('get').get_subtype(get_policy, query_filter)
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    if port_type == 'port_channel_appliances':
                        api_call = json.loads(api_handle.create_fabric_appliance_pc_role(api_body, **api_args).data)
                    elif port_type == 'port_channel_ethernet_uplinks':
                        api_call = json.loads(api_handle.create_fabric_uplink_pc_role(api_body, **api_args).data)
                    elif port_type == 'port_channel_fc_uplinks':
                        api_call = json.loads(api_handle.create_fabric_fc_uplink_pc_role(api_body, **api_args).data)
                    elif port_type == 'port_channel_fcoe_uplinks':
                        api_call = json.loads(api_handle.create_fabric_fcoe_uplink_pc_role(api_body, **api_args).data)
                    elif port_type == 'port_role_appliances':
                        api_call = json.loads(api_handle.create_fabric_appliance_role(api_body, **api_args).data)
                    elif port_type == 'port_role_ethernet_uplinks':
                        api_call = json.loads(api_handle.create_fabric_uplink_role(api_body, **api_args).data)
                    elif port_type == 'port_role_fc_storage':
                        api_call = json.loads(api_handle.create_fabric_fc_storage_role(api_body, **api_args).data)
                    elif port_type == 'port_role_fc_uplinks':
                        api_call = json.loads(api_handle.create_fabric_fc_uplink_role(api_body, **api_args).data)
                    elif port_type == 'port_role_fcoe_uplinks':
                        api_call = json.loads(api_handle.create_fabric_fcoe_uplink_role(api_body, **api_args).data)
                    elif port_type == 'port_role_servers':
                        api_call = json.loads(api_handle.create_fabric_server_role(api_body, **api_args).data)
                    port_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    if re.search('port_channel', port_type): port_moid = ports[api_body['pc_id']]['Moid']
                    else: port_moid = ports[api_body['port_id']]['Moid']
                    if port_type == 'port_channel_appliances':
                        api_call = json.loads(api_handle.patch_fabric_appliance_pc_role(port_moid, api_body, **api_args).data)
                    elif port_type == 'port_channel_ethernet_uplinks':
                        api_call = json.loads(api_handle.patch_fabric_uplink_pc_role(port_moid, api_body, **api_args).data)
                    elif port_type == 'port_channel_fc_uplinks':
                        api_call = json.loads(api_handle.patch_fabric_fc_uplink_pc_role(port_moid, api_body, **api_args).data)
                    elif port_type == 'port_channel_fcoe_uplinks':
                        api_call = json.loads(api_handle.patch_fabric_fcoe_uplink_pc_role(port_moid, api_body, **api_args).data)
                    elif port_type == 'port_role_appliances':
                        api_call = json.loads(api_handle.patch_fabric_appliance_role(port_moid, api_body, **api_args).data)
                    elif port_type == 'port_role_ethernet_uplinks':
                        api_call = json.loads(api_handle.patch_fabric_uplink_role(port_moid, api_body, **api_args).data)
                    elif port_type == 'port_role_fc_storage':
                        api_call = json.loads(api_handle.patch_fabric_fc_storage_role(port_moid, api_body, **api_args).data)
                    elif port_type == 'port_role_fc_uplinks':
                        api_call = json.loads(api_handle.patch_fabric_fc_uplink_role(port_moid, api_body, **api_args).data)
                    elif port_type == 'port_role_fcoe_uplinks':
                        api_call = json.loads(api_handle.patch_fabric_fcoe_uplink_role(port_moid, api_body, **api_args).data)
                    elif port_type == 'port_role_servers':
                        api_call = json.loads(api_handle.patch_fabric_server_role(port_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                if re.search('port_channel', port_type):
                    validating.completed_sub_item(self.type, f"Port-Channel {api_body['pc_id']}", api_method, port_moid)
                else:
                    validating.completed_sub_item(self.type, f"Port {api_body['port_id']}", api_method, port_moid)
            except ApiException as e:
                if port_type == 'port_channel_appliances':
                    print("Exception when calling FabricApi->%s_fabric_appliance_pc_role: %s\n" % (api_method, e))
                elif port_type == 'port_channel_ethernet_uplinks':
                    print("Exception when calling FabricApi->%s_fabric_uplink_pc_role: %s\n" % (api_method, e))
                elif port_type == 'port_channel_fc_uplinks':
                    print("Exception when calling FabricApi->%s_fabric_fc_uplink_pc_role: %s\n" % (api_method, e))
                elif port_type == 'port_channel_fcoe_uplinks':
                    print("Exception when calling FabricApi->%s_fabric_fcoe_uplink_pc_role: %s\n" % (api_method, e))
                elif port_type == 'port_role_appliances':
                    print("Exception when calling FabricApi->%s_fabric_appliance_role: %s\n" % (api_method, e))
                elif port_type == 'port_role_ethernet_uplinks':
                    print("Exception when calling FabricApi->%s_fabric_uplink_role: %s\n" % (api_method, e))
                elif port_type == 'port_role_fc_storage':
                    print("Exception when calling FabricApi->%s_fabric_fc_storage_role: %s\n" % (api_method, e))
                elif port_type == 'port_role_fc_uplinks':
                    print("Exception when calling FabricApi->%s_fabric_fc_uplink_role: %s\n" % (api_method, e))
                elif port_type == 'port_role_fcoe_uplinks':
                    print("Exception when calling FabricApi->%s_fabric_fcoe_uplink_role: %s\n" % (api_method, e))
                elif port_type == 'port_role_servers':
                    print("Exception when calling FabricApi->%s_fabric_server_role: %s\n" % (api_method, e))
                sys.exit(1)
        
        #=====================================================
        # Create API Body for Port Policies
        #=====================================================
        for i in item[self.type]:
            api_body = deepcopy(jsonVars['port']['classes'][self.type])
            api_body.update({'port_policy':{'class_id':'mo.MoRef','moid':port_moid,'object_type':'fabric.PortPolicy'}})
            if i.get('ethernet_network_control_policy'):
                pol_type = 'ethernet_network_control_policy'
                api_body.update({'eth_network_control_policy':{
                    'class_id':'mo.MoRef','moid':pargs[pol_type]['moids'][i[pol_type]]['Moid'],
                    'object_type':'fabric.EthNetworkControlPolicy'
                }})
            if i.get('ethernet_network_group_policy'):
                pol_type = 'ethernet_network_group_policy'
                api_body.update({'eth_network_group_policy':[{
                    'class_id':'mo.MoRef','moid':pargs[pol_type]['moids'][i[pol_type]]['Moid'],
                    'object_type':'fabric.EthNetworkGroupPolicy'
                }]})
            if i.get('flow_control_policy'):
                pol_type = 'flow_control_policy'
                api_body.update({pol_type:{
                    'class_id':'mo.MoRef','moid':pargs[pol_type]['moids'][i[pol_type]]['Moid'],
                    'object_type':'fabric.FlowControlPolicy'
                }})
            if i.get('link_aggregation_policy'):
                pol_type = 'link_aggregation_policy'
                api_body.update({pol_type:{
                    'class_id':'mo.MoRef','moid':pargs[pol_type]['moids'][i[pol_type]]['Moid'],
                    'object_type':'fabric.LinkAggregationPolicy'
                }})
            if i.get('link_control_policy'):
                pol_type = 'link_control_policy'
                api_body.update({pol_type:{
                    'class_id':'mo.MoRef','moid':pargs[pol_type]['moids'][i[pol_type]]['Moid'],
                    'object_type':'fabric.LinkControlPolicy'
                }})
            if i.get('admin_speed'): api_body.update({'admin_speed':i['admin_speed']})
            if i.get('fec'): api_body.update({'fec':i['fec']})
            if i.get('mode'): api_body.update({'mode':i['mode']})
            if i.get('priority'): api_body.update({'priority':i['priority']})
            if re.search('port_channel', self.type):
                if len(i['pc_ids']) > 1: api_body.update({'pc_id':i['pc_ids'][name_count]})
                else: api_body.update({'pc_id':item['pc_id'][0]})
                if i.get('vsan_ids'):
                    if len(i['vsan_ids']) > 1: api_body.update({'vsan_id':i['vsan_ids'][name_count]})
                    else: api_body.update({'vsan_id':i['vsan_ids'][0]})
                api_body['ports'] = []
                for intf in i['interfaces']:
                    intf_body = {'class_id':'fabric.PortIdentifier','object_type':'fabric.PortIdentifier'}
                    intf_body.update({'port_id':intf['port_id']})
                    if intf.get('breakout_port_id'): intf_body.update({'aggregate_port_id':intf['breakout_port_id']})
                    else: intf_body.update({'aggregate_port_id':0})
                    if intf.get('slot_id'): intf_body.update({'slot_id':intf['slot_id']})
                    else: intf_body.update({'slot_id':1})
                    api_body['ports'].append(intf_body)
                api_tasks(api_handle, api_body, port_moid, self.type)
            elif re.search('role', self.type):
                interfaces = ezfunctions.vlan_list_full(i['port_list'])
                for intf in interfaces:
                    intf_body = deepcopy(api_body)
                    if i.get('breakout_port_id'): intf_body.update({'aggregate_port_id':intf['breakout_port_id']})
                    else: intf_body.update({'aggregate_port_id':0})
                    intf_body.update({'port_id':int(intf)})
                    if i.get('device_number'): intf_body.update({'preferred_device_id':i['device_number']})
                    if i.get('connected_device_type'): intf_body.update({'preferred_device_type':i['connected_device_type']})
                    if i.get('slot_id'): intf_body.update({'slot_id':intf['slot_id']})
                    else: intf_body.update({'slot_id':1})
                    api_tasks(api_handle, intf_body, port_moid, self.type)

    #=====================================================
    # Create/Patch Power Policies
    #=====================================================
    def power(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        dpolicies = {}
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = power_api.PowerApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_power_policy_list
            empty, power_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            for k, v in item.items():
                if k in jsonVars['power']['key_map']:
                    api_body.update({jsonVars['power']['key_map'][k]:v})
                    api_body.pop(k)
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_power_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = power_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_power_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_power_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch SAN Connectivity Policies
    #=====================================================
    def san_connectivity(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        dpolicies = {}
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            api_handle = fcpool_api.FcpoolApi(api_client)
            get_policy = api_handle.get_fcpool_pool_list
            e4, wwnnp = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
            api_handle = vnic_api.VnicApi(api_client)
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_vnic_san_connectivity_policy_list
            empty, san_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = {}
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            for k, v in item.items():
                if k in jsonVars['san_connectivity']['key_map']:
                    api_body.update({jsonVars['san_connectivity']['key_map'][k]:v})
            if not api_body.get('vhba_placement_modes'): api_body.update({'placement_mode':'custom'})
            if item.get('wwnn_pool'):
                fc_moid = wwnnp[item['wwnn_pool']]['Moid']
                api_body.update({'wwnn_pool':{'class_id':'mo.MoRef','moid':fc_moid,'object_type':'fcpool.Pool'}})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_vnic_san_connectivity_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = san_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_vnic_san_connectivity_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_vnic_san_connectivity_policy: %s\n" % (api_method, e))
                sys.exit(1)
            #=====================================================
            # Create and Attach VLANs to VLAN Policy
            #=====================================================
            isdk_policies('vhbas').vhbas(api_client, jsonVars, item, org_moid, pol_moid)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Serial over LAN Policies
    #=====================================================
    def serial_over_lan(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        dpolicies = {}
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = sol_api.SolApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_sol_policy_list
            empty, sol_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_sol_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = sol_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_sol_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_sol_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch SNMP Policies
    #=====================================================
    def snmp(self, **kwargs):
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        dpolicies = {}
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = snmp_api.SnmpApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_snmp_policy_list
            empty, log_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body['v2_enabled'] = False
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            for k, v in item.items():
                if k in jsonVars['snmp']['key_map']:
                    api_body.update({jsonVars['snmp']['key_map'][k]:v})
                    api_body.pop(k)
            if api_body.get('access_community_string'):
                kwargs['Variable'] = f"access_community_string_{api_body['access_community_string']}"
                kwargs = ezfunctions.sensitive_var_value(**kwargs)
                api_body['access_community_string'] = kwargs['var_value']
                api_body['v2_enabled'] = True
            if api_body.get('trap_community'):
                kwargs['Variable'] = f"trap_community_string_{api_body['trap_community']}"
                kwargs = ezfunctions.sensitive_var_value(**kwargs)
                api_body['trap_community'] = kwargs['var_value']
                api_body['v2_enabled'] = True
            if 'snmp_trap_destinations' in item:
                api_body['snmp_traps'] = []
                for i in item['snmp_trap_destinations']:
                    trap_item = dict({'class_id':'snmp.Trap','object_type':'snmp.Trap'}, **i)
                    for k, v in i.items():
                        if k in jsonVars['snmp_trap_destinations']['key_map']:
                            trap_item.update({jsonVars['snmp_trap_destinations']['key_map'][k]:v})
                    if trap_item.get('community'):
                        kwargs['Variable'] = f"snmp_trap_community_{trap_item['community']}"
                        kwargs = ezfunctions.sensitive_var_value(**kwargs)
                        trap_item['community'] = kwargs['var_value']
                        api_body['v2_enabled'] = True
                    api_body['snmp_traps'].append(trap_item)
                api_body.pop('snmp_trap_destinations')
                if len(item['snmp_trap_destinations']) == 0: api_body.pop('snmp_traps')
            if 'snmp_users' in item:
                if len(item['snmp_users']) > 0: api_body['v3_enabled'] = True
                else: api_body['v3_enabled'] = False
                api_body.pop('snmp_users')
                api_body['snmp_users'] = []
                for i in item['snmp_users']:
                    user_item = dict({'class_id':'snmp.User','object_type':'snmp.User'}, **i)
                    if user_item.get('auth_password'):
                        kwargs['Variable'] = f"snmp_auth_password_{user_item['auth_password']}"
                        kwargs = ezfunctions.sensitive_var_value(**kwargs)
                        user_item['auth_password'] = kwargs['var_value']
                    if user_item.get('privacy_password'):
                        kwargs['Variable'] = f"snmp_privacy_password_{user_item['privacy_password']}"
                        kwargs = ezfunctions.sensitive_var_value(**kwargs)
                        user_item['privacy_password'] = kwargs['var_value']
                    api_body['snmp_users'].append(user_item)
                if len(item['snmp_users']) == 0: api_body.pop('snmp_users')
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_snmp_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = log_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_snmp_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling SnmpApi->%s_snmp_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Storage Policies
    #=====================================================
    def storage(self, **kwargs):
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        dpolicies = {}
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = storage_api.StorageApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            #=====================================================
            # Grab Storage Policy Settings from Library
            #=====================================================
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_storage_storage_policy_list
            empty, storage_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy({})
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            for k, v in item.items():
                if k in jsonVars['storage']['key_map']: api_body.update({jsonVars['storage']['key_map'][k]:v})
            if item.get('m2_raid_configuration'):
                api_body.update({'m2_virtual_drive':{
                    'class_id':'storage.M2VirtualDriveConfig','object_type':'storage.M2VirtualDriveConfig',
                    'controller_slot':item['m2_raid_configuration'][0]['slot'],
                    'enable':True
                }})
            if item.get('single_drive_raid_configuration'):
                api_body.update({'raid0_drive':{}})
                for k,v in item['single_drive_raid_configuration'].items():
                    if k in jsonVars['storage']['raid0_map']:
                        api_body['raid0_drive'].update({jsonVars['storage']['raid0_map'][k]:v})
                if item['single_drive_raid_configuration'].get('virtual_drive_policy'):
                    api_body['raid0_drive']['virtual_drive_policy'] = item['single_drive_raid_configuration'
                                                                           ]['virtual_drive_policy']
                    api_body['raid0_drive']['virtual_drive_policy'].update({
                        'class_id':'storage.VirtualDrivePolicy','object_type':'storage.VirtualDrivePolicy'
                    })
                api_body['raid0_drive'].update({'class_id':'storage.R0Drive','object_type':'storage.R0Drive'})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_storage_storage_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = storage_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_storage_storage_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling StorageApi->%s_storage_storage_policy: %s\n" % (api_method, e))
                sys.exit(1)
            if item.get('drive_groups'):
                isdk_policies('dg').storage_dg(api_client, item, pol_moid)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Assign Drive Groups to Storage Policies
    #=====================================================
    def storage_dg(self, api_client, item, storage_moid):
        api_handle = storage_api.StorageApi(api_client)
        for i in item['drive_groups']:
            #=====================================================
            # Confirm if the VSAN is already Attached
            #=====================================================
            get_policy   = api_handle.get_storage_disk_group_list
            query_filter = f"Name eq '{i['name']}' and StoragePolicy.Moid eq '{storage_moid}'"
            empty, drive_groups = isdk_pools('get').get_subtype(get_policy, query_filter)
            #=====================================================
            # Create API Body for VLANs
            #=====================================================
            api_body = deepcopy({
                'class_id':'storage.DriveGroup','object_type':'storage.DriveGroup',
                'name':i['name'],'raid_level':i['raid_level']
                })
            api_body.update({'storage_policy':{
                'class_id':'mo.MoRef','moid':storage_moid,'object_type':'storage.StoragePolicy'}
                })
            if i.get('manual_drive_group'):
                api_body['manual_drive_group'] = {
                    'class_id':'storage.ManualDriveGroup','object_type':'storage.ManualDriveGroup'
                }
                if i['manual_drive_group'][0].get('dedicated_hot_spares'):
                    api_body['manual_drive_group']['dedicated_hot_spares'] = i['manual_drive_group']['dedicated_hot_spares']
                api_body['manual_drive_group']['span_groups'] = []
                for x in i['manual_drive_group'][0]['drive_array_spans']:
                    api_body['manual_drive_group']['span_groups'].append({
                        'class_id':'storage.SpanDrives','object_type':'storage.SpanDrives','slots':x['slots']
                    })
            if i.get('virtual_drives'):
                api_body['virtual_drives'] = []
                for x in i['virtual_drives']:
                    vd_body = deepcopy(x)
                    vd_body.update({
                        'class_id':'storage.VirtualDriveConfiguration','object_type':'storage.VirtualDriveConfiguration'
                    })
                    if vd_body.get('virtual_drive_policy'):
                        vd_body['virtual_drive_policy'].update({
                            'class_id':'storage.VirtualDrivePolicy','object_type':'storage.VirtualDrivePolicy'
                        })
                    api_body['virtual_drives'].append(vd_body)
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    vapi_method = 'create'
                    vapi_call = json.loads(api_handle.create_storage_drive_group(api_body, **api_args).data)
                else:
                    vapi_method = 'patch'
                    pol_moid = drive_groups[item['name']]['Moid']
                    vapi_call = json.loads(api_handle.create_storage_drive_group(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(vapi_call, indent=4))
            except ApiException as e:
                print("Exception when calling StorageApi->%s_storage_drive_group: %s\n" % (vapi_method, e))
                sys.exit(1)

    #=====================================================
    # Create/Patch Switch Control Policies
    #=====================================================
    def switch_control(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        dpolicies = {}
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_fabric_switch_control_policy_list
            empty, ctrl_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({
                'mac_aging_settings':{
                    'mac_aging_option':'Default', 'mac_aging_time':14500, 'object_type':'fabric.MacAgingSettings'
                },
                'organization':{
                    'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
                },
                'udld_settings':{
                    'message_interval':15,'recovery_action':'reset','object_type':'fabric.UdldGlobalSettings'
                }
            })
            for k, v in item.items():
                if k in jsonVars['switch_control']['key_map']:
                    if 'mac_' in k: api_body['mac_aging_settings'].update({jsonVars['switch_control']['key_map'][k]:v})
                    elif 'udld_' in k: api_body['udld_settings'].update({jsonVars['switch_control']['key_map'][k]:v})
                    api_body.pop(k)
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_fabric_switch_control_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = ctrl_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_fabric_switch_control_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_fabric_switch_control_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Syslog Policies
    #=====================================================
    def syslog(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        dpolicies = {}
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = syslog_api.SyslogApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_syslog_policy_list
            empty, log_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            if 'local_logging' in item:
                api_body.update({'local_clients':[{
                    'class_id':'syslog.LocalFileLoggingClient',
                    'object_type':'syslog.LocalFileLoggingClient',
                    'min_severity':item['local_logging']['minimum_severity']
                }]})
                api_body.pop('local_logging')
            if item.get('remote_logging'):
                rsyslog = {'class_id':'syslog.RemoteLoggingClient','object_type':'syslog.RemoteLoggingClient'}
                for key, value in item['remote_logging'].items():
                    for k, v in value.items():
                        if k in jsonVars['remote_logging']['key_map']:
                            api_body['remote_logging'][key].update({jsonVars['remote_logging']['key_map'][k]:v})
                            api_body['remote_logging'][key].pop(k)
                    api_body['remote_logging'][key].update(rsyslog)
                for key, value in item['remote_logging'].items():
                    if value['hostname'] == '0.0.0.0': api_body['remote_logging'].pop(key)
                if len(api_body['remote_logging']) > 0:
                    api_body['remote_clients'] = []
                    for key, value in api_body['remote_logging'].items():
                        api_body['remote_clients'].append(deepcopy(value))
                api_body.pop('remote_logging')
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_syslog_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = log_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_syslog_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_syslog_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch System QoS Policies
    #=====================================================
    def system_qos(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        home      = kwargs['home']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        dpolicies = {}
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_fabric_system_qos_policy_list
            empty, qos_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            for i in api_body['classes']:
                i.update({'admin_state':i['state'],'name':i['priority'],'object_type':'fabric.QosClass'})
                i.pop('priority')
                i.pop('state')
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_fabric_system_qos_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = qos_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_fabric_system_qos_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_fabric_system_qos_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Thermal Policies
    #=====================================================
    def thermal(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        home      = kwargs['home']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        dpolicies = {}
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = thermal_api.ThermalApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_thermal_policy_list
            empty, thermal_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_thermal_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = thermal_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_thermal_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_thermal_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Assign VNICs to LAN Connectivity Policies
    #=====================================================
    def vhbas(self, api_client, jsonVars, item, org_moid, scp_moid):
        #=====================================================
        # Get Ethernet Policies and MAC Pools
        #=====================================================
        api_handle = fabric_api.FabricApi(api_client)
        get_policy = api_handle.get_fabric_fc_zone_policy_list
        e1, fcz = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        api_handle = fcpool_api.FcpoolApi(api_client)
        get_policy = api_handle.get_fcpool_pool_list
        e2, wwpnp = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        api_handle = vnic_api.VnicApi(api_client)
        get_policy = api_handle.get_vnic_fc_adapter_policy_list
        e3, fca = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        get_policy = api_handle.get_vnic_fc_network_policy_list
        e4, fcn = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        get_policy = api_handle.get_vnic_fc_qos_policy_list
        e5, fcq = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        #=====================================================
        # Create API Body for VNICs
        #=====================================================
        for i in item['vhbas']:
            vnic_count = len(i['names'])
            for x in range(0,vnic_count):
                fcap = fca[i['fibre_channel_adapter_policy']]['Moid']
                fcnp = fcn[i['fibre_channel_network_policies'][x]]['Moid']
                fcqp = fcq[i['fibre_channel_qos_policy']]['Moid']
                api_body = {}
                for k, v in i.items():
                    if k in jsonVars['vhbas']['key_map']:
                        api_body.update({jsonVars['vhbas']['key_map'][k]:v})
                        api_body.pop(k)
                api_body.update({'class_id':'vnic.FcIf','object_type':'vnic.FcIf'})
                api_body.update({
                    'placement':{'id':'MLOM','object_type':'vnic.PlacementSettings','pci_link':0,'uplink':0}
                })
                if i.get('fc_zone_policies'):
                    api_body.update({'fc_zone_policies':[]})
                    zcount = 0
                    for z in i['fc_zone_policies']:
                        fczp = fcz[i['fc_zone_policies'][zcount]]['Moid']
                        zcount += 1
                        api_body['fc_zone_policies'].append(
                            {'class_id':'mo.MoRef','moid':fczp,'object_type':'fabric.FcZonePolicy'}
                        )
                api_body.update({'name':i['names'][x],'order':i['placement_pci_order'][x]})
                if i.get('placement_switch_id'):
                    api_body['placement'].update({'switch_id':i['placement_switch_id']})
                else:
                    if x == 0: s_id = 'A'
                    else: s_id = 'B'
                    api_body['placement'].update({'switch_id':s_id})
                place_list = ['placement_pci_links', 'placement_slot_ids', 'placement_uplink_ports']
                for p in place_list:
                    count = 0
                    if i.get(p): api_body.pop(p); count += 1
                    if count == 1:
                        if len(item[p]) == 2: pval = item[p][x]
                        else: pval = item[p][0]
                        if 'slot' in p: pvar = 'id'
                        pvar = p.replace('placement_', '')
                        pvar = pvar.replace('s', '')
                        api_body['placement'][pvar] = pval
                api_body.update({
                    'fc_adapter_policy':{
                        'class_id':'mo.MoRef','moid':fcap,'object_type':'vnic.FcAdapterPolicy'
                    },
                    'fc_network_policy':{
                        'class_id':'mo.MoRef','moid':fcnp,'object_type':'vnic.FcNetworkPolicy'
                    },
                    'fc_qos_policy':{
                        'class_id':'mo.MoRef','moid':fcqp,'object_type':'vnic.FcQosPolicy'
                    },
                    'san_connectivity_policy':{
                        'class_id':'mo.MoRef','moid':scp_moid,'object_type':'vnic.SanConnectivityPolicy'
                    }
                })
                if i.get('vhba_type'):
                    api_body.update({'type':i['vhba_type']})
                    api_body.pop('vhba_type')
                else: api_body.update({'type':'fc-initiator'})
                if i.get('wwpn_pools'):
                    wwpnpool = wwpnp[i['wwpn_pools'][x]]['Moid']
                    api_body.update({
                        'wwpn_address_type':'POOL',
                        'wwpn_pool':{
                            'class_id':'mo.MoRef','moid':wwpnpool,'object_type':'fcpool.Pool'
                        }
                    })
                get_policy   = api_handle.get_vnic_fc_if_list
                query_filter = f"Name eq '{api_body['name']}' and SanConnectivityPolicy.Moid eq '{scp_moid}'"
                empty, vhbas = isdk_pools('get').get_subtype(get_policy, query_filter)
                #=====================================================
                # Create or Patch the Policy via the Intersight API
                #=====================================================
                try:
                    api_args = dict(_preload_content = False)
                    if empty == True:
                        api_method = 'create'
                        api_call = json.loads(api_handle.create_vnic_fc_if(api_body, **api_args).data)
                        pol_moid = api_call['Moid']
                    else:
                        api_method = 'patch'
                        pol_moid = vhbas[api_body['name']]['Moid']
                        api_call = json.loads(api_handle.patch_vnic_fc_if(pol_moid, api_body, **api_args).data)
                    if print_response_always == True: print(json.dumps(api_call, indent=4))
                except ApiException as e:
                    print("Exception when calling VnicApi->%s_vnic_fc_if: %s\n" % (api_method, e))
                    sys.exit(1)

    #=====================================================
    # Create/Patch Virtual KVM Policies
    #=====================================================
    def virtual_kvm(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = kvm_api.KvmApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_kvm_policy_list
            empty, kvm_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            for k, v in item.items():
                if k in jsonVars['virtual_kvm']['key_map']:
                    api_body.update({jsonVars['virtual_kvm']['key_map'][k]:v})
                    api_body.pop(k)
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_kvm_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = kvm_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_kvm_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_kvm_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch Virtual Media Policies
    #=====================================================
    def virtual_media(self, **kwargs):
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = vmedia_api.VmediaApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_vmedia_policy_list
            empty, vmedia_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy({})
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            for k, v in item.items():
                if k in jsonVars['virtual_media']['key_map']: api_body.update({jsonVars['virtual_media']['key_map'][k]:v})
            if item.get('add_virtual_media'):
                api_body.update({'mappings':[]})
                for i in item['add_virtual_media']:
                    vmedia_add = {}
                    for k, v in i.items():
                        if k in jsonVars['virtual_media']['add_key_map']:
                            vmedia_add.update({jsonVars['virtual_media']['add_key_map'][k]:v})
                    vmedia_add.update({'class_id':'vmeida.Mapping','object_type':'vmeida.Mapping'})
                    api_body['mappings'].append(vmedia_add)
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_vmedia_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = vmedia_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_vmedia_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling VmediaApi->%s_vmedia_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Create/Patch VLAN Policies
    #=====================================================
    def vlan(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_fabric_eth_network_policy_list
            empty, vlan_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            api_body.pop('vlans')
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_fabric_eth_network_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = vlan_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_fabric_eth_network_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_fabric_eth_network_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
            #=====================================================
            # Create and Attach VLANs to VLAN Policy
            #=====================================================
            if item.get('vlans'):
                isdk_policies('vlans').vlans(api_client, item, org_moid, pol_moid)
        validating.end_section(self.type)
        return dpolicies
            
    #=====================================================
    # Assign VLANs to VLAN Policies
    #=====================================================
    def vlans(self, api_client, item, org_moid, vpolicy_moid):
        api_handle = fabric_api.FabricApi(api_client)
        #=====================================================
        # Get Organization Multicast Policies
        #=====================================================
        get_policy = api_handle.get_fabric_multicast_policy_list
        mempty, mcast_policies = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        #=====================================================
        # Create API Body for VLANs
        #=====================================================
        for i in item['vlans']:
            vlan_list = ezfunctions.vlan_list_full(i['vlan_list'])
            for x in vlan_list:
                if type(x) == str: x = int(x)
                api_body = deepcopy(i)
                api_body.pop('vlan_list')
                api_body.update({'vlan_id':x})
                if i.get('native_vlan'):
                    api_body.update({'is_native':i['native_vlan']})
                    api_body.pop('native_vlan')
                if re.search('^[\d]$', str(x)): zeros = '000'
                elif re.search('^[\d]{2}$', str(x)): zeros = '00'
                elif re.search('^[\d]{3}$', str(x)): zeros = '0'
                elif re.search('^[\d]{4}$', str(x)): zeros = ''
                if i['name'] == 'vlan': api_body.update({'name':f"{i['name']}{zeros}{x}"})
                else: api_body.update({'name':f"{i['name']}-vl{zeros}{x}"})
                api_body.update({'eth_network_policy':{
                    'class_id':'mo.MoRef',
                    'moid':vpolicy_moid,
                    'object_type':'fabric.EthNetworkPolicy'
                }})
                api_body.update({'multicast_policy':{
                    'class_id':'mo.MoRef',
                    'moid':mcast_policies[i['multicast_policy']]['Moid'],
                    'object_type':'fabric.MulticastPolicy'
                }})
                get_policy   = api_handle.get_fabric_vlan_list
                query_filter = f"VlanId eq '{int(x)}' and EthNetworkPolicy.Moid eq '{vpolicy_moid}'"
                empty, vlans = isdk_pools('get').get_subtype(get_policy, query_filter)
                #=====================================================
                # Create or Patch the Policy via the Intersight API
                #=====================================================
                try:
                    api_args = dict(_preload_content = False)
                    if empty == True:
                        api_method = 'create'
                        api_call = json.loads(api_handle.create_fabric_vlan(api_body, **api_args).data)
                        pol_moid = api_call['Moid']
                    else:
                        api_method = 'patch'
                        pol_moid = vlans[api_body['name']]['Moid']
                        api_call = json.loads(api_handle.patch_fabric_vlan(pol_moid, api_body, **api_args).data)
                    if print_response_always == True: print(json.dumps(api_call, indent=4))
                    validating.completed_sub_item(self.type, api_body['name'], api_method, pol_moid)
                except ApiException as e:
                    print("Exception when calling FabricApi->%s_fabric_vlan: %s\n" % (api_method, e))
                    sys.exit(1)

    #=====================================================
    # Assign VNICs to LAN Connectivity Policies
    #=====================================================
    def vnics(self, api_client, jsonVars, item, org_moid, lcp_moid):
        #=====================================================
        # Get Ethernet Policies and MAC Pools
        #=====================================================
        api_handle = fabric_api.FabricApi(api_client)
        get_policy = api_handle.get_fabric_eth_network_control_policy_list
        e1, ethc = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        get_policy = api_handle.get_fabric_eth_network_group_policy_list
        e2, ethg = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        api_handle = macpool_api.MacpoolApi(api_client)
        get_policy = api_handle.get_macpool_pool_list
        e3, macp = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        api_handle = vnic_api.VnicApi(api_client)
        get_policy = api_handle.get_vnic_eth_adapter_policy_list
        e4, etha = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        get_policy = api_handle.get_vnic_eth_qos_policy_list
        e5, ethq = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        #=====================================================
        # Create API Body for VNICs
        #=====================================================
        for i in item['vnics']:
            vnic_count = len(i['names'])
            for x in range(0,vnic_count):
                ethap = etha[i['ethernet_adapter_policy']]['Moid']
                ethcp = ethc[i['ethernet_network_control_policy']]['Moid']
                ethgp = ethg[i['ethernet_network_group_policy']]['Moid']
                ethqp = ethq[i['ethernet_qos_policy']]['Moid']
                api_body = deepcopy(i)
                api_body.update({'class_id':'vnic.EthIf','object_type':'vnic.EthIf'})
                if not api_body.get('cdn_values'):
                    api_body.update({'cdn':{'value':i['names'][x],'source':'vnic','object_type':'vnic.Cdn'}})
                else:
                    api_body.update({
                        'cdn':{'value':i['cdn_values'][x],'source':i['cdn_source'],'object_type':'vnic.Cdn'}
                    })
                if api_body.get('enable_failover'): api_body.update({'failover_enabled',api_body['enable_failover']})
                api_body.update({
                    'placement':{'id':'MLOM','object_type':'vnic.PlacementSettings','pci_link':0,'uplink':0}
                })
                api_body.update({'name':i['names'][x],'order':i['placement_pci_order'][x]})
                if i.get('placement_switch_id'):
                    api_body['placement'].update({'switch_id':i['placement_switch_id']})
                    api_body.pop('placement_switch_id')
                else:
                    if x == 0: s_id = 'A'
                    else: s_id = 'B'
                    api_body['placement'].update({'switch_id':s_id})
                place_list = ['placement_pci_links', 'placement_slot_ids', 'placement_uplink_ports']
                for p in place_list:
                    count = 0
                    if i.get(p): api_body.pop(p); count += 1
                    if count == 1:
                        if len(item[p]) == 2: pval = item[p][x]
                        else: pval = item[p][0]
                        if 'slot' in p: pvar = 'id'
                        pvar = p.replace('placement_', '')
                        pvar = pvar.replace('s', '')
                        api_body['placement'][pvar] = pval
                api_body.update({
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
                    macpool = macp[i['mac_address_pools'][x]]['Moid']
                    api_body.update({
                        'mac_address_type':'POOL',
                        'mac_pool':{
                            'class_id':'mo.MoRef','moid':macpool,'object_type':'macpool.Pool'
                        }
                    })
                pop_list = jsonVars['vnics']['pop_list']
                for p in pop_list:
                    if api_body.get(p): api_body.pop(p)
                get_policy   = api_handle.get_vnic_eth_if_list
                query_filter = f"Name eq '{api_body['name']}' and LanConnectivityPolicy.Moid eq '{lcp_moid}'"
                empty, vnics = isdk_pools('get').get_subtype(get_policy, query_filter)
                #=====================================================
                # Create or Patch the Policy via the Intersight API
                #=====================================================
                try:
                    api_args = dict(_preload_content = False)
                    if empty == True:
                        api_method = 'create'
                        api_call = json.loads(api_handle.create_vnic_eth_if(api_body, **api_args).data)
                        pol_moid = api_call['Moid']
                    else:
                        api_method = 'patch'
                        pol_moid = vnics[api_body['name']]['Moid']
                        api_call = json.loads(api_handle.patch_vnic_eth_if(pol_moid, api_body, **api_args).data)
                    if print_response_always == True: print(json.dumps(api_call, indent=4))
                    validating.completed_sub_item(self.type, api_body['name'], api_method, pol_moid)
                except ApiException as e:
                    print("Exception when calling VnicApi->%s_vnic_eth_if: %s\n" % (api_method, e))
                    sys.exit(1)

    #=====================================================
    # Create/Patch VSAN Policies
    #=====================================================
    def vsan(self, **kwargs):
        #=====================================================
        # Load Kwargs from Main
        #=====================================================
        args      = kwargs['args']
        dpolicies = {}
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['policies'][self.type]
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        validating.begin_section(self.type)
        for item in policies:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_fabric_fc_network_policy_list
            empty, vsan_policies = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = deepcopy(item)
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moid,'object_type':'organization.Organization'
            }})
            api_body.pop('vsans')
            if item.get('tags'):
                api_body.update({'tags':item['tags']})
                api_body['tags'].append(jsonVars['tags'])
            else: api_body.update({'tags':[jsonVars['tags']]})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_fabric_fc_network_policy(api_body, **api_args).data)
                    pol_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pol_moid = vsan_policies[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_fabric_fc_network_policy(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item(self.type, item['name'], api_method, pol_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_fabric_fc_network_policy: %s\n" % (api_method, e))
                sys.exit(1)
            dpolicies.update({api_body['name']:pol_moid})
            #=====================================================
            # Create and Attach VSANs to VSAN Policy
            #=====================================================
            if item.get('vsans'):
                isdk_policies('vsans').vsans(api_client, item, pol_moid)
        validating.end_section(self.type)
        return dpolicies

    #=====================================================
    # Assign VSANs to VSAN Policies
    #=====================================================
    def vsans(self, api_client, item, vpolicy_moid):
        api_handle = fabric_api.FabricApi(api_client)
        for i in item['vsans']:
            #=====================================================
            # Confirm if the VSAN is already Attached
            #=====================================================
            get_policy   = api_handle.get_fabric_vsan_list
            query_filter = f"VSanId eq '{int(i['vsan_id'])}' and FcNetworkPolicy.Moid eq '{vpolicy_moid}'"
            empty, vsans = isdk_pools('get').get_subtype(get_policy, query_filter)
            #=====================================================
            # Create API Body for VLANs
            #=====================================================
            api_body = deepcopy(i)
            api_body.update({'fcoe_vlan':i['fcoe_vlan_id']})
            api_body.pop('fcoe_vlan_id')
            api_body.update({'fc_network_policy':{
                'class_id':'mo.MoRef','moid':vpolicy_moid,'object_type':'fabric.FcNetworkPolicy'
            }})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    vapi_method = 'create'
                    vapi_call = json.loads(api_handle.create_fabric_vsan(api_body, **api_args).data)
                else:
                    vapi_method = 'patch'
                    pol_moid = vsans[item['name']]['Moid']
                    vapi_call = json.loads(api_handle.patch_fabric_vsan(pol_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(vapi_call, indent=4))
            except ApiException as e:
                print("Exception when calling FabricApi->%s_fabric_vsan: %s\n" % (vapi_method, e))
                sys.exit(1)
