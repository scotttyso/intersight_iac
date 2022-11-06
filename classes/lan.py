import p3
import vxan
import pools
import ezfunctions
import jinja2
import os
import pkg_resources
import platform
import re
import subprocess
import validating

ucs_template_path = pkg_resources.resource_filename('lan', '../templates/')

class policies(object):
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
    def ethernet_adapter_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Ethernet Adapter Policy'
        policy_x = 'Ethernet Adapter'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["name_prefix"] = name_prefix
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ethernet_adapter_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  {policy_x} Policies:  To simplify your work, this wizard will use {policy_x}')
            print(f'  Templates that are pre-configured.  You can add custom {policy_x} policy')
            print(f'  configuration to the {polVars["template_type"]}.auto.tfvars file at your descretion.')
            print(f'  That will not be covered by this wizard as the focus of the wizard is on simplicity.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    polVars["multi_select"] = False
                    jsonVars = easy_jsonData['policies']['vnic.EthNetworkPolicy']
                    polVars["var_description"] = jsonVars['templates']['description']
                    polVars["jsonVars"] = sorted(jsonVars['templates']['enum'])
                    polVars["defaultVar"] = jsonVars['templates']['default']
                    polVars["varType"] = 'Ethernet Adapter Template'
                    polVars["policy_template"] = ezfunctions.variablesFromAPI(**polVars)

                    if not polVars["name_prefix"] == '':
                        name = '%s_%s' % (polVars["name_prefix"], polVars["policy_template"])
                    else:
                        name = '%s_%s' % (polVars["org"], polVars["policy_template"])

                    polVars["name"] = ezfunctions.policy_name(name, polVars["policy_type"])
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], polVars["policy_type"])

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   adapter_template = "{polVars["policy_template"]}"')
                    print(f'   description      = "{polVars["descr"]}"')
                    print(f'   name             = "{polVars["name"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                        if confirm_policy == 'Y' or confirm_policy == '':
                            confirm_policy = 'Y'

                            # Write Policies to Template File
                            polVars["template_file"] = '%s.jinja2' % ('ethernet_adapter_templates')
                            ezfunctions.write_to_template(self, **polVars)

                            configure_loop, policy_loop = ezfunctions.exit_default_yes(polVars["policy_type"])
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

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Ethernet Network Control Policy Module
    #==============================================
    def ethernet_network_control_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'netwk_ctrl'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Ethernet Network Control Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ethernet_network_control_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} will allow you to control Network Discovery with ')
            print(f'  protocols like CDP and LLDP as well as MAC Address Control Features.\n')
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
                polVars["action_on_uplink_fail"] = 'linkDown'

                valid = False
                while valid == False:
                    cdp = input('Do you want to enable CDP (Cisco Discovery Protocol) for this Policy?  Enter "Y" or "N" [Y]: ')
                    if cdp == '' or cdp == 'Y':
                        polVars["cdp_enable"] = True
                        valid = True
                    elif cdp == 'N':
                        polVars["cdp_enable"] = False
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Option.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                valid = False
                while valid == False:
                    cdp = input('Do you want to enable LLDP (Link Level Discovery Protocol) for this Policy?  Enter "Y" or "N" [Y]: ')
                    if cdp == '' or cdp == 'Y':
                        polVars["lldp_receive_enable"] = True
                        polVars["lldp_transmit_enable"] = True
                        valid = True
                    elif cdp == 'N':
                        polVars["lldp_receive_enable"] = False
                        polVars["lldp_transmit_enable"] = False
                        valid = True
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Error!! Invalid Option.  Please enter "Y" or "N".')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                polVars["multi_select"] = False
                jsonVars = jsonData['components']['schemas']['fabric.EthNetworkControlPolicy']['allOf'][1]['properties']
                polVars["var_description"] = jsonVars['MacRegistrationMode']['description']
                polVars["jsonVars"] = sorted(jsonVars['MacRegistrationMode']['enum'])
                polVars["defaultVar"] = jsonVars['MacRegistrationMode']['default']
                polVars["varType"] = 'MAC Registration Mode'
                polVars["mac_register_mode"] = ezfunctions.variablesFromAPI(**polVars)

                polVars["var_description"] = jsonVars['ForgeMac']['description']
                polVars["jsonVars"] = sorted(jsonVars['ForgeMac']['enum'])
                polVars["defaultVar"] = jsonVars['ForgeMac']['default']
                polVars["varType"] = 'MAC Security Forge'
                polVars["mac_security_forge"] = ezfunctions.variablesFromAPI(**polVars)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    action_on_uplink_fail = "{polVars["action_on_uplink_fail"]}"')
                print(f'    cdp_enable            = {polVars["cdp_enable"]}')
                print(f'    description           = "{polVars["descr"]}"')
                print(f'    lldp_enable_receive   = {polVars["lldp_receive_enable"]}')
                print(f'    lldp_enable_transmit  = {polVars["lldp_transmit_enable"]}')
                print(f'    mac_register_mode     = "{polVars["mac_register_mode"]}"')
                print(f'    mac_security_forge    = "{polVars["mac_security_forge"]}"')
                print(f'    name                  = "{polVars["name"]}"')
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
    # Ethernet Network Group Policy Module
    #==============================================
    def ethernet_network_group_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = ['Management', 'Migration', 'Storage', 'VMs']
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Ethernet Network Group Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ethernet_network_group_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

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
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
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

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)
                polVars["action_on_uplink_fail"] = 'linkDown'

                policy_list = [
                    'policies.vlan_policies.vlan_policy',
                ]
                polVars["allow_opt_out"] = False
                for policy in policy_list:
                    vlan_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
                
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

                vlan_list = ezfunctions.vlan_list_full(vlan_convert)

                valid = False
                while valid == False:
                    VlanList = input('Enter the VLAN or List of VLANs to add to this VLAN Group: ')
                    if not VlanList == '':
                        vlanListExpanded = ezfunctions.vlan_list_full(VlanList)

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

                polVars["allowed_vlans"] = VlanList
                if not nativeVlan == '':
                    polVars["native_vlan"] = nativeVlan
                else:
                    polVars["native_vlan"] = ''
                    polVars.pop('native_vlan')

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    allowed_vlans = "{polVars["allowed_vlans"]}"')
                print(f'    description   = "{polVars["descr"]}"')
                print(f'    name          = "{polVars["name"]}"')
                if not nativeVlan == '':
                    print(f'    native_vlan   = {polVars["native_vlan"]}')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the configuration above?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **polVars)

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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Ethernet Network Policy Module
    #==============================================
    def ethernet_network_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'network'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Ethernet Network Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ethernet_network_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  An {policy_type} determines if the port can carry single VLAN (Access) ')
            print(f'  or multiple VLANs (Trunk) traffic. You can specify the VLAN to be associated with an ')
            print(f'  Ethernet packet if no tag is found.\n\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure an {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['vnic.VlanSettings']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['Mode']['description']
                    polVars["jsonVars"] = sorted(jsonVars['Mode']['enum'])
                    polVars["defaultVar"] = jsonVars['Mode']['default']
                    polVars["varType"] = 'VLAN Mode'
                    polVars["vlan_mode"] = ezfunctions.variablesFromAPI(**polVars)

                    valid = False
                    while valid == False:
                        polVars["default_vlan"] = input('What is the default vlan to assign to this Policy.  Range is 0 to 4094: ')
                        if re.fullmatch(r'[0-9]{1,4}', polVars["default_vlan"]):
                            valid = validating.number_in_range('VLAN ID', polVars["default_vlan"], 0, 4094)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    default_vlan  = {polVars["default_vlan"]}')
                    print(f'    description   = "{polVars["descr"]}"')
                    print(f'    name          = "{polVars["name"]}"')
                    print(f'    vlan_mode     = "{polVars["vlan_mode"]}"')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    valid_confirm = False
                    while valid_confirm == False:
                        confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
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

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Ethernet QoS Policy Module
    #==============================================
    def ethernet_qos_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = ['Management', 'Migration', 'Storage', 'VMs']
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'Ethernet QoS Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ethernet_qos_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

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
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')

            polVars["multi_select"] = False
            jsonVars = jsonData['components']['schemas']['vnic.EthNetworkPolicy']['allOf'][1]['properties']
            polVars["var_description"] = jsonVars['TargetPlatform']['description']
            polVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
            polVars["defaultVar"] = 'FIAttached'
            polVars["varType"] = 'Target Platform'
            polVars["target_platform"] = ezfunctions.variablesFromAPI(**polVars)

            loop_count = 0
            policy_loop = False
            while policy_loop == False:

                name = ''
                if polVars["target_platform"] == 'FIAttached':
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

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    Enable Trust Host CoS enables the VIC to Pass thru the CoS value recieved from the Host.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid = False
                while valid == False:
                    question = input(f'Do you want to Enable Trust Host based CoS?  Enter "Y" or "N" [N]: ')
                    if question == '' or question == 'N':
                        polVars["enable_trust_host_cos"] = False
                        valid = True
                    elif question == 'Y':
                        polVars["enable_trust_host_cos"] = True
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
                        polVars["varName"] = 'Rate Limit'
                        varValue = Question
                        valid = validating.number_in_range(polVars["varName"], varValue, minValue, maxValue)
                    else:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'    Invalid Rate Limit value "{Question}"!!!')
                        print(f'    The valid range is between 0 and 100000. The default value is 0.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')

                polVars["rate_limit"] = Question

                if polVars["target_platform"] == 'Standalone':
                    polVars["burst"] = 1024
                    polVars["priority"] = 'Best Effort'
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
                            polVars["varName"] = 'Class of Service'
                            varValue = Question
                            valid = validating.number_in_range(polVars["varName"], varValue, minValue, maxValue)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    Invalid Class of Service value "{Question}"!!!')
                            print(f'    The valid range is between 0 and 6. The default value is 0.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    polVars["cos"] = Question

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
                            polVars["varName"] = 'MTU'
                            varValue = Question
                            valid = validating.number_in_range(polVars["varName"], varValue, minValue, maxValue)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    Invalid MTU value "{Question}"!!!')
                            print(f'    The valid range is between 1500 and 9000. The default value is 1500.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    polVars["mtu"] = Question

                else:
                    polVars["cos"] = 0
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
                            polVars["varName"] = 'Burst'
                            varValue = Question
                            valid = validating.number_in_range(polVars["varName"], varValue, minValue, maxValue)
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'    Invalid Burst value "{Question}"!!!')
                            print(f'    The valid range is between 1024 and 1000000. The default value is 1024.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    polVars["burst"] = Question

                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['vnic.EthQosPolicy']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['Priority']['description']
                    polVars["jsonVars"] = sorted(jsonVars['Priority']['enum'])
                    polVars["defaultVar"] = jsonVars['Priority']['default']
                    polVars["varType"] = '%s QoS Priority' % (polVars["name"])
                    polVars["priority"] = ezfunctions.variablesFromAPI(**polVars)

                    if loop_count == 0:
                        if polVars["target_platform"] == 'FIAttached':
                            policy_list = [
                                'policies.system_qos_policies.system_qos_policy',
                            ]
                            polVars["allow_opt_out"] = False
                            for policy in policy_list:
                                system_qos_policy,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)

                    mtu = policyData['system_qos_policies'][0][system_qos_policy][0]['classes'][0][polVars["priority"]][0]['mtu']
                    if mtu > 8999:
                        polVars["mtu"] = 9000
                    else:
                        polVars["mtu"] = mtu

                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  ')
                if polVars["target_platform"] == 'FIAttached':
                    print(f'   burst                 = {polVars["burst"]}')
                if polVars["target_platform"] == 'Standalone':
                    print(f'   cos                   = {polVars["cos"]}')
                print(f'   description           = "{polVars["descr"]}"')
                print(f'   enable_trust_host_cos = {polVars["enable_trust_host_cos"]}')
                print(f'   mtu                   = {polVars["mtu"]}')
                print(f'   name                  = "{polVars["name"]}"')
                if polVars["target_platform"] == 'FIAttached':
                    print(f'   priority              = "{polVars["priority"]}"')
                print(f'   rate_limit            = {polVars["rate_limit"]}')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                valid_confirm = False
                while valid_confirm == False:
                    confirm_policy = input('Do you want to accept the above configuration?  Enter "Y" or "N" [Y]: ')
                    if confirm_policy == 'Y' or confirm_policy == '':
                        confirm_policy = 'Y'

                        # Write Policies to Template File
                        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                        ezfunctions.write_to_template(self, **polVars)

                        valid_exit = False
                        while valid_exit == False:
                            if loop_count < 3 and polVars["target_platform"] == 'FIAttached':
                                exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [Y]: ')
                            else:
                                exit_answer = input(f'Would You like to Configure another {policy_type}?  Enter "Y" or "N" [N]: ')
                            if loop_count < 3 and exit_answer == '' and polVars["target_platform"] == 'FIAttached':
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
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # iSCSI Adapter Policy Module
    #==============================================
    def iscsi_adapter_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'adapter'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'iSCSI Adapter Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'iscsi_adapter_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to configure values for TCP Connection Timeout, ')
            print(f'  DHCP Timeout, and the Retry Count if the specified LUN ID is busy.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    # Pull in the Policies for iSCSI Adapter
                    jsonVars = jsonData['components']['schemas']['vnic.IscsiAdapterPolicy']['allOf'][1]['properties']

                    # DHCP Timeout
                    polVars["Description"] = jsonVars['DhcpTimeout']['description']
                    polVars["varInput"] = 'Enter the number of seconds after which the DHCP times out.'
                    polVars["varDefault"] = 60
                    polVars["varName"] = 'DHCP Timeout'
                    polVars["minNum"] = jsonVars['DhcpTimeout']['minimum']
                    polVars["maxNum"] = jsonVars['DhcpTimeout']['maximum']
                    polVars["dhcp_timeout"] = ezfunctions.varNumberLoop(**polVars)

                    # LUN Busy Retry Count
                    polVars["Description"] = jsonVars['LunBusyRetryCount']['description']
                    polVars["varInput"] = 'Enter the number of times connection is to be attempted when the LUN ID is busy.'
                    polVars["varDefault"] = 15
                    polVars["varName"] = 'LUN Busy Retry Count'
                    polVars["minNum"] = jsonVars['LunBusyRetryCount']['minimum']
                    polVars["maxNum"] = jsonVars['LunBusyRetryCount']['maximum']
                    polVars["lun_busy_retry_count"] = ezfunctions.varNumberLoop(**polVars)

                    # TCP Connection Timeout
                    polVars["Description"] = jsonVars['ConnectionTimeOut']['description']
                    polVars["varInput"] = 'Enter the number of seconds after which the TCP connection times out.'
                    polVars["varDefault"] = 15
                    polVars["varName"] = 'TCP Connection Timeout'
                    polVars["minNum"] = jsonVars['ConnectionTimeOut']['minimum']
                    polVars["maxNum"] = jsonVars['ConnectionTimeOut']['maximum']
                    polVars["tcp_connection_timeout"] = ezfunctions.varNumberLoop(**polVars)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   dhcp_timeout           = {polVars["dhcp_timeout"]}')
                    print(f'   description            = "{polVars["descr"]}"')
                    print(f'   lun_busy_retry_count   = "{polVars["lun_busy_retry_count"]}"')
                    print(f'   name                   = "{polVars["name"]}"')
                    print(f'   tcp_connection_timeout = "{polVars["tcp_connection_timeout"]}"')
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

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # iSCSI Boot Policy Module
    #==============================================
    def iscsi_boot_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'boot'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'iSCSI Boot Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'iscsi_boot_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to initialize the Operating System on FI-attached ')
            print(f'  blade and rack servers from a remote disk across a Storage Area Network. The remote disk, ')
            print(f'  known as the target, is accessed using TCP/IP and iSCSI boot firmware.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    # Pull in the Policies for iSCSI Boot
                    jsonVars = jsonData['components']['schemas']['vnic.IscsiBootPolicy']['allOf'][1]['properties']
                    polVars["multi_select"] = False

                    # Target Source Type
                    polVars["var_description"] = jsonVars['TargetSourceType']['description']
                    polVars["jsonVars"] = sorted(jsonVars['TargetSourceType']['enum'])
                    polVars["defaultVar"] = jsonVars['TargetSourceType']['default']
                    polVars["varType"] = 'Target Source Type'
                    polVars["target_source_type"] = ezfunctions.variablesFromAPI(**polVars)

                    if polVars["target_source_type"] == 'Auto':
                        Authentication = 'none'
                        polVars["initiator_ip_source"] = 'DHCP'
                        polVars["primary_target_policy"] = ''
                        polVars["secondary_target_policy"] = ''

                        polVars["Description"] = jsonVars['AutoTargetvendorName']['description']
                        polVars["varDefault"] = ''
                        polVars["varInput"] = 'DHCP Vendor ID or IQN:'
                        polVars["varName"] = 'DHCP Vendor ID or IQN'
                        polVars["varRegex"] = '^[\\S]+$'
                        polVars["minLength"] = 1
                        polVars["maxLength"] = 32
                        polVars["dhcp_vendor_id_iqn"] = ezfunctions.varStringLoop(**polVars)

                    elif polVars["target_source_type"] == 'Static':
                        polVars["optional_message"] = '  !!! Select the Primary Static Target !!!\n'
                        policy_list = [
                            'policies.iscsi_static_target_policies.iscsi_static_target_policy'
                        ]
                        polVars["allow_opt_out"] = False
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            polVars["primary_target_policy"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
                            polVars.update(policyData)

                        polVars["optional_message"] = '  !!! Optionally Select the Secondary Static Target or enter 100 for no Secondary !!!\n'
                        policy_list = [
                            'policies.iscsi_static_target_policies.iscsi_static_target_policy'
                        ]
                        polVars["allow_opt_out"] = True
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            polVars["secondary_target_policy"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
                            polVars.update(policyData)

                        polVars.pop("optional_message")
                        # Initiator IP Source
                        polVars["var_description"] = jsonVars['InitiatorIpSource']['description']
                        polVars["jsonVars"] = sorted(jsonVars['InitiatorIpSource']['enum'])
                        polVars["defaultVar"] = jsonVars['InitiatorIpSource']['default']
                        polVars["varType"] = 'Initiator IP Source'
                        polVars["initiator_ip_source"] = ezfunctions.variablesFromAPI(**polVars)

                        if polVars["initiator_ip_source"] == 'Pool':
                            polVars["optional_message"] = '  !!! Initiator IP Pool !!!\n'
                            # Prompt User for the IP Pool
                            policy_list = [
                                'pools.ip_pools.ip_pool'
                            ]
                            polVars["allow_opt_out"] = False
                            for policy in policy_list:
                                policy_short = policy.split('.')[2]
                                polVars['ip_pool'],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
                                polVars.update(policyData)
                            polVars.pop("optional_message")

                        elif polVars["initiator_ip_source"] == 'Static':
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(jsonVars['InitiatorStaticIpV4Config']['description'])
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                            jsonVars = jsonData['components']['schemas']['ippool.IpV4Config']['allOf'][1]['properties']
                            polVars["Description"] = 'Static IP address provided for iSCSI Initiator.'
                            polVars["varDefault"] = ''
                            polVars["varInput"] = f'IP Address:'
                            polVars["varName"] = f'IP Address'
                            polVars["varRegex"] = jsonVars['Gateway']['pattern']
                            polVars["minLength"] = 5
                            polVars["maxLength"] = 15
                            ipAddress = ezfunctions.varStringLoop(**polVars)

                            polVars["Description"] = jsonVars['Netmask']['description']
                            polVars["varDefault"] = ''
                            polVars["varInput"] = f'Subnet Mask:'
                            polVars["varName"] = f'Subnet Mask'
                            polVars["varRegex"] = jsonVars['Netmask']['pattern']
                            polVars["minLength"] = 5
                            polVars["maxLength"] = 15
                            subnetMask = ezfunctions.varStringLoop(**polVars)

                            polVars["Description"] = jsonVars['Gateway']['description']
                            polVars["varDefault"] = ''
                            polVars["varInput"] = f'Default Gateway:'
                            polVars["varName"] = f'Default Gateway'
                            polVars["varRegex"] = jsonVars['Gateway']['pattern']
                            polVars["minLength"] = 5
                            polVars["maxLength"] = 15
                            defaultGateway = ezfunctions.varStringLoop(**polVars)

                            polVars["Description"] = jsonVars['PrimaryDns']['description']
                            polVars["varDefault"] = ''
                            polVars["varInput"] = f'Primary DNS Server.  [press enter to skip]:'
                            polVars["varName"] = f'Primary DNS Server'
                            polVars["varRegex"] = jsonVars['PrimaryDns']['pattern']
                            polVars["minLength"] = 5
                            polVars["maxLength"] = 15
                            primaryDns = ezfunctions.varStringLoop(**polVars)

                            polVars["Description"] = jsonVars['SecondaryDns']['description']
                            polVars["varDefault"] = ''
                            polVars["varInput"] = f'Secondary DNS Server.  [press enter to skip]:'
                            polVars["varName"] = f'Secondary DNS Server'
                            polVars["varRegex"] = jsonVars['SecondaryDns']['pattern']
                            polVars["minLength"] = 5
                            polVars["maxLength"] = 15
                            secondaryDns = ezfunctions.varStringLoop(**polVars)

                            polVars["initiator_static_ip_v4_config"] = {
                                'ip_address':ipAddress,
                                'subnet_mask':subnetMask,
                                'default_gateway':defaultGateway,
                                'primary_dns':primaryDns,
                                'secondary_dns':secondaryDns,
                            }

                        # Type of Authentication
                        polVars["var_description"] = 'Select Which Type of Authentication you want to Perform.'
                        polVars["jsonVars"] = ['chap', 'mutual_chap', 'none']
                        polVars["defaultVar"] = 'none'
                        polVars["varType"] = 'Authentication Type'
                        Authentication = ezfunctions.variablesFromAPI(**polVars)

                        if re.search('chap', Authentication):
                            jsonVars = jsonData['components']['schemas']['vnic.IscsiAuthProfile']['allOf'][1]['properties']
                            auth_type = Authentication.replace('_', ' ')
                            auth_type = auth_type.capitalize()

                            polVars["Description"] = jsonVars['UserId']['description']
                            polVars["varDefault"] = ''
                            polVars["varInput"] = f'{auth_type} Username:'
                            polVars["varName"] = f'{auth_type} Username'
                            polVars["varRegex"] = jsonVars['UserId']['pattern']
                            polVars["minLength"] = 1
                            polVars["maxLength"] = 128
                            user_id = ezfunctions.varStringLoop(**polVars)

                            polVars["Description"] = jsonVars['Password']['description']
                            polVars["varDefault"] = ''
                            polVars["varInput"] = f'{auth_type} Password:'
                            polVars["varName"] = f'{auth_type} Password'
                            polVars["varRegex"] = jsonVars['Password']['pattern']
                            polVars["minLength"] = 12
                            polVars["maxLength"] = 16
                            iscsi_boot_password = ezfunctions.varSensitiveStringLoop(**polVars)
                            os.environ['TF_VAR_iscsi_boot_password'] = '%s' % (iscsi_boot_password)
                            password = 1

                            polVars[Authentication] = {
                                'password':password,
                                'user_id':user_id
                            }

                    # Prompt User for the iSCSI Adapter Policy
                    policy_list = [
                        'policies.iscsi_adapter_policies.iscsi_adapter_policy'
                    ]
                    polVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        polVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
                        polVars.update(policyData)


                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    if 'chap' in Authentication:
                        print(f'   authentication      = "Authentication"')
                    print(f'   description         = "{polVars["descr"]}"')
                    if polVars["target_source_type"] == 'Auto':
                        print(f'   dhcp_vendor_id_iqn  = "{polVars["dhcp_vendor_id_iqn"]}"')
                    if polVars["initiator_ip_source"] == 'Pool':
                        print(f'   initiator_ip_pool   = "{polVars["ip_pool"]}"')
                    print(f'   initiator_ip_source = "{polVars["initiator_ip_source"]}"')
                    if polVars.get('initiator_static_ip_v4_config'):
                        print(f'   initiator_static_ip_v4_config = ''{')
                        print(f'     default_gateway = "{polVars["initiator_static_ip_v4_config"]["default_gateway"]}"')
                        print(f'     ip_address      = "{polVars["initiator_static_ip_v4_config"]["ip_address"]}"')
                        print(f'     primary_dns     = "{polVars["initiator_static_ip_v4_config"]["primary_dns"]}"')
                        print(f'     secondary_dns   = "{polVars["initiator_static_ip_v4_config"]["secondary_dns"]}"')
                        print(f'     subnet_mask     = "{polVars["initiator_static_ip_v4_config"]["subnet_mask"]}"')
                        print(f'   ''}')
                    print(f'   iscsi_adapter_policy    = "{polVars["iscsi_adapter_policy"]}"')
                    print(f'   name                    = "{polVars["name"]}"')
                    if 'chap' in Authentication:
                        print(f'   password                = {password}')
                    print(f'   primary_target_policy   = "{polVars["primary_target_policy"]}"')
                    print(f'   secondary_target_policy = "{polVars["secondary_target_policy"]}"')
                    print(f'   target_source_type      = "{polVars["target_source_type"]}"')
                    if 'chap' in Authentication:
                        print(f'   username                = {user_id}')
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

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # iSCSI Static Target Policy Module
    #==============================================
    def iscsi_static_target_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'target'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'iSCSI Static Target Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'iscsi_static_target_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  The {policy_type} allows you to specify the name, IP address, port, and ')
            print(f'  logical unit number of the primary target for iSCSI boot. You can optionally specify these ')
            print(f'  details for a secondary target as well.\n')
            print(f'  This wizard will save the configuration for this section to the following file:')
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s_%s' % (name_prefix, name_suffix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    # Pull in the Policies for iSCSI Static Target
                    jsonVars = jsonData['components']['schemas']['vnic.IscsiStaticTargetPolicy']['allOf'][1]['properties']

                    desc_add = '\n  such as:\n  * iqn.1984-12.com.cisco:lnx1\n  * iqn.1984-12.com.cisco:win-server1'
                    # Target Name
                    polVars["Description"] = jsonVars['TargetName']['description'] + desc_add
                    polVars["varDefault"] = ''
                    polVars["varInput"] = 'Enter the name of the target:'
                    polVars["varName"] = 'Target Name'
                    polVars["varRegex"] = jsonVars['TargetName']['pattern']
                    polVars["minLength"] = 1
                    polVars["maxLength"] = 255
                    polVars["target_name"] = ezfunctions.varStringLoop(**polVars)

                    # IP Address
                    polVars["Description"] = jsonVars['IpAddress']['description']
                    polVars["varDefault"] = ''
                    polVars["varInput"] = 'Enter the target IP address:'
                    polVars["varName"] = 'IP Address'
                    polVars["varRegex"] = jsonVars['IpAddress']['pattern']
                    polVars["minLength"] = 5
                    polVars["maxLength"] = 15
                    polVars["ip_address"] = ezfunctions.varStringLoop(**polVars)

                    # Port
                    polVars["Description"] = jsonVars['Port']['description']
                    polVars["varInput"] = 'Enter the port number of the target.'
                    polVars["varDefault"] = 3260
                    polVars["varName"] = 'Port'
                    polVars["minNum"] = jsonVars['Port']['minimum']
                    polVars["maxNum"] = jsonVars['Port']['maximum']
                    polVars["port"] = ezfunctions.varNumberLoop(**polVars)

                    # LUN Identifier
                    polVars["Description"] = jsonVars['Lun']['description']
                    polVars["varInput"] = 'Enter the ID of the boot logical unit number.'
                    polVars["varDefault"] = 0
                    polVars["varName"] = 'LUN Identifier'
                    polVars["minNum"] = 0
                    polVars["maxNum"] = 1024
                    polVars["lun_id"] = ezfunctions.varNumberLoop(**polVars)

                    # LUN Bootable
                    polVars["Description"] = jsonVars['Lun']['description']
                    polVars["varInput"] = f'Should LUN {polVars["lun_id"]} be bootable?'
                    polVars["varDefault"] = 'Y'
                    polVars["varName"] = 'LUN Identifier'
                    polVars["bootable"] = ezfunctions.varBoolLoop(**polVars)

                    polVars["lun"] = {
                        'bootable':polVars["bootable"],
                        'lun_id':polVars["lun_id"]
                    }
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'   description = "{polVars["descr"]}"')
                    print(f'   ip_address  = "{polVars["ip_address"]}"')
                    print(f'   name        = "{polVars["name"]}"')
                    print(f'   port        = {polVars["port"]}')
                    print(f'   target_name = "{polVars["target_name"]}"')
                    print(f'   lun = [')
                    print(f'     ''{')
                    print(f'       bootable = {polVars["lun"]["bootable"]}')
                    print(f'       lun_id   = {polVars["lun"]["lun_id"]}')
                    print(f'     ''}')
                    print(f'   ]')
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

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # LAN Connectivity Policy Module
    #==============================================
    def lan_connectivity_policies(self, jsonData, easy_jsonData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = ['Management', 'Migration', 'Storage', 'Virtual_Machines']
        opSystem = kwargs['opSystem']
        org = self.org
        ezfunctions.policy_names = []
        policy_type = 'LAN Connectivity Policy'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'lan_connectivity_policies'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

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
            if opSystem == 'Windows':
                print(f'  - {tfDir}\\{org}\\{self.type}\\{polVars["template_type"]}.auto.tfvars')
            else:
                print(f'  - {tfDir}/{org}/{self.type}/{polVars["template_type"]}.auto.tfvars')
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

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    polVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['vnic.LanConnectivityPolicy']['allOf'][1]['properties']

                    polVars["var_description"] = jsonVars['TargetPlatform']['description']
                    polVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    polVars["defaultVar"] = 'FIAttached'
                    polVars["varType"] = 'Target Platform'
                    polVars["target_platform"] = ezfunctions.variablesFromAPI(**polVars)

                    if polVars["target_platform"] == 'FIAttached':
                        polVars["Description"] = jsonVars['AzureQosEnabled']['description']
                        polVars["varInput"] = f'Do you want to Enable AzureStack-Host QoS?'
                        polVars["varDefault"] = 'N'
                        polVars["varName"] = 'AzureStack-Host QoS'
                        polVars["enable_azure_stack_host_qos"] = ezfunctions.varBoolLoop(**polVars)

                        polVars["var_description"] = jsonVars['IqnAllocationType']['description']
                        polVars["jsonVars"] = sorted(jsonVars['IqnAllocationType']['enum'])
                        polVars["defaultVar"] = jsonVars['IqnAllocationType']['default']
                        polVars["varType"] = 'Iqn Allocation Type'
                        polVars["iqn_allocation_type"] = ezfunctions.variablesFromAPI(**polVars)

                        if polVars["iqn_allocation_type"] == 'Pool':
                            polVars["iqn_static_identifier"] = ''
                            policy_list = [
                                'pools.iqn_pools.iqn_pool',
                            ]
                            polVars["allow_opt_out"] = False
                            for policy in policy_list:
                                policy_short = policy.split('.')[2]
                                polVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
                                polVars.update(policyData)

                        elif polVars["iqn_allocation_type"] == 'Static':
                                polVars["iqn_pool"] = ''
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
                                            polVars["iqn_static_identifier"] = 'iqn.1984-12.com.cisco.iscsi:%s' % (suffix)
                                            print(f'IQN is {polVars["iqn_static_identifier"]}')
                                        valid = True
                                    elif question == 'N':
                                        polVars["Description"] = jsonVars['StaticIqnName']['description']
                                        polVars["varDefault"] = ''
                                        polVars["varInput"] = 'What is the Static IQN you would like to assign to this LAN Policy?'
                                        polVars["varName"] = 'Static IQN'
                                        polVars["varRegex"] = jsonVars['StaticIqnName']['pattern']
                                        polVars["minLength"] = 4
                                        polVars["maxLength"] = 128
                                        polVars["iqn_static_identifier"] = ezfunctions.varStringLoop(**polVars)

                        polVars["var_description"] = jsonVars['PlacementMode']['description']
                        polVars["jsonVars"] = sorted(jsonVars['PlacementMode']['enum'])
                        polVars["defaultVar"] = jsonVars['PlacementMode']['default']
                        polVars["varType"] = 'Placement Mode'
                        polVars["vnic_placement_mode"] = ezfunctions.variablesFromAPI(**polVars)

                    else:
                        polVars["iqn_allocation_type"] = 'None'

                    global_name = polVars["name"]
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

                    policy_list = [
                        'policies.san_connectivity_policies.san_connectivity_policy'
                    ]
                    polVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        polVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
                        polVars.update(policyData)

                    if polVars['san_connectivity_policy']:
                        san_policy = polVars['san_connectivity_policy']
                        for item in policyData['san_connectivity_policies'][0][san_policy][0]['vhbas']:
                            for k, v in item.items():
                                pLink = v[0]['placement_pci_link']
                                pOrder = v[0]['placement_pci_order']
                                pci_order_consumed[0][pLink].append(pOrder)

                    polVars["vnics"] = []
                    vnic_loop = False
                    while vnic_loop == False:
                        jsonVars = jsonData['components']['schemas']['vnic.EthIf']['allOf'][1]['properties']

                        polVars["Description"] = jsonVars['FailoverEnabled']['description']
                        polVars["varInput"] = f'Do you want to Enable Failover for this vNIC?'
                        polVars["varDefault"] = 'N'
                        polVars["varName"] = 'Enable Failover'
                        polVars["enable_failover"] = ezfunctions.varBoolLoop(**polVars)

                        print(f' inner loop count is {inner_loop_count}')
                        if polVars["enable_failover"] == True:
                            fabrics = ['A']
                            polVars["varDefault"] = 'vnic'
                        else:
                            fabrics = ['A','B']
                            if inner_loop_count < 5:
                                numValue = inner_loop_count -1
                                polVars["varDefault"] = name_suffix[numValue]
                            else:
                                polVars["varDefault"] = 'vnic'
                        polVars["Description"] = jsonVars['Name']['description']
                        polVars["varInput"] = f'What is the name for this vNIC? [{polVars["varDefault"]}]:'
                        polVars["varName"] = 'vNIC Name'
                        polVars["varRegex"] = jsonVars['Name']['pattern']
                        polVars["minLength"] = 1
                        polVars["maxLength"] = jsonVars['Name']['maxLength']
                        Name = ezfunctions.varStringLoop(**polVars)
                        for x in fabrics:
                            polVars[f"name_{x}"] = '%s-%s' % (Name, x)

                        if polVars["target_platform"] == 'FIAttached':
                            polVars["var_description"] = jsonVars['MacAddressType']['description']
                            polVars["jsonVars"] = sorted(jsonVars['MacAddressType']['enum'])
                            polVars["defaultVar"] = jsonVars['MacAddressType']['default']
                            polVars["varType"] = 'Mac Address Type'
                            polVars[f"mac_address_allocation_type"] = ezfunctions.variablesFromAPI(**polVars)

                            if polVars[f"mac_address_allocation_type"] == 'POOL':
                                for x in fabrics:
                                    polVars["name"] = polVars[f"name_{x}"]
                                    policy_list = [
                                        'pools.mac_pools.mac_pool',
                                    ]
                                    polVars["allow_opt_out"] = False
                                    for policy in policy_list:
                                        polVars[f"static_mac_{x}"] = ''
                                        if polVars["enable_failover"] == False:
                                            polVars["optional_message"] = f'MAC Address Pool for Fabric {x}'
                                        policy_short = policy.split('.')[2]
                                        polVars[f'mac_pool_{x}'],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
                                        polVars.update(policyData)
                                    polVars.pop('optional_message')
                            else:
                                for x in fabrics:
                                    polVars[f'mac_pool_{x}'] = ''
                                    polVars["Description"] = jsonVars['StaticMacAddress']['description']
                                    if polVars["enable_failover"] == True:
                                        polVars["varInput"] = f'What is the static MAC Address?'
                                    else:
                                        polVars["varInput"] = f'What is the static MAC Address for Fabric {x}?'
                                    if polVars["enable_failover"] == True:
                                        polVars["varName"] = f'Static Mac Address'
                                    else:
                                        polVars["varName"] = f'Fabric {x} Mac Address'
                                    polVars["varRegex"] = jsonData['components']['schemas']['boot.Pxe']['allOf'][1]['properties']['MacAddress']['pattern']
                                    polVars["minLength"] = 17
                                    polVars["maxLength"] = 17
                                    polVars[f"static_mac_{x}"] = ezfunctions.varStringLoop(**polVars)

                        # Pull in API Attributes
                        jsonVars = jsonData['components']['schemas']['vnic.PlacementSettings']['allOf'][1]['properties']

                        for x in fabrics:
                            polVars["var_description"] = jsonVars['PciLink']['description']
                            if polVars["enable_failover"] == False:
                                polVars["var_description"] = polVars["var_description"] + f'\n\nPCI Link For Fabric {x}'
                            polVars["jsonVars"] = [0, 1]
                            polVars["defaultVar"] = jsonVars['PciLink']['default']
                            if polVars["enable_failover"] == True:
                                polVars["varType"] = 'PCI Link'
                            else:
                                polVars["varType"] = f'Fabric {x} PCI Link'
                            polVars[f"pci_link_{x}"] = ezfunctions.variablesFromAPI(**polVars)
                            print(polVars[f"pci_link_{x}"])

                            if polVars["target_platform"] == 'Standalone':
                                polVars["var_description"] = jsonVars['Uplink']['description']
                                polVars["jsonVars"] = [0, 1, 2, 3]
                                polVars["defaultVar"] = 0
                                polVars["varType"] = 'Mac Address Type'
                                polVars[f"uplink_port_{x}"] = ezfunctions.variablesFromAPI(**polVars)

                        polVars["var_description"] = jsonVars['Id']['description']
                        polVars["jsonVars"] = easy_jsonData['policies']['vnic.PlacementSettings']['enum']
                        polVars["defaultVar"] = easy_jsonData['policies']['vnic.PlacementSettings']['default']
                        polVars["varType"] = 'Slot ID'
                        polVars[f"slot_id"] = ezfunctions.variablesFromAPI(**polVars)

                        # Pull in API Attributes
                        jsonVars = jsonData['components']['schemas']['vnic.EthIf']['allOf'][1]['properties']

                        for x in fabrics:
                            valid = False
                            while valid == False:
                                polVars["Description"] = jsonVars['Order']['description']
                                if polVars["enable_failover"] == False:
                                    polVars["varInput"] = f'\nPCI Order For Fabric {x}.'
                                else:
                                    polVars["varInput"] = f'\nPCI Order.'
                                if len(pci_order_consumed[0][polVars[f"pci_link_{x}"]]) > 0:
                                    polVars["varDefault"] = len(pci_order_consumed[0][polVars[f"pci_link_{x}"]])
                                else:
                                    polVars["varDefault"] = 0
                                polVars["varName"] = 'PCI Order'
                                polVars["minNum"] = 0
                                polVars["maxNum"] = 255
                                polVars[f"pci_order_{x}"] = ezfunctions.varNumberLoop(**polVars)

                                consumed_count = 0
                                for i in pci_order_consumed[0][polVars[f"pci_link_{x}"]]:
                                    if int(i) == int(polVars[f"pci_order_{x}"]):
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        print(f'  Error!! PCI Order "{polVars[f"PciOrder_{x}"]}" is already in use.  Please use an alternative.')
                                        print(f'\n-------------------------------------------------------------------------------------------\n')
                                        consumed_count += 1

                                if consumed_count == 0:
                                    pci_order_consumed[0][polVars[f"pci_link_{x}"]].append(polVars[f"pci_order_{x}"])
                                    valid = True

                        # Pull in API Attributes
                        jsonVars = jsonData['components']['schemas']['vnic.Cdn']['allOf'][1]['properties']

                        polVars["var_description"] = jsonVars['Source']['description']
                        polVars["jsonVars"] = jsonVars['Source']['enum']
                        polVars["defaultVar"] = jsonVars['Source']['default']
                        polVars["varType"] = 'CDN Source'
                        polVars["cdn_source"] = ezfunctions.variablesFromAPI(**polVars)

                        if polVars["cdn_source"] == 'user':
                            for x in fabrics:
                                polVars["Description"] = jsonVars['Value']['description']
                                if polVars["enable_failover"] == True:
                                    polVars["varInput"] = 'What is the value for the Consistent Device Name?'
                                else:
                                    polVars["varInput"] = 'What is the value for Fabric {x} Consistent Device Name?'
                                polVars["varName"] = 'CDN Name'
                                polVars["varRegex"] = jsonVars['Value']['pattern']
                                polVars["minLength"] = 1
                                polVars["maxLength"] = jsonVars['Value']['maxLength']
                                polVars[f"cdn_value_{x}"] = ezfunctions.varStringLoop(**polVars)
                        else:
                            for x in fabrics:
                                polVars[f"cdn_value_{x}"] = ''

                        polVars["name"] = polVars["name"].split('-')[0]
                        policy_list = [
                            'policies.ethernet_adapter_policies.ethernet_adapter_policy',
                        ]
                        if polVars["target_platform"] == 'Standalone':
                            policy_list.append('policies.ethernet_network_policies.ethernet_network_policy')
                        else:
                            policy_list.append('policies.ethernet_network_control_policies.ethernet_network_control_policy')
                            policy_list.append('policies.ethernet_network_group_policies.ethernet_network_group_policy')
                        policy_list.append('policies.ethernet_qos_policies.ethernet_qos_policy')
                        polVars["allow_opt_out"] = False
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            polVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
                            polVars.update(policyData)
                        if not polVars["iqn_allocation_type"] == 'None':
                            policy_list [
                                'policies.iscsi_boot_policies.iscsi_boot_policy'
                            ]
                            for x in fabrics:
                                if polVars["enable_failover"] == False:
                                    polVars["optional_message"] = f'iSCSI Boot Policy for Fabric {x}'
                                policy_short = policy.split('.')[2]
                                polVars[f"{policy_short}_{x}"],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars)
                                polVars.update(policyData)
                            else:
                                polVars[f'iscsi_boot_policy_{x}'] = ''



                        for x in fabrics:
                            polVars[f"vnic_fabric_{x}"] = {
                                'cdn_source':polVars["cdn_source"],
                            }
                            if not polVars[f"cdn_value_{x}"] == '':
                                polVars[f"vnic_fabric_{x}"].update({'cdn_value':polVars[f"cdn_value_{x}"]})
                            polVars[f"vnic_fabric_{x}"].update({'enable_failover':polVars["enable_failover"]})
                            polVars[f"vnic_fabric_{x}"].update({'ethernet_adapter_policy':polVars["ethernet_adapter_policy"]})
                            if polVars["target_platform"] == 'Standalone':
                                polVars[f"vnic_fabric_{x}"].update({'ethernet_network_policy':polVars["ethernet_network_policy"]})
                            else:
                                polVars[f"vnic_fabric_{x}"].update({'ethernet_network_control_policy':polVars["ethernet_network_control_policy"]})
                                polVars[f"vnic_fabric_{x}"].update({'ethernet_network_group_policy':polVars["ethernet_network_group_policy"]})
                            polVars[f"vnic_fabric_{x}"].update({'ethernet_qos_policy':polVars["ethernet_qos_policy"]})
                            if not polVars["iqn_allocation_type"] == 'None':
                                polVars[f"vnic_fabric_{x}"].update({'iscsi_boot_policy':polVars[f"iscsi_boot_policy_{x}"]})
                            if polVars["target_platform"] == 'FIAttached':
                                polVars[f"vnic_fabric_{x}"].update({'mac_address_allocation_type':polVars[f"mac_address_allocation_type"]})
                                if polVars["mac_address_allocation_type"] == 'POOL':
                                    polVars[f"vnic_fabric_{x}"].update({'mac_address_pool':polVars[f"mac_pool_{x}"]})
                                else:
                                    polVars[f"vnic_fabric_{x}"].update({'mac_address_static':polVars[f"static_mac_{x}"]})
                            polVars[f"vnic_fabric_{x}"].update({'name':polVars[f"name_{x}"]})
                            polVars[f"vnic_fabric_{x}"].update({'pci_link':polVars[f"pci_link_{x}"]})
                            polVars[f"vnic_fabric_{x}"].update({'pci_order':polVars[f"pci_order_{x}"]})
                            polVars[f"vnic_fabric_{x}"].update({'slot_id':polVars[f"slot_id"]})
                            if polVars["target_platform"] == 'FIAttached':
                                polVars[f"vnic_fabric_{x}"].update({'switch_id':f"{x}"})
                            else:
                                polVars[f"vnic_fabric_{x}"].update({'uplink_port':polVars[f"uplink_port_{x}"]})

                        polVars["name"] = global_name
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        for x in fabrics:
                            if polVars["enable_failover"] == False:
                                print(f'Fabric {x}:')
                            for k, v in polVars[f"vnic_fabric_{x}"].items():
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
                                    polVars["vnics"].append(polVars[f"vnic_fabric_{x}"])
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
                    print(f'    description                 = {polVars["descr"]}')
                    if polVars["target_platform"] == 'FIAttached':
                        print(f'    enable_azure_stack_host_qos = {polVars["enable_azure_stack_host_qos"]}')
                    if not polVars["iqn_allocation_type"] == 'None':
                        print(f'    iqn_allocation_type         = "{polVars["iqn_allocation_type"]}"')
                    if polVars["iqn_allocation_type"] == 'Pool':
                        print(f'    iqn_pool                    = "{polVars["iqn_pool"]}"')
                    if polVars["iqn_allocation_type"] == 'Static':
                        print(f'    iqn_static_identifier       = "{polVars["iqn_static_identifier"]}"')
                    print(f'    name                        = "{polVars["name"]}"')
                    print(f'    target_platform             = "{polVars["target_platform"]}"')
                    print(f'    vnic_placement_mode         = "{polVars["vnic_placement_mode"]}"')
                    if len(polVars["vnics"]) > 0:
                        print(f'    vnics = ''{')
                        for item in polVars["vnics"]:
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
                            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
                            ezfunctions.write_to_template(self, **polVars)

                            # Add Template Name to Policies Output
                            ezfunctions.policy_names.append(polVars["name"])

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

            elif configure == 'N':
                configure_loop = True
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

def policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **polVars):
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
                elif 'Pools' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Pools', 'Pool')
                elif 'Templates' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Templates', 'Template')

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
            if inner_policy == 'iqn_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).iqn_pools(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'mac_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).mac_pools(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'ethernet_adapter_policies':
                policies(name_prefix, polVars["org"], inner_type).ethernet_adapter_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'ethernet_network_control_policies':
                policies(name_prefix, polVars["org"], inner_type).ethernet_network_control_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'ethernet_network_group_policies':
                policies(name_prefix, polVars["org"], inner_type).ethernet_network_group_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'ethernet_network_policies':
                policies(name_prefix, polVars["org"], inner_type).ethernet_network_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'ethernet_qos_policies':
                policies(name_prefix, polVars["org"], inner_type).ethernet_qos_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'iscsi_adapter_policies':
                policies(name_prefix, polVars["org"], inner_type).iscsi_adapter_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'iscsi_boot_policies':
                policies(name_prefix, polVars["org"], inner_type).iscsi_boot_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'iscsi_static_target_policies':
                policies(name_prefix, polVars["org"], inner_type).iscsi_static_target_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'system_qos_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).system_qos_policies(jsonData, easy_jsonData, **kwargs)
            elif inner_policy == 'vlan_policies':
                vxan.policies(name_prefix, polVars["org"], inner_type).vlan_policies(jsonData, easy_jsonData, **kwargs)
