#!/usr/bin/env python3

from copy import deepcopy
from pathlib import Path
import argparse
import codecs
import json
import io
import os
import platform
import sys

sys.path.insert(0, './classes')
from classes import day2tools
from classes import ezfunctions
# Global Variables
excel_workbook = None
Parser = argparse.ArgumentParser(description='Intersight Day 2 Tools')

def main():
    description = None
    if description is not None:
        Parser.description = description
    Parser.add_argument(
        '-a', '--api-key-id', default=os.getenv('intersight_apikey'),
        help='The Intersight API client key id for HTTP signature scheme'
    )
    Parser.add_argument(
        '-e', '--endpoint', default=os.getenv('intersight_endpoint'),
        help='The Intersight hostname for the API endpoint. The default is intersight.com'
    )
    Parser.add_argument(
        '-f', '--full-inventory', action='store_true',
        help='For Spreadsheet Pull the Full Server Inventory'
    )
    Parser.add_argument(
        '-i', '--ignore-tls', action='store_true',
        help='Ignore TLS server-side certificate verification'
    )
    Parser.add_argument(
        '-j',
        '--json-file',
        default=None,
        help='Source JSON File for VLAN Additional Process.'
    )
    Parser.add_argument(
        '-k', '--api-key-file', default=os.getenv('intersight_keyfile'),
        help='Name of file containing The Intersight secret key for the HTTP signature scheme'
    )
    Parser.add_argument(
        '-p', '--process',
        default='server_inventory',
        help='Which Process to run with the Script.  Options are:'\
            '1. add_policies '\
            '2. add_vlan '\
            '3. server_inventory '\
            '4. hcl_inventory '\
            '5. hcl_status.'
    )
    Parser.add_argument(
        '-v', '--api-key-v3', action='store_true',
        help='Flag for API Key Version 3.'
    )
    Parser.add_argument(
        '-wb', '--workbook', default='Settings.xlsx',
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
    jsonFile = f'{script_path}{path_sep}variables{path_sep}intersight-openapi-v3-1.0.11-11360.json'
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
    kwargs['args'] = args
    kwargs['ezData']      = ezData['components']['schemas']
    kwargs['home']        = Path.home()
    kwargs['jsonData']    = jsonData['components']['schemas']
    kwargs['opSystem']    = platform.system()
    kwargs['path_sep']    = path_sep
    kwargs['script_path'] = script_path
    kwargs = ezfunctions.intersight_config(**kwargs)
    kwargs['args'].url = 'https://%s' % (kwargs['args'].endpoint)
    args   = kwargs['args']

    if not args.json_file == None:
        if not os.path.isfile(args.json_file):
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  !!ERROR!!')
            print(f'  Did not find the file {args.json_file}.')
            print(f'  Please Validate that you have specified the correct file and path.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            exit()
        else:
            def try_utf8(json_file):
                try:
                    f = codecs.open(json_file, encoding='utf-8', errors='strict')
                    for line in f: pass
                    print("Valid utf-8")
                    return 'Good'
                except UnicodeDecodeError:
                    print("invalid utf-8")
                    return None

            json_file = args.json_file
            if 'hcl_inventory' in args.process:
                udata = try_utf8(json_file)
                if udata is None: json_open = open(json_file, 'r', encoding='utf-16')
                else: json_open = open(json_file, 'r')
            else:
                json_open = open(json_file, 'r')
            kwargs['json_data'] = json.load(json_open)
        if args.process == 'hcl_inventory':
            json_data = []
            for item in kwargs['json_data']:
                if 'Cisco' in item['Hostname']['Manufacturer']:
                    json_data.append(item)
            kwargs['json_data'] = deepcopy(json_data)

    if args.process == 'server_inventory':
        type = 'server_inventory'
        day2tools.intersight_api(type).server_inventory(**kwargs)
    elif args.process == 'add_policies':
        type = 'add_policies'
        day2tools.intersight_api(type).add_policies(**kwargs)
    elif args.process == 'add_vlan':
        type = 'add_vlan'
        day2tools.intersight_api(type).add_vlan(**kwargs)
    elif args.process == 'hcl_inventory':
        type = 'hcl_inventory'
        day2tools.intersight_api('hcl_inventory').hcl_inventory(**kwargs)
    elif args.process == 'hcl_status':
        type = 'hcl_status'
        day2tools.intersight_api(type).hcl_status(**kwargs)

if __name__ == '__main__':
    main()
