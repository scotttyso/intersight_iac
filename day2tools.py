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
        default=os.getenv('TF_VAR_secfile'),
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
        help='Which Process to run with the Script.  Options are 1. add_vlan 2. server_inventory.'
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
    args.api_key_file = api_secret(args)

    kwargs = {}
    kwargs['args'] = args
    if args.process == 'server_inventory':
        type = 'server_inventory'
        class_day2tools.intersight(type).server_inventory(**kwargs)
    if args.process == 'add_vlan':
        type = 'add_vlan'
        class_day2tools.intersight(type).add_vlan(**kwargs)

if __name__ == '__main__':
    main()
