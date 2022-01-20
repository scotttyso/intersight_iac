#!/usr/bin/env python3
"""Intersight IAC - 
This Wizard to Create Terraform HCL configuration from Question and Answer or the IMM Transition Tool.
It uses argparse to take in the following CLI arguments:
    u or url:                The intersight root URL for the api endpoint. (The default is https://intersight.com)
    d or dir:                Base Directory to use for creation of the HCL Configuration Files
    i or ignore-tls:         Ignores TLS server-side certificate verification
    l or api-key-legacy:     Use legacy API client (v2) key
    j or json_file:          IMM Transition JSON export to convert to HCL
    a or api-key:            API client key id for the HTTP signature scheme
    s or api-key-file:       Name of file containing secret key for the HTTP signature scheme
"""

import argparse
import credentials
import json
import subprocess
import os
import re
import requests
import validating
from easy_functions import policies_parse
from easy_functions import sensitive_var_value
from easy_functions import varBoolLoop
from easy_functions import variablesFromAPI
from easy_functions import varStringLoop
from class_imm_transition import imm_transition
from class_pools import pools
from class_policies_lan import policies_lan
from class_policies_p1 import policies_p1
from class_policies_p2 import policies_p2
from class_policies_p3 import policies_p3
from class_policies_san import policies_san
from class_policies_vxan import policies_vxan
from class_profiles import profiles
from class_quick_start import quick_start
from class_terraform import terraform_cloud
from temp_coding import temp_coding
from io import StringIO
from intersight.api import organization_api
from intersight.model.organization_organization_relationship import OrganizationOrganizationRelationship
from lxml import etree
from pathlib import Path
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

home = Path.home()
Parser = argparse.ArgumentParser(description='Intersight Easy IMM Deployment Module')

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

        # Query the Terraform Versions from the Release URL
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

        # Removing Deprecated Versions from the List
        deprecatedVersions = ["1.1.0", "1.1.1"]
        for depver in deprecatedVersions:
            verCount = 0
            for Version in terraform_versions:
                print(f'depver is {depver} and Version is {Version}')
                if str(depver) == str(Version):
                    terraform_versions.pop(verCount)
                verCount += 1
        
        # Assign the Terraform Version from the Terraform Release URL Above
        templateVars["multi_select"] = False
        templateVars["var_description"] = "Terraform Version for Workspaces:"
        templateVars["jsonVars"] = terraform_versions
        templateVars["varType"] = 'Terraform Version'
        templateVars["defaultVar"] = ''
        templateVars["terraformVersion"] = variablesFromAPI(**templateVars)

        repoFoldercheck = False
        while repoFoldercheck == False:
            if os.environ.get('TF_DEST_DIR') is None:
                tfDir = 'Intersight'
            else:
                tfDir = os.environ.get('TF_DEST_DIR')
            if re.search(r'\/', tfDir):
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  The System Path has been entered as:')
                print(f'  {tfDir}')
                print(f'  For the Terraform Cloud Workspace we need the shortpath to the org files.')
                print(f'  Please confirm the Path Below for the short Path to the Repository Directory.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                question = input(f'Press Enter to Confirm or Make Corrections: [{tfDir}]: ')
                if question == '':
                    repoFoldercheck = True
                else:
                    tfDir = question
                    repoFoldercheck = True
        folder_list = [
            f'{tfDir}/{org}/policies',
            f'{tfDir}/{org}/pools',
            f'{tfDir}/{org}/profiles',
            f'{tfDir}/{org}/ucs_domain_profiles'
        ]
        for folder in folder_list:
            folder_length = len(folder.split('/'))

            templateVars["autoApply"] = True
            templateVars["Description"] = f'Intersight Organization {org} - %s' % (folder.split('/')[folder_length -2])
            if re.search('(pools|policies|ucs_domain_profiles)', folder.split('/')[folder_length -1]):
                templateVars["globalRemoteState"] = True
            else:
                templateVars["globalRemoteState"] = False
            templateVars["workingDirectory"] = folder

            templateVars["Description"] = f'Name of the {folder.split("/")[folder_length -1]} Workspace to Create in Terraform Cloud'
            templateVars["varDefault"] = f'{org}_{folder.split("/")[folder_length -1]}'
            templateVars["varInput"] = f'Terraform Cloud Workspace Name. [{org}_{folder.split("/")[folder_length -1]}]: '
            templateVars["varName"] = f'Workspace Name'
            templateVars["varRegex"] = '^[a-zA-Z0-9\\-\\_]+$'
            templateVars["minLength"] = 1
            templateVars["maxLength"] = 90
            templateVars["workspaceName"] = varStringLoop(**templateVars)
            tfcb_config.append({folder.split('/')[folder_length -1]:templateVars["workspaceName"]})
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
                templateVars["Description"] = var.split('.')[1]
                templateVars["varId"] = var.split('.')[0]
                templateVars["varKey"] = var.split('.')[0]
                templateVars["varValue"] = sensitive_var_value(jsonData, **templateVars)
                templateVars["Sensitive"] = True
                terraform_cloud().tfcVariables(**templateVars)

            if folder.split("/")[folder_length -1] == 'policies':
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
                                            elif k == 'users' or k == 'vmedia_mappings':
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
                    templateVars["varValue"] = sensitive_var_value(jsonData, **templateVars)
                    templateVars["varId"] = var
                    templateVars["varKey"] = var
                    templateVars["Sensitive"] = True
                    terraform_cloud().tfcVariables(**templateVars)

        tfcb_config.append({'org':org})
        for folder in folder_list:
            name_prefix = 'dummy'
            type = 'pools'
            policies_p1(name_prefix, org, type).intersight(easy_jsonData, tfcb_config)
            type = 'policies'
            policies_p1(name_prefix, org, type).intersight(easy_jsonData, tfcb_config)
            type = 'profiles'
            policies_p1(name_prefix, org, type).intersight(easy_jsonData, tfcb_config)
            type = 'ucs_domain_profiles'
            policies_p1(name_prefix, org, type).intersight(easy_jsonData, tfcb_config)
    else:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  Skipping Step to Create Terraform Cloud Workspaces.')
        print(f'  Moving to last step to Confirm the Intersight Organization Exists.')
        print(f'\n-------------------------------------------------------------------------------------------\n')
     
def intersight_org_check(home, org, args):
    check_org = True
    while check_org == True:
        question = input(f'Do You Want to Check Intersight for the Organization {org}?  Enter "Y" or "N" [Y]: ')
        if question == 'Y' or question == '':
            # Login to Intersight API
            api_client = credentials.config_credentials(home, args)

            #=============================================================
            # Create Intersight API instance and Verify if the Org Exists
            #=============================================================
            api_handle = organization_api.OrganizationApi(api_client)
            query_filter = f"Name eq '{org}'"
            kwargs = dict(filter=query_filter)
            org_list = api_handle.get_organization_organization_list(**kwargs)
            if not org_list.results:
                api_body = {
                    "ClassId":"mo.MoRef",
                    "Name":org,
                    "ObjectType":"organization.Organization"
                }
                organization = api_handle.create_organization_organization(api_body)
                org_2nd_list = api_handle.get_organization_organization_list(**kwargs)
                if org_2nd_list.results:
                    org_moid = org_2nd_list.results[0].moid
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Organization {org} has the Moid of {org_moid},')
                    print(f'  which was just Created.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            elif org_list.results:
                org_moid = org_list.results[0].moid
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Organization {org} has the Moid of {org_moid},')
                print(f'  which already exists.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
            check_org = False
        elif question == 'N':
            check_org = False
        else:
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
            print(f'\n-------------------------------------------------------------------------------------------\n')

    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Proceedures Complete!!! Closing Environment and Exiting Script.')
    print(f'\n-------------------------------------------------------------------------------------------\n')

def merge_easy_imm_repository(easy_jsonData, org):
    if os.environ.get('TF_DEST_DIR') is None:
        tfDir = 'Intersight'
    else:
        tfDir = os.environ.get('TF_DEST_DIR')
    if re.search(r'^/.*[\w\-\.\:\/]+\/$', tfDir):
        folder_list = [
            f'{tfDir}{org}/policies',
            f'{tfDir}{org}/pools',
            f'{tfDir}{org}/profiles',
            f'{tfDir}{org}/ucs_domain_profiles'
        ]
    elif re.search(r'^/.*[\w\-\.\:\/]+$', tfDir):
        folder_list = [
            f'{tfDir}/{org}/policies',
            f'{tfDir}/{org}/pools',
            f'{tfDir}/{org}/profiles',
            f'{tfDir}/{org}/ucs_domain_profiles'
        ]
    elif re.search (r'^\w+', tfDir):
        folder_list = [
            f'./{tfDir}/{org}/policies',
            f'./{tfDir}/{org}/pools',
            f'./{tfDir}/{org}/profiles',
            f'./{tfDir}/{org}/ucs_domain_profiles'
        ]
    for folder in folder_list:
        if os.path.isdir(folder):
            folder_length = len(folder.split('/'))
            folder_type = folder.split('/')[folder_length -1]
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
            folder_length = len(folder.split('/'))
            folder_type = folder.split('/')[folder_length -1]
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
    imm_transition(json_data, type).multicast_policies()
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
    imm_transition(json_data, type).vlan_policies()
    imm_transition(json_data, type).vsan_policies()
    type = 'profiles'
    imm_transition(json_data, type).ucs_chassis_profiles()
    type = 'ucs_domain_profiles'
    imm_transition(json_data, type).ucs_domain_profiles()
    type = 'profiles'
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
            'quick_start_pools',
            'quick_start_domain_policies',
            'quick_start_lan_san_policies',
            'quick_start_ucs_chassis',
            'quick_start_ucs_servers',
        ]
        if 'm2' in main_menu:
            policy_list.append('quick_start_vmware_m2')
        elif 'raid' in main_menu:
            policy_list.append('quick_start_vmware_raid1')
        policy_list.append('quick_start_server_profile')

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
        # Intersight Pools
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
        # Intersight Policies
        #==============================================
        type = 'policies'
        if policy == 'adapter_configuration_policies':
            policies_p1(name_prefix, org, type).adapter_configuration_policies(jsonData, easy_jsonData)
        if policy == 'bios_policies':
            policies_p1(name_prefix, org, type).bios_policies(jsonData, easy_jsonData)
        if policy == 'boot_order_policies':
            policies_p1(name_prefix, org, type).boot_order_policies(jsonData, easy_jsonData)
        elif policy == 'certificate_management_policies':
            policies_p1(name_prefix, org, type).certificate_management_policies(jsonData, easy_jsonData)
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
            policies_p1(domain_prefix, org, type).flow_control_policies(jsonData, easy_jsonData)
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
            policies_p1(domain_prefix, org, type).link_aggregation_policies(jsonData, easy_jsonData)
        elif policy == 'link_control_policies':
            policies_p1(domain_prefix, org, type).link_control_policies(jsonData, easy_jsonData)
        elif policy == 'local_user_policies':
            policies_p2(name_prefix, org, type).local_user_policies(jsonData, easy_jsonData)
        elif policy == 'multicast_policies':
            policies_vxan(domain_prefix, org, type).multicast_policies(jsonData, easy_jsonData)
        elif policy == 'network_connectivity_policies':
            policies_p2(name_prefix, org, type).network_connectivity_policies(jsonData, easy_jsonData)
        elif policy == 'ntp_policies':
            policies_p2(name_prefix, org, type).ntp_policies(jsonData, easy_jsonData)
        elif policy == 'persistent_memory_policies':
            policies_p2(name_prefix, org, type).persistent_memory_policies(jsonData, easy_jsonData)
        elif policy == 'port_policies':
            policies_p2(domain_prefix, org, type).port_policies(jsonData, easy_jsonData)
        elif policy == 'power_policies':
            policies_p3(name_prefix, org, type).power_policies(jsonData, easy_jsonData)
        elif policy == 'san_connectivity_policies':
            policies_san(name_prefix, org, type).san_connectivity_policies(jsonData, easy_jsonData)
        # elif policy == 'sd_card_policies':
        #     policies(name_prefix, org, type).sd_card_policies(jsonData, easy_jsonData)
        elif policy == 'serial_over_lan_policies':
            policies_p3(name_prefix, org, type).serial_over_lan_policies(jsonData, easy_jsonData)
        elif policy == 'smtp_policies':
            policies_p3(name_prefix, org, type).smtp_policies(jsonData, easy_jsonData)
        elif policy == 'snmp_policies':
            policies_p3(name_prefix, org, type).snmp_policies(jsonData, easy_jsonData)
        elif policy ==  'ssh_policies':
            policies_p3(name_prefix, org, type).ssh_policies(jsonData, easy_jsonData)
        elif policy == 'storage_policies':
            policies_p3(name_prefix, org, type).storage_policies(jsonData, easy_jsonData)
        elif policy == 'switch_control_policies':
            policies_p3(domain_prefix, org, type).switch_control_policies(jsonData, easy_jsonData)
        elif policy == 'syslog_policies':
            policies_p3(name_prefix, org, type).syslog_policies(jsonData, easy_jsonData)
        elif policy == 'system_qos_policies':
            policies_p3(domain_prefix, org, type).system_qos_policies(jsonData, easy_jsonData)
        elif policy == 'thermal_policies':
            policies_p3(name_prefix, org, type).thermal_policies(jsonData, easy_jsonData)
        elif policy == 'virtual_kvm_policies':
            policies_p3(name_prefix, org, type).virtual_kvm_policies(jsonData, easy_jsonData)
        elif policy == 'virtual_media_policies':
            policies_p3(name_prefix, org, type).virtual_media_policies(jsonData, easy_jsonData)
        elif policy == 'vlan_policies':
            policies_vxan(domain_prefix, org, type).vlan_policies(jsonData, easy_jsonData)
        elif policy == 'vsan_policies':
            policies_vxan(domain_prefix, org, type).vsan_policies(jsonData, easy_jsonData)

        #==============================================
        # Intersight Profiles
        #==============================================
        type = 'profiles'
        if policy == 'ucs_chassis_profiles':
            profiles(domain_prefix, org, type).ucs_chassis_profiles(jsonData, easy_jsonData)
        elif policy == 'ucs_server_profile_templates':
            profiles(name_prefix, org, type).ucs_server_profile_templates(jsonData, easy_jsonData)
        elif policy == 'ucs_server_profiles':
            profiles(name_prefix, org, type).ucs_server_profiles(jsonData, easy_jsonData)

        type = 'ucs_domain_profiles'
        if policy == 'ucs_domain_profiles':
            profiles(domain_prefix, org, type).ucs_domain_profiles(jsonData, easy_jsonData, name_prefix)

        
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
            Config = True
            if 'domain' in policy:
                # kwargs = {'primary_dns': '208.67.220.220', 'secondary_dns': ''}
                kwargs.update({'server_type':'FIAttached'})
                Config,vlan_policy,vsan_a,vsan_b,fc_ports,mtu = quick_start(
                    name_prefix, org, type
                    ).domain_policies(
                    jsonData, easy_jsonData, **kwargs
                )
                if Config == True:
                    kwargs.update({'vlan_policy':vlan_policy["vlan_policy"],'vlans':vlan_policy["vlans"],'native_vlan':vlan_policy["native_vlan"]})
                    kwargs.update({'vsan_a':vsan_a,'vsan_b':vsan_b,'fc_ports':fc_ports})
                    kwargs.update({'mtu':mtu})
            else:
                kwargs.update({'server_type':'Standalone'})
                kwargs.update({'fc_ports':[]})
                type = 'policies'
                Config = quick_start(name_prefix, org, type).standalone_policies(jsonData, easy_jsonData)
            if not Config == False:
                # kwargs = {'primary_dns': '208.67.220.220', 'secondary_dns': '', 'server_type': 'FIAttached', 'vlan_policy': 'asgard-ucs', 'vlans': '1-99', 'native_vlan': '1', 'vsan_a': 100, 'vsan_b': 200, 'fc_ports': [1, 2, 3, 4], 'mtu': 9216}
                quick_start(name_prefix, org, type).server_policies(jsonData, easy_jsonData, **kwargs)
        elif 'quick_start_lan_san_policies' in policy:
            type = 'policies'
            if not Config == False:
                quick_start(domain_prefix, org, type).lan_san_policies(jsonData, easy_jsonData, **kwargs)
        elif policy == 'quick_start_vmware_m2':
            if not Config == False:
                quick_start(name_prefix, org, type).vmware_m2()
                kwargs.update({'boot_order_policy':'VMware_M2_pxe'})
        elif policy == 'quick_start_vmware_raid1':
            if not Config == False:
                quick_start(name_prefix, org, type).vmware_raid1()
                kwargs.update({'boot_order_policy':'VMware_Raid1_pxe'})
        elif 'quick_start_server_profile' in policy:
            if not Config == False:
                type = 'profiles'
                quick_start(domain_prefix, org, type).server_profiles(jsonData, easy_jsonData, **kwargs)

    return org


def main():
    description = None
    if description is not None:
        Parser.description = description
    Parser.add_argument(
        '-a', '--api-key-id',
        default=os.getenv('TF_VAR_apikey'),
        help='The Intersight API client key id for HTTP signature scheme'
    )
    Parser.add_argument(
        '-s', '--api-key-file',
        default='~/Downloads/SecretKey.txt',
        help='Name of file containing The Intersight secret key for the HTTP signature scheme'
    )
    Parser.add_argument('--api-key-v3', action='store_true',
                        help='Use New API client (v3) key'
    )
    Parser.add_argument('-d', '--dir', default='Intersight',
                        help='The Directory to Publish the Terraform Files to.'
    )
    Parser.add_argument('-i', '--ignore-tls', action='store_true',
                        help='Ignore TLS server-side certificate verification'
    )
    Parser.add_argument('-j', '--json_file', default=None,
                        help='The IMM Transition Tool JSON Dump File to Convert to HCL.'
    )
    Parser.add_argument('-u', '--url', default='https://intersight.com',
                        help='The Intersight root URL for the API endpoint. The default is https://intersight.com'
    )
    args = Parser.parse_args()

    jsonFile = 'Templates/variables/intersight_openapi.json'
    jsonOpen = open(jsonFile, 'r')
    jsonData = json.load(jsonOpen)
    jsonOpen.close()

    jsonFile = 'Templates/variables/easy_variables.json'
    jsonOpen = open(jsonFile, 'r')
    easy_jsonData = json.load(jsonOpen)
    jsonOpen.close()

    destdirCheck = False
    while destdirCheck == False:
        splitDir = args.dir.split("/")
        for folder in splitDir:
            if folder == '':
                folderCount = 0
            elif not re.search(r'^[\w\-\.\:\/]+$', folder):
                print(folder)
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  !!ERROR!!')
                print(f'  The Directory structure can only contain the following characters:')
                print(f'  letters(a-z, A-Z), numbers(0-9), hyphen(-), period(.), colon(:), or and underscore(-).')
                print(f'  It can be a short path or a fully qualified path.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                exit()
        os.environ['TF_DEST_DIR'] = '%s' % (args.dir)
        destdirCheck = True



    if not args.json_file == None:
        if os.path.isfile(args.json_file):
            json_file = args.json_file
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
        intersight_org_check(home, org, args)

if __name__ == '__main__':
    main()
