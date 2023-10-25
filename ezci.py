#!/usr/bin/env python3
""" Infrastructure Deployment - 
This Script is built to Deploy Infrastructure from a YAML Configuration File.
The Script uses argparse to take in the following CLI arguments:
    a or intersight-api-key-id: The Intersight API key id for HTTP signature scheme.
    d or dir:                   Base Directory to use for creation of the YAML Configuration Files.
    dl or debug-level:          The Debug Level to Run for Script Output
    e or intersight-fqdn:       The Intersight hostname for the API endpoint. The default is intersight.com.
    i or ignore-tls:            Ignore TLS server-side certificate verification.  Default is False.
    k or intersight-secret-key: Name of the file containing The Intersight secret key for the HTTP signature scheme.
    s or deployment-step:       The steps in the proceedure to run. Options Are: 
                                  1. initial
                                  2. servers
                                  3. luns
                                  4. operating_system
                                  5. os_configuration
    t or deployment-type:       Infrastructure Deployment Type. Options Are: 
                                  1. azurestack
                                  2. flashstack
                                  3. flexpod
                                  4. imm_domain
                                  5. imm_standalone
    v or api-key-v3:            Flag for API Key Version 3.
    y or yaml-file:             The input YAML File.
"""
#=============================================================================
# Source Modules
#=============================================================================
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
import os, sys
script_path= os.path.dirname(os.path.realpath(sys.argv[0]))
sys.path.insert(0, f'{script_path}{os.sep}classes')
try:
    from classes import ci, ezfunctions, isight, network, pcolor, vsphere
    from copy import deepcopy
    from dotmap import DotMap
    from json_ref_dict import materialize, RefDict
    from pathlib import Path
    import argparse, json, logging, os, platform, re, yaml
except ImportError as e:
    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
    prRed(f" Module {e.name} is required to run this script")
    prRed(f" Install the module using the following: `pip install {e.name}`")
    sys.exit(1)
#=================================================================
# Function: Parse Arguments
#=================================================================
def cli_arguments():
    Parser = argparse.ArgumentParser(description='Intersight Converged Infrastructure Deployment Module')
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
        help='The Intersight hostname for the API endpoint. The default is intersight.com.')
    Parser.add_argument(
        '-i', '--ignore-tls', action='store_false',
        help='Ignore TLS server-side certificate verification.  Default is False.')
    Parser.add_argument( '-ilp', '--local-user-password-1',   help='Intersight Managed Mode Local User Password 1.' )
    Parser.add_argument( '-ilp2','--local-user-password-2',   help='Intersight Managed Mode Local User Password 2.' )
    Parser.add_argument( '-imm', '--imm-transition-password', help='IMM Transition Tool Password.' )
    Parser.add_argument( '-isa', '--snmp-auth-password-1',    help='Intersight Managed Mode SNMP Auth Password.' )
    Parser.add_argument( '-isp', '--snmp-privacy-password-1', help='Intersight Managed Mode SNMP Privilege Password.' )
    Parser.add_argument(
        '-k', '--intersight-secret-key', default='~/Downloads/SecretKey.txt',
        help='Name of the file containing The Intersight secret key or contents of the secret key in environment.')
    Parser.add_argument( '-np',  '--netapp-password',  help='NetApp Login Password.' )
    Parser.add_argument( '-nsa', '--netapp-snmp-auth', help='NetApp SNMP Auth Password.' )
    Parser.add_argument( '-nsp', '--netapp-snmp-priv', help='NetApp SNMP Privilege Password.' )
    Parser.add_argument( '-nxp', '--nexus-password',   help='Nexus Login Password.' )
    Parser.add_argument( '-p', '--pure-storage-password',   help='Pure Storage Login Password.' )
    Parser.add_argument( '-psa', '--pure-storage-snmp-auth', help='Pure Storage SNMP Auth Password.' )
    Parser.add_argument( '-psp', '--pure-storage-snmp-priv', help='Pure Storage SNMP Privilege Password.' )
    Parser.add_argument(
        '-s', '--deployment-step', default ='initial', required=True,
        help ='The steps in the proceedure to run. Options Are: '\
            '1. initial '
            '2. servers '\
            '3. luns '\
            '4. operating_system '\
            '5. os_configuration ')
    Parser.add_argument(
        '-t', '--deployment-type', default ='imm_domain', required=True,
        help ='Infrastructure Deployment Type. Options Are: '\
            '1. azurestack '
            '2. flashstack '\
            '3. flexpod '\
            '3. imm_domain '\
            '4. imm_standalone ')
    Parser.add_argument( '-v', '--api-key-v3', action='store_true', help='Flag for API Key Version 3.' )
    Parser.add_argument( '-vep', '--vmware-esxi-password',          help='VMware ESXi Root Login Password.' )
    Parser.add_argument( '-vvp', '--vmware-vcenter-password',       help='VMware vCenter Admin Login Password.' )
    Parser.add_argument( '-wap', '--windows-admin-password',        help='Windows Administrator Login Password.' )
    Parser.add_argument( '-wdp', '--windows-domain-password',       help='Windows Domain Registration Login Password.' )
    Parser.add_argument( '-y', '--yaml-file',                       help = 'The input YAML File.' )
    kwargs = DotMap()
    kwargs.args = Parser.parse_args()
    return kwargs

#=================================================================
# The Main Module
#=================================================================
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
    #==============================================
    # Determine the Script Path
    #==============================================
    kwargs.script_path= os.path.dirname(os.path.realpath(sys.argv[0]))
    script_path       = kwargs.script_path
    kwargs.args.dir   = os.path.join(Path.home(), kwargs.args.yaml_file.split('/')[0])
    args_dict = vars(kwargs.args)
    for k,v in args_dict.items():
        if type(v) == str:
            if v: os.environ[k] = v
    if kwargs.args.intersight_secret_key:
        if '~' in kwargs.args.intersight_secret_key:
            kwargs.args.intersight_secret_key = os.path.expanduser(kwargs.args.intersight_secret_key)
    kwargs.deployment_type= kwargs.args.deployment_type
    kwargs.home           = Path.home()
    kwargs.logger         = logger
    kwargs.op_system      = platform.system()
    kwargs.imm_dict.orgs  = DotMap()
    #==============================================
    # Send Notification Message
    #==============================================
    pcolor.Green(f'\n{"-"*91}\n\n  Begin Deployment for {kwargs.deployment_type}.')
    pcolor.Green(f'  * Deployment Step is {kwargs.args.deployment_step}.\n\n{"-"*91}\n')
    #================================================
    # Import Stored Parameters and Add to kwargs
    #================================================
    ezdata = materialize(RefDict(f'{script_path}{os.sep}variables{os.sep}easy-imm.json', 'r', encoding="utf8"))
    kwargs.ez_tags = {'Key':'ezci','Value':ezdata['info']['version']}
    kwargs.ezdata  = DotMap(ezdata['components']['schemas'])
    #==============================================
    # Add Sensitive Variables to Environment
    #==============================================
    sensitive_list = [
        'local_user_password_1', 'local_user_password_2', 'snmp_auth_password_1', 'snmp_privacy_password_1',
        'netapp_password', 'nexus_password', 'pure_storage_password', 'vmware_esxi_password', 'vmware_vcenter_password',
        'windows_admin_password', 'windows_domain_password']
    for e in sensitive_list:
        if vars(kwargs.args)[e]: os.environ[e] = vars(kwargs.args)[e]
    #==============================================
    # Get Intersight Configuration
    # - intersight_api_key_id
    # - intersight_fqdn
    # - intersight_secret_key
    #==============================================
    kwargs         = ezfunctions.intersight_config(kwargs)
    kwargs.args.url= 'https://%s' % (kwargs.args.intersight_fqdn)
    #==============================================
    # Check Folder Path Naming for Bad Characters
    #==============================================
    for folder in kwargs.args.dir.split(os.sep):
        if folder == '': fcount = 0
        elif not re.search(r'^[\w\-\.\:\/\\]+$', folder):
            prRed(f'\n{"-"*91}\n\n  !! ERROR !!\n  The Directory structure can only contain the following characters:')
            prRed(f'  letters(a-z, A-Z), numbers(0-9), hyphen(-), period(.), colon(:), or and underscore(_).')
            prRed(f'  It can be a short path or a fully qualified path. {folder} failed this check.\n\n{"-"*91}\n')
            sys.exit(1)
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
    if re.search('(flashstack|flexpod)', kwargs.args.deployment_type):
        if kwargs.args.deployment_type == 'flexpod':  run_type = 'netapp'
        elif kwargs.args.deployment_type == 'flashstack': run_type = 'pure_storage'
        kwargs = eval(f"ci.wizard(run_type).{run_type}(kwargs)")

    #=================================================================
    # When Deployment Step is initial - Deploy NXOS|Storage|Domain
    #=================================================================
    if 'flashstack' in kwargs.args.deployment_type: kwargs.protocols = ['fcp', 'iscsi', 'nvme-roce']
    elif 'flexpod' in kwargs.args.deployment_type: kwargs.protocols = ['fcp', 'iscsi', 'nfs', 'nvme-tcp']

    if kwargs.args.deployment_step == 'initial':
        #==============================================
        # Configure Switches if configure Set to True
        #==============================================
        if kwargs.imm_dict.wizard.nxos_config == True:
            if kwargs.imm_dict.wizard.get('nxos'):
                network_config = DotMap(deepcopy(kwargs.imm_dict.wizard.nxos[0]))
                network_types = ['network', 'ooband']
                for network_type in network_types:
                    config_count = 0
                    for i in network_config.switches:
                        if i.switch_type == network_type: config_count += 1
                    if config_count == 2: kwargs = network.nxos('nxos').config(network_config, network_type, kwargs)
        #==============================================
        # Configure Storage Appliances
        #==============================================
        if kwargs.args.deployment_type == 'flashstack': kwargs = ci.wizard('build').build_pure_storage(kwargs)
        #elif kwargs.args.deployment_type == 'flexpod':  kwargs = ci.wizard('build').build_netapp(kwargs)
        #==============================================
        # Configure Domain
        #==============================================
        if re.search('(fl(ashstack|expod)|imm_domain)', kwargs.args.deployment_type):
            kwargs = ci.wizard('build').build_imm_domain(kwargs)
        #==============================================
        # Create YAML Files
        #==============================================
        orgs = list(kwargs.imm_dict.orgs.keys())
        if len(kwargs.imm_dict.orgs) > 0: ezfunctions.create_yaml(orgs, kwargs)
        for org in orgs:
            kwargs.org = org
            #==============================================
            # Policies
            #==============================================
            if kwargs.imm_dict.orgs[org].get('policies'):
                for ptype in kwargs.policy_list:
                    if kwargs.imm_dict.orgs[org]['policies'].get(ptype):
                        kwargs = eval(f"isight.imm(ptype).policies(kwargs)")
        for org in orgs:
            kwargs.org = org
            #==============================================
            # Deploy Domain
            #==============================================
            if re.search('(flashstack|flexpod|imm_domain)', kwargs.args.deployment_type):
                kwargs = eval(f"isight.imm('domain').profiles(kwargs)")
    #=================================================================
    # Deploy Chassis/Server Pools/Policies/Profiles
    #=================================================================
    elif kwargs.args.deployment_step == 'servers':
        kwargs.deployed = {}
        #==============================================
        # Configure IMM Pools/Policies/Profiles
        #==============================================
        kwargs = ci.wizard('build').build_imm_servers(kwargs)
        orgs   = list(kwargs.imm_dict.orgs.keys())
        #==============================================
        # Create YAML Files
        #==============================================
        ezfunctions.create_yaml(orgs, kwargs)
        #==============================================
        # Pools
        #==============================================
        for org in orgs:
            if kwargs.imm_dict.orgs[org].get('pools'):
                for ptype in kwargs.imm_dict.orgs[org]['pools']:
                    kwargs = eval(f"isight.imm(ptype).pools(kwargs)")
        #==============================================
        # Policies
        #==============================================
        for org in orgs:
            if kwargs.imm_dict.orgs[org].get('policies'):
                for ptype in kwargs.policy_list:
                    kwargs = eval(f"isight.imm(ptype).policies(kwargs)")
        for org in orgs:
            kwargs.isight[org].policy = DotMap(dict(sorted(kwargs.isight[org].policy.toDict().items())))
        #print(json.dumps(kwargs.isight, indent=4))
        #==============================================
        # Profiles and Server Identities
        #==============================================
        for org in orgs:
            if kwargs.imm_dict.orgs[org].get('templates'):
                if kwargs.imm_dict.orgs[org]['templates'].get('server'): kwargs = eval(f"isight.imm('server_template').profiles(kwargs)")
            if kwargs.imm_dict.orgs[org].get('profiles'):
                profile_list = ['chassis', 'server']
                for i in profile_list:
                    if kwargs.imm_dict.orgs[org]['profiles'].get(i): kwargs = eval(f"isight.imm(i).profiles(kwargs)")
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
                for k, v in i.items(): kwargs.server_profiles[i.name][k] = v
            #==============================================
            # Install OS
            #==============================================
            kwargs = ci.wizard('os_install').os_install(kwargs)
        #==============================================
        # Create YAML Files
        #==============================================
        ezfunctions.create_yaml(orgs, kwargs)
    #=================================================================
    # Configure the Operating System
    #=================================================================
    elif kwargs.args.deployment_step == 'os_configuration':
        #==============================================
        # Loop Through the Orgs
        #==============================================
        orgs = list(kwargs.imm_dict.orgs.keys())
        for org in orgs:
            #=====================================================
            # merge os_configuration with server_profiles
            #=====================================================
            for i in kwargs.imm_dict.orgs[kwargs.org].wizard.os_configuration:
                for k, v in i.items(): kwargs.server_profiles[i.name][k] = v
            kwargs.repo_server = kwargs.imm_dict.orgs[kwargs.org].wizard.repository_server
            #==============================================
            # Configure Virtualization Environment
            #==============================================
            vmware = False
            for i in kwargs.virtualization:
                if i.type == 'vmware': vmware = True
            if vmware == True:
                kwargs = vsphere.api('esx').esx(kwargs)
                kwargs = vsphere.api('powercli').powercli(kwargs)
    pcolor.Green(f'\n{"-"*91}\n\n  !!! Proceedures Complete !!!\n  Closing Environment and Exiting Script...\n\n{"-"*91}\n')
    sys.exit(0)

if __name__ == '__main__':
    main()
