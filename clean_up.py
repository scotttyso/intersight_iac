#!/usr/bin/env python3
"""Intersight IAC - Cleanup Wizard
This Wizard is used to Cleanup Intersight Orgs and Terraform Cloud Workspaces after Demonstrations.
It uses argparse to take in the following CLI arguments:
    u or url:                The intersight root URL for the api endpoint. (The default is https://intersight.com)
    d or delete:             Base Directory to use for creation of the HCL Configuration Files
    l or api-key-legacy:     Use legacy API client (v2) key
    k or api-key:            API client key id for the HTTP signature scheme
    f or api-key-file:       Name of file containing secret key for the HTTP signature scheme
"""

from copy import deepcopy
from intersight.api import organization_api
from intersight.api import resource_api
from pathlib import Path
import argparse
import credentials
import json
import os
import platform
import re
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, './classes')
import classes.ezfunctions
import classes.tf

home = Path.home()
Parser = argparse.ArgumentParser(description='Intersight Easy IMM Deployment Module')

def delete_terraform_workspaces(org, **kwargs):
    tfcb_config = []
    valid = False
    while valid == False:
        kwargs['jData'] = deepcopy({})
        kwargs['jData']["default"]     = True
        kwargs['jData']["description"] = 'Terraform Cloud Workspaces'
        kwargs['jData']["varInput"]    = f'Do you want to Proceed with Deleting Workspaces in Terraform Cloud?'
        kwargs['jData']["varName"]     = 'Terraform Cloud Workspaces'
        runTFCB = classes.ezfunctions.varBoolLoop(**kwargs)
        valid = True
    if runTFCB == True:
        polVars = {}
        #==============================================
        # Obtain Terraform Target
        #==============================================
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
        #==============================================
        # Obtain Terraform Token
        #==============================================
        polVars["terraform_cloud_token"] = classes.tf.terraform_cloud().terraform_token()
        #==============================================
        # Obtain Terraform Organization
        #==============================================
        polVars["tfc_organization"] = classes.tf.terraform_cloud().tfc_organization(polVars, **kwargs)
        #==============================================
        # Delete Terraform Workspaces
        #==============================================
        workspaceLoop = False
        deLoop = False
        while workspaceLoop == False:
            #==============================================
            # Obtain Terraform Workspace Name
            #==============================================
            kwargs['jData'] = deepcopy({})
            kwargs['jData']["description"] = 'Name of the Workspace to Delete in Terraform Cloud'
            kwargs['jData']["default"]     = org
            kwargs['jData']["pattern"]     = '^[a-zA-Z0-9\\-\\_]+$'
            kwargs['jData']["minimum"]     = 1
            kwargs['jData']["maximum"]     = 90
            kwargs['jData']["varInput"]    = f'Terraform Cloud Workspace Name.'
            kwargs['jData']["varName"]     = f'Workspace Name'
            polVars["workspaceName"]       = classes.ezfunctions.varStringLoop(**kwargs)
            classes.tf.terraform_cloud().tfcWorkspace_remove(**polVars)
            policy_type = 'Delete another Workspace'
            deLoop, workspaceLoop = classes.ezfunctions.exit_default_del_tfc(policy_type, 'Y')

    else:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  Skipping Step to Delete Terraform Cloud Workspaces.')
        print(f'  Moving to last step to Confirm the Intersight Organization Exists.')
        print(f'\n-------------------------------------------------------------------------------------------\n')
     
def intersight_org_delete(home, org, args):
    # Login to Intersight API
    api_client = credentials.config_credentials(home, args)

    #=============================================================
    # Create Intersight API instance and Verify if the Org Exists
    #=============================================================
    api_handle = organization_api.OrganizationApi(api_client)
    query_filter = f"Name eq '{org}'"
    kwargs = dict(filter=query_filter)
    org_list = api_handle.get_organization_organization_list(**kwargs)
    org_moid = None
    if org_list.results:
        org_moid = org_list.results[0].moid
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  Organization {org} has the Moid of {org_moid}.')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        org_remove = True
        while org_remove == True:
            Delete = input(f'Do You Want to proceed with deleting {org}?  Enter "Y" or "N": ')
            if Delete == 'Y':
                if not org_moid == None:
                    api_handle.delete_organization_organization(org_moid)
                    
                    api_handle = resource_api.ResourceApi(api_client)
                    query_filter = f"Name eq '{org}_rg'"
                    kwargs = dict(filter=query_filter)
                    rg_list = api_handle.get_resource_group_list(**kwargs)
                    rg_moid = None
                    if rg_list.results:
                        rg_moid = rg_list.results[0].moid
                        api_handle.delete_resource_group(rg_moid)

                    org_remove = False
            elif Delete == 'N':
                org_remove = False
            else:
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Error!! Invalid Value.  Please enter "Y" or "N".')
                print(f'\n-------------------------------------------------------------------------------------------\n')

    print(f'\n-------------------------------------------------------------------------------------------\n')
    print(f'  Proceedures Complete!!! Closing Environment and Exiting Script.')
    print(f'\n-------------------------------------------------------------------------------------------\n')

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
    Parser.add_argument('-o', '--organization', default=None,
                        help='The Organization to Clean-up.'
    )
    Parser.add_argument('-u', '--url', default='https://intersight.com',
                        help='The Intersight root URL for the API endpoint. The default is https://intersight.com'
    )
    args = Parser.parse_args()
    org = args.organization

    os.environ['TF_DEST_DIR'] = '%s' % (args.dir)

    #==============================================
    # Setup Main Script Parameters
    #==============================================
    opSystem = platform.system()
    if opSystem == 'Windows': path_sep = '\\'
    else: path_sep = '/'
    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    jsonFile    = f'{script_path}{path_sep}variables{path_sep}intersight-openapi-v3-1.0.11-11360.json'
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
    delete_terraform_workspaces(org, **kwargs)
    intersight_org_delete(home, org, args)

if __name__ == '__main__':
    main()
