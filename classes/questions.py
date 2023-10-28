#=============================================================================
# Source Modules
#=============================================================================
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
import sys
try:
    from classes import ezfunctions, isight, pcolor
    from dotmap import DotMap
    import os, re, textwrap, yaml
except ImportError as e:
    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
    prRed(f" Module {e.name} is required to run this script")
    prRed(f" Install the module using the following: `pip install {e.name}`")
    sys.exit(1)

# Exception Classes
class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, indentless)

#=================================================================
# Function: Prompt User with Existing Pools/Policies/Profiles
#=================================================================
def existing_object(ptype, item, kwargs):
    attributes = kwargs.imm_dict.orgs[kwargs.org][ptype][item]
    ptitle = ezfunctions.mod_pol_description((item.replace('_', ' ')).title())
    #==============================================
    # Show User Configuration
    #==============================================
    pcolor.Green(f'\n{"-"*91}\n  Found Existing Configuration:\n')
    pcolor.Green(textwrap.indent(yaml.dump(attributes, Dumper=MyDumper, default_flow_style=False), " "*3, predicate=None))
    pcolor.Green(f'\n{"-"*91}\n')
    kwargs.jdata = DotMap(
        default     = False,
        description = f'Do you want to Delete Any of these?',
        title       = 'Delete Policies',
        type        = 'boolean'
    )
    del_objects = ezfunctions.variablePrompt(kwargs)
    if del_objects == True:
        kwargs.jdata = DotMap(
            enum        = [e.name for e in kwargs.imm_dict.orgs[kwargs.org][ptype][item]],
            description = f'Select the Options you want to Delete:',
            optional    = True,
            multi_select= True,
            title       = 'Delete Objects',
            type        = 'string'
        )
        delete_objects = ezfunctions.variablePrompt(kwargs)
        for e in delete_objects:
            idict = [i for i in kwargs.imm_dict.orgs[kwargs.org][ptype][item] if not (i.name == e)]
            kwargs.imm_dict.orgs[kwargs.org][ptype][item] = idict
        kwargs.jdata = DotMap(
            default     = False,
            description = f'Do you want to Delete `{e}` from Intersight as well?',
            title       = f'Delete {e}',
            type        = 'boolean'
        )
        del_int = ezfunctions.variablePrompt(kwargs)
        if del_int == True:
            kwargs.uri = kwargs.ezdata[ptype].intersight_uri
            kwargs = isight.api_get(False, [e], ptype, kwargs)
            if len(kwargs.results) > 0:
                kwargs.method = 'delete'
                kwargs = isight.api(ptype).calls(kwargs)
            else:
                pcolor.Red(f"\n{'-'*91}\n")
                pcolor.Red(f'  !!! ERROR !!!!\n  Did not find {ptitle}: `{e}` in Intersight')
                pcolor.Red(f"\n{'-'*91}\n")
    kwargs.jdata = DotMap(
        default     = True,
        description = f'Do you want to configure additional {ptitle} {ptype.title()}s?',
        title       = 'Config',
        type        = 'boolean'
    )
    kwargs.configure_more = ezfunctions.variablePrompt(kwargs)
    return kwargs

#=================================================================
# Function: Main Menu, Prompt User for Deployment Type
#=================================================================
def main_menu_assignment_method(kwargs):
    description = 'Select the Method you will use to assign server profiles:\n'
    d1 = '* Chassis/Slot:  Assign Server Profiles to Chassis/Slot.\n'
    d2 = '* Resource Pool: Assign Server Profiles to Resource Pools.\n'
    d3 = '* Serial:        Assign Server Profiles based on the Server Serial Number.'
    if kwargs.target_platform == 'FIAttached':
        description = description + d1 + d2 + d3
        enum_list   = ['Chassis/Slot', 'Resource Pool', 'Serial']
    else:
        description = description + d2 + d3
        enum_list   = ['Resource Pool', 'Serial']
    kwargs.jdata = DotMap(
        enum         = enum_list,
        default      = 'Serial',
        description  = description,
        title        = 'Deployment Type',
        type         = 'string'
    )
    kwargs.imm_dict.orgs[kwargs.org].wizard.assignment_method = ezfunctions.variablePrompt(kwargs)
    return kwargs

#=================================================================
# Function: Prompt User for Build Method
#=================================================================
def main_menu_discovery(kwargs):
    kwargs.jdata = DotMap(
        default      = False,
        description  = 'Is the Equipment Already Registered to Intersight?',
        title        = 'Discovery Status',
        type         = 'boolean'
    )
    kwargs.imm_dict.orgs[kwargs.org].wizard.discovery = ezfunctions.variablePrompt(kwargs)
    return kwargs

#=================================================================
# Function: Prompt User for Build Method
#=================================================================
def main_menu_build_type(kwargs):
    description = 'Choose the Automation Method.\n'\
    '* Interactive: This Wizard will Prompt the User for all Pool, Policy, and Profile settings.\n'\
    '* Machine: This Wizard will Discover the Inventory, and configure based on Best Practices, '\
        'only prompting for information unique to an environment.'
    kwargs.jdata = DotMap(
        enum         = ['Interactive', 'Machine'],
        default      = 'Machine',
        description  = description,
        title        = 'Automation Type',
        type         = 'string'
    )
    kwargs.imm_dict.orgs[kwargs.org].wizard.build_type = ezfunctions.variablePrompt(kwargs)
    return kwargs

#=================================================================
# Function: Prompt User for Deployment Type: Python/Terraform
#=================================================================
def main_menu_deployment_method(kwargs):
    deployment_method = kwargs.args.deployment_method
    if deployment_method == None: deployment_method = ''
    if re.search('Python|Terraform', deployment_method): kwargs.imm_dict.orgs[kwargs.org].wizard.deployment_method = deployment_method
    else:
        description = 'Choose the Automation Language You want to use to deploy to Intersight.\n'\
        '* Python: This Wizard will Create the YAML Files and Deploy to Intersight.\n'\
        '* Terraform: This Wizard will only Create the YAML Files.  Terraform will be used to Manage Deployment and IaC.'
        kwargs.jdata = DotMap(
            enum         = ['Python', 'Terraform'],
            default      = 'Python',
            description  = description,
            title        = 'Automation Type',
            type         = 'string'
        )
    kwargs.imm_dict.orgs[kwargs.org].wizard.deployment_method = ezfunctions.variablePrompt(kwargs)
    return kwargs

#=================================================================
# Function: Main Menu, Prompt User for Deployment Type
#=================================================================
def main_menu_deployment_type(kwargs):
    description = 'Select the Option to Perform:\n'\
    '* FIAttached: Build Pools/Policies/Profiles for a Domain.\n'\
    '* Standalone: Build Pools/Policies/Profiles for a Group of Standalone Servers.\n'\
    '* Profile:    Deploy a Profile from an Existing Server Profile Template.\n'\
    '* Individual: Select Individual Pools, Policies, Profiles to Build.\n'\
    '* Deploy:     Skip Wizard and deploy configured from the YAML Files for Pools, Policies, and Profiles.\n'\
    '* Exit:       Cancel the Wizard'
    kwargs.jdata = DotMap(
        enum         = ['FIAttached', 'Standalone', 'Profile', 'Individual', 'Deploy', 'Exit'],
        default      = 'FIAttached',
        description  = description,
        multi_select = False,
        sort         = False,
        title        = 'Deployment Type',
        type         = 'string'
    )
    kwargs.deployment_type = ezfunctions.variablePrompt(kwargs)
    return kwargs

#=================================================================
# Function: Prompt User for Pools/Policies/Profiles to Create
#=================================================================
def main_menu_individual(kwargs):
    kwargs.main_menu_list = []
    for e in kwargs.ptypes:
        if 'Pools' in e: default = 'ip'; main_menu_list = kwargs.pool_list
        elif 'Policies' in e: default = 'bios'; main_menu_list = kwargs.policy_list
        elif 'Profiles' in e:
            default = 'server_template'
            if kwargs.target_platform == 'Standalone': main_menu_list = ['server', 'server_template']
            else: main_menu_list = ['chassis', 'domain', 'server', 'server_template']
        kwargs.jdata = DotMap(
            enum         = main_menu_list,
            default      = default,
            description  = f'Select the {e} to Apply to the Environment:',
            multi_select = True,
            sort         = False,
            title        = e,
            type         = 'string'
        )
        kwargs.main_menu_list.extend(ezfunctions.variablePrompt(kwargs))
    return kwargs

#=================================================================
# Function: Prompt User for Individual Types
#=================================================================
def main_menu_individual_types(kwargs):
    kwargs.jdata = DotMap(
        enum         = ['Pools', 'Policies', 'Profiles'],
        default      = 'Policies',
        description  = 'Choose the indidividual type(s) to create.',
        sort         = False,
        multi_select = True,
        title        = 'Individual Type(s)',
        type         = 'string'
    )
    kwargs.ptypes = ezfunctions.variablePrompt(kwargs)
    return kwargs

#=================================================================
# Function: Prompt User for Build Method
#=================================================================
def main_menu_name_prefix(kwargs):
    if not kwargs.imm_dict.orgs[kwargs.org].policies.get('name_prefix'):
        #==============================================
        # Prompt User for Name Prefix
        #==============================================
        kwargs.jdata = DotMap(
            description = f'Name Prefix to assign to Pools and Policies.',
            maxLength   = 32,
            minLength   = 0,
            optional    = True,
            pattern     = "^[a-zA-Z0-9_\\. :-]{0,32}$",
            title       = 'Name Prefix',
            type        = 'string'
        )
        kwargs.imm_dict.orgs[kwargs.org].wizard.name_prefix = ezfunctions.variablePrompt(kwargs)
    return kwargs

#=================================================================
# Function: Prompt User for Build Method
#=================================================================
def main_menu_name_suffix(kwargs):
    if not kwargs.imm_dict.orgs[kwargs.org].policies.get('name_suffix'):
        #==============================================
        # Prompt User for Name Prefix
        #==============================================
        kwargs.jdata = DotMap(
            description = f'Name Suffix to assign to Pools and Policies.',
            maxLength   = 32,
            minLength   = 0,
            optional    = True,
            pattern     = "^[a-zA-Z0-9_\\. :-]{0,32}$",
            title       = 'Name Suffix',
            type        = 'string'
        )
        kwargs.imm_dict.orgs[kwargs.org].wizard.name_suffix = ezfunctions.variablePrompt(kwargs)
    return kwargs

#=================================================================
# Function: Prompt User for Target Platform
#=================================================================
def main_menu_operating_systems(kwargs):
    if 'FIAttached' == kwargs.target_platform: enum_list = ['Linux', 'VMware', 'Windows']
    else: enum_list = ['AzureStack', 'Linux', 'VMware', 'Windows']
    kwargs.jdata = DotMap(
        enum         = enum_list,
        default      = 'VMware',
        description  = 'Select the Operating System(s) to be installed for this deployment.',
        multi_select = True,
        title        = 'Operating System(s)',
        type         = 'string'
    )
    if kwargs.imm_dict.orgs[kwargs.org].wizard.deployment_type == 'Profile': kwargs.jdata.multi_select == False
    kwargs.imm_dict.orgs[kwargs.org].wizard.operating_systems = ezfunctions.variablePrompt(kwargs)
    return kwargs

#=================================================================
# Function: Prompt User for Intersight Organization
#=================================================================
def organization(kwargs):
    kwargs = isight.api('organization').all_organizations(kwargs)
    org_list = sorted(list(kwargs.org_moids.keys()), key=str.casefold)
    org_list.append('Create New')
    kwargs.jdata = DotMap(
        enum        = org_list,
        default     = 'default',
        description = 'Select an Existing Organization or `Create New`, for the organization to apply these changes within.',
        sort        = False,
        title       = 'Intersight Organization',
        type        = 'string')
    kwargs.org = ezfunctions.variablePrompt(kwargs)
    if kwargs.org == 'Create New':
        kwargs.jdata = DotMap(
            description = 'Name for the Organization',
            title       = 'Intersight Organization',
            type        = 'string')
        kwargs.org = ezfunctions.variablePrompt(kwargs)
        kwargs.api_body = { "Name":f'{kwargs.org}', "ObjectType":"resource.Group" }
        kwargs.method = 'post'
        kwargs = isight.api(kwargs.qtype).calls(kwargs)
        rg_moid = kwargs.pmoid
        kwargs.api_body = {
            "Name":kwargs.org, "ObjectType":"organization.Organization",
            "ResourceGroups":[{"Moid": rg_moid, "ObjectType":"resource.Group"}]}
        kwargs = isight.api(kwargs.qtype).calls(kwargs)
        kwargs.org_moids[kwargs.org] = DotMap(moid = kwargs.pmoid)
    return kwargs

#=================================================================
# Function: Prompt User to Load Previous Configurations
#=================================================================
def previous_configuration(kwargs):
    dir_check = False; load_config = False
    if os.path.exists(kwargs.args.dir):
        for e in os.listdir(kwargs.args.dir):
            if re.search('^policies|pools|profiles|templates|wizard$', e): dir_check = True
        if dir_check == True and kwargs.args.load_config == False:
            kwargs.jdata = DotMap(
                default     = True,
                description = f'Import Configuration found in `{kwargs.args.dir}`',
                title       = 'Load Existing Configuration(s)',
                type        = 'boolean'
            )
            load_config = ezfunctions.variablePrompt(kwargs)
            kwargs.args.load_config = True
        elif kwargs.args.load_config == True: load_config = True
        if load_config == True and kwargs.args.load_config == True:
            kwargs = DotMap(ezfunctions.load_previous_configurations(kwargs))
    return kwargs

#=================================================================
# Function: Prompt User to Configure
#=================================================================
def prompt_user_for_sub_item(item, kwargs):
    kwargs.jdata = DotMap(
        default      = True,
        description  = f'Do You want to configure `{item}`?',
        title        = item,
        type         = 'boolean'
    )
    answer = ezfunctions.variablePrompt(kwargs)
    return answer

#=================================================================
# Function: Prompt User to Accept Configuration
#=================================================================
def prompt_user_to_accept(item, idict, kwargs):
    pcolor.Green(f'\n{"-"*91}\n')
    pcolor.Green(textwrap.indent(yaml.dump(idict.toDict(), Dumper=MyDumper, default_flow_style=False), prefix=" "*3, predicate=None))
    pcolor.Green(f'\n{"-"*91}\n')
    kwargs.jdata = DotMap(
        default      = True,
        description  = f'Do You want to accept the above configuration for {item}?',
        title        = f'Accept',
        type         = 'boolean'
    )
    answer = ezfunctions.variablePrompt(kwargs)
    return answer

#=================================================================
# Function: Prompt User to Configure
#=================================================================
def promp_user_to_add(item, kwargs):
    ptype = kwargs.ezdata[item].intersight_type
    kwargs.jdata = DotMap(
        default      = False,
        description  = f'Do You want to configure additional {item}s?',
        title        = item,
        type         = 'boolean'
    )
    answer = ezfunctions.variablePrompt(kwargs)
    return answer

#=================================================================
# Function: Prompt User to Configure
#=================================================================
def prompt_user_to_configure(item, ptype, kwargs):
    ptitle = ezfunctions.mod_pol_description((item.replace('_', ' ')).title())
    kwargs.jdata = DotMap(
        default      = True,
        description  = f'Do You want to configure a {ptitle} {ptype.title()}s?',
        title        = f'{ptitle} {ptype.title()}',
        type         = 'boolean'
    )
    answer = ezfunctions.variablePrompt(kwargs)
    return answer

#=================================================================
# Function: Prompt User for Value
#=================================================================
def prompt_user_item(k, v, kwargs):
    kwargs.jdata = v
    kwargs.jdata.title = k
    answer = ezfunctions.variablePrompt(kwargs)
    return answer

#=================================================================
# Function: Prompt User for Target Platform
#=================================================================
def target_platform(kwargs):
    description = 'Select the Server Profile Target Platform.  Options are:\n'\
    '* FIAttached: Build Pools/Policies/Profiles for a Domain.\n'\
    '* Standalone: Build Pools/Policies/Profiles for Standalone Servers.\n'
    kwargs.jdata = DotMap(
        enum         = ['FIAttached', 'Standalone'],
        default      = 'FIAttached',
        description  = description,
        multi_select = False,
        sort         = False,
        title        = 'Type of Servers',
        type         = 'string'
    )
    kwargs.imm_dict.orgs[kwargs.org].wizard.target_platform = ezfunctions.variablePrompt(kwargs)
    kwargs.target_platform = kwargs.imm_dict.orgs[kwargs.org].wizard.target_platform
    return kwargs
