#!/usr/bin/env python3
import json
import subprocess
import os
import re
import requests
import sys
import validating
from easy_functions import policies_parse
from easy_functions import varBoolLoop
from easy_functions import variablesFromAPI
from easy_functions import varStringLoop
from class_imm_transition import imm_transition
from class_pools import pools
from class_policies_domain import policies_domain
from class_policies_lan import policies_lan
from class_policies_san import policies_san
from class_policies_p1 import policies_p1
from class_policies_p2 import policies_p2
from class_profiles import profiles
from class_quick_start import quick_start
from class_terraform import terraform_cloud
from io import StringIO
from lxml import etree
from pathlib import Path

home = Path.home()

def create_terraform_workspaces(jsonData, easy_jsonData, org):
    tfcb_config = []
    valid = False
    while valid == False:
        templateVars = {}
        templateVars["Description"] = 'Terraform Cloud Workspaces'
        templateVars["varInput"] = f'Do you want to Proceed with creating Workspaces in Terraform Cloud?'
        templateVars["varDefault"] = 'Y'
        templateVars["varName"] = 'Terraform Cloud Workspaces'
        runTFCB = varBoolLoop(**templateVars)
        valid = True
    if runTFCB == True:
        templateVars = {}
        templateVars["terraform_cloud_token"] = terraform_cloud().terraform_token()
        templateVars["tfc_organization"] = terraform_cloud().tfc_organization(**templateVars)
        tfcb_config.append({'tfc_organization':templateVars["tfc_organization"]})
        tfc_vcs_provider,templateVars["tfc_oath_token"] = terraform_cloud().tfc_vcs_providers(**templateVars)
        templateVars["tfc_vcs_provider"] = tfc_vcs_provider
        templateVars["vcsBaseRepo"] = terraform_cloud().tfc_vcs_repository(**templateVars)

        templateVars["agentPoolId"] = ''
        templateVars["allowDestroyPlan"] = False
        templateVars["executionMode"] = 'remote'
        templateVars["queueAllRuns"] = False
        templateVars["speculativeEnabled"] = True
        templateVars["triggerPrefixes"] = []

        terraform_versions = []
        url = f'https://releases.hashicorp.com/terraform/'
        r = requests.get(url)
        html = r.content.decode("utf-8")
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html), parser=parser)
        # This will get the anchor tags <a href...>
        refs = tree.xpath("//a")
        links = [link.get('href', '') for link in refs]
        for i in links:
            if re.search(r'/terraform/[1-2]\.[0-9]+\.[0-9]+/', i):
                tf_version = re.search(r'/terraform/([1-2]\.[0-9]+\.[0-9]+)/', i).group(1)
                terraform_versions.append(tf_version)

        templateVars["multi_select"] = False
        templateVars["var_description"] = "Terraform Version for Workspaces:"
        templateVars["jsonVars"] = sorted(terraform_versions)
        templateVars["varType"] = 'Terraform Version'
        templateVars["defaultVar"] = ''
        templateVars["terraformVersion"] = variablesFromAPI(**templateVars)
        # templateVars["terraformVersion"] = '1.0.9'

        folder_list = [
            f'./Intersight/{org}/policies',
            f'./Intersight/{org}/policies_vlans',
            f'./Intersight/{org}/pools',
            f'./Intersight/{org}/ucs_chassis_profiles',
            f'./Intersight/{org}/ucs_domain_profiles',
            f'./Intersight/{org}/ucs_server_profiles'
        ]
        for folder in folder_list:
            templateVars["autoApply"] = False
            templateVars["Description"] = f'Intersight Organization {org} - %s' % (folder.split('/')[3])
            if re.search('(pools|profiles)', folder.split('/')[3]):
                templateVars["globalRemoteState"] = True
            else:
                templateVars["globalRemoteState"] = False
            templateVars["workingDirectory"] = folder

            templateVars["Description"] = 'Name of the Workspace to Create in Terraform Cloud'
            templateVars["varDefault"] = f'{org}_{folder.split("/")[3]}'
            templateVars["varInput"] = f'Terraform Cloud Workspace Name. [{org}_{folder.split("/")[3]}]: '
            templateVars["varName"] = f'Workspace Name'
            templateVars["varRegex"] = '^[a-zA-Z0-9\\-\\_]+$'
            templateVars["minLength"] = 1
            templateVars["maxLength"] = 90
            templateVars["workspaceName"] = varStringLoop(**templateVars)
            tfcb_config.append({folder.split('/')[3]:templateVars["workspaceName"]})
            # templateVars["vcsBranch"] = ''


            templateVars['workspace_id'] = terraform_cloud().tfcWorkspace(**templateVars)
            vars = [
                'apikey.Intersight API Key',
                'secretkey.Intersight Secret Key'
            ]
            for var in vars:
                templateVars["Variable"] = var.split('.')[0]
                if 'secret' in var:
                    templateVars["Multi_Line_Input"] = True
                templateVars["varValue"] = terraform_cloud().sensitive_var_value(jsonData, **templateVars)
                templateVars["varId"] = var.split('.')[0]
                templateVars["varKey"] = var.split('.')[0]
                templateVars["Description"] = var.split('.')[1]
                templateVars["Sensitive"] = True
                terraform_cloud().tfcVariables(**templateVars)

            if folder.split("/")[3] == 'policies':
                templateVars["Multi_Line_Input"] = False
                vars = [
                    'ipmi_over_lan_policies.ipmi_key',
                    'iscsi_boot_policies.password',
                    'ldap_policies.binding_password',
                    'local_user_policies.local_user_password',
                    'persistent_memory_policies.secure_passphrase',
                    'snmp_policies.access_community_string',
                    'snmp_policies.password',
                    'snmp_policies.trap_community_string',
                    'virtual_media_policies.vmedia_password'
                ]
                sensitive_vars = []
                for var in vars:
                    policy_type = 'policies'
                    policy = '%s' % (var.split('.')[0])
                    policies,json_data = policies_parse(org, policy_type, policy)
                    y = var.split('.')[0]
                    z = var.split('.')[1]
                    if y == 'persistent_memory_policies':
                        if len(policies) > 0:
                            sensitive_vars.append(z)
                    else:
                        for keys, values in json_data.items():
                            for item in values:
                                for key, value in item.items():
                                    for i in value:
                                        for k, v in i.items():
                                            if k == z:
                                                if not v == 0:
                                                    if y == 'iscsi_boot_policies':
                                                        varValue = 'iscsi_boot_password'
                                                    else:
                                                        varValue = '%s_%s' % (k, v)
                                                    sensitive_vars.append(varValue)
                                            elif k == 'binding_parameters':
                                                for itema in v:
                                                    for ka, va in itema.items():
                                                        if ka == 'bind_method':
                                                            if va == 'ConfiguredCredentials':
                                                                sensitive_vars.append('binding_parameters_password')
                                            elif k == 'local_users' or k == 'vmedia_mappings':
                                                for itema in v:
                                                    for ka, va in itema.items():
                                                        for itemb in va:
                                                            for kb, vb in itemb.items():
                                                                if kb == 'password':
                                                                    varValue = '%s_%s' % (z, vb)
                                                                    sensitive_vars.append(varValue)
                                            elif k == 'snmp_users' and z == 'password':
                                                for itema in v:
                                                    for ka, va in itema.items():
                                                        for itemb in va:
                                                            for kb, vb in itemb.items():
                                                                if kb == 'auth_password':
                                                                    varValue = 'snmp_auth_%s_%s' % (z, vb)
                                                                    sensitive_vars.append(varValue)
                                                                elif kb == 'privacy_password':
                                                                    varValue = 'snmp_privacy_%s_%s' % (z, vb)
                                                                    sensitive_vars.append(varValue)
                for var in sensitive_vars:
                    templateVars["Variable"] = var
                    if 'ipmi_key' in var:
                        templateVars["Description"] = 'IPMI over LAN Encryption Key'
                    elif 'iscsi' in var:
                        templateVars["Description"] = 'iSCSI Boot Password'
                    elif 'local_user' in var:
                        templateVars["Description"] = 'Local User Password'
                    elif 'access_comm' in var:
                        templateVars["Description"] = 'SNMP Access Community String'
                    elif 'snmp_auth' in var:
                        templateVars["Description"] = 'SNMP Authorization Password'
                    elif 'snmp_priv' in var:
                        templateVars["Description"] = 'SNMP Privacy Password'
                    elif 'trap_comm' in var:
                        templateVars["Description"] = 'SNMP Trap Community String'
                    templateVars["varValue"] = terraform_cloud().sensitive_var_value(jsonData, **templateVars)
                    templateVars["varId"] = var
                    templateVars["varKey"] = var
                    templateVars["Sensitive"] = True
                    terraform_cloud().tfcVariables(**templateVars)

        tfcb_config.append({'org':org})
        for folder in folder_list:
            name_prefix = 'dummy'
            type = 'pools'
            policies(name_prefix, org, type).intersight(easy_jsonData, tfcb_config)
            type = 'policies'
            policies(name_prefix, org, type).intersight(easy_jsonData, tfcb_config)
            type = 'policies_vlans'
            policies(name_prefix, org, type).intersight(easy_jsonData, tfcb_config)
            type = 'ucs_chassis_profiles'
            policies(name_prefix, org, type).intersight(easy_jsonData, tfcb_config)
            type = 'ucs_domain_profiles'
            policies(name_prefix, org, type).intersight(easy_jsonData, tfcb_config)
            type = 'ucs_server_profiles'
            policies(name_prefix, org, type).intersight(easy_jsonData, tfcb_config)


    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Proceedures Complete!!! Closing Environment and Exiting Script.')
    print(f'\n-------------------------------------------------------------------------------------------\n')

def merge_easy_imm_repository(easy_jsonData, org):
    folder_list = [
        f'./Intersight/{org}/policies',
        f'./Intersight/{org}/policies_vlans',
        f'./Intersight/{org}/pools',
        f'./Intersight/{org}/ucs_chassis_profiles',
        f'./Intersight/{org}/ucs_domain_profiles',
        f'./Intersight/{org}/ucs_server_profiles'
    ]
    for folder in folder_list:
        if os.path.isdir(folder):
            folder_type = folder.split('/')[3]
            files = easy_jsonData['wizard']['files'][folder_type]
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'\n  Beginning Easy IMM Module Downloads for "{folder}"\n')
            for file in files:
                dest_file = f'{folder}/{file}'
                if not os.path.isfile(dest_file):
                    print(f'  Downloading "{file}" to "{folder}"')
                    url = f'https://raw.github.com/terraform-cisco-modules/terraform-intersight-easy-imm/master/modules/{folder_type}/{file}'
                    r = requests.get(url)
                    open(dest_file, 'wb').write(r.content)
                    print(f'  Download Complete!\n')

            print(f'\n  Completed Easy IMM Module Downloads for "{folder}"')
            print(f'\n-------------------------------------------------------------------------------------------\n')

    for folder in folder_list:
        if os.path.isdir(folder):
            folder_type = folder.split('/')[3]
            files = easy_jsonData['wizard']['files'][folder_type]
            removeList = [
                'data_sources.tf',
                'locals.tf',
                'main.tf',
                'output.tf',
                'outputs.tf',
                'provider.tf',
                'README.md',
                'variables.tf',
            ]
            for xRemove in removeList:
                if xRemove in files:
                    files.remove(xRemove)
            for file in files:
                varFiles = f"{file.split('.')[0]}.auto.tfvars"
                dest_file = f'{folder}/{varFiles}'
                if not os.path.isfile(dest_file):
                    wr_file = open(dest_file, 'w')
                    x = file.split('.')
                    x2 = x[0].split('_')
                    varList = []
                    for var in x2:
                        var = var.capitalize()
                        if var == 'Policies':
                            var = 'Policy'
                        elif var == 'Pools':
                            var = 'Pool'
                        elif var == 'Profiles':
                            var = 'Profile'
                        varList.append(var)
                    varDescr = ' '.join(varList)
                    varDescr = varDescr + ' Variables'

                    wrString = f'#______________________________________________\n#\n# {varDescr}\n'\
                        '#______________________________________________\n'\
                        '\n%s = {\n}\n' % (file.split('.')[0])
                    wr_file.write(wrString)
                    wr_file.close()

            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Running "terraform fmt" in folder "{folder}",')
            print(f'  to correct variable formatting!')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            p = subprocess.Popen(
                ['terraform', 'fmt', folder],
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE
            )
            print('Format updated for the following Files:')
            for line in iter(p.stdout.readline, b''):
                line = line.decode("utf-8")
                line = line.strip()
                print(f'- {line}')

def process_imm_transition(json_data):
    print(f'\n---------------------------------------------------------------------------------------\n')
    print(f'  Starting the Easy IMM Transition Wizard!')
    print(f'\n---------------------------------------------------------------------------------------\n')

    type = 'pools'
    orgs = imm_transition(json_data, type).return_orgs()
    imm_transition(json_data, type).ip_pools()
    imm_transition(json_data, type).iqn_pools()
    imm_transition(json_data, type).mac_pools()
    imm_transition(json_data, type).uuid_pools()
    imm_transition(json_data, type).wwnn_pools()
    imm_transition(json_data, type).wwpn_pools()
    type = 'policies'
    imm_transition(json_data, type).bios_policies()
    imm_transition(json_data, type).boot_order_policies()
    imm_transition(json_data, type).ethernet_adapter_policies()
    imm_transition(json_data, type).ethernet_network_control_policies()
    imm_transition(json_data, type).ethernet_network_group_policies()
    imm_transition(json_data, type).ethernet_network_policies()
    imm_transition(json_data, type).ethernet_qos_policies()
    imm_transition(json_data, type).fibre_channel_adapter_policies()
    imm_transition(json_data, type).fibre_channel_network_policies()
    imm_transition(json_data, type).fibre_channel_qos_policies()
    imm_transition(json_data, type).flow_control_policies()
    imm_transition(json_data, type).imc_access_policies()
    imm_transition(json_data, type).ipmi_over_lan_policies()
    imm_transition(json_data, type).iscsi_adapter_policies()
    imm_transition(json_data, type).iscsi_boot_policies()
    imm_transition(json_data, type).iscsi_static_target_policies()
    imm_transition(json_data, type).lan_connectivity_policies()
    imm_transition(json_data, type).link_aggregation_policies()
    imm_transition(json_data, type).link_control_policies()
    imm_transition(json_data, type).network_connectivity_policies()
    imm_transition(json_data, type).ntp_policies()
    imm_transition(json_data, type).port_policies()
    imm_transition(json_data, type).power_policies()
    imm_transition(json_data, type).san_connectivity_policies()
    imm_transition(json_data, type).sd_card_policies()
    imm_transition(json_data, type).serial_over_lan_policies()
    imm_transition(json_data, type).snmp_policies()
    imm_transition(json_data, type).storage_policies()
    imm_transition(json_data, type).switch_control_policies()
    imm_transition(json_data, type).syslog_policies()
    imm_transition(json_data, type).system_qos_policies()
    imm_transition(json_data, type).thermal_policies()
    imm_transition(json_data, type).virtual_kvm_policies()
    imm_transition(json_data, type).virtual_media_policies()
    imm_transition(json_data, type).vsan_policies()
    type = 'policies_vlans'
    imm_transition(json_data, type).multicast_policies()
    imm_transition(json_data, type).vlan_policies()
    type = 'ucs_domain_profiles'
    imm_transition(json_data, type).ucs_domain_profiles()
    type = 'ucs_server_profiles'
    imm_transition(json_data, type).ucs_server_profile_templates()
    imm_transition(json_data, type).ucs_server_profiles()

    # Return Organizations found in jsonData
    return orgs

def process_wizard(easy_jsonData, jsonData):
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Starting the Easy IMM Initial Configuration Wizard!')
    print(f'\n-------------------------------------------------------------------------------------------\n')

    templateVars = {}
    templateVars["multi_select"] = False
    jsonVars = easy_jsonData['wizard']
    templateVars["var_description"] = jsonVars['mainMenu']['description']
    templateVars["jsonVars"] = jsonVars['mainMenu']['enum']
    templateVars["defaultVar"] = jsonVars['mainMenu']['default']
    templateVars["varType"] = 'Main Menu'
    main_menu = variablesFromAPI(**templateVars)
    main_menu = main_menu.replace(' ', '_')
    main_menu = main_menu.lower()

    policy_list = []
    print(f'main_menu is {main_menu}')
    if main_menu == 'deploy_domain_wizard':
        policy_list = [
            # Pools
            'ip_pools',
            'iqn_pools',
            'mac_pools',
            'resource_pools',
            'uuid_pools',
            'wwnn_pools',
            'wwpn_pools',
            # UCS Domain Policies and Profiles
            'multicast_policies',
            'vlan_policies',
            'vsan_policies',
            'flow_control_policies',
            'link_aggregation_policies',
            'link_control_policies',
            'port_policies',
            'network_connectivity_policies',
            'ntp_policies',
            'syslog_policies',
            'snmp_policies',
            'system_qos_policies',
            'switch_control_policies',
            'ucs_domain_profiles',
            # UCS Chassis Policies and Profiles
            'imc_access_policies',
            'power_policies',
            'thermal_policies',
            'ucs_chassis_profiles',
            # UCS Server Policies and Profiles
            'bios_policies',
            'boot_order_policies',
            'virtual_media_policies',
            'certificate_management_policies',
            'ipmi_over_lan_policies',
            'local_user_policies',
            'serial_over_lan_policies',
            'virtual_kvm_policies',
            'sd_card_policies',
            'storage_policies',
            'ethernet_adapter_policies',
            'ethernet_network_control_policies',
            'ethernet_network_group_policies',
            'ethernet_qos_policies',
            'iscsi_adapter_policies',
            'iscsi_boot_policies',
            'iscsi_static_target_policies',
            'lan_connectivity_policies',
            'fibre_channel_adapter_policies',
            'fibre_channel_network_policies',
            'fibre_channel_qos_policies',
            'san_connectivity_policies',
            'ucs_server_template_profiles',
            'ucs_server_profiles',
        ]
    elif main_menu == 'deploy_domain_chassis_wizard':
        policy_list = [
            # UCS Chassis Policies and Profiles
            'power_policies',
            'thermal_policies',
            'ucs_chassis_profiles'
        ]
    elif main_menu == 'deploy_domain_fabric_interconnect_wizard':
        policy_list = [
            # UCS Domain Policies and Profiles
            'multicast_policies',
            'vlan_policies',
            'vsan_policies',
            'flow_control_policies',
            'link_aggregation_policies',
            'link_control_policies',
            'port_policies',
            'ntp_policies',
            'network_connectivity_policies',
            'system_qos_policies',
            'switch_control_policies',
            'ucs_domain_profiles',
        ]
    elif main_menu == 'deploy_domain_servers_wizard':
        policy_list = [
            # Pools
            'ip_pools',
            'iqn_pools',
            'mac_pools',
            'resource_pools',
            'uuid_pools',
            'wwnn_pools',
            'wwpn_pools',
            # UCS Server Policies and Profiles
            'bios_policies',
            'boot_order_policies',
            'virtual_media_policies',
            'certificate_management_policies',
            'ipmi_over_lan_policies',
            'local_user_policies',
            'serial_over_lan_policies',
            'virtual_kvm_policies',
            'sd_card_policies',
            'storage_policies',
            'ethernet_adapter_policies',
            'ethernet_network_control_policies',
            'ethernet_network_group_policies',
            'ethernet_qos_policies',
            'iscsi_adapter_policies',
            'iscsi_boot_policies',
            'iscsi_static_target_policies',
            'lan_connectivity_policies',
            'fibre_channel_adapter_policies',
            'fibre_channel_network_policies',
            'fibre_channel_qos_policies',
            'san_connectivity_policies',
            'ucs_server_template_profiles',
            'ucs_server_profiles',
        ]
    elif main_menu == 'deploy_standalone_servers_wizard':
        policy_list = [
            # Pools
            'ip_pools',
            'resource_pools',
            # UCS Server Policies and Profiles
            'bios_policies',
            'boot_order_policies',
            'persistent_memory_policies',
            'virtual_media_policies',
            'device_connector_policies',
            'ipmi_over_lan_policies',
            'ldap_policies',
            'local_user_policies',
            'network_connectivity_policies',
            'ntp_policies',
            'serial_over_lan_policies',
            'smtp_policies',
            'snmp_policies',
            'ssh_policies',
            'syslog_policies',
            'virtual_kvm_policies',
            'sd_card_policies',
            'storage_policies',
            'adapter_configuration_policies',
            'ethernet_adapter_policies',
            'ethernet_network_control_policies',
            'ethernet_network_policies',
            'ethernet_qos_policies',
            'iscsi_adapter_policies',
            'iscsi_boot_policies',
            'iscsi_static_target_policies',
            'lan_connectivity_policies',
            'fibre_channel_adapter_policies',
            'fibre_channel_network_policies',
            'fibre_channel_qos_policies',
            'san_connectivity_policies',
            'ucs_server_template_profiles',
            'ucs_server_profiles',
        ]
    #  Easy Deploy - VMware M2 Boot Server Profiles
    elif '-_domain_-' in main_menu:
        policy_list = [
            # 'quick_start_pools',
            'quick_start_domain_policies',
            # 'quick_start_domain_policies'
            # 'quick_start_lan_san_policies',
            # 'quick_start_ucs_domain',
            # 'quick_start_ucs_chassis',
        ]
        if 'm2' in main_menu:
            policy_list.append('quick_start_vmware_m2')
        elif 'raid' in main_menu:
            policy_list.append('quick_start_vmware_raid1')

    if main_menu == 'deploy_individual_policies':
        templateVars["var_description"] = jsonVars['Individual']['description']
        templateVars["jsonVars"] = jsonVars['Individual']['enum']
        templateVars["defaultVar"] = jsonVars['Individual']['default']
        templateVars["varType"] = 'Configuration Type'
        type_menu = variablesFromAPI(**templateVars)
        multi_select_descr = '\n    - Single policy: 1 or 5\n'\
            '    - List of Policies: 1,2,3\n'\
            '    - Range of Policies: 1-3,5-6\n'
        templateVars["multi_select"] = True
        if type_menu == 'Policies':
            templateVars["var_description"] = jsonVars['Policies']['description'] + multi_select_descr
            templateVars["jsonVars"] = jsonVars['Policies']['enum']
            templateVars["defaultVar"] = jsonVars['Policies']['default']
            templateVars["varType"] = 'Policies'
            policies_list = variablesFromAPI(**templateVars)
            for line in policies_list:
                line = line.replace(' ', '_')
                line = line.replace('-', '_')
                line = line.lower()
                policy_list.append(line)
        elif type_menu == 'Pools':
            templateVars["var_description"] = jsonVars['Pools']['description'] + multi_select_descr
            templateVars["jsonVars"] = jsonVars['Pools']['enum']
            templateVars["defaultVar"] = jsonVars['Pools']['default']
            templateVars["varType"] = 'Pools'
            policies_list = variablesFromAPI(**templateVars)
            for line in policies_list:
                line = line.replace(' ', '_')
                line = line.replace('-', '_')
                line = line.lower()
                policy_list.append(line)
        elif type_menu == 'Profiles':
            templateVars["var_description"] = jsonVars['Profiles']['description'] + multi_select_descr
            templateVars["jsonVars"] = sorted(jsonVars['Profiles']['enum'])
            templateVars["defaultVar"] = jsonVars['Profiles']['default']
            templateVars["varType"] = 'Profiles'
            policies_list = variablesFromAPI(**templateVars)
            for line in policies_list:
                line = line.replace(' ', '_')
                line = line.replace('-', '_')
                line = line.lower()
                policy_list.append(line)

    valid = False
    while valid == False:
        org = input('What is your Intersight Organization Name?  [default]: ')
        if org == '':
            org = 'default'
        valid = validating.org_rule('Intersight Organization', org, 1, 62)

    if not main_menu == 'skip_policy_deployment':
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  By Default, the Intersight Organization will be used as the Name Prefix for Pools ')
        print(f'  and Policies.  To Assign a different Prefix to the Pools and Policies use the prefix ')
        print(f'  options below.  As Options, a different prefix for UCS domain policies and a prefix')
        print(f'  for Pools and Server Policies can be entered to override the default behavior.')
        print(f'\n-------------------------------------------------------------------------------------------\n')

        if not 'quick_start' in main_menu:
            valid = False
            while valid == False:
                domain_prefix = input('Enter a Name Prefix for Domain Profile Policies.  [press enter to skip]: ')
                if domain_prefix == '':
                    valid = True
                else:
                    valid = validating.name_rule(f"Name Prefix", domain_prefix, 1, 62)
            valid = False
            while valid == False:
                name_prefix = input('Enter a Name Prefix for Pools and Server Policies.  [press enter to skip]: ')
                if name_prefix == '':
                    valid = True
                else:
                    valid = validating.name_rule(f"Name Prefix", name_prefix, 1, 62)
        else:
            domain_prefix = 'default'
            name_prefix = 'default'

    kwargs = {}
    for policy in policy_list:
        #==============================================
        # UCS Pools
        #==============================================
        type = 'pools'
        if policy == 'ip_pools':
            pools(name_prefix, org, type).ip_pools(jsonData, easy_jsonData)
        elif policy == 'iqn_pools':
            pools(name_prefix, org, type).iqn_pools(jsonData, easy_jsonData)
        elif policy == 'mac_pools':
            pools(name_prefix, org, type).mac_pools(jsonData, easy_jsonData)
        elif policy == 'wwnn_pools':
            pools(name_prefix, org, type).wwnn_pools(jsonData, easy_jsonData)
        elif policy == 'wwpn_pools':
            pools(name_prefix, org, type).wwpn_pools(jsonData, easy_jsonData)
        elif policy == 'uuid_pools':
            pools(name_prefix, org, type).uuid_pools(jsonData, easy_jsonData)

        #==============================================
        # UCS Policies
        #==============================================
        type = 'policies_vlans'
        if policy == 'multicast_policies':
            policies_domain(domain_prefix, org, type).multicast_policies(jsonData, easy_jsonData)
        elif policy == 'vlan_policies':
            policies_domain(domain_prefix, org, type).vlan_policies(jsonData, easy_jsonData)
        type = 'policies'
        #================================
        # Policies needed for 1st release
        #================================
        # storage_policies
        #================================
        # Policies needed for 2nd release
        #================================
        # certificate_management_policies
        # sd_card_policies
        if policy == 'adapter_configuration_policies':
            policies_p1(name_prefix, org, type).adapter_configuration_policies(jsonData, easy_jsonData)
        if policy == 'bios_policies':
            policies_p1(name_prefix, org, type).bios_policies(jsonData, easy_jsonData)
        if policy == 'boot_order_policies':
            policies_p1(name_prefix, org, type).boot_order_policies(jsonData, easy_jsonData)
        #========================================================
        # Certificate Management Policies doesn't work
        #========================================================
        # elif policy == 'certificate_management_policies':
        #     policies(name_prefix, org, type).certificate_management_policies()
        elif policy == 'device_connector_policies':
            policies_p1(name_prefix, org, type).device_connector_policies(jsonData, easy_jsonData)
        elif policy == 'ethernet_adapter_policies':
            policies_lan(name_prefix, org, type).ethernet_adapter_policies(jsonData, easy_jsonData)
        elif policy == 'ethernet_network_control_policies':
            policies_lan(name_prefix, org, type).ethernet_network_control_policies(jsonData, easy_jsonData)
        elif policy == 'ethernet_network_group_policies':
            policies_lan(name_prefix, org, type).ethernet_network_group_policies(jsonData, easy_jsonData)
        elif policy == 'ethernet_network_policies':
            policies_lan(name_prefix, org, type).ethernet_network_policies(jsonData, easy_jsonData)
        elif policy == 'ethernet_qos_policies':
            policies_lan(name_prefix, org, type).ethernet_qos_policies(jsonData, easy_jsonData)
        elif policy == 'fibre_channel_adapter_policies':
            policies_san(name_prefix, org, type).fibre_channel_adapter_policies(jsonData, easy_jsonData)
        elif policy == 'fibre_channel_network_policies':
            policies_san(name_prefix, org, type).fibre_channel_network_policies(jsonData, easy_jsonData)
        elif policy == 'fibre_channel_qos_policies':
            policies_san(name_prefix, org, type).fibre_channel_qos_policies(jsonData, easy_jsonData)
        elif policy == 'flow_control_policies':
            policies_domain(domain_prefix, org, type).flow_control_policies(jsonData, easy_jsonData)
        elif policy == 'imc_access_policies':
            policies_p1(name_prefix, org, type).imc_access_policies(jsonData, easy_jsonData)
        elif policy == 'ipmi_over_lan_policies':
            policies_p1(name_prefix, org, type).ipmi_over_lan_policies(jsonData, easy_jsonData)
        elif policy == 'iscsi_adapter_policies':
            policies_lan(name_prefix, org, type).iscsi_adapter_policies(jsonData, easy_jsonData)
        elif policy == 'iscsi_boot_policies':
            policies_lan(name_prefix, org, type).iscsi_boot_policies(jsonData, easy_jsonData)
        elif policy == 'iscsi_static_target_policies':
            policies_lan(name_prefix, org, type).iscsi_static_target_policies(jsonData, easy_jsonData)
        elif policy == 'lan_connectivity_policies':
            policies_lan(name_prefix, org, type).lan_connectivity_policies(jsonData, easy_jsonData)
        elif policy == 'ldap_policies':
            policies_p1(name_prefix, org, type).ldap_policies(jsonData, easy_jsonData)
        elif policy == 'link_aggregation_policies':
            policies_domain(domain_prefix, org, type).link_aggregation_policies(jsonData, easy_jsonData)
        elif policy == 'link_control_policies':
            policies_domain(domain_prefix, org, type).link_control_policies(jsonData, easy_jsonData)
        elif policy == 'local_user_policies':
            policies_p1(name_prefix, org, type).local_user_policies(jsonData, easy_jsonData)
        elif policy == 'network_connectivity_policies':
            policies_p2(name_prefix, org, type).network_connectivity_policies(jsonData, easy_jsonData)
        elif policy == 'ntp_policies':
            policies_p2(name_prefix, org, type).ntp_policies(jsonData, easy_jsonData)
        elif policy == 'persistent_memory_policies':
            policies_p2(name_prefix, org, type).persistent_memory_policies(jsonData, easy_jsonData)
        elif policy == 'port_policies':
            policies_domain(domain_prefix, org, type).port_policies(jsonData, easy_jsonData)
        elif policy == 'power_policies':
            policies_p2(name_prefix, org, type).power_policies(jsonData, easy_jsonData)
        elif policy == 'san_connectivity_policies':
            policies_san(name_prefix, org, type).san_connectivity_policies(jsonData, easy_jsonData)
        # elif policy == 'sd_card_policies':
        #     policies(name_prefix, org, type).sd_card_policies(jsonData, easy_jsonData)
        elif policy == 'serial_over_lan_policies':
            policies_p2(name_prefix, org, type).serial_over_lan_policies(jsonData, easy_jsonData)
        elif policy == 'smtp_policies':
            policies_p2(name_prefix, org, type).smtp_policies(jsonData, easy_jsonData)
        elif policy == 'snmp_policies':
            policies_p2(name_prefix, org, type).snmp_policies(jsonData, easy_jsonData)
        elif policy ==  'ssh_policies':
            policies_p2(name_prefix, org, type).ssh_policies(jsonData, easy_jsonData)
        # elif policy == 'storage_policies':
        #     policies(name_prefix, org, type).storage_policies(jsonData, easy_jsonData)
        elif policy == 'switch_control_policies':
            policies_domain(domain_prefix, org, type).switch_control_policies(jsonData, easy_jsonData)
        elif policy == 'syslog_policies':
            policies_p2(name_prefix, org, type).syslog_policies(jsonData, easy_jsonData)
        elif policy == 'system_qos_policies':
            policies_domain(domain_prefix, org, type).system_qos_policies(jsonData, easy_jsonData)
        elif policy == 'thermal_policies':
            policies_p2(name_prefix, org, type).thermal_policies(jsonData, easy_jsonData)
        elif policy == 'virtual_kvm_policies':
            policies_p2(name_prefix, org, type).virtual_kvm_policies(jsonData, easy_jsonData)
        elif policy == 'virtual_media_policies':
            policies_p2(name_prefix, org, type).virtual_media_policies(jsonData, easy_jsonData)
        elif policy == 'vsan_policies':
            policies_domain(domain_prefix, org, type).vsan_policies(jsonData, easy_jsonData)

        #==============================================
        # UCS Profiles
        #==============================================
        type = 'ucs_chassis_profiles'
        if policy == 'ucs_chassis_profiles':
            profiles(domain_prefix, org, type).ucs_chassis_profiles(jsonData, easy_jsonData)

        type = 'ucs_domain_profiles'
        if policy == 'ucs_domain_profiles':
            profiles(domain_prefix, org, type).ucs_domain_profiles(jsonData, easy_jsonData, name_prefix)

        type = 'ucs_server_profiles'
        if policy == 'ucs_server_profile_templates':
            profiles(name_prefix, org, type).ucs_server_profile_templates(jsonData, easy_jsonData)
        elif policy == 'ucs_server_profiles':
            profiles(name_prefix, org, type).ucs_server_profiles(jsonData, easy_jsonData)
        
        #==============================================
        # Quick Start - Pools
        #==============================================
        type = 'pools'
        if 'quick_start_pools' in policy:
            primary_dns,secondary_dns = quick_start(domain_prefix, org, type).pools(jsonData, easy_jsonData)
            kwargs.update({'primary_dns':primary_dns,'secondary_dns':secondary_dns})
        #==============================================
        # Quick Start - Policies
        #==============================================
        type = 'policies'
        if 'quick_start_domain_policies' in policy or 'quick_start_rack_policies' in policy:
            vsan_policies = []
            vlan_policies = ''
            if 'domain' in policy:
                kwargs.update({'server_type':'FIAttached'})
                vlan_policy,vsan_policies = quick_start(name_prefix, org, type).domain_policies(jsonData, easy_jsonData, **kwargs)
                kwargs.update({'vlan_policy':vlan_policy,'vsan_policies':vsan_policies})
            else:
                kwargs.update({'server_type':'Standalone'})
                kwargs.update({'vsan_policies':vsan_policies})
                quick_start(name_prefix, org, type).standalone_policies(jsonData, easy_jsonData)
            quick_start(name_prefix, org, type).server_policies(jsonData, easy_jsonData, **kwargs)
        elif 'quick_start_lan_san_policies' in policy:
            quick_start(domain_prefix, org, type).lan_san_policies(jsonData, easy_jsonData, **kwargs)
        elif policy == 'quick_start_vmware_m2':
            quick_start(name_prefix, org, type).vmware_m2()
        elif policy == 'quick_start_vmware_raid1':
            quick_start(name_prefix, org, type).vmware_raid1()

    return org


def main():
    jsonFile = 'Templates/variables/intersight_openapi.json'
    jsonOpen = open(jsonFile, 'r')
    jsonData = json.load(jsonOpen)
    jsonOpen.close()

    jsonFile = 'Templates/variables/easy_variables.json'
    jsonOpen = open(jsonFile, 'r')
    easy_jsonData = json.load(jsonOpen)
    jsonOpen.close()

    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        json_open = open(json_file, 'r')
        json_data = json.load(json_open)
        orgs = process_imm_transition(json_data)
    else:
        org = process_wizard(easy_jsonData, jsonData)
        orgs = []
        orgs.append(org)
    for org in orgs:
        merge_easy_imm_repository(easy_jsonData, org)
        create_terraform_workspaces(jsonData, easy_jsonData, org)

if __name__ == '__main__':
    main()
