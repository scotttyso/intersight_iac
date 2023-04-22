#!/usr/bin/env python3
"""Converged Infrastructure Deployment - 
This Script is built to Deploy Converged Infrastructure from an Excel Spreadsheet.
It uses argparse to take in the following CLI arguments:
    d or dir:        Base Directory to use for creation of the HCL Configuration Files
    w or workbook:   Name of Excel Workbook file for the Data Source
"""

#======================================================
# Source Modules
#======================================================
from copy import deepcopy
from dotmap import DotMap
from pathlib import Path
import argparse
import json
import os
import platform
import re
import sys
import yaml

sys.path.insert(0, './classes')
from classes import ci
from classes import ezfunctionsv2 as ezfunctions
from classes import isight
from classes import netapp
from classes import network
from classes import vsphere

class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

def cli_arguments():
    Parser = argparse.ArgumentParser(description='Intersight Converged Infrastructure Deployment Module')
    Parser.add_argument(
        '-a', '--api-key-id', default=os.getenv('intersight_apikey'),
        help='The Intersight API client key id for HTTP signature scheme'
    )
    Parser.add_argument(
        '-d', '--dir',
        default = 'Intersight',
        help = 'The Directory to use for the Creation of the Terraform Files.'
    )
    Parser.add_argument(
        '-e', '--endpoint', default=os.getenv('intersight_endpoint'),
        help='The Intersight hostname for the API endpoint. The default is intersight.com'
    )
    Parser.add_argument(
        '-i', '--ignore-tls', action='store_true',
        help='Ignore TLS server-side certificate verification'
    )
    Parser.add_argument(
        '-k', '--api-key-file', default=os.getenv('intersight_keyfile'),
        help='Name of file containing The Intersight secret key for the HTTP signature scheme'
    )
    Parser.add_argument(
        '-l', '--load-config', action='store_false',
        help='Skip Wizard and Just Load Configuration Files.'
    )
    Parser.add_argument(
        '-s', '--deployment_step',
        default ='flexpod',
        required=True,
        help    ='The steps in the proceedure to run. Options Are:'\
            '1. initial'
            '2. servers'\
            '3. luns'\
            '4. operating_system'\
            '5. management'
    )
    Parser.add_argument(
        '-t', '--deployment_type',
        default ='flexpod',
        required=True,
        help    ='Infrastructure Deployment Type. Options Are:'\
            '1. azure_hci'
            '2. netapp'\
            '3. pure'\
            '4. imm_domain'
    )
    Parser.add_argument(
        '-v', '--api-key-v3', action='store_true',
        help='Flag for API Key Version 3.'
    )
    Parser.add_argument(
        '-wb', '--workbook',
        help = 'The source Workbook.'
    )
    Parser.add_argument(
        '-y', '--yaml',
        help = 'The source YAML File.'
    )
    kwargs = DotMap()
    kwargs.args = Parser.parse_args()
    return kwargs

#=================================================================
# The Main Module
#=================================================================
def main():
    #==============================================
    # Build kwargs
    #==============================================
    kwargs   = cli_arguments()
    if '~' in kwargs.args.api_key_file:
        kwargs.args.api_key_file = os.path.expanduser(kwargs.args.api_key_file)
    kwargs.deployment_type= 'converged'
    kwargs.home           = Path.home()
    kwargs.opSystem   = platform.system()
    kwargs.immDict.orgs = DotMap()

    #==============================================
    # Determine the Operating System Parameters
    #==============================================
    kwargs.script_path= os.path.dirname(os.path.realpath(sys.argv[0]))
    if kwargs.opSystem == 'Windows': kwargs.path_sep = '\\'
    else: kwargs.path_sep = '/'

    #================================================
    # Import Stored Parameters
    #================================================
    path_sep   = kwargs.path_sep
    script_path= kwargs.script_path
    file       = f'{script_path}{path_sep}variables{path_sep}intersight-openapi-v3-1.0.11-11360.json'
    jsonData   = json.load(open(file, 'r'))
    file       = f'{script_path}{path_sep}variables{path_sep}easy_variablesv2.json'
    ezData     = json.load(open(file, 'r'))

    #================================================
    # Add Data to kwargs
    #================================================
    kwargs.ezData  = DotMap(ezData['components']['schemas'])
    kwargs.jsonData= DotMap(jsonData['components']['schemas'])

    #==============================================
    # Get Intersight Configuration
    # - apikey
    # - endpoint
    # - keyfile
    #==============================================
    kwargs = ezfunctions.intersight_config(kwargs)
    kwargs.args.url= 'https://%s' % (kwargs.args.endpoint)
    #==============================================
    # Check Folder Naming for Illegal Characters
    #==============================================
    destdirCheck = False
    while destdirCheck == False:
        splitDir = kwargs.args.dir.split(path_sep)
        splitDir = [i for i in splitDir if i]
        for folder in splitDir:
            if not re.search(r'^[\w\-\.\:\/\\]+$', folder):
                print(folder)
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  !! ERROR !!')
                print(f'  The Directory structure can only contain the following characters:')
                print(f'  letters(a-z, A-Z), numbers(0-9), hyphen(-), period(.), colon(:), or and underscore(_).')
                print(f'  It can be a short path or a fully qualified path. {folder} failed this check.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                sys.exit(1)
        destdirCheck = True

    #==============================================
    # Load Previous Configurations
    #==============================================
    if kwargs.args.load_config == False:
        kwargs = DotMap(ezfunctions.load_previous_configurations(kwargs))

    #==============================================
    # Process the YAML input File
    #==============================================
    if (kwargs.args.yaml):
        yfile = open(os.path.join(kwargs.args.yaml), 'r')
        kwargs.immDict.wizard = DotMap(yaml.safe_load(yfile))

    #==============================================
    # Build Deployment Library
    #==============================================
    kwargs.nope = False
    #kwargs = isight.api('organization').organizations(kwargs)
    kwargs.org_moids = DotMap({'default': {'moid': '5ddea1e16972652d32b6493a'}, 'Asgard': {'moid': '5f6509326972652d32fa70a8'}, 'Wakanda': {'moid': '60aeca786972652d32ee5e46'}, 'Production': {'moid': '61b9e6516972652d32099398'}, 'terratest': {'moid': '633ed7606972652d32ecc0a6'}, 'Panther': {'moid': '636a5a086972652d32b1740e'}, 'RICH': {'moid': '639ffbbe6972652d3243d65f'}})
    kwargs = ci.wizard('dns_ntp').dns_ntp(kwargs)
    kwargs = ci.wizard('imm').imm(kwargs)
    kwargs = ci.wizard('vlans').vlans(kwargs)
    if re.search('(netapp|pure)', kwargs.args.deployment_type):
        kwargs = eval(f"ci.wizard(kwargs.args.deployment_type).{kwargs.args.deployment_type}(kwargs)")

    #=================================================================
    # When Deployment Step is initial - Deploy NXOS|Storage|Domain
    #=================================================================
    if kwargs.args.deployment_step == 'initial':
        #==============================================
        # Configure Switches if configure Set to True
        #==============================================
        #if kwargs.immDict.wizard.get('nxos'):
        #    network_config = DotMap(deepcopy(kwargs.immDict.wizard.nxos[0]))
        #    network_types = ['network', 'ooband']
        #    for network_type in network_types:
        #        config_count = 0
        #        for i in network_config.switches:
        #            if i.configure == True and i.switch_type == network_type: config_count += 1
        #        if config_count == 2:
        #            kwargs = network.nxos('nxos').config(network_config, network_type, kwargs)

        #==============================================
        # Configure Storage Appliances
        #==============================================
        #if kwargs.args.deployment_type == 'netapp':
        #    kwargs = ci.wizard('build').build_netapp(kwargs)

        #==============================================
        # Configure and Deploy Domain
        #==============================================
        if re.search('(imm_domain|netapp|pure)', kwargs.args.deployment_type):
            kwargs = ci.wizard('build').build_imm_domain(kwargs)

        #==============================================
        # Create YAML Files
        #==============================================
        ezfunctions.create_yaml(orgs, kwargs)

        orgs = list(kwargs.immDict.orgs.keys())
        for org in orgs:
            #==============================================
            # Policies
            #==============================================
            api = 'isight.policies_class'
            if kwargs.immDict.orgs[org].get('policies'):
                print(kwargs.policy_type)
                for ptype in kwargs.policy_list:
                    print(ptype)
                    if re.search('^[l-z]', ptype):
                        if kwargs.immDict.orgs[org]['policies'].get(ptype):
                            dpolicies = eval(f"{api}(ptype).policies(kwargs)")
                            kwargs.deployed.update({ptype:dpolicies})

            #==============================================
            # Deploy Domain
            #==============================================
            if re.search('(imm_domain|netapp|pure)', kwargs.args.deployment_type):
                kwargs = eval(f"isight.profiles_class('domain').profiles(kwargs)")


    #=================================================================
    # Deploy Chassis/Server Pools/Policies/Profiles
    #=================================================================
    elif kwargs.args.deployment_step == 'server':
        kwargs.deployed = {}
        #==============================================
        # Configure and Deploy Server Profiles
        #==============================================
        kwargs = ci.wizard('build').build_imm_servers(kwargs)

        #==============================================
        # Create YAML Files
        #==============================================
        orgs   = list(kwargs.immDict.orgs.keys())
        ezfunctions.create_yaml(orgs, kwargs)

        for org in orgs:
            #==============================================
            # Pools
            #==============================================
            api = 'isight.pools_class'
            if kwargs.immDict.orgs[org].get('pools'):
                for pool_type in kwargs.immDict.orgs[org]['pools']:
                    kwargs = eval(f"{api}(pool_type).pools(kwargs)")

            #==============================================
            # Policies
            #==============================================
            api = 'isight.policies_class'
            if kwargs.immDict.orgs[org].get('policies'):
                for ptype in kwargs.policy_list:
                    if kwargs.immDict.orgs[org]['policies'].get(ptype):
                        dpolicies = eval(f"{api}(ptype).policies(kwargs)")
                        kwargs.deployed.update({ptype:dpolicies})

            #==============================================
            # Profiles
            #==============================================
            api = 'isight.profiles_class'
            ptype = 'templates'
            if kwargs.immDict.orgs[org].get(ptype):
                if kwargs.immDict.orgs[org][ptype].get('server'):
                    kwargs = eval(f"{api}(ptype).profiles(kwargs)")
            ptype = 'profiles'
            if kwargs.immDict.orgs[org].get(ptype):
                profile_list = ['chassis', 'server']
                for i in profile_list:
                    if kwargs.immDict.orgs[org][ptype].get(i):
                        kwargs = eval(f"{api}(i).profiles(kwargs)")

    #=================================================================
    # Configure Luns/igroups/mapping - Collect Server Identities
    #=================================================================
    elif kwargs.args.deployment_step == 'luns':
        #==============================================
        # Loop Through the Orgs
        #==============================================
        orgs   = list(kwargs.immDict.orgs.keys())
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
        orgs   = list(kwargs.immDict.orgs.keys())
        for org in orgs:
            #==============================================
            # Upgrade Firmware
            #==============================================
            #if kwargs.nope == True:
            #    kwargs = ci.fw_os('firmware').firmware(kwargs)
            #==============================================
            # Install OS
            #==============================================
            kwargs = ci.wizard('os_install').os_install(kwargs)

    if kwargs.deployment_step == 'management':
        for org in orgs:
            #==============================================
            # Configure ESX Hosts and vCenter
            #==============================================
            if kwargs.nope == True:
                kwargs = vsphere.api('esx').esx(kwargs)
            kwargs = vsphere.api('vcenter').vcenter(kwargs)
            #kwargs = vsphere.api('datastore').datastore(kwargs)

    print(f'\n-----------------------------------------------------------------------------\n')
    print(f'  Proceedures Complete!!! Closing Environment and Exiting Script.')
    print(f'\n-----------------------------------------------------------------------------\n')
    sys.exit(1)

if __name__ == '__main__':
    main()
