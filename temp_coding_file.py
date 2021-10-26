#!/usr/bin/env python3

import jinja2
import json
import os
import pkg_resources
import re
import stdiomask
import subprocess
import validating

ucs_template_path = pkg_resources.resource_filename('lib_ucs', 'ucs_templates/')

class easy_imm_wizard(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type


    #========================================
    # LAN Connectivity Policy Module
    #========================================
    def lan_connectivity_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = ['Management', 'Migration', 'Storage', 'Virtual_Machines']
        org = self.org
        policy_names = []
        policy_type = 'LAN Connectivity Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'lan_connectivity_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  A {policy_type} will configure vNIC adapters for Server Profiles.\n')
            print(f'  If failover is not configured the Wizard will create a Pair of vNICs.')
            print(f'  For Instance with a Virtual Host that may have the following vNIC Pairs:')
            print(f'     1. Management')
            print(f'     2. Migration/vMotion')
            print(f'     3. Storage')
            print(f'     4. Virtual Machines\n')
            print(f'  This wizard will save the configuraton for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['vnic.LanConnectivityPolicy']['allOf'][1]['properties']

                    templateVars["var_description"] = jsonVars['TargetPlatform']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    templateVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                    templateVars["varType"] = 'Target Platform'
                    templateVars["target_platform"] = variablesFromAPI(**templateVars)

                    if templateVars["target_platform"] == 'FIAttached':
                        templateVars["Description"] = jsonVars['AzureQosEnabled']['description']
                        templateVars["varInput"] = f'Do you want to Enable AzureStack-Host QoS?'
                        templateVars["varDefault"] = 'N'
                        templateVars["varName"] = 'AzureStack-Host QoS'
                        templateVars["enable_azure_stack_host_qos"] = varBoolLoop(**templateVars)

                        templateVars["var_description"] = jsonVars['IqnAllocationType']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['IqnAllocationType']['enum'])
                        templateVars["defaultVar"] = jsonVars['IqnAllocationType']['default']
                        templateVars["varType"] = 'Iqn Allocation Type'
                        templateVars["iqn_allocation_type"] = variablesFromAPI(**templateVars)

                        if templateVars["iqn_allocation_type"] == 'Pool':
                            templateVars["iqn_static_identifier"] = ''
                            policy_list = [
                                'pools.iqn_pools.iqn_pool',
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                policy_short = policy.split('.')[2]
                                templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                templateVars.update(policyData)

                        elif templateVars["iqn_allocation_type"] == 'Static':
                                templateVars["iqn_pool"] = ''
                                valid = False
                                while valid == False:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  User provided static iSCSI Qualified Name (IQN) for use as initiator identifiers by iSCSI')
                                    print(f'  vNICs.')
                                    print(f'  The iSCSI Qualified Name (IQN) format is: iqn.yyyy-mm.naming-authority:unique name, where:')
                                    print(f'    - literal iqn (iSCSI Qualified Name) - always iqn')
                                    print(f'    - date (yyyy-mm) that the naming authority took ownership of the domain')
                                    print(f'    - reversed domain name of the authority (e.g. org.linux, com.example, com.cisco)')
                                    print(f'    - unique name is any name you want to use, for example, the name of your host. The naming')
                                    print(f'      authority must make sure that any names assigned following the colon are unique, such as:')
                                    print(f'        * iqn.1984-12.com.cisco.iscsi:lnx1')
                                    print(f'        * iqn.1984-12.com.cisco.iscsi:win-server1')
                                    print(f'  Note: You can also obtain an IQN by going to any Linux system and typing in the command:')
                                    print(f'        - iscsi-iname')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    question = input(f'\nWould you Like the script to auto generate an IQN For you?  Enter "Y" or "N" [Y]: ')
                                    if question == '' or question == 'Y':
                                        p = subprocess.Popen(['iscsi-iname'],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT)
                                        for line in iter(p.stdout.readline, b''):
                                            line = line.decode("utf-8")
                                            line = line.strip()
                                            suffix = line.split(':')[1]
                                            templateVars["iqn_static_identifier"] = 'iqn.1984-12.com.cisco.iscsi:%s' % (suffix)
                                            print(f'IQN is {templateVars["iqn_static_identifier"]}')
                                        valid = True
                                    elif question == 'N':
                                        templateVars["Description"] = jsonVars['StaticIqnName']['description']
                                        templateVars["varDefault"] = ''
                                        templateVars["varInput"] = 'What is the Static IQN you would like to assign to this LAN Policy?'
                                        templateVars["varName"] = 'Static IQN'
                                        templateVars["varRegex"] = jsonVars['StaticIqnName']['pattern']
                                        templateVars["minLength"] = 4
                                        templateVars["maxLength"] = 128
                                        templateVars["iqn_static_identifier"] = varStringLoop(**templateVars)

                        templateVars["var_description"] = jsonVars['PlacementMode']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['PlacementMode']['enum'])
                        templateVars["defaultVar"] = jsonVars['PlacementMode']['default']
                        templateVars["varType"] = 'Placement Mode'
                        templateVars["vnic_placement_mode"] = variablesFromAPI(**templateVars)

                    else:
                        templateVars["iqn_allocation_type"] = 'None'

                    print(f'\n-----------------------------------------------------------------------------------------------\n')
                    print(f'  Easy IMM will now begin the vNIC Configuration Process.  We recommend the following guidlines:')
                    print(f'    - For Baremetal Operating Systems like Linux and Windows; use a Failover Policy with a single vnic')
                    print(f'    - For a Virtual Environment it is a Good Practice to not use Failover and use the following')
                    print(f'      vnic layout:')
                    print(f'      1. Management')
                    print(f'      2. Migration/vMotion')
                    print(f'      3. Storage')
                    print(f'      4. Virtual Machines')
                    print(f'  If you select no for Failover Policy the script will create mirroring vnics for A and B')
                    print(f'\n-----------------------------------------------------------------------------------------------\n')
                    inner_loop_count = 1
                    pci_order_consumed = [{0:[]},{1:[]}]
                    templateVars["vnics"] = []
                    vnic_loop = False
                    while vnic_loop == False:
                        jsonVars = jsonData['components']['schemas']['vnic.EthIf']['allOf'][1]['properties']

                        templateVars["Description"] = jsonVars['FailoverEnabled']['description']
                        templateVars["varInput"] = f'Do you want to Enable Failover for this vNIC?'
                        templateVars["varDefault"] = 'Y'
                        templateVars["varName"] = 'Enable Failover'
                        templateVars["enable_failover"] = varBoolLoop(**templateVars)

                        if templateVars["enable_failover"] == True:
                            fabrics = ['A']
                            templateVars["varDefault"] = 'vnic'
                        else:
                            fabrics = ['A','B']
                            if inner_loop_count < 4:
                                templateVars["varDefault"] = name_suffix[inner_loop_count]
                            else:
                                templateVars["varDefault"] = 'vnic'
                        templateVars["Description"] = jsonVars['Name']['description']
                        templateVars["varInput"] = 'What is the name for this vNIC?'
                        templateVars["varName"] = 'vNIC Name'
                        templateVars["varRegex"] = jsonVars['Name']['pattern']
                        templateVars["minLength"] = 1
                        templateVars["maxLength"] = jsonVars['Name']['maxLength']
                        Name = varStringLoop(**templateVars)
                        for x in fabrics:
                            templateVars[f"name_{x}"] = '%s-%s' % (Name, x)

                        if templateVars["target_platform"] == 'FIAttached':
                            templateVars["var_description"] = jsonVars['MacAddressType']['description']
                            templateVars["jsonVars"] = sorted(jsonVars['MacAddressType']['enum'])
                            templateVars["defaultVar"] = jsonVars['MacAddressType']['default']
                            templateVars["varType"] = 'Mac Address Type'
                            MacAddressType = variablesFromAPI(**templateVars)

                            if MacAddressType == 'POOL':
                                for x in fabrics:
                                    policy_list = [
                                        'pools.mac_pools.mac_pool',
                                    ]
                                    templateVars["allow_opt_out"] = False
                                    for policy in policy_list:
                                        templateVars[f"StaticMac_{x}"] = ''
                                        if templateVars["enable_failover"] == False:
                                            templateVars["optional_message"] = f'MAC Address Pool for Fabric {x}'
                                        policy_short = policy.split('.')[2]
                                        templateVars[f'mac_pool_{x}'],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                        templateVars.update(policyData)
                                    templateVars.pop('optional_message')
                            else:
                                for x in fabrics:
                                    templateVars[f'macPool_{x}'] = ''
                                    templateVars["Description"] = jsonVars['StaticMacAddress']['description']
                                    if templateVars["enable_failover"] == True:
                                        templateVars["varInput"] = f'What is the static MAC Address?'
                                    else:
                                        templateVars["varInput"] = f'What is the static MAC Address for Fabric {x}?'
                                    if templateVars["enable_failover"] == True:
                                        templateVars["varName"] = f'Static Mac Address'
                                    else:
                                        templateVars["varName"] = f'Fabric {x} Mac Address'
                                    templateVars["varRegex"] = jsonData['components']['schemas']['boot.Pxe']['allOf'][1]['properties']['MacAddress']['pattern']
                                    templateVars["minLength"] = 17
                                    templateVars["maxLength"] = 17
                                    templateVars[f"StaticMac_{x}"] = varStringLoop(**templateVars)

                        # Pull in API Attributes
                        jsonVars = jsonData['components']['schemas']['vnic.PlacementSettings']['allOf'][1]['properties']

                        for x in fabrics:
                            templateVars["var_description"] = jsonVars['PciLink']['description']
                            if templateVars["enable_failover"] == False:
                                templateVars["var_description"] = templateVars["var_description"] + f'\nPCI Link For Fabric {x}'
                            templateVars["jsonVars"] = [0, 1]
                            templateVars["defaultVar"] = jsonVars['PciLink']['default']
                            if templateVars["enable_failover"] == True:
                                templateVars["varType"] = 'PCI Link'
                            else:
                                templateVars["varType"] = 'Fabric {x} PCI Link'
                            templateVars[f"pci_link_{x}"] = variablesFromAPI(**templateVars)

                            if templateVars["target_platform"] == 'Standalone':
                                templateVars["var_description"] = jsonVars['Uplink']['description']
                                templateVars["jsonVars"] = [0, 1, 2, 3]
                                templateVars["defaultVar"] = 0
                                templateVars["varType"] = 'Mac Address Type'
                                templateVars[f"uplink_port_{x}"] = variablesFromAPI(**templateVars)

                        templateVars["var_description"] = jsonVars['Id']['description']
                        templateVars["jsonVars"] = easy_jsonData['policies']['vnic.PlacementSettings']['enum']
                        templateVars["defaultVar"] = easy_jsonData['policies']['vnic.PlacementSettings']['default']
                        templateVars["varType"] = 'Slot ID'
                        templateVars[f"slot_id"] = variablesFromAPI(**templateVars)

                        # Pull in API Attributes
                        jsonVars = jsonData['components']['schemas']['vnic.EthIf']['allOf'][1]['properties']

                        for x in fabrics:
                            valid = False
                            while valid == False:
                                templateVars["Description"] = jsonVars['Order']['description']
                                if templateVars["enable_failover"] == False:
                                    templateVars["varInput"] = f'\nPCI Order For Fabric {x}.'
                                else:
                                    templateVars["varInput"] = f'\nPCI Order.'
                                if len(pci_order_consumed[0][f"pci_link_{x}"]) > 0:
                                    templateVars["varDefault"] = len(pci_order_consumed[0][f"pci_link_{x}"]) - 1
                                else:
                                    templateVars["varDefault"] = 0
                                templateVars["varName"] = 'PCI Order'
                                templateVars["minNum"] = 0
                                templateVars["maxNum"] = 255
                                templateVars[f"pci_order_{x}"] = varNumberLoop(**templateVars)

                                consumed_count = 0
                                for i in pci_order_consumed[0][f"pci_link_{x}"]:
                                    if int(i) == int(templateVars[f"PciOrder_{x}"]):
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! PCI Order "{templateVars[f"PciOrder_{x}"]}" is already in use.  Please use an alternative.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        consumed_count += 1

                                if consumed_count == 0:
                                    pci_order_consumed[0][f"pci_link_{x}"].append(templateVars[f"PciOrder_{x}"])
                                    valid = True

                        # Pull in API Attributes
                        jsonVars = jsonData['components']['schemas']['vnic.Cdn']['allOf'][1]['properties']

                        templateVars["var_description"] = jsonVars['Source']['description']
                        templateVars["jsonVars"] = jsonVars['Source']['enum']
                        templateVars["defaultVar"] = jsonVars['Source']['default']
                        templateVars["varType"] = 'CDN Source'
                        templateVars["cdn_source"] = variablesFromAPI(**templateVars)

                        if templateVars["cdn_source"] == 'user':
                            for x in fabrics:
                                templateVars["Description"] = jsonVars['Value']['description']
                                if templateVars["enable_failover"] == True:
                                    templateVars["varInput"] = 'What is the value for the Consistent Device Name?'
                                else:
                                    templateVars["varInput"] = 'What is the value for Fabric {x} Consistent Device Name?'
                                templateVars["varName"] = 'CDN Name'
                                templateVars["varRegex"] = jsonVars['Value']['pattern']
                                templateVars["minLength"] = 1
                                templateVars["maxLength"] = jsonVars['Value']['maxLength']
                                templateVars[f"cdn_value_{x}"] = varStringLoop(**templateVars)
                        else:
                            for x in fabrics:
                                templateVars[f"cdn_value_{x}"] = ''

                        policy_list = [
                            'policies.ethernet_adapter_policies.ethernet_adapter_policy',
                        ]
                        if templateVars["target_platform"] == 'Standalone':
                            policy_list.append('policies.ethernet_network_policies.ethernet_network_policy')
                        else:
                            policy_list.append('policies.ethernet_network_control_policies.ethernet_network_control_policy')
                            policy_list.append('policies.ethernet_network_group_policies.ethernet_network_group_policy')
                        policy_list.append('policies.ethernet_qos_policies.ethernet_qos_policy')
                        templateVars["allow_opt_out"] = False
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                            templateVars.update(policyData)
                        if not templateVars["iqn_allocation_type"] == 'None':
                            policy_list [
                                'policies.iscsi_boot_policies.iscsi_boot_policy'
                            ]
                            for x in fabrics:
                                if templateVars["enable_failover"] == False:
                                    templateVars["optional_message"] = f'iSCSI Boot Policy for Fabric {x}'
                                policy_short = policy.split('.')[2]
                                templateVars[f"{policy_short}_{x}"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                templateVars.update(policyData)
                            else:
                                templateVars[f'iscsi_boot_policy_{x}'] = ''



                        for x in fabrics:
                            templateVars[f"vnic_fabric_{x}"] = {
                                'cdn_source':templateVars["cdn_source"],
                            }
                            if not templateVars[f"cdn_value_{x}"] == '':
                                templateVars[f"vnic_fabric_{x}"].update({'cdn_value':templateVars[f"cdn_value_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'enable_failover':templateVars["enable_failover"]})
                            templateVars[f"vnic_fabric_{x}"].update({'ethernet_adapter_policy':templateVars["ethernet_adapter_policy"]})
                            if templateVars["target_platform"] == 'Standalone':
                                templateVars[f"vnic_fabric_{x}"].update({'ethernet_network_policy':templateVars["ethernet_network_policy"]})
                            else:
                                templateVars[f"vnic_fabric_{x}"].update({'ethernet_network_control_policy':templateVars["ethernet_network_control_policy"]})
                                templateVars[f"vnic_fabric_{x}"].update({'ethernet_network_group_policy':templateVars["ethernet_network_group_policy"]})
                            templateVars[f"vnic_fabric_{x}"].update({'ethernet_qos_policy':templateVars["ethernet_qos_policy"]})
                            if not templateVars["iqn_allocation_type"] == 'None':
                                templateVars[f"vnic_fabric_{x}"].update({'iscsi_boot_policy':templateVars[f"iscsi_boot_policy_{x}"]})
                            if templateVars["target_platform"] == 'FIAttached':
                                templateVars[f"vnic_fabric_{x}"].update({'mac_address_allocation_type':templateVars[f"mac_address_allocation_type"]})
                                if templateVars["mac_address_allocation_type"] == 'POOL':
                                    templateVars[f"vnic_fabric_{x}"].update({'mac_address_pool':templateVars[f"macPool_{x}"]})
                                else:
                                    templateVars[f"vnic_fabric_{x}"].update({'mac_address_static':templateVars[f"StaticMac_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'name':templateVars[f"name_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'pci_link':templateVars[f"pci_link_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'pci_order':templateVars[f"pci_order_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'slot_id':templateVars[f"slot_id"]})
                            if templateVars["target_platform"] == 'FIAttached':
                                templateVars[f"vnic_fabric_{x}"].update({'switch_id':templateVars[f"{x}"]})
                            else:
                                templateVars[f"vnic_fabric_{x}"].update({'uplink_port':templateVars[f"uplink_port_{x}"]})

                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        for x in fabrics:
                            if templateVars["enable_failover"] == False:
                                print(f'Fabric {x}:')
                            for k, v in [f'vnic_fabric_{x}'].items():
                                if k == 'cdn_source':
                                    print(f'    cdn_source                      = "{v}"')
                                elif k == 'cdn_value':
                                    print(f'    cdn_value                       = "{v}"')
                                elif k == 'enable_failover':
                                    print(f'    enable_failover                 = "{v}"')
                                elif k == 'ethernet_adapter_policy':
                                    print(f'    ethernet_adapter_policy         = "{v}"')
                                elif k == 'ethernet_network_control_policy':
                                    print(f'    ethernet_network_control_policy = "{v}"')
                                elif k == 'ethernet_network_group_policy':
                                    print(f'    ethernet_network_group_policy   = "{v}"')
                                elif k == 'ethernet_network_policy':
                                    print(f'    ethernet_network_policy         = "{v}"')
                                elif k == 'iscsi_boot_policy':
                                    print(f'    iscsi_boot_policy               = "{v}"')
                                elif k == 'mac_address_allocation_type':
                                    print(f'    mac_address_allocation_type     = "{v}"')
                                elif k == 'mac_address_pool':
                                    print(f'    mac_address_pool                = "{v}"')
                                elif k == 'mac_address_static':
                                    print(f'    mac_address_static              = "{v}"')
                                elif k == 'name':
                                    print(f'    name                            = "{v}"')
                                elif k == 'pci_link':
                                    print(f'    placement_pci_link              = {v}')
                                elif k == 'pci_order':
                                    print(f'    placement_pci_order             = {v}')
                                elif k == 'slot_id':
                                    print(f'    placement_slot_id               = "{v}"')
                                elif k == 'switch_id':
                                    print(f'    placement_switch_id             = "{v}"')
                                elif k == 'uplink_port':
                                    print(f'    placement_uplink_port           = {v}')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                            if confirm_v == 'Y' or confirm_v == '':
                                for x in fabrics:
                                    templateVars["vnics"].append(templateVars[f"vnic_fabric_{x}"])
                                valid_exit = False
                                while valid_exit == False:
                                    loop_exit = input(f'Would You like to Configure another vNIC?  Enter "Y" or "N" [N]: ')
                                    if loop_exit == 'Y':
                                        inner_loop_count += 1
                                        valid_confirm = True
                                        valid_exit = True
                                    elif loop_exit == 'N' or loop_exit == '':
                                        vnic_loop = True
                                        valid_confirm = True
                                        valid_exit = True
                                    else:
                                        print(f'\n------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                        print(f'\n------------------------------------------------------\n')

                            elif confirm_v == 'N':
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Starting Remote Host Configuration Over.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                valid_confirm = True
                            else:
                                print(f'\n------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n------------------------------------------------------\n')


                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    # if templateVars["target_platform"] == 'FIAttached':
                    print(f'    description                 = {templateVars["descr"]}')
                    print(f'    enable_azure_stack_host_qos = "{templateVars["enable_azure_stack_host_qos"]}"')
                    # if not templateVars["iqn_allocation_type"] == 'None':
                    print(f'    iqn_allocation_type         = "{templateVars["iqn_allocation_type"]}"')
                    # if templateVars["iqn_allocation_type"] == 'Pool':
                    print(f'    iqn_pool                    = "{templateVars["iqn_pool"]}"')
                    # if templateVars["iqn_allocation_type"] == 'Static':
                    print(f'    iqn_static_identifier       = "{templateVars["iqn_static_identifier"]}"')
                    print(f'    name                        = "{templateVars["name"]}"')
                    print(f'    target_platform             = "{templateVars["target_platform"]}"')
                    print(f'    vnic_placement_mode         = "{templateVars["vnic_placement_mode"]}"')
                    if len(templateVars["vnics"]) > 0:
                        print(f'    vnics = ''{')
                        for item in templateVars["vnics"]:
                            for k, v in item.items():
                                if k == 'name':
                                    print(f'      "{v}" = ''{')
                            for k, v in item.items():
                                if k == 'cdn_source':
                                    print(f'        cdn_source                      = "{v}"')
                                elif k == 'cdn_value':
                                    print(f'        cdn_value                       = "{v}"')
                                elif k == 'enable_failover':
                                    print(f'        enable_failover                 = "{v}"')
                                elif k == 'ethernet_adapter_policy':
                                    print(f'        ethernet_adapter_policy         = "{v}"')
                                elif k == 'ethernet_network_control_policy':
                                    print(f'        ethernet_network_control_policy = "{v}"')
                                elif k == 'ethernet_network_group_policy':
                                    print(f'        ethernet_network_group_policy   = "{v}"')
                                elif k == 'ethernet_network_policy':
                                    print(f'        ethernet_network_policy         = "{v}"')
                                elif k == 'iscsi_boot_policy':
                                    print(f'        iscsi_boot_policy               = "{v}"')
                                elif k == 'mac_address_allocation_type':
                                    print(f'        mac_address_allocation_type     = "{v}"')
                                elif k == 'mac_address_pool':
                                    print(f'        mac_address_pool                = "{v}"')
                                elif k == 'mac_address_static':
                                    print(f'        mac_address_static              = "{v}"')
                                elif k == 'name':
                                    print(f'        name                            = "{v}"')
                                elif k == 'pci_link':
                                    print(f'        placement_pci_link              = {v}')
                                elif k == 'pci_order':
                                    print(f'        placement_pci_order             = {v}')
                                elif k == 'slot_id':
                                    print(f'        placement_slot_id               = "{v}"')
                                elif k == 'switch_id':
                                    print(f'        placement_switch_id             = "{v}"')
                                elif k == 'uplink_port':
                                    print(f'        placement_uplink_port           = {v}')
                            print(f'      ''}')
                        print(f'    ''}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            # Add Template Name to Policies Output
                            policy_names.append(templateVars["name"])

                            configure_loop, policy_loop = exit_default_no(templateVars["policy_type"])
                            valid_confirm = True

                        elif confirm_policy == 'N':
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Starting {templateVars["policy_type"]} Section over.')
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
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)


def choose_policy(policy, **templateVars):

    if 'policies' in policy:
        policy_short = policy.replace('policies', 'policy')
    elif 'pools' in policy:
        policy_short = policy.replace('pools', 'pool')
    x = policy_short.split('_')
    policy_description = []
    for y in x:
        y = y.capitalize()
        policy_description.append(y)
    policy_description = " ".join(policy_description)
    policy_description = policy_description.replace('Ip', 'IP')
    policy_description = policy_description.replace('Ntp', 'NTP')
    policy_description = policy_description.replace('Snmp', 'SNMP')
    policy_description = policy_description.replace('Wwnn', 'WWNN')
    policy_description = policy_description.replace('Wwpn', 'WWPN')

    if len(policy) > 0:
        templateVars["policy"] = policy_description
        policy_short = policies_list(templateVars["policies"], **templateVars)
    else:
        policy_short = ""
    return policy_short

def exit_default_no(policy_type):
    valid_exit = False
    while valid_exit == False:
        exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
        if exit_answer == '' or exit_answer == 'N':
            policy_loop = True
            configure_loop = True
            valid_exit = True
        elif exit_answer == 'Y':
            policy_loop = False
            configure_loop = False
            valid_exit = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')
    return configure_loop, policy_loop

def exit_default_yes(policy_type):
    valid_exit = False
    while valid_exit == False:
        exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [Y]: ')
        if exit_answer == '' or exit_answer == 'Y':
            policy_loop = False
            configure_loop = False
            valid_exit = True
        elif exit_answer == 'N':
            policy_loop = True
            configure_loop = True
            valid_exit = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')
    return configure_loop, policy_loop

def exit_loop_default_yes(loop_count, policy_type):
    valid_exit = False
    while valid_exit == False:
        if loop_count % 2 == 0:
            exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [Y]: ')
        else:
            exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
        if (loop_count % 2 == 0 and exit_answer == '') or exit_answer == 'Y':
            policy_loop = False
            configure_loop = False
            loop_count += 1
            valid_exit = True
        elif not loop_count % 2 == 0 and exit_answer == '':
            policy_loop = True
            configure_loop = True
            valid_exit = True
        elif exit_answer == 'N':
            policy_loop = True
            configure_loop = True
            valid_exit = True
        else:
            print(f'\n------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n------------------------------------------------------\n')
    return configure_loop, loop_count, policy_loop

def naming_rule(name_prefix, name_suffix, org):
    if not name_prefix == '':
        name = '%s_%s' % (name_prefix, name_suffix)
    else:
        name = '%s_%s' % (org, name_suffix)
    return name

def naming_rule_fabric(loop_count, name_prefix, org):
    if loop_count % 2 == 0:
        if not name_prefix == '':
            name = '%s_A' % (name_prefix)
        elif not org == 'default':
            name = '%s_A' % (org)
        else:
            name = 'Fabric_A'
    else:
        if not name_prefix == '':
            name = '%s_B' % (name_prefix)
        elif not org == 'default':
            name = '%s_B' % (org)
        else:
            name = 'Fabric_B'
    return name

def policies_list(policies_list, **templateVars):
    valid = False
    while valid == False:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  {templateVars["policy"]} Options:')
        for i, v in enumerate(policies_list):
            i += 1
            if i < 10:
                print(f'     {i}. {v}')
            else:
                print(f'    {i}. {v}')
        if templateVars["allow_opt_out"] == True:
            print(f'     99. Do not assign a(n) {templateVars["policy"]}.')
        print(f'     100. Create a New {templateVars["policy"]}.')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        policy_temp = input(f'Select the Option Number for the {templateVars["policy"]} to Assign to {templateVars["name"]}: ')
        for i, v in enumerate(policies_list):
            i += 1
            if int(policy_temp) == i:
                policy = v
                valid = True
                return policy
            elif int(policy_temp) == 99:
                policy = ''
                valid = True
                return policy
            elif int(policy_temp) == 100:
                policy = 'create_policy'
                valid = True
                return policy

        if policy_temp == '':
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! Invalid Selection.  Please Select a valid Index from the List.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
        elif int(policy_temp) == 99:
            policy = ''
            valid = True
            return policy
        elif int(policy_temp) == 100:
            policy = 'create_policy'
            valid = True
            return policy

def policies_parse(org, policy_type, policy):
    policies = []
    policy_file = './Intersight/%s/%s/%s.auto.tfvars' % (org, policy_type, policy)
    if os.path.isfile(policy_file):
        if len(policy_file) > 0:
            cmd = 'json2hcl -reverse < %s' % (policy_file)
            p = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            if 'unable to parse' in p.stdout.decode('utf-8'):
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  !!!! Encountered Error in Attempting to read file !!!!')
                print(f'  - {policy_file}')
                print(f'  Error was:')
                print(f'  - {p.stdout.decode("utf-8")}')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                jsonData = {}
                return policies,jsonData
            else:
                jsonData = json.loads(p.stdout.decode('utf-8'))
                for i in jsonData[policy]:
                    for k, v in i.items():
                        policies.append(k)
                return policies,jsonData
    else:
        jsonData = {}
        return policies,jsonData

def policy_loop_standard(self, header, initial_policy, template_type):
    # Set the org_count to 0 for the First Organization
    org_count = 0

    # Loop through the orgs discovered by the Class
    for org in self.orgs:

        # Pull in Variables from Class
        templateVars = self.templateVars
        templateVars["org"] = org

        # Define the Template Source
        templateVars["header"] = header
        templateVars["template_type"] = template_type
        template_file = "template_open.jinja2"
        template = self.templateEnv.get_template(template_file)


        # Process the template
        dest_dir = '%s' % (self.type)
        dest_file = '%s.auto.tfvars' % (template_type)
        if initial_policy == True:
            write_method = 'w'
        else:
            write_method = 'a'
        process_method(write_method, dest_dir, dest_file, template, **templateVars)

        # Define the Template Source
        template_file = '%s.jinja2' % (template_type)
        template = self.templateEnv.get_template(template_file)

        if template_type in self.json_data["config"]["orgs"][org_count]:
            for item in self.json_data["config"]["orgs"][org_count][template_type]:
                # Reset TemplateVars to Default for each Loop
                templateVars = {}
                templateVars["org"] = org

                # Define the Template Source
                templateVars["header"] = header

                # Loop Through Json Items to Create templateVars Blocks
                for k, v in item.items():
                    templateVars[k] = v

                # if template_type == 'iscsi_boot_policies':
                #     print(templateVars)
                # Process the template
                dest_dir = '%s' % (self.type)
                dest_file = '%s.auto.tfvars' % (template_type)
                process_method('a', dest_dir, dest_file, template, **templateVars)

        # Define the Template Source
        template_file = "template_close.jinja2"
        template = self.templateEnv.get_template(template_file)

        # Process the template
        dest_dir = '%s' % (self.type)
        dest_file = '%s.auto.tfvars' % (template_type)
        process_method('a', dest_dir, dest_file, template, **templateVars)

        # Increment the org_count for the next Organization Loop
        org_count += 1

def policy_select_loop(name_prefix, policy, **templateVars):
    valid = False
    while valid == False:
        create_policy = True
        inner_policy = policy.split('.')[1]
        inner_type = policy.split('.')[0]
        inner_var = policy.split('.')[2]
        templateVars[inner_var] = ''
        templateVars["policies"],policyData = policies_parse(templateVars["org"], inner_type, inner_policy)
        if not len(templateVars['policies']) > 0:
            create_policy = True
        else:
            templateVars[inner_var] = choose_policy(inner_policy, **templateVars)
        if templateVars[inner_var] == 'create_policy':
            create_policy = True
        elif templateVars[inner_var] == '' and templateVars["allow_opt_out"] == True:
            valid = True
            create_policy = False
            return templateVars[inner_var],policyData
        elif not templateVars[inner_var] == '':
            valid = True
            create_policy = False
            return templateVars[inner_var],policyData
        if create_policy == True:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {inner_policy}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            if inner_policy == 'ip_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ip_pools()
            elif inner_policy == 'iqn_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).iqn_pools()
            elif inner_policy == 'mac_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).mac_pools()
            elif inner_policy == 'uuid_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).uuid_pools()
            elif inner_policy == 'wwnn_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).wwnn_pools()
            elif inner_policy == 'wwpn_pools':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).wwpn_pools()
            elif inner_policy == 'adapter_configuration_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).adapter_configuration_policies()
            elif inner_policy == 'bios_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).bios_policies()
            elif inner_policy == 'boot_order_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).boot_order_policies()
            elif inner_policy == 'certificate_management_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).certificate_management_policies()
            elif inner_policy == 'device_connector_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).device_connector_policies()
            elif inner_policy == 'ethernet_adapter_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ethernet_adapter_policies()
            elif inner_policy == 'ethernet_network_control_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ethernet_network_control_policies()
            elif inner_policy == 'ethernet_network_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ethernet_network_policies()
            elif inner_policy == 'ethernet_qos_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ethernet_qos_policies()
            elif inner_policy == 'fibre_channel_adapter_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).fibre_channel_adapter_policies()
            elif inner_policy == 'fibre_channel_network_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).fibre_channel_network_policies()
            elif inner_policy == 'fibre_channel_qos_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).fibre_channel_qos_policies()
            elif inner_policy == 'flow_control_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).flow_control_policies()
            elif inner_policy == 'imc_access_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).imc_access_policies()
            elif inner_policy == 'ipmi_over_lan_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ipmi_over_lan_policies()
            elif inner_policy == 'iscsi_adapter_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).iscsi_adapter_policies()
            elif inner_policy == 'iscsi_boot_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).iscsi_boot_policies()
            elif inner_policy == 'iscsi_static_target_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).iscsi_static_target_policies()
            elif inner_policy == 'lan_connectivity_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).lan_connectivity_policies()
            elif inner_policy == 'ldap_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ldap_policies()
            elif inner_policy == 'link_aggregation_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).link_aggregation_policies()
            elif inner_policy == 'link_control_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).link_control_policies()
            elif inner_policy == 'local_user_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).local_user_policies()
            elif inner_policy == 'multicast_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).multicast_policies()
            elif inner_policy == 'network_connectivity_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).network_connectivity_policies()
            elif inner_policy == 'ntp_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ntp_policies()
            elif inner_policy == 'persistent_memory_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).persistent_memory_policies()
            elif inner_policy == 'port_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).port_policies()
            elif inner_policy == 'san_connectivity_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).san_connectivity_policies()
            elif inner_policy == 'sd_card_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).sd_card_policies()
            elif inner_policy == 'serial_over_lan_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).serial_over_lan_policies()
            elif inner_policy == 'smtp_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).smtp_policies()
            elif inner_policy == 'snmp_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).snmp_policies()
            elif inner_policy == 'ssh_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).ssh_policies()
            elif inner_policy == 'storage_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).storage_policies()
            elif inner_policy == 'switch_control_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).switch_control_policies()
            elif inner_policy == 'syslog_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).syslog_policies()
            elif inner_policy == 'system_qos_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).system_qos_policies()
            elif inner_policy == 'thermal_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).thermal_policies()
            elif inner_policy == 'virtual_kvm_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).virtual_kvm_policies()
            elif inner_policy == 'virtual_media_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).virtual_media_policies()
            elif inner_policy == 'vlan_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).vlan_policies()
            elif inner_policy == 'vsan_policies':
                easy_imm_wizard(name_prefix, templateVars["org"], inner_type).vsan_policies()

def policy_descr(name, policy_type):
    valid = False
    while valid == False:
        descr = input(f'What is the Description for the {policy_type}?  [{name} {policy_type}]: ')
        if descr == '':
            descr = '%s %s' % (name, policy_type)
        valid = validating.description(f'{policy_type} Description', descr, 1, 62)
        if valid == True:
            return descr

def policy_name(namex, policy_type):
    valid = False
    while valid == False:
        name = input(f'What is the Name for the {policy_type}?  [{namex}]: ')
        if name == '':
            name = '%s' % (namex)
        valid = validating.name_rule(f'{policy_type} Name', name, 1, 62)
        if valid == True:
            return name

def policy_template(self, **templateVars):
    configure_loop = False
    while configure_loop == False:
        policy_loop = False
        while policy_loop == False:

            valid = False
            while valid == False:
                policy_file = 'ucs_templates/variables/%s' % (templateVars["policy_file"])
                if os.path.isfile(policy_file):
                    template_file = open(policy_file, 'r')
                    template_file.seek(0)
                    policy_templates = []
                    for line in template_file:
                        line = line.strip()
                        policy_templates.append(line)
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  {templateVars["policy_type"]} Templates:')
                    for i, v in enumerate(policy_templates):
                        i += 1
                        if i < 10:
                            print(f'     {i}. {v}')
                        else:
                            print(f'    {i}. {v}')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                policy_temp = input(f'Enter the Index Number for the {templateVars["policy_type"]} Template to Create: ')
                for i, v in enumerate(policy_templates):
                    i += 1
                    if int(policy_temp) == i:
                        templateVars["policy_template"] = v
                        valid = True
                if valid == False:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Selection.  Please Select a valid Index from the List.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                template_file.close()

            if not templateVars["name_prefix"] == '':
                name = '%s_%s' % (templateVars["name_prefix"], templateVars["policy_template"])
            else:
                name = '%s_%s' % (templateVars["org"], templateVars["policy_template"])

            templateVars["name"] = policy_name(name, templateVars["policy_type"])
            templateVars["descr"] = policy_descr(templateVars["name"], templateVars["policy_type"])

            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Do you want to accept the following configuration?')
            if templateVars["template_type"] == 'bios_policies':
                print(f'   bios_template = "{templateVars["policy_template"]}"')
                print(f'   description   = "{templateVars["descr"]}"')
                print(f'   name          = "{templateVars["name"]}"')
            else:
                print(f'   adapter_template = "{templateVars["policy_template"]}"')
                print(f'   description      = "{templateVars["descr"]}"')
                print(f'   name             = "{templateVars["name"]}"')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            valid_confirm = False
            while valid_confirm == False:
                confirm_policy = input('Enter "Y" or "N" [Y]: ')
                if confirm_policy == 'Y' or confirm_policy == '':
                    confirm_policy = 'Y'

                    # Write Policies to Template File
                    write_to_template(self, **templateVars)

                    configure_loop, policy_loop = exit_default_yes(templateVars["policy_type"])
                    valid_confirm = True

                elif confirm_policy == 'N':
                    print(f'\n------------------------------------------------------\n')
                    print(f'  Starting {templateVars["policy_type"]} Section over.')
                    print(f'\n------------------------------------------------------\n')
                    valid_confirm = True

                else:
                    print(f'\n------------------------------------------------------\n')
                    print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                    print(f'\n------------------------------------------------------\n')

def vars_from_list(var_options, **templateVars):
    selection = []
    selection_count = 0
    valid = False
    while valid == False:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'{templateVars["var_description"]}')
        for index, value in enumerate(var_options):
            index += 1
            if index < 10:
                print(f'     {index}. {value}')
            else:
                print(f'    {index}. {value}')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        exit_answer = False
        while exit_answer == False:
            var_selection = input(f'Please Enter the Option Number to Select for {templateVars["var_type"]}: ')
            if not var_selection == '':
                if re.search(r'[0-9]+', str(var_selection)):
                    xcount = 1
                    for index, value in enumerate(var_options):
                        index += 1
                        if int(var_selection) == index:
                            selection.append(value)
                            xcount = 0
                    if xcount == 0:
                        if selection_count % 2 == 0 and templateVars["multi_select"] == True:
                            answer_finished = input(f'Would you like to add another port to the {templateVars["port_type"]}?  Enter "Y" or "N" [Y]: ')
                        elif templateVars["multi_select"] == True:
                            answer_finished = input(f'Would you like to add another port to the {templateVars["port_type"]}?  Enter "Y" or "N" [N]: ')
                        elif templateVars["multi_select"] == False:
                            answer_finished = 'N'
                        if (selection_count % 2 == 0 and answer_finished == '') or answer_finished == 'Y':
                            exit_answer = True
                            selection_count += 1
                        elif answer_finished == '' or answer_finished == 'N':
                            exit_answer = True
                            valid = True
                        elif templateVars["multi_select"] == False:
                            exit_answer = True
                            valid = True
                        else:
                            print(f'\n------------------------------------------------------\n')
                            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                            print(f'\n------------------------------------------------------\n')
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Selection.  Please select a valid option from the List.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Selection.  Please Select a valid Option from the List.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Selection.  Please Select a valid Option from the List.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
    return selection

def process_method(wr_method, dest_dir, dest_file, template, **templateVars):
    dest_dir = './Intersight/%s/%s' % (templateVars["org"], dest_dir)
    if not os.path.isdir(dest_dir):
        mk_dir = 'mkdir -p %s' % (dest_dir)
        os.system(mk_dir)
    dest_file_path = '%s/%s' % (dest_dir, dest_file)
    if not os.path.isfile(dest_file_path):
        create_file = 'touch %s' % (dest_file_path)
        os.system(create_file)
    tf_file = dest_file_path
    wr_file = open(tf_file, wr_method)

    # Render Payload and Write to File
    payload = template.render(templateVars)
    wr_file.write(payload)
    wr_file.close()

def variablesFromAPI(**templateVars):
    valid = False
    while valid == False:
        json_vars = templateVars["jsonVars"]
        if 'popList' in templateVars:
            if len(templateVars["popList"]) > 0:
                for x in templateVars["popList"]:
                    varsCount = len(json_vars)
                    for r in range(0, varsCount):
                        if json_vars[r] == x:
                            json_vars.pop(r)
                            break
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'{templateVars["var_description"]}')
        print(f'\n    Select an Option Below:')
        for index, value in enumerate(json_vars):
            index += 1
            if value == templateVars["defaultVar"]:
                defaultIndex = index
            if index < 10:
                print(f'     {index}. {value}')
            else:
                print(f'    {index}. {value}')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        if templateVars["multi_select"] == True:
            if not templateVars["defaultVar"] == '':
                var_selection = input(f'Please Enter the Option Number(s) to Select for {templateVars["varType"]}.  [{defaultIndex}]: ')
            else:
                var_selection = input(f'Please Enter the Option Number(s) to Select for {templateVars["varType"]}: ')
        else:
            if not templateVars["defaultVar"] == '':
                var_selection = input(f'Please Enter the Option Number to Select for {templateVars["varType"]}.  [{defaultIndex}]: ')
            else:
                var_selection = input(f'Please Enter the Option Number to Select for {templateVars["varType"]}: ')
        if var_selection == '':
            var_selection = defaultIndex
        if templateVars["multi_select"] == False and re.search(r'^[0-9]+$', str(var_selection)):
            for index, value in enumerate(json_vars):
                index += 1
                if int(var_selection) == index:
                    selection = value
                    valid = True
        elif templateVars["multi_select"] == True and re.search(r'(^[0-9]+$|^[0-9\-,]+[0-9]$)', str(var_selection)):
            var_list = vlan_list_full(var_selection)
            var_length = int(len(var_list))
            var_count = 0
            selection = []
            for index, value in enumerate(json_vars):
                index += 1
                for vars in var_list:
                    if int(vars) == index:
                        var_count += 1
                        selection.append(value)
            if var_count == var_length:
                valid = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  The list of Vars {var_list} did not match the available list.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! Invalid Selection.  Please Select a valid Option from the List.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return selection

def varBoolLoop(**templateVars):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  {templateVars["Description"]}')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        varValue = input(f'{templateVars["varInput"]}  [{templateVars["varDefault"]}]: ')
        if varValue == '':
            if templateVars["varDefault"] == 'Y':
                varValue = True
            elif templateVars["varDefault"] == 'N':
                varValue = False
            valid = True
        elif varValue == 'N':
            varValue = False
            valid = True
        elif varValue == 'Y':
            varValue = True
            valid = True
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'   {templateVars["varName"]} value of "{varValue}" is Invalid!!! Please enter "Y" or "N".')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return varValue

def varNumberLoop(**templateVars):
    maxNum = templateVars["maxNum"]
    minNum = templateVars["minNum"]
    varName = templateVars["varName"]

    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  {templateVars["Description"]}')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        varValue = input(f'{templateVars["varInput"]}  [{templateVars["varDefault"]}]: ')
        if varValue == '':
            varValue = templateVars["varDefault"]
        if re.fullmatch(r'^[0-9]+$', str(varValue)):
            valid = validating.number_in_range(varName, varValue, minNum, maxNum)
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'   {varName} value of "{varValue}" is Invalid!!! ')
            print(f'   Valid range is {minNum} to {maxNum}.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return varValue

def varSensitiveStringLoop(**templateVars):
    maxLength = templateVars["maxLength"]
    minLength = templateVars["minLength"]
    varName = templateVars["varName"]
    varRegex = templateVars["varRegex"]

    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  {templateVars["Description"]}')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        varValue = stdiomask.getpass(f'{templateVars["varInput"]} ')
        if not varValue == '':
            valid = validating.length_and_regex_sensitive(varRegex, varName, varValue, minLength, maxLength)
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'   {varName} value is Invalid!!! ')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return varValue

def varStringLoop(**templateVars):
    maxLength = templateVars["maxLength"]
    minLength = templateVars["minLength"]
    varName = templateVars["varName"]
    varRegex = templateVars["varRegex"]

    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  {templateVars["Description"]}')
    print(f'\n-------------------------------------------------------------------------------------------\n')
    valid = False
    while valid == False:
        varValue = input(f'{templateVars["varInput"]} ')
        if 'press enter to skip' in templateVars["varInput"] and varValue == '':
            valid = True
        elif not templateVars["varDefault"] == '' and varValue == '':
            varValue = templateVars["varDefault"]
            valid = True
        elif not varValue == '':
            valid = validating.length_and_regex(varRegex, varName, varValue, minLength, maxLength)
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'   {varName} value of "{varValue}" is Invalid!!! ')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return varValue

def variable_loop(**templateVars):
    valid = False
    while valid == False:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'{templateVars["var_description"]}')
        policy_file = 'ucs_templates/variables/%s' % (templateVars["policy_file"])
        if os.path.isfile(policy_file):
            variable_file = open(policy_file, 'r')
            varsx = []
            for line in variable_file:
                varsx.append(line.strip())
            for index, value in enumerate(varsx):
                index += 1
                if index < 10:
                    print(f'     {index}. {value}')
                else:
                    print(f'    {index}. {value}')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        var_selection = input(f'Please Enter the Option Number to Select for {templateVars["var_type"]}: ')
        if not var_selection == '':
            if templateVars["multi_select"] == False and re.search(r'^[0-9]+$', str(var_selection)):
                for index, value in enumerate(varsx):
                    index += 1
                    if int(var_selection) == index:
                        selection = value
                        valid = True
            elif templateVars["multi_select"] == True and re.search(r'(^[0-9]+$|^[0-9\-,]+[0-9]$)', str(var_selection)):
                var_list = vlan_list_full(var_selection)
                var_length = int(len(var_list))
                var_count = 0
                selection = []
                for index, value in enumerate(varsx):
                    index += 1
                    for vars in var_list:
                        if int(vars) == index:
                            var_count += 1
                            selection.append(value)
                if var_count == var_length:
                    valid = True
                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  The list of Vars {var_list} did not match the available list.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Selection.  Please Select a valid Option from the List.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! Invalid Selection.  Please Select a valid Option from the List.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
    return selection

def vlan_list_full(vlan_list):
    full_vlan_list = []
    if re.search(r',', str(vlan_list)):
        vlist = vlan_list.split(',')
        for v in vlist:
            if re.fullmatch('^\\d{1,4}\\-\\d{1,4}$', v):
                a,b = v.split('-')
                a = int(a)
                b = int(b)
                vrange = range(a,b+1)
                for vl in vrange:
                    full_vlan_list.append(vl)
            elif re.fullmatch('^\\d{1,4}$', v):
                full_vlan_list.append(v)
    elif re.search('\\-', str(vlan_list)):
        a,b = vlan_list.split('-')
        a = int(a)
        b = int(b)
        vrange = range(a,b+1)
        for v in vrange:
            full_vlan_list.append(v)
    else:
        full_vlan_list.append(vlan_list)
    return full_vlan_list

def write_to_template(self, **templateVars):
    # Define the Template Source
    template = self.templateEnv.get_template(templateVars["template_file"])

    # Process the template
    dest_dir = '%s' % (self.type)
    dest_file = '%s.auto.tfvars' % (templateVars["template_type"])
    if templateVars["initial_write"] == True:
        write_method = 'w'
    else:
        write_method = 'a'
    process_method(write_method, dest_dir, dest_file, template, **templateVars)
