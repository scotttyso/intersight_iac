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

sys.path.insert(0, './classes')
from classes import ci
from classes import ezfunctions
from classes import isdk
from classes import isdkp
from classes import netapp
#======================================================
# Regular Expressions to Control wich rows in the
# Worksheet should be processed.
#======================================================
reg1 = 'credentials|dhcp_dns_ntp|imm_(domain|fc|policy|profiles)|interfaces'
reg2 = 'mgmt|nxos|ontap(_(lic|mgmt))?|ranges|vlans'
wb_regex = re.compile(f'^({reg1}|{reg2})$')

#=================================================================
# Function to Read the Wizard Worksheet
#=================================================================
def process_wizard(**kwargs):
    kwargs['class_init'] = 'wizard'
    kwargs['class_folder'] = 'wizard'
    kwargs['func_regex'] = wb_regex
    kwargs['ws'] = 'wizard'
    kwargs = read_worksheet(**kwargs)
    return kwargs


#=================================================================
# Function to process the Worksheets and Create Terraform Files
#=================================================================
def read_worksheet(**kwargs):
    wb = kwargs['wb']
    ws = wb[kwargs['ws']]
    rows = ws.max_row
    func_list = ezfunctions.findKeys(ws, kwargs['func_regex'])
    ezfunctions.stdout_log(ws, 'begin')
    for func in func_list:
        count = ezfunctions.countKeys(ws, func)
        var_dict = ezfunctions.findVars(ws, func, rows, count)
        for pos in var_dict:
            row_num = var_dict[pos]['row']
            del var_dict[pos]['row']
            for x in list(var_dict[pos].keys()):
                if var_dict[pos][x] == '':
                    del var_dict[pos][x]
            ezfunctions.stdout_log(ws, row_num)
            kwargs['var_dict'] = var_dict[pos]
            kwargs['row_num'] = row_num
            kwargs['ws'] = ws
            class_id = f"ci.{kwargs['class_init']}"
            easyDict = eval(f"{class_id}(func).settings(**kwargs)")
    
    ezfunctions.stdout_log(ws, 'end')
    # Return the easyDict
    return easyDict

#=================================================================
# The Main Module
#=================================================================
def main():
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
        '-v', '--api-key-v3', action='store_true',
        help='Flag for API Key Version 3.'
    )
    Parser.add_argument(
        '-wb', '--workbook',
        help = 'The source Workbook.'
    )
    args = Parser.parse_args()

    # Determine the Operating System
    opSystem = platform.system()
    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    if opSystem == 'Windows': path_sep = '\\'
    else: path_sep = '/'
    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    #================================================
    # Import Stored Parameters
    #================================================
    jsonFile = f'{script_path}{path_sep}variables{path_sep}intersight-openapi-v3-1.0.11-9235.json'
    jsonOpen = open(jsonFile, 'r')
    jsonData = json.load(jsonOpen)
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
    kwargs['ezData']      = ezData['components']['schemas']
    kwargs['home']        = Path.home()
    kwargs['immDict']     = {'orgs':{}}
    kwargs['jsonData']    = jsonData['components']['schemas']
    kwargs['opSystem']    = platform.system()
    kwargs['path_sep']    = path_sep
    kwargs['script_path'] = script_path
    #==============================================
    # Get Intersight Configuration
    # - apikey
    # - endpoint
    # - keyfile
    #==============================================
    kwargs = ezfunctions.intersight_config(**kwargs)
    kwargs['args'].url = 'https://%s' % (kwargs['args'].endpoint)
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
    # Import the Workbook
    #==============================================
    if os.path.isfile(args.workbook): excel_workbook = args.workbook
    else:
        print(f'\n-------------------------------------------------------------------------------------------\n')
        print(f'\nWorkbook not Found.  Please enter a valid {path_sep}path{path_sep}filename for the source workbook.')
        print(f'\n-------------------------------------------------------------------------------------------\n')
        while True:
            print(f'Please enter a valid {path_sep}path{path_sep}filename for the source you will be using.')
            excel_workbook = input('/Path/Filename: ')
            if os.path.isfile(excel_workbook):
                print(f'\n-----------------------------------------------------------------------------\n')
                print(f'   {excel_workbook} exists.  Will Now begin collecting variables...')
                print(f'\n-----------------------------------------------------------------------------\n')
                break
            print(f'\n!!!Workbook not Found!!!\n'\
                '.  Please enter a valid {path_sep}path{path_sep}filename for the source you will be using.')
    kwargs = ezfunctions.read_in(excel_workbook, **kwargs)
    #==============================================
    # Process the Wizard Worksheet
    #==============================================
    kwargs = process_wizard(**kwargs)
    #==============================================
    # Process the Wizard Worksheet
    #==============================================
    pargs = DotMap()
    #orgs   = list(kwargs['immDict']['orgs'].keys())
    kwargs, pargs = isdk.api('organization').organizations(pargs, **kwargs)
    kwargs, pargs = ci.wizard('dns_ntp').dns_ntp(pargs, **kwargs)
    kwargs, pargs = ci.wizard('vlans').vlans(pargs, **kwargs)
    kwargs, pargs = ci.wizard('netapp').netapp(pargs, **kwargs)
    kwargs, pargs = ci.wizard('imm').imm(pargs, **kwargs)
    kwargs, pargs = ci.wizard('build').build(pargs, **kwargs)
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
        #==============================================
        # NetApp Part 1
        #==============================================
        #==============================================
        # Pools
        #==============================================
        nope = False
        if nope == True:
            cisdk = 'isdkp.api_pools'
            if kwargs['immDict']['orgs'][org].get('pools'):
                for pool_type in kwargs['immDict']['orgs'][org]['pools']:
                    if kwargs['immDict']['orgs'][org]['pools'].get(pool_type):
                        kwargs = eval(f"{cisdk}(pool_type).pools(pargs, **kwargs)")
        #==============================================
        # Policies
        #==============================================
        if nope == True:
            policies = {}
            policies_in_order = OrderedDict(sorted(kwargs['immDict']['orgs'][org]['policies'].items()))
            for k, v in policies_in_order.items(): policies.update({k:v})
            istatic = {'iscsi_static_target':policies['iscsi_static_target']}
            policies = dict(istatic, **policies)
            cisdk = 'isdkp.api_policies'
            if kwargs['immDict']['orgs'][org].get('policies'):
                for ptype in policies:
                    if kwargs['immDict']['orgs'][org]['policies'].get(ptype):
                        if re.search('^vlan', ptype):
                            dpolicies = eval(f"{cisdk}(ptype).policies(pargs, **kwargs)")
                            kwargs['isdk_deployed'].update({ptype:dpolicies})
        #==============================================
        # Profiles
        #==============================================
        if nope == True:
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
        # Profiles
        #==============================================
        kwargs, pargs = ci.wizard('wizard').server_identities(pargs, **kwargs)

    print(f'\n-----------------------------------------------------------------------------\n')
    print(f'  Proceedures Complete!!! Closing Environment and Exiting Script.')
    print(f'\n-----------------------------------------------------------------------------\n')
    sys.exit(1)

if __name__ == '__main__':
    main()
