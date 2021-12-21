#!/usr/bin/env python3

import jinja2
import pkg_resources
import re
import validating
from class_policies_lan import policies_lan
from class_policies_p1 import policies_p1
from class_policies_p2 import policies_p2
from class_policies_p3 import policies_p3
from class_policies_san import policies_san
from class_policies_vxan import policies_vxan
from class_pools import pools
from easy_functions import choose_policy, policies_parse
from easy_functions import exit_default_no
from easy_functions import policy_descr, policy_name
from easy_functions import ucs_domain_serials
from easy_functions import variablesFromAPI
from easy_functions import varNumberLoop
from easy_functions import varStringLoop
from easy_functions import write_to_template

ucs_template_path = pkg_resources.resource_filename('class_profiles', 'Templates/')

class profiles(object):
    def __init__(self, name_prefix, org, type):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(ucs_template_path + '%s/') % (type))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.name_prefix = name_prefix
        self.org = org
        self.type = type

    #==============================================
    # Quick Start - UCS Chassis Profile Module
    #==============================================
    def quick_start_chassis(self, easy_jsonData, **templateVars):
        org = self.org
        policy_type = 'UCS Chassis Profile'
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ucs_chassis_profiles'

        domain_name = templateVars["name"]
        templateVars["Description"] = f'Number of Chassis attached to {domain_name}.'
        templateVars["varInput"] = f'Enter the Number of Chassis attached to {domain_name}:'
        templateVars["varDefault"] = 1
        templateVars["varName"] = 'Chassis Count'
        templateVars["minNum"] = 1
        templateVars["maxNum"] = 20
        chassis_count = varNumberLoop(**templateVars)

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        rangex = int(chassis_count) + 1
        for x in range(1,rangex):
            # Chassis Model
            templateVars["multi_select"] = False
            jsonVars = easy_jsonData['policies']['thermal.Policy']
            templateVars["var_description"] = jsonVars['chassisType']['description']
            templateVars["jsonVars"] = sorted(jsonVars['chassisType']['enum'])
            templateVars["defaultVar"] = jsonVars['chassisType']['default']
            templateVars["varType"] = 'Chassis Model'
            chassis_model = variablesFromAPI(**templateVars)

            # Set Default Policy Values
            templateVars["imc_access_policy"] = templateVars["org"]
            templateVars["power_policy"] = chassis_model
            templateVars["snmp_policy"] = templateVars["org"]
            templateVars["thermal_policy"] = chassis_model
            templateVars["name"] = f'{domain_name}-{x}'
            templateVars["descr"] = f'{domain_name}-{x} Chassis Profile.'

            # Obtain Chassis Serial Number or Skip
            templateVars["Description"] = 'Serial Number of the Chassis to assign to the Profile.'
            templateVars["varDefault"] = ''
            templateVars["varInput"] = f'What is the Serial Number of Chassis {x}? [press enter to skip]:'
            templateVars["varName"] = 'Serial Number'
            templateVars["varRegex"] = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
            templateVars["minLength"] = 11
            templateVars["maxLength"] = 11
            templateVars['serial_number'] = varStringLoop(**templateVars)

            # Write Policies to Template File
            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
            write_to_template(self, **templateVars)

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # Quick Start - UCS Domain Profile Module
    #==============================================
    def quick_start_domain(self, **templateVars):
        org = self.org
        policy_type = 'UCS Domain Profile'
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ucs_domain_profiles'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        # Write Policies to Template File
        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
        write_to_template(self, **templateVars)

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # Quick Start - UCS Server Profile Module
    #==============================================
    def quick_start_server_profiles(self, **templateVars):
        org = self.org
        policy_type = 'UCS Server Profile'
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ucs_server_profiles'

        templateVars["Description"] = f'Number of Server Profiles.'
        templateVars["varInput"] = f'Enter the Number of Server Profiles to Create:'
        templateVars["varDefault"] = 1
        templateVars["varName"] = 'Server Count'
        templateVars["minNum"] = 1
        templateVars["maxNum"] = 160
        server_count = varNumberLoop(**templateVars)

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        rangex = int(server_count) + 1
        for x in range(1,rangex):
            # Server Profile Name
            valid = False
            while valid == False:
                name = input(f'What is the Name for the Server Profile? ')
                if not name == '':
                    valid = validating.name_rule(f'Server Profile Name', name, 1, 62)
                else:
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Error!! Invalid Value.  Please Re-enter the Server Profile Name.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            templateVars["name"] = name

            # Set Default Policy Values
            templateVars["descr"] = f'{templateVars["name"]} Server Profile'
            templateVars["ucs_server_profile_template"] = f'{templateVars["boot_order_policy"]}'

            # Obtain Chassis Serial Number or Skip
            templateVars["Description"] = f'Serial Number of the Server Profile {templateVars["name"]}.'
            templateVars["varDefault"] = ''
            templateVars["varInput"] = f'What is the Serial Number of {templateVars["name"]}? [press enter to skip]:'
            templateVars["varName"] = 'Serial Number'
            templateVars["varRegex"] = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
            templateVars["minLength"] = 11
            templateVars["maxLength"] = 11
            templateVars['serial_number'] = varStringLoop(**templateVars)

            if not templateVars['serial_number'] == '':
                templateVars["server_assignment_mode"] = 'Static'
            else:
                templateVars["server_assignment_mode"] = 'None'

            # Write Policies to Template File
            templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
            write_to_template(self, **templateVars)

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==================================================
    # Quick Start - UCS Server Profile Template Module
    #==================================================
    def quick_start_server_templates(self, **templateVars):
        org = self.org
        policy_type = 'UCS Server Profile Template'
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ucs_server_profile_templates'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        # Set Default Policy Values
        templateVars["name"] = f'{templateVars["boot_order_policy"]}'
        templateVars["descr"] = f'{templateVars["name"]} Server Profile Template'

        templateVars["uuid_pool"] = 'VMware'
        templateVars["bios_policy"] = 'VMware'
        templateVars["boot_policy"] = f'{templateVars["boot_order_policy"]}'
        templateVars["virtual_media_policy"] = ''
        templateVars["ipmi_over_lan_policy"] = f'{org}'
        templateVars["local_user_policy"] = f'{org}'
        templateVars["serial_over_lan_policy"] = f'{org}'
        templateVars["snmp_policy"] = f'{org}'
        templateVars["syslog_policy"] = f'{org}'
        templateVars["virtual_kvm_policy"] = f'{org}'
        templateVars["sd_card_policy"] = ''
        if templateVars["boot_order_policy"] == 'VMware_M2':
            templateVars["storage_policy"] = 'M2_Raid'
        elif templateVars["boot_order_policy"] == 'VMware_Raid1':
            templateVars["storage_policy"] = 'MRAID'
        templateVars["lan_connectivity_policy"] = 'VMware_LAN'
        if len(templateVars["fc_ports"]) > 0:
            templateVars["san_connectivity_policy"] = 'VMware_SAN'

        if templateVars["server_type"] == 'FIAttached':
            templateVars["certificate_management_policy"] = ''
            templateVars["imc_access_policy"] = f'{org}'
            templateVars["power_policy"] = 'Server'
            templateVars["target_platform"] = 'FIAttached'

        if templateVars["server_type"] == 'Standalone':
            templateVars["adapter_configuration_policy"] = f'{org}'
            templateVars["device_connector_policy"] = f'{org}'
            templateVars["ldap_policy"] = f'{org}'
            templateVars["network_connectivity_policy"] = f'{org}'
            templateVars["ntp_policy"] = f'{org}'
            templateVars["persistent_memory_policy"] = f'{org}'
            templateVars["smtp_policy"] = f'{org}'
            templateVars["ssh_policy"] = f'{org}'
            templateVars["target_platform"] = 'Standalone'

        # Write Policies to Template File
        templateVars["template_file"] = '%s.jinja2' % (templateVars["template_type"])
        write_to_template(self, **templateVars)

        # Close the Template file
        templateVars["template_file"] = 'template_close.jinja2'
        write_to_template(self, **templateVars)

    #==============================================
    # UCS Chassis Profile Module
    #==============================================
    def ucs_chassis_profiles(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'chassis'
        org = self.org
        policy_type = 'UCS Chassis Profile'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ucs_chassis_profiles'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s' % (name_prefix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = easy_jsonData['profiles']
                    templateVars["var_description"] = jsonVars['action']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['action']['enum'])
                    templateVars["defaultVar"] = jsonVars['action']['default']
                    templateVars["varType"] = 'Action'
                    templateVars["action"] = variablesFromAPI(**templateVars)

                    valid = False
                    while valid == False:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Note: If you do not have the Serial Number at this time you can manually add it to the:')
                        print(f'        - ucs_chassis_profiles/ucs_chassis_profiles.auto.tfvars file later.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        templateVars["serial_number"] = input('What is the Serial Number of the Chassis? [press enter to skip]: ')
                        if templateVars["serial_number"] == '':
                            valid = True
                        elif re.fullmatch(r'^[A-Z]{3}[2-3][\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\dA-Z]{4}$', templateVars["serial_number"]):
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Serial Number.  "{templateVars["serial_number"]}" is not a valid serial.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    policy_list = [
                        'policies.imc_access_policies.imc_access_policy',
                        'policies.power_policies.power_policy',
                        'policies.snmp_policies.snmp_policy',
                        'policies.thermal_policies.thermal_policy'
                    ]
                    templateVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        templateVars.update(policyData)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    action            = "No-op"')
                    if not templateVars["serial_number"] == '':
                        print(f'    assign_chassis    = True')
                    else:
                        print(f'    assign_chassis    = False')
                    print(f'    name              = "{templateVars["name"]}"')
                    print(f'    imc_access_policy = "{templateVars["imc_access_policy"]}"')
                    print(f'    power_policy      = "{templateVars["power_policy"]}"')
                    print(f'    serial_number     = "{templateVars["serial_number"]}"')
                    print(f'    snmp_policy       = "{templateVars["snmp_policy"]}"')
                    print(f'    thermal_policy    = "{templateVars["thermal_policy"]}"')
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
    # UCS Domain Profile Module
    #==============================================
    def ucs_domain_profiles(self, jsonData, easy_jsonData, policy_prefix):
        name_prefix = self.name_prefix
        name_suffix = 'ucs'
        org = self.org
        policy_type = 'UCS Domain Profile'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ucs_domain_profiles'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            configure = input(f'Do You Want to Configure a {policy_type}?  Enter "Y" or "N" [Y]: ')
            if configure == 'Y' or configure == '':
                policy_loop = False
                while policy_loop == False:

                    if not name_prefix == '':
                        name = '%s' % (name_prefix)
                    else:
                        name = '%s_%s' % (org, name_suffix)

                    templateVars["name"] = policy_name(name, policy_type)
                    templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                    templateVars["multi_select"] = False
                    jsonVars = easy_jsonData['profiles']
                    templateVars["var_description"] = jsonVars['action']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['action']['enum'])
                    templateVars["defaultVar"] = jsonVars['action']['default']
                    templateVars["varType"] = 'Action'
                    templateVars["action"] = variablesFromAPI(**templateVars)

                    serial_a,serial_b = ucs_domain_serials()
                    templateVars["serial_number_fabric_a"] = serial_a
                    templateVars["serial_number_fabric_b"] = serial_b

                    policy_list = [
                        'policies.network_connectivity_policies.network_connectivity_policy',
                        'policies.ntp_policies.ntp_policy',
                        'policies.snmp_policies.snmp_policy',
                        'policies.switch_control_policies.switch_control_policy',
                        'policies.syslog_policies.syslog_policy',
                        'policies.system_qos_policies.system_qos_policy'
                    ]
                    templateVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        if re.search(r'(switch_control|system_qos)', policy):
                            templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        else:
                            templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, policy_prefix, policy, **templateVars)
                        templateVars.update(policyData)

                    policy_list = [
                        'policies.port_policies.port_policy',
                        'policies.vlan_policies.vlan_policy',
                        'policies.vsan_policies.vsan_policy'
                    ]
                    templateVars["allow_opt_out"] = False
                    for policy in policy_list:
                        policy_long = policy.split('.')[1]
                        policy_short = policy.split('.')[2]
                        x = policy_short.split('_')
                        policy_description = []
                        for y in x:
                            y = y.capitalize()
                            policy_description.append(y)
                        policy_description = " ".join(policy_description)

                        templateVars[policy_long] = {}
                        # templateVars["policy"] = '%s Fabric A' % (policy_description)
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  !!! Select the {policy_description} for Fabric A !!!')
                        fabric_a,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        # templateVars["policy"] = '%s Fabric B' % (policy_description)
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  !!! Select the {policy_description} for Fabric B !!!')
                        fabric_b,policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        templateVars[policy_long].update({'fabric_a':fabric_a})
                        templateVars[policy_long].update({'fabric_b':fabric_b})
                        if policy_long == 'port_policies':
                            device_model_a = policyData['port_policies'][0][fabric_a][0]['device_model']
                            device_model_b = policyData['port_policies'][0][fabric_b][0]['device_model']
                            if not device_model_a == device_model_b:
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                print(f'  !!! Error.  Device Model for the port Policies does not match !!!')
                                print(f'  Fabric A Port Policy device_model is {device_model_a}.')
                                print(f'  Fabric B Port Policy device_model is {device_model_b}.')
                                print(f'  The script is going to set the device_model to match Fabric A for now but you should.')
                                print(f'  either reject this configuration assuming you mistakenly chose non-matching port policies.')
                                print(f'  or re-run the port-policy wizard again to correct the configuration.')
                                print(f'\n-------------------------------------------------------------------------------------------\n')
                                templateVars["device_model"] = device_model_a
                            else:
                                templateVars["device_model"] = device_model_a


                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    action                      = "No-op"')
                    if not (templateVars["serial_number_fabric_a"] == '' and templateVars["serial_number_fabric_a"] == ''):
                        print(f'    assign_switches             = True')
                    else:
                        print(f'    assign_switches             = False')
                    print(f'    device_model                = "{templateVars["device_model"]}"')
                    print(f'    name                        = "{templateVars["name"]}"')
                    print(f'    network_connectivity_policy = "{templateVars["network_connectivity_policy"]}"')
                    print(f'    ntp_policy                  = "{templateVars["ntp_policy"]}"')
                    print(f'    port_policy_fabric_a        = "{templateVars["port_policies"]["fabric_a"]}"')
                    print(f'    port_policy_fabric_b        = "{templateVars["port_policies"]["fabric_b"]}"')
                    print(f'    serial_number_fabric_a      = "{templateVars["serial_number_fabric_a"]}"')
                    print(f'    serial_number_fabric_b      = "{templateVars["serial_number_fabric_b"]}"')
                    print(f'    snmp_policy                 = "{templateVars["snmp_policy"]}"')
                    print(f'    switch_control_policy       = "{templateVars["switch_control_policy"]}"')
                    print(f'    syslog_policy               = "{templateVars["syslog_policy"]}"')
                    print(f'    system_qos_policy           = "{templateVars["system_qos_policy"]}"')
                    print(f'    vlan_policy_fabric_a        = "{templateVars["vlan_policies"]["fabric_a"]}"')
                    print(f'    vlan_policy_fabric_b        = "{templateVars["vlan_policies"]["fabric_b"]}"')
                    print(f'    vsan_policy_fabric_a        = "{templateVars["vsan_policies"]["fabric_a"]}"')
                    print(f'    vsan_policy_fabric_b        = "{templateVars["vsan_policies"]["fabric_b"]}"')
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
    # UCS Server Profile Module
    #==============================================
    def ucs_server_profiles(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'server'
        org = self.org
        policy_type = 'UCS Server Profile'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ucs_server_profiles'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                templateVars["name"] = policy_name(name, policy_type)
                templateVars["descr"] = policy_descr(templateVars["name"], policy_type)

                templateVars["allow_opt_out"] = False
                templateVars["multi_select"] = False
                jsonVars = easy_jsonData['profiles']
                templateVars["var_description"] = jsonVars['action']['description']
                templateVars["jsonVars"] = sorted(jsonVars['action']['enum'])
                templateVars["defaultVar"] = jsonVars['action']['default']
                templateVars["varType"] = 'Action'
                templateVars["action"] = variablesFromAPI(**templateVars)


                jsonVars = jsonData['components']['schemas']['server.Profile']['allOf'][1]['properties']
                templateVars["var_description"] = jsonVars['ServerAssignmentMode']['description']
                templateVars["jsonVars"] = sorted(jsonVars['ServerAssignmentMode']['enum'])
                templateVars["defaultVar"] = jsonVars['ServerAssignmentMode']['default']
                templateVars["varType"] = 'Server Assignment Mode'
                templateVars["server_assignment_mode"] = variablesFromAPI(**templateVars)

                if templateVars["server_assignment_mode"] == 'Static':
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Note: If you do not have the Serial Number at this time you can manually add it to the:')
                    print(f'        - ucs_server_profiles/ucs_server_profiles.auto.tfvars file later.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    templateVars["Description"] = 'Serial Number of the Physical Compute Resource to assign to the Profile.'
                    templateVars["varDefault"] = ''
                    templateVars["varInput"] = 'What is the Serial Number of the Server? [press enter to skip]:'
                    templateVars["varName"] = 'Serial Number'
                    templateVars["varRegex"] = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
                    templateVars["minLength"] = 11
                    templateVars["maxLength"] = 11
                    templateVars['serial_number'] = varStringLoop(**templateVars)
                elif templateVars["server_assignment_mode"] == 'Pool':
                    policy_list = [
                        'pools.resource_pools.resource_pool'
                    ]
                    templateVars["allow_opt_out"] = False
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        templateVars.update(policyData)
                        server_template = True
                        valid = True

                valid = False
                while valid == False:
                    server_template = input('Do you want to Associate to a UCS Server Profile Template?  Enter "Y" or "N" [Y]: ')
                    if server_template == '' or server_template == 'Y':
                        policy_list = [
                            'ucs_server_profiles.ucs_server_profile_templates.ucs_server_profile_template'
                        ]
                        templateVars["allow_opt_out"] = False
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                            templateVars.update(policyData)
                            server_template = True
                            valid = True
                    elif server_template == 'N':
                        server_template = False
                        valid = True
                    else:
                        print(f'\n------------------------------------------------------\n')
                        print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                        print(f'\n------------------------------------------------------\n')

                if server_template == False:
                    templateVars["multi_select"] = False
                    jsonVars = jsonData['components']['schemas']['server.BaseProfile']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['TargetPlatform']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    templateVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                    templateVars["varType"] = 'Target Platform'
                    templateVars["target_platform"] = variablesFromAPI(**templateVars)

                    #___________________________________________________________________________
                    #
                    # Policies On Hold for Right Now
                    # 'policies.certificate_management_policies.certificate_management_policy',
                    #___________________________________________________________________________
                    if templateVars["target_platform"] == 'FIAttached':
                        policy_list = [
                            #___________________________
                            #
                            # Compute Configuration
                            #___________________________
                            'pools.uuid_pools.uuid_pool',
                            'policies.bios_policies.bios_policy',
                            'policies.boot_order_policies.boot_order_policy',
                            'policies.power_policies.power_policy',
                            'policies.virtual_media_policies.virtual_media_policy',
                            #___________________________
                            #
                            # Management Configuration
                            #___________________________
                            'policies.imc_access_policies.imc_access_policy',
                            'policies.ipmi_over_lan_policies.ipmi_over_lan_policy',
                            'policies.local_user_policies.local_user_policy',
                            'policies.serial_over_lan_policies.serial_over_lan_policy',
                            'policies.snmp_policies.snmp_policy',
                            'policies.syslog_policies.syslog_policy',
                            'policies.virtual_kvm_policies.virtual_kvm_policy',
                            #___________________________
                            #
                            # Storage Configuration
                            #___________________________
                            'policies.sd_card_policies.sd_card_policy',
                            'policies.storage_policies.storage_policy',
                            #___________________________
                            #
                            # Network Configuration
                            #___________________________
                            'policies.lan_connectivity_policies.lan_connectivity_policy',
                            'policies.san_connectivity_policies.san_connectivity_policy',
                        ]
                    elif templateVars["target_platform"] == 'Standalone':
                        policy_list = [
                            #___________________________
                            #
                            # Compute Configuration
                            #___________________________
                            'policies.bios_policies.bios_policy',
                            'policies.boot_order_policies.boot_order_policy',
                            'policies.persistent_memory_policies.persistent_memory_policy',
                            'policies.virtual_media_policies.virtual_media_policy',
                            #___________________________
                            #
                            # Management Configuration
                            #___________________________
                            'policies.device_connector_policies.device_connector_policy',
                            'policies.ipmi_over_lan_policies.ipmi_over_lan_policy',
                            'policies.ldap_policies_policies.ldap_policy',
                            'policies.local_user_policies.local_user_policy',
                            'policies.network_connectivity_policies.network_connectivity_policy',
                            'policies.ntp_policies.ntp_policy',
                            'policies.serial_over_lan_policies.serial_over_lan_policy',
                            'policies.smtp_policies.smtp_policy',
                            'policies.snmp_policies.snmp_policy',
                            'policies.ssh_policies.ssh_policy',
                            'policies.syslog_policies.syslog_policy',
                            'policies.virtual_kvm_policies.virtual_kvm_policy',
                            #___________________________
                            #
                            # Storage Configuration
                            #___________________________
                            'policies.sd_card_policies.sd_card_policy',
                            'policies.storage_policies.storage_policy',
                            #___________________________
                            #
                            # Network Configuration
                            #___________________________
                            'policies.adapter_configuration_policies.adapter_configuration_policy',
                            'policies.lan_connectivity_policies.lan_connectivity_policy',
                            'policies.san_connectivity_policies.san_connectivity_policy',
                        ]
                    templateVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        templateVars.update(policyData)

                templateVars["boot_policy"] = templateVars["boot_order_policy"]
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    action          = "{templateVars["action"]}"')
                print(f'    description     = "{templateVars["descr"]}"')
                print(f'    name            = "{templateVars["name"]}"')
                if templateVars["server_assignment_mode"] == 'Pool':
                    print(f'    resource_pool   = {templateVars["resource_pool"]}')
                if templateVars["server_assignment_mode"] == 'Static':
                    print(f'    serial_number   = "{templateVars["serial_number"]}"')
                if server_template == True:
                    print(f'    ucs_server_profile_template = "{templateVars["ucs_server_profile_template"]}"')
                if server_template == False:
                    print(f'    target_platform = "{templateVars["target_platform"]}"')
                if server_template == False:
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Compute Configuration')
                    print(f'    #___________________________"')
                    if not templateVars["static_uuid_address"] == '':
                        print(f'    static_uuid_address        = "{templateVars["static_uuid_address"]}"')
                    if not templateVars["uuid_pool"] == '':
                        print(f'    uuid_pool                  = "{templateVars["uuid_pool"]}"')
                    print(f'    bios_policy                = "{templateVars["bios_policy"]}"')
                    print(f'    boot_order_policy          = "{templateVars["boot_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    persistent_memory_policies = "{templateVars["persistent_memory_policies"]}"')
                    if templateVars["target_platform"] == 'FIAttached':
                        print(f'    power_policy               = "{templateVars["power_policy"]}"')
                    print(f'    virtual_media_policy       = "{templateVars["virtual_media_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Management Configuration')
                    print(f'    #___________________________"')
                    # if target_platform == 'FIAttached':
                    #     print(f'    certificate_management_policy = "{templateVars["pcertificate_management_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    device_connector_policies     = "{templateVars["device_connector_policies"]}"')
                    if templateVars["target_platform"] == 'FIAttached':
                        print(f'    imc_access_policy             = "{templateVars["imc_access_policy"]}"')
                    print(f'    ipmi_over_lan_policy          = "{templateVars["ipmi_over_lan_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    ldap_policies                 = "{templateVars["ldap_policies"]}"')
                    print(f'    local_user_policy             = "{templateVars["local_user_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    network_connectivity_policy   = "{templateVars["network_connectivity_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    ntp_policy                    = "{templateVars["ntp_policy"]}"')
                    print(f'    serial_over_lan_policy        = "{templateVars["serial_over_lan_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    smtp_policy                   = "{templateVars["smtp_policy"]}"')
                    print(f'    snmp_policy                   = "{templateVars["snmp_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    ssh_policy                    = "{templateVars["ssh_policy"]}"')
                    print(f'    syslog_policy                 = "{templateVars["syslog_policy"]}"')
                    print(f'    virtual_kvm_policy            = "{templateVars["virtual_kvm_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Storage Configuration')
                    print(f'    #___________________________"')
                    print(f'    sd_card_policy = "{templateVars["sd_card_policy"]}"')
                    print(f'    storage_policy = "{templateVars["storage_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Network Configuration')
                    print(f'    #___________________________"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    adapter_configuration_policy = "{templateVars["adapter_configuration_policy"]}"')
                    print(f'    lan_connectivity_policy      = "{templateVars["lan_connectivity_policy"]}"')
                    print(f'    san_connectivity_policy      = "{templateVars["san_connectivity_policy"]}"')
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
    # UCS Server Profile Template Module
    #==============================================
    def ucs_server_profile_templates(self, jsonData, easy_jsonData):
        name_prefix = self.name_prefix
        name_suffix = 'template'
        org = self.org
        policy_type = 'UCS Server Profile Template'
        templateVars = {}
        templateVars["header"] = '%s Variables' % (policy_type)
        templateVars["initial_write"] = True
        templateVars["org"] = org
        templateVars["policy_type"] = policy_type
        templateVars["template_file"] = 'template_open.jinja2'
        templateVars["template_type"] = 'ucs_server_profile_templates'

        # Open the Template file
        write_to_template(self, **templateVars)
        templateVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
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
                    jsonVars = jsonData['components']['schemas']['server.BaseProfile']['allOf'][1]['properties']
                    templateVars["var_description"] = jsonVars['TargetPlatform']['description']
                    templateVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    templateVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                    templateVars["varType"] = 'Target Platform'
                    templateVars["target_platform"] = variablesFromAPI(**templateVars)

                    #___________________________________________________________________________
                    #
                    # Policies On Hold for Right Now
                    # 'policies.certificate_management_policies.certificate_management_policy',
                    #___________________________________________________________________________
                    if templateVars["target_platform"] == 'FIAttached':
                        policy_list = [
                            #___________________________
                            #
                            # Compute Configuration
                            #___________________________
                            'pools.uuid_pools.uuid_pool',
                            'policies.bios_policies.bios_policy',
                            'policies.boot_order_policies.boot_order_policy',
                            'policies.power_policies.power_policy',
                            'policies.virtual_media_policies.virtual_media_policy',
                            #___________________________
                            #
                            # Management Configuration
                            #___________________________
                            'policies.imc_access_policies.imc_access_policy',
                            'policies.ipmi_over_lan_policies.ipmi_over_lan_policy',
                            'policies.local_user_policies.local_user_policy',
                            'policies.serial_over_lan_policies.serial_over_lan_policy',
                            'policies.snmp_policies.snmp_policy',
                            'policies.syslog_policies.syslog_policy',
                            'policies.virtual_kvm_policies.virtual_kvm_policy',
                            #___________________________
                            #
                            # Storage Configuration
                            #___________________________
                            'policies.sd_card_policies.sd_card_policy',
                            'policies.storage_policies.storage_policy',
                            #___________________________
                            #
                            # Network Configuration
                            #___________________________
                            'policies.lan_connectivity_policies.lan_connectivity_policy',
                            'policies.san_connectivity_policies.san_connectivity_policy',
                        ]
                    elif templateVars["target_platform"] == 'Standalone':
                        policy_list = [
                            #___________________________
                            #
                            # Compute Configuration
                            #___________________________
                            'policies.bios_policies.bios_policy',
                            'policies.boot_order_policies.boot_order_policy',
                            'policies.persistent_memory_policies.persistent_memory_policy',
                            'policies.virtual_media_policies.virtual_media_policy',
                            #___________________________
                            #
                            # Management Configuration
                            #___________________________
                            'policies.device_connector_policies.device_connector_policy',
                            'policies.ipmi_over_lan_policies.ipmi_over_lan_policy',
                            'policies.ldap_policies_policies.ldap_policy',
                            'policies.local_user_policies.local_user_policy',
                            'policies.network_connectivity_policies.network_connectivity_policy',
                            'policies.ntp_policies.ntp_policy',
                            'policies.serial_over_lan_policies.serial_over_lan_policy',
                            'policies.smtp_policies.smtp_policy',
                            'policies.snmp_policies.snmp_policy',
                            'policies.ssh_policies.ssh_policy',
                            'policies.syslog_policies.syslog_policy',
                            'policies.virtual_kvm_policies.virtual_kvm_policy',
                            #___________________________
                            #
                            # Storage Configuration
                            #___________________________
                            'policies.sd_card_policies.sd_card_policy',
                            'policies.storage_policies.storage_policy',
                            #___________________________
                            #
                            # Network Configuration
                            #___________________________
                            'policies.adapter_configuration_policies.adapter_configuration_policy',
                            'policies.lan_connectivity_policies.lan_connectivity_policy',
                            'policies.san_connectivity_policies.san_connectivity_policy',
                        ]
                    templateVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        templateVars[policy_short],policyData = policy_select_loop(jsonData, easy_jsonData, name_prefix, policy, **templateVars)
                        templateVars.update(policyData)

                    templateVars["boot_policy"] = templateVars["boot_order_policy"]
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description     = "{templateVars["descr"]}"')
                    print(f'    name            = "{templateVars["name"]}"')
                    print(f'    target_platform = "{templateVars["target_platform"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Compute Configuration')
                    print(f'    #___________________________"')
                    if templateVars["target_platform"] == 'FIAttached':
                        print(f'    uuid_pool                  = "{templateVars["uuid_pool"]}"')
                    print(f'    bios_policy                = "{templateVars["bios_policy"]}"')
                    print(f'    boot_order_policy          = "{templateVars["boot_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    persistent_memory_policies = "{templateVars["persistent_memory_policy"]}"')
                    if templateVars["target_platform"] == 'FIAttached':
                        print(f'    power_policy               = "{templateVars["power_policy"]}"')
                    print(f'    virtual_media_policy       = "{templateVars["virtual_media_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Management Configuration')
                    print(f'    #___________________________"')
                    # if target_platform == 'FIAttached':
                    #     print(f'    certificate_management_policy = "{templateVars["certificate_management_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    device_connector_policies     = "{templateVars["device_connector_policy"]}"')
                    if templateVars["target_platform"] == 'FIAttached':
                        print(f'    imc_access_policy             = "{templateVars["imc_access_policy"]}"')
                    print(f'    ipmi_over_lan_policy          = "{templateVars["ipmi_over_lan_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    ldap_policies                 = "{templateVars["ldap_policy"]}"')
                    print(f'    local_user_policy             = "{templateVars["local_user_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    network_connectivity_policy   = "{templateVars["network_connectivity_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    ntp_policy                    = "{templateVars["ntp_policy"]}"')
                    print(f'    serial_over_lan_policy        = "{templateVars["serial_over_lan_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    smtp_policy                   = "{templateVars["smtp_policy"]}"')
                    print(f'    snmp_policy                   = "{templateVars["snmp_policy"]}"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    ssh_policy                    = "{templateVars["ssh_policy"]}"')
                    print(f'    syslog_policy                 = "{templateVars["syslog_policy"]}"')
                    print(f'    virtual_kvm_policy            = "{templateVars["virtual_kvm_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Storage Configuration')
                    print(f'    #___________________________"')
                    print(f'    sd_card_policy = "{templateVars["sd_card_policy"]}"')
                    print(f'    storage_policy = "{templateVars["storage_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Network Configuration')
                    print(f'    #___________________________"')
                    if templateVars["target_platform"] == 'Standalone':
                        print(f'    adapter_configuration_policy = "{templateVars["adapter_configuration_policy"]}"')
                    print(f'    lan_connectivity_policy      = "{templateVars["lan_connectivity_policy"]}"')
                    print(f'    san_connectivity_policy      = "{templateVars["san_connectivity_policy"]}"')
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
                policy_description = policy_description.replace('Ip', 'IP')
                policy_description = policy_description.replace('Ipmi', 'IPMI')
                policy_description = policy_description.replace('Iqn', 'IQN')
                policy_description = policy_description.replace('Ntp', 'NTP')
                policy_description = policy_description.replace('Snmp', 'SNMP')
                policy_description = policy_description.replace('Ssh', 'SSH')
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
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {inner_policy}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            if inner_policy == 'ip_pools':
                pools(name_prefix, templateVars["org"], inner_type).ip_pools(jsonData, easy_jsonData)
            elif inner_policy == 'iqn_pools':
                pools(name_prefix, templateVars["org"], inner_type).iqn_pools(jsonData, easy_jsonData)
            elif inner_policy == 'mac_pools':
                pools(name_prefix, templateVars["org"], inner_type).mac_pools(jsonData, easy_jsonData)
            elif inner_policy == 'uuid_pools':
                pools(name_prefix, templateVars["org"], inner_type).uuid_pools(jsonData, easy_jsonData)
            elif inner_policy == 'wwnn_pools':
                pools(name_prefix, templateVars["org"], inner_type).wwnn_pools(jsonData, easy_jsonData)
            elif inner_policy == 'wwpn_pools':
                pools(name_prefix, templateVars["org"], inner_type).wwpn_pools(jsonData, easy_jsonData)
            elif inner_policy == 'adapter_configuration_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).adapter_configuration_policies(jsonData, easy_jsonData)
            elif inner_policy == 'bios_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).bios_policies(jsonData, easy_jsonData)
            elif inner_policy == 'boot_order_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).boot_order_policies(jsonData, easy_jsonData)
            elif inner_policy == 'certificate_management_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).certificate_management_policies(jsonData, easy_jsonData)
            elif inner_policy == 'device_connector_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).device_connector_policies(jsonData, easy_jsonData)
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
            elif inner_policy == 'fibre_channel_adapter_policies':
                policies_san(name_prefix, templateVars["org"], inner_type).fibre_channel_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'fibre_channel_network_policies':
                policies_san(name_prefix, templateVars["org"], inner_type).fibre_channel_network_policies(jsonData, easy_jsonData)
            elif inner_policy == 'fibre_channel_qos_policies':
                policies_san(name_prefix, templateVars["org"], inner_type).fibre_channel_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'flow_control_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).flow_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'imc_access_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).imc_access_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ipmi_over_lan_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).ipmi_over_lan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_adapter_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).iscsi_adapter_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_boot_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).iscsi_boot_policies(jsonData, easy_jsonData)
            elif inner_policy == 'iscsi_static_target_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).iscsi_static_target_policies(jsonData, easy_jsonData)
            elif inner_policy == 'lan_connectivity_policies':
                policies_lan(name_prefix, templateVars["org"], inner_type).lan_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ldap_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).ldap_policies(jsonData, easy_jsonData)
            elif inner_policy == 'link_aggregation_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).link_aggregation_policies(jsonData, easy_jsonData)
            elif inner_policy == 'link_control_policies':
                policies_p1(name_prefix, templateVars["org"], inner_type).link_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'local_user_policies':
                policies_p2(name_prefix, templateVars["org"], inner_type).local_user_policies(jsonData, easy_jsonData)
            elif inner_policy == 'multicast_policies':
                policies_vxan(name_prefix, templateVars["org"], inner_type).multicast_policies(jsonData, easy_jsonData)
            elif inner_policy == 'network_connectivity_policies':
                policies_p2(name_prefix, templateVars["org"], inner_type).network_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ntp_policies':
                policies_p2(name_prefix, templateVars["org"], inner_type).ntp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'persistent_memory_policies':
                policies_p2(name_prefix, templateVars["org"], inner_type).persistent_memory_policies(jsonData, easy_jsonData)
            elif inner_policy == 'port_policies':
                policies_p2(name_prefix, templateVars["org"], inner_type).port_policies(jsonData, easy_jsonData)
            elif inner_policy == 'power_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).power_policies(jsonData, easy_jsonData)
            elif inner_policy == 'san_connectivity_policies':
                policies_san(name_prefix, templateVars["org"], inner_type).san_connectivity_policies(jsonData, easy_jsonData)
            elif inner_policy == 'sd_card_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).sd_card_policies(jsonData, easy_jsonData)
            elif inner_policy == 'serial_over_lan_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).serial_over_lan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'smtp_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).smtp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'snmp_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).snmp_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ssh_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).ssh_policies(jsonData, easy_jsonData)
            elif inner_policy == 'storage_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).storage_policies(jsonData, easy_jsonData)
            elif inner_policy == 'switch_control_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).switch_control_policies(jsonData, easy_jsonData)
            elif inner_policy == 'syslog_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).syslog_policies(jsonData, easy_jsonData)
            elif inner_policy == 'system_qos_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).system_qos_policies(jsonData, easy_jsonData)
            elif inner_policy == 'thermal_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).thermal_policies(jsonData, easy_jsonData)
            elif inner_policy == 'ucs_server_profiles':
                profiles(name_prefix, templateVars["org"], inner_type).ucs_server_profiles(jsonData, easy_jsonData)
            elif inner_policy == 'ucs_server_profile_templates':
                profiles(name_prefix, templateVars["org"], inner_type).ucs_server_profile_templates(jsonData, easy_jsonData)
            elif inner_policy == 'virtual_kvm_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).virtual_kvm_policies(jsonData, easy_jsonData)
            elif inner_policy == 'virtual_media_policies':
                policies_p3(name_prefix, templateVars["org"], inner_type).virtual_media_policies(jsonData, easy_jsonData)
            elif inner_policy == 'vlan_policies':
                policies_vxan(name_prefix, templateVars["org"], inner_type).vlan_policies(jsonData, easy_jsonData)
            elif inner_policy == 'vsan_policies':
                policies_vxan(name_prefix, templateVars["org"], inner_type).vsan_policies(jsonData, easy_jsonData)
