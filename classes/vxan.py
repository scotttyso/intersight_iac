#!/usr/bin/env python3
from copy import deepcopy
import ezfunctions
import jinja2
import json
import os
import pkg_resources
import platform
import re
import validating

ucs_template_path = pkg_resources.resource_filename('vxan', '../templates/')

class policies(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # Multicast Policy Module
    #==============================================
    def multicast_policies(self, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'multicast'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Multicast Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'multicast_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Each VLAN must have a Multicast Policy applied to it.  Optional attributes will be')
            print(f'  the IGMP Querier IPs.  IGMP Querier IPs are only needed if you have a non Routed VLAN')
            print(f'  and you need the Fabric Interconnects to act as IGMP Queriers for the network.')
            print(f'  If you configure IGMP Queriers for a Multicast Policy that Policy should only be')
            print(f'  Assigned to the VLAN for which those Queriers will service.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)
                polVars["igmp_snooping_state"] = 'Enabled'

                valid = False
                while valid == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    polVars["querier_ip_address"] = input('IGMP Querier IP for Fabric Interconnect A.  [press enter to skip] ')
                    if polVars["querier_ip_address"] == '':
                        valid = True
                    if not polVars["querier_ip_address"] == '':
                        valid = validating.ip_address('Fabric A IGMP Querier IP', polVars["querier_ip_address"])

                    if not polVars["querier_ip_address"] == '':
                        polVars["igmp_snooping_querier_state"] == 'Enabled'
                        valid = False
                        while valid == False:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            polVars["querier_ip_address_peer"] = input('IGMP Querier IP for Fabric Interconnect B.  [press enter to skip] ')
                            if polVars["querier_ip_address_peer"] == '':
                                valid = True
                            if not polVars["querier_ip_address_peer"] == '':
                                valid = validating.ip_address('Fabric B IGMP Querier IP', polVars["querier_ip_address"])
                    else:
                        polVars["igmp_snooping_querier_state"] = 'Disabled'
                        polVars["querier_ip_address_peer"] = ''

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    description                 = "{polVars["descr"]}"')
                print(f'    igmp_snooping_state         = "{polVars["igmp_snooping_state"]}"')
                print(f'    igmp_snooping_querier_state = "{polVars["igmp_snooping_querier_state"]}"')
                print(f'    name                        = "{polVars["name"]}"')
                if not polVars["querier_ip_address_peer"] == '':
                    print(f'    querier_ip_address          = "{polVars["querier_ip_address"]}"')
                    print(f'    querier_ip_address_peer     = "{polVars["querier_ip_address_peer"]}"')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **polVars)

                        configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                        valid_confirm = True

                    elif confirm_policy == 'N':
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Starting {polVars["policy_type"]} Section over.')
                        print(f'\n------------------------------------------------------\n')
                        valid_confirm = True

                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # VLAN Policy Module
    #==============================================
    def vlan_policies(self, jsonData, ezData, **kwargs):
        vlan_policies_vlans = []
        name_prefix = self.name_prefix
        name_suffix = 'vlans'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'VLAN Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'vlan_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will define the VLANs Assigned to the Fabric Interconnects.')
            print(f'  The vlan list can be in the format of:')
            print(f'     5 - Single VLAN')
            print(f'     1-10 - Range of VLANs')
            print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
            print(f'     1-10,20-30 - Ranges and Lists of VLANs')
            print(f'  When configuring a VLAN List or Range the name will be used as a prefix in the format of:')
            print('     {name}-vlXXXX')
            print(f'  Where XXXX would be 0001 for vlan 1, 0100 for vlan 100, and 4094 for vlan 4094.')
            print(f'  If you want to Assign a Native VLAN Make sure it is in the vlan list for this wizard.')
            print(f'  IMPORTANT NOTE: You can only have one Native VLAN for the Fabric at this time,')
            print(f'                  as Disjoint Layer 2 is not yet supported.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:
                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)
                polVars["auto_allow_on_uplinks"] = True

                valid = False
                while valid == False:
                    vlan_list = '%s' % (input(f'Enter the VLAN or List of VLANs to add to {polVars["name"]}: '))
                    if not vlan_list == '':
                        vlan_list_expanded = ezfunctions.vlan_list_full(vlan_list)
                        valid_vlan = True
                        for vlan in vlan_list_expanded:
                            valid_vlan = validating.number_in_range('VLAN ID', vlan, 1, 4094)
                            if valid_vlan == False:
                                break
                        native_count = 0
                        native_vlan = ''
                        native_name = ''
                        if valid_vlan == True:
                            valid_name = False
                            while valid_name == False:
                                if len(vlan_list_expanded) == 1:
                                    vlan_name = '%s' % (input(f'Enter the Name you want to assign to "{vlan_list}": '))
                                    valid_name = validating.name_rule('VLAN Name', vlan_name, 1, 62)
                                else:
                                    vlan_name = '%s' % (input(f'Enter the Prefix Name you want to assign to "{vlan_list}": '))
                                    valid_name = validating.name_rule('VLAN Name', vlan_name, 1, 55)
                            native_vlan = input('Do you want to configure one of the VLANs as a Native VLAN? [press enter to skip]:')
                        if not native_vlan == '' and valid_vlan == True:
                            for vlan in vlan_list_expanded:
                                if int(native_vlan) == int(vlan):
                                    native_count = 1
                            if native_count == 1:
                                valid_name = False
                                while valid_name == False:
                                    native_name = '%s' % (input(f'Enter the Name to assign to the Native VLAN {native_vlan}.  [default]: '))
                                    if native_name == '':
                                        native_name = 'default'
                                    valid_name = validating.name_rule('VLAN Name', vlan_name, 1, 62)
                                valid = True
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! The Native VLAN was not in the Allowed List.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        elif valid_vlan == True:
                            valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  The allowed vlan list can be in the format of:')
                        print(f'     5 - Single VLAN')
                        print(f'     1-10 - Range of VLANs')
                        print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
                        print(f'     1-10,20-30 - Ranges and Lists of VLANs')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                if not native_vlan == '':
                    if int(native_vlan) in vlan_list_expanded:
                        while(int(native_vlan) in vlan_list_expanded):
                            vlan_list_expanded.remove(int(native_vlan))
                elif native_vlan == '' and 1 in vlan_list_expanded:
                    native_vlan == 1
                    while(1 in vlan_list_expanded):
                        vlan_list_expanded.remove(1)

                polVars["vlan_list"] = ezfunctions.vlan_list_format(vlan_list_expanded)

                vlan_list = ezfunctions.vlan_list_format(vlan_list_expanded)
                
                policy_list = [
                    'policies.multicast_policies.multicast_policy'
                ]
                polVars["allow_opt_out"] = False
                for policy in policy_list:
                    policy_short = policy.split('.')[2]
                    polVars[policy_short],policyData = policy_select_loop(jsonData, ezData, name_prefix, policy, **polVars)
                    polVars.update(policyData)

                if not native_vlan == '' and len(vlan_list) > 1:
                    if int(native_vlan) == 1:
                        auto_native = True
                    else:
                        auto_native = False
                    polVars["vlans"] = [
                        {
                            'auto_allow_on_uplinks':auto_native,
                            'id':native_vlan,
                            'multicast_policy':polVars["multicast_policy"],
                            'name':native_name,
                            'native_vlan':True
                        },
                        {
                            'auto_allow_on_uplinks':False,
                            'id':vlan_list,
                            'multicast_policy':polVars["multicast_policy"],
                            'name':vlan_name,
                            'native_vlan':False
                        }
                    ]
                elif not native_vlan == '' and len(vlan_list) == 1:
                    if int(native_vlan) == 1:
                        auto_native = True
                    else:
                        auto_native = False
                    polVars["vlans"] = [
                        {
                            'auto_allow_on_uplinks':auto_native,
                            'id':native_vlan,
                            'multicast_policy':polVars["multicast_policy"],
                            'name':native_name,
                            'native_vlan':True
                        }
                    ]
                else:
                    polVars["vlans"] = [
                        {
                            'auto_allow_on_uplinks':False,
                            'id':vlan_list,
                            'multicast_policy':polVars["multicast_policy"],
                            'name':vlan_name,
                            'native_vlan':False
                        }
                    ]

                print(json.dumps(polVars, indent=4))
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   description      = "{polVars["descr"]}"')
                print(f'   multicast_policy = "{polVars["multicast_policy"]}"')
                print(f'   name             = "{polVars["name"]}"')
                if not native_vlan == '':
                    print(f'   native_vlan      = "{native_vlan}"')
                    print(f'   native_vlan_name = "{native_name}"')
                print(f'   vlan_list        = "{vlan_list}"')
                print(f'   vlan_name        = "{vlan_name}"')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **polVars)

                        # Add VLANs to VLAN Policy List
                        vlan_policies_vlans.append({polVars['name']:vlan_list_expanded})

                        configure_loop, policy_loop = ezfunctions.exit_default_no(polVars["policy_type"])
                        valid_confirm = True

                    elif confirm_policy == 'N':
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Starting {polVars["policy_type"]} Section over.')
                        print(f'\n------------------------------------------------------\n')
                        valid_confirm = True

                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # VSAN Policy Module
    #==============================================
    def vsan_policies(self, jsonData, ezData, **kwargs):
        vsan_policies_vsans = []
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'VSAN Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'vsan_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  A {policy_type} will define the VSANs Assigned to the Fabric Interconnects.  You will need')
            print(f'  one VSAN Policy for Fabric A and another VSAN Policy for Fabric B.\n')
            print(f'  IMPORTANT Note: The Fabric Interconnects will encapsulate Fibre-Channel traffic locally')
            print(f'                  in a FCoE (Fibre-Channel over Ethernet) VLAN.  This VLAN Must not be')
            print(f'                  already used by the VLAN Policy.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:

                    name = ezfunctions.naming_rule_fabric(loop_count, name_prefix, org)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)
                    polVars["auto_allow_on_uplinks"] = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Uplink Trunking: Default is No.')
                    print(f'     Most deployments do not enable Uplink Trunking for Fibre-Channel. ')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    
                    # Pull Information from the API
                    polVars["multi_select"] = False
                    jsonVars = jsonData['fabric.FcNetworkPolicy']['allOf'][1]['properties']

                    # Uplink Trunking
                    polVars["Description"] = jsonVars['EnableTrunking']['description']
                    polVars["varInput"] = f'Do you want to Enable Uplink Trunking for this VSAN Policy?'
                    polVars["varDefault"] = 'N'
                    polVars["varName"] = 'Enable Trunking'
                    polVars["uplink_trunking"] = ezfunctions.varBoolLoop(**polVars)

                    polVars["vsans"] = []
                    vsan_count = 0
                    vsan_loop = False
                    while vsan_loop == False:
                        valid = False
                        while valid == False:
                            if loop_count % 2 == 0:
                                vsan_id = input(f'Enter the VSAN id to add to {polVars["name"]}. [100]: ')
                            else:
                                vsan_id = input(f'Enter the VSAN id to add to {polVars["name"]}. [200]: ')
                            if loop_count % 2 == 0 and vsan_id == '':
                                vsan_id = 100
                            elif vsan_id == '':
                                vsan_id = 200
                            if re.search(r'[0-9]{1,4}', str(vsan_id)):
                                valid = validating.number_in_range('VSAN ID', vsan_id, 1, 4094)
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Invalid Entry!  Please Enter a VSAN ID in the range of 1-4094.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        valid = False
                        while valid == False:
                            fcoe_id = input(f'Enter the VLAN id for the FCOE VLAN to encapsulate "{vsan_id}" over Ethernet.  [{vsan_id}]: ')
                            if fcoe_id == '':
                                fcoe_id = vsan_id
                            if re.search(r'[0-9]{1,4}', str(fcoe_id)):
                                valid_vlan = validating.number_in_range('VSAN ID', fcoe_id, 1, 4094)
                                if valid_vlan == True:
                                    policy_list = [
                                        'policies.vlan_policies.vlan_policy',
                                    ]
                                    polVars["allow_opt_out"] = False
                                    for policy in policy_list:
                                        vlan_policy,policyData = policy_select_loop(jsonData, ezData, name_prefix, policy, **polVars)
                                    vlan_list = []
                                    for key, value in policyData['vlan_policies'].items():
                                            if key == vlan_policy:
                                                for k, v in value['vlans'].items():
                                                    for y, val in v.items():
                                                        if y == 'vlan_list':
                                                            vlan_list.append(val)

                                    vlan_list = ','.join(vlan_list)
                                    vlan_list = ezfunctions.vlan_list_full(vlan_list)
                                    overlap = False
                                    for vlan in vlan_list:
                                        if int(vlan) == int(fcoe_id):
                                            print(f'\n-------------------------------------------------------------------------------------------\n')
                                            print(f'  Error!!  The FCoE VLAN {fcoe_id} is already assigned to the VLAN Policy')
                                            print(f'  {vlan_policy}.  Please choose a VLAN id that is not already in use.')
                                            print(f'\n-------------------------------------------------------------------------------------------\n')
                                            overlap = True
                                            break
                                    if overlap == False:
                                        valid = True
                                else:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Invalid Entry!  Please Enter a valid VLAN ID in the range of 1-4094.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')

                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Invalid Entry!  Please Enter a valid VLAN ID in the range of 1-4094.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        jsonVars = jsonData['fabric.Vsan']['allOf'][1]['properties']

                        # VSAN Name
                        polVars["Description"] = jsonVars['Name']['description']
                        if loop_count % 2 == 0:
                            polVars["varDefault"] = 'VSAN-A'
                        else:
                            polVars["varDefault"] = 'VSAN-B'
                        polVars["varInput"] = f'What Name would you like to assign to "{vsan_id}"?  [{polVars["varDefault"]}]'
                        polVars["varName"] = 'VSAN Name'
                        polVars["varRegex"] = '.*'
                        polVars["minLength"] = 1
                        polVars["maxLength"] = 128
                        vsan_name = ezfunctions.varStringLoop(**polVars)

                        # Assign the VSAN Scope for this List
                        polVars["var_description"] = jsonVars['VsanScope']['description']
                        polVars["jsonVars"] = sorted(jsonVars['VsanScope']['enum'])
                        polVars["defaultVar"] = jsonVars['VsanScope']['default']
                        polVars["varType"] = 'Vsan Scope'
                        vsan_scope = ezfunctions.variablesFromAPI(**polVars)

                        vsan = {
                            'fcoe_vlan_id':fcoe_id,
                            'name':vsan_name,
                            'id':vsan_id,
                            'vsan_scope':vsan_scope
                        }
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'   fcoe_vlan_id = {fcoe_id}')
                        print(f'   name         = "{vsan_name}"')
                        print(f'   vsan_id      = {vsan_id}')
                        print(f'   vsan_scope   = "{vsan_scope}"')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            confirm_vsan = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                            if confirm_vsan == 'Y' or confirm_vsan == '':
                                polVars['vsans'].append(vsan)
                                valid_exit = False
                                while valid_exit == False:
                                    vsan_exit = input(f'Would You like to Configure another VSAN?  Enter "Y" or "N" [N]: ')
                                    if vsan_exit == 'Y':
                                        vsan_count += 1
                                        valid_confirm = True
                                        valid_exit = True
                                    elif vsan_exit == 'N' or vsan_exit == '':
                                        vsan_loop = True
                                        valid_confirm = True
                                        valid_exit = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')

                            elif confirm_vsan == 'N':
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Starting VSAN Configuration Over.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = True
                            else:
                                print(f'\n------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n------------------------------------------------------\n')

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description     = "{polVars["descr"]}"')
                    print(f'    name            = "{polVars["name"]}"')
                    print(f'    uplink_trunking = {polVars["uplink_trunking"]}')
                    print(f'    vsans           = [')
                    item_count = 1
                    for item in polVars["vsans"]:
                        print(f'      {item_count} = ''{')
                        print(f'        fcoe_vlan_id = {item["fcoe_vlan_id"]}')
                        print(f'        name         = "{item["name"]}"')
                        print(f'        vsan_id      = {item["vsan_id"]}')
                        print(f'        vsan_scope   = {item["vsan_scope"]}')
                        print('      }')
                        item_count += 1
                    print(f'    ]')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Add VSANs to VSAN Policy List
                            vsan_policies_vsans.append({polVars['name']:polVars["vsans"]})

                            configure_loop, loop_count, policy_loop = ezfunctions.exit_loop_default_yes(loop_count, policy_type)
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {policy_type} Section over.')
                            print(f'\n------------------------------------------------------\n')
                            valid_confirm = True

                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

def policy_select_loop(jsonData, ezData, name_prefix, policy, **polVars):
    loop_valid = False
    while loop_valid == False:
        create_policy = True
        inner_policy = policy.split('.')[1]
        inner_type = policy.split('.')[0]
        inner_var = policy.split('.')[2]
        polVars[inner_var] = ''
        polVars["policies"],policyData = ezfunctions.policies_parse(polVars["org"], inner_type, inner_policy)
        if not len(polVars["policies"]) > 0:
            valid = False
            while valid == False:

                x = inner_policy.split('_')
                ezfunctions.policy_description = []
                for y in x:
                    y = y.capitalize()
                    ezfunctions.policy_description.append(y)
                ezfunctions.policy_description = " ".join(ezfunctions.policy_description)
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There were no {ezfunctions.policy_description} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

                if 'Policies' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Policies', 'Policy')

                if polVars["allow_opt_out"] == True:
                    Question = input(f'Do you want to create a(n) {ezfunctions.policy_description}?  Enter "Y" or "N" [Y]: ')
                    if Question == '' or Question == 'Y':
                        create_policy = True
                        valid = True
                    elif Question == 'N':
                        create_policy = False
                        valid = True
                        return polVars[inner_var],policyData
                else:
                    create_policy = True
                    valid = True

        else:
            polVars[inner_var] = ezfunctions.choose_policy(inner_policy, **polVars)
            if polVars[inner_var] == 'create_policy':
                create_policy = True
            elif polVars[inner_var] == '' and polVars["allow_opt_out"] == True:
                loop_valid = True
                create_policy = False
                return polVars[inner_var],policyData
            elif not polVars[inner_var] == '':
                loop_valid = True
                create_policy = False
                return polVars[inner_var],policyData
        if create_policy == True:
            kwargs = {}
            opSystem = platform.system()
            if os.environ.get('TF_DEST_DIR') is None:
                tfDir = 'Intersight'
            else:
                tfDir = os.environ.get('TF_DEST_DIR')
            if tfDir[-1] == '\\' or tfDir[-1] == '/':
                    tfDir = tfDir[:-1]

            kwargs.update({'opSystem':opSystem,'tfDir':tfDir})

            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {inner_policy}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            if inner_policy == 'multicast_policies':
                policies(name_prefix, polVars["org"], inner_type).multicast_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'vlan_policies':
                policies(name_prefix, polVars["org"], inner_type).vlan_policies(jsonData, ezData, **kwargs)

