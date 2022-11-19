from collections import OrderedDict
from datetime import datetime
from intersight.api import access_api
from intersight.api import adapter_api
from intersight.api import asset_api
from intersight.api import bios_api
from intersight.api import boot_api
from intersight.api import certificatemanagement_api
from intersight.api import compute_api
from intersight.api import cond_api
from intersight.api import deviceconnector_api
from intersight.api import fabric_api
from intersight.api import fcpool_api
from intersight.api import iam_api
from intersight.api import ipmioverlan_api
from intersight.api import kvm_api
from intersight.api import macpool_api
from intersight.api import memory_api
from intersight.api import networkconfig_api
from intersight.api import ntp_api
from intersight.api import organization_api
from intersight.api import power_api
from intersight.api import sdcard_api
from intersight.api import server_api
from intersight.api import smtp_api
from intersight.api import snmp_api
from intersight.api import ssh_api
from intersight.api import storage_api
from intersight.api import syslog_api
from intersight.api import virtualization_api
from intersight.api import vmedia_api
from intersight.api import vnic_api
from intersight.exceptions import ApiException
from openpyxl.styles import Alignment, Border, Font, NamedStyle, PatternFill, Side
from pathlib import Path
import credentials
import classes.ezfunctions
import json
import pprint
import pytz
import openpyxl
import os
import re
import sys
import classes.validating
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pp = pprint.PrettyPrinter(indent=4)
home = Path.home()

class intersight_api(object):
    def __init__(self, type):
        self.type = type

    def add_policies(self, **kwargs):
        args = kwargs['args']
        path_sep = kwargs['path_sep']
        script_path = kwargs['script_path']
        jsonArg = False
        jsonFile = f'{script_path}{path_sep}variables{path_sep}easy_variables.json'
        jsonOpen = open(jsonFile, 'r')
        easy_jsonData = json.load(jsonOpen)
        jsonOpen.close()

        if not args.json_file == None:
            jsonArg = True
            jsonOpen = open(args.json_file, 'r')
            jsonData = json.load(jsonOpen)
        tags = [{'key': 'Module','value': 'day2tools'}]

        def process_results(apiQuery):
            api_dict = {}
            api_list = []
            empty = False
            if apiQuery.get('Results'):
                for i in apiQuery['Results']:
                    iMoid = i['Moid']
                    iName = i['Name']
                    idict = {iName:{'Moid':iMoid}}
                    api_dict.update(idict)
                    api_list.append(iName)
                return empty, api_dict, api_list
            else:
                empty = True
                return empty, api_dict, api_list
        
        def empty_results(apiQuery):
                print(f"The API Query Results were empty for {apiQuery['ObjectType']}.  Exiting...")
                exit()

        print(f'\n-------------------------------------------------------------------------------------------\n')
        print('  Beginning Policy Append to Profiles...')
        print(f'\n-------------------------------------------------------------------------------------------\n')

        # Determine if the Profiles are for FI-attached or Standalone Servers
        kwargs['multi_select'] = False
        if jsonArg == False:
            kwargs['jData'] = {}
            kwargs['jData']['default']     = 'FIAttached'
            kwargs['jData']['description'] = 'Select the Profile Type.'
            kwargs['jData']['enum']        = ['FIAttached', 'Standalone']
            kwargs['jData']['varType']     = 'Profile Type'
            profile_type = classes.ezfunctions.variablesFromAPI(**kwargs)
        else: profile_type = jsonData['profile_type']

        # Prompt User for the Type of Policy to Attach to the Profiles
        if jsonArg == False:
            jsonVars = easy_jsonData['components']['schemas']['policies']['allOf'][1]['properties']
            kwargs['jData'] = jsonVars[profile_type]
            kwargs['jData']['description'] = 'Select the Policy Type.'
            kwargs['jData']['varType']     = 'Policy Type'
            policy_type = classes.ezfunctions.variablesFromAPI(**kwargs)
        else: policy_type = jsonData['policy_type']

        # Query API for the Organization List
        api_client = credentials.config_credentials(home, args)
        api_handle = organization_api.OrganizationApi(api_client)
        kwargs = dict(_preload_content = False)
        apiQuery = json.loads(api_handle.get_organization_organization_list(**kwargs).data)
        empty, orgs, org_names = process_results(apiQuery)
        if empty == True: empty_results(apiQuery)

        # Request from User Which Organizations to Apply this to if not provided with jsonArg.
        if jsonArg == False:
            kwargs['multi_select'] = True
            kwargs['jData'] = {}
            kwargs['jData']['default']     = 'default'
            kwargs['jData']['description'] = f'Select the Organizations to Apply the {policy_type} to.'
            kwargs['jData']['enum']        = org_names
            kwargs['jData']['varType']     = 'Organizations'
            organizations = classes.ezfunctions.variablesFromAPI(**kwargs)
        else: organizations = jsonData['organizations']

        for org in organizations:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting Loop on Organization {org}.')
            print(f'\n-------------------------------------------------------------------------------------------\n')

            # Query API for the List of Policies
            policy_api = easy_jsonData['components']['schemas']['api_calls']['allOf'][1]['properties'][policy_type]
            api_handle = eval(f"{policy_api['enum'][0]}(api_client)")
            print(api_handle)
            query_filter = f"Organization.Moid eq '{orgs[org]['Moid']}'"
            kwargs = dict(filter=query_filter, _preload_content = False)
            apiQuery = eval(f"json.loads(api_handle.{policy_api['enum'][1]}(**kwargs).data)")
            empty, policyDict, policyNames = process_results(apiQuery)
            if empty == True: empty_results(apiQuery)

            # Prompt User for Policy to Attach.
            kwargs['multi_select'] = False
            kwargs['jData'] = {}
            kwargs['jData']['default']     = policyNames[0]
            kwargs['jData']['description'] = f'Select the {policy_type} Policy to attach to the Server Profile.'
            kwargs['jData']['enum']        = policyNames
            kwargs['jData']['varType']     = f'{policy_type} Policy Name'
            policy_name = classes.ezfunctions.variablesFromAPI(**kwargs)

            # Obtain Server Profile Data
            query_filter = f"Organization.Moid eq '{orgs[org]['Moid']}' and TargetPlatform eq '{profile_type}'"
            kwargs = dict(filter=query_filter, top = 1000, _preload_content = False)
            api_handle = server_api.ServerApi(api_client)
            apiQuery = json.loads((api_handle.get_server_profile_list(**kwargs)).data)
            empty, profileDict, profileNames = process_results(apiQuery)
            if empty == True: empty_results(apiQuery)
            profileNames.sort()

            # Request from User Which Profiles to Apply this to if not provided with jsonArg.
            if jsonArg == False:
                kwargs['multi_select'] = True
                kwargs['jData'] = {}
                kwargs['jData']['default']     = profileNames[0]
                kwargs['jData']['description'] = f'Select the Server Profiles to Apply the {policy_type} to.'
                kwargs['jData']['enum']        = profileNames
                kwargs['jData']['varType']     = 'Server Profiles'
                profile_names = classes.ezfunctions.variablesFromAPI(**kwargs)
            else: profile_names = jsonData['server_profiles']
            
            # Attach the Policy to the Selected Server Profiles
            for profilex in profile_names:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Starting on Server Profile {profilex}.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                policyMoid = policyDict[policy_name]['Moid']
                profileMoid = profileDict[profilex]['Moid']
                object_type = policy_api['enum'][2]

                # Index the Server List to find the Server Profile and pull the Policy Bucket
                name_index = dict((d['Name'], i) for i, d in enumerate(apiQuery['Results']))
                server_index = name_index.get(profilex, -1)
                policy_bucket = apiQuery['Results'][server_index]['PolicyBucket']

                # See if the Policy Type is Already Attached
                # If attached Update to the new Moid
                # If not attached the Policy
                object_index = dict((d['ObjectType'], i) for i, d in enumerate(policy_bucket))
                if object_index.get(object_type):
                    type_index = object_index.get(object_type, -1)
                    policy_link = f"https://www.intersight.com/api/v1/{policy_api['enum'][3]}/{policyMoid}"
                    policy_bucket[type_index].update({"Moid":policyMoid, "link": policy_link})
                    json_payload = {"PolicyBucket":policy_bucket}
                else:
                    policy_bucket.append({"classId": "mo.MoRef", "Moid": policyMoid, "ObjectType": object_type})
                    json_payload = {"PolicyBucket":policy_bucket}

                try:
                    kwargs = dict(_preload_content = False)
                    apiPost = json.loads(api_handle.patch_server_profile(profileMoid, json_payload, **kwargs).data)
                    print(json.dumps(apiPost, indent=4))
                except ApiException as e:
                    print("Exception when calling ServerApi->patch_server_profile: %s\n" % e)
                    sys.exit(1)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Finished Server Profile {profilex}.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Finished Loop on Organization {org}.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print('  Finished Updating Server Profiles...')
        print(f'\n-------------------------------------------------------------------------------------------\n')

    def add_vlan(self, **kwargs):
        args = kwargs['args']
        jsonFile = False
        if not args.json_file == None:
            jsonFile = True
            jsonOpen = open(args.json_file, 'r')
            jsonData = json.load(jsonOpen)
        tags = [{'key': 'Module','value': 'day2tools'}]

        def process_results(apiQuery):
            api_dict = {}
            api_list = []
            empty = False
            if apiQuery.get('Results'):
                for i in apiQuery['Results']:
                    iMoid = i['Moid']
                    iName = i['Name']
                    idict = {iName:{'Moid':iMoid}}
                    api_dict.update(idict)
                    api_list.append(iName)
                return empty, api_dict, api_list
            else:
                empty = True
                return empty, api_dict, api_list
        
        def empty_results(apiQuery):
                print(f"The API Query Results were empty for {apiQuery['ObjectType']}.  Exiting...")
                exit()
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print('  Beginning VLAN Addition...')
        print(f'\n-------------------------------------------------------------------------------------------\n')

        # Prompt User for VLAN.
        valid = False
        while valid == False:
            vlan_id = '%s' % (input(f'    What is the VLAN ID: '))
            if re.search('^\d+$', vlan_id): valid = classes.validating.number_in_range('VLAN ID', vlan_id, 1, 4094)

        # Prompt User for VLAN Name.
        valid = False
        while valid == False:
            vlan_name = '%s' % (input(f'    What is the name you want to assign to VLAN {vlan_id}: '))
            valid = classes.validating.name_rule('VLAN Name', vlan_name, 1, 62)

        # Query API for the Organization List
        api_client = credentials.config_credentials(home, args)
        api_handle = organization_api.OrganizationApi(api_client)
        kwargs = dict(_preload_content = False)
        apiQuery = json.loads(api_handle.get_organization_organization_list(**kwargs).data)
        empty, orgs, org_names = process_results(apiQuery)
        if empty == True: empty_results(apiQuery)

        # Request from User Which Organizations to Apply this to.
        if jsonFile == False:
            kwargs['multi_select'] = True
            kwargs['jData'] = {}
            kwargs['jData']['default']     = 'default'
            kwargs['jData']['description'] = 'Select the Organizations to Apply this VLAN to.'
            kwargs['jData']['enum']        = org_names
            kwargs['jData']['varType']     = 'Organizations'
            organizations = classes.ezfunctions.variablesFromAPI(**kwargs)
        else: organizations = jsonData['organizations']
        for org in organizations:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting Loop on Organization {org}.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            # Query the API for the VLAN Policies
            api_handle = fabric_api.FabricApi(api_client)
            query_filter = f"Organization.Moid eq '{orgs[org]['Moid']}'"
            qargs = dict(filter=query_filter, _preload_content = False)
            apiQuery = json.loads(api_handle.get_fabric_eth_network_policy_list(**qargs).data)
            empty, vlan_policies,vlan_policies_names = process_results(apiQuery)
            if empty == True: empty_results(apiQuery)

            # Prompt the User to Select the VLAN Policy
            if jsonFile == False:
                kwargs['multi_select'] = False
                kwargs['jData'] = {}
                kwargs['description'] = f'Select the VLAN Policy for Organization {org}.'
                kwargs['enum']        = vlan_policies_names
                kwargs['varType']     = 'VLAN Policy'
                vlan_policy = classes.ezfunctions.variablesFromAPI(**kwargs)
            else: vlan_policy = jsonData['vlan_policy']

            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Checking VLAN Policy {vlan_policy} for VLAN {vlan_id}.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            vlan_policy_moid = vlan_policies[vlan_policy]['Moid']
            query_filter = f"EthNetworkPolicy.Moid eq '{vlan_policy_moid}'"
            kwargs = dict(filter = query_filter, top = 1000, _preload_content = False)
            apiQuery = json.loads(api_handle.get_fabric_vlan_list(**kwargs).data)
            if apiQuery.get('Results'):
                mcast_policy_moid = apiQuery['Results'][1]['MulticastPolicy']['Moid']
                match_count = 0
                vlan_list = []
                for i in apiQuery['Results']:
                    vlan_list.append(i['VlanId'])
                    if int(i['VlanId']) == int(vlan_id):
                        match_count += 1
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print('  VLAN is already in the policy {} and has moid {}.').format(vlan_policy, i['Moid'])
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                vlan_list.sort()
                vlans = classes.ezfunctions.vlan_list_format(vlan_list)
                if match_count == 0:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  VLAN {vlan_id} was not in VLAN Policy {vlan_policy}.  Adding VLAN...')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    policy = {
                        'class_id':'fabric.Vlan',
                        'eth_network_policy': {
                            'class_id': 'mo.MoRef',
                            'moid': vlan_policy_moid,
                            'object_type': 'fabric.EthNetworkPolicy'
                        },
                        'is_native': False,
                        'multicast_policy': {
                            'class_id': 'mo.MoRef',
                            'moid': mcast_policy_moid,
                            'object_type': 'fabric.MulticastPolicy'
                        },
                        'name': vlan_name,
                        'object_type': 'fabric.Vlan',
                        'vlan_id': int(vlan_id)
                        }
                    try:
                        kwargs = dict(_preload_content = False)
                        apiPost = json.loads(api_handle.create_fabric_vlan(policy, **kwargs).data)
                        print(json.dumps(apiPost, indent=4))
                    except ApiException as e:
                        print("Exception when calling FabricApi->create_fabric_vlan: %s\n" % e)
                        sys.exit(1)

            # Query the API for Ethernet Network Group Policies
            query_filter = f"Organization.Moid eq '{orgs[org]['Moid']}'"
            qargs = dict(filter=query_filter, _preload_content = False)
            apiQuery = json.loads(api_handle.get_fabric_eth_network_group_policy_list(**qargs).data)
            empty, eth_group_policies,eth_group_policies_names = process_results(apiQuery)
            if empty == True: empty_results(apiQuery)

            # Prompt the User to Select the Ethernet Network Group Policies
            if jsonFile == False:
                kwargs['multi_select'] = True
                kwargs['jData']
                kwargs['var_description'] = f'Select the Ethernet Network Group Polices to append'\
                    f'the VLAN to in Organization {org}.'
                kwargs['jsonVars'] = eth_group_policies_names
                kwargs['defaultVar'] = ''
                kwargs['varType'] = 'VLAN Group Policies'
                ethernet_network_group_policies = classes.ezfunctions.variablesFromAPI(**kwargs)
            else:
                ethernet_network_group_policies = jsonData['ethernet_network_group_policies']

            for i in ethernet_network_group_policies:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f"  Patching the Ethernet Network Group Policy '{i}' ...")
                print(f'\n-------------------------------------------------------------------------------------------\n')
                ethgroup_moid = eth_group_policies[i]['Moid']
                patch_body = {
                    'vlan_settings':{
                        'allowed_vlans':vlans
                    }
                }
                try:
                    kwargs = dict(_preload_content = False)
                    apiPatch = json.loads(api_handle.patch_fabric_eth_network_group_policy(
                        fabric_eth_network_group_policy=patch_body,
                        moid=ethgroup_moid,
                        **kwargs
                    ).data)
                    print(json.dumps(apiPatch, indent=4))
                except ApiException as e:
                    print("Exception when calling FabricApi->patch_fabric_eth_network_group_policy: %s\n" % e)
                    sys.exit(1)

            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Checking if the Ethernet Network Group Policy {vlan_id}_NIC-A Already Exists.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            ethgcount = 0
            for k, v in eth_group_policies.items():
                if k == f'{vlan_id}_NIC-A':
                    ethgcount += 1
                    vnic_eth_net_grp = v['Moid']
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Ethernet Network Group Policy {vlan_id}_NIC-A Exists.  Moid is {vnic_eth_net_grp}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            if ethgcount == 0:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Ethernet Network Group Policy {vlan_id}_NIC-A does not exist.  Creating...')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                policy = {
                    'class_id': 'fabric.EthNetworkGroupPolicy',
                    'description': f'{vlan_id}_NIC-A Ethernet Network Group',
                    'name': f'{vlan_id}_NIC-A',
                    'object_type': 'fabric.EthNetworkGroupPolicy',
                    'organization': {
                        'class_id': 'mo.MoRef',
                        'moid':  orgs[org]['Moid'],
                        'object_type': 'organization.Organization'
                    },
                    'tags': tags,
                    'vlan_settings': {
                        'allowed_vlans': f'{vlan_id}',
                        'class_id': 'fabric.VlanSettings',
                        'native_vlan': int(vlan_id),
                        'object_type': 'fabric.VlanSettings'
                    }
                }
                try:
                    kwargs = dict(_preload_content = False)
                    apiPost = json.loads(api_handle.create_fabric_eth_network_group_policy(policy, **kwargs).data)
                    print(json.dumps(apiPost, indent=4))
                    vnic_eth_net_grp = apiPost['Moid']
                except ApiException as e:
                    print("Exception when calling FabricApi->create_fabric_eth_network_group_policy: %s\n" % e)
                    sys.exit(1)

            # Query the API for the Ethernet Network Control Policies
            query_filter = f"Organization.Moid eq '{orgs[org]['Moid']}'"
            qargs = dict(filter=query_filter, _preload_content = False)
            apiQuery = json.loads(api_handle.get_fabric_eth_network_control_policy_list(**qargs).data)
            empty, eth_control_policies,eth_control_names = process_results(apiQuery)
            if empty == True: empty_results(apiQuery)

            # Prompt User for the Ethernet Network Control Policy
            if jsonFile == False:
                kwargs['multi_select'] = False
                kwargs['var_description'] = f'Select the Ethernet Network Control Policy for Organization {org}.'
                kwargs['jsonVars'] = eth_control_names
                kwargs['defaultVar'] = ''
                kwargs['varType'] = 'Ethernet Network Control Policies'
                ethernet_network_control_policy = classes.ezfunctions.variablesFromAPI(**kwargs)
            else:
                ethernet_network_control_policy = jsonData['ethernet_network_control_policy']

            # Query the API for MAC Pools
            query_filter = f"Organization.Moid eq '{orgs[org]['Moid']}'"
            qargs = dict(filter=query_filter, _preload_content = False)
            api_handle = macpool_api.MacpoolApi(api_client)
            apiQuery = json.loads(api_handle.get_macpool_pool_list(**qargs).data)
            empty, mac_pools,mac_pools_names = process_results(apiQuery)
            if empty == True: empty_results(apiQuery)

            # Prompt User for MAC Pool
            if jsonFile == False:
                kwargs['var_description'] = f'Select the MAC Pool for Organization {org}.'
                kwargs['jsonVars'] = mac_pools_names
                kwargs['defaultVar'] = ''
                kwargs['varType'] = 'MAC Pool'
                mac_pool = classes.ezfunctions.variablesFromAPI(**kwargs)
            else:
                mac_pool = jsonData['mac_pool']

            # Query the API for the Ethernet Adapter Policies
            query_filter = f"Organization.Moid eq '{orgs[org]['Moid']}'"
            qargs = dict(filter=query_filter, _preload_content = False)
            api_handle = vnic_api.VnicApi(api_client)
            apiQuery = json.loads(api_handle.get_vnic_eth_adapter_policy_list(**qargs).data)
            empty, adapter_policies,adapter_policies_names = process_results(apiQuery)
            if empty == True: empty_results(apiQuery)

            # Prompt User for Ethernet Adapter Policy
            if jsonFile == False:
                kwargs['multi_select'] = False
                kwargs['var_description'] = f'Select the Ethernet Adapter Policy for Organization {org}.'
                kwargs['jsonVars'] = adapter_policies_names
                kwargs['defaultVar'] = ''
                kwargs['varType'] = 'Ethernet Adapter Policies'
                ethernet_adapter_policy = classes.ezfunctions.variablesFromAPI(**kwargs)
            else:
                ethernet_adapter_policy = jsonData['ethernet_adapter_policy']


            # Query the API for the Ethernet QoS Policies
            query_filter = f"Organization.Moid eq '{orgs[org]['Moid']}'"
            qargs = dict(filter=query_filter, _preload_content = False)
            apiQuery = json.loads(api_handle.get_vnic_eth_qos_policy_list(**qargs).data)
            empty, qos_policies,qos_policies_names = process_results(apiQuery)
            if empty == True: empty_results(apiQuery)

            # Prompt User for Ethernet Adapter Policy
            if jsonFile == False:
                kwargs['var_description'] = f'Select the Ethernet QoS Policy for Organization {org}.'
                kwargs['jsonVars'] = qos_policies_names
                kwargs['defaultVar'] = ''
                kwargs['varType'] = 'Ethernet QoS Policies'
                ethernet_qos_policy = classes.ezfunctions.variablesFromAPI(**kwargs)
            else:
                ethernet_qos_policy = jsonData['ethernet_qos_policy']


            # Query the API for the Adapter Policies
            query_filter = f"Organization.Moid eq '{orgs[org]['Moid']}'"
            qargs = dict(filter=query_filter, _preload_content = False)
            apiQuery = json.loads(api_handle.get_vnic_lan_connectivity_policy_list(**qargs).data)
            empty, lan_policies,lan_policies_names = process_results(apiQuery)
            if empty == True: empty_results(apiQuery)

            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Checking if the LAN Policy {vlan_id} Already Exists.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            lcount = 0
            for k, v in lan_policies.items():
                if k == vlan_id:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print('  LAN Policy {} exists.  Moid is {}').format(vlan_id, v['Moid'])
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    lcount += 1
            if lcount == 0:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  LAN Policy {vlan_id} does not exist.  Creating...')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                policy = {
                    'class_id':'vnic.LanConnectivityPolicy',
                    'name': str(vlan_id),
                    'object_type': 'vnic.LanConnectivityPolicy',
                    'organization': {
                        'class_id': 'mo.MoRef',
                        'moid': orgs[org]['Moid'],
                        'object_type': 'organization.Organization'
                    },
                    'tags': tags,
                    'target_platform': 'FIAttached'
                    }
                try:
                    kwargs = dict(_preload_content = False)
                    apiPost = json.loads(api_handle.create_vnic_lan_connectivity_policy(policy, **kwargs).data)
                    print(json.dumps(apiPost, indent=4))
                    lanp = {vlan_id:{'Moid':apiPost['Moid']}}
                    lan_policies.update(lanp)
                except ApiException as e:
                    print("Exception when calling VnicApi->create_vnic_lan_connectivity_policy: %s\n" % e)
                    sys.exit(1)

            print(f'\n-------------------------------------------------------------------------------------------\n')
            print('  Checking if the LAN Connectivity vNIC "NIC-A" Exists...')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            query_filter = f"LanConnectivityPolicy.Moid eq '{lan_policies[vlan_id]['Moid']}'"
            qargs = dict(filter=query_filter, _preload_content = False)
            apiQuery = json.loads(api_handle.get_vnic_eth_if_list(**qargs).data)
            empty, vnics, vnic_names = process_results(apiQuery)
            if empty == True:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f"  vNIC 'NIC-A' was not attached to LAN Policy {vlan_id}.  Creating...")
                print(f'\n-------------------------------------------------------------------------------------------\n')
                policy = {
                    'cdn': {
                        'class_id': 'vnic.Cdn',
                        'object_type': 'vnic.Cdn',
                        'source': 'vnic',
                        'value': 'NIC-A'
                    },
                    'class_id': 'vnic.EthIf',
                    'eth_adapter_policy': {
                        'class_id': 'mo.MoRef',
                        'moid': adapter_policies[ethernet_adapter_policy]['Moid'],
                        'object_type': 'vnic.EthAdapterPolicy'
                    },
                    'eth_network_policy': None,
                    'eth_qos_policy': {
                        'class_id': 'mo.MoRef',
                        'moid': qos_policies[ethernet_qos_policy]['Moid'],
                        'object_type': 'vnic.EthQosPolicy'
                    },
                    'fabric_eth_network_control_policy': {
                        'class_id': 'mo.MoRef',
                        'moid': eth_control_policies[ethernet_network_control_policy]['Moid'],
                        'object_type': 'fabric.EthNetworkControlPolicy'
                    },
                    'fabric_eth_network_group_policy': [
                        {
                            'class_id': 'mo.MoRef',
                            'moid': vnic_eth_net_grp,
                            'object_type': 'fabric.EthNetworkGroupPolicy'
                        }
                    ],
                    'failover_enabled': True,
                    'lan_connectivity_policy': {
                        'class_id': 'mo.MoRef',
                        'moid': lan_policies[vlan_id]['Moid'],
                        'object_type': 'vnic.LanConnectivityPolicy'
                    },
                    'mac_address_type': 'POOL',
                    'mac_lease': None,
                    'mac_pool': {
                        'class_id': 'mo.MoRef',
                        'moid': mac_pools[mac_pool]['Moid'],
                        'object_type': 'macpool.Pool'
                    },
                    'name': 'NIC-A',
                    'object_type': 'vnic.EthIf',
                    'order': 2,
                    'placement': {
                        'class_id': 'vnic.PlacementSettings',
                        'id': 'MLOM',
                        'object_type': 'vnic.PlacementSettings',
                        'pci_link': 0,
                        'switch_id': 'A',
                        'uplink': 0
                    },
                }
                try:
                    kwargs = dict(_preload_content = False)
                    apiPost = json.loads(api_handle.create_vnic_eth_if(policy, **kwargs).data)
                    print(json.dumps(apiPost, indent=4))
                except ApiException as e:
                    print("Exception when calling VnicApi->create_vnic_lan_connectivity_policy: %s\n" % e)
                    sys.exit(1)
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print('  LAN Connectivity vNIC "NIC-A" exists.  Moid is {}').format(vnics['NIC-A']['Moid'])
                print(f'\n-------------------------------------------------------------------------------------------\n')
                
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Finished Loop on Organization {org}.')
            print(f'\n-------------------------------------------------------------------------------------------\n')

        print(f'\n-------------------------------------------------------------------------------------------\n')
        print('  Finished Adding VLAN...')
        print(f'\n-------------------------------------------------------------------------------------------\n')

    def hcl_inventory(self, **kwargs):
        args     = kwargs['args']
        pyDict   = {}
        jsonData = kwargs['json_data']

        # Obtain Server Profile Data
        api_client = credentials.config_credentials(home, args)
        for item in jsonData:
            if 'Cisco' in item['Hostname']['Manufacturer']:
                esxBuild    = item['Hostname']['Build']
                esxVersion  = item['Hostname']['Version']
                Hostname    = item['Hostname']['Name']
                Serial      = item['Serial']
                toolDate    = item['InstallDate']
                toolName    = item['Name']
                toolVersion = item['Version']

                # Query API for Server Details
                api_client = credentials.config_credentials(home, args)
                api_handle = compute_api.ComputeApi(api_client)
                api_filter = f"Serial eq '{Serial}'"
                api_args = dict(filter= api_filter, _preload_content = False)
                if re.search('UCSB', item['Hostname']['Model']):
                    apiQuery = json.loads(api_handle.get_compute_blade_identity_list(**api_args).data)
                else:
                    apiQuery = json.loads(api_handle.get_compute_rack_unit_list(**api_args).data)
                if apiQuery.get('Results'):
                    for i in apiQuery['Results']:
                        if re.search('UCSB', item['Hostname']['Model']):
                            serverDn = 'chassis-' + str(i['ChassisId']) + "/blade-" + str(i['SlotId'])
                        else:
                            serverDn = 'rackunit-' + str(i['ServerId'])
                        physMoid = i['Moid']
                        if i.get('ServiceProfile'): serverP = i['ServiceProfile']
                        else: serverP = ''
                        api_handle = asset_api.AssetApi(api_client)
                        api_args = dict(_preload_content = False)
                        domainParent = json.loads(api_handle.get_asset_device_registration_by_moid(
                            i['RegisteredDevice']['Moid'], **api_args).data
                        )
                # Obtain Server Profile Data
                api_filter = f"ManagedObject.Moid eq '{physMoid}'"
                api_args = dict(filter=api_filter, _preload_content = False)
                api_handle = cond_api.CondApi(api_client)
                apiQuery = json.loads((api_handle.get_cond_hcl_status_list(**api_args)).data)
                if apiQuery.get('Results'):
                    hostResults = {
                        Serial:{
                            'Domain':domainParent['DeviceHostname'][0],
                            'Model':apiQuery['Results'][0]['HclModel'],
                            'Serial':Serial,
                            'Server':serverDn,
                            'Profile':serverP,
                            'Firmware':apiQuery['Results'][0]['HclFirmwareVersion'],
                            'Hostname':Hostname,
                            'ESX Version':esxVersion,
                            'ESX Build':esxBuild,
                            'UCS Tools Install Date':toolDate,
                            'UCS Tools Version':toolVersion
                        }
                    }
                    pyDict.update(hostResults)

        if len(pyDict) > 0:
            # Build Named Style Sheets for Workbook
            bd1 = Side(style="thick", color="0070C0")
            bd2 = Side(style="medium", color="0070C0")
            heading_1 = NamedStyle(name="heading_1")
            heading_1.alignment = Alignment(horizontal="center", vertical="center", wrap_text="True")
            heading_1.border = Border(left=bd1, top=bd1, right=bd1, bottom=bd1)
            heading_1.fill = PatternFill("solid", fgColor="305496")
            heading_1.font = Font(bold=True, size=15, color="FFFFFF")
            heading_2 = NamedStyle(name="heading_2")
            heading_2.alignment = Alignment(horizontal="center", vertical="center", wrap_text="True")
            heading_2.border = Border(left=bd2, top=bd2, right=bd2, bottom=bd2)
            heading_2.font = Font(bold=True, size=15, color="44546A")
            even = NamedStyle(name="even")
            even.alignment = Alignment(horizontal="center", vertical="center", wrap_text="True")
            even.border = Border(left=bd1, top=bd1, right=bd1, bottom=bd1)
            even.font = Font(bold=False, size=12, color="44546A")
            odd = NamedStyle(name="odd")
            odd.alignment = Alignment(horizontal="center", vertical="center", wrap_text="True")
            odd.border = Border(left=bd2, top=bd2, right=bd2, bottom=bd2)
            odd.fill = PatternFill("solid", fgColor="D9E1F2")
            odd.font = Font(bold=False, size=12, color="44546A")

            Est = pytz.timezone('US/Eastern')
            datetime_est = datetime.now(Est)
            Est1 = datetime_est.strftime('%Y-%m-%d_%H-%M')
            Est2 = datetime_est.strftime('%Y-%m-%d %H:%M:%S %Z %z')

            workbook = f'UCS-Tools-Inventory-{Est1}.xlsx'
            wb = openpyxl.Workbook()
            wb.add_named_style(heading_1)
            wb.add_named_style(heading_2)
            wb.add_named_style(even)
            wb.add_named_style(odd)
            ws = wb.active
            ws.title = 'Inventory List'

            # Read Server Inventory to Create Column Headers
            column_headers = [
                'Domain','Model','Serial','Server','Profile','Firmware','Hostname','ESX Version','ESX Build',
                'UCS Tools Install Date', 'UCS Tools Version'
            ]
            for i in range(len(column_headers)):
                ws.column_dimensions[chr(ord('@')+i+1)].width = 30
            cLength = len(column_headers)
            ws_header = f'Collected UCS Data on {Est2}'
            data = [ws_header]
            ws.append(data)
            ws.merge_cells(f'A1:{chr(ord("@")+cLength)}1')
            for cell in ws['1:1']:
                cell.style = 'heading_1'
            ws.append(column_headers)
            for cell in ws['2:2']:
                cell.style = 'heading_2'
            ws_row_count = 3
            
            # Populate the Columns with Server Inventory
            for key, value in pyDict.items():
                data = []
                for k, v in value.items():
                    data.append(v)
                    
                # Add the Columns to the Spreadsheet
                ws.append(data)
                for cell in ws[ws_row_count:ws_row_count]:
                    if ws_row_count % 2 == 0: cell.style = 'odd'
                    else: cell.style = 'even'
                ws_row_count += 1
            
            # Save the Workbook
            wb.save(filename=workbook)

    def hcl_status(self, **kwargs):
        args = kwargs['args']
        pyDict = {}
        # Obtain Server Profile Data
        api_client = credentials.config_credentials(home, args)
        kwargs = dict(top = 1000, _preload_content = False)
        api_handle = server_api.ServerApi(api_client)
        apiQuery = json.loads((api_handle.get_server_profile_list(**kwargs)).data)
        if not apiQuery.get('Results'):
            print('empty results.  Exiting script...')
        for i in apiQuery['Results']:
            profileMoid = i['Moid']
            profileName = i['Name']
            print(f'Obtaining Data for Server Profile {profileName}')
            if i['TargetPlatform'] == 'FIAttached':
                if i['AssociatedServer']:
                    
                    # Obtain Physical UCS Server Information
                    serverMoid = i['AssociatedServer']['Moid']
                    serverType = i['AssociatedServer']['ObjectType']
                    api_handle = compute_api.ComputeApi(api_client)
                    kwargs = dict(_preload_content = False)
                    if serverType == 'compute.Blade':
                        apiQuery = json.loads(api_handle.get_compute_blade_by_moid(serverMoid, **kwargs).data)
                        serverDn = 'chassis-' + str(apiQuery['ChassisId']) + "/blade-" + str(apiQuery['SlotId'])
                    else:
                        apiQuery = json.loads(api_handle.get_compute_rack_unit_by_moid(serverMoid, **kwargs).data)
                        serverDn = 'rackunit-' + str(apiQuery['ServerId'])
                    serverSerial = apiQuery['Serial']
                    api_handle = asset_api.AssetApi(api_client)
                    serverReg = json.loads(api_handle.get_asset_device_registration_by_moid(
                        apiQuery['RegisteredDevice']['Moid'], **kwargs).data
                    )
                    domainParent = json.loads(api_handle.get_asset_device_registration_by_moid(
                        serverReg['ParentConnection']['Moid'], **kwargs).data
                    )

                    # Get HCL Status
                    api_handle = cond_api.CondApi(api_client)
                    query_filter = f"ManagedObject.Moid eq '{serverMoid}'"
                    kwargs = dict(filter = query_filter, _preload_content = False)
                    hclQuery = json.loads(api_handle.get_cond_hcl_status_list(**kwargs).data)
                    # print(json.dumps(hclQuery['Results'], indent=4))

                    hostResults = {
                        profileName:{
                            'domain_name':domainParent['DeviceHostname'][0],
                            'moid':profileMoid,
                            'serial':serverSerial,
                            'server_dn':serverDn,
                            'hcl_status':hclQuery['Results'][0]['Status']
                        }
                    }
                    pyDict.update(hostResults)

            # Build Named Style Sheets for Workbook
            bd1 = Side(style="thick", color="0070C0")
            bd2 = Side(style="medium", color="0070C0")
            heading_1 = NamedStyle(name="heading_1")
            heading_1.alignment = Alignment(horizontal="center", vertical="center", wrap_text="True")
            heading_1.border = Border(left=bd1, top=bd1, right=bd1, bottom=bd1)
            heading_1.fill = PatternFill("solid", fgColor="305496")
            heading_1.font = Font(bold=True, size=15, color="FFFFFF")
            heading_2 = NamedStyle(name="heading_2")
            heading_2.alignment = Alignment(horizontal="center", vertical="center", wrap_text="True")
            heading_2.border = Border(left=bd2, top=bd2, right=bd2, bottom=bd2)
            heading_2.font = Font(bold=True, size=15, color="44546A")
            even = NamedStyle(name="even")
            even.alignment = Alignment(horizontal="center", vertical="center", wrap_text="True")
            even.border = Border(left=bd1, top=bd1, right=bd1, bottom=bd1)
            even.font = Font(bold=False, size=12, color="44546A")
            odd = NamedStyle(name="odd")
            odd.alignment = Alignment(horizontal="center", vertical="center", wrap_text="True")
            odd.border = Border(left=bd2, top=bd2, right=bd2, bottom=bd2)
            odd.fill = PatternFill("solid", fgColor="D9E1F2")
            odd.font = Font(bold=False, size=12, color="44546A")

            Est = pytz.timezone('US/Eastern')
            datetime_est = datetime.now(Est)
            Est1 = datetime_est.strftime('%Y-%m-%d_%H-%M')
            Est2 = datetime_est.strftime('%Y-%m-%d %H:%M:%S %Z %z')
            workbook = f'HCL_Status_Collector-{Est1}.xlsx'
            wb = openpyxl.Workbook()
            wb.add_named_style(heading_1)
            wb.add_named_style(heading_2)
            wb.add_named_style(even)
            wb.add_named_style(odd)
            ws = wb.active
            ws.title = 'HCL Status'
            ws.column_dimensions['A'].width = 30
            ws.column_dimensions['B'].width = 30
            ws.column_dimensions['C'].width = 30
            ws.column_dimensions['D'].width = 30
            ws_header = f'Collected UCS Data on {Est2}'
            data = [ws_header]
            ws.append(data)
            ws.merge_cells('A1:D1')
            for cell in ws['1:1']:
                cell.style = 'heading_1'
            data = [
                'Server Profile','Physical Server','Serial Number','HCL Status'
            ]
            ws.append(data)
            for cell in ws['2:2']:
                cell.style = 'heading_2'
            ws_row_count = 3
            for k, v in pyDict.items():
                data = [
                    k,
                    v['server_dn'],
                    v['serial'],
                    v['hcl_status']
                ]
                ws.append(data)
                for cell in ws[ws_row_count:ws_row_count]:
                    if ws_row_count % 2 == 0:
                        cell.style = 'odd'
                    else:
                        cell.style = 'even'
                ws_row_count += 1
            wb.save(filename=workbook)

    def server_inventory(self, **kwargs):
        args     = kwargs['args']
        pyDict   = {}
        # Obtain Server Profile Data
        api_client = credentials.config_credentials(home, args)
        kwargs = dict(top = 1000, _preload_content = False)
        api_handle = server_api.ServerApi(api_client)
        apiQuery = json.loads((api_handle.get_server_profile_list(**kwargs)).data)
        if not apiQuery.get('Results'):
            print('empty results.  Exiting script...')
        for i in apiQuery['Results']:
            profileMoid = i['Moid']
            profileName = i['Name']
            print(f'Obtaining Data for Server Profile {profileName}')
            if i['TargetPlatform'] == 'FIAttached':
                if i['AssociatedServer']:
                    api_handle = fcpool_api.FcpoolApi(api_client)
                    query_filter = f"PoolPurpose eq 'WWNN' and AssignedToEntity.Moid eq '{profileMoid}'"
                    kwargs = dict(filter = query_filter, _preload_content = False)
                    fcPool = json.loads(api_handle.get_fcpool_lease_list(**kwargs).data)
                    wwnn_address = fcPool['Results'][0]['WwnId']

                    # Obtain Physical UCS Server Information
                    serverMoid = i['AssociatedServer']['Moid']
                    serverType = i['AssociatedServer']['ObjectType']
                    api_handle = compute_api.ComputeApi(api_client)
                    kwargs = dict(_preload_content = False)
                    if serverType == 'compute.Blade':
                        apiQuery = json.loads(api_handle.get_compute_blade_by_moid(serverMoid, **kwargs).data)
                        serverDn = 'chassis-' + str(apiQuery['ChassisId']) + "/blade-" + str(apiQuery['SlotId'])
                    else:
                        apiQuery = json.loads(api_handle.get_compute_rack_unit_by_moid(serverMoid, **kwargs).data)
                        serverDn = 'rackunit-' + str(apiQuery['ServerId'])
                    serverSerial = apiQuery['Serial']
                    api_handle = asset_api.AssetApi(api_client)
                    serverReg = json.loads(api_handle.get_asset_device_registration_by_moid(
                        apiQuery['RegisteredDevice']['Moid'], **kwargs).data
                    )
                    domainParent = json.loads(api_handle.get_asset_device_registration_by_moid(
                        serverReg['ParentConnection']['Moid'], **kwargs).data
                    )

                    # Obtain Server vNICs (Ethernet/Fibre-Channel)
                    api_handle = vnic_api.VnicApi(api_client)
                    query_filter = f"Profile.Moid eq '{profileMoid}'"
                    kwargs = dict(filter = query_filter, _preload_content = False)
                    ethapiQuery = json.loads(api_handle.get_vnic_eth_if_list(**kwargs).data)
                    fcapiQuery  = json.loads(api_handle.get_vnic_fc_if_list(**kwargs).data)
                    vnics = {}
                    for item in ethapiQuery['Results']:
                        vnic_name = item['Name']
                        mac_address = item['MacAddress']
                        ngpMoid = item['FabricEthNetworkGroupPolicy'][0]['Moid']
                        qosMoid = item['EthQosPolicy']['Moid']
                        api_handle = vnic_api.VnicApi(api_client)
                        kwargs = dict(_preload_content = False)
                        qosPolicy = json.loads(api_handle.get_vnic_eth_qos_policy_by_moid(qosMoid, **kwargs).data)
                        mTu = qosPolicy['Mtu']
                        vnic = {
                            vnic_name: {
                                'mac_address':mac_address,
                                'mtu':mTu,
                            }
                        }
                        vnics.update(vnic)

                    vhbas = {}
                    for item in fcapiQuery['Results']:
                        vhba_name = item['Name']
                        if item['WwpnAddressType'] == 'STATIC':
                            wwpn_address = item['StaticWwpnAddress']
                        else:
                            wwpn_address = item['Wwpn']
                        switch_id = item['Placement']['SwitchId']
                        fcnpMoid = item['FcNetworkPolicy']['Moid']
                        vhbas[vhba_name] = {
                            'switch_id':switch_id,
                            'wwpn_address':wwpn_address
                        }
                    sorted_vhbas = {}
                    for key in sorted(vhbas):
                        sorted_vhbas[key] = vhbas[key]
                    sorted_vnics = {}
                    for key in sorted(vnics):
                        sorted_vnics[key] = vnics[key]
                    hostResults = {
                        profileName:{
                            'domain_name':domainParent['DeviceHostname'][0],
                            'moid':profileMoid,
                            'serial':serverSerial,
                            'server_dn':serverDn,
                            'vhbas':sorted_vhbas,
                            'vnics':sorted_vnics,
                            'wwnn':wwnn_address
                        }
                    }
                    pyDict.update(hostResults)

        if len(pyDict) > 0:
            pyDict = OrderedDict(sorted(pyDict.items()))

            # Build Named Style Sheets for Workbook
            bd1 = Side(style="thick", color="0070C0")
            bd2 = Side(style="medium", color="0070C0")
            heading_1 = NamedStyle(name="heading_1")
            heading_1.alignment = Alignment(horizontal="center", vertical="center", wrap_text="True")
            heading_1.border = Border(left=bd1, top=bd1, right=bd1, bottom=bd1)
            heading_1.fill = PatternFill("solid", fgColor="305496")
            heading_1.font = Font(bold=True, size=15, color="FFFFFF")
            heading_2 = NamedStyle(name="heading_2")
            heading_2.alignment = Alignment(horizontal="center", vertical="center", wrap_text="True")
            heading_2.border = Border(left=bd2, top=bd2, right=bd2, bottom=bd2)
            heading_2.font = Font(bold=True, size=15, color="44546A")
            even = NamedStyle(name="even")
            even.alignment = Alignment(horizontal="center", vertical="center", wrap_text="True")
            even.border = Border(left=bd1, top=bd1, right=bd1, bottom=bd1)
            even.font = Font(bold=False, size=12, color="44546A")
            odd = NamedStyle(name="odd")
            odd.alignment = Alignment(horizontal="center", vertical="center", wrap_text="True")
            odd.border = Border(left=bd2, top=bd2, right=bd2, bottom=bd2)
            odd.fill = PatternFill("solid", fgColor="D9E1F2")
            odd.font = Font(bold=False, size=12, color="44546A")

            Est = pytz.timezone('US/Eastern')
            datetime_est = datetime.now(Est)
            Est1 = datetime_est.strftime('%Y-%m-%d_%H-%M')
            Est2 = datetime_est.strftime('%Y-%m-%d %H:%M:%S %Z %z')

            if args.full_inventory:
                workbook = f'UCS-Inventory-Collector-{Est1}.xlsx'
                wb = openpyxl.Workbook()
                wb.add_named_style(heading_1)
                wb.add_named_style(heading_2)
                wb.add_named_style(even)
                wb.add_named_style(odd)
                ws = wb.active
                ws.title = 'Inventory List'

                # Read Server Inventory to Create Column Headers
                column_headers = ['Domain','Profile','Server','Serial']
                # print(json.dumps(pyDict, indent=4))
                vhba_list = []
                vnic_list = []
                for key, value in pyDict.items():
                    if value.get('wwnn'):
                        if not 'WWNN' in column_headers:
                            column_headers.append('WWNN')
                    if value.get('vhbas'):
                        for k, v in value['vhbas'].items():
                            if not k in vhba_list:
                                vhba_list.append(k)
                    if value.get('vnics'):
                        for k, v in value['vnics'].items():
                            if not k in vnic_list:
                                vnic_list.append(k)
                vhba_list.sort()
                vnic_list.sort()
                column_headers = column_headers + vhba_list + vnic_list
                for i in range(len(column_headers)):
                    ws.column_dimensions[chr(ord('@')+i+1)].width = 30
                cLength = len(column_headers)
                ws_header = f'Collected UCS Data on {Est2}'
                data = [ws_header]
                ws.append(data)
                ws.merge_cells(f'A1:{chr(ord("@")+cLength)}1')
                for cell in ws['1:1']:
                    cell.style = 'heading_1'
                ws.append(column_headers)
                for cell in ws['2:2']:
                    cell.style = 'heading_2'
                ws_row_count = 3
                
                # Populate the Columns with Server Inventory
                for k, v in pyDict.items():
                    data = []
                    for i in column_headers:
                        column_count = 0
                        if i == 'Domain':
                            data.append(v['domain_name'])
                            column_count += 1
                        elif i == 'Profile':
                            data.append(k)
                            column_count += 1
                        elif i == 'Server':
                            data.append(v['server_dn'])
                            column_count += 1
                        elif i == 'Serial':
                            data.append(v['serial'])
                            column_count += 1
                        elif i == 'WWNN':
                            data.append(v['wwnn'])
                            column_count += 1
                        else:
                            if v.get('vhbas'):
                                for key, value in v['vhbas'].items():
                                    if i == key:
                                        data.append(value['wwpn_address'])
                                        column_count += 1
                            if v.get('vnics'):
                                for key, value in v['vnics'].items():
                                    if i == key:
                                        data.append(value['mac_address'])
                                        column_count += 1
                        if column_count == 0:
                            data.append('Not Configured')
                        
                    # Add the Columns to the Spreadsheet
                    ws.append(data)
                    for cell in ws[ws_row_count:ws_row_count]:
                        if ws_row_count % 2 == 0:
                            cell.style = 'odd'
                        else:
                            cell.style = 'even'
                    ws_row_count += 1
                
                # Save the Workbook
                wb.save(filename=workbook)
            else:
                workbook = f'UCS-WWPN-Collector-{Est1}.xlsx'
                wb = openpyxl.Workbook()
                wb.add_named_style(heading_1)
                wb.add_named_style(heading_2)
                wb.add_named_style(even)
                wb.add_named_style(odd)
                ws = wb.active
                ws.title = 'WWPN List'


                # Read Server Inventory to Create Column Headers
                column_headers = ['Profile']
                # print(json.dumps(pyDict, indent=4))
                vhba_list = []
                for key, value in pyDict.items():
                    if value.get('wwnn'):
                        if not 'WWNN' in column_headers:
                            column_headers.append('WWNN')
                    if value.get('vhbas'):
                        for k, v in value['vhbas'].items():
                            if not k in vhba_list:
                                vhba_list.append(k)
                vhba_list.sort()
                column_headers= column_headers + vhba_list
                for i in range(len(column_headers)):
                    ws.column_dimensions[chr(ord('@')+i+1)].width = 30
                cLength = len(column_headers)
                ws_header = f'Collected UCS Data on {Est2}'
                data = [ws_header]
                ws.append(data)
                ws.merge_cells(f'A1:{chr(ord("@")+cLength)}1')
                for cell in ws['1:1']:
                    cell.style = 'heading_1'
                ws.append(data)
                for cell in ws['2:2']:
                    cell.style = 'heading_2'
                ws_row_count = 3
                
                # Populate the Columns with Server Inventory
                for k, v in pyDict.items():
                    data = []
                    for i in column_headers:
                        column_count = 0
                        if i == 'Profile':
                            data.append(k)
                            column_count += 1
                        elif i == 'WWNN':
                            data.append(v['wwnn'])
                            column_count += 1
                        else:
                            if v.get('vhbas'):
                                for key, value in v['vhbas'].items():
                                    if i == key:
                                        data.append(value['wwpn_address'])
                                        column_count += 1
                        if column_count == 0:
                            data.append('Not Configured')
                        
                    # Add the Columns to the Spreadsheet
                    ws.append(data)
                    for cell in ws[ws_row_count:ws_row_count]:
                        if ws_row_count % 2 == 0:
                            cell.style = 'odd'
                        else:
                            cell.style = 'even'
                    ws_row_count += 1
                
                # Save the Workbook
                wb.save(filename=workbook)
