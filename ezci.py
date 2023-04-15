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
from collections import OrderedDict
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
from classes import ezfunctions
from classes import isdk
from classes import isdkp
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
        '-s', '--deployment_step',
        default ='flexpod',
        required=True,
        help    ='The steps in the proceedure to run. Options Are:'\
            '1. initial'
            '2. server'\
            '3. operating_system'\
            '4. management'
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
    args = Parser.parse_args()
    return args

#=================================================================
# The Main Module
#=================================================================
def main():
    # Determine the Operating System
    opSystem = platform.system()
    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    if opSystem == 'Windows': path_sep = '\\'
    else: path_sep = '/'
    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    #================================================
    # Import Stored Parameters
    #================================================
    file    = f'{script_path}{path_sep}variables{path_sep}intersight-openapi-v3-1.0.11-11360.json'
    jsonData= json.load(open(file, 'r'))
    file    = f'{script_path}{path_sep}variables{path_sep}easy_variables.json'
    ezData  = json.load(open(file, 'r'))

    #==============================================
    # Build kwargs
    #==============================================
    args   = cli_arguments()
    kwargs = {}
    kwargs['args']           = args
    kwargs['deployment_type']= 'converged'
    kwargs['ezData']         = ezData['components']['schemas']
    kwargs['home']           = Path.home()
    kwargs['immDict']        = {'orgs':{}}
    kwargs['jsonData']       = jsonData['components']['schemas']
    kwargs['opSystem']       = platform.system()
    kwargs['path_sep']       = path_sep
    kwargs['script_path']    = script_path

    #==============================================
    # Get Intersight Configuration
    # - apikey
    # - endpoint
    # - keyfile
    #==============================================
    kwargs  = ezfunctions.intersight_config(**kwargs)
    args.url= 'https://%s' % (args.endpoint)
    kwargs['args']= args
    #==============================================
    # Check Folder Naming for Illegal Characters
    #==============================================
    destdirCheck = False
    while destdirCheck == False:
        splitDir = args.dir.split(path_sep)
        splitDir = [i for i in splitDir if i]
        for folder in splitDir:
            if not re.search(r'^[\w\-\.\:\/\\]+$', folder):
                print(folder)
                print(f'\n-------------------------------------------------------------------------------------------\n')
                print(f'  !!ERROR!!')
                print(f'  The Directory structure can only contain the following characters:')
                print(f'  letters(a-z, A-Z), numbers(0-9), hyphen(-), period(.), colon(:), or and underscore(_).')
                print(f'  It can be a short path or a fully qualified path. {folder} failed this check.')
                print(f'\n-------------------------------------------------------------------------------------------\n')
                sys.exit(1)
        destdirCheck = True

    #==============================================
    # Process the YAML input File
    #==============================================
    if (args.yaml):
        yfile = open(os.path.join(args.yaml), 'r')
        kwargs['immDict']['wizard'] = yaml.safe_load(yfile)

    #==============================================
    # Build Deployment Library
    #==============================================
    pargs = DotMap()
    pargs.nope = False
    kwargs, pargs = isdk.api('organization').organizations(pargs, **kwargs)
    kwargs, pargs = ci.wizard('dns_ntp').dns_ntp(pargs, **kwargs)
    kwargs, pargs = ci.wizard('imm').imm(pargs, **kwargs)
    kwargs, pargs = ci.wizard('vlans').vlans(pargs, **kwargs)
    if re.search('(netapp|pure)', args.deployment_type):
        kwargs, pargs = eval(f"ci.wizard(args.deployment_type).{args.deployment_type}(pargs, **kwargs)")

    #=================================================================
    # When Deployment Step is initial - Deploy NXOS|Storage|Domain
    #=================================================================
    if args.deployment_step == 'initial':
        if pargs.nope == True:
            #==============================================
            # Configure Switches if configure Set to True
            #==============================================
            if kwargs['immDict']['wizard'].get('nxos'):
                network_config = DotMap(deepcopy(kwargs['immDict']['wizard']['nxos'][0]))
                network_types = ['network', 'ooband']
                for network_type in network_types:
                    config_count = 0
                    for i in network_config.switches:
                        if i.configure == True and i.switch_type == network_type: config_count += 1
                    if config_count == 2:
                        kwargs, pargs = network.nxos('nxos').config(network_config, network_type, pargs, **kwargs)

        #==============================================
        # Configure Storage Appliances
        #==============================================
        if args.deployment_type == 'netapp':
            if pargs.nope == False:
                kwargs, pargs = ci.wizard('build').build_netapp(pargs, **kwargs)
            else:
                pargs.netapp.wwpns.a    = [{'fcp-lif-01-1a':'20:0e:00:a0:98:aa:1c:8d'}, {'fcp-lif-02-1a':'20:0f:00:a0:98:aa:1c:8d'}]
                pargs.netapp.wwpns.b    = [{'fcp-lif-01-1c':'20:10:00:a0:98:aa:1c:8d'}, {'fcp-lif-02-1c':'20:11:00:a0:98:aa:1c:8d'}]
                pargs.netapp.iscsi.iqn  = 'iqn.1992-08.com.netapp:sn.57c603ffcc2811ed9ce100a098aa1c8d:vs.6'
                pargs.netapp.nvme.nqn   = 'nqn.1992-08.com.netapp:sn.57c603ffcc2811ed9ce100a098aa1c8d:discovery'

        #==============================================
        # Configure and Deploy Domain
        #==============================================
        if re.search('(imm_domain|netapp|pure)', args.deployment_type):
            kwargs, pargs = ci.wizard('build').build_imm_domain(pargs, **kwargs)
            kwargs = eval(f"isdkp.api_profiles('domain').profiles(pargs, **kwargs)")

    print(json.dumps(kwargs['immDict']['orgs'], indent=4))
    exit()

    #==============================================
    # Create YAML Files
    #==============================================
    #print(json.dumps(kwargs['immDict']['wizard'], indent=4))
    orgs   = list(kwargs['immDict']['orgs'].keys())
    ezfunctions.create_yaml(orgs, **kwargs)
    #==============================================
    # Loop Through the Orgs
    #==============================================
    kwargs['isdk_deployed'] = {}
    for org in orgs:
        #print(json.dumps(kwargs['immDict']['orgs'][org]['netapp']['volume'], indent=4))
        #==============================================
        # Pools
        #==============================================
        if pargs.nope == True:
            cisdk = 'isdkp.api_pools'
            if kwargs['immDict']['orgs'][org].get('pools'):
                for pool_type in kwargs['immDict']['orgs'][org]['pools']:
                    if kwargs['immDict']['orgs'][org]['pools'].get(pool_type):
                        kwargs = eval(f"{cisdk}(pool_type).pools(pargs, **kwargs)")
        #==============================================
        # Policies
        #==============================================
        if pargs.nope == True:
            policies = {}
            policies_in_order = OrderedDict(sorted(kwargs['immDict']['orgs'][org]['policies'].items()))
            for k, v in policies_in_order.items(): policies.update({k:v})
            istatic = {'iscsi_static_target':policies['iscsi_static_target']}
            policies = dict(istatic, **policies)
            cisdk = 'isdkp.api_policies'
            if kwargs['immDict']['orgs'][org].get('policies'):
                for ptype in policies:
                    if kwargs['immDict']['orgs'][org]['policies'].get(ptype):
                        if re.search('^[a-z]', ptype):
                            dpolicies = eval(f"{cisdk}(ptype).policies(pargs, **kwargs)")
                            kwargs['isdk_deployed'].update({ptype:dpolicies})
        #==============================================
        # Profiles
        #==============================================
        if pargs.nope == True:
            cisdk = 'isdkp.api_profiles'
            ptype = 'templates'
            if kwargs['immDict']['orgs'][org].get(ptype):
                if kwargs['immDict']['orgs'][org][ptype].get('server'):
                    kwargs = eval(f"{cisdk}(ptype).profiles(pargs, **kwargs)")
            ptype = 'profiles'
            if kwargs['immDict']['orgs'][org].get(ptype):
                if kwargs['immDict']['orgs'][org][ptype].get('domain'):
                    kwargs = eval(f"{cisdk}('domain').profiles(pargs, **kwargs)")
                if kwargs['immDict']['orgs'][org][ptype].get('chassis'):
                    kwargs = eval(f"{cisdk}('chassis').profiles(pargs, **kwargs)")
                if kwargs['immDict']['orgs'][org][ptype].get('server'):
                    kwargs = eval(f"{cisdk}('server').profiles(pargs, **kwargs)")

        #==============================================
        # Server Identities
        #==============================================
        kwargs, pargs = ci.wizard('wizard').server_identities(pargs, **kwargs)
        #==============================================
        # Upgrade Firmware
        #==============================================
        if pargs.nope == True:
            kwargs, pargs = ci.fw_os('firmware').firmware(pargs, **kwargs)
        #==============================================
        # Install OS
        #==============================================
        if pargs.nope == True:
            kwargs, pargs = ci.fw_os('os_install').os_install(pargs, **kwargs)
        #==============================================
        # Configure ESX Hosts and vCenter
        #==============================================
        if pargs.nope == True:
            kwargs, pargs = vsphere.api('esx').esx(pargs, **kwargs)
        kwargs, pargs = vsphere.api('vcenter').vcenter(pargs, **kwargs)
        #kwargs, pargs = vsphere.api('datastore').datastore(pargs, **kwargs)

    print(f'\n-----------------------------------------------------------------------------\n')
    print(f'  Proceedures Complete!!! Closing Environment and Exiting Script.')
    print(f'\n-----------------------------------------------------------------------------\n')
    sys.exit(1)

if __name__ == '__main__':
    main()
