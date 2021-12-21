#!/usr/bin/env python3

import jinja2
import os
import pkg_resources
import re
import subprocess
import validating
from class_policies_vxan import policies_vxan
from class_policies_p3 import policies_p3
from class_pools import pools
from easy_functions import choose_policy, policies_parse
from easy_functions import exit_default_no, exit_default_yes
from easy_functions import policy_descr, policy_name
from easy_functions import variablesFromAPI
from easy_functions import varBoolLoop
from easy_functions import varNumberLoop
from easy_functions import varSensitiveStringLoop
from easy_functions import varStringLoop
from easy_functions import vlan_list_full
from easy_functions import write_to_template

ucs_template_path = pkg_resources.resource_filename('class_policies_lan', 'Templates/')

class policies_lan(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # Ethernet Adapter Policy Module
    #==============================================
    def ethernet_adapter_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        org = self.org
        policy_type = 'Ethernet Adapter Policy'
        policy_x = 'Ethernet Adapter'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["name_prefix"] = name_prefix
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ethernet_adapter_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  {policy_x} Policies:  To simplify your work, this wizard will use {policy_x}')
            print(f'  Templates that are pre-configured.  You can add custom {policy_x} policy')
            print(f'  configuration to the {templateVars["template_type"]}.auto.tfvars file at your descretion.')
            print(f'  That will not be covered by this wizard as the focus of the wizard is on simplicity.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    templateVars["multi_select"] = False
                    jsonVars = easy_jsonData['policies']['vnic.EthNetworkPolicy']
                    templateVars["var_description"] = jsonVars['templates']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['templates']['enum'])
                    templateVars["defaultVar"] = jsonVars['templates']['default']
                    templateVars["varType"] = 'Ethernet Adapter Template'
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
    # Ethernet Network Control Policy Module
    #==============================================
    def ethernet_network_control_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'netwk_ctrl'
        org = self.org
        policy_type = 'Ethernet Network Control Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ethernet_network_control_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will allow you to control Network Discovery with ')
            print(f'  protocols like CDP and LLDP as well as MAC Address Control Features.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)
                templateVars["action_on_uplink_fail"] = 'linkDown'

                valid = False
                while valid == False:
                    cdp = input('Do you want to enable CDP (Cisco Discovery Protocol) for this Policy?  Enter "Y" or "N" [Y]: ')
                    if cdp == '' or cdp == 'Y':
                        templateVars["cdp_enable"] = True
                        valid = True
                    elif cdp == 'N':
                        templateVars["cdp_enable"] = False
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Option.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                valid = False
                while valid == False:
                    cdp = input('Do you want to enable LLDP (Link Level Discovery Protocol) for this Policy?  Enter "Y" or "N" [Y]: ')
                    if cdp == '' or cdp == 'Y':
                        templateVars["lldp_receive_enable"] = True
                        templateVars["lldp_transmit_enable"] = True
                        valid = True
                    elif cdp == 'N':
                        templateVars["lldp_receive_enable"] = False
                        templateVars["lldp_transmit_enable"] = False
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Option.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                templateVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['fabric.EthNetworkControlPolicy']['allOf'][1]['properties']
                templateVars["var_description"] = jsonVars['MacRegistrationMode']['description']
                templateVars["jsonVars"] = sorted(jsonVars['MacRegistrationMode']['enum'])
                templateVars["defaultVar"] = jsonVars['MacRegistrationMode']['default']
                templateVars["varType"] = 'MAC Registration Mode'
                templateVars["mac_register_mode"] = variablesFromAPI(**templateVars)

                templateVars["var_description"] = jsonVars['ForgeMac']['description']
                templateVars["jsonVars"] = sorted(jsonVars['ForgeMac']['enum'])
                templateVars["defaultVar"] = jsonVars['ForgeMac']['default']
                templateVars["varType"] = 'MAC Security Forge'
                templateVars["mac_security_forge"] = variablesFromAPI(**templateVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    action_on_uplink_fail = "{templateVars["action_on_uplink_fail"]}"')
                print(f'    cdp_enable            = {templateVars["cdp_enable"]}')
                print(f'    description           = "{templateVars["descr"]}"')
                print(f'    lldp_enable_receive   = {templateVars["lldp_receive_enable"]}')
                print(f'    lldp_enable_transmit  = {templateVars["lldp_transmit_enable"]}')
                print(f'    mac_register_mode     = "{templateVars["mac_register_mode"]}"')
                print(f'    mac_security_forge    = "{templateVars["mac_security_forge"]}"')
                print(f'    name                  = "{templateVars["name"]}"')
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

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # Ethernet Network Group Policy Module
    #==============================================
    def ethernet_network_group_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = ['Management', 'Migration', 'Storage', 'VMs']
        org = self.org
        policy_type = 'Ethernet Network Group Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ethernet_network_group_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will define the Allowed VLANs on a Server vNIC Template.')
            print(f'  As a recommendation you will need an {policy_type} per vNIC Grouping.')
            print(f'  For Instance with a Virtual Host that may have the following vNIC Pairs:')
            print(f'     1. Management')
            print(f'     2. Migration/vMotion')
            print(f'     3. Storage')
            print(f'     4. Virtual Machines')
            print(f'  You will want to configure 1 {policy_type} per Group.')
            print(f'  The allowed vlan list can be in the format of:')
            print(f'     5 - Single VLAN')
            print(f'     1-10 - Range of VLANs')
            print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
            print(f'     1-10,20-30 - Ranges and Lists of VLANs')
            print(f'  If you want to Assign a Native VLAN Make sure it is in the allowed list.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            loop_count = 0
            policy_loop = False
            while policy_loop == False:

                name = ''
                for i, v in enumerate(name_suffix):
                    if int(loop_count) == i:
                        if not name_prefix == '':
                            name = '%s_%s' % (name_prefix, v)
                        else:
                            name = '%s_%s' % (org, v)
                if name == '':
                    name = '%s_%s' % (org, 'vlan_group')

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)
                templateVars["action_on_uplink_fail"] = 'linkDown'

                policy_list = [
                    'policies.vlan_policies.vlan_policy',
                ]
                templateVars["allow_opt_out"] = False
                for policy in policy_list:
                    vlan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                
                vlan_list = []
                for item in policyData['vlan_policies'][0][vlan_policy][0]['vlans']:
                    for k, v in item.items():
                        vlan_list.append(v[0]['vlan_list'])

                vlan_convert = ''
                for vlan in vlan_list:
                    if vlan_convert == '':
                        vlan_convert = str(vlan)
                    else:
                        vlan_convert = vlan_convert + ',' + str(vlan)

                vlan_list = vlan_list_full(vlan_convert)

                valid = False
                while valid == False:
                    VlanList = input('Enter the VLAN or List of VLANs to add to this VLAN Group: ')
                    if not VlanList == '':
                        vlanListExpanded = vlan_list_full(VlanList)

                        valid_vlan = True
                        vlans_not_in_domain_policy = []
                        for vlan in vlanListExpanded:
                            if str(vlan).isnumeric():
                                valid_vlan = validating.number_in_range('VLAN ID', vlan, 1, 4094)
                                if not valid_vlan == False:
                                    vlan_count = 0
                                    for vlans in vlan_list:
                                        if int(vlan) == int(vlans):
                                            vlan_count += 1
                                            break
                                    if vlan_count == 0:
                                        vlans_not_in_domain_policy.append(vlan)
                            else:
                                vlans_not_in_domain_policy.append(vlan)

                        if len(vlans_not_in_domain_policy) > 0:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error with VLAN(s) assignment!!  The following VLAN(s) are missing.')
                            print(f'  - Missing VLANs: {vlans_not_in_domain_policy}')
                            print(f'  - VLAN Policy: "{vlan_policy}"')
                            print(f'  - Has VLANs: "{vlan_convert}"')
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            valid_vlan = False

                        native_count = 0
                        nativeVlan = ''
                        if valid_vlan == True:
                            nativeValid = False
                            while nativeValid == False:
                                nativeVlan = input('Do you want to Configure one of the VLANs as a Native VLAN?  [press enter to skip]:')
                                if nativeVlan == '':
                                    nativeValid = True
                                    valid = True
                                else:
                                    for vlan in vlanListExpanded:
                                        if int(nativeVlan) == int(vlan):
                                            native_count = 1
                                    if not native_count == 1:
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! The Native VLAN was not in the Allowed List.')
                                        print(f'  Allowed VLAN List is: "{VlanList}"')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                    else:
                                        nativeValid = True
                                        valid = True

                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  The allowed vlan list can be in the format of:')
                        print(f'     5 - Single VLAN')
                        print(f'     1-10 - Range of VLANs')
                        print(f'     1,2,3,4,5,11,12,13,14,15 - List of VLANs')
                        print(f'     1-10,20-30 - Ranges and Lists of VLANs')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                templateVars["allowed_vlans"] = VlanList
                if not nativeVlan == '':
                    templateVars["native_vlan"] = nativeVlan
                else:
                    templateVars["native_vlan"] = ''
                    templateVars.pop('native_vlan')

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    allowed_vlans = "{templateVars["allowed_vlans"]}"')
                print(f'    description   = "{templateVars["descr"]}"')
                print(f'    name          = "{templateVars["name"]}"')
                if not nativeVlan == '':
                    print(f'    native_vlan   = {templateVars["native_vlan"]}')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                        write_to_template(self, **templateVars)

                        valid_exit = False
                        while valid_exit == False:
                            if loop_count < 3:
                                exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [Y]: ')
                            else:
                                exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
                            if (loop_count < 3 and exit_answer == '') or exit_answer == 'Y':
                                loop_count += 1
                                valid_exit = True
                            elif (loop_count > 2 and exit_answer == '') or exit_answer == 'N':
                                policy_loop = True
                                configure_loop = True
                                valid_exit = True
                            else:
                                print(f'\n------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n------------------------------------------------------\n')
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

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # Ethernet Network Policy Module
    #==============================================
    def ethernet_network_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'network'
        org = self.org
        policy_type = 'Ethernet Network Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ethernet_network_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} determines if the port can carry single VLAN (Access) ')
            print(f'  or multiple VLANs (Trunk) traffic. You can specify the VLAN to be associated with an ')
            print(f'  Ethernet packet if no tag is found.\n\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
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
                    jsonVars = jsonData['components']['schemas']['vnic.VlanSettings']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['Mode']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['Mode']['enum'])
                    templateVars["defaultVar"] = jsonVars['Mode']['default']
                    templateVars["varType"] = 'VLAN Mode'
                    templateVars["vlan_mode"] = variablesFromAPI(**templateVars)

                    valid = False
                    while valid == False:
                        templateVars["default_vlan"] = input('What is the default vlan to assign to this Policy.  Range is 0 to 4094: ')
                        if re.fullmatch(r'[0-9]{1,4}', templateVars["default_vlan"]):
                            valid = validating.number_in_range('VLAN ID', templateVars["default_vlan"], 0, 4094)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    default_vlan  = {templateVars["default_vlan"]}')
                    print(f'    description   = "{templateVars["descr"]}"')
                    print(f'    name          = "{templateVars["name"]}"')
                    print(f'    vlan_mode     = "{templateVars["vlan_mode"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
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
    # Ethernet QoS Policy Module
    #==============================================
    def ethernet_qos_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = ['Management', 'Migration', 'Storage', 'VMs']
        org = self.org
        policy_type = 'Ethernet QoS Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ethernet_qos_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will configure QoS on a Server vNIC Template.')
            print(f'  As a recommendation you will need an {policy_type} per vNIC Group.')
            print(f'  For Instance with a Virtual Host that may have the following vNIC Groups:')
            print(f'     1. Management')
            print(f'     2. Migration/vMotion')
            print(f'     3. Storage')
            print(f'     4. Virtual Machines')
            print(f'  It would be a good practice to configure different QoS Priorities for Each vNIC Group.')
            print(f'  For Instance a good practice would be something like the following:')
            print(f'     Management - Silver')
            print(f'     Migration/vMotion - Bronze')
            print(f'     Storage - Platinum')
            print(f'     Virtual Machines - Gold.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')

            templateVars["multi_select"] = False
            jsonVars = jsonData['components']['schemas']['vnic.EthNetworkPolicy']['allOf'][1]['properties']
            templateVars["var_description"] = jsonVars['TargetPlatform']['description']
            templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
            templateVars["defaultVar"] = 'FIAttached'
            templateVars["varType"] = 'Target Platform'
            templateVars["target_platform"] = variablesFromAPI(**templateVars)

            loop_count = 0
            policy_loop = False
            while policy_loop == False:

                name = ''
                if templateVars["target_platform"] == 'FIAttached':
                    for i, v in enumerate(name_suffix):
                        if int(loop_count) == i:
                            if not name_prefix == '':
                                name = '%s_%s' % (name_prefix, v)
                            else:
                                name = '%s_%s' % (org, v)
                else:
                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, 'qos')

                if name == '':
                    name = '%s_%s' % (org, 'qos')

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    Enable Trust Host CoS enables the VIC to Pass thru the CoS value recieved from the Host.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid = False
                while valid == False:
                    question = input(f'Do you want to Enable Trust Host based CoS?  Enter "Y" or "N" [N]: ')
                    if question == '' or question == 'N':
                        templateVars["enable_trust_host_cos"] = False
                        valid = True
                    elif question == 'Y':
                        templateVars["enable_trust_host_cos"] = True
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    The value in Mbps (0-100000) to use for limiting the data rate on the virtual interface. ')
                print(f'    Setting this to zero will turn rate limiting off.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid = False
                while valid == False:
                    Question = input('What is the Rate Limit you want to assign to the Policy?  [0]: ')
                    if Question == '':
                        Question = 0
                    if re.fullmatch(r'^[0-9]{1,6}$', str(Question)):
                        minValue = 0
                        maxValue = 100000
                        templateVars["varName"] = 'Rate Limit'
                        varValue = Question
                        valid = validating.number_in_range(templateVars["varName"], varValue, minValue, maxValue)
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'    Invalid Rate Limit value "{Question}"!!!')
                        print(f'    The valid range is between 0 and 100000. The default value is 0.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                templateVars["rate_limit"] = Question

                if templateVars["target_platform"] == 'Standalone':
                    templateVars["burst"] = 1024
                    templateVars["priority"] = 'Best Effort'
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    The Class of Service to be associated to the traffic on the virtual interface.')
                    print(f'    The valid range is between 0 and 6. The default value is 0.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        Question = input('What is the Class of Service you want to assign to the Policy?  [0]: ')
                        if Question == '':
                            Question = 0
                        if re.fullmatch(r'^[0-6]$', str(Question)):
                            minValue = 0
                            maxValue = 6
                            templateVars["varName"] = 'Class of Service'
                            varValue = Question
                            valid = validating.number_in_range(templateVars["varName"], varValue, minValue, maxValue)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    Invalid Class of Service value "{Question}"!!!')
                            print(f'    The valid range is between 0 and 6. The default value is 0.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["cos"] = Question

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    The Maximum Transmission Unit (MTU) or packet size that the virtual interface accepts.')
                    print(f'    The valid range is between 1500 and 9000. The default value is 1500.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        Question = input('What is the MTU you want to assign to the Policy?  [1500]: ')
                        if Question == '':
                            Question = 1500
                        if re.fullmatch(r'^[0-9]{4}$', str(Question)):
                            minValue = 1500
                            maxValue = 9000
                            templateVars["varName"] = 'MTU'
                            varValue = Question
                            valid = validating.number_in_range(templateVars["varName"], varValue, minValue, maxValue)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    Invalid MTU value "{Question}"!!!')
                            print(f'    The valid range is between 1500 and 9000. The default value is 1500.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["mtu"] = Question

                else:
                    templateVars["cos"] = 0
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    The burst traffic allowed on the vNIC in bytes.')
                    print(f'    The valid range is between 1024 and 1000000. The default value is 1024.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid = False
                    while valid == False:
                        Question = input('What is the Burst Rate you want to assign to the Policy?  [1024]: ')
                        if Question == '':
                            Question = 1024
                        if re.fullmatch(r'^[0-9]{4,7}$', str(Question)):
                            minValue = 1024
                            maxValue = 1000000
                            templateVars["varName"] = 'Burst'
                            varValue = Question
                            valid = validating.number_in_range(templateVars["varName"], varValue, minValue, maxValue)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    Invalid Burst value "{Question}"!!!')
                            print(f'    The valid range is between 1024 and 1000000. The default value is 1024.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    templateVars["burst"] = Question

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['vnic.EthQosPolicy']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['Priority']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['Priority']['enum'])
                    templateVars["defaultVar"] = jsonVars['Priority']['default']
                    templateVars["varType"] = '%s QoS Priority' % (templateVars["name"])
                    templateVars["priority"] = variablesFromAPI(**templateVars)

                    if loop_count == 0:
                        if templateVars["target_platform"] == 'FIAttached':
                            policy_list = [
                                'policies.system_qos_policies.system_qos_policy',
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                system_qos_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)

                    mtu = policyData['system_qos_policies'][0][system_qos_policy][0]['classes'][0][templateVars["priority"]][0]['mtu']
                    if mtu > 8999:
                        templateVars["mtu"] = 9000
                    else:
                        templateVars["mtu"] = mtu

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  ')
                if templateVars["target_platform"] == 'FIAttached':
                    print(f'   burst                 = {templateVars["burst"]}')
                if templateVars["target_platform"] == 'Standalone':
                    print(f'   cos                   = {templateVars["cos"]}')
                print(f'   description           = "{templateVars["descr"]}"')
                print(f'   enable_trust_host_cos = {templateVars["enable_trust_host_cos"]}')
                print(f'   mtu                   = {templateVars["mtu"]}')
                print(f'   name                  = "{templateVars["name"]}"')
                if templateVars["target_platform"] == 'FIAttached':
                    print(f'   priority              = "{templateVars["priority"]}"')
                print(f'   rate_limit            = {templateVars["rate_limit"]}')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
                        write_to_template(self, **templateVars)

                        valid_exit = False
                        while valid_exit == False:
                            if loop_count < 3 and templateVars["target_platform"] == 'FIAttached':
                                exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [Y]: ')
                            else:
                                exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
                            if loop_count < 3 and exit_answer == '' and templateVars["target_platform"] == 'FIAttached':
                                loop_count += 1
                                valid_exit = True
                            elif exit_answer == 'Y':
                                loop_count += 1
                                valid_exit = True
                            elif (exit_answer == '') or exit_answer == 'N':
                                policy_loop = True
                                configure_loop = True
                                valid_exit = True
                            else:
                                print(f'\n------------------------------------------------------\n')
                                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                                print(f'\n------------------------------------------------------\n')
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

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # iSCSI Adapter Policy Module
    #==============================================
    def iscsi_adapter_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'adapter'
        org = self.org
        policy_type = 'iSCSI Adapter Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'iscsi_adapter_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to configure values for TCP Connection Timeout, ')
            print(f'  DHCP Timeout, and the Retry Count if the specified LUN ID is busy.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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

                    # Pull in the Policies for iSCSI Adapter
                    jsonVars = jsonData['components']['schemas']['vnic.IscsiAdapterPolicy']['allOf'][1]['properties']

                    # DHCP Timeout
                    templateVars["Description"] = jsonVars['DhcpTimeout']['description']
                    templateVars["varInput"] = 'Enter the number of seconds after which the DHCP times out.'
                    templateVars["varDefault"] = 60
                    templateVars["varName"] = 'DHCP Timeout'
                    templateVars["minNum"] = jsonVars['DhcpTimeout']['minimum']
                    templateVars["maxNum"] = jsonVars['DhcpTimeout']['maximum']
                    templateVars["dhcp_timeout"] = varNumberLoop(**templateVars)

                    # LUN Busy Retry Count
                    templateVars["Description"] = jsonVars['LunBusyRetryCount']['description']
                    templateVars["varInput"] = 'Enter the number of times connection is to be attempted when the LUN ID is busy.'
                    templateVars["varDefault"] = 15
                    templateVars["varName"] = 'LUN Busy Retry Count'
                    templateVars["minNum"] = jsonVars['LunBusyRetryCount']['minimum']
                    templateVars["maxNum"] = jsonVars['LunBusyRetryCount']['maximum']
                    templateVars["lun_busy_retry_count"] = varNumberLoop(**templateVars)

                    # TCP Connection Timeout
                    templateVars["Description"] = jsonVars['ConnectionTimeOut']['description']
                    templateVars["varInput"] = 'Enter the number of seconds after which the TCP connection times out.'
                    templateVars["varDefault"] = 15
                    templateVars["varName"] = 'TCP Connection Timeout'
                    templateVars["minNum"] = jsonVars['ConnectionTimeOut']['minimum']
                    templateVars["maxNum"] = jsonVars['ConnectionTimeOut']['maximum']
                    templateVars["tcp_connection_timeout"] = varNumberLoop(**templateVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   dhcp_timeout           = {templateVars["dhcp_timeout"]}')
                    print(f'   description            = "{templateVars["descr"]}"')
                    print(f'   lun_busy_retry_count   = "{templateVars["lun_busy_retry_count"]}"')
                    print(f'   name                   = "{templateVars["name"]}"')
                    print(f'   tcp_connection_timeout = "{templateVars["tcp_connection_timeout"]}"')
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
    # iSCSI Boot Policy Module
    #==============================================
    def iscsi_boot_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'boot'
        org = self.org
        policy_type = 'iSCSI Boot Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'iscsi_boot_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to initialize the Operating System on FI-attached ')
            print(f'  blade and rack servers from a remote disk across a Storage Area Network. The remote disk, ')
            print(f'  known as the target, is accessed using TCP/IP and iSCSI boot firmware.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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

                    # Pull in the Policies for iSCSI Boot
                    jsonVars = jsonData['components']['schemas']['vnic.IscsiBootPolicy']['allOf'][1]['properties']
                    templateVars["multi_select"] = False

                    # Target Source Type
                    templateVars["var_description"] = jsonVars['TargetSourceType']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['TargetSourceType']['enum'])
                    templateVars["defaultVar"] = jsonVars['TargetSourceType']['default']
                    templateVars["varType"] = 'Target Source Type'
                    templateVars["target_source_type"] = variablesFromAPI(**templateVars)

                    if templateVars["target_source_type"] == 'Auto':
                        Authentication = 'none'
                        templateVars["initiator_ip_source"] = 'DHCP'
                        templateVars["primary_target_policy"] = ''
                        templateVars["secondary_target_policy"] = ''

                        templateVars["Description"] = jsonVars['AutoTargetvendorName']['description']
                        templateVars["varDefault"] = ''
                        templateVars["varInput"] = 'DHCP Vendor ID or IQN:'
                        templateVars["varName"] = 'DHCP Vendor ID or IQN'
                        templateVars["varRegex"] = '^[\\S]+$'
                        templateVars["minLength"] = 1
                        templateVars["maxLength"] = 32
                        templateVars["dhcp_vendor_id_iqn"] = varStringLoop(**templateVars)

                    elif templateVars["target_source_type"] == 'Static':
                        templateVars["optional_message"] = '  !!! Select the Primary Static Target !!!\n'
                        policy_list = [
                            'policies.iscsi_static_target_policies.iscsi_static_target_policy'
                        ]
                        templateVars["allow_opt_out"] = False
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            templateVars["primary_target_policy"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                            templateVars.update(policyData)

                        templateVars["optional_message"] = '  !!! Optionally Select the Secondary Static Target or enter 100 for no Secondary !!!\n'
                        policy_list = [
                            'policies.iscsi_static_target_policies.iscsi_static_target_policy'
                        ]
                        templateVars["allow_opt_out"] = True
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            templateVars["secondary_target_policy"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                            templateVars.update(policyData)

                        templateVars.pop("optional_message")
                        # Initiator IP Source
                        templateVars["var_description"] = jsonVars['InitiatorIpSource']['description']
                        templateVars["jsonVars"] = sorted(jsonVars['InitiatorIpSource']['enum'])
                        templateVars["defaultVar"] = jsonVars['InitiatorIpSource']['default']
                        templateVars["varType"] = 'Initiator IP Source'
                        templateVars["initiator_ip_source"] = variablesFromAPI(**templateVars)

                        if templateVars["initiator_ip_source"] == 'Pool':
                            templateVars["optional_message"] = '  !!! Initiator IP Pool !!!\n'
                            # Prompt User for the IP Pool
                            policy_list = [
                                'pools.ip_pools.ip_pool'
                            ]
                            templateVars["allow_opt_out"] = False
                            for policy in policy_list:
                                policy_short = policy.split('.')[2]
                                templateVars['ip_pool'],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                templateVars.update(policyData)
                            templateVars.pop("optional_message")

                        elif templateVars["initiator_ip_source"] == 'Static':
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(jsonVars['InitiatorStaticIpV4Config']['description'])
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                            jsonVars = jsonData['components']['schemas']['ippool.IpV4Config']['allOf'][1]['properties']
                            templateVars["Description"] = 'Static IP address provided for iSCSI Initiator.'
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'IP Address:'
                            templateVars["varName"] = f'IP Address'
                            templateVars["varRegex"] = jsonVars['Gateway']['pattern']
                            templateVars["minLength"] = 5
                            templateVars["maxLength"] = 15
                            ipAddress = varStringLoop(**templateVars)

                            templateVars["Description"] = jsonVars['Netmask']['description']
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'Subnet Mask:'
                            templateVars["varName"] = f'Subnet Mask'
                            templateVars["varRegex"] = jsonVars['Netmask']['pattern']
                            templateVars["minLength"] = 5
                            templateVars["maxLength"] = 15
                            subnetMask = varStringLoop(**templateVars)

                            templateVars["Description"] = jsonVars['Gateway']['description']
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'Default Gateway:'
                            templateVars["varName"] = f'Default Gateway'
                            templateVars["varRegex"] = jsonVars['Gateway']['pattern']
                            templateVars["minLength"] = 5
                            templateVars["maxLength"] = 15
                            defaultGateway = varStringLoop(**templateVars)

                            templateVars["Description"] = jsonVars['PrimaryDns']['description']
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'Primary DNS Server.  [press enter to skip]:'
                            templateVars["varName"] = f'Primary DNS Server'
                            templateVars["varRegex"] = jsonVars['PrimaryDns']['pattern']
                            templateVars["minLength"] = 5
                            templateVars["maxLength"] = 15
                            primaryDns = varStringLoop(**templateVars)

                            templateVars["Description"] = jsonVars['SecondaryDns']['description']
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'Secondary DNS Server.  [press enter to skip]:'
                            templateVars["varName"] = f'Secondary DNS Server'
                            templateVars["varRegex"] = jsonVars['SecondaryDns']['pattern']
                            templateVars["minLength"] = 5
                            templateVars["maxLength"] = 15
                            secondaryDns = varStringLoop(**templateVars)

                            templateVars["initiator_static_ip_v4_config"] = {
                                'ip_address':ipAddress,
                                'subnet_mask':subnetMask,
                                'default_gateway':defaultGateway,
                                'primary_dns':primaryDns,
                                'secondary_dns':secondaryDns,
                            }

                        # Type of Authentication
                        templateVars["var_description"] = 'Select Which Type of Authentication you want to Perform.'
                        templateVars["jsonVars"] = ['chap', 'mutual_chap', 'none']
                        templateVars["defaultVar"] = 'none'
                        templateVars["varType"] = 'Authentication Type'
                        Authentication = variablesFromAPI(**templateVars)

                        if re.search('chap', Authentication):
                            jsonVars = jsonData['components']['schemas']['vnic.IscsiAuthProfile']['allOf'][1]['properties']
                            auth_type = Authentication.replace('_', ' ')
                            auth_type = auth_type.capitalize()

                            templateVars["Description"] = jsonVars['UserId']['description']
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'{auth_type} Username:'
                            templateVars["varName"] = f'{auth_type} Username'
                            templateVars["varRegex"] = jsonVars['UserId']['pattern']
                            templateVars["minLength"] = 1
                            templateVars["maxLength"] = 128
                            user_id = varStringLoop(**templateVars)

                            templateVars["Description"] = jsonVars['Password']['description']
                            templateVars["varDefault"] = ''
                            templateVars["varInput"] = f'{auth_type} Password:'
                            templateVars["varName"] = f'{auth_type} Password'
                            templateVars["varRegex"] = jsonVars['Password']['pattern']
                            templateVars["minLength"] = 12
                            templateVars["maxLength"] = 16
                            iscsi_boot_password = varSensitiveStringLoop(**templateVars)
                            os.environ['TF_VAR_iscsi_boot_password'] = '%s' % (iscsi_boot_password)
                            password = 1

                            templateVars[Authentication] = {
                                'password':password,
                                'user_id':user_id
                            }

                    # Prompt User for the iSCSI Adapter Policy
                    policy_list = [
                        'policies.iscsi_adapter_policies.iscsi_adapter_policy'
                    ]
                    templateVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        templateVars.update(policyData)


                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    if 'chap' in Authentication:
                        print(f'   authentication      = "Authentication"')
                    print(f'   description         = "{templateVars["descr"]}"')
                    if templateVars["target_source_type"] == 'Auto':
                        print(f'   dhcp_vendor_id_iqn  = "{templateVars["dhcp_vendor_id_iqn"]}"')
                    if templateVars["initiator_ip_source"] == 'Pool':
                        print(f'   initiator_ip_pool   = "{templateVars["ip_pool"]}"')
                    print(f'   initiator_ip_source = "{templateVars["initiator_ip_source"]}"')
                    if templateVars.get('initiator_static_ip_v4_config'):
                        print(f'   initiator_static_ip_v4_config = ''{')
                        print(f'     default_gateway = "{templateVars["initiator_static_ip_v4_config"]["default_gateway"]}"')
                        print(f'     ip_address      = "{templateVars["initiator_static_ip_v4_config"]["ip_address"]}"')
                        print(f'     primary_dns     = "{templateVars["initiator_static_ip_v4_config"]["primary_dns"]}"')
                        print(f'     secondary_dns   = "{templateVars["initiator_static_ip_v4_config"]["secondary_dns"]}"')
                        print(f'     subnet_mask     = "{templateVars["initiator_static_ip_v4_config"]["subnet_mask"]}"')
                        print(f'   ''}')
                    print(f'   iscsi_adapter_policy    = "{templateVars["iscsi_adapter_policy"]}"')
                    print(f'   name                    = "{templateVars["name"]}"')
                    if 'chap' in Authentication:
                        print(f'   password                = {password}')
                    print(f'   primary_target_policy   = "{templateVars["primary_target_policy"]}"')
                    print(f'   secondary_target_policy = "{templateVars["secondary_target_policy"]}"')
                    print(f'   target_source_type      = "{templateVars["target_source_type"]}"')
                    if 'chap' in Authentication:
                        print(f'   username                = {user_id}')
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
    # iSCSI Static Target Policy Module
    #==============================================
    def iscsi_static_target_policies(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'target'
        org = self.org
        policy_type = 'iSCSI Static Target Policy'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'iscsi_static_target_policies'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to specify the name, IP address, port, and ')
            print(f'  logical unit number of the primary target for iSCSI boot. You can optionally specify these ')
            print(f'  details for a secondary target as well.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
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

                    # Pull in the Policies for iSCSI Static Target
                    jsonVars = jsonData['components']['schemas']['vnic.IscsiStaticTargetPolicy']['allOf'][1]['properties']

                    desc_add = '\n  such as:\n  * iqn.1984-12.com.cisco:lnx1\n  * iqn.1984-12.com.cisco:win-server1'
                    # Target Name
                    templateVars["Description"] = jsonVars['TargetName']['description'] + desc_add
                    templateVars["varDefault"] = ''
                    templateVars["varInput"] = 'Enter the name of the target:'
                    templateVars["varName"] = 'Target Name'
                    templateVars["varRegex"] = jsonVars['TargetName']['pattern']
                    templateVars["minLength"] = 1
                    templateVars["maxLength"] = 255
                    templateVars["target_name"] = varStringLoop(**templateVars)

                    # IP Address
                    templateVars["Description"] = jsonVars['IpAddress']['description']
                    templateVars["varDefault"] = ''
                    templateVars["varInput"] = 'Enter the target IP address:'
                    templateVars["varName"] = 'IP Address'
                    templateVars["varRegex"] = jsonVars['IpAddress']['pattern']
                    templateVars["minLength"] = 5
                    templateVars["maxLength"] = 15
                    templateVars["ip_address"] = varStringLoop(**templateVars)

                    # Port
                    templateVars["Description"] = jsonVars['Port']['description']
                    templateVars["varInput"] = 'Enter the port number of the target.'
                    templateVars["varDefault"] = 3260
                    templateVars["varName"] = 'Port'
                    templateVars["minNum"] = jsonVars['Port']['minimum']
                    templateVars["maxNum"] = jsonVars['Port']['maximum']
                    templateVars["port"] = varNumberLoop(**templateVars)

                    # LUN Identifier
                    templateVars["Description"] = jsonVars['Lun']['description']
                    templateVars["varInput"] = 'Enter the ID of the boot logical unit number.'
                    templateVars["varDefault"] = 0
                    templateVars["varName"] = 'LUN Identifier'
                    templateVars["minNum"] = 0
                    templateVars["maxNum"] = 1024
                    templateVars["lun_id"] = varNumberLoop(**templateVars)

                    # LUN Bootable
                    templateVars["Description"] = jsonVars['Lun']['description']
                    templateVars["varInput"] = f'Should LUN {templateVars["lun_id"]} be bootable?'
                    templateVars["varDefault"] = 'Y'
                    templateVars["varName"] = 'LUN Identifier'
                    templateVars["bootable"] = varBoolLoop(**templateVars)

                    templateVars["lun"] = {
                        'bootable':templateVars["bootable"],
                        'lun_id':templateVars["lun_id"]
                    }
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   description = "{templateVars["descr"]}"')
                    print(f'   ip_address  = "{templateVars["ip_address"]}"')
                    print(f'   name        = "{templateVars["name"]}"')
                    print(f'   port        = {templateVars["port"]}')
                    print(f'   target_name = "{templateVars["target_name"]}"')
                    print(f'   lun = [')
                    print(f'     ''{')
                    print(f'       bootable = {templateVars["lun"]["bootable"]}')
                    print(f'       lun_id   = {templateVars["lun"]["lun_id"]}')
                    print(f'     ''}')
                    print(f'   ]')
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
    # LAN Connectivity Policy Module
    #==============================================
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
            print(f'  This wizard will save the configuration for this section to the following file:')
            print(f'  - Intersight/{org}/{self.type}/{templateVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                loop_count = 1
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, 'lancon')
                    else:
                        name = '%s_%s' % (org, 'lancon')

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['vnic.LanConnectivityPolicy']['allOf'][1]['properties']

                    templateVars["var_description"] = jsonVars['TargetPlatform']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    templateVars["defaultVar"] = 'FIAttached'
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

                    global_name = templateVars["name"]
                    print(f'\n-----------------------------------------------------------------------------------------------\n')
                    print(f'Easy IMM will now begin the vNIC Configuration Process.  We recommend the following guidlines:')
                    print(f'  - For Baremetal Operating Systems like Linux and Windows; use a Failover Policy with a single vnic')
                    print(f'  - For a Virtual Environment it is a Good Practice to not use Failover and use the following')
                    print(f'    vnic layout:')
                    print(f'    1. Management')
                    print(f'    2. Migration/vMotion')
                    print(f'    3. Storage')
                    print(f'    4. Virtual Machines')
                    print(f'If you select no for Failover Policy the script will create mirroring vnics for A and B')
                    print(f'\n-----------------------------------------------------------------------------------------------\n')
                    inner_loop_count = 1
                    pci_order_consumed = [{0:[]},{1:[]}]
                    templateVars["vnics"] = []
                    vnic_loop = False
                    while vnic_loop == False:
                        jsonVars = jsonData['components']['schemas']['vnic.EthIf']['allOf'][1]['properties']

                        templateVars["Description"] = jsonVars['FailoverEnabled']['description']
                        templateVars["varInput"] = f'Do you want to Enable Failover for this vNIC?'
                        templateVars["varDefault"] = 'N'
                        templateVars["varName"] = 'Enable Failover'
                        templateVars["enable_failover"] = varBoolLoop(**templateVars)

                        print(f' inner loop count is {inner_loop_count}')
                        if templateVars["enable_failover"] == True:
                            fabrics = ['A']
                            templateVars["varDefault"] = 'vnic'
                        else:
                            fabrics = ['A','B']
                            if inner_loop_count < 5:
                                numValue = inner_loop_count -1
                                templateVars["varDefault"] = name_suffix[numValue]
                            else:
                                templateVars["varDefault"] = 'vnic'
                        templateVars["Description"] = jsonVars['Name']['description']
                        templateVars["varInput"] = f'What is the name for this vNIC? [{templateVars["varDefault"]}]:'
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
                            templateVars[f"mac_address_allocation_type"] = variablesFromAPI(**templateVars)

                            if templateVars[f"mac_address_allocation_type"] == 'POOL':
                                for x in fabrics:
                                    templateVars["name"] = templateVars[f"name_{x}"]
                                    policy_list = [
                                        'pools.mac_pools.mac_pool',
                                    ]
                                    templateVars["allow_opt_out"] = False
                                    for policy in policy_list:
                                        templateVars[f"static_mac_{x}"] = ''
                                        if templateVars["enable_failover"] == False:
                                            templateVars["optional_message"] = f'MAC Address Pool for Fabric {x}'
                                        policy_short = policy.split('.')[2]
                                        templateVars[f'mac_pool_{x}'],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                                        templateVars.update(policyData)
                                    templateVars.pop('optional_message')
                            else:
                                for x in fabrics:
                                    templateVars[f'mac_pool_{x}'] = ''
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
                                    templateVars[f"static_mac_{x}"] = varStringLoop(**templateVars)

                        # Pull in API Attributes
                        jsonVars = jsonData['components']['schemas']['vnic.PlacementSettings']['allOf'][1]['properties']

                        for x in fabrics:
                            templateVars["var_description"] = jsonVars['PciLink']['description']
                            if templateVars["enable_failover"] == False:
                                templateVars["var_description"] = templateVars["var_description"] + f'\n\nPCI Link For Fabric {x}'
                            templateVars["jsonVars"] = [0, 1]
                            templateVars["defaultVar"] = jsonVars['PciLink']['default']
                            if templateVars["enable_failover"] == True:
                                templateVars["varType"] = 'PCI Link'
                            else:
                                templateVars["varType"] = f'Fabric {x} PCI Link'
                            templateVars[f"pci_link_{x}"] = variablesFromAPI(**templateVars)
                            print(templateVars[f"pci_link_{x}"])

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
                                if len(pci_order_consumed[0][templateVars[f"pci_link_{x}"]]) > 0:
                                    templateVars["varDefault"] = len(pci_order_consumed[0][templateVars[f"pci_link_{x}"]])
                                else:
                                    templateVars["varDefault"] = 0
                                templateVars["varName"] = 'PCI Order'
                                templateVars["minNum"] = 0
                                templateVars["maxNum"] = 255
                                templateVars[f"pci_order_{x}"] = varNumberLoop(**templateVars)

                                consumed_count = 0
                                for i in pci_order_consumed[0][templateVars[f"pci_link_{x}"]]:
                                    if int(i) == int(templateVars[f"pci_order_{x}"]):
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! PCI Order "{templateVars[f"PciOrder_{x}"]}" is already in use.  Please use an alternative.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        consumed_count += 1

                                if consumed_count == 0:
                                    pci_order_consumed[0][templateVars[f"pci_link_{x}"]].append(templateVars[f"pci_order_{x}"])
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

                        templateVars["name"] = templateVars["name"].split('-')[0]
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
                                    templateVars[f"vnic_fabric_{x}"].update({'mac_address_pool':templateVars[f"mac_pool_{x}"]})
                                else:
                                    templateVars[f"vnic_fabric_{x}"].update({'mac_address_static':templateVars[f"static_mac_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'name':templateVars[f"name_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'pci_link':templateVars[f"pci_link_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'pci_order':templateVars[f"pci_order_{x}"]})
                            templateVars[f"vnic_fabric_{x}"].update({'slot_id':templateVars[f"slot_id"]})
                            if templateVars["target_platform"] == 'FIAttached':
                                templateVars[f"vnic_fabric_{x}"].update({'switch_id':f"{x}"})
                            else:
                                templateVars[f"vnic_fabric_{x}"].update({'uplink_port':templateVars[f"uplink_port_{x}"]})

                        templateVars["name"] = global_name
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        for x in fabrics:
                            if templateVars["enable_failover"] == False:
                                print(f'Fabric {x}:')
                            for k, v in templateVars[f"vnic_fabric_{x}"].items():
                                if k == 'cdn_source':
                                    print(f'    cdn_source                      = "{v}"')
                                elif k == 'cdn_value':
                                    print(f'    cdn_value                       = "{v}"')
                                elif k == 'enable_failover':
                                    print(f'    enable_failover                 = {v}')
                                elif k == 'ethernet_adapter_policy':
                                    print(f'    ethernet_adapter_policy         = "{v}"')
                                elif k == 'ethernet_network_control_policy':
                                    print(f'    ethernet_network_control_policy = "{v}"')
                                elif k == 'ethernet_network_group_policy':
                                    print(f'    ethernet_network_group_policy   = "{v}"')
                                elif k == 'ethernet_network_policy':
                                    print(f'    ethernet_network_policy         = "{v}"')
                                elif k == 'ethernet_qos_policy':
                                    print(f'    ethernet_qos_policy             = "{v}"')
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
                                    if inner_loop_count < 4:
                                        loop_exit = input(f'Would You like to Configure another vNIC?  Enter "Y" or "N" [Y]: ')
                                    else:
                                        loop_exit = input(f'Would You like to Configure another vNIC?  Enter "Y" or "N" [N]: ')
                                    if loop_exit == 'Y' or (inner_loop_count < 4 and loop_exit == ''):
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
                    print(f'    description                 = {templateVars["descr"]}')
                    if templateVars["target_platform"] == 'FIAttached':
                        print(f'    enable_azure_stack_host_qos = {templateVars["enable_azure_stack_host_qos"]}')
                    if not templateVars["iqn_allocation_type"] == 'None':
                        print(f'    iqn_allocation_type         = "{templateVars["iqn_allocation_type"]}"')
                    if templateVars["iqn_allocation_type"] == 'Pool':
                        print(f'    iqn_pool                    = "{templateVars["iqn_pool"]}"')
                    if templateVars["iqn_allocation_type"] == 'Static':
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
                                    print(f'        enable_failover                 = {v}')
                                elif k == 'ethernet_adapter_policy':
                                    print(f'        ethernet_adapter_policy         = "{v}"')
                                elif k == 'ethernet_network_control_policy':
                                    print(f'        ethernet_network_control_policy = "{v}"')
                                elif k == 'ethernet_network_group_policy':
                                    print(f'        ethernet_network_group_policy   = "{v}"')
                                elif k == 'ethernet_network_policy':
                                    print(f'        ethernet_network_policy         = "{v}"')
                                elif k == 'ethernet_qos_policy':
                                    print(f'    ethernet_qos_policy             = "{v}"')
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
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There were no {policy_description} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

                if 'Policies' in policy_description:
                    policy_description = policy_description.replace('Policies', 'Policy')
                elif 'Pools' in policy_description:
                    policy_description = policy_description.replace('Pools', 'Pool')
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
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {inner_policy}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            if inner_policy == 'iqn_pools':
                pools(name_prefix, templateVars["org"], inner_type).iqn_pools(jsonData, easy_jsonData)
            elif inner_policy == 'mac_pools':
                pools(name_prefix, templateVars["org"], inner_type).mac_pools(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_adapter_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).ethernet_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_network_control_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).ethernet_network_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_network_group_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).ethernet_network_group_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_network_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).ethernet_network_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ethernet_qos_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).ethernet_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_adapter_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).iscsi_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_boot_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).iscsi_boot_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_static_target_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).iscsi_static_target_policies(jsonData, easy_jsonData)
            elif inner_policy == 'system_qos_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).system_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'vlan_policies':
                policies_vxan(name_prefix, templateVars["org"], inner_type).vlan_policies(jsonData, easy_jsonData)
