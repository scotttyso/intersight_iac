#!/usr/bin/env python3
"""Intersight IAC - 
Use This Wizard to Create Terraform HCL configuration from Question and Answer or the IMM Transition Tool.
It uses argparse to take in the following CLI arguments:
    a or intersight-api-key-id: The Intersight API key id for HTTP signature scheme.
    d or dir:                   Base Directory to use for creation of the YAML Configuration Files.
    dl or debug-level:          The Debug Level to Run for Script Output
    e or intersight-fqdn:       The Intersight hostname for the API endpoint. The default is intersight.com.
    i or ignore-tls:            Ignore TLS server-side certificate verification.  Default is False.
    j or json_file:             IMM Transition JSON export to convert to HCL.
    l or load-config            Flag to Load Previously Saved YAML Configuration Files.
    k or intersight-secret-key: Name of the file containing The Intersight secret key for the HTTP signature scheme.
    t or deployment-method:     Deployment Method.  Values are: Intersight or Terraform
    v or api-key-v3:            Flag for API Key Version 3.
"""
#=============================================================================
# Source Modules
#=============================================================================
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
import os, sys
script_path= os.path.dirname(os.path.realpath(sys.argv[0]))
sys.path.insert(0, f'{script_path}{os.sep}classes')
try:
    from classes import build, ezfunctions, imm, isight, lansan, pcolor, policies, pools, profiles, questions, quick_start, tf, validating
    from collections import OrderedDict
    from copy import deepcopy
    from dotmap import DotMap
    from json_ref_dict import materialize, RefDict
    from pathlib import Path
    import argparse, json, os, logging, platform, re, requests, urllib3, yaml
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError as e:
    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
    prRed(f" Module {e.name} is required to run this script")
    prRed(f" Install the module using the following: `pip install {e.name}`")

#=================================================================
# Function: Parse Arguments
#=================================================================
def cli_arguments():
    Parser = argparse.ArgumentParser(description='Intersight Easy IMM Deployment Module')
    Parser.add_argument(
        '-a', '--intersight-api-key-id', default=os.getenv('intersight_api_key_id'),
        help='The Intersight API key id for HTTP signature scheme.')
    Parser.add_argument(
        '-d', '--dir', default = 'Intersight',
        help = 'The Directory to use for the Creation of the YAML Configuration Files.')
    Parser.add_argument(
        '-dl', '--debug-level', default =0,
        help ='The Amount of Debug output to Show: '\
            '1. Shows the api request response status code '\
            '5. Show URL String + Lower Options '\
            '6. Adds Results + Lower Options '\
            '7. Adds json payload + Lower Options '\
            'Note: payload shows as pretty and straight to check for stray object types like Dotmap and numpy')
    Parser.add_argument(
        '-f', '--intersight-fqdn', default='intersight.com',
        help = 'The Directory to use for the Creation of the YAML Configuration Files.')
    Parser.add_argument(
        '-i', '--ignore-tls', action='store_false',
        help='Ignore TLS server-side certificate verification.  Default is False.')
    Parser.add_argument(
        '-j', '--json-file', default=None,
        help='The IMM Transition Tool JSON Dump File to Convert to HCL.')
    Parser.add_argument(
        '-k', '--intersight-secret-key', default='~/Downloads/SecretKey.txt',
        help='Name of the file containing The Intersight secret key or contents of the secret key in environment.')
    Parser.add_argument(
        '-l', '--load-config', action='store_true',
        help='Skip Wizard and Just Load Configuration Files.')
    Parser.add_argument(
        '-t', '--deployment-method', default=None,
        help = 'Deployment Method values are: \
            1.  Python \
            2.  Terraform')
    Parser.add_argument( '-v', '--api-key-v3', action='store_true', help='Flag for API Key Version 3.' )
    kwargs = DotMap()
    kwargs.args = Parser.parse_args()
    return kwargs

#=================================================================
# Function: Build Pool/Policy List(s)
#=================================================================
def build_policy_list(kwargs):
    kwargs.policy_list = []; kwargs.pool_list = []
    for k, v in kwargs.ezdata.items():
        if v.intersight_type == 'pool' and not '.' in k: kwargs.pool_list.append(k)
        elif v.intersight_type == 'policy':
            if kwargs.target_platform == 'FIAttached':
                if not '.' in k and ('chassis' in v.target_platforms or 'FIAttached' in v.target_platforms):  kwargs.policy_list.append(k)
            else:
                if 'Standalone' in v.target_platforms and not '.' in k: kwargs.policy_list.append(k)
    return kwargs

#=================================================================
# Function: Create Terraform Workspaces
#=================================================================
def create_terraform_workspaces(orgs, kwargs):
    jsonData = kwargs.jsonData
    opSystem = kwargs.opSystem
    org = kwargs.org
    tfcb_config = []
    polVars = DotMap()
    kwargs.jData = DotMap()
    kwargs.jData.default     = True
    kwargs.jData.description = f'Terraform Cloud Workspaces'
    kwargs.jData.varInput    = f'Do you want to Proceed with creating Workspaces in Terraform Cloud or Enterprise?'
    kwargs.jData.varName     = 'Terraform Cloud Workspaces'
    runTFCB = ezfunctions.varBoolLoop(kwargs)
    if runTFCB == True:
        polVars = {}
        kwargs.multi_select = False
        kwargs.jData = DotMap()
        kwargs.jData.default     = 'Terraform Cloud'
        kwargs.jData.description = 'Select the Terraform Target.'
        kwargs.jData.enum        = ['Terraform Cloud', 'Terraform Enterprise']
        kwargs.jData.varType     = 'Target'
        terraform_target = ezfunctions.variablesFromAPI(kwargs)

        if terraform_target[0] == 'Terraform Enterprise':
            kwargs.jData = DotMap()
            kwargs.jData.default     = f'app.terraform.io'
            kwargs.jData.description = f'Hostname of the Terraform Enterprise Instance'
            kwargs.jData.pattern     = '^[a-zA-Z0-9\\-\\.\\:]+$'
            kwargs.jData.minimum     = 1
            kwargs.jData.maximum     = 90
            kwargs.jData.varInput    = f'What is the Hostname of the TFE Instance?'
            kwargs.jData.varName     = f'Terraform Target Name'
            polVars.tfc_host = ezfunctions.varStringLoop(kwargs)
            if re.search(r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", polVars.tfc_host):
                validating.ip_address('Terraform Target', polVars.tfc_host)
            elif ':' in polVars.tfc_host:
                validating.ip_address('Terraform Target', polVars.tfc_host)
            else: validating.dns_name('Terraform Target', polVars.tfc_host)
        else:
            polVars.tfc_host = 'app.terraform.io'
        #polVars = {}
        polVars.terraform_cloud_token = tf.terraform_cloud().terraform_token()
        #==============================================
        # Obtain Terraform Cloud Organization
        #==============================================
        if os.environ.get('tfc_organization') is None:
            polVars.tfc_organization = tf.terraform_cloud().tfc_organization(polVars, kwargs)
            os.environ.tfc_organization = polVars.tfc_organization
        else: polVars.tfc_organization = os.environ.get('tfc_organization')
        tfcb_config.append({'tfc_organization':polVars.tfc_organization})
        #==============================================
        # Obtain Version Control Provider
        #==============================================
        if os.environ.get('tfc_vcs_provider') is None:
            tfc_vcs_provider,polVars.tfc_oath_token = tf.terraform_cloud().tfc_vcs_providers(polVars, kwargs)
            polVars.tfc_vcs_provider = tfc_vcs_provider
            os.environ.tfc_vcs_provider = tfc_vcs_provider
            os.environ.tfc_oath_token = polVars.tfc_oath_token
        else:
            polVars.tfc_vcs_provider = os.environ.get('tfc_vcs_provider')
            polVars.tfc_oath_token = os.environ.tfc_oath_token
        #==============================================
        # Obtain Version Control Base Repo
        #==============================================
        if os.environ.get('vcsBaseRepo') is None:
            polVars.vcsBaseRepo = tf.terraform_cloud().tfc_vcs_repository(polVars, kwargs)
            os.environ.vcsBaseRepo = polVars.vcsBaseRepo
        else: polVars.vcsBaseRepo = os.environ.get('vcsBaseRepo')
        
        polVars.agentPoolId = ''
        polVars.allowDestroyPlan = False
        polVars.executionMode = 'remote'
        polVars.queueAllRuns = False
        polVars.speculativeEnabled = True
        polVars.triggerPrefixes = []
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
        kwargs.jData = DotMap()
        kwargs.jData.default     = terraform_versions[0]
        kwargs.jData.description = "Terraform Version for Workspaces:"
        kwargs.jData.dontsort    = True
        kwargs.jData.enum        = terraform_versions
        kwargs.jData.varType     = 'Terraform Version'
        polVars.terraformVersion = ezfunctions.variablesFromAPI(kwargs)
        #==============================================
        # Begin Creating Workspaces
        #==============================================
        for org in orgs:
            kwargs.org = org
            kwargs.jData = DotMap()
            kwargs.jData.default     = f'{org}'
            kwargs.jData.description = f'Name of the {org} Workspace to Create in Terraform Cloud'
            kwargs.jData.pattern     = '^[a-zA-Z0-9\\-\\_]+$'
            kwargs.jData.minimum     = 1
            kwargs.jData.maximum     = 90
            kwargs.jData.varInput    = f'Terraform Cloud Workspace Name.'
            kwargs.jData.varName     = f'Workspace Name'
            polVars.workspaceName = ezfunctions.varStringLoop(kwargs)
            polVars.workspace_id = tf.terraform_cloud().tfcWorkspace(polVars, kwargs)
            vars = ['apikey.Intersight API Key', 'secretkey.Intersight Secret Key' ]
            for var in vars:
                pcolor.Green(f"* Adding {var.split('.')[1]} to {polVars.workspaceName}")
                kwargs['Variable'] = var.split('.')[0]
                if 'secret' in var:
                    kwargs['Multi_Line_Input'] = True
                polVars.description = var.split('.')[1]
                polVars['varId'] = var.split('.')[0]
                polVars['varKey'] = var.split('.')[0]
                kwargs = ezfunctions.sensitive_var_value(kwargs)
                polVars['varValue'] = kwargs['var_value']
                polVars['Sensitive'] = True
                if 'secret' in var and opSystem == 'Windows':
                    if os.path.isfile(polVars['varValue']):
                        f = open(polVars['varValue'])
                        polVars['varValue'] = f.read().replace('\n', '\\n')
                tf.terraform_cloud().tfcVariables(polVars, kwargs)
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
                kwargs = ezfunctions.policies_parse('policies', policy, policy)
                policies = deepcopy(kwargs['policies'][policy])
                y = var.split('.')[0]
                z = var.split('.')[1]
                if len(policies) > 0:
                    if y == 'persistent_memory':
                        varValue = z
                        polVars = ezfunctions.tfc_sensitive_variables(varValue, jsonData, **polVars)
                        tf.terraform_cloud().tfcVariables(**polVars)
                    else:
                        for item in policies:
                            if y == 'ipmi_over_lan' and item.get('enabled'):
                                varValue = z
                                polVars = ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                tf.terraform_cloud().tfcVariables(**polVars)
                            elif y == 'iscsi_boot' and item.get('authentication'):
                                if re.search('chap', item['authentication']):
                                    varValue = z
                                    polVars = ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                    tf.terraform_cloud().tfcVariables(**polVars)
                            elif y == 'ldap' and item.get('binding_parameters'):
                                if item['binding_parameters'].get('bind_method'):
                                    if item['binding_parameters']['bind_method'] == 'ConfiguredCredentials':
                                        varValue = z
                                        polVars = ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                        tf.terraform_cloud().tfcVariables(**polVars)
                            elif y == 'local_user':
                                if item.get('enforce_strong_password'):
                                    polVars['enforce_strong_password'] = item['enforce_strong_password']
                                else: polVars['enforce_strong_password'] = True
                                for i in item['users']:
                                    varValue = '%s_%s' % (z, i['password'])
                                    polVars = ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                    tf.terraform_cloud().tfcVariables(**polVars)
                            elif y == 'snmp':
                                if item.get('access_community_string'):
                                    varValue = 'access_community_string_%s' % (i['access_community_string'])
                                    polVars = ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                    tf.terraform_cloud().tfcVariables(**polVars)
                                if item.get('snmp_users'):
                                    for i in item['snmp_users']:
                                        varValue = 'snmp_auth_password_%s' % (i['auth_password'])
                                        polVars = ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                        tf.terraform_cloud().tfcVariables(**polVars)
                                        if i.get('privacy_password'):
                                            varValue = 'snmp_privacy_password_%s' % (i['privacy_password'])
                                            polVars = ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                            tf.terraform_cloud().tfcVariables(**polVars)
                                if item.get('snmp_traps'):
                                    for i in item['snmp_traps']:
                                        if i.get('community_string'):
                                            varValue = 'snmp_trap_community_%s' % (i['community_string'])
                                            polVars = ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                            tf.terraform_cloud().tfcVariables(**polVars)
                                if item.get('trap_community_string'):
                                    varValue = 'trap_community_string'
                                    polVars = ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                    tf.terraform_cloud().tfcVariables(**polVars)
                            elif y == 'virtual_media' and item.get('add_virtual_media'):
                                for i in item['add_virtual_media']:
                                    if i.get('password'):
                                        varValue = '%s_%s' % (z, i['password'])
                                        polVars = ezfunctions.tfc_sensitive_variables(varValue, jsonData, polVars)
                                        tf.terraform_cloud().tfcVariables(**polVars)
    else:
        pcolor.Cyan(f'\n-------------------------------------------------------------------------------------------\n')
        pcolor.Cyan(f'  Skipping Step to Create Terraform Cloud Workspaces.')
        pcolor.Cyan(f'  Moving to last step to Confirm the Intersight Organization Exists.')
        pcolor.Cyan(f'\n-------------------------------------------------------------------------------------------\n')
    # Configure the provider.tf and variables.auto.tfvars
    name_prefix = 'dummy'
    type = 'policies'
    policies.policies(name_prefix, org, type).variables(kwargs)
    # Return kwargs
    return kwargs
     
#=================================================================
# Function: Main Menu
#=================================================================
def main_menu(kwargs):
    pcolor.Cyan(f'\n{"-"*91}\n\n  Starting the Easy IMM Configuration Wizard!\n\n{"-"*91}\n')
    kwargs = questions.previous_configuration(kwargs)
    kwargs.main_menu_list = []
    kwargs = questions.main_menu_deployment_type(kwargs)
    def running_thru_orgs(kwargs):
        if kwargs.deployment_type == 'Individual':
            kwargs.imm_dict.orgs[kwargs.org].wizard.build_type = 'Interactive'
        if kwargs.deployment_type == 'Profile':
            kwargs.imm_dict.orgs[kwargs.org].wizard.build_type = 'Machine'
        if not kwargs.imm_dict.orgs[kwargs.org].wizard.build_type:
            kwargs = questions.main_menu_build_type(kwargs)
        if not kwargs.imm_dict.orgs[kwargs.org].wizard.deployment_method:
            kwargs = questions.main_menu_deployment_method(kwargs)
        if re.search('Individual|Profile', kwargs.deployment_type):
            if not kwargs.imm_dict.orgs[kwargs.org].wizard.target_platform:
                kwargs = questions.target_platform(kwargs)
        elif re.search('FIAttached|Standalone', kwargs.deployment_type):
            kwargs.target_platform = kwargs.deployment_type
            if not kwargs.imm_dict.orgs[kwargs.org].wizard.operating_systems:
                kwargs = questions.main_menu_operating_systems(kwargs)
            if not kwargs.imm_dict.orgs[kwargs.org].wizard.assignment_method:
                kwargs = questions.main_menu_assignment_method(kwargs)
            if kwargs.imm_dict.orgs[kwargs.org].wizard.build_type == 'Machine':
                if not kwargs.imm_dict.orgs[kwargs.org].wizard.discovery:
                    kwargs = questions.main_menu_discovery(kwargs)
        if not 'name_prefix' in list(kwargs.imm_dict.orgs[kwargs.org].wizard.keys()): kwargs = questions.main_menu_name_prefix(kwargs)
        if not 'name_suffix' in list(kwargs.imm_dict.orgs[kwargs.org].wizard.keys()): kwargs = questions.main_menu_name_suffix(kwargs)
        for p in ['pools', 'policies']:
            kwargs.imm_dict.orgs[kwargs.org][p].name_prefix.default = kwargs.name_prefix
            kwargs.imm_dict.orgs[kwargs.org][p].name_suffix.default = kwargs.name_suffix
        #==============================================
        # Create YAML Files
        #==============================================
        ezfunctions.create_wizard_yaml(kwargs)
        #==============================================
        # Build Pool/Policy/Profile List
        #==============================================
        kwargs = build_policy_list(kwargs)
        if 'Individual' in kwargs.deployment_type:
            kwargs = questions.main_menu_individual_types(kwargs)
            kwargs = questions.main_menu_individual(kwargs)
        elif re.search('FIAttached', kwargs.deployment_type):
            kwargs.ptypes = ['Pools', 'Policies', 'Profiles']
            if 'Pools' in kwargs.ptypes: kwargs.main_menu_list.extend(kwargs.pool_list)
            if 'Policies' in kwargs.ptypes: kwargs.main_menu_list.extend(kwargs.policy_list)
            if 'Profiles' in kwargs.ptypes:
                if kwargs.target_platform == 'Standalone': kwargs.main_menu_list.extend(['server', 'server_template'])
                else: kwargs.main_menu_list.extend(['chassis', 'domain', 'server', 'server_template'])
        if not 'Resource' in kwargs.imm_dict.orgs[kwargs.org].wizard.assignment_method:
            if 'resource' in kwargs.main_menu_list: kwargs.main_menu_list.remove('resource')
        else: pcolor.Red(kwargs.imm_dict.orgs[kwargs.org].wizard.assignment_method); sys.exit(1)
        return kwargs
    if not re.search('Exit|Deploy', kwargs.deployment_type):
        #==============================================
        # Prompt User with Questions
        #==============================================
        if len(kwargs.imm_dict.orgs.keys()) == 0:
            kwargs = questions.organization(kwargs)
            kwargs.imm_dict.orgs[kwargs.org] = DotMap()
            kwargs = running_thru_orgs(kwargs)
        else:
            kwargs = questions.organization(kwargs)
            orgs = list(kwargs.imm_dict.orgs.keys())
            if kwargs.org in orgs:
                for org in orgs:
                    kwargs.org = org
                    if kwargs.imm_dict.orgs[kwargs.org].get('wizard'):
                        for k,v in kwargs.imm_dict.orgs[kwargs.org].wizard.items(): kwargs[k] = v
                    kwargs = running_thru_orgs(kwargs)
            else: kwargs = running_thru_orgs(kwargs)

    return kwargs


#=================================================================
# Function: Wizard
#=================================================================
def process_wizard(kwargs):
    #==============================================
    # Process List from Main Menu
    #==============================================
    for p in kwargs.main_menu_list:
        profile_list = ['chassis', 'domain', 'server', 'server_template']
        #==============================================
        # Intersight Pools/Policies
        #==============================================
        if p in kwargs.pool_list or p in kwargs.policy_list or p in profile_list:
            kwargs = build.build_imm(p).ezimm(kwargs)
    return kwargs

#==============================================
# Function: Main Script
#==============================================
def main():
    #==============================================
    # Configure logger and Build kwargs
    #==============================================
    script_name = (sys.argv[0].split(os.sep)[-1]).split('.')[0]
    dest_dir = f"{Path.home()}{os.sep}Logs"
    dest_file = script_name + '.log'
    if not os.path.exists(dest_dir): os.mkdir(dest_dir)
    if not os.path.exists(os.path.join(dest_dir, dest_file)): 
        create_file = f'type nul >> {os.path.join(dest_dir, dest_file)}'; os.system(create_file)
    FORMAT = '%(asctime)-15s [%(levelname)s] [%(filename)s:%(lineno)s] %(message)s'
    logging.basicConfig( filename=f"{dest_dir}{os.sep}{script_name}.log", filemode='a', format=FORMAT, level=logging.DEBUG )
    logger = logging.getLogger('openapi')
    kwargs = cli_arguments()
    if os.getenv('intersight_fqdn'): kwargs.args.intersight_fqdn = os.getenv('intersight_fqdn')
    if os.getenv('intersight_secret_key'): kwargs.args.intersight_secret_key = os.getenv('intersight_secret_key')
    #==============================================
    # Determine the Script Path
    #==============================================
    kwargs.script_path= script_path
    args_dict = vars(kwargs.args)
    for k,v in args_dict.items():
        if type(v) == str:
            if v: os.environ[k] = v
    if kwargs.args.intersight_secret_key:
        if '~' in kwargs.args.intersight_secret_key:
            kwargs.args.intersight_secret_key = os.path.expanduser(kwargs.args.intersight_secret_key)
    kwargs.home      = Path.home()
    kwargs.logger    = logger
    kwargs.op_system = platform.system()
    #================================================
    # Import Stored Parameters and Add to kwargs
    #================================================
    ezdata = materialize(RefDict(f'{script_path}{os.sep}variables{os.sep}easy-imm.json', 'r', encoding="utf8"))
    kwargs.ez_tags = {'Key':'ezimm','Value':ezdata['info']['version']}
    kwargs.ezdata  = DotMap(ezdata['components']['schemas'])
    #==============================================
    # Get Intersight Configuration
    # - apikey
    # - endpoint
    # - keyfile
    #==============================================
    kwargs = ezfunctions.intersight_config(kwargs)
    kwargs.args.url = 'https://%s' % (kwargs.args.intersight_fqdn)
    #==============================================
    # Check Folder Structure for Illegal Characters
    #==============================================
    for folder in kwargs.args.dir.split(os.sep):
        if folder == '': fcount = 0
        elif not re.search(r'^[\w\-\.\:\/\\]+$', folder):
            prRed(f'\n{"-"*91}\n\n  !!ERROR!!')
            prRed(f'  The Directory structure can only contain the following characters:')
            prRed(f'  letters(a-z, A-Z), numbers(0-9), hyphen(-), period(.), colon(:), and underscore(-).')
            prRed(f'  It can be a short path or a fully qualified path.  "{folder}" does not qualify.')
            prRed(f'  Exiting...\n\n{"-"*91}\n')
            sys.exit(1)
    #==============================================
    # Run IMM Transition if json Arg Present
    #==============================================
    if not kwargs.args.json_file == None:
        #==============================================
        # Validate the Existence of the json File
        #==============================================
        if not os.path.isfile(kwargs.args.json_file):
            prRed(f'\n{"-"*91}\n\n  !!ERROR!!\n  Did not find the file {kwargs.args.json_file}.')
            prRed(f'  Please Validate that you have specified the correct file and path.\n\n{"-"*91}\n')
            sys.exit(1)
        else:
            kwargs.deployment_type = 'Terraform'
            json_file = kwargs.args.json_file
            json_open = open(json_file, 'r')
            kwargs.json_data = DotMap(json.load(json_open))
            device_type = kwargs.json_data.easyucs.metadata[0].device_type
            #==============================================
            # Validate the device_type in json file
            #==============================================
            if not device_type == 'intersight':
                prRed(f'\n{"-"*91}\n\n  !!ERROR!!\n  The File "{kwargs.args.json_file}" device_type is "{device_type}".')
                prRed(f'  This file is the UCSM Configuration converted from XML to JSON.')
                prRed(f'  The device_type is found on line 10 of the json config file.')
                prRed(f'  The Script is looking for the file that has been converted to Intersight Managed Mode.')
                prRed(f'  The JSON file should be downloaded at the last step of the IMM Transition tool where the')
                prRed(f'  API Key and Secret would be entered to upload to Intersight.')
                prRed(f'  Exiting Wizard...\n\n{"-"*91}\n')
                sys.exit(1)
            #==============================================
            # Run through the IMM Transition Wizard
            #==============================================
            kwargs = imm.transition('transition').policy_loop(kwargs)
            kwargs.orgs = list(kwargs.imm_dict.orgs.keys())
    else:
        #==============================================
        # Prompt User for Main Menu
        #==============================================
        kwargs = main_menu(kwargs)
        if not re.search('Exit|Deploy', kwargs.deployment_type):
            kwargs = process_wizard(kwargs)
        kwargs.orgs = list(kwargs.imm_dict.orgs.keys())
        if re.search('Deploy', kwargs.deployment_type): kwargs.args.deployment_method = 'Python'
    #==============================================
    # Create YAML Files
    #==============================================
    orgs = kwargs.orgs
    ezfunctions.create_yaml(orgs, kwargs)
    if len(kwargs.imm_dict.orgs.keys()) > 0:
        kwargs = isight.api('organization').organizations(kwargs)
        if kwargs.args.deployment_method == 'Terraform':
            #==============================================
            # Create Terraform Config and Workspaces
            #==============================================
            ezfunctions.merge_easy_imm_repository(kwargs)
            kwargs = ezfunctions.terraform_provider_config(kwargs)
            kwargs = create_terraform_workspaces(orgs, kwargs)
        elif kwargs.args.deployment_method == 'Python':
            #==============================================
            # Pools
            #==============================================
            pool_list = []
            for k, v in kwargs.ezdata.items():
                if v.intersight_type == 'pool' and not '.' in k: pool_list.append(k)
            for org in orgs:
                kwargs.org = org
                if kwargs.imm_dict.orgs[org].get('pools'):
                    for ptype in pool_list:
                        if ptype in kwargs.imm_dict.orgs[org]['pools']:  kwargs = eval(f"isight.imm(ptype).pools(kwargs)")
            #==============================================
            # Policies
            #==============================================
            policy_list = []
            for k, v in kwargs.ezdata.items():
                if v.intersight_type == 'policy' and not '.' in k: policy_list.append(k)
            for org in orgs:
                kwargs.org = org
                if kwargs.imm_dict.orgs[org].get('policies'):
                    for ptype in policy_list:
                        if ptype in kwargs.imm_dict.orgs[org]['policies']:  kwargs = eval(f"isight.imm(ptype).policies(kwargs)")
            #==============================================
            # Profiles
            #==============================================
            for org in orgs:
                kwargs.org = org
                if kwargs.imm_dict.orgs[org].get('templates'):
                    if kwargs.imm_dict.orgs[org]['templates'].get('server'): kwargs = eval(f"isight.imm('server_template').profiles(kwargs)")
                if kwargs.imm_dict.orgs[org].get('profiles'):
                    profile_list = ['domain', 'chassis', 'server']
                    for i in profile_list:
                        if kwargs.imm_dict.orgs[org]['profiles'].get(i): kwargs = eval(f"isight.imm(i).profiles(kwargs)")

    pcolor.Cyan(f'\n{"-"*91}\n\n  !!! Proceedures Complete !!!\n  Closing Environment and Exiting Script...\n\n{"-"*91}\n')
    sys.exit(0)

if __name__ == '__main__':
    main()
