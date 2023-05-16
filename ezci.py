#!/usr/bin/env python3
"""Converged Infrastructure Deployment - 
This Script is built to Deploy Converged Infrastructure from a YAML Configuration File.
The Script uses argparse to take in the following CLI arguments:
    a or api-key-id:      The Intersight API key id for HTTP signature scheme.
    d or dir:             Base Directory to use for creation of the YAML Configuration Files.
    e or endpoint:        The Intersight hostname for the API endpoint. The default is intersight.com.
    i or ignore-tls:      Ignore TLS server-side certificate verification.  Default is False.
    k or api-key-file:    Name of the file containing The Intersight secret key for the HTTP signature scheme.
    l or debug-level:     The Debug Level to Run for Script Output
    s or deployment-step: The steps in the proceedure to run. Options Are:
                            1. initial
                            2. servers
                            3. luns
                            4. operating_system
                            5. os_configuration
    t or deployment-type:    Infrastructure Deployment Type. Options Are:
                            1. azure_hci
                            2. netapp
                            3. pure
                            4. imm_domain
    v or api-key-v3:      Flag for API Key Version 3.
    y or yaml-file:       The input YAML File.
"""

#=====================================================
# Print Color Functions
#=====================================================
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prLightGray(skk): print("\033[94m {}\033[00m" .format(skk))
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk))
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))

#======================================================
# Source Modules
#======================================================
try:
    import sys
    sys.path.insert(0, './classes')
    from classes import ci
    from classes import ezfunctionsv2 as ezfunctions
    from classes import isight
    from classes import netapp
    from classes import network
    from classes import vsphere
    from copy import deepcopy
    from dotmap import DotMap
    from pathlib import Path
    import argparse
    import json
    import logging
    import os
    import platform
    import re
    import socket
    import yaml
except ImportError as e:
    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
    prRed(f" Module {e.name} is required to run this script")
    prRed(f" Install the module using the following: `pip install {e.name}`")



class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

#=================================================================
# Parse Arguments
#=================================================================
def cli_arguments():
    Parser = argparse.ArgumentParser(description='Intersight Converged Infrastructure Deployment Module')
    Parser.add_argument(
        '-a', '--api-key-id', default=os.getenv('intersight_apikey'),
        help='The Intersight API key id for HTTP signature scheme.'
    )
    Parser.add_argument(
        '-d', '--dir',
        default = 'Intersight',
        help = 'The Directory to use for the Creation of the Terraform Files.'
    )
    Parser.add_argument(
        '-e', '--endpoint', default='intersight.com',
        help='The Intersight hostname for the API endpoint. The default is intersight.com.'
    )
    Parser.add_argument(
        '-i', '--ignore-tls', action='store_false',
        help='Ignore TLS server-side certificate verification.  Default is False.'
    )
    Parser.add_argument(
        '-ilp', '--local-password-1',
        help='Intersight Managed Mode Local User Password 1.'
    )
    Parser.add_argument(
        '-ilp2', '--local-password-2',
        help='Intersight Managed Mode Local User Password 2.'
    )
    Parser.add_argument(
        '-isa', '--snmp-auth-password-1',
        help='Intersight Managed Mode SNMP Auth Password.'
    )
    Parser.add_argument(
        '-isp', '--snmp-privacy-password-1',
        help='Intersight Managed Mode SNMP Privilege Password.'
    )
    Parser.add_argument(
        '-k', '--api-key-file', default='~/Downloads/SecretKey.txt',
        #'-k', '--api-key-file', default=os.getenv('intersight_keyfile'),
        help='Name of the file containing The Intersight secret key for the HTTP signature scheme.'
    )
    Parser.add_argument(
        '-l', '--debug-level',
        default =0,
        help    ='The Amount of Debug output to Show:'\
            '1. Shows the api request response status code'
            '5. Show URL String + Lower Options'\
            '6. Adds Results + Lower Options'\
            '7. Adds json payload + Lower Options'\
            'Note: payload shows as pretty and straight to check for stray object types like Dotmap and numpy'
    )
    Parser.add_argument(
        '-np', '--netapp-password',
        help='NetApp Login Password.'
    )
    Parser.add_argument(
        '-nsa', '--netapp-snmp-auth',
        help='NetApp SNMP Auth Password.'
    )
    Parser.add_argument(
        '-nsp', '--netapp-snmp-priv',
        help='NetApp SNMP Privilege Password.'
    )
    Parser.add_argument(
        '-nxp', '--nexus-password',
        help='Nexus Login Password.'
    )
    Parser.add_argument(
        '-s', '--deployment-step',
        default ='flexpod',
        help    ='The steps in the proceedure to run. Options Are:'\
            '1. initial '
            '2. servers '\
            '3. luns '\
            '4. operating_system '\
            '5. os_configuration ',
        required=True
    )
    Parser.add_argument(
        '-t', '--deployment-type',
        default ='flexpod',
        help    ='Infrastructure Deployment Type. Options Are:'\
            '1. azure_hci '
            '2. flashstack '\
            '3. flexpod '\
            '4. imm_domain ',
        required=True
    )
    Parser.add_argument(
        '-v', '--api-key-v3', action='store_true',
        help='Flag for API Key Version 3.'
    )
    Parser.add_argument(
        '-vep', '--vmware-esxi-password',
        help='VMware ESXi Root Login Password.'
    )
    Parser.add_argument(
        '-vvp', '--vmware-vcenter-password',
        help='VMware vCenter Admin Login Password.'
    )
    Parser.add_argument(
        '-y', '--yaml-file',
        help = 'The input YAML File.'
    )
    kwargs = DotMap()
    kwargs.args = Parser.parse_args()
    return kwargs

#=================================================================
# The Main Module
#=================================================================
def main():
    #==============================================
    # Configure logger
    #==============================================
    dest_dir = f"{Path.home()}/Logs"
    dest_file = dest_dir + os.sep + sys.argv[0] + '.log'
    if not os.path.exists(dest_dir): os.mkdir(dest_dir)
    if not os.path.exists(os.path.join(dest_dir, dest_file)): 
        create_file = f'type nul >> {os.path.join(dest_dir, dest_file)}'
        os.system(create_file)

    script_name = sys.argv[0].split('/')[-1]
    FORMAT = '%(asctime)-15s [%(levelname)s] [%(filename)s:%(lineno)s] %(message)s'
    logging.basicConfig(
        filename=f"{Path.home()}{os.sep}Logs{os.sep}{script_name}.log",
        filemode='a',
        format=FORMAT,
        level=logging.DEBUG
    )
    logger = logging.getLogger('openapi')

    #==============================================
    # Build kwargs
    #==============================================
    kwargs   = cli_arguments()

    #==============================================
    # Determine the Script Path
    #==============================================
    kwargs.script_path= os.path.dirname(os.path.realpath(sys.argv[0]))
    script_path= kwargs.script_path
    kwargs.args.dir = os.path.join(script_path, kwargs.args.yaml_file.split('/')[0])

    args_dict = vars(kwargs.args)
    for k,v in args_dict.items():
        if type(v) == str:
            if v: os.environ[k] = v

    if kwargs.args.api_key_file:
        if '~' in kwargs.args.api_key_file:
            kwargs.args.api_key_file = os.path.expanduser(kwargs.args.api_key_file)

    kwargs.deployment_type= kwargs.args.deployment_type
    kwargs.home           = Path.home()
    kwargs.logger         = logger
    kwargs.op_system      = platform.system()
    kwargs.imm_dict.orgs  = DotMap()

    #==============================================
    # Add Sensitive Variables to Environment
    #==============================================
    if kwargs.args.nexus_password:
        os.environ['nexus_password'] = kwargs.args.nexus_password

    prLightGray(f'\n{"-"*91}\n')
    prLightGray(f'  Begin Deployment for {kwargs.deployment_type}.')
    prLightGray(f'  * Deployment Step is {kwargs.args.deployment_step}.')
    prLightGray(f'\n{"-"*91}\n')
    #================================================
    # Import Stored Parameters
    #================================================
    file       = f'{script_path}{os.sep}variables{os.sep}intersight-openapi-v3-1.0.11-11360.json'
    json_data  = json.load(open(file, 'r', encoding="utf8"))
    file       = f'{script_path}{os.sep}variables{os.sep}easy_variablesv2.json'
    ez_data    = json.load(open(file, 'r', encoding="utf8"))

    #================================================
    # Add Data to kwargs
    #================================================
    kwargs.ez_data  = DotMap(ez_data['components']['schemas'])
    kwargs.json_data= DotMap()
    kwargs.json_data= DotMap(json_data['components']['schemas'])

    #==============================================
    # Get Intersight Configuration
    # - apikey
    # - endpoint
    # - keyfile
    #==============================================
    kwargs         = ezfunctions.intersight_config(kwargs)
    kwargs.args.url= 'https://%s' % (kwargs.args.endpoint)

    #==============================================
    # Check Folder Path Naming for Bad Characters
    #==============================================
    destdirCheck = False
    while destdirCheck == False:
        path_sep = os.sep
        splitDir = kwargs.args.dir.split(path_sep)
        splitDir = [i for i in splitDir if i]
        for folder in splitDir:
            if not re.search(r'^[\w\-\.\:\/\\]+$', folder):
                prRed(folder)
                prRed(f'\n{"-"*91}\n')
                prRed(f'  !! ERROR !!')
                prRed(f'  The Directory structure can only contain the following characters:')
                prRed(f'  letters(a-z, A-Z), numbers(0-9), hyphen(-), period(.), colon(:), or and underscore(_).')
                prRed(f'  It can be a short path or a fully qualified path. {folder} failed this check.')
                prRed(f'\n{"-"*91}\n')
                sys.exit(1)
        destdirCheck = True

    #==============================================
    # Load Previous Configurations
    #==============================================
    kwargs = DotMap(ezfunctions.load_previous_configurations(kwargs))

    #==============================================
    # Process the YAML input File
    #==============================================
    if (kwargs.args.yaml_file):
        yfile = open(os.path.join(kwargs.args.yaml_file), 'r')
        kwargs.imm_dict.wizard = DotMap(yaml.safe_load(yfile))

    #==============================================
    # Build Deployment Library
    #==============================================
    kwargs = ci.wizard('dns_ntp').dns_ntp(kwargs)
    kwargs = ci.wizard('imm').imm(kwargs)
    kwargs = isight.api('organization').organizations(kwargs)
    kwargs = ci.wizard('vlans').vlans(kwargs)
    if re.search('(flexpod|flashstack)', kwargs.args.deployment_type):
        kwargs = eval(f"ci.wizard(kwargs.args.deployment_type).{kwargs.args.deployment_type}(kwargs)")

    #==============================================
    # Installation Files Location
    #==============================================
    kwargs.files_dir= '/var/www/upload'
    kwargs.repo_server= socket.getfqdn()
    kwargs.repo_path  = '/'


    #=================================================================
    # When Deployment Step is initial - Deploy NXOS|Storage|Domain
    #=================================================================
    if kwargs.args.deployment_step == 'initial':
        #==============================================
        # Configure Switches if configure Set to True
        #==============================================
        if kwargs.imm_dict.wizard.get('nxos'):
            network_config = DotMap(deepcopy(kwargs.imm_dict.wizard.nxos[0]))
            network_types = ['network', 'ooband']
            for network_type in network_types:
                config_count = 0
                for i in network_config.switches:
                    if i.configure == True and i.switch_type == network_type: config_count += 1
                if config_count == 2:
                    kwargs = network.nxos('nxos').config(network_config, network_type, kwargs)

        #==============================================
        # Configure Storage Appliances
        #==============================================
        if kwargs.args.deployment_type == 'flexpod':
            kwargs = ci.wizard('build').build_netapp(kwargs)

        #==============================================
        # Configure Domain
        #==============================================
        if re.search('(flashstack|flexpod|imm_domain)', kwargs.args.deployment_type):
            kwargs = ci.wizard('build').build_imm_domain(kwargs)

        #==============================================
        # Create YAML Files
        #==============================================
        orgs = list(kwargs.imm_dict.orgs.keys())
        ezfunctions.create_yaml(orgs, kwargs)

        for org in orgs:
            #==============================================
            # Policies
            #==============================================
            api = 'isight.policies_class'
            if kwargs.imm_dict.orgs[org].get('policies'):
                for ptype in kwargs.policy_list:
                    if kwargs.imm_dict.orgs[org]['policies'].get(ptype):
                        dpolicies = eval(f"{api}(ptype).policies(kwargs)")

            #==============================================
            # Deploy Domain
            #==============================================
            if re.search('(imm_domain|netapp|pure)', kwargs.args.deployment_type):
                kwargs = eval(f"isight.profiles_class('domain').profiles(kwargs)")


    #=================================================================
    # Deploy Chassis/Server Pools/Policies/Profiles
    #=================================================================
    elif kwargs.args.deployment_step == 'servers':
        kwargs.deployed = {}
        #==============================================
        # Configure and Deploy Server Profiles
        #==============================================
        kwargs = ci.wizard('build').build_imm_servers(kwargs)

        #==============================================
        # Create YAML Files
        #==============================================
        orgs = list(kwargs.imm_dict.orgs.keys())
        ezfunctions.create_yaml(orgs, kwargs)

        for org in orgs:
            #==============================================
            # Pools
            #==============================================
            api = 'isight.pools_class'
            if kwargs.imm_dict.orgs[org].get('pools'):
                for pool_type in kwargs.imm_dict.orgs[org]['pools']:
                    kwargs = eval(f"{api}(pool_type).pools(kwargs)")

            #==============================================
            # Policies
            #==============================================
            api = 'isight.policies_class'
            if kwargs.imm_dict.orgs[org].get('policies'):
                for ptype in kwargs.policy_list:
                    if kwargs.imm_dict.orgs[org]['policies'].get(ptype):
                        dpolicies = eval(f"{api}(ptype).policies(kwargs)")
                        kwargs.deployed.update({ptype:dpolicies})

            #==============================================
            # Profiles
            #==============================================
            api = 'isight.profiles_class'
            ptype = 'templates'
            if kwargs.imm_dict.orgs[org].get(ptype):
                if kwargs.imm_dict.orgs[org][ptype].get('server'):
                    kwargs = eval(f"{api}(ptype).profiles(kwargs)")
            ptype = 'profiles'
            if kwargs.imm_dict.orgs[org].get(ptype):
                profile_list = ['chassis', 'server']
                for i in profile_list:
                    if kwargs.imm_dict.orgs[org][ptype].get(i):
                        kwargs = eval(f"{api}(i).profiles(kwargs)")

    #=================================================================
    # Configure Luns/igroups/mapping - Collect Server Identities
    #=================================================================
    elif kwargs.args.deployment_step == 'luns':
        #==============================================
        # Loop Through the Orgs
        #==============================================
        orgs = list(kwargs.imm_dict.orgs.keys())
        for org in orgs:
            #==============================================
            # Server Identities
            #==============================================
            kwargs = ci.wizard('wizard').server_identities(kwargs)

        #==============================================
        # Create YAML Files
        #==============================================
        ezfunctions.create_yaml(orgs, kwargs)


    #=================================================================
    # Install the Operating System
    #=================================================================
    elif kwargs.args.deployment_step == 'operating_system':
        #==============================================
        # Loop Through the Orgs
        #==============================================
        orgs = list(kwargs.imm_dict.orgs.keys())
        for org in orgs:
            #=====================================================
            # Load Variables and Login to ESXi Hosts
            #=====================================================
            for i in kwargs.imm_dict.orgs[kwargs.org].wizard.os_configuration:
                for k, v in i.items():
                    kwargs.server_profiles[i.name][k] = v

            #==============================================
            # Install OS
            #==============================================
            kwargs = ci.wizard('os_install').os_install(kwargs)

    #=================================================================
    # Configure the Operating System
    #=================================================================
    if kwargs.args.deployment_step == 'os_configure':
        #==============================================
        # Loop Through the Orgs
        #==============================================
        orgs = list(kwargs.imm_dict.orgs.keys())
        for org in orgs:
            #=====================================================
            # Load Variables and Login to ESXi Hosts
            #=====================================================
            for i in kwargs.imm_dict.orgs[kwargs.org].wizard.os_configuration:
                for k, v in i.items():
                    kwargs.server_profiles[i.name][k] = v
            
            #==============================================
            # Configure Virtualization Environment
            #==============================================
            vmware = False
            for i in kwargs.virtualization:
                if i.type == 'vmware': vmware = True
            if vmware == True:
                kwargs = vsphere.api('esx').esx(kwargs)
                kwargs = vsphere.api('powercli').powercli(kwargs)

    prLightGray(f'\n{"-"*91}\n')
    prLightGray(f'  Proceedures Complete!!! Closing Environment and Exiting Script.')
    prLightGray(f'\n{"-"*91}\n')
    sys.exit(1)

if __name__ == '__main__':
    main()
