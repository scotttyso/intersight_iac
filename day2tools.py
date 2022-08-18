#!/usr/bin/env python3

from easy_functions import api_key, api_secret
import argparse
import class_day2tools
import os

# Global Variables
excel_workbook = None
Parser = argparse.ArgumentParser(description='Intersight Day 2 Tools')

def main():
    description = None
    if description is not None:
        Parser.description = description
    Parser.add_argument(
        '-a', '--api-key-id',
        default=os.getenv('TF_VAR_apikey'),
        help='The Intersight API client key id for HTTP signature scheme'
    )
    Parser.add_argument(
        '-s', '--api-key-file',
        default=os.getenv('TF_VAR_secret_file'),
        help='Name of file containing The Intersight secret key for the HTTP signature scheme'
    )
    Parser.add_argument(
        '--api-key-v3', action='store_true',
        help='Use New API client (v3) key'
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
        help='Which Process to run with the Script.  Options are 1. add_policies 2. add_vlan 3. server_inventory 4. hcl_status.'
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
    args.api_key_id = api_key(args)
    if not args.api_key_file == None:
        args.api_key_file = api_secret(args)
    else:
        args.api_key_file = '~/Downloads/SecretKey.txt'
        args.api_key_file = api_secret(args)

    kwargs = {}
    kwargs['args'] = args
    if args.process == 'server_inventory':
        type = 'server_inventory'
        class_day2tools.intersight_api(type).server_inventory(**kwargs)
    elif args.process == 'add_policies':
        type = 'add_policies'
        class_day2tools.intersight_api(type).add_policies(**kwargs)
    elif args.process == 'add_vlan':
        type = 'add_vlan'
        class_day2tools.intersight_api(type).add_vlan(**kwargs)
    elif args.process == 'hcl_status':
        type = 'hcl_status'
        class_day2tools.intersight_api(type).hcl_status(**kwargs)

if __name__ == '__main__':
    main()
