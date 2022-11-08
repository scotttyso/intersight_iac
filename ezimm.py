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
    u or url:                The intersight root URL for the api endpoint. (The default is https://intersight.com)
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
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import yaml
import textwrap

sys.path.insert(0, './classes')
import classes.ezfunctions
import classes.imm_transition
import classes.p1
import classes.p2
import classes.p3
import classes.pools
import classes.profiles
import classes.quick_start
import classes.tf
import classes.lan
import classes.san
import classes.validating
import classes.vxan

def create_terraform_workspaces(**kwargs):
    args = kwargs['args']
    baseRepo = args.dir
    ezData = kwargs['ezData']
    jsonData = kwargs['jsonData']
    opSystem = kwargs['opSystem']
    org = kwargs['org']
    path_sep = kwargs['path_sep']
    tfcb_config = []

    polVars = {}
    polVars["Description"] = f'Terraform Cloud Workspaces for Organization {org}'
    polVars["varInput"] = f'Do you want to Proceed with creating Workspaces in Terraform Cloud or Enterprise?'
    polVars["varDefault"] = 'Y'
    polVars["varName"] = 'Terraform Cloud Workspaces'
    runTFCB = classes.ezfunctions.varBoolLoop(**polVars)
    if runTFCB == True:
        kwargs = {}
        kwargs["multi_select"] = True
        kwargs["var_description"] = f'Select the Terraform Target.'
        kwargs["jsonVars"] = ['Terraform Cloud', 'Terraform Enterprise']
        kwargs["defaultVar"] = 'Terraform Cloud'
        kwargs["varType"] = 'Target'
        terraform_target = classes.ezfunctions.variablesFromAPI(**kwargs)

        if terraform_target[0] == 'Terraform Enterprise':
            polVars["Description"] = f'Hostname of the Terraform Enterprise Instance'
            polVars["varDefault"] = f'app.terraform.io'
            polVars["varInput"] = f'What is the Hostname of the TFE Instance? [app.terraform.io]: '
            polVars["varName"] = f'Terraform Target Name'
            polVars["varRegex"] = '^[a-zA-Z0-9\\-\\.\\:]+$'
            polVars["minLength"] = 1
            polVars["maxLength"] = 90
            polVars["tfc_host"] = classes.ezfunctions.varStringLoop(**polVars)
            if re.search(r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", polVars["tfc_host"]):
                classes.validating.ip_address('Terraform Target', polVars["tfc_host"])
            elif ':' in polVars["tfc_host"]:
                classes.validating.ip_address('Terraform Target', polVars["tfc_host"])
            else:
                classes.validating.dns_name('Terraform Target', polVars["tfc_host"])
        else:
            polVars['tfc_host'] = 'app.terraform.io'

        #polVars = {}
        polVars["classes.tf.terraform_cloud_token"] = classes.tf.terraform_cloud().terraform_token()
        
        # Obtain Terraform Cloud Organization
        if os.environ.get('tfc_organization') is None:
            polVars["tfc_organization"] = classes.tf.terraform_cloud().tfc_organization(**polVars)
            os.environ['tfc_organization'] = polVars["tfc_organization"]
        else:
            polVars["tfc_organization"] = os.environ.get('tfc_organization')
        tfcb_config.append({'tfc_organization':polVars["tfc_organization"]})
        
        # Obtain Version Control Provider
        if os.environ.get('tfc_vcs_provider') is None:
            tfc_vcs_provider,polVars["tfc_oath_token"] = classes.tf.terraform_cloud().tfc_vcs_providers(**polVars)
            polVars["tfc_vcs_provider"] = tfc_vcs_provider
            os.environ['tfc_vcs_provider'] = tfc_vcs_provider
            os.environ['tfc_oath_token'] = polVars["tfc_oath_token"]
        else:
            polVars["tfc_vcs_provider"] = os.environ.get('tfc_vcs_provider')
            polVars["tfc_oath_token"] = os.environ['tfc_oath_token']

        # Obtain Version Control Base Repo
        if os.environ.get('vcsBaseRepo') is None:
            polVars["vcsBaseRepo"] = classes.tf.terraform_cloud().tfc_vcs_repository(**polVars)
            os.environ['vcsBaseRepo'] = polVars["vcsBaseRepo"]
        else:
            polVars["vcsBaseRepo"] = os.environ.get('vcsBaseRepo')
        
        polVars["agentPoolId"] = ''
        polVars["allowDestroyPlan"] = False
        polVars["executionMode"] = 'remote'
        polVars["queueAllRuns"] = False
        polVars["speculativeEnabled"] = True
        polVars["triggerPrefixes"] = []

        # Query the Terraform Versions from the Release URL
        terraform_versions = []
        url = f'https://github.com/hashicorp/terraform/releases'
        # Get the Latest Release Tag for Terraform
        url = f'https://github.com/hashicorp/terraform/tags'
        r = requests.get(url, stream=True)
        for line in r.iter_lines():
            # print(line)
            toString = line.decode("utf-8")
            if re.search(r'/releases/tag/v(\d+\.\d+\.\d+)\"', toString):
                terraform_versions.append(re.search('/releases/tag/v(\d+\.\d+\.\d+)', toString).group(1))


        # Removing Deprecated Versions from the List
        deprecatedVersions = ["1.1.0", "1.1.1"]
        for depver in deprecatedVersions:
            for Version in terraform_versions:
                if str(depver) == str(Version):
                    terraform_versions.remove(depver)
        terraform_versions = list(set(terraform_versions))
        terraform_versions.sort(reverse=True)
        # Assign the Terraform Version from the Terraform Release URL Above
        polVars["multi_select"] = False
        polVars["var_description"] = "Terraform Version for Workspaces:"
        polVars["jsonVars"] = terraform_versions
        polVars["varType"] = 'Terraform Version'
        polVars["defaultVar"] = terraform_versions[0]

        # Obtain Terraform Workspace Version
        if not kwargs['ez_settings'].get('terraformVersion') == None:
            polVars["terraformVersion"] = kwargs['ez_settings'].get('terraformVersion')
        else:
            polVars["terraformVersion"] = classes.ezfunctions.variablesFromAPI(**polVars)

        polVars["Description"] = f'Name of the {org} Workspace to Create in Terraform Cloud'
        polVars["varDefault"] = f'{org}'
        polVars["varInput"] = f'Terraform Cloud Workspace Name. [{org}]: '
        polVars["varName"] = f'Workspace Name'
        polVars["varRegex"] = '^[a-zA-Z0-9\\-\\_]+$'
        polVars["minLength"] = 1
        polVars["maxLength"] = 90
        polVars["workspaceName"] = classes.ezfunctions.varStringLoop(**polVars)

        polVars['workspace_id'] = classes.tf.terraform_cloud().tfcWorkspace(**polVars)
        vars = [
            'apikey.Intersight API Key',
            'secretkey.Intersight Secret Key'
        ]
        for var in vars:
            print(f'* Adding {var.split(".")[1]} to {polVars["workspaceName"]}')
            polVars["Variable"] = var.split('.')[0]
            if 'secret' in var:
                polVars["Multi_Line_Input"] = True
            polVars["Description"] = var.split('.')[1]
            polVars["varId"] = var.split('.')[0]
            polVars["varKey"] = var.split('.')[0]
            polVars["varValue"] = classes.ezfunctions.sensitive_var_value(jsonData, **polVars)
            polVars["Sensitive"] = True
            if 'secret' in var and opSystem == 'Windows':
                if os.path.isfile(polVars["varValue"]):
                    f = open(polVars["varValue"])
                    polVars["varValue"] = f.read().replace('\n', '\\n')
            classes.tf.terraform_cloud().tfcVariables(**polVars)

            polVars["Multi_Line_Input"] = False
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
            for var in vars:
                policy_type = 'policies'
                policy = '%s' % (var.split('.')[0])
                policies,json_data = classes.ezfunctions.policies_parse(org, policy_type, policy)
                y = var.split('.')[0]
                z = var.split('.')[1]
                if y == 'persistent_memory_policies':
                    if len(policies) > 0:
                        varValue = z
                        classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, **polVars)
                else:
                    for keys, values in json_data.items():
                        for key, value in values.items():
                            for k, v in value.items():
                                if 'local_user' in keys and k == 'enforce_strong_password':
                                    polVars['enforce_strong_password'] = v
                                if k == z:
                                    if not v == 0:
                                        if y == 'iscsi_boot_policies':
                                            varValue = 'iscsi_boot_password'
                                        else:
                                            varValue = '%s_%s' % (k, v)
                                        polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                        classes.tf.terraform_cloud().tfcVariables(**polVars)
                                elif k == 'binding_parameters':
                                    for ka, va in v.items():
                                        if ka == 'bind_method':
                                            if va == 'ConfiguredCredentials':
                                                varValue = 'binding_parameters_password'
                                                polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                                classes.tf.terraform_cloud().tfcVariables(**polVars)
                                elif k == 'users' or k == 'vmedia_mappings':
                                    for ka, va in v.items():
                                        for kb, vb in va.items():
                                            if kb == 'password':
                                                varValue = '%s_%s' % (z, vb)
                                                polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                                classes.tf.terraform_cloud().tfcVariables(**polVars)
                                elif k == 'snmp_users' and z == 'password':
                                    for ka, va in v.items():
                                        for kb, vb in va.items():
                                            if kb == 'auth_password':
                                                varValue = 'snmp_auth_%s_%s' % (z, vb)
                                                polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                                classes.tf.terraform_cloud().tfcVariables(**polVars)
                                            elif kb == 'privacy_password':
                                                varValue = 'snmp_privacy_%s_%s' % (z, vb)
                                                polVars = classes.ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                                classes.tf.terraform_cloud().tfcVariables(**polVars)

        tfcb_config.append({'backend':'remote','org':org})
        name_prefix = 'dummy'
        type = 'pools'
        classes.p1.policies(name_prefix, org, type).intersight(ezData, tfcb_config)
        type = 'policies'
        classes.p1.policies(name_prefix, org, type).intersight(ezData, tfcb_config)
        type = 'profiles'
        classes.p1.policies(name_prefix, org, type).intersight(ezData, tfcb_config)
        type = 'ucs_domain_profiles'
        classes.p1.policies(name_prefix, org, type).intersight(ezData, tfcb_config)
    else:
        valid = False
        while valid == False:
            polVars = {}
            polVars["Description"] = f'Will You be utilizing Local or Terraform Cloud'
            polVars["varInput"] = f'Will you be utilizing Terraform Cloud?'
            polVars["varDefault"] = 'Y'
            polVars["varName"] = 'Terraform Type'
            runTFCB = classes.ezfunctions.varBoolLoop(**polVars)

            if runTFCB == False:
                tfcb_config.append({'backend':'local','org':org,'tfc_organization':'default'})
                tfcb_config.append({'policies':'','pools':'','ucs_domain_profiles':''})

                name_prefix = 'dummy'
                type = 'pools'
                classes.p1.policies(name_prefix, org, type).intersight(ezData, tfcb_config)
                type = 'policies'
                classes.p1.policies(name_prefix, org, type).intersight(ezData, tfcb_config)
                type = 'profiles'
                classes.p1.policies(name_prefix, org, type).intersight(ezData, tfcb_config)
                type = 'ucs_domain_profiles'
                classes.p1.policies(name_prefix, org, type).intersight(ezData, tfcb_config)
                valid = True
            else:
                valid = True

        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  Skipping Step to Create Terraform Cloud Workspaces.')
        print(f'  Moving to last step to Confirm the Intersight Organization Exists.')
        print(f'\n-------------------------------------------------------------------------------------------\n')
     
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
                api_body = {
                    "ClassId":"resource.Group",
                    "Name":resourceGroup,
                    "ObjectType":"resource.Group"
                }
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
                    "ResourceGroups":[{
                        "ClassId":"mo.MoRef",
                        "Moid": rg_moid,
                        "ObjectType":"resource.Group"
                    }]
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

def imm_transition(**kwargs):
    ezData = kwargs['ezData']
    json_data = kwargs['json_data']
    print(f'\n---------------------------------------------------------------------------------------\n')
    print(f'  Starting the Easy IMM Transition Wizard!')
    print(f'\n---------------------------------------------------------------------------------------\n')

    type = 'pools'
    plist = ezData['ezimm']['allOf'][1]['properties']['list_pools']
    for i in plist:
        kwargs = eval(f"classes.imm_transition(json_data, type).{i}(**kwargs)")
    type = 'policies'
    plist = ezData['ezimm']['allOf'][1]['properties']['list_policies']
    for i in plist:
        kwargs = eval(f"classes.imm_transition(json_data, type).{i}(**kwargs)")
    type = 'profiles'
    plist = ezData['ezimm']['allOf'][1]['properties']['list_profiles']
    for i in plist:
        kwargs = eval(f"classes.imm_transition(json_data, type).{i}(**kwargs)")

    # Return Organizations found in jsonData
    return kwargs

def prompt_main_menu(**kwargs):
    ezData = kwargs['ezData']
    jsonData = kwargs['jsonData']

    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Starting the Easy IMM Initial Configuration Wizard!')
    print(f'\n-------------------------------------------------------------------------------------------\n')

    polVars = {}
    polVars["multi_select"] = False
    jsonVars = ezData['ezimm']['allOf'][1]['properties']['wizard']
    polVars["var_description"] = jsonVars['mainMenu']['description']
    polVars["jsonVars"] = jsonVars['mainMenu']['enum']
    polVars["defaultVar"] = jsonVars['mainMenu']['default']
    polVars["varType"] = 'Main Menu'
    main_menu = classes.ezfunctions.variablesFromAPI(**polVars)
    main_menu = main_menu.replace(' ', '_')
    main_menu = main_menu.lower()

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
        polVars["var_description"] = jsonVars['Individual']['description']
        polVars["jsonVars"] = jsonVars['Individual']['enum']
        polVars["defaultVar"] = jsonVars['Individual']['default']
        polVars["varType"] = 'Configuration Type'
        type_menu = classes.ezfunctions.variablesFromAPI(**polVars)
        multi_select_descr = '\n'\
            '    - Single policy: 1 or 5\n'\
            '    - List of Policies: 1,2,3\n'\
            '    - Range of Policies: 1-3,5-6\n'
        polVars["multi_select"] = True
        def policy_list_modify(policies_list):
            for line in policies_list:
                line = line.replace(' ', '_')
                line = line.replace('-', '_')
                line = line.lower()
                policy_list.append(line)
            return policy_list
        if type_menu == 'Policies':
            polVars["var_description"] = jsonVars['Policies']['description'] + multi_select_descr
            polVars["jsonVars"] = jsonVars['Policies']['enum']
            polVars["defaultVar"] = jsonVars['Policies']['default']
            polVars["varType"] = 'Policies'
            policies_list = classes.ezfunctions.variablesFromAPI(**polVars)
            policy_list = policy_list_modify(policies_list)
        elif type_menu == 'Pools':
            polVars["var_description"] = jsonVars['Pools']['description'] + multi_select_descr
            polVars["jsonVars"] = jsonVars['Pools']['enum']
            polVars["defaultVar"] = jsonVars['Pools']['default']
            polVars["varType"] = 'Pools'
            policies_list = classes.ezfunctions.variablesFromAPI(**polVars)
            policy_list = policy_list_modify(policies_list)
        elif type_menu == 'Profiles':
            polVars["var_description"] = jsonVars['Profiles']['description'] + multi_select_descr
            polVars["jsonVars"] = sorted(jsonVars['Profiles']['enum'])
            polVars["defaultVar"] = jsonVars['Profiles']['default']
            polVars["varType"] = 'Profiles'
            policies_list = classes.ezfunctions.variablesFromAPI(**polVars)
            policy_list = policy_list_modify(policies_list)

    kwargs['main_menu'] = main_menu
    kwargs['policy_list'] = policy_list
    return kwargs

def prompt_org(**kwargs):
    valid = False
    while valid == False:
        org = input('What is your Intersight Organization Name?  [default]: ')
        if org == '':
            org = 'default'
        valid = classes.validating.org_rule('Intersight Organization', org, 1, 62)
    kwargs['org'] = org
    return kwargs

def process_wizard(**kwargs):
    ezData = kwargs['ezData']
    main_menu = kwargs['main_menu']
    org = kwargs['org']
    policy_list = kwargs['policy_list']
    
    if not main_menu == 'skip_policy_deployment':
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  By Default, the Intersight Organization will be used as the Name Prefix for Pools ')
        print(f'  and Policies.  To Assign a different Prefix to the Pools and Policies use the prefix ')
        print(f'  options below.  As Options, a different prefix for UCS domain policies and a prefix')
        print(f'  for Pools and Server Policies can be entered to override the default behavior.')
        print(f'\n-------------------------------------------------------------------------------------------\n')

        if not 'classes.quick_start' in main_menu:
            valid = False
            while valid == False:
                domain_prefix = input('Enter a Name Prefix for Domain Profile Policies.  [press enter to skip]: ')
                if domain_prefix == '':
                    valid = True
                else:
                    valid = classes.validating.name_rule(f"Name Prefix", domain_prefix, 1, 62)
            valid = False
            while valid == False:
                name_prefix = input('Enter a Name Prefix for Pools and Server Policies.  [press enter to skip]: ')
                if name_prefix == '':
                    valid = True
                else:
                    valid = classes.validating.name_rule(f"Name Prefix", name_prefix, 1, 62)
        else:
            domain_prefix = 'default'
            name_prefix = 'default'

    for policy in policy_list:
        #==============================================
        # Intersight Pools
        #==============================================
        cpool = 'classes.pools.pools'
        type = 'pools'
        plist = ezData['ezimm']['allOf'][1]['properties']['list_pools']
        for i in plist:
            if policy == i:
                kwargs = eval(f"{cpool}(name_prefix, org, type).{policy}(**kwargs)")

        #==============================================
        # Intersight Policies
        #==============================================
        type = 'policies'
        plist = ezData['ezimm']['allOf'][1]['properties']['list_policies']
        lan_list = ezData['ezimm']['allOf'][1]['properties']['lan_list']
        p1_list = ezData['ezimm']['allOf'][1]['properties']['p1_list']
        p2_list = ezData['ezimm']['allOf'][1]['properties']['p2_list']
        p3_list = ezData['ezimm']['allOf'][1]['properties']['p3_list']
        san_list = ezData['ezimm']['allOf'][1]['properties']['san_list']
        vxan_list = ezData['ezimm']['allOf'][1]['properties']['vxan_list']
        for i in plist:
            if policy == i:
                if policy in lan_list:
                    kwargs = eval(f"classes.lan.policies(name_prefix, org, type).{i}(**kwargs)")
                elif policy in p1_list:
                    kwargs = eval(f"classes.p1.policies(name_prefix, org, type).{i}(**kwargs)")
                elif policy in p2_list:
                    kwargs = eval(f"classes.p2.policies(name_prefix, org, type).{i}(**kwargs)")
                elif policy in p3_list:
                    kwargs = eval(f"classes.p3.policies(name_prefix, org, type).{i}(**kwargs)")
                elif policy in san_list:
                    kwargs = eval(f"classes.san.policies(name_prefix, org, type).{i}(**kwargs)")
                elif policy in vxan_list:
                    kwargs = eval(f"classes.vxan.policies(name_prefix, org, type).{i}(**kwargs)")

        #==============================================
        # Intersight Profiles
        #==============================================
        kwargs['domain_prefix'] = domain_prefix
        plist = ezData['ezimm']['allOf'][1]['properties']['list_profiles']
        type = 'profiles'
        for i in plist:
            if policy == i:
                kwargs = eval(f"classes.profiles.profiles(name_prefix, org, type).{i}(**kwargs)")
        
        #==============================================
        # Quick Start - Pools
        #==============================================

        quick = 'classes.quick_start.quick_start'
        kwargs['domain_prefix'] = domain_prefix
        type = 'pools'
        #if 'quick_start_pools' in policy:
        #    kwargs = eval(f"{quick}(name_prefix, org, type).pools(**kwargs)")

        #==============================================
        # TESTING TEMP PARAMETERS
        #==============================================
        script_path = kwargs['script_path']
        path_sep = kwargs['path_sep']
        jsonFile = f'{script_path}{path_sep}asgard.json'
        jsonOpen = open(jsonFile, 'r')
        kwargs['immDict'] = {'orgs':{org:{}}}
        kwargs['immDict']['orgs'][org] = json.load(jsonOpen)
        jsonOpen.close()
        kwargs["vlan_list"] = '1-99'

        #==============================================
        # Quick Start - Policies
        #==============================================
        type = 'policies'
        if 'quick_start_domain_policies' in policy or 'quick_start_rack_policies' in policy:
            kwargs['Config'] = True
            if 'domain' in policy:
                kwargs.update(deepcopy({'server_type':'FIAttached'}))
                #kwargs = eval(f"{quick}(name_prefix, org, type).domain_policies(**kwargs)")
            else:
                kwargs.update({'server_type':'Standalone'})
                kwargs.update({'fc_ports':[]})
                type = 'policies'
                kwargs = eval(f"{quick}(name_prefix, org, type).standalone_policies(**kwargs)")
            if not kwargs['Config'] == False and 'domain' in policy:
                kwargs = eval(f"{quick}(name_prefix, org, type).server_policies(**kwargs)")
            if not kwargs['Config'] == False:
                kwargs = eval(f"{quick}(name_prefix, org, type).bios_policies(**kwargs)")
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
                kwargs = eval(f"{quick}(domain_prefix, org, type).server_profiles(**kwargs)")
    return kwargs

def main():
    Parser = argparse.ArgumentParser(description='Intersight Easy IMM Deployment Module')
    Parser.add_argument(
        '-a',
        '--api-key-id',
        default=os.getenv('TF_VAR_apikey'),
        help='The Intersight API client key id for HTTP signature scheme'
    )
    Parser.add_argument(
        '-d',
        '--dir',
        default='Intersight',
        help='The Directory to Publish the Terraform Files to.'
    )
    Parser.add_argument(
        '-i',
        '--ignore-tls',
        action='store_true',
        help='Ignore TLS server-side certificate verification'
    )
    Parser.add_argument(
        '-j',
        '--json-file',
        default=None,
        help='The IMM Transition Tool JSON Dump File to Convert to HCL.'
    )
    Parser.add_argument(
        '-s',
        '--api-key-file',
        default='~/Downloads/SecretKey.txt',
        help='Name of file containing The Intersight secret key for the HTTP signature scheme'
    )
    Parser.add_argument(
        '-u',
        '--url',
        default='https://intersight.com',
        help='The Intersight root URL for the API endpoint. The default is https://intersight.com'
    )
    Parser.add_argument(
        '-v',
        '--api-key-v3',
        action='store_true',
        help='Flag for API Key Version 3.'
    )
    args = Parser.parse_args()
    args.api_key_id = classes.ezfunctions.api_key(args)
    args.api_key_file = classes.ezfunctions.api_secret(args)

    # Setup Main Script Arguments
    opSystem = platform.system()
    kwargs = {}
    kwargs['args'] = args
    kwargs['home'] = Path.home()
    kwargs['opSystem'] = platform.system()
    if opSystem == 'Windows': path_sep = '\\'
    else: path_sep = '/'
    kwargs['path_sep'] = path_sep

    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    kwargs['script_path'] = script_path

    jsonFile = f'{script_path}{path_sep}templates{path_sep}variables{path_sep}intersight-openapi-v3-1.0.11-9235.json'
    jsonOpen = open(jsonFile, 'r')
    jsonData = json.load(jsonOpen)
    jsonOpen.close()
    kwargs['jsonData'] = jsonData['components']['schemas']

    jsonFile = f'{script_path}{path_sep}templates{path_sep}variables{path_sep}easy_variables.json'
    jsonOpen = open(jsonFile, 'r')
    ezData = json.load(jsonOpen)
    jsonOpen.close()
    kwargs['ezData'] = ezData['components']['schemas']
    kwargs['immDict'] = {'orgs':{}}
    kwargs['ez_settings'] = {}

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

    if not args.json_file == None:
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
            json_data = json.load(json_open)
            device_type = json_data['easyucs']['metadata'][0]['device_type']
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
            orgs = classes.imm_transition.imm_transition(json_data, 'policies').return_orgs()
            for org in orgs:
                kwargs = imm_transition(**kwargs)
    else:
        kwargs = prompt_main_menu(**kwargs)
        kwargs = prompt_org(**kwargs)
        kwargs['immDict']['orgs'].update(deepcopy({kwargs['org']:{}}))
        kwargs = process_wizard(**kwargs)
        orgs = list(kwargs['immDict']['orgs'].keys())
    for org in orgs:
        kwargs['org'] = org
        kwargs['immDict']['orgs'].update(deepcopy({org:{}}))
        kwargs = classes.ezfunctions.merge_easy_imm_repository(**kwargs)
        kwargs = create_terraform_workspaces(**kwargs)
        kwargs = intersight_org_check(**kwargs)

    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Proceedures Complete!!! Closing Environment and Exiting Script.')
    print(f'\n-------------------------------------------------------------------------------------------\n')

if __name__ == '__main__':
    main()
