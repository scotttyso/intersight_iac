import jinja2
import json
import lib_ucs
import os
import pkg_resources
import re
import requests
import stdiomask
import sys
import time
import validating

# Global options for debugging
print_payload = False
print_response_always = True
print_response_on_fail = True

# Log levels 0 = None, 1 = Class only, 2 = Line
log_level = 2

# Global path to main Template directory
tf_template_path = pkg_resources.resource_filename('lib_terraform', './')

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
class Terraform_Cloud(object):
    def __init__(self):
        self.templateLoader = jinja2.FileSystemLoader(
            searchpath=(tf_template_path + 'Terraform_Cloud/'))
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)

    def sensitive_var_value(self, jsonData, **templateVars):
        sensitive_var = 'TF_VAR_%s' % (templateVars['Variable'])
        # -------------------------------------------------------------------------------------------------------------------------
        # Check to see if the Variable is already set in the Environment, and if not prompt the user for Input.
        #--------------------------------------------------------------------------------------------------------------------------
        if os.environ.get(sensitive_var) is None:
            print(f"\n----------------------------------------------------------------------------------\n")
            print(f"  The Script did not find {sensitive_var} as an 'environment' variable.")
            print(f"  To not be prompted for the value of {templateVars['Variable']} each time")
            print(f"  add the following to your local environemnt:\n")
            print(f"   - export {sensitive_var}='{templateVars['Variable']}_value'")
            print(f"\n----------------------------------------------------------------------------------\n")

        if os.environ.get(sensitive_var) is None:
            valid = False
            while valid == False:
                varValue = input('press enter to continue: ')
                if varValue == '':
                    valid = True

            valid = False
            while valid == False:
                if templateVars.get('Multi_Line_Input'):
                    print(f'Enter the value for {templateVars["Variable"]}:')
                    lines = []
                    while True:
                        # line = input('')
                        line = stdiomask.getpass(prompt='')
                        if line:
                            lines.append(line)
                        else:
                            break
                    secure_value = '\\n'.join(lines)
                else:
                    secure_value = stdiomask.getpass(prompt=f'Enter the value for {templateVars["Variable"]}: ')

                # Validate Sensitive Passwords
                if re.search('(apikey|secretkey)', sensitive_var):
                    valid = True
                if 'bind' in sensitive_var:
                    jsonVars = jsonData['components']['schemas']['iam.LdapBaseProperties']['allOf'][1]['properties']
                    minLength = 1
                    maxLength = 254
                    rePattern = jsonVars['Password']['pattern']
                    varName = 'SNMP Community'
                    valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
                elif 'community' in sensitive_var:
                    jsonVars = jsonData['components']['schemas']['snmp.Policy']['allOf'][1]['properties']
                    minLength = 1
                    maxLength = jsonVars['TrapCommunity']['maxLength']
                    rePattern = '^[\\S]+$'
                    varName = 'SNMP Community'
                    valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
                elif 'ipmi_key' in sensitive_var:
                    jsonVars = jsonData['components']['schemas']['ipmioverlan.Policy']['allOf'][1]['properties']
                    minLength = 2
                    maxLength = jsonVars['EncryptionKey']['maxLength']
                    rePattern = jsonVars['EncryptionKey']['pattern']
                    varName = 'IPMI Encryption Key'
                    valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
                elif 'iscsi_boot' in sensitive_var:
                    jsonVars = jsonData['components']['schemas']['vnic.IscsiAuthProfile']['allOf'][1]['properties']
                    minLength = 12
                    maxLength = 16
                    rePattern = jsonVars['Password']['pattern']
                    varName = 'iSCSI Boot Password'
                    valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
                elif 'local' in sensitive_var:
                    jsonVars = jsonData['components']['schemas']['iam.EndPointUserRole']['allOf'][1]['properties']
                    minLength = jsonVars['Password']['minLength']
                    maxLength = jsonVars['Password']['maxLength']
                    rePattern = jsonVars['Password']['pattern']
                    varName = 'Local User Password'
                    valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
                elif 'secure_passphrase' in sensitive_var:
                    jsonVars = jsonData['components']['schemas']['memory.PersistentMemoryLocalSecurity']['allOf'][1]['properties']
                    minLength = jsonVars['SecurePassphrase']['minLength']
                    maxLength = jsonVars['SecurePassphrase']['maxLength']
                    rePattern = jsonVars['SecurePassphrase']['pattern']
                    varName = 'Persistent Memory Secure Passphrase'
                    valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
                elif 'snmp' in sensitive_var:
                    jsonVars = jsonData['components']['schemas']['snmp.Policy']['allOf'][1]['properties']
                    minLength = 1
                    maxLength = jsonVars['TrapCommunity']['maxLength']
                    rePattern = '^[\\S]+$'
                    if 'auth' in sensitive_var:
                        varName = 'SNMP Authorization Password'
                    else:
                        varName = 'SNMP Privacy Password'
                    valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)
                elif 'vmedia' in sensitive_var:
                    jsonVars = jsonData['components']['schemas']['vmedia.Mapping']['allOf'][1]['properties']
                    minLength = 1
                    maxLength = jsonVars['Password']['maxLength']
                    rePattern = '^[\\S]+$'
                    varName = 'vMedia Mapping Password'
                    valid = validating.length_and_regex_sensitive(rePattern, varName, secure_value, minLength, maxLength)

            # Add the Variable to the Environment
            os.environ[sensitive_var] = '%s' % (secure_value)
            var_value = secure_value

        else:
            # Add the Variable to the Environment
            if templateVars.get('Multi_Line_Input'):
                var_value = os.environ.get(sensitive_var)
                var_value = var_value.replace('\n', '\\n')
            else:
                var_value = os.environ.get(sensitive_var)

        return var_value

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
                    secure_value = stdiomask.getpass(prompt=f'Enter the value for the Terraform Cloud Token: ')
                    break
                except Exception as e:
                    print('Something went wrong. Error received: {}'.format(e))

            # Add the TF_VAR_terraform_cloud_token to the Environment
            os.environ['TF_VAR_terraform_cloud_token'] = '%s' % (secure_value)
            terraform_cloud_token = secure_value
        else:
            terraform_cloud_token = os.environ.get('TF_VAR_terraform_cloud_token')

        return terraform_cloud_token

    def tfc_organization(self, **templateVars):
        #-------------------------------
        # Configure the Variables URL
        #-------------------------------
        url = 'https://app.terraform.io/api/v2/organizations'
        tf_token = 'Bearer %s' % (templateVars['terraform_cloud_token'])
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
            templateVars["multi_select"] = False
            templateVars["var_description"] = 'Terraform Cloud Organizations:'
            templateVars["jsonVars"] = tfcOrgs
            templateVars["varType"] = 'Terraform Cloud Organization'
            templateVars["defaultVar"] = ''
            tfc_organization = lib_ucs.variablesFromAPI(**templateVars)
            return tfc_organization
        else:
            print(status)

    def tfc_vcs_repository(self, **templateVars):
        #-------------------------------
        # Configure the Variables URL
        #-------------------------------
        oauth_token = templateVars["tfc_oath_token"]
        url = 'https://app.terraform.io/api/v2/oauth-tokens/%s/authorized-repos?oauth_token_id=%s' % (oauth_token, oauth_token)
        tf_token = 'Bearer %s' % (templateVars['terraform_cloud_token'])
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
            templateVars["multi_select"] = False
            templateVars["var_description"] = "Terraform Cloud VCS Base Repository:"
            templateVars["jsonVars"] = sorted(repo_list)
            templateVars["varType"] = 'VCS Base Repository'
            templateVars["defaultVar"] = ''
            vcsBaseRepo = lib_ucs.variablesFromAPI(**templateVars)

            return vcsBaseRepo
        else:
            print(status)

    def tfc_vcs_providers(self, **templateVars):
        #-------------------------------
        # Configure the Variables URL
        #-------------------------------
        url = 'https://app.terraform.io/api/v2/organizations/%s/oauth-clients' % (templateVars["tfc_organization"])
        tf_token = 'Bearer %s' % (templateVars['terraform_cloud_token'])
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
            templateVars["multi_select"] = False
            templateVars["var_description"] = "Terraform Cloud VCS Provider:"
            templateVars["jsonVars"] = vcsProvider
            templateVars["varType"] = 'VCS Provider'
            templateVars["defaultVar"] = ''
            vcsRepoName = lib_ucs.variablesFromAPI(**templateVars)

            for i in vcsAttributes:
                if i["name"] == vcsRepoName:
                    tfc_oauth_token = i["oauth_token"]
                    vcsBaseRepo = i["id"]
            # print(f'vcsBaseRepo {vcsBaseRepo} and tfc_oauth_token {tfc_oauth_token}')
            return vcsBaseRepo,tfc_oauth_token
        else:
            print(status)

    def tfcWorkspace(self, **templateVars):
        #-------------------------------
        # Configure the Workspace URL
        #-------------------------------
        url = 'https://app.terraform.io/api/v2/organizations/%s/workspaces/%s' %  (templateVars['tfc_organization'], templateVars['workspaceName'])
        tf_token = 'Bearer %s' % (templateVars['terraform_cloud_token'])
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
            if json_data['data']['attributes']['name'] == templateVars['workspaceName']:
                workspace_id = json_data['data']['id']
                key_count =+ 1
        # for key in json_data['data']:
        #     print(key['attributes']['name'])
        #     if key['attributes']['name'] == templateVars['Workspace_Name']:
        #         workspace_id = key['id']
        #         key_count =+ 1

        #--------------------------------------------
        # If the Workspace was not found Create it.
        #--------------------------------------------
        if not key_count > 0:
            #-------------------------------
            # Get Workspaces the Workspace URL
            #-------------------------------
            url = 'https://app.terraform.io/api/v2/organizations/%s/workspaces/' %  (templateVars['tfc_organization'])
            tf_token = 'Bearer %s' % (templateVars['terraform_cloud_token'])
            tf_header = {'Authorization': tf_token,
                    'Content-Type': 'application/vnd.api+json'
            }

            # Define the Template Source
            template_file = 'workspace.jinja2'
            template = self.templateEnv.get_template(template_file)

            # Create the Payload
            payload = template.render(templateVars)

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
            url = 'https://app.terraform.io/api/v2/workspaces/%s/' %  (workspace_id)
            tf_token = 'Bearer %s' % (templateVars['terraform_cloud_token'])
            tf_header = {'Authorization': tf_token,
                    'Content-Type': 'application/vnd.api+json'
            }

            # Define the Template Source
            template_file = 'workspace.jinja2'
            template = self.templateEnv.get_template(template_file)

            # Create the Payload
            payload = template.render(templateVars)

            if print_payload:
                print(payload)

            # PATCH the Contents to Terraform Cloud
            json_data = patch(url, payload, tf_header, template_file)
            # Get the Workspace ID from the JSON Dump
            workspace_id = json_data['data']['id']
            key_count =+ 1

        if not key_count > 0:
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f"\n   Unable to Determine the Workspace ID for {templateVars['Workspace_Name']}.")
            print(f"\n   Exiting...")
            print(f'\n-----------------------------------------------------------------------------\n')
            exit()

        # print(json.dumps(json_data, indent = 4))
        return workspace_id

    def tfcVariables(self, **templateVars):
        #-------------------------------
        # Configure the Variables URL
        #-------------------------------
        url = 'https://app.terraform.io/api/v2/workspaces/%s/vars' %  (templateVars['workspace_id'])
        tf_token = 'Bearer %s' % (templateVars['terraform_cloud_token'])
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
                if keys['attributes']['key'] == templateVars['Variable']:
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
            payload = template.render(templateVars)

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
            url = 'https://app.terraform.io/api/v2/workspaces/%s/vars/%s' %  (templateVars['workspace_id'], var_id)
            tf_token = 'Bearer %s' % (templateVars['terraform_cloud_token'])
            tf_header = {'Authorization': tf_token,
                    'Content-Type': 'application/vnd.api+json'
            }

            # Define the Template Source
            template_file = 'variables.jinja2'
            template = self.templateEnv.get_template(template_file)

            # Create the Payload
            templateVars.pop('varId')
            payload = template.render(templateVars)

            if print_payload:
                print(payload)

            # PATCH the Contents to Terraform Cloud
            json_data = patch(url, payload, tf_header, template_file)
            # Get the Workspace ID from the JSON Dump
            var_id = json_data['data']['id']
            key_count =+ 1

        if not key_count > 0:
            print(f'\n-----------------------------------------------------------------------------\n')
            print(f"\n   Unable to Determine the Variable ID for {templateVars['Variable']}.")
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
            r = requests.get(url, headers=site_header)
            status = r.status_code

            # Use this for Troubleshooting
            if print_response_always:
                print(status)
                # print(r.text)

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
            r = requests.patch(url, data=payload, headers=site_header)

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
            r = requests.post(url, data=payload, headers=site_header)

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
