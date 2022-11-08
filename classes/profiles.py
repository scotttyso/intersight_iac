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

def policy_select_loop(**kwargs):
    ezData = kwargs['ezData']
    policy = kwargs['policy']
    name_prefix = kwargs['name_prefix']
    org = kwargs['org']
    loop_valid = False
    while loop_valid == False:
        create_policy = True
        kwargs['inner_policy'] = policy.split('.')[1]
        kwargs['inner_type']   = policy.split('.')[0]
        kwargs['inner_var']    = policy.split('.')[2]
        inner_policy = kwargs['inner_policy']
        inner_type   = kwargs['inner_type']
        kwargs = ezfunctions.policies_parse(inner_type, inner_policy, **kwargs)
        if not len(kwargs["policies"]) > 0:
            valid = False
            while valid == False:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'   There was no {inner_policy} found.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                policy_description = ezfunctions.mod_pol_description(inner_policy)
                if kwargs["allow_opt_out"] == True:
                    Question = input(f'Do you want to create a(n) {policy_description}?  Enter "Y" or "N" [Y]: ')
                    if Question == '' or Question == 'Y':
                        create_policy = True
                        valid = True
                    elif Question == 'N':
                        create_policy = False
                        valid = True
                        return kwargs
                else:
                    create_policy = True
                    valid = True
        else:
            kwargs = ezfunctions.choose_policy(inner_policy, **kwargs)
            if kwargs['policy'] == 'create_policy': create_policy = True
            elif kwargs['policy'] == '' and kwargs["allow_opt_out"] == True:
                loop_valid = True
                create_policy = False
                kwargs[kwargs['inner_var']] = ''
                return kwargs
            elif not kwargs['policy'] == '':
                loop_valid = True
                create_policy = False
                kwargs[kwargs['inner_var']] = kwargs['policy']
                return kwargs

        # Simple Loop to show name_prefix in Use
        ncount = 0
        if ncount == 5: print(name_prefix)
        
        # Create Policy if Option was Selected
        if create_policy == True:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Starting module to create {inner_policy} in {org}')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            lan_list = ezData['ezimm']['allOf'][1]['properties']['lan_list']
            p1_list = ezData['ezimm']['allOf'][1]['properties']['p1_list']
            p2_list = ezData['ezimm']['allOf'][1]['properties']['p2_list']
            p3_list = ezData['ezimm']['allOf'][1]['properties']['p3_list']
            san_list = ezData['ezimm']['allOf'][1]['properties']['san_list']
            vxan_list = ezData['ezimm']['allOf'][1]['properties']['vxan_list']
            profile_list = ['ucs_server_profiles', 'ucs_server_profile_templates']
            if re.search('pools$', inner_policy):
                kwargs = eval(f"pools.pools(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in p1_list:
                kwargs = eval(f"p1.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in p2_list:
                kwargs = eval(f"p2.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in p3_list:
                kwargs = eval(f"p3.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in lan_list:
                kwargs = eval(f"lan.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in san_list:
                kwargs = eval(f"san.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in vxan_list:
                kwargs = eval(f"vxan.policies(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
            elif inner_policy in profile_list:
                kwargs = eval(f"profiles(name_prefix, org, inner_type).{inner_policy}(**kwargs)")
