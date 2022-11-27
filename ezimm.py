#!/usr/bin/env python3
"""Intersight IAC - 
Use This Wizard to Create Terraform HCL configuration from Question and Answer or the IMM Transition Tool.
It uses argparse to take in the following CLI arguments:
    a or api-key:            API client key id for the HTTP signature scheme
    d or dir:                Base Directory to use for creation of the HCL Configuration Files
    i or ignore-tls:         Ignores TLS server-side certificate verification
    j or json_file:          IMM Transition JSON export to convert to HCL
    l or api-key-legacy:     Use legacy API client (v2) key
    s or api-key-file:       Name of file containing secret key for the HTTP signature scheme
    e or endoint:            The intersight hostname for the api endpoint. (The default is intersight.com)
"""
from copy import deepcopy
from intersight.api import organization_api
from intersight.api import resource_api
from intersight.model.organization_organization_relationship import OrganizationOrganizationRelationship
from pathlib import Path
import argparse
import credentials
import json
import os
import platform
import re
import requests
import sys
import urllib3
import yaml
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, './classes')
import classes.ezfunctions
import classes.imm
import classes.lansan
import classes.policies
import classes.pools
import classes.profiles
import classes.quick_start
import classes.tf
import classes.validating

def create_terraform_workspaces(orgs, **kwargs):
    args = kwargs['args']
    baseRepo = args.dir
    ezData = kwargs['ezData']
    jsonData = kwargs['jsonData']
    opSystem = kwargs['opSystem']
    org = kwargs['org']
    path_sep = kwargs['path_sep']
    tfcb_config = []
    polVars = {}
    kwargs['jData'] = deepcopy({})
    kwargs['jData']['default']     = True
    kwargs['jData']['description'] = f'Terraform Cloud Workspaces'
    kwargs['jData']['varInput']    = f'Do you want to Proceed with creating Workspaces in Terraform Cloud or Enterprise?'
    kwargs['jData']['varName']     = 'Terraform Cloud Workspaces'
    runTFCB = classes.ezfunctions.varBoolLoop(**kwargs)
    if runTFCB == True:
        polVars = {}
        kwargs['multi_select'] = False
        kwargs['jData'] = deepcopy({})
        kwargs['jData']['default']     = 'Terraform Cloud'
        kwargs['jData']['description'] = 'Select the Terraform Target.'
        kwargs['jData']['enum']        = ['Terraform Cloud', 'Terraform Enterprise']
        kwargs['jData']['varType']     = 'Target'
        terraform_target = classes.ezfunctions.variablesFromAPI(**kwargs)

        if terraform_target[0] == 'Terraform Enterprise':
            kwargs['jData'] = deepcopy({})
            kwargs['jData']['default']     = f'app.terraform.io'
            kwargs['jData']['description'] = f'Hostname of the Terraform Enterprise Instance'
            kwargs['jData']['pattern']     = '^[a-zA-Z0-9\\-\\.\\:]+$'
            kwargs['jData']['minimum']     = 1
            kwargs['jData']['maximum']     = 90
            kwargs['jData']['varInput']    = f'What is the Hostname of the TFE Instance?'
            kwargs['jData']['varName']     = f'Terraform Target Name'
            polVars['tfc_host'] = classes.ezfunctions.varStringLoop(**kwargs)
            if re.search(r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", polVars['tfc_host']):
                classes.validating.ip_address('Terraform Target', polVars['tfc_host'])
            elif ':' in polVars['tfc_host']:
                classes.validating.ip_address('Terraform Target', polVars['tfc_host'])
            else: classes.validating.dns_name('Terraform Target', polVars['tfc_host'])
        else:
            polVars['tfc_host'] = 'app.terraform.io'
        #polVars = {}
        polVars['terraform_cloud_token'] = classes.tf.terraform_cloud().terraform_token()
        #==============================================
        # Obtain Terraform Cloud Organization
        #==============================================
        if os.environ.get('tfc_organization') is None:
            polVars['tfc_organization'] = classes.tf.terraform_cloud().tfc_organization(polVars, **kwargs)
            os.environ['tfc_organization'] = polVars['tfc_organization']
        else: polVars['tfc_organization'] = os.environ.get('tfc_organization')
        tfcb_config.append({'tfc_organization':polVars['tfc_organization']})
        #==============================================
        # Obtain Version Control Provider
        #==============================================
        if os.environ.get('tfc_vcs_provider') is None:
            tfc_vcs_provider,polVars['tfc_oath_token'] = classes.tf.terraform_cloud().tfc_vcs_providers(polVars, **kwargs)
            polVars['tfc_vcs_provider'] = tfc_vcs_provider
            os.environ['tfc_vcs_provider'] = tfc_vcs_provider
            os.environ['tfc_oath_token'] = polVars['tfc_oath_token']
        else:
            polVars['tfc_vcs_provider'] = os.environ.get('tfc_vcs_provider')
            polVars['tfc_oath_token'] = os.environ['tfc_oath_token']
        #==============================================
        # Obtain Version Control Base Repo
        #==============================================
        if os.environ.get('vcsBaseRepo') is None:
            polVars['vcsBaseRepo'] = classes.tf.terraform_cloud().tfc_vcs_repository(polVars, **kwargs)
            os.environ['vcsBaseRepo'] = polVars['vcsBaseRepo']
        else: polVars['vcsBaseRepo'] = os.environ.get('vcsBaseRepo')
        
        polVars['agentPoolId'] = ''
        polVars['allowDestroyPlan'] = False
        polVars['executionMode'] = 'remote'
        polVars['queueAllRuns'] = False
        polVars['speculativeEnabled'] = True
        polVars['triggerPrefixes'] = []
        #==============================================
        # Obtain Terraform Versions from GitHub
        #==============================================
        terraform_versions = []
        # Get the Latest Release Tag for Terraform
        url = f'https://github.com/hashicorp/terraform/tags'
        r = requests.get(url, stream=True)
        for line in r.iter_lines():
            toString = line.decode("utf-8")
            if re.search(r'/releases/tag/v(\d+\.\d+\.\d+)\"', toString):
                terraform_versions.append(re.search('/releases/tag/v(\d+\.\d+\.\d+)', toString).group(1))
        #==============================================
        # Removing Deprecated Versions from the List
        #==============================================
        deprecatedVersions = ['1.1.0", "1.1.1']
        for depver in deprecatedVersions:
            for Version in terraform_versions:
                if str(depver) == str(Version):
                    terraform_versions.remove(depver)
        terraform_versions = list(set(terraform_versions))
        terraform_versions.sort(reverse=True)
        #==============================================
        # Assign the Terraform Version
        #==============================================
        kwargs['jData'] = deepcopy({})
        kwargs['jData']['default']     = terraform_versions[0]
        kwargs['jData']['description'] = "Terraform Version for Workspaces:"
        kwargs['jData']['dontsort']    = True
        kwargs['jData']['enum']        = terraform_versions
        kwargs['jData']['varType']     = 'Terraform Version'
        polVars['terraformVersion'] = classes.ezfunctions.variablesFromAPI(**kwargs)
        #==============================================
        # Begin Creating Workspaces
        #==============================================
        for org in orgs:
            kwargs['org'] = org
            kwargs['jData'] = deepcopy({})
            kwargs['jData']['default']     = f'{org}'
            kwargs['jData']['description'] = f'Name of the {org} Workspace to Create in Terraform Cloud'
            kwargs['jData']['pattern']     = '^[a-zA-Z0-9\\-\\_]+$'
            kwargs['jData']['minimum']     = 1
            kwargs['jData']['maximum']     = 90
            kwargs['jData']['varInput']    = f'Terraform Cloud Workspace Name.'
            kwargs['jData']['varName']     = f'Workspace Name'
            polVars['workspaceName'] = classes.ezfunctions.varStringLoop(**kwargs)
            polVars['workspace_id'] = classes.tf.terraform_cloud().tfcWorkspace(polVars, **kwargs)
            vars = ['apikey.Intersight API Key', 'secretkey.Intersight Secret Key' ]
            for var in vars:
                print(f"* Adding {var.split('.')[1]} to {polVars['workspaceName']}")
                kwargs['Variable'] = var.split('.')[0]
                if 'secret' in var:
                    kwargs['Multi_Line_Input'] = True
                polVars['description'] = var.split('.')[1]
                polVars['varId'] = var.split('.')[0]
                polVars['varKey'] = var.split('.')[0]
                kwargs = classes.ezfunctions.sensitive_var_value(**kwargs)
                polVars['varValue'] = kwargs['var_value']
                polVars['Sensitive'] = True
                if 'secret' in var and opSystem == 'Windows':
                    if os.path.isfile(polVars['varValue']):
                        f = open(polVars['varValue'])
                        polVars['varValue'] = f.read().replace('\n', '\\n')
                classes.tf.terraform_cloud().tfcVariables(polVars, **kwargs)
                kwargs['Multi_Line_Input'] = False
            vars = [
                'ipmi_over_lan.ipmi_key',
                'iscsi_boot.iscsi_boot_password',
                'ldap.binding_parameters_password',
                'local_user.local_user_password',
                'persistent_memory.secure_passphrase',
                'snmp.sensitive_vars',
                'virtual_media.vmedia_password'
            ]
            for var in vars:
                policy = '%s' % (var.split('.')[0])
                kwargs = classes.ezfunctions.policies_parse('policies', policy, policy)
                policies = deepcopy(kwargs['policies'][policy])
                y = var.split('.')[0]
                z = var.split('.')[1]
                if len(policies) > 0:
                    if y == 'persistent_memory':
                        varValue = z
                        polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, **polVars)
                        classes.tf.terraform_cloud().tfcVariables(**polVars)
                    else:
                        for item in policies:
                            if y == 'ipmi_over_lan' and item.get('enabled'):
                                varValue = z
                                polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                classes.tf.terraform_cloud().tfcVariables(**polVars)
                            elif y == 'iscsi_boot' and item.get('authentication'):
                                if re.search('chap', item['authentication']):
                                    varValue = z
                                    polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                    classes.tf.terraform_cloud().tfcVariables(**polVars)
                            elif y == 'ldap' and item.get('binding_parameters'):
                                if item['binding_parameters'].get('bind_method'):
                                    if item['binding_parameters']['bind_method'] == 'ConfiguredCredentials':
                                        varValue = z
                                        polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                        classes.tf.terraform_cloud().tfcVariables(**polVars)
                            elif y == 'local_user':
                                if item.get('enforce_strong_password'):
                                    polVars['enforce_strong_password'] = item['enforce_strong_password']
                                else: polVars['enforce_strong_password'] = True
                                for i in item['users']:
                                    varValue = '%s_%s' % (z, i['password'])
                                    polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                    classes.tf.terraform_cloud().tfcVariables(**polVars)
                            elif y == 'snmp':
                                if item.get('access_community_string'):
                                    varValue = 'access_community_string_%s' % (i['access_community_string'])
                                    polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                    classes.tf.terraform_cloud().tfcVariables(**polVars)
                                if item.get('snmp_users'):
                                    for i in item['snmp_users']:
                                        varValue = 'snmp_auth_password_%s' % (i['auth_password'])
                                        polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                        classes.tf.terraform_cloud().tfcVariables(**polVars)
                                        if i.get('privacy_password'):
                                            varValue = 'snmp_privacy_password_%s' % (i['privacy_password'])
                                            polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                            classes.tf.terraform_cloud().tfcVariables(**polVars)
                                if item.get('snmp_traps'):
                                    for i in item['snmp_traps']:
                                        if i.get('community_string'):
                                            varValue = 'snmp_trap_community_%s' % (i['community_string'])
                                            polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                            classes.tf.terraform_cloud().tfcVariables(**polVars)
                                if item.get('trap_community_string'):
                                    varValue = 'trap_community_string'
                                    polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                    classes.tf.terraform_cloud().tfcVariables(**polVars)
                            elif y == 'virtual_media' and item.get('add_virtual_media'):
                                for i in item['add_virtual_media']:
                                    if i.get('password'):
                                        varValue = '%s_%s' % (z, i['password'])
                                        polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                        classes.tf.terraform_cloud().tfcVariables(**polVars)
    else:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  Skipping Step to Create Terraform Cloud Workspaces.')
        print(f'  Moving to last step to Confirm the Intersight Organization Exists.')
        print(f'\n-------------------------------------------------------------------------------------------\n')
    for org in orgs:
        # Configure the provider.tf and variables.auto.tfvars
        name_prefix = 'dummy'
        type = 'policies'
        classes.policies.policies(name_prefix, org, type).variables(**kwargs)
    # Return kwargs
    return kwargs
     
def intersight_org_check(**kwargs):
    args = kwargs['args']
    home = kwargs['home']
    org = kwargs['org']
    check_org = True
    while check_org == True:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        question = input(f'Do You Want to Check Intersight for the Organization {org}?  Enter "Y" or "N" [Y]: ')
        if question == 'Y' or question == '':
            # Login to Intersight API
            api_client = credentials.config_credentials(home, args)

            #========================================================================
            # Create Intersight API instance and Verify if the Resource Group Exists
            #========================================================================
            api_handle = resource_api.ResourceApi(api_client)
            query_filter = f"Name eq '{org}_rg'"
            kwargs = dict(filter=query_filter)
            rg_list = api_handle.get_resource_group_list(**kwargs)
            resourceGroup = f'{org}_rg'
            if not rg_list.results:
                api_body = { "ClassId":"resource.Group", "Name":resourceGroup, "ObjectType":"resource.Group"}
                resource_group = api_handle.create_resource_group(api_body)
                rg_2nd_list = api_handle.get_resource_group_list(**kwargs)
                if rg_2nd_list.results:
                    rg_moid = rg_2nd_list.results[0].moid
                    print(f'\n-------------------------------------------------------------------------------------------\n')
                    print(f'  Resource Group {org}_rg has the Moid of {rg_moid},')
                    print(f'  which was just Created.')
                    print(f'\n-------------------------------------------------------------------------------------------\n')
            elif rg_list.results:
                rg_moid = rg_list.results[0].moid
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Resource Group {org}_rg has the Moid of {rg_moid},')
                print(f'  which already exists.')
                print(f'\n-------------------------------------------------------------------------------------------\n')

            #=============================================================
            # Create Intersight API instance and Verify if the Org Exists
            #=============================================================
            api_handle = organization_api.OrganizationApi(api_client)
            query_filter = f"Name eq '{org}'"
            kwargs = dict(filter=query_filter)
            org_list = api_handle.get_organization_organization_list(**kwargs)
            if not org_list.results:
                api_body = {
                    "ClassId":"organization.Organization",
                    "Name":org,
                    "ObjectType":"organization.Organization",
                    "ResourceGroups":[{"ClassId":"mo.MoRef", "Moid": rg_moid, "ObjectType":"resource.Group"}]
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

def prompt_main_menu(**kwargs):
    ezData = kwargs['ezData']
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Starting the Easy IMM Initial Configuration Wizard!')
    print(f'\n-------------------------------------------------------------------------------------------\n')

    kwargs['multi_select'] = False
    jsonVars = ezData['ezimm']['allOf'][1]['properties']['wizard']
    kwargs['jData'] = deepcopy(jsonVars['mainMenu'])
    kwargs['jData']['varType'] = 'Main Menu'
    main_menu = classes.ezfunctions.variablesFromAPI(**kwargs)
    main_menu = main_menu.replace(' ', '_').lower()

    list_chassis     = ezData['ezimm']['allOf'][1]['properties']['list_chassis']
    list_domains     = ezData['ezimm']['allOf'][1]['properties']['list_domains']
    list_fi_attached = ezData['ezimm']['allOf'][1]['properties']['list_fi_attached']
    list_pools       = ezData['ezimm']['allOf'][1]['properties']['list_pools']
    list_pools_racks = ezData['ezimm']['allOf'][1]['properties']['rack_pools']
    list_standalone  = ezData['ezimm']['allOf'][1]['properties']['list_standalone']
    policy_list = []
    if main_menu == 'deploy_domain_wizard':
        policy_list.extend(list_pools)
        policy_list.extend(list_domains)
        policy_list.extend(list_chassis)
        policy_list.remove('imc_access_policies')
        policy_list.extend(list_fi_attached)
    elif main_menu == 'deploy_domain_chassis_wizard':
        policy_list.extend(list_chassis)
    elif main_menu == 'deploy_domain_fabric_interconnect_wizard':
        policy_list.extend(list_domains)
    elif main_menu == 'deploy_domain_servers_wizard':
        policy_list.extend(list_pools)
        policy_list.extend(list_fi_attached)
    elif main_menu == 'deploy_standalone_servers_wizard':
        policy_list.extend(list_pools_racks)
        policy_list.extend(list_standalone)
    elif '-_domain_-' in main_menu:
        policy_list = [
            'quick_start_pools', 'quick_start_domain_policies', 'quick_start_lan_san_policies',
            'quick_start_ucs_chassis', 'quick_start_ucs_servers',
        ]
        if 'm2' in main_menu: policy_list.append('quick_start_vmware_m2')
        elif 'raid' in main_menu: policy_list.append('quick_start_vmware_raid1')
        elif 'stateless' in main_menu: policy_list.append('quick_start_vmware_stateless')
        policy_list.append('quick_start_server_profile')

    if main_menu == 'deploy_individual_policies':
        kwargs['jData'] = deepcopy(jsonVars['Individual'])
        kwargs['jData']['varType'] = 'Configuration Type'
        type_menu = classes.ezfunctions.variablesFromAPI(**kwargs)
        multi_select_descr = '\n'\
            '    - Single policy: 1 or 5\n'\
            '    - List of Policies: 1,2,3\n'\
            '    - Range of Policies: 1-3,5-6\n'
        kwargs['multi_select'] = True
        def policy_list_modify(policies_list):
            for line in policies_list:
                policy_list.append((line.replace(' ', '_')).replace('-', '_').lower())
            return policy_list
        if type_menu == 'Policies':
            kwargs['jData'] = deepcopy(jsonVars['Policies'])
            kwargs['jData']['dontsort'] = True
            kwargs['jData']['description'] = kwargs['jData']['description'] + multi_select_descr
            kwargs['jData']['varType'] = 'Policies'
            policies_list = classes.ezfunctions.variablesFromAPI(**kwargs)
            policy_list = policy_list_modify(policies_list)
        elif type_menu == 'Pools':
            kwargs['jData'] = deepcopy(jsonVars['Pools'])
            kwargs['jData']['dontsort'] = True
            kwargs['jData']['description'] = kwargs['jData']['description'] + multi_select_descr
            kwargs['jData']['varType'] = 'Pools'
            policies_list = classes.ezfunctions.variablesFromAPI(**kwargs)
            policy_list = policy_list_modify(policies_list)
        elif type_menu == 'Profiles':
            kwargs['jData'] = deepcopy(jsonVars['Profiles'])
            kwargs['jData']['dontsort'] = True
            kwargs['jData']['description'] = kwargs['jData']['description'] + multi_select_descr
            kwargs['jData']['varType'] = 'Profiles'
            policies_list = classes.ezfunctions.variablesFromAPI(**kwargs)
            policy_list = policy_list_modify(policies_list)
    # Return Main Menu Outputs
    kwargs['main_menu'] = main_menu
    kwargs['policy_list'] = policy_list
    return kwargs

def prompt_org(**kwargs):
    valid = False
    while valid == False:
        org = input('What is your Intersight Organization Name?  [default]: ')
        if org == '': org = 'default'
        valid = classes.validating.org_rule('Intersight Organization', org, 1, 62)
    kwargs['org'] = org
    return kwargs

def prompt_previous_configurations(**kwargs):
    baseRepo = kwargs['args'].dir
    ezData   = kwargs['ezData']['ezimm']['allOf'][1]['properties']
    vclasses = ezData['classes']['enum']
    org      = kwargs['org']
    existing_files = False
    use_configs    = False
    if os.path.isdir(baseRepo):
        dir_list = os.listdir(kwargs['args'].dir)
        if len(dir_list) > 0:
            existing_files = True
    if existing_files == True:
        kwargs['jData'] = {}
        kwargs['jData']['default']     = True
        kwargs['jData']['description'] = 'Load Previous Configurations'
        kwargs['jData']['varInput']    = f'Do You want to Import Configuration found in "{baseRepo}"?'
        kwargs['jData']['varName']     = 'Existing Configuration'
        use_configs = classes.ezfunctions.varBoolLoop(**kwargs)
    if use_configs == True:
        for item in vclasses:
            dest_dir = ezData[f'class.{item}']['directory']
            if os.path.isdir(os.path.join(baseRepo, org, dest_dir)):
                dest_path = f'{os.path.join(baseRepo, org, dest_dir)}'
                dir_list = os.listdir(dest_path)
                for i in dir_list:
                    yfile = open(os.path.join(dest_path, i), 'r')
                    data = yaml.safe_load(yfile)
                    if not kwargs['immDict']['orgs'][org]['intersight'].get(item):
                        kwargs['immDict']['orgs'][org]['intersight'][item] = {}
                    kwargs['immDict']['orgs'][org]['intersight'][item].update(data['intersight'][item])
    # Return kwargs
    return kwargs

def process_wizard(**kwargs):
    ezData      = kwargs['ezData']
    main_menu   = kwargs['main_menu']
    org         = kwargs['org']
    policy_list = kwargs['policy_list']
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
                if domain_prefix == '': valid = True
                else: valid = classes.validating.name_rule(f"Name Prefix", domain_prefix, 1, 62)
            valid = False
            while valid == False:
                name_prefix = input('Enter a Name Prefix for Pools and Server Policies.  [press enter to skip]: ')
                if name_prefix == '': valid = True
                else: valid = classes.validating.name_rule(f"Name Prefix", name_prefix, 1, 62)
        else:
            domain_prefix = org
            name_prefix = org

    for policy in policy_list:
        kwargs['domain_prefix'] = domain_prefix
        #==============================================
        # Intersight Pools
        #==============================================
        cpool = 'classes.pools.pools'
        type = 'pools'
        plist = ezData['ezimm']['allOf'][1]['properties']['list_pools']['enum']
        for i in plist:
            if policy == i: kwargs = eval(f"{cpool}(name_prefix, org, type).{policy}(**kwargs)")
        #==============================================
        # Intersight Policies
        #==============================================
        type = 'policies'
        list_lansan   = ezData['ezimm']['allOf'][1]['properties']['list_lansan']['enum']
        list_policies = ezData['ezimm']['allOf'][1]['properties']['list_policies']['enum']
        plist         = list_lansan + list_policies
        plist.sort()
        for i in plist:
            if policy == i:
                if policy in list_lansan:
                    kwargs = eval(f"classes.lansan.policies(name_prefix, org, type).{i}(**kwargs)")
                elif policy in list_policies:
                    kwargs = eval(f"classes.policies.policies(name_prefix, org, type).{i}(**kwargs)")
        #==============================================
        # Intersight Profiles
        #==============================================
        plist = ezData['ezimm']['allOf'][1]['properties']['list_profiles']['enum']
        type = 'profiles'
        for i in plist:
            if policy == i: kwargs = eval(f"classes.profiles.profiles(name_prefix, org, type).{i}(**kwargs)")
        #==============================================
        # Quick Start - Pools
        #==============================================
        quick = 'classes.quick_start.quick_start'
        type = 'pools'
        if 'quick_start_pools' in policy:
            kwargs = eval(f"{quick}(name_prefix, org, type).pools(**kwargs)")
        #==============================================
        # TESTING TEMP PARAMETERS
        #==============================================
        #script_path = kwargs['script_path']
        #path_sep = kwargs['path_sep']
        #jsonFile = f'{script_path}{path_sep}asgard.json'
        #jsonOpen = open(jsonFile, 'r')
        #kwargs['immDict'] = json.load(jsonOpen)
        #jsonOpen.close()
        #kwargs['primary_dns'] = '208.67.220.220'
        #kwargs['secondary_dns'] = '208.67.220.220'
        #kwargs['fc_ports_in_use'] = [1, 4]
        #kwargs['mtu']           = 9216
        #kwargs['tpm_installed'] = True
        #kwargs['vlan_list']     = '1-99'
        #kwargs['vsan_id_a']     = 100
        #kwargs['vsan_id_b']     = 200
        #==============================================
        # Quick Start - Policies
        #==============================================
        type = 'policies'
        if 'quick_start_domain_policies' in policy or 'quick_start_rack_policies' in policy:
            kwargs['Config'] = True
            if 'quick_start_domain_policies' in policy:
                kwargs.update(deepcopy({'server_type':'FIAttached'}))
                kwargs = eval(f"{quick}(name_prefix, org, type).domain_policies(**kwargs)")
            else: kwargs.update(deepcopy({'fc_ports':[],'server_type':'Standalone'}))
            if not kwargs['Config'] == False:
                kwargs = eval(f"{quick}(name_prefix, org, type).bios_policies(**kwargs)")
                kwargs = eval(f"{quick}(name_prefix, org, type).server_policies(**kwargs)")
            if 'quick_start_rack_policies' in policy:
                type = 'policies'
                kwargs = eval(f"{quick}(name_prefix, org, type).standalone_policies(**kwargs)")
        elif 'quick_start_lan_san_policies' in policy:
            type = 'policies'
            if not kwargs['Config'] == False:
                kwargs = eval(f"{quick}(domain_prefix, org, type).lan_san_policies(**kwargs)")
        elif re.search('quick_start_vmware_(m2|raid1|stateless)', policy):
            if not kwargs['Config'] == False:
                kwargs['boot_type'] = policy.split('_')[3]
                kwargs = eval(f"{quick}(name_prefix, org, type).boot_and_storage(**kwargs)")
        elif 'quick_start_server_profile' in policy:
            if not kwargs['Config'] == False:
                type = 'profiles'
                kwargs = eval(f"{quick}(name_prefix, org, type).server_profiles(**kwargs)")
    return kwargs

#==============================================
# Main Script
#==============================================
def main():
    #==============================================
    # Import Parser and Setup Arguments
    #==============================================
    Parser = argparse.ArgumentParser(description='Intersight Easy IMM Deployment Module')
    Parser.add_argument(
        '-a', '--api-key-id', default=os.getenv('TF_VAR_apikey'),
        help='The Intersight API client key id for HTTP signature scheme'
    )
    Parser.add_argument(
        '-d', '--dir', default='Intersight',
        help='The Directory to Publish the Terraform Files to.'
    )
    Parser.add_argument(
        '-e', '--endpoint', default='intersight.com',
        help='The Intersight hostname for the API endpoint. The default is intersight.com'
    )
    Parser.add_argument(
        '-i', '--ignore-tls', action='store_true',
        help='Ignore TLS server-side certificate verification'
    )
    Parser.add_argument(
        '-j', '--json-file', default=None,
        help='The IMM Transition Tool JSON Dump File to Convert to HCL.'
    )
    Parser.add_argument(
        '-s', '--api-key-file', default='~/Downloads/SecretKey.txt',
        help='Name of file containing The Intersight secret key for the HTTP signature scheme'
    )
    Parser.add_argument(
        '-v', '--api-key-v3', action='store_true',
        help='Flag for API Key Version 3.'
    )
    args = Parser.parse_args()
    args.api_key_id = classes.ezfunctions.api_key(args)
    args.api_key_file = classes.ezfunctions.api_secret(args)
    args.url = f'https://{args.endpoint}'

    #==============================================
    # Setup Main Script Parameters
    #==============================================
    opSystem = platform.system()
    if opSystem == 'Windows': path_sep = '\\'
    else: path_sep = '/'
    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    jsonFile    = f'{script_path}{path_sep}variables{path_sep}intersight-openapi-v3-1.0.11-9235.json'
    jsonOpen    = open(jsonFile, 'r')
    jsonData    = json.load(jsonOpen)
    jsonOpen.close()
    jsonFile = f'{script_path}{path_sep}variables{path_sep}easy_variables.json'
    jsonOpen = open(jsonFile, 'r')
    ezData   = json.load(jsonOpen)
    jsonOpen.close()
    #==============================================
    # Build kwargs
    #==============================================
    kwargs = {}
    kwargs['args']        = args
    kwargs['home']        = Path.home()
    kwargs['opSystem']    = platform.system()
    kwargs['path_sep']    = path_sep
    kwargs['script_path'] = script_path
    kwargs['jsonData']    = jsonData['components']['schemas']
    kwargs['ezData']      = ezData['components']['schemas']
    kwargs['immDict']     = {'orgs':{}}
    kwargs['ez_settings'] = {}
    #==============================================
    # Check Folder Naming for Illegal Characters
    #==============================================
    destdirCheck = False
    while destdirCheck == False:
        splitDir = args.dir.split(path_sep)
        for folder in splitDir:
            if folder == '': folderCount = 0
            elif not re.search(r'^[\w\-\.\:\/\\]+$', folder):
                print(folder)
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  !!ERROR!!')
                print(f'  The Directory structure can only contain the following characters:')
                print(f'  letters(a-z, A-Z), numbers(0-9), hyphen(-), period(.), colon(:), and underscore(-).')
                print(f'  It can be a short path or a fully qualified path.  "{folder}" does not qualify.')
                print(f'  Exiting...')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                exit()
        destdirCheck = True
    #==============================================
    # Run IMM Transition if json Arg Present
    #==============================================
    if not args.json_file == None:
        #==============================================
        # Validate the Existence of the json File
        #==============================================
        if not os.path.isfile(args.json_file):
            print(folder)
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  !!ERROR!!')
            print(f'  Did not find the file {args.json_file}.')
            print(f'  Please Validate that you have specified the correct file and path.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            exit()
        else:
            json_file = args.json_file
            json_open = open(json_file, 'r')
            kwargs['json_data'] = json.load(json_open)
            device_type = kwargs['json_data']['easyucs']['metadata'][0]['device_type']
            #==============================================
            # Validate the device_type in json file
            #==============================================
            if not device_type == 'intersight':
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  !!ERROR!!')
                print(f'  The File "{args.json_file}" device_type is "{device_type}".')
                print(f'  This file is the UCSM Configuration converted from XML to JSON.')
                print(f'  The device_type is found on line 10 of the json config file.')
                print(f'  The Script is looking for the file that has been converted to Intersight Managed Mode.')
                print(f'  The JSON file should be downloaded at the last step of the IMM Transition tool where the')
                print(f'  API Key and Secret would be entered to upload to Intersight.')
                print(f'  Exiting Wizard...')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                exit()
            #==============================================
            # Run through the IMM Transition Wizard
            #==============================================
            kwargs = classes.imm.transition('transition').policy_loop(**kwargs)
            orgs = list(kwargs['immDict']['orgs'].keys())
    else:
        #==============================================
        # Run through the Wizard
        #==============================================
        kwargs = prompt_main_menu(**kwargs)
        kwargs = prompt_org(**kwargs)
        kwargs['immDict']['orgs'].update(deepcopy({kwargs['org']:{'intersight':{}}}))
        kwargs = prompt_previous_configurations(**kwargs)
        kwargs = process_wizard(**kwargs)
        orgs = list(kwargs['immDict']['orgs'].keys())
    #==============================================
    # Merge Repostiroy and Create YAML Files
    #==============================================
    classes.ezfunctions.merge_easy_imm_repository(orgs, **kwargs)
    classes.ezfunctions.create_yaml(orgs, **kwargs)
    #==============================================
    # Create Terraform Config and Workspaces
    #==============================================
    kwargs = classes.ezfunctions.terraform_provider_config(**kwargs)
    kwargs = create_terraform_workspaces(orgs, **kwargs)
    #==============================================
    # Check Existence of Intersight Orgs
    #==============================================
    for org in orgs:
        kwargs['org'] = org
        intersight_org_check(**kwargs)
    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Proceedures Complete!!! Closing Environment and Exiting Script.')
    print(f'\n-------------------------------------------------------------------------------------------\n')

if __name__ == '__main__':
    main()
