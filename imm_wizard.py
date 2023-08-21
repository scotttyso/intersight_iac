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
                            2. flashstack
                            3. flexpod
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
#try:
import sys
sys.path.insert(0, './classes')
from classes import ci
from classes import ezfunctions as ezfunctions
from classes import isight
from classes import netapp
from classes import network
from classes import vsphere
from copy import deepcopy
from dotmap import DotMap
from pathlib import Path
from pprint import pprint
from json_ref_dict import materialize, RefDict
import argparse
import json
import logging
import os
import platform
import re
import socket
import yaml
#except ImportError as e:
#    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
#    prRed(f" Module {e.name} is required to run this script")
#    prRed(f" Install the module using the following: `pip install {e.name}`")
#    sys.exit(1)



class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

#=================================================================
# Parse Arguments
#=================================================================
def cli_arguments():
    Parser = argparse.ArgumentParser(description='Intersight Converged Infrastructure Deployment Module')
    Parser.add_argument(
        '-a', '--intersight-api-key-id', default=os.getenv('intersight_api_key_id'),
        help='The Intersight API key id for HTTP signature scheme.'
    )
    Parser.add_argument(
        '-d', '--dir',
        default = 'Intersight',
        help = 'The Directory to use for the Creation of the Terraform Files.'
    )
    Parser.add_argument(
        '-f', '--intersight-fqdn', default='intersight.com',
        help='The Intersight hostname for the API endpoint. The default is intersight.com.'
    )
    Parser.add_argument(
        '-i', '--ignore-tls', action='store_false',
        help='Ignore TLS server-side certificate verification.  Default is False.'
    )
    Parser.add_argument(
        '-ilp', '--local-user-password-1',
        help='Intersight Managed Mode Local User Password 1.'
    )
    Parser.add_argument(
        '-ilp2', '--local-user-password-2',
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
        '-k', '--intersight_secret_key', default='~/Downloads/SecretKey.txt',
        help='Name of the file containing The Intersight secret key or contents of the secret key in environment.'
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
        #required=True
    )
    Parser.add_argument(
        '-t', '--deployment-type',
        default ='flexpod',
        help    ='Infrastructure Deployment Type. Options Are:'\
            '1. azure_hci '
            '2. flashstack '\
            '3. flexpod '\
            '4. imm_domain ',
        #required=True
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
    ##==============================================
    ## Configure logger
    ##==============================================
    #script_name = (sys.argv[0].split(os.sep)[-1]).split('.')[0]
    #dest_dir = f"{Path.home()}{os.sep}Logs"
    #dest_file = script_name + '.log'
    #if not os.path.exists(dest_dir): os.mkdir(dest_dir)
    #if not os.path.exists(os.path.join(dest_dir, dest_file)): 
    #    create_file = f'type nul >> {os.path.join(dest_dir, dest_file)}'
    #    os.system(create_file)
    #
    #FORMAT = '%(asctime)-15s [%(levelname)s] [%(filename)s:%(lineno)s] %(message)s'
    #logging.basicConfig(
    #    filename=f"{dest_dir}{os.sep}{script_name}.log",
    #    filemode='a',
    #    format=FORMAT,
    #    level=logging.DEBUG
    #)
    #logger = logging.getLogger('openapi')
    #
    ##==============================================
    ## Build kwargs
    ##==============================================
    kwargs   = cli_arguments()
    #
    ##==============================================
    ## Determine the Script Path
    ##==============================================
    kwargs.script_path= os.path.dirname(os.path.realpath(sys.argv[0]))
    script_path= kwargs.script_path
    #kwargs.args.dir = os.path.join(Path.home(), kwargs.args.yaml_file.split('/')[0])
    #
    #args_dict = vars(kwargs.args)
    #for k,v in args_dict.items():
    #    if type(v) == str:
    #        if v: os.environ[k] = v
    #
    #
    #if kwargs.args.intersight_secret_key:
    #    if '~' in kwargs.args.intersight_secret_key:
    #        kwargs.args.intersight_secret_key = os.path.expanduser(kwargs.args.intersight_secret_key)
    #
    #kwargs.deployment_type= kwargs.args.deployment_type
    #kwargs.home           = Path.home()
    #kwargs.logger         = logger
    #kwargs.op_system      = platform.system()
    #kwargs.imm_dict.orgs  = DotMap()
    #
    ##==============================================
    ## Add Sensitive Variables to Environment
    ##==============================================
    #sensitive_list = [
    #    'local_user_password_1',
    #    'local_user_password_2',
    #    'snmp_auth_password_1',
    #    'snmp_privacy_password_1',
    #    'netapp_password',
    #    'nexus_password',
    #    'vmware_esxi_password',
    #    'vmware_vcenter_password'
    #]
    #for e in sensitive_list:
    #    if vars(kwargs.args)[e]:
    #        os.environ[e] = vars(kwargs.args)[e]
    #
    ##==============================================
    ## Send Notification Message
    ##==============================================
    #prLightGray(f'\n{"-"*91}\n')
    #prLightGray(f'  Begin Deployment for {kwargs.deployment_type}.')
    #prLightGray(f'  * Deployment Step is {kwargs.args.deployment_step}.')
    #prLightGray(f'\n{"-"*91}\n')
    ##================================================
    ## Import Stored Parameters
    ##================================================
    schema = RefDict(f'{script_path}{os.sep}variables{os.sep}easy-imm.json')
    data = materialize(schema)
    print(json.dumps(data['components']['schemas']['port'], indent = 4 ))
    #pprint(data['components']['schemas']['port'])
    exit()

if __name__ == '__main__':
    main()
