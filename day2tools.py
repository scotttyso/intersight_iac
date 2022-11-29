#!/usr/bin/env python3

from copy import deepcopy
import argparse
import classes.day2tools
import classes.ezfunctions
import json
import io
import os
import platform
import sys

# Global Variables
excel_workbook = None
Parser = argparse.ArgumentParser(description='Intersight Day 2 Tools')

def main():
    description = None
    if description is not None:
        Parser.description = description
    Parser.add_argument(
        '-a', '--api-key-id',
        default=os.getenv('apikey'),
        help='The Intersight API client key id for HTTP signature scheme'
    )
    Parser.add_argument(
        '-s', '--api-key-file',
        default=os.getenv('secretkeyfile'),
        help='Name of file containing The Intersight secret key for the HTTP signature scheme'
    )
    Parser.add_argument(
        '--api-key-v3', action='store_true',
        help='Use New API client (v3) key'
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
        '-u', '--url', default='https://intersight.com',
        help='The Intersight root URL for the API endpoint. The default is https://intersight.com'
    )
    Parser.add_argument(
        '-w', '--worksheet', default='Settings.xlsx',
        help='The Worksheet Containing the Server Configuration Data.'
    )
    args = Parser.parse_args()
    args.api_key_id = classes.ezfunctions.api_key(args)

    # Determine the Operating System
    opSystem = platform.system()
    kwargs = {}
    kwargs['args'] = args
    kwargs['script_path'] = os.path.dirname(os.path.realpath(sys.argv[0]))
    if opSystem == 'Windows': kwargs['path_sep'] = '\\'
    else: kwargs['path_sep'] = '/'
    if not args.json_file == None:
        if not os.path.isfile(args.json_file):
            print(f'\n-------------------------------------------------------------------------------------------\n')
            print(f'  !!ERROR!!')
            print(f'  Did not find the file {args.json_file}.')
            print(f'  Please Validate that you have specified the correct file and path.')
            print(f'\n-------------------------------------------------------------------------------------------\n')
            exit()
        else:
            json_file = args.json_file
            if 'hcl_inventory' in args.process:
                json_open = open(json_file, 'r', encoding='utf-16')
            else:
                json_open = open(json_file, 'r')
            kwargs['json_data'] = json.load(json_open)
        if args.process == 'hcl_inventory':
            json_data = []
            for item in kwargs['json_data']:
                if 'Cisco' in item['Hostname']['Manufacturer']:
                    json_data.append(item)
            kwargs['json_data'] = deepcopy(json_data)

    # Verify the SecretKey
    if not args.api_key_file == None:
        args.api_key_file = classes.ezfunctions.api_secret(args)
    else:
        if opSystem == 'Windows': args.api_key_file = '$HOME\Downloads\SecretKey.txt'
        else: args.api_key_file = '~/Downloads/SecretKey.txt'
        args.api_key_file = classes.ezfunctions.api_secret(args)

    if args.process == 'server_inventory':
        type = 'server_inventory'
        classes.day2tools.intersight_api(type).server_inventory(**kwargs)
    elif args.process == 'add_policies':
        type = 'add_policies'
        classes.day2tools.intersight_api(type).add_policies(**kwargs)
    elif args.process == 'add_vlan':
        type = 'add_vlan'
        classes.day2tools.intersight_api(type).add_vlan(**kwargs)
    elif args.process == 'hcl_inventory':
        type = 'hcl_inventory'
        classes.day2tools.intersight_api('hcl_inventory').hcl_inventory(**kwargs)
    elif args.process == 'hcl_status':
        type = 'hcl_status'
        classes.day2tools.intersight_api(type).hcl_status(**kwargs)

if __name__ == '__main__':
    main()
