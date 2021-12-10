#!/usr/bin/env python3
"""Intersight Device Connector API configuration and device claim via the Intersight API."""
# from datetime import datetime, timedelta
# from helpers import format_time, print_results_to_table
# from pprint import pformat
from time import sleep
# from typing import Text, Type

# import argparse
import credentials
import device_connector
import json
import intersight
import logging
import traceback
import os.path
import re
import sys
import stdiomask
import validators

from intersight.api import asset_api
from intersight.api import resource_api


FORMAT = '%(asctime)-15s [%(levelname)s] [%(filename)s:%(lineno)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('openapi')

def get_api_client(api_key_id, api_secret_file, endpoint="https://intersight.com"):
    with open(api_secret_file, 'r') as f:
        api_key = f.read()

    if re.search('BEGIN RSA PRIVATE KEY', api_key):
        # API Key v2 format
        signing_algorithm = intersight.signing.ALGORITHM_RSASSA_PKCS1v15
        signing_scheme = intersight.signing.SCHEME_RSA_SHA256
        hash_algorithm = intersight.signing.HASH_SHA256

    elif re.search('BEGIN EC PRIVATE KEY', api_key):
        # API Key v3 format
        signing_algorithm = intersight.signing.ALGORITHM_ECDSA_MODE_DETERMINISTIC_RFC6979
        signing_scheme = intersight.signing.SCHEME_HS2019
        hash_algorithm = intersight.signing.HASH_SHA256

    configuration = intersight.Configuration(
        host=endpoint,
        signing_info=intersight.signing.HttpSigningConfiguration(
            key_id=api_key_id,
            private_key_path=api_secret_file,
            signing_scheme=signing_scheme,
            signing_algorithm=signing_algorithm,
            hash_algorithm=hash_algorithm,
            signed_headers=[
                intersight.signing.HEADER_REQUEST_TARGET,
                intersight.signing.HEADER_HOST,
                intersight.signing.HEADER_DATE,
                intersight.signing.HEADER_DIGEST,
            ]
        )
    )

    return intersight.ApiClient(configuration)

if __name__ == "__main__":
    return_code = 0

    client,devices_list = credentials.config_credentials()

    try:
        valid = False
        while valid == False:
            if os.environ.get('username') is None:
                username = input('Enter the username to authenticate to the devices: ')
            else:
                username = os.environ.get('username')

            if not username == '':
                valid = True
            else:
                print('Invalid Username.  Please Re-Enter the username.')

        valid = False
        while valid == False:
            if os.environ.get('password') is None:
                password = stdiomask.getpass(prompt='Enter the password to authenticate to the devices: ')
            else:
                password = os.environ.get('password')

            if not password == '':
                valid = True
            else:
                print('Invalid Password.  Please Re-Enter the password.')

        for device in devices_list:
            result = dict(changed=False)
            result['msg'] = "  Host : %s" % device['hostname']
            # default access mode to allow control (Read-only False) and set to a boolean value if a string
            if not device.get('read_only'):
                device['read_only'] = False
            else:
                if device['read_only'] == 'True' or device['read_only'] == 'true':
                    device['read_only'] = True
                elif device['read_only'] == 'False' or device['read_only'] == 'false':
                    device['read_only'] = False
            
            device['username'] = username
            device['password'] = password

            # create device connector object based on device type
            if device['device_type'] == 'ucs' or device['device_type'] == 'ucsm' or device['device_type'] == 'ucspe':
                dc_obj = device_connector.UcsDeviceConnector(device)
            elif device['device_type'] == 'hx':
                dc_obj = device_connector.HxDeviceConnector(device)
            elif device['device_type'] == 'imc':
                # attempt ucs connection and if that doesn't login revert to older imc login
                dc_obj = device_connector.UcsDeviceConnector(device)
                if not dc_obj.logged_in:
                    dc_obj = device_connector.ImcDeviceConnector(device)
            else:
                result['msg'] += "  Unknown device_type %s" % device['device_type']
                return_code = 1
                print(json.dumps(result))
                continue
            
            if not dc_obj.logged_in:
                result['msg'] += "  Login error"
                return_code = 1
                print(json.dumps(result))
                continue

            ro_json = dc_obj.configure_connector()
            if not ro_json['AdminState']:
                return_code = 1
                if ro_json.get('ApiError'):
                    result['msg'] += ro_json['ApiError']
                print(json.dumps(result))
                continue

            # set access mode (ReadOnlyMode True/False) to desired state
            if (ro_json.get('ReadOnlyMode') is not None) and (ro_json['ReadOnlyMode'] != device['read_only']):
                ro_json = dc_obj.configure_access_mode(ro_json)
                if ro_json.get('ApiError'):
                    result['msg'] += ro_json['ApiError']
                    return_code = 1
                    print(json.dumps(result))
                    continue
                result['changed'] = True

            # configure proxy settings (changes reported in called function)
            ro_json = dc_obj.configure_proxy(ro_json, result)
            if ro_json.get('ApiError'):
                result['msg'] += ro_json['ApiError']
                return_code = 1
                print(json.dumps(result))
                continue

            # wait for a connection to establish before checking claim state

            for _ in range(10):
                if ro_json['ConnectionState'] != 'Connected':
                    sleep(1)
                    ro_json = dc_obj.get_status()

            result['msg'] += "  AdminState : %s" % ro_json['AdminState']
            result['msg'] += "  ConnectionState : %s" % ro_json['ConnectionState']
            result['msg'] += "  Claimed state : %s" % ro_json['AccountOwnershipState']

            if ro_json['ConnectionState'] != 'Connected':
                return_code = 1
                continue
            else:
                print(ro_json['ConnectionState'])
                (claim_resp, device_id, claim_code) = dc_obj.get_claim_info(ro_json)
                result['msg'] += "  Id : %s" % device_id

            if ro_json['AccountOwnershipState'] != 'Claimed':
                # attempt to claim
                (claim_resp, device_id, claim_code) = dc_obj.get_claim_info(ro_json)
                if claim_resp.get('ApiError'):
                    result['msg'] += claim_resp['ApiError']
                    return_code = 1
                    continue

                result['msg'] += "  Id : %s" % device_id
                result['msg'] += "  Token : %s" % claim_code

                # Create Intersight API instance and post ID/claim code
                # ----------------------
                api_handle = asset_api.AssetApi(client)

                # setting claim_code and device_id
                claim_body = {'SecurityToken': claim_code, 'SerialNumber': device_id}
                claim_result = api_handle.create_asset_device_claim(claim_body)
                result['changed'] = True

            api_handle = asset_api.AssetApi(client)
            query_filter = f"TargetId eq '{device_id}'"
            kwargs = dict(filter=query_filter)
            target_list = api_handle.get_asset_target_list(**kwargs)
            if target_list.results:
                target_moid = target_list.results[0].moid
                device_registration = target_list.results[0].parent.moid
                api_handle = resource_api.ResourceApi(client)
                query_filter = f"Name eq '{device['resource_group']}'"
                kwargs = dict(filter=query_filter)
                resource_group = api_handle.get_resource_group_list(**kwargs)
                if resource_group.results:
                    resource_group_moid = resource_group.results[0].moid
                    device_registrations = re.search(r'\(([0-9a-z\'\,]+)\)', resource_group.results[0].selectors[0].selector).group(1)
                    if not device_registration in device_registrations:
                        appended_targets = device_registrations + "," + f"'{device_registration}'"
                        resource_group = {
                            "Selectors":[
                                {
                                    "ClassId": "resource.Selector",
                                    "ObjectType": "resource.Selector",
                                    "Selector": "/api/v1/asset/DeviceRegistrations?$filter=Moid in("f"{appended_targets})"
                                }
                            ]
                        }
                        resource_group_patch = api_handle.patch_resource_group(resource_group_moid, resource_group)
                        result['Resource Group'] = device['resource_group']
                        result['Resource Updated'] = True
                        result['changed'] = True
                    else:
                        result['Resource Group'] = device['resource_group']
                        result['Resource Updated'] = False

            print('')
            print('-' * 60)
            for key, value in result.items():
                if key == 'msg':
                    msg_split = value.split('  ')
                    msg_split.sort()
                    for msg in msg_split:
                        if not msg == '':
                            print(msg)
                else:
                    print(key, ':', value)
            print('-' * 60)
            print('')

            # logout of any open sessions
            dc_obj.logout()

    except Exception as err:
        print("Exception:", str(err))
        import traceback
        print('-' * 60)
        traceback.print_exc(file=sys.stdout)
        print('-' * 60)
        sys.exit(1)

    finally:
        # logout of any sessions active after exception handling
        if ('dc_obj' in locals() or 'dc_obj' in globals()):
            dc_obj.logout()

    sys.exit(return_code)