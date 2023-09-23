#!/usr/bin/env python3

"""Intersight Device Connector API configuration and device claim via the Intersight API."""

#=============================================================================
# Source Modules
#=============================================================================
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
import os, sys
script_path= os.path.dirname(os.path.realpath(sys.argv[0]))
sys.path.insert(0, f'{script_path}{os.sep}classes')
try:
    from classes import claim_device, ezfunctions, pcolor
    from dotmap import DotMap
    from pathlib import Path
    import argparse, json, logging, os, platform, traceback, yaml
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
        help='The Intersight API key id for HTTP signature scheme.')
    Parser.add_argument(
        '-e', '--endpoint', default='intersight.com',
        help='The Intersight hostname for the API endpoint. The default is intersight.com.')
    Parser.add_argument(
        '-i', '--ignore-tls', action='store_false',
        help='Ignore TLS server-side certificate verification.  Default is False.')
    Parser.add_argument(
        '-k', '--api-key-file', default=os.getenv('intersight_keyfile'),
        help='Name of the file containing The Intersight secret key for the HTTP signature scheme.')
    Parser.add_argument(
        '-u', '--username', default='admin',
        help    ='Name of the file containing The Intersight secret key for the HTTP signature scheme.')
    Parser.add_argument(
        '-y', '--yaml-file',
        help = 'The input YAML File.',
        required= True)
    kwargs = DotMap()
    kwargs.args = Parser.parse_args()
    return kwargs

#=================================================================
# The Main Module
#=================================================================
def main():
    return_code = 0
    #==============================================
    # Configer logger
    #==============================================
    FORMAT = '%(asctime)-15s [%(levelname)s] [%(filename)s:%(lineno)s] %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    logger = logging.getLogger('openapi')

    #==============================================
    # Build kwargs
    #==============================================
    kwargs = cli_arguments()
    if kwargs.args.api_key_file:
        if '~' in kwargs.args.api_key_file:
            kwargs.args.api_key_file = os.path.expanduser(kwargs.args.api_key_file)
    kwargs.deployment_type='claim_devices'
    kwargs.home           = Path.home()
    kwargs.logger         = logger
    kwargs.op_system      = platform.system()
    kwargs.script_path    = os.path.dirname(os.path.realpath(sys.argv[0]))

    #================================================
    # Import Stored Parameters
    #================================================
    script_path= kwargs.script_path
    file       = f'{script_path}{os.sep}variables{os.sep}intersight-openapi-v3-1.0.11-11360.json'
    json_data  = json.load(open(file, 'r'))
    file       = f'{script_path}{os.sep}variables{os.sep}easy_variablesv2.json'
    ez_data    = json.load(open(file, 'r'))

    #================================================
    # Add Data to kwargs
    #================================================
    kwargs.ez_data  = DotMap(ez_data['components']['schemas'])
    kwargs.json_data= DotMap(json_data['components']['schemas'])

    pcolor.LightGray(f'\n{"-"*91}\n')
    pcolor.LightGray(f'  * Begin Device Claims.')
    pcolor.LightGray(f'\n{"-"*91}\n')
    yfile = open(os.path.join(kwargs.args.yaml_file), 'r')
    kwargs.yaml = DotMap(yaml.safe_load(yfile))



    try:
        kwargs.username     = kwargs.args.username
        kwargs.sensitive_var= 'ucs_password'
        kwargs              = ezfunctions.sensitive_var_value(kwargs)
        kwargs.password     = kwargs.var_value
        kwargs = claim_device.claim_targets(kwargs)

    except Exception as err:
        print("Exception:", str(err))
        print('-' * 60)
        traceback.print_exc(file=sys.stdout)
        print('-' * 60)
        if kwargs.return_code:
            sys.exit(kwargs.return_code)
        else: sys.exit(return_code)

    pcolor.LightGray(f'\n{"-"*91}\n')
    pcolor.LightGray(f'  * Completed Device Claims.')
    pcolor.LightGray(f'\n{"-"*91}\n')
    sys.exit(1)
if __name__ == '__main__':
    main()
