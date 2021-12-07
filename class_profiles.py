#!/usr/bin/env python3

import jinja2
import pkg_resources
import re
from easy_functions import exit_default_no
from easy_functions import policy_descr, policy_name
from easy_functions import policy_select_loop
from easy_functions import ucs_domain_serials
from easy_functions import variablesFromAPI
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
                        'policies_vlans.vlan_policies.vlan_policy',
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
                    print(f'    boot_order_policy          = "{templateVars["boot_order_policy"]}"')
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
                    print(f'    boot_order_policy          = "{templateVars["boot_order_policy"]}"')
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
