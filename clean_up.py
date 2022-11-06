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

from intersight.api import organization_api
from intersight.api import resource_api
from pathlib import Path
import argparse
import classes.tf
import credentials
import classes.ezfunctions
import os
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

home = Path.home()
Parser = argparse.ArgumentParser(description='Intersight Easy IMM Deployment Module')

def delete_terraform_workspaces(org):
    tfcb_config = []
    valid = False
    while valid == False:
        templateVars = {}
        templateVars["Description"] = 'Terraform Cloud Workspaces'
        templateVars["varInput"] = f'Do you want to Proceed with Deleting Workspaces in Terraform Cloud?'
        templateVars["varDefault"] = 'Y'
        templateVars["varName"] = 'Terraform Cloud Workspaces'
        runTFCB = classes.ezfunctions.varBoolLoop(**templateVars)
        valid = True
    if runTFCB == True:
        templateVars = {}
        templateVars["class_terraform.terraform_cloud_token"] = classes.tf.terraform_cloud().terraform_token()
        templateVars["tfc_organization"] = classes.tf.terraform_cloud().tfc_organization(**templateVars)
        tfcb_config.append({'tfc_organization':templateVars["tfc_organization"]})

        # Obtain Version Control Provider
        if os.environ.get('tfc_vcs_provider') is None:
            tfc_vcs_provider,templateVars["tfc_oath_token"] = classes.tf.terraform_cloud().tfc_vcs_providers(**templateVars)
            templateVars["tfc_vcs_provider"] = tfc_vcs_provider
            os.environ['tfc_vcs_provider'] = tfc_vcs_provider
            os.environ['tfc_oath_token'] = templateVars["tfc_oath_token"]
        else:
            templateVars["tfc_vcs_provider"] = os.environ.get('tfc_vcs_provider')
            templateVars["tfc_oath_token"] = os.environ['tfc_oath_token']

        # Obtain Version Control Base Repo
        if os.environ.get('vcsBaseRepo') is None:
            templateVars["vcsBaseRepo"] = classes.tf.terraform_cloud().tfc_vcs_repository(**templateVars)
            os.environ['vcsBaseRepo'] = templateVars["vcsBaseRepo"]
        else:
            templateVars["vcsBaseRepo"] = os.environ.get('vcsBaseRepo')

        repoFoldercheck = False
        while repoFoldercheck == False:
            if not os.environ.get('tfWorkDir') is None:
                tfDir = os.environ.get('tfWorkDir')
            else:
                if os.environ.get('TF_DEST_DIR') is None:
                    tfDir = 'Intersight'
                    os.environ['tfWorkDir'] = 'Intersight'
                else:
                    tfDir = os.environ.get('TF_DEST_DIR')
            if re.search(r'(^\/|^\.\.)', tfDir):
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  Within Terraform Cloud, the Workspace will be configured with the directory where the ')
                print(f'  configuration files are stored in the repo: {templateVars["vcsBaseRepo"]}.')
                print(f'  For Example if the shortpath was "Intersight", The Repo URL end up like:\n')
                print(f'    - {templateVars["vcsBaseRepo"]}/Intersight/policies')
                print(f'    - {templateVars["vcsBaseRepo"]}/Intersight/pools')
                print(f'    - {templateVars["vcsBaseRepo"]}/Intersight/profiles')
                print(f'    - {templateVars["vcsBaseRepo"]}/Intersight/ucs_domain_profiles\n')
                print(f'  The Destination Directory has been entered as:\n')
                print(f'  {tfDir}\n')
                print(f'  Which looks to be a system path instead of a Repository Directory.')
                print(f'  Please confirm the Path Below is the short Path to the Repository Directory.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                dirLength = len(tfDir.split('/'))
                if re.search(r'\/$', tfDir):
                    question = input(f'Press Enter to Confirm or Make Corrections: [{tfDir.split("/")[dirLength -2]}]: ')
                else:
                    question = input(f'Press Enter to Confirm or Make Corrections: [{tfDir.split("/")[dirLength -1]}]: ')
                if question == '':
                    if re.search(r'\/$', tfDir):
                        tfDir = tfDir.split("/")[dirLength -2]
                    else:
                        tfDir = tfDir.split("/")[dirLength -1]
                    os.environ['tfWorkDir'] = tfDir
                    repoFoldercheck = True
                else:
                    tfDir = question
                    os.environ['tfWorkDir'] = tfDir
                    repoFoldercheck = True
            else:
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

            templateVars["Description"] = 'Name of the Workspace to Delete in Terraform Cloud'
            folder_value = folder.split('/')[folder_length -1]
            templateVars["varDefault"] = f'{org}_{folder_value}'
            templateVars["varInput"] = f'Terraform Cloud Workspace Name. [{org}_{folder_value}]: '
            templateVars["varName"] = f'Workspace Name'
            templateVars["varRegex"] = '^[a-zA-Z0-9\\-\\_]+$'
            templateVars["minLength"] = 1
            templateVars["maxLength"] = 90
            templateVars["workspaceName"] = classes.ezfunctions.varStringLoop(**templateVars)
            tfcb_config.append({folder_value:templateVars["workspaceName"]})
            classes.tf.terraform_cloud().tfcWorkspace_remove(**templateVars)

    else:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'  Skipping Step to Create Terraform Cloud Workspaces.')
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

    delete_terraform_workspaces(org)
    intersight_org_delete(home, org, args)

if __name__ == '__main__':
    main()
