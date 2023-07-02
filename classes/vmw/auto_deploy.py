#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys

sys.path.insert(0, './classes')
import classes.ezfunctions
import classes.vmware

# Global Variables
excel_workbook = None
Parser = argparse.ArgumentParser(description='VMware Host Configuration')
workspace_dict = {}

# Class Regular Expressions
VMware_regex = re.compile('^(globals|server|vmks|vnics|vcenter)$')

def process_servers(args, wb, pydict):
    # Evaluate Server Worksheet
    class_ref = 'classes.vmware.Servers'
    func_regex = VMware_regex
    ws = wb['Hosts']
    pydict = read_worksheet(args, class_ref, func_regex, pydict, wb, ws)
    return pydict

def read_worksheet(args, class_ref, func_regex, pydict, wb, ws):
    rows = ws.max_row
    func_list = classes.ezfunctions.findKeys(ws, func_regex)
    class_init = '%s(ws)' % (class_ref)
    classes.ezfunctions.stdout_log(ws, None)
    for func in func_list:
        count = classes.ezfunctions.countKeys(ws, func)
        var_dict = classes.ezfunctions.findVars(ws, func, rows, count)
        for pos in var_dict:
            row_num = var_dict[pos]['row']
            del var_dict[pos]['row']
            for x in list(var_dict[pos].keys()):
                if var_dict[pos][x] == '':
                    del var_dict[pos][x]
            classes.ezfunctions.stdout_log(ws, row_num)
            pydict = eval(f"{class_init}.{func}(args, pydict, row_num, wb, ws, **var_dict[pos])")
    return pydict

            

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
        default='~/Downloads/SecretKey.txt',
        help='Name of file containing The Intersight secret key for the HTTP signature scheme'
    )
    Parser.add_argument('--api-key-v3', action='store_true',
                        help='Use New API client (v3) key'
    )
    Parser.add_argument('-i', '--ignore-tls', action='store_true',
                        help='Ignore TLS server-side certificate verification'
    )
    Parser.add_argument('-u', '--url', default='https://intersight.com',
                        help='The Intersight root URL for the API endpoint. The default is https://intersight.com'
    )
    Parser.add_argument('-w', '--worksheet', default='Settings.xlsx',
                        help='The Worksheet Containing the Server Configuration Data.'
    )
    args = Parser.parse_args()
    args.api_key_id = classes.ezfunctions.api_key(args)
    args.api_key_file = classes.ezfunctions.api_secret(args)

    if os.path.isfile(args.worksheet):
        excel_workbook = args.worksheet
    else:
        print('\nWorkbook not Found.  Please enter a valid /path/filename for the source you will be using.')
        while True:
            print('Please enter a valid /path/filename for the source you will be using.')
            excel_workbook = input('/Path/Filename: ')
            if os.path.isfile(excel_workbook):
                print(f'\n-----------------------------------------------------------------------------\n')
                print(f'   {excel_workbook} exists.  Will Now Check for API Variables...')
                print(f'\n-----------------------------------------------------------------------------\n')
                break
            else:
                print('\nWorkbook not Found.  Please enter a valid /path/filename for the source you will be using.')

    # Load Workbook
    wb = classes.ezfunctions.read_in(excel_workbook)

    # Run Proceedures for Worksheets in the Workbook
    pydict = {
        'global_settings':{},
        'servers':{},
        'vcenters':{},
        'vmk_dict':{},
        'vnic_dict':{}
    }
    pydict = process_servers(args, wb, pydict)
    # pretty_data = json.dumps(serverList.json(), indent=4)
    # for i in serverList:
    pydict.pop('global_settings')
    pydict.pop('vmk_dict')
    pydict.pop('vnic_dict')
    jsonDump = json.dumps(pydict, indent=4)
    open('settings.json', 'w').write(jsonDump)
    print(jsonDump)


if __name__ == '__main__':
    main()
