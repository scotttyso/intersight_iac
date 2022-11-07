#!/usr/bin/env python3
from copy import deepcopy
import lan
import p1
import p2
import p3
import pools
import san
import vxan
import ezfunctions
import jinja2
import os
import pkg_resources
import platform
import re
import validating

ucs_template_path = pkg_resources.resource_filename('profiles', '../templates/')

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
    def quick_start_chassis(self, ezData, **polVars):
        org = self.org
        policy_type = 'UCS Chassis Profile'
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ucs_chassis_profiles'

        domain_name = polVars["name"]
        polVars["Description"] = f'Number of Chassis attached to {domain_name}.'
        polVars["varInput"] = f'Enter the Number of Chassis attached to {domain_name}:'
        polVars["varDefault"] = 1
        polVars["varName"] = 'Chassis Count'
        polVars["minNum"] = 1
        polVars["maxNum"] = 20
        chassis_count = ezfunctions.varNumberLoop(**polVars)

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        rangex = int(chassis_count) + 1
        for x in range(1,rangex):
            # Chassis Model
            polVars["multi_select"] = False
            jsonVars = ezData['policies']['thermal.Policy']
            polVars["var_description"] = jsonVars['chassisType']['description']
            polVars["jsonVars"] = sorted(jsonVars['chassisType']['enum'])
            polVars["defaultVar"] = jsonVars['chassisType']['default']
            polVars["varType"] = 'Chassis Model'
            chassis_model = ezfunctions.variablesFromAPI(**polVars)

            # Set Default Policy Values
            polVars["imc_access_policy"] = polVars["org"]
            polVars["power_policy"] = chassis_model
            polVars["snmp_policy"] = polVars["org"]
            polVars["thermal_policy"] = chassis_model
            polVars["name"] = f'{domain_name}-{x}'
            polVars["descr"] = f'{domain_name}-{x} Chassis Profile.'

            # Obtain Chassis Serial Number or Skip
            polVars["Description"] = 'Serial Number of the Chassis to assign to the Profile.'
            polVars["varDefault"] = ''
            polVars["varInput"] = f'What is the Serial Number of Chassis {x}? [press enter to skip]:'
            polVars["varName"] = 'Serial Number'
            polVars["varRegex"] = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
            polVars["minLength"] = 11
            polVars["maxLength"] = 11
            polVars['serial_number'] = ezfunctions.varStringLoop(**polVars)

            # Write Policies to Template File
            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
            ezfunctions.write_to_template(self, **polVars)

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Quick Start - UCS Domain Profile Module
    #==============================================
    def quick_start_domain(self, **polVars):
        org = self.org
        policy_type = 'UCS Domain Profile'
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ucs_domain_profiles'

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        # Write Policies to Template File
        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
        ezfunctions.write_to_template(self, **polVars)

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # Quick Start - UCS Server Profile Module
    #==============================================
    def quick_start_server_profiles(self, jsonData, ezData, **polVars):
        org = self.org
        policy_type = 'UCS Server Profile'
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ucs_server_profiles'

        polVars["Description"] = f'Number of Server Profiles.'
        polVars["varInput"] = f'Enter the Number of Server Profiles to Create:'
        polVars["varDefault"] = 1
        polVars["varName"] = 'Server Count'
        polVars["minNum"] = 1
        polVars["maxNum"] = 160
        server_count = ezfunctions.varNumberLoop(**polVars)

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

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
            polVars["name"] = name

            # Set Default Policy Values
            polVars["descr"] = f'{polVars["name"]} Server Profile'
            polVars["ucs_server_profile_template"] = f'{polVars["boot_order_policy"]}'

            # Obtain Server Serial Number or Skip
            polVars["Description"] = f'Serial Number of the Server Profile {polVars["name"]}.'
            polVars["varDefault"] = ''
            polVars["varInput"] = f'What is the Serial Number of {polVars["name"]}? [press enter to skip]:'
            polVars["varName"] = 'Serial Number'
            polVars["varRegex"] = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
            polVars["minLength"] = 11
            polVars["maxLength"] = 11
            polVars['serial_number'] = ezfunctions.varStringLoop(**polVars)

            if not polVars['serial_number'] == '':
                polVars["server_assignment_mode"] = 'Static'
            else:
                polVars["server_assignment_mode"] = 'None'

            polVars["multi_select"] = False
            # Generation of UCS Server
            jsonVars = ezData['policies']['server.Generation']
            polVars["var_description"] = jsonVars['systemType']['description']
            polVars["jsonVars"] = sorted(jsonVars['systemType']['enum'])
            polVars["defaultVar"] = jsonVars['systemType']['default']
            polVars["varType"] = 'Generation of UCS Server'
            ucs_generation = ezfunctions.variablesFromAPI(**polVars)

            if ucs_generation == 'M5':
                # Trusted Platform Module
                polVars["Description"] = 'Flag to Determine if the Server has TPM Installed.'
                polVars["varInput"] = f'Is a Trusted Platform Module installed in this Server and do you want to enable secure-boot?'
                polVars["varDefault"] = 'N'
                polVars["varName"] = 'TPM Installed'
                tpm_installed = ezfunctions.varBoolLoop(**polVars)
            else:
                tpm_installed = True

            if ucs_generation == 'M5' and tpm_installed == True:
                polVars["bios_policy"] = 'M5_VMware_tpm'
            elif ucs_generation == 'M5':
                polVars["bios_policy"] = 'M5_VMware'
            elif ucs_generation == 'M6':
                polVars["bios_policy"] = 'M6_VMware_tpm'

            # Write Policies to Template File
            polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
            ezfunctions.write_to_template(self, **polVars)

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==================================================
    # Quick Start - UCS Server Profile Template Module
    #==================================================
    def quick_start_server_templates(self, **polVars):
        org = self.org
        policy_type = 'UCS Server Profile Template'
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ucs_server_profile_templates'

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        # Set Default Policy Values
        polVars["name"] = f'{polVars["boot_order_policy"]}'
        polVars["descr"] = f'{polVars["name"]} Server Profile Template'

        polVars["uuid_pool"] = 'VMware'
        polVars["bios_policy"] = 'M6_VMware'
        polVars["boot_policy"] = f'{polVars["boot_order_policy"]}'
        polVars["virtual_media_policy"] = ''
        polVars["ipmi_over_lan_policy"] = f'{org}'
        polVars["local_user_policy"] = f'{org}'
        polVars["serial_over_lan_policy"] = f'{org}'
        polVars["snmp_policy"] = f'{org}'
        polVars["syslog_policy"] = f'{org}'
        polVars["virtual_kvm_policy"] = f'{org}'
        polVars["sd_card_policy"] = ''
        if re.search('VMware_M2', polVars["boot_order_policy"]):
            polVars["storage_policy"] = 'M2_Raid'
        elif polVars["boot_order_policy"] == 'VMware_Raid1':
            polVars["storage_policy"] = 'MRAID'
        elif polVars["boot_order_policy"] == 'VMware_PXE':
            polVars["storage_policy"] = ''
        polVars["lan_connectivity_policy"] = 'VMware_LAN'
        if len(polVars["fc_ports"]) > 0:
            polVars["san_connectivity_policy"] = 'VMware_SAN'

        if polVars["server_type"] == 'FIAttached':
            polVars["certificate_management_policy"] = ''
            polVars["imc_access_policy"] = f'{org}'
            polVars["power_policy"] = 'Server'
            polVars["target_platform"] = 'FIAttached'

        if polVars["server_type"] == 'Standalone':
            polVars["adapter_configuration_policy"] = f'{org}'
            polVars["device_connector_policy"] = f'{org}'
            polVars["ldap_policy"] = f'{org}'
            polVars["network_connectivity_policy"] = f'{org}'
            polVars["ntp_policy"] = f'{org}'
            polVars["persistent_memory_policy"] = f'{org}'
            polVars["smtp_policy"] = f'{org}'
            polVars["ssh_policy"] = f'{org}'
            polVars["target_platform"] = 'Standalone'

        # Write Policies to Template File
        polVars["template_file"] = '%s.jinja2' % (polVars["template_type"])
        ezfunctions.write_to_template(self, **polVars)

        # Close the Template file
        polVars["template_file"] = 'template_close.jinja2'
        ezfunctions.write_to_template(self, **polVars)

    #==============================================
    # UCS Chassis Profile Module
    #==============================================
    def ucs_chassis_profiles(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'chassis'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'UCS Chassis Profile'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ucs_chassis_profiles'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

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

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    polVars["multi_select"] = False
                    jsonVars = ezData['profiles']
                    polVars["var_description"] = jsonVars['action']['description']
                    polVars["jsonVars"] = sorted(jsonVars['action']['enum'])
                    polVars["defaultVar"] = jsonVars['action']['default']
                    polVars["varType"] = 'Action'
                    polVars["action"] = ezfunctions.variablesFromAPI(**polVars)

                    valid = False
                    while valid == False:
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  Note: If you do not have the Serial Number at this time you can manually add it to the:')
                        print(f'        - profiles/ucs_chassis_profiles.auto.tfvars file later.')
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        polVars["serial_number"] = input('What is the Serial Number of the Chassis? [press enter to skip]: ')
                        if polVars["serial_number"] == '':
                            valid = True
                        elif re.fullmatch(r'^[A-Z]{3}[2-3][\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\dA-Z]{4}$', polVars["serial_number"]):
                            valid = True
                        else:
                            print(f'\n-------------------------------------------------------------------------------------------\n')
                            print(f'  Error!! Invalid Serial Number.  "{polVars["serial_number"]}" is not a valid serial.')
                            print(f'\n-------------------------------------------------------------------------------------------\n')

                    policy_list = [
                        'policies.imc_access_policies.imc_access_policy',
                        'policies.power_policies.power_policy',
                        'policies.snmp_policies.snmp_policy',
                        'policies.thermal_policies.thermal_policy'
                    ]
                    polVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        polVars[policy_short],policyData = policy_select_loop(jsonData, ezData, name_prefix, policy, **polVars)
                        polVars.update(policyData)

                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    action            = "No-op"')
                    if not polVars["serial_number"] == '':
                        print(f'    assign_chassis    = True')
                    else:
                        print(f'    assign_chassis    = False')
                    print(f'    name              = "{polVars["name"]}"')
                    print(f'    imc_access_policy = "{polVars["imc_access_policy"]}"')
                    print(f'    power_policy      = "{polVars["power_policy"]}"')
                    print(f'    serial_number     = "{polVars["serial_number"]}"')
                    print(f'    snmp_policy       = "{polVars["snmp_policy"]}"')
                    print(f'    thermal_policy    = "{polVars["thermal_policy"]}"')
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
    # UCS Domain Profile Module
    #==============================================
    def ucs_domain_profiles(self, jsonData, ezData, policy_prefix, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'ucs'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'UCS Domain Profile'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ucs_domain_profiles'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

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

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    polVars["multi_select"] = False
                    jsonVars = ezData['profiles']
                    polVars["var_description"] = jsonVars['action']['description']
                    polVars["jsonVars"] = sorted(jsonVars['action']['enum'])
                    polVars["defaultVar"] = jsonVars['action']['default']
                    polVars["varType"] = 'Action'
                    polVars["action"] = ezfunctions.variablesFromAPI(**polVars)

                    serial_a,serial_b = ezfunctions.ucs_domain_serials()
                    polVars["serial_number_fabric_a"] = serial_a
                    polVars["serial_number_fabric_b"] = serial_b

                    policy_list = [
                        'policies.network_connectivity_policies.network_connectivity_policy',
                        'policies.ntp_policies.ntp_policy',
                        'policies.snmp_policies.snmp_policy',
                        'policies.switch_control_policies.switch_control_policy',
                        'policies.syslog_policies.syslog_policy',
                        'policies.system_qos_policies.system_qos_policy'
                    ]
                    polVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        if re.search(r'(switch_control|system_qos)', policy):
                            polVars[policy_short],policyData = policy_select_loop(jsonData, ezData, name_prefix, policy, **polVars)
                        else:
                            polVars[policy_short],policyData = policy_select_loop(jsonData, ezData, policy_prefix, policy, **polVars)
                        polVars.update(policyData)

                    policy_list = [
                        'policies.port_policies.port_policy',
                        'policies.vlan_policies.vlan_policy',
                        'policies.vsan_policies.vsan_policy'
                    ]
                    polVars["allow_opt_out"] = False
                    for policy in policy_list:
                        policy_long = policy.split('.')[1]
                        policy_short = policy.split('.')[2]
                        x = policy_short.split('_')
                        ezfunctions.policy_description = []
                        for y in x:
                            y = y.capitalize()
                            ezfunctions.policy_description.append(y)
                        ezfunctions.policy_description = " ".join(ezfunctions.policy_description)

                        polVars[policy_long] = {}
                        # polVars["policy"] = '%s Fabric A' % (ezfunctions.policy_description)
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  !!! Select the {ezfunctions.policy_description} for Fabric A !!!')
                        fabric_a,policyData = policy_select_loop(jsonData, ezData, name_prefix, policy, **polVars)
                        # polVars["policy"] = '%s Fabric B' % (ezfunctions.policy_description)
                        print(f'\n-------------------------------------------------------------------------------------------\n')
                        print(f'  !!! Select the {ezfunctions.policy_description} for Fabric B !!!')
                        fabric_b,policyData = policy_select_loop(jsonData, ezData, name_prefix, policy, **polVars)
                        polVars[policy_long].update({'fabric_a':fabric_a})
                        polVars[policy_long].update({'fabric_b':fabric_b})
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
                                polVars["device_model"] = device_model_a
                            else:
                                polVars["device_model"] = device_model_a


                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    action                      = "No-op"')
                    if not (polVars["serial_number_fabric_a"] == '' and polVars["serial_number_fabric_a"] == ''):
                        print(f'    assign_switches             = True')
                    else:
                        print(f'    assign_switches             = False')
                    print(f'    device_model                = "{polVars["device_model"]}"')
                    print(f'    name                        = "{polVars["name"]}"')
                    print(f'    network_connectivity_policy = "{polVars["network_connectivity_policy"]}"')
                    print(f'    ntp_policy                  = "{polVars["ntp_policy"]}"')
                    print(f'    port_policy_fabric_a        = "{polVars["port_policies"]["fabric_a"]}"')
                    print(f'    port_policy_fabric_b        = "{polVars["port_policies"]["fabric_b"]}"')
                    print(f'    serial_number_fabric_a      = "{polVars["serial_number_fabric_a"]}"')
                    print(f'    serial_number_fabric_b      = "{polVars["serial_number_fabric_b"]}"')
                    print(f'    snmp_policy                 = "{polVars["snmp_policy"]}"')
                    print(f'    switch_control_policy       = "{polVars["switch_control_policy"]}"')
                    print(f'    syslog_policy               = "{polVars["syslog_policy"]}"')
                    print(f'    system_qos_policy           = "{polVars["system_qos_policy"]}"')
                    print(f'    vlan_policy_fabric_a        = "{polVars["vlan_policies"]["fabric_a"]}"')
                    print(f'    vlan_policy_fabric_b        = "{polVars["vlan_policies"]["fabric_b"]}"')
                    print(f'    vsan_policy_fabric_a        = "{polVars["vsan_policies"]["fabric_a"]}"')
                    print(f'    vsan_policy_fabric_b        = "{polVars["vsan_policies"]["fabric_b"]}"')
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
    # UCS Server Profile Module
    #==============================================
    def ucs_server_profiles(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'server'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'UCS Server Profile'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ucs_server_profiles'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

        configure_loop = False
        while configure_loop == False:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            policy_loop = False
            while policy_loop == False:

                if not name_prefix == '':
                    name = '%s_%s' % (name_prefix, name_suffix)
                else:
                    name = '%s_%s' % (org, name_suffix)

                polVars["name"] = ezfunctions.policy_name(name, policy_type)
                polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                polVars["allow_opt_out"] = False
                polVars["multi_select"] = False
                jsonVars = ezData['profiles']
                polVars["var_description"] = jsonVars['action']['description']
                polVars["jsonVars"] = sorted(jsonVars['action']['enum'])
                polVars["defaultVar"] = jsonVars['action']['default']
                polVars["varType"] = 'Action'
                polVars["action"] = ezfunctions.variablesFromAPI(**polVars)


                jsonVars = jsonData['server.Profile']['allOf'][1]['properties']
                polVars["var_description"] = jsonVars['ServerAssignmentMode']['description']
                polVars["jsonVars"] = sorted(jsonVars['ServerAssignmentMode']['enum'])
                polVars["defaultVar"] = jsonVars['ServerAssignmentMode']['default']
                polVars["varType"] = 'Server Assignment Mode'
                polVars["server_assignment_mode"] = ezfunctions.variablesFromAPI(**polVars)

                if polVars["server_assignment_mode"] == 'Static':
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Note: If you do not have the Serial Number at this time you can manually add it to the:')
                    print(f'        - profiles/ucs_server_profiles.auto.tfvars file later.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    polVars["Description"] = 'Serial Number of the Physical Compute Resource to assign to the Profile.'
                    polVars["varDefault"] = ''
                    polVars["varInput"] = 'What is the Serial Number of the Server? [press enter to skip]:'
                    polVars["varName"] = 'Serial Number'
                    polVars["varRegex"] = '^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$'
                    polVars["minLength"] = 11
                    polVars["maxLength"] = 11
                    polVars['serial_number'] = ezfunctions.varStringLoop(**polVars)
                elif polVars["server_assignment_mode"] == 'Pool':
                    policy_list = [
                        'pools.resource_pools.resource_pool'
                    ]
                    polVars["allow_opt_out"] = False
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        polVars[policy_short],policyData = policy_select_loop(jsonData, ezData, name_prefix, policy, **polVars)
                        polVars.update(policyData)
                        server_template = True
                        valid = True

                valid = False
                while valid == False:
                    server_template = input('Do you want to Associate to a UCS Server Profile Template?  Enter "Y" or "N" [Y]: ')
                    if server_template == '' or server_template == 'Y':
                        policy_list = [
                            'profiles.ucs_server_profile_templates.ucs_server_profile_template'
                        ]
                        polVars["allow_opt_out"] = False
                        for policy in policy_list:
                            policy_short = policy.split('.')[2]
                            polVars[policy_short],policyData = policy_select_loop(jsonData, ezData, name_prefix, policy, **polVars)
                            polVars.update(policyData)
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
                    polVars["multi_select"] = False
                    jsonVars = jsonData['server.BaseProfile']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['TargetPlatform']['description']
                    polVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    polVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                    polVars["varType"] = 'Target Platform'
                    polVars["target_platform"] = ezfunctions.variablesFromAPI(**polVars)

                    #___________________________________________________________________________
                    #
                    # Policies On Hold for Right Now
                    # 'policies.certificate_management_policies.certificate_management_policy',
                    #___________________________________________________________________________
                    polVars["uuid_pool"] = ''
                    polVars["static_uuid_address"] = ''
                    if polVars["target_platform"] == 'FIAttached':
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
                    elif polVars["target_platform"] == 'Standalone':
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
                            'policies.ldap_policies.ldap_policy',
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
                    polVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        polVars[policy_short],policyData = policy_select_loop(jsonData, ezData, name_prefix, policy, **polVars)
                        polVars.update(policyData)

                polVars["boot_policy"] = polVars["boot_order_policy"]
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'    action          = "{polVars["action"]}"')
                print(f'    description     = "{polVars["descr"]}"')
                print(f'    name            = "{polVars["name"]}"')
                if polVars["server_assignment_mode"] == 'Pool':
                    print(f'    resource_pool   = {polVars["resource_pool"]}')
                if polVars["server_assignment_mode"] == 'Static':
                    print(f'    serial_number   = "{polVars["serial_number"]}"')
                if server_template == True:
                    print(f'    ucs_server_profile_template = "{polVars["ucs_server_profile_template"]}"')
                if server_template == False:
                    print(f'    target_platform = "{polVars["target_platform"]}"')
                if server_template == False:
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Compute Configuration')
                    print(f'    #___________________________"')
                    if not polVars["static_uuid_address"] == '':
                        print(f'    static_uuid_address        = "{polVars["static_uuid_address"]}"')
                    if not polVars["uuid_pool"] == '':
                        print(f'    uuid_pool                  = "{polVars["uuid_pool"]}"')
                    print(f'    bios_policy                = "{polVars["bios_policy"]}"')
                    print(f'    boot_order_policy          = "{polVars["boot_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    persistent_memory_policies = "{polVars["persistent_memory_policy"]}"')
                    if polVars["target_platform"] == 'FIAttached':
                        print(f'    power_policy               = "{polVars["power_policy"]}"')
                    print(f'    virtual_media_policy       = "{polVars["virtual_media_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Management Configuration')
                    print(f'    #___________________________"')
                    # if target_platform == 'FIAttached':
                    #     print(f'    certificate_management_policy = "{polVars["pcertificate_management_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    device_connector_policy       = "{polVars["device_connector_policy"]}"')
                    if polVars["target_platform"] == 'FIAttached':
                        print(f'    imc_access_policy             = "{polVars["imc_access_policy"]}"')
                    print(f'    ipmi_over_lan_policy          = "{polVars["ipmi_over_lan_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    ldap_policy                   = "{polVars["ldap_policy"]}"')
                    print(f'    local_user_policy             = "{polVars["local_user_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    network_connectivity_policy   = "{polVars["network_connectivity_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    ntp_policy                    = "{polVars["ntp_policy"]}"')
                    print(f'    serial_over_lan_policy        = "{polVars["serial_over_lan_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    smtp_policy                   = "{polVars["smtp_policy"]}"')
                    print(f'    snmp_policy                   = "{polVars["snmp_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    ssh_policy                    = "{polVars["ssh_policy"]}"')
                    print(f'    syslog_policy                 = "{polVars["syslog_policy"]}"')
                    print(f'    virtual_kvm_policy            = "{polVars["virtual_kvm_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Storage Configuration')
                    print(f'    #___________________________"')
                    print(f'    sd_card_policy = "{polVars["sd_card_policy"]}"')
                    print(f'    storage_policy = "{polVars["storage_policy"]}"')
                    print(f'    #___________________________"')
                    print(f'    #')
                    print(f'    # Network Configuration')
                    print(f'    #___________________________"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    adapter_configuration_policy = "{polVars["adapter_configuration_policy"]}"')
                    print(f'    lan_connectivity_policy      = "{polVars["lan_connectivity_policy"]}"')
                    print(f'    san_connectivity_policy      = "{polVars["san_connectivity_policy"]}"')
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
    # UCS Server Profile Template Module
    #==============================================
    def ucs_server_profile_templates(self, jsonData, ezData, **kwargs):
        name_prefix = self.name_prefix
        name_suffix = 'template'
        opSystem = kwargs['opSystem']
        org = self.org
        policy_type = 'UCS Server Profile Template'
        polVars = {}
        polVars["header"] = '%s Variables' % (policy_type)
        polVars["initial_write"] = True
        polVars["org"] = org
        polVars["policy_type"] = policy_type
        polVars["template_file"] = 'template_open.jinja2'
        polVars["template_type"] = 'ucs_server_profile_templates'
        tfDir = kwargs['tfDir']

        # Open the Template file
        ezfunctions.write_to_template(self, **polVars)
        polVars["initial_write"] = False

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

                    polVars["name"] = ezfunctions.policy_name(name, policy_type)
                    polVars["descr"] = ezfunctions.policy_descr(polVars["name"], policy_type)

                    polVars["multi_select"] = False
                    jsonVars = jsonData['server.BaseProfile']['allOf'][1]['properties']
                    polVars["var_description"] = jsonVars['TargetPlatform']['description']
                    polVars["jsonVars"] = sorted(jsonVars['TargetPlatform']['enum'])
                    polVars["defaultVar"] = jsonVars['TargetPlatform']['default']
                    polVars["varType"] = 'Target Platform'
                    polVars["target_platform"] = ezfunctions.variablesFromAPI(**polVars)

                    #___________________________________________________________________________
                    #
                    # Policies On Hold for Right Now
                    # 'policies.certificate_management_policies.certificate_management_policy',
                    #___________________________________________________________________________
                    if polVars["target_platform"] == 'FIAttached':
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
                    elif polVars["target_platform"] == 'Standalone':
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
                    polVars["allow_opt_out"] = True
                    for policy in policy_list:
                        policy_short = policy.split('.')[2]
                        polVars[policy_short],policyData = policy_select_loop(jsonData, ezData, name_prefix, policy, **polVars)
                        polVars.update(policyData)

                    polVars["boot_policy"] = polVars["boot_order_policy"]
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'    description     = "{polVars["descr"]}"')
                    print(f'    name            = "{polVars["name"]}"')
                    print(f'    target_platform = "{polVars["target_platform"]}"')
                    print(f'    #___________________________')
                    print(f'    #')
                    print(f'    # Compute Configuration')
                    print(f'    #___________________________')
                    if polVars["target_platform"] == 'FIAttached':
                        print(f'    uuid_pool                  = "{polVars["uuid_pool"]}"')
                    print(f'    bios_policy                = "{polVars["bios_policy"]}"')
                    print(f'    boot_order_policy          = "{polVars["boot_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    persistent_memory_policies = "{polVars["persistent_memory_policy"]}"')
                    if polVars["target_platform"] == 'FIAttached':
                        print(f'    power_policy               = "{polVars["power_policy"]}"')
                    print(f'    virtual_media_policy       = "{polVars["virtual_media_policy"]}"')
                    print(f'    #___________________________')
                    print(f'    #')
                    print(f'    # Management Configuration')
                    print(f'    #___________________________')
                    # if target_platform == 'FIAttached':
                    #     print(f'    certificate_management_policy = "{polVars["certificate_management_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    device_connector_policies     = "{polVars["device_connector_policy"]}"')
                    if polVars["target_platform"] == 'FIAttached':
                        print(f'    imc_access_policy             = "{polVars["imc_access_policy"]}"')
                    print(f'    ipmi_over_lan_policy          = "{polVars["ipmi_over_lan_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    ldap_policies                 = "{polVars["ldap_policy"]}"')
                    print(f'    local_user_policy             = "{polVars["local_user_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    network_connectivity_policy   = "{polVars["network_connectivity_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    ntp_policy                    = "{polVars["ntp_policy"]}"')
                    print(f'    serial_over_lan_policy        = "{polVars["serial_over_lan_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    smtp_policy                   = "{polVars["smtp_policy"]}"')
                    print(f'    snmp_policy                   = "{polVars["snmp_policy"]}"')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    ssh_policy                    = "{polVars["ssh_policy"]}"')
                    print(f'    syslog_policy                 = "{polVars["syslog_policy"]}"')
                    print(f'    virtual_kvm_policy            = "{polVars["virtual_kvm_policy"]}"')
                    print(f'    #___________________________')
                    print(f'    #')
                    print(f'    # Storage Configuration')
                    print(f'    #___________________________')
                    print(f'    sd_card_policy = "{polVars["sd_card_policy"]}"')
                    print(f'    storage_policy = "{polVars["storage_policy"]}"')
                    print(f'    #___________________________')
                    print(f'    #')
                    print(f'    # Network Configuration')
                    print(f'    #___________________________')
                    if polVars["target_platform"] == 'Standalone':
                        print(f'    adapter_configuration_policy = "{polVars["adapter_configuration_policy"]}"')
                    print(f'    lan_connectivity_policy      = "{polVars["lan_connectivity_policy"]}"')
                    print(f'    san_connectivity_policy      = "{polVars["san_connectivity_policy"]}"')
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
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Ipmi', 'IPMI')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Ip', 'IP')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Iqn', 'IQN')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Ldap', 'LDAP')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Ntp', 'NTP')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Sd', 'SD')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Smtp', 'SMTP')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Snmp', 'SNMP')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Ssh', 'SSH')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Wwnn', 'WWNN')
                ezfunctions.policy_description = ezfunctions.policy_description.replace('Wwpn', 'WWPN')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There were no {ezfunctions.policy_description} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

                if 'Policies' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Policies', 'Policy')
                elif 'Pools' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Pools', 'Pool')
                elif 'Profiles' in ezfunctions.policy_description:
                    ezfunctions.policy_description = ezfunctions.policy_description.replace('Profiles', 'Profile')
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
            if inner_policy == 'ip_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).ip_pools(jsonData, ezData, **kwargs)
            elif inner_policy == 'iqn_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).iqn_pools(jsonData, ezData, **kwargs)
            elif inner_policy == 'mac_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).mac_pools(jsonData, ezData, **kwargs)
            elif inner_policy == 'uuid_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).uuid_pools(jsonData, ezData, **kwargs)
            elif inner_policy == 'wwnn_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).wwnn_pools(jsonData, ezData, **kwargs)
            elif inner_policy == 'wwpn_pools':
                pools.pools(name_prefix, polVars["org"], inner_type).wwpn_pools(jsonData, ezData, **kwargs)
            elif inner_policy == 'adapter_configuration_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).adapter_configuration_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'bios_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).bios_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'boot_order_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).boot_order_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'certificate_management_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).certificate_management_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'device_connector_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).device_connector_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'ethernet_adapter_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).ethernet_adapter_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'ethernet_network_control_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).ethernet_network_control_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'ethernet_network_group_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).ethernet_network_group_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'ethernet_network_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).ethernet_network_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'ethernet_qos_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).ethernet_qos_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'fibre_channel_adapter_policies':
                san.policies(name_prefix, polVars["org"], inner_type).fibre_channel_adapter_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'fibre_channel_network_policies':
                san.policies(name_prefix, polVars["org"], inner_type).fibre_channel_network_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'fibre_channel_qos_policies':
                san.policies(name_prefix, polVars["org"], inner_type).fibre_channel_qos_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'flow_control_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).flow_control_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'imc_access_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).imc_access_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'ipmi_over_lan_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).ipmi_over_lan_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'iscsi_adapter_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).iscsi_adapter_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'iscsi_boot_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).iscsi_boot_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'iscsi_static_target_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).iscsi_static_target_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'lan_connectivity_policies':
                lan.policies(name_prefix, polVars["org"], inner_type).lan_connectivity_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'ldap_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).ldap_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'link_aggregation_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).link_aggregation_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'link_control_policies':
                p1.policies(name_prefix, polVars["org"], inner_type).link_control_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'local_user_policies':
                p2.policies(name_prefix, polVars["org"], inner_type).local_user_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'multicast_policies':
                vxan.policies(name_prefix, polVars["org"], inner_type).multicast_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'network_connectivity_policies':
                p2.policies(name_prefix, polVars["org"], inner_type).network_connectivity_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'ntp_policies':
                p2.policies(name_prefix, polVars["org"], inner_type).ntp_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'persistent_memory_policies':
                p2.policies(name_prefix, polVars["org"], inner_type).persistent_memory_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'port_policies':
                p2.policies(name_prefix, polVars["org"], inner_type).port_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'power_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).power_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'san_connectivity_policies':
                san.policies(name_prefix, polVars["org"], inner_type).san_connectivity_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'sd_card_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).sd_card_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'serial_over_lan_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).serial_over_lan_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'smtp_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).smtp_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'snmp_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).snmp_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'ssh_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).ssh_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'storage_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).storage_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'switch_control_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).switch_control_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'syslog_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).syslog_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'system_qos_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).system_qos_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'thermal_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).thermal_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'ucs_server_profiles':
                profiles(name_prefix, polVars["org"], inner_type).ucs_server_profiles(jsonData, ezData, **kwargs)
            elif inner_policy == 'ucs_server_profile_templates':
                profiles(name_prefix, polVars["org"], inner_type).ucs_server_profile_templates(jsonData, ezData, **kwargs)
            elif inner_policy == 'virtual_kvm_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).virtual_kvm_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'virtual_media_policies':
                p3.policies(name_prefix, polVars["org"], inner_type).virtual_media_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'vlan_policies':
                vxan.policies(name_prefix, polVars["org"], inner_type).vlan_policies(jsonData, ezData, **kwargs)
            elif inner_policy == 'vsan_policies':
                vxan.policies(name_prefix, polVars["org"], inner_type).vsan_policies(jsonData, ezData, **kwargs)
