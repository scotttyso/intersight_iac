#!/usr/bin/env python3

import jinja2
import os
import pkg_resources
import platform
import re
import validating
from class_pools import pools
from class_policies_vxan import policies_vxan
from class_policies_lan import policies_lan
from easy_functions import choose_policy, policies_parse
from easy_functions import exit_default_no, exit_default_yes, exit_loop_default_yes
from easy_functions import naming_rule_fabric
from easy_functions import policy_descr, policy_name
from easy_functions import variablesFromAPI
from easy_functions import vlan_list_full
from easy_functions import write_to_template

ucs_template_path = pkg_resources.resource_filename('class_policies_san', 'Templates/')

class policies_san(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # Fibre-Channel Adapter Policy Module
    #==============================================
    def fibre_channel_adapter_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Fibre-Channel Adapter Policy'
        policy_x = 'Fibre-Channel Adapter'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["name_prefix"] = name_prefix
        templateVars["org"] = org
        templateVars["policy_file"] = 'fibre_channel_adapter_templates.txt'
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'fibre_channel_adapter_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  {policy_x} Policies:  To simplify your work, this wizard will use {policy_x}')
            print(f'  Templates that are pre-configured.  You can add custom {policy_x} policy')
            print(f'  configuration to the {templateVars["template_type"]}.auto.tfvars file at your descretion.  ')
            print(f'  That will not be covered by this wizard as the focus of the wizard is on simplicity.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    templateVars["multi_select"] = False
                    jsonVars = easy_jsonData['policies']['vnic.FcNetworkPolicy']
                    templateVars["var_description"] = jsonVars['templates']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['templates']['enum'])
                    templateVars["defaultVar"] = jsonVars['templates']['default']
                    templateVars["varType"] = 'Fibre-Channel Adapter Template'
                    templateVars["policy_template"] = variablesFromAPI(**templateVars)

                    if not templateVars["name_prefix"] == '':
                        name = '%s_%s' % (templateVars["name_prefix"], templateVars["policy_template"])
                    else:
                        name = '%s_%s' % (templateVars["org"], templateVars["policy_template"])

                    templateVars["name"] = policy_name(name, templateVars["policy_type"])
                    templateVars["descr"] = policy_descr(templateVars["name"], templateVars["policy_type"])

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   adapter_template = "{templateVars["policy_template"]}"')
                    print(f'   description      = "{templateVars["descr"]}"')
                    print(f'   name             = "{templateVars["name"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % ('ethernet_adapter_templates')
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

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # Fibre-Channel Network Policy Module
    #==============================================
    def fibre_channel_network_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Fibre-Channel Network Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'fibre_channel_network_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  Fibre-Channel Network Policies Notes:')
            print(f'  - You will need one Policy per Fabric.  VSAN A and VSAN B.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 0
                policy_loop = False
                while policy_loop == False:

                    name = naming_rule_fabric(loop_count, name_prefix, org)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['server.BaseProfile']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['TargetPlatform']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    templateVars["defaultVar"] = 'FIAttached'
                    templateVars["varType"] = 'Target Platform'
                    templateVars["target_platform"] = variablesFromAPI(**templateVars)

                    if templateVars["target_platform"] == 'Standalone':
                        valid = False
                        while valid == False:
                            templateVars["default_vlan"] = input('What is the Default VLAN you want to Assign to this Policy? ')
                            valid = validating.number_in_range('Default VLAN', templateVars["default_vlan"], 1, 4094)
                    else:
                        templateVars["default_vlan"] = 0

                    valid = False
                    while valid == False:
                        if loop_count % 2 == 0:
                            templateVars["vsan_id"] = input('What VSAN Do you want to Assign to this Policy?  [100]: ')
                        else:
                            templateVars["vsan_id"] = input('What VSAN Do you want to Assign to this Policy?  [200]: ')
                        if templateVars["vsan_id"] == '':
                            if loop_count % 2 == 0:
                                templateVars["vsan_id"] = 100
                            else:
                                templateVars["vsan_id"] = 200
                        vsan_valid = validating.number_in_range('VSAN ID', templateVars["vsan_id"], 1, 4094)
                        if vsan_valid == True:
                            if templateVars["target_platform"] == 'FIAttached':
                                policy_list = [
                                    'policies.vsan_policies.vsan_policy',
                                ]
                                templateVars["allow_opt_out"] = False
                                for policy in policy_list:
                                    vsan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)

                                vsan_list = []
                                for item in policyData['vsan_policies'][0][vsan_policy][0]['vsans']:
                                    for key, value in item.items():
                                        vsan_list.append(value[0]['vsan_id'])

                                vsan_string = ''
                                for vsan in vsan_list:
                                    if vsan_string == '':
                                        vsan_string = str(vsan)
                                    else:
                                        vsan_string = vsan_string + ',' + str(vsan)
                                vsan_list = vlan_list_full(vsan_string)
                                vsan_count = 0
                                for vsan in vsan_list:
                                    if int(templateVars["vsan_id"]) == int(vsan):
                                        vsan_count = 1
                                        break
                                if vsan_count == 0:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error with VSAN!!  The VSAN {templateVars["vsan_id"]} is not in the VSAN Policy')
                                    print(f'  {vsan_policy}.  Options are {vsan_list}.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                else:
                                    valid = True

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'   default_vlan = "{templateVars["default_vlan"]}"')
                    print(f'   description  = "{templateVars["descr"]}"')
                    print(f'   name         = "{templateVars["name"]}"')
                    print(f'   vsan_id      = "{templateVars["vsan_id"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

                            configure_loop, loop_count, policy_loop = exit_loop_default_yes(loop_count, policy_type)
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
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # Fibre-Channel QoS Policy Module
    #==============================================
    def fibre_channel_qos_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'qos'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Fibre-Channel QoS Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'fibre_channel_qos_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  It is a good practice to apply a {policy_type} to the vHBAs.  This wizard')
            print(f'  creates the policy with all the default values, so you only need one')
            print(f'  {policy_type}.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)
                    templateVars["burst"] = 1024
                    templateVars["max_data_field_size"] = 2112
                    templateVars["rate_limit"] = 0

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    burst               = "{templateVars["burst"]}"')
                    print(f'    description         = "{templateVars["descr"]}"')
                    print(f'    max_data_field_size = "{templateVars["max_data_field_size"]}"')
                    print(f'    name                = "{templateVars["name"]}"')
                    print(f'    rate_limit          = "{templateVars["rate_limit"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

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

    #==============================================
    # SAN Connectivity Policy Module
    #==============================================
    def san_connectivity_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'san'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'SAN Connectivity Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'san_connectivity_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  You can Skip this policy if you are not configuring Fibre-Channel.\n')
            print(f'  A {policy_type} will configure vHBA adapters for Server Profiles.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{templateVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['vnic.SanConnectivityPolicy']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['TargetPlatform']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    templateVars["defaultVar"] = 'FIAttached'
                    templateVars["varType"] = 'Target Platform'
                    templateVars["target_platform"] = variablesFromAPI(**templateVars)

                    if templateVars["target_platform"] == 'FIAttached':
                        templateVars["var_description"] = jsonVars['PlacementMode']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['PlacementMode']['enum'])
                        templateVars["defaultVar"] = jsonVars['PlacementMode']['default']
                        templateVars["varType"] = 'Placement Mode'
                        templateVars["vhba_placement_mode"] = variablesFromAPI(**templateVars)

                        templateVars["var_description"] = jsonVars['WwnnAddressType']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['WwnnAddressType']['enum'])
                        templateVars["defaultVar"] = jsonVars['WwnnAddressType']['default']
                        templateVars["varType"] = 'WWNN Allocation Type'
                        templateVars["wwnn_allocation_type"] = variablesFromAPI(**templateVars)

                        templateVars["wwnn_pool"] = ''
                        templateVars["wwnn_static"] = ''
                        if templateVars["wwnn_allocation_type"] == 'POOL':
                            policy_list = [
                                'pools.wwnn_pools.wwnn_pool'
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                templateVars["wwnn_pool"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                templateVars.update(policyData)

                        else:
                            valid = False
                            while valid == False:
                                templateVars["wwnn_static"] = input(f'What is the Static WWNN you would like to assign to this SAN Policy?  ')
                                if not templateVars["wwnn_static"] == '':
                                    valid = validating.wwxn_address('WWNN Static', templateVars["wwnn_static"])

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   BEGINNING vHBA Creation Process')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    fabrics = ['A', 'B']
                    templateVars["vhbas"] = []
                    inner_loop_count = 1
                    vhba_loop = False
                    while vhba_loop == False:
                        temp_policy_name = templateVars["name"]
                        templateVars["name"] = 'the vHBAs'
                        policy_list = [
                            'policies.fibre_channel_adapter_policies.fibre_channel_adapter_policy',
                            'policies.fibre_channel_qos_policies.fibre_channel_qos_policy'
                        ]
                        templateVars["allow_opt_out"] = False
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                            templateVars.update(policyData)

                        pci_order_consumed = [{0:[]},{1:[]}]

                        for x in fabrics:
                            templateVars["name"] = f'the vHBA on Fabric {x}'
                            policy_list = [
                                'policies.fibre_channel_network_policies.fibre_channel_network_policy'
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                policy_short = policy.split('.')[2]
                                templateVars[f"{policy_short}_{x}"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                templateVars.update(policyData)

                        templateVars["name"] = temp_policy_name

                        for x in fabrics:
                            valid = False
                            while valid == False:
                                templateVars[f'name_{x}'] = input(f'What is the name for Fabric {x} vHBA?  [HBA-{x}]: ')
                                if templateVars[f'name_{x}'] == '':
                                    templateVars[f'name_{x}'] = 'HBA-%s' % (x)
                                valid = validating.vname('vNIC Name', templateVars[f'name_{x}'])

                        valid = False
                        while valid == False:
                            question = input(f'\nNote: Persistent LUN Binding Enables retention of LUN ID associations in memory until they are'\
                                ' manually cleared.\n\n'\
                                'Do you want to Enable Persistent LUN Bindings?    Enter "Y" or "N" [N]: ')
                            if question == '' or question == 'N':
                                templateVars["persistent_lun_bindings"] = False
                                valid = True
                            elif question == 'Y':
                                templateVars["persistent_lun_bindings"] = True
                                valid = True
                            else:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n-------------------------------------------------------------------------------------------\n')

                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'    The PCI Link used as transport for the virtual interface. All VIC adapters have a')
                        print(f'    single PCI link except VIC 1385 which has two.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        for x in fabrics:
                            valid = False
                            while valid == False:
                                question = input(f'What is the PCI Link you want to Assign to Fabric {x}?  Range is 0-1.  [0]: ')
                                if question == '' or int(question) == 0:
                                    templateVars[f"pci_link_{x}"] = 0
                                    valid = True
                                elif int(question) == 1:
                                    templateVars[f"pci_link_{x}"] = 1
                                    valid = True
                                else:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Error!! Invalid Value.  Please enter 0 or 1.')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')

                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'    PCI Order establishes The order in which the virtual interface is brought up. The order ')
                        print(f'    assigned to an interface should be unique for all the Ethernet and Fibre-Channel ')
                        print(f'    interfaces on each PCI link on a VIC adapter. The maximum value of PCI order is limited ')
                        print(f'    by the number of virtual interfaces (Ethernet and Fibre-Channel) on each PCI link on a ')
                        print(f'    VIC adapter. All VIC adapters have a single PCI link except VIC 1385 which has two.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        pci_order_0 = 0
                        pci_order_1 = 0
                        for x in fabrics:
                            for item in pci_order_consumed:
                                for k, v in item.items():
                                    if int(k) == 0:
                                        for i in v:
                                            pci_order_0 = i
                                    else:
                                        for i in v:
                                            pci_order_1 = i
                            valid = False
                            while valid == False:
                                if templateVars[f'pci_link_{x}'] == 0:
                                    pci_order = (int(pci_order_0) + 1)
                                elif templateVars[f'pci_link_{x}'] == 1:
                                    pci_order = (int(pci_order_1) + 1)
                                question = input(f'What is the PCI Order you want to Assign to Fabric {x}?  [{pci_order}]: ')
                                if question == '':
                                    templateVars[f"pci_order_{x}"] = pci_order
                                duplicate = 0
                                for item in pci_order_consumed:
                                    for k, v in item.items():
                                        if templateVars[f'pci_link_{x}'] == 0 and int(k) == 0:
                                            for i in v:
                                                if int(i) == int(pci_order):
                                                    duplicate += 1
                                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                                    print(f'  Error!! PCI Order "{pci_order}" is already in use.  Please use an alternate.')
                                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                        elif templateVars[f'pci_link_{x}'] == 1 and int(k) == 1:
                                            for i in v:
                                                if int(i) == int(pci_order):
                                                    duplicate += 1
                                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                                    print(f'  Error!! PCI Order "{pci_order}" is already in use.  Please use an alternate.')
                                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                if duplicate == 0:
                                    if templateVars[f'pci_link_{x}'] == 0:
                                        pci_order_consumed[0][0].append(pci_order)
                                    elif templateVars[f'pci_link_{x}'] == 1:
                                        pci_order_consumed[1][1].append(pci_order)
                                    valid = True

                        templateVars["multi_select"] = False
                        jsonVars = easy_jsonData['policies']
                        templateVars["var_description"] = jsonVars['vnic.PlacementSettings']['description']
                        templateVars["jsonVars"] = [x for x in jsonVars['vnic.PlacementSettings']['enum']]
                        templateVars["defaultVar"] = jsonVars['vnic.PlacementSettings']['default']
                        templateVars["varType"] = 'Slot Id'
                        templateVars["slot_id"] = variablesFromAPI(**templateVars)

                        if not templateVars["target_platform"] == 'FIAttached':
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    The Uplink Port is the Adapter port on which the virtual interface will be created.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            for x in fabrics:
                                valid = False
                                while valid == False:
                                    question = input(f'What is the Uplink Port you want to Assign to Fabric {x}?  Range is 0-3.  [0]: ')
                                    if question == '':
                                        templateVars[f"uplink_port_{x}"] = 0
                                    if re.fullmatch(r'^[0-3]', str(question)):
                                        templateVars[f"uplink_port_{x}"] = question
                                        valid = validating.number_in_range(f'Fabric {x} PCI Uplink', templateVars[f"uplink_port_{x}"], 0, 3)
                                    else:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! Invalid Value.  Please enter 0 or 1.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')

                        jsonVars = jsonData['components']['schemas']['vnic.FcIf']['allOf'][1]['properties']
                        templateVars["var_description"] = jsonVars['Type']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['Type']['enum'])
                        templateVars["defaultVar"] = jsonVars['Type']['default']
                        templateVars["varType"] = 'vHBA Type'
                        templateVars["vhba_type"] = variablesFromAPI(**templateVars)

                        templateVars["var_description"] = jsonVars['WwpnAddressType']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['WwpnAddressType']['enum'])
                        templateVars["defaultVar"] = jsonVars['WwpnAddressType']['default']
                        templateVars["varType"] = 'WWPN Allocation Type'
                        templateVars["wwpn_allocation_type"] = variablesFromAPI(**templateVars)

                        if templateVars["target_platform"] == 'FIAttached':
                            templateVars[f'wwpn_pool_A'] = ''
                            templateVars[f'wwpn_pool_B'] = ''
                            templateVars[f'wwpn_static_A'] = ''
                            templateVars[f'wwpn_static_B'] = ''
                            if templateVars["wwpn_allocation_type"] == 'POOL':
                                policy_list = [
                                    'pools.wwpn_pools.wwpn_pool'
                                ]
                                templateVars["allow_opt_out"] = False
                                for x in fabrics:
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    print(f'  Select WWPN Pool for Fabric {x}:')
                                    print(f'\n-------------------------------------------------------------------------------------------\n')
                                    for policy in policy_list:
                                        policy_short = policy.split('.')[2]
                                        templateVars[f'{policy_short}_{x}'],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                        templateVars.update(policyData)

                            else:
                                valid = False
                                while valid == False:
                                    for x in fabrics:
                                        templateVars["wwpn_static"] = input(f'What is the Static WWPN you would like to assign to Fabric {x}?  ')
                                    if not templateVars["wwpn_static"] == '':
                                        templateVars[f"wwpn_static_{x}"]
                                        valid = validating.wwxn_address(f'Fabric {x} WWPN Static', templateVars["wwpn_static"])

                        if templateVars["target_platform"] == 'FIAttached':
                            vhba_fabric_a = {
                                'fibre_channel_adapter_policy':templateVars["fibre_channel_adapter_policy"],
                                'fibre_channel_network_policy':templateVars["fibre_channel_network_policy_A"],
                                'fibre_channel_qos_policy':templateVars["fibre_channel_qos_policy"],
                                'name':templateVars["name_A"],
                                'persistent_lun_bindings':templateVars["persistent_lun_bindings"],
                                'pci_link':templateVars["pci_link_A"],
                                'pci_order':templateVars["pci_order_A"],
                                'slot_id':templateVars["slot_id"],
                                'switch_id':'A',
                                'vhba_type':templateVars["vhba_type"],
                                'wwpn_allocation_type':templateVars["wwpn_allocation_type"],
                                'wwpn_pool':templateVars["wwpn_pool_A"],
                                'wwpn_static':templateVars["wwpn_static_A"],
                            }
                            vhba_fabric_b = {
                                'fibre_channel_adapter_policy':templateVars["fibre_channel_adapter_policy"],
                                'fibre_channel_network_policy':templateVars["fibre_channel_network_policy_B"],
                                'fibre_channel_qos_policy':templateVars["fibre_channel_qos_policy"],
                                'name':templateVars["name_B"],
                                'persistent_lun_bindings':templateVars["persistent_lun_bindings"],
                                'pci_link':templateVars["pci_link_B"],
                                'pci_order':templateVars["pci_order_B"],
                                'slot_id':templateVars["slot_id"],
                                'switch_id':'B',
                                'vhba_type':templateVars["vhba_type"],
                                'wwpn_allocation_type':templateVars["wwpn_allocation_type"],
                                'wwpn_pool':templateVars["wwpn_pool_B"],
                                'wwpn_static':templateVars["wwpn_static_B"]
                            }
                        else:
                            vhba_fabric_a = {
                                'fibre_channel_adapter_policy':templateVars["fibre_channel_adapter_policy"],
                                'fibre_channel_network_policy':templateVars["fibre_channel_network_policy_A"],
                                'fibre_channel_qos_policy':templateVars["fibre_channel_qos_policy"],
                                'name':templateVars["name_A"],
                                'persistent_lun_bindings':templateVars["persistent_lun_bindings"],
                                'pci_link':templateVars["pci_link_A"],
                                'pci_order':templateVars["pci_order_A"],
                                'slot_id':templateVars["slot_id"],
                                'uplink_port':templateVars["uplink_port_A"],
                                'vhba_type':templateVars["vhba_type"],
                                'wwpn_allocation_type':templateVars["wwpn_allocation_type"],
                                'wwpn_pool':templateVars["wwpn_pool_A"],
                                'wwpn_static':templateVars["wwpn_static_A"]
                            }
                            vhba_fabric_b = {
                                'fibre_channel_adapter_policy':templateVars["fibre_channel_adapter_policy"],
                                'fibre_channel_network_policy':templateVars["fibre_channel_network_policy_B"],
                                'fibre_channel_qos_policy':templateVars["fibre_channel_qos_policy"],
                                'name':templateVars["name_B"],
                                'persistent_lun_bindings':templateVars["persistent_lun_bindings"],
                                'pci_link':templateVars["pci_link_B"],
                                'pci_order':templateVars["pci_order_B"],
                                'slot_id':templateVars["slot_id"],
                                'uplink_port':templateVars["uplink_port_B"],
                                'vhba_type':templateVars["vhba_type"],
                                'wwpn_allocation_type':templateVars["wwpn_allocation_type"],
                                'wwpn_pool':templateVars["wwpn_pool_B"],
                                'wwpn_static':templateVars["wwpn_static_B"]
                            }
                        print(vhba_fabric_a)
                        print(vhba_fabric_b)
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'Fabric A:')
                        print(f'   fibre_channel_adapter_policy = "{templateVars["fibre_channel_adapter_policy"]}"')
                        print(f'   fibre_channel_network_policy = "{templateVars["fibre_channel_network_policy_A"]}"')
                        print(f'   fibre_channel_qos_policy     = "{templateVars["fibre_channel_qos_policy"]}"')
                        print(f'   name                         = "{templateVars["name_A"]}"')
                        print(f'   persistent_lun_bindings      = {templateVars["persistent_lun_bindings"]}')
                        print(f'   placement_pci_link           = {templateVars["pci_link_A"]}')
                        print(f'   placement_pci_order          = {templateVars["pci_order_A"]}')
                        print(f'   placement_slot_id            = "{templateVars["slot_id"]}"')
                        if templateVars["target_platform"] == 'FIAttached':
                            print(f'   placement_switch_id          = "A"')
                        else:
                            print(f'   placement_uplink_port        = "{templateVars["uplink_port_A"]}"')
                        print(f'   vhba_type                    = "{templateVars["vhba_type"]}"')
                        print(f'   wwpn_allocation_type         = "{templateVars["wwpn_allocation_type"]}"')
                        if templateVars["wwpn_allocation_type"] == 'Pool':
                            print(f'   wwpn_pool                    = "{templateVars["wwpn_pool_A"]}"')
                        else:
                            print(f'   wwpn_static_address          = "{templateVars["wwpn_static_A"]}"')
                        print(f'Fabric B:')
                        print(f'   fibre_channel_adapter_policy = "{templateVars["fibre_channel_adapter_policy"]}"')
                        print(f'   fibre_channel_network_policy = "{templateVars["fibre_channel_network_policy_B"]}"')
                        print(f'   fibre_channel_qos_policy     = "{templateVars["fibre_channel_qos_policy"]}"')
                        print(f'   name                         = "{templateVars["name_B"]}"')
                        print(f'   persistent_lun_bindings      = {templateVars["persistent_lun_bindings"]}')
                        print(f'   placement_pci_link           = {templateVars["pci_link_B"]}')
                        print(f'   placement_pci_order          = {templateVars["pci_order_B"]}')
                        print(f'   placement_slot_id            = "{templateVars["slot_id"]}"')
                        if templateVars["target_platform"] == 'FIAttached':
                            print(f'   placement_switch_id          = "B"')
                        else:
                            print(f'   placement_uplink_port        = "{templateVars["uplink_port_B"]}"')
                        print(f'   vhba_type                    = "{templateVars["vhba_type"]}"')
                        if templateVars["target_platform"] == 'FIAttached':
                            print(f'   wwpn_allocation_type         = "{templateVars["wwpn_allocation_type"]}"')
                            if templateVars["wwpn_allocation_type"] == 'Pool':
                                print(f'   wwpn_pool                    = "{templateVars["wwpn_pool_B"]}"')
                            else:
                                print(f'   wwpn_static_address          = "{templateVars["wwpn_static_B"]}"')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        valid_confirm = False
                        while valid_confirm == False:
                            confirm_v = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                            if confirm_v == 'Y' or confirm_v == '':
                                templateVars["vhbas"].append(vhba_fabric_a)
                                templateVars["vhbas"].append(vhba_fabric_b)
                                valid_exit = False
                                while valid_exit == False:
                                    loop_exit = input(f'Would You like to Configure another set of vHBAs?  Enter "Y" or "N" [N]: ')
                                    if loop_exit == 'Y':
                                        inner_loop_count += 1
                                        valid_confirm = True
                                        valid_exit = True
                                    elif loop_exit == 'N' or loop_exit == '':
                                        vhba_loop = True
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
                    print(f'    description          = "{templateVars["descr"]}"')
                    print(f'    name                 = "{templateVars["name"]}"')
                    print(f'    target_platform      = "{templateVars["target_platform"]}"')
                    if templateVars["target_platform"] == 'FIAttached':
                        print(f'    vhba_placement_mode  = "{templateVars["vhba_placement_mode"]}"')
                        print(f'    wwnn_allocation_type = "{templateVars["wwnn_allocation_type"]}"')
                        print(f'    wwnn_pool            = "{templateVars["wwnn_pool"]}"')
                        print(f'    wwnn_static          = "{templateVars["wwnn_static"]}"')
                    if len(templateVars["vhbas"]) > 0:
                        print(f'    vhbas = ''[')
                        for item in templateVars["vhbas"]:
                            print(f'      ''{')
                            for k, v in item.items():
                                if k == 'fibre_channel_adapter_policy':
                                    print(f'        fibre_channel_adapter_policy = "{v}"')
                                elif k == 'fibre_channel_network_policy':
                                    print(f'        fibre_channel_network_policy = "{v}"')
                                elif k == 'fibre_channel_qos_policy':
                                    print(f'        fibre_channel_qos_policy     = "{v}"')
                                elif k == 'name':
                                    print(f'        name                         = "{v}"')
                                elif k == 'persistent_lun_bindings':
                                    print(f'        persistent_lun_bindings      = {v}')
                                elif k == 'pci_link':
                                    print(f'        placement_pci_link           = {v}')
                                elif k == 'pci_link':
                                    print(f'        placement_pci_order          = {v}')
                                elif k == 'placement_slot_id':
                                    print(f'        placement_slot_id            = "{v}"')
                                elif k == 'switch_id':
                                    print(f'        placement_switch_id          = "{v}"')
                                elif k == 'uplink_port':
                                    print(f'        placement_uplink_port        = "{v}"')
                                elif k == 'vhba_type':
                                    print(f'        vhba_type                    = "{v}"')
                                elif k == 'wwpn_allocation_type':
                                    print(f'        wwpn_allocation_type         = "{v}"')
                                elif k == 'wwpn_pool':
                                    print(f'        wwpn_pool                    = "{v}"')
                                elif k == 'wwpn_static':
                                    print(f'        wwpn_static                  = "{v}"')
                            print(f'      ''}')
                        print(f'    '']')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                            write_to_template(self, **templateVars)

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

def policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars):
    loop_valid = False
    while loop_valid == False:
        create_policy = True
        inner_policy = policy.split('.')[1]
        inner_type = policy.split('.')[0]
        inner_var = policy.split('.')[2]
        templateVars[inner_var] = ''
        templateVars["policies"],policyData = policies_parse(templateVars["org"], inner_type, inner_policy)
        if not len(templateVars["policies"]) > 0:
            valid = False
            while valid == False:

                x = inner_policy.split('_')
                policy_description = []
                for y in x:
                    y = y.capitalize()
                    policy_description.append(y)
                policy_description = " ".join(policy_description)
                policy_description = policy_description.replace('Wwnn', 'WWNN')
                policy_description = policy_description.replace('Wwpn', 'WWPN')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There were no {policy_description} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

                if 'Policies' in policy_description:
                    policy_description = policy_description.replace('Policies', 'Policy')
                elif 'Pools' in policy_description:
                    policy_description = policy_description.replace('Pools', 'Pool')
                elif 'Profiles' in policy_description:
                    policy_description = policy_description.replace('Profiles', 'Profile')
                elif 'Templates' in policy_description:
                    policy_description = policy_description.replace('Templates', 'Template')

                if templateVars["allow_opt_out"] == True:
                    Question = input(f'Do you want to create a(n) {policy_description}?  Enter "Y" or "N" [Y]: ')
                    if Question == '' or Question == 'Y':
                        create_policy = True
                        valid = True
                    elif Question == 'N':
                        create_policy = False
                        valid = True
                        return templateVars[inner_var],policyData
                else:
                    create_policy = True
                    valid = True

        else:
            templateVars[inner_var] = choose_policy(inner_policy, **templateVars)
            if templateVars[inner_var] == 'create_policy':
                create_policy = True
            elif templateVars[inner_var] == '' and templateVars["allow_opt_out"] == True:
                loop_valid = True
                create_policy = False
                return templateVars[inner_var],policyData
            elif not templateVars[inner_var] == '':
                loop_valid = True
                create_policy = False
                return templateVars[inner_var],policyData
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
            if inner_policy == 'wwnn_pools':
                pools(name_prefix, templateVars["org"], inner_type).wwnn_pools(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'wwpn_pools':
                pools(name_prefix, templateVars["org"], inner_type).wwpn_pools(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'fibre_channel_adapter_policies':
                policies_san(name_prefix, templateVars["org"], inner_type).fibre_channel_adapter_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'fibre_channel_network_policies':
                policies_san(name_prefix, templateVars["org"], inner_type).fibre_channel_network_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'fibre_channel_qos_policies':
                policies_san(name_prefix, templateVars["org"], inner_type).fibre_channel_qos_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'lan_connectivity_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).lan_connectivity_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'vlan_policies':
                policies_vxan(name_prefix, templateVars["org"], inner_type).vlan_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'vsan_policies':
                policies_vxan(name_prefix, templateVars["org"], inner_type).vsan_policies(jsonData, easy_jsonData, **kwargs)
