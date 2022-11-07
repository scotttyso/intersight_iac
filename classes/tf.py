from copy import deepcopy
from requests.api import delete
import ezfunctions
import jinja2
import json
import os
import platform
import pkg_resources
import re
import requests
import stdiomask
import time
import validating

# Global options for debugging
print_payload = False
print_response_always = False
print_response_on_fail = True

# Log levels 0 = None, 1 = Class only, 2 = Line
log_level = 2

# Global path to main Template directory
tf_template_path = pkg_resources.resource_filename('tf', '../templates/')

# Exception Classes
class InsufficientArgs(Exception):
    pass

class ErrException(Exception):
    pass

class InvalidArg(Exception):
    pass

class LoginFailed(Exception):
    pass

# Terraform Cloud For Business - Policies
# Class must be instantiated with Variables
class terraform_cloud(object):
    def __init__(self):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(tf_template_path + 'Terraform_Cloud/'))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)

    def terraform_token(self):
        # -------------------------------------------------------------------------------------------------------------------------
        # Check to see if the TF_VAR_terraform_cloud_token is already set in the Environment, and if not prompt the user for Input
        #--------------------------------------------------------------------------------------------------------------------------
        if os.environ.get('TF_VAR_terraform_cloud_token') is None:
            print(f'\n----------------------------------------------------------------------------------------\n')
            print(f'  The Run or State Location was set to Terraform Cloud.  To Store the Data in Terraform')
            print(f'  Cloud we will need a User or Org Token to authenticate to Terraform Cloud.  If you ')
            print(f'  have not already obtained a token see instructions in how to obtain a token Here:\n')
            print(f'   - https://www.terraform.io/docs/cloud/users-teams-organizations/api-tokens.html')
            print(f'\n----------------------------------------------------------------------------------------\n')

            while True:
                user_response = input('press enter to continue: ')
                if user_response == '':
                    break

            # Request the TF_VAR_terraform_cloud_token Value from the User
            while True:
                try:
                    secure_value = stdiomask.getpass(prompt=f'Enter the value for the Terraform Enterprise/Cloud Token: ')
                    break
                except Exception as e:
                    print('Something went wrong. Error received: {}'.format(e))

            # Add the TF_VAR_terraform_cloud_token to the Environment
            os.environ['TF_VAR_terraform_cloud_token'] = '%s' % (secure_value)
            terraform_cloud_token = secure_value
        else:
            terraform_cloud_token = os.environ.get('TF_VAR_terraform_cloud_token')

        return terraform_cloud_token

    def tfc_organization(self, **polVars):
        #-------------------------------
        # Configure the Variables URL
        #-------------------------------
        url = f'https://{polVars["tfc_host"]}/api/v2/organizations'
        tf_token = 'Bearer %s' % (polVars['terraform_cloud_token'])
        tf_header = {'Authorization': tf_token,
                'Content-Type': 'application/vnd.api+json'
        }

        #----------------------------------------------------------------------------------
        # Get the Contents of the Workspace to Search for the Variable
        #----------------------------------------------------------------------------------
        status,json_data = get(url, tf_header, 'Get Terraform Cloud Organizations')

        #--------------------------------------------------------------
        # Parse the JSON Data to see if the Variable Exists or Not.
        #--------------------------------------------------------------

        if status == 200:
            # print(json.dumps(json_data, indent = 4))
            json_data = json_data['data']
            tfcOrgs = []
            for item in json_data:
                for k, v in item.items():
                    if k == 'id':
                        tfcOrgs.append(v)

            # print(tfcOrgs)
            polVars["multi_select"] = False
            polVars["var_description"] = 'Terraform Cloud Organizations:'
            polVars["jsonVars"] = tfcOrgs
            polVars["varType"] = 'Terraform Cloud Organization'
            polVars["defaultVar"] = ''
            tfc_organization = ezfunctions.variablesFromAPI(**polVars)
            return tfc_organization
        else:
            print(status)

    def tfc_vcs_repository(self, **polVars):
        #-------------------------------
        # Configure the Variables URL
        #-------------------------------
        oauth_token = polVars["tfc_oath_token"]
        tfc_host = polVars["tfc_host"]
        url = f'https://{tfc_host}/api/v2/oauth-tokens/{oauth_token}/authorized-repos?oauth_token_id={oauth_token}'
        tf_token = 'Bearer %s' % (polVars['terraform_cloud_token'])
        tf_header = {'Authorization': tf_token,
                'Content-Type': 'application/vnd.api+json'
        }

        #----------------------------------------------------------------------------------
        # Get the Contents of the Workspace to Search for the Variable
        #----------------------------------------------------------------------------------
        status,json_data = get(url, tf_header, 'Get VCS Repos')

        #--------------------------------------------------------------
        # Parse the JSON Data to see if the Variable Exists or Not.
        #--------------------------------------------------------------

        if status == 200:
            # print(json.dumps(json_data, indent = 4))
            json_data = json_data['data']
            repo_list = []
            for item in json_data:
                for k, v in item.items():
                    if k == 'id':
                        repo_list.append(v)

            # print(vcsProvider)
            polVars["multi_select"] = False
            polVars["var_description"] = "Terraform Cloud VCS Base Repository:"
            polVars["jsonVars"] = sorted(repo_list)
            polVars["varType"] = 'VCS Base Repository'
            polVars["defaultVar"] = ''
            vcsBaseRepo = ezfunctions.variablesFromAPI(**polVars)

            return vcsBaseRepo
        else:
            print(status)

    def tfc_vcs_providers(self, **polVars):
        #-------------------------------
        # Configure the Variables URL
        #-------------------------------
        tfc_host = polVars["tfc_host"]
        tfc_organization = polVars["tfc_organization"]
        url = f'https://{tfc_host}/api/v2/organizations/{tfc_organization}/oauth-clients'
        tf_token = 'Bearer %s' % (polVars['terraform_cloud_token'])
        tf_header = {'Authorization': tf_token,
                'Content-Type': 'application/vnd.api+json'
        }

        #----------------------------------------------------------------------------------
        # Get the Contents of the Workspace to Search for the Variable
        #----------------------------------------------------------------------------------
        status,json_data = get(url, tf_header, 'Get VCS Repos')

        #--------------------------------------------------------------
        # Parse the JSON Data to see if the Variable Exists or Not.
        #--------------------------------------------------------------

        if status == 200:
            json_data = json_data['data']
            vcsProvider = []
            vcsAttributes = []
            for item in json_data:
                for k, v in item.items():
                    if k == 'id':
                        vcs_id = v
                    elif k == 'attributes':
                        vcs_name = v['name']
                    elif k == 'relationships':
                        oauth_token = v["oauth-tokens"]["data"][0]["id"]
                vcsProvider.append(vcs_name)
                vcs_repo = {
                    'id':vcs_id,
                    'name':vcs_name,
                    'oauth_token':oauth_token
                }
                vcsAttributes.append(vcs_repo)

            # print(vcsProvider)
            polVars["multi_select"] = False
            polVars["var_description"] = "Terraform Cloud VCS Provider:"
            polVars["jsonVars"] = vcsProvider
            polVars["varType"] = 'VCS Provider'
            polVars["defaultVar"] = ''
            vcsRepoName = ezfunctions.variablesFromAPI(**polVars)

            for i in vcsAttributes:
                if i["name"] == vcsRepoName:
                    tfc_oauth_token = i["oauth_token"]
                    vcsBaseRepo = i["id"]
            # print(f'vcsBaseRepo {vcsBaseRepo} and tfc_oauth_token {tfc_oauth_token}')
            return vcsBaseRepo,tfc_oauth_token
        else:
            print(status)

    def tfcWorkspace(self, **polVars):
        #-------------------------------
        # Configure the Workspace URL
        #-------------------------------
        tfc_host = polVars["tfc_host"]
        tfc_organization = polVars["tfc_organization"]
        workspaceName = polVars['workspaceName']
        url = f'https://{tfc_host}/api/v2/organizations/{tfc_organization}/workspaces/{workspaceName}'
        tf_token = 'Bearer %s' % (polVars['terraform_cloud_token'])
        tf_header = {'Authorization': tf_token,
                'Content-Type': 'application/vnd.api+json'
        }

        #----------------------------------------------------------------------------------
        # Get the Contents of the Organization to Search for the Workspace
        #----------------------------------------------------------------------------------
        status,json_data = get(url, tf_header, 'workspace_check')

        #--------------------------------------------------------------
        # Parse the JSON Data to see if the Workspace Exists or Not.
        #--------------------------------------------------------------
        key_count = 0
        workspace_id = ''
        # print(json.dumps(json_data, indent = 4))
        if status == 200:
            if json_data['data']['attributes']['name'] == polVars['workspaceName']:
                workspace_id = json_data['data']['id']
                key_count =+ 1
        # for key in json_data['data']:
        #     print(key['attributes']['name'])
        #     if key['attributes']['name'] == polVars['Workspace_Name']:
        #         workspace_id = key['id']
        #         key_count =+ 1

        #--------------------------------------------
        # If the Workspace was not found Create it.
        #--------------------------------------------

        opSystem = platform.system()
        if opSystem == 'Windows':
            workingDir = polVars["workingDirectory"]
            polVars["workingDirectory"] = workingDir.replace('\\', '/')

        if re.search(r'^\/', polVars["workingDirectory"]):
            workingDir = polVars["workingDirectory"]
            polVars["workingDirectory"] = workingDir[1 : ]
        elif re.search(r'^\.\/', polVars["workingDirectory"]):
            workingDir = polVars["workingDirectory"]
            polVars["workingDirectory"] = workingDir[2 : ]
        
        if not key_count > 0:
            #-------------------------------
            # Get Workspaces the Workspace URL
            #-------------------------------
            url = f'https://{tfc_host}/api/v2/organizations/{tfc_organization}/workspaces/'
            tf_token = 'Bearer %s' % (polVars['terraform_cloud_token'])
            tf_header = {'Authorization': tf_token,
                    'Content-Type': 'application/vnd.api+json'
            }

            # Define the Template Source
            template_file = 'workspace.jinja2'
            template = self.templateEnv.get_template(template_file)

            # Create the Payload
            payload = template.render(polVars)

            if print_payload:
                print(payload)

            # Post the Contents to Terraform Cloud
            json_data = post(url, payload, tf_header, template_file)

            # Get the Workspace ID from the JSON Dump
            workspace_id = json_data['data']['id']
            key_count =+ 1

        else:
            #-----------------------------------
            # Configure the PATCH Variables URL
            #-----------------------------------
            url = f'https://{tfc_host}/api/v2/workspaces/{workspace_id}/'
            tf_token = 'Bearer %s' % (polVars['terraform_cloud_token'])
            tf_header = {'Authorization': tf_token,
                    'Content-Type': 'application/vnd.api+json'
            }

            # Define the Template Source
            template_file = 'workspace.jinja2'
            template = self.templateEnv.get_template(template_file)

            # Create the Payload
            payload = template.render(polVars)

            if print_payload:
                print(payload)

            # PATCH the Contents to Terraform Cloud
            json_data = patch(url, payload, tf_header, template_file)
            # Get the Workspace ID from the JSON Dump
            workspace_id = json_data['data']['id']
            key_count =+ 1

        if not key_count > 0:
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f'\n   Unable to Determine the Workspace ID for "{polVars["workspaceName"]}".')
            print(f'\n   Exiting...')
            print(f'\n-----------------------------------------------------------------------------\n')
            exit()

        # print(json.dumps(json_data, indent = 4))
        return workspace_id

    def tfcWorkspace_remove(self, **polVars):
        #-------------------------------
        # Configure the Workspace URL
        #-------------------------------
        tfc_host = polVars["tfc_host"]
        tfc_organization = polVars["tfc_organization"]
        workspaceName = polVars['workspaceName']
        url = f'https://{tfc_host}/api/v2/organizations/{tfc_organization}/workspaces/{workspaceName}'
        tf_token = 'Bearer %s' % (polVars['terraform_cloud_token'])
        tf_header = {'Authorization': tf_token,
                'Content-Type': 'application/vnd.api+json'
        }

        #----------------------------------------------------------------------------------
        # Delete the Workspace of the Organization to Search for the Workspace
        #----------------------------------------------------------------------------------
        response = delete(url, headers=tf_header)
        # print(response)

        #--------------------------------------------------------------
        # Parse the JSON Data to see if the Workspace Exists or Not.
        #--------------------------------------------------------------
        del_count = 0
        workspace_id = ''
        # print(json.dumps(json_data, indent = 4))
        if response.status_code == 200:
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f'    Successfully Deleted Workspace "{workspaceName}".')
            print(f'\n-----------------------------------------------------------------------------\n')
            del_count =+ 1
        elif response.status_code == 204:
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f'    Successfully Deleted Workspace "{workspaceName}".')
            print(f'\n-----------------------------------------------------------------------------\n')
            del_count =+ 1

        if not del_count > 0:
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f'    Unable to Determine the Workspace ID for "{workspaceName}".')
            print(f'\n-----------------------------------------------------------------------------\n')
            # exit()

        # print(json.dumps(json_data, indent = 4))

    def tfcVariables(self, **polVars):
        #-------------------------------
        # Configure the Variables URL
        #-------------------------------
        tfc_host = polVars["tfc_host"]
        workspace_id = polVars['workspace_id']
        url = f'https://{tfc_host}/api/v2/workspaces/{workspace_id}/vars'
        tf_token = 'Bearer %s' % (polVars['terraform_cloud_token'])
        tf_header = {'Authorization': tf_token,
                'Content-Type': 'application/vnd.api+json'
        }

        #----------------------------------------------------------------------------------
        # Get the Contents of the Workspace to Search for the Variable
        #----------------------------------------------------------------------------------
        status,json_data = get(url, tf_header, 'variable_check')

        #--------------------------------------------------------------
        # Parse the JSON Data to see if the Variable Exists or Not.
        #--------------------------------------------------------------
        # print(json.dumps(json_data, indent = 4))
        json_text = json.dumps(json_data)
        key_count = 0
        var_id = ''
        if 'id' in json_text:
            for keys in json_data['data']:
                if keys['attributes']['key'] == polVars['Variable']:
                    var_id = keys['id']
                    key_count =+ 1

        #--------------------------------------------
        # If the Variable was not found Create it.
        # If it is Found Update the Value
        #--------------------------------------------
        if not key_count > 0:
            # Define the Template Source
            template_file = 'variables.jinja2'
            template = self.templateEnv.get_template(template_file)

            # Create the Payload
            payload = template.render(polVars)

            if print_payload:
                print(payload)

            # Post the Contents to Terraform Cloud
            json_data = post(url, payload, tf_header, template_file)

            # Get the Workspace ID from the JSON Dump
            var_id = json_data['data']['id']
            key_count =+ 1

        else:
            #-----------------------------------
            # Configure the PATCH Variables URL
            #-----------------------------------
            url = f'https://{tfc_host}/api/v2/workspaces/{workspace_id}/vars/{var_id}'
            tf_token = 'Bearer %s' % (polVars['terraform_cloud_token'])
            tf_header = {'Authorization': tf_token,
                    'Content-Type': 'application/vnd.api+json'
            }

            # Define the Template Source
            template_file = 'variables.jinja2'
            template = self.templateEnv.get_template(template_file)

            # Create the Payload
            polVars.pop('varId')
            payload = template.render(polVars)

            if print_payload:
                print(payload)

            # PATCH the Contents to Terraform Cloud
            json_data = patch(url, payload, tf_header, template_file)
            # Get the Workspace ID from the JSON Dump
            var_id = json_data['data']['id']
            key_count =+ 1

        if not key_count > 0:
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f"\n   Unable to Determine the Variable ID for {polVars['Variable']}.")
            print(f"\n   Exiting...")
            print(f'\n-----------------------------------------------------------------------------\n')
            exit()

        # print(json.dumps(json_data, indent = 4))
        return var_id

# Function to get contents from URL
def get(url, site_header, section=''):
    r = ''
    while r == '':
        try:
            r = requests.get(url, headers=site_header, verify=False)
            status = r.status_code

            # Use this for Troubleshooting
            if print_response_always:
                print(status)
                print(r.text)

            if status == 200 or status == 404:
                json_data = r.json()
                return status,json_data
            else:
                validating.error_request(r.status_code, r.text)

        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            exit()

# Function to PATCH Contents to URL
def patch(url, payload, site_header, section=''):
    r = ''
    while r == '':
        try:
            r = requests.patch(url, data=payload, headers=site_header, verify=False)

            # Use this for Troubleshooting
            if print_response_always:
                print(r.status_code)
                # print(r.text)

            if r.status_code != 200:
                validating.error_request(r.status_code, r.text)

            json_data = r.json()
            return json_data

        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            exit()

# Function to POST Contents to URL
def post(url, payload, site_header, section=''):
    r = ''
    while r == '':
        try:
            r = requests.post(url, data=payload, headers=site_header, verify=False)

            # Use this for Troubleshooting
            if print_response_always:
                print(r.status_code)
                # print(r.text)

            if r.status_code != 201:
                validating.error_request(r.status_code, r.text)

            json_data = r.json()
            return json_data

        except requests.exceptions.ConnectionError as e:
            print("Connection error, pausing before retrying. Error: %s" % (e))
            time.sleep(5)
        except Exception as e:
            print("Method %s Failed. Exception: %s" % (section[:-5], e))
            exit()
