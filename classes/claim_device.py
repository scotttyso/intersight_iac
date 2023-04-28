from classes import device_connector
from classes import isight
from dotmap import DotMap
from time import sleep
import json
import numpy
import re

def claim_targets(kwargs):
    kwargs.device_id.names = []
    kwargs.resource_group.names = []
    return_code = 0

    result = DotMap()
    for i in kwargs.yaml.device_list:
        for e in i.devices:
            device = DotMap(
                device_type   = i.device_type,
                hostname      = e,
                password      = kwargs.password,
                resource_group=i.resource_group,
                username      = kwargs.username
            )
            result[device.hostname] = DotMap(changed=False)
            result[device.hostname].msg = f"  Host : {device.hostname}"
            if not i.get('read_only'): device.read_only = False
            
            # create device connector object based on device type
            if re.search("^(imc|ucs|ucsm|ucspe)$", device.device_type):
                # attempt ucs connection
                dc_obj = device_connector.ucs_device_connector(device)
                # if ucs connection doesnt work and device_type is imc revert to older imc login
                if not dc_obj.logged_in and device.device_type == 'imc':
                    dc_obj = device_connector.imc_device_connector(device)
            elif device.device_type == 'hx':
                dc_obj = device_connector.hx_device_connector(device)
            elif device.device_type == 'imc':
                dc_obj = device_connector.ucs_device_connector(device)
            else:
                result[device.hostname].msg += "  Unknown device_type %s" % device.device_type
                return_code = 1
                print(json.dumps(result[device.hostname]))
                continue
            
            if not dc_obj.logged_in:
                result[device.hostname].msg += "  Login error"
                return_code = 1
                print(json.dumps(result[device.hostname]))
                continue

            ro_json = DotMap(dc_obj.configure_connector())

            if not ro_json.AdminState:
                return_code = 1
                if ro_json.get('ApiError'):
                    result[device.hostname].msg += ro_json.ApiError
                print(json.dumps(result[device.hostname]))
                continue

            # set access mode (ReadOnlyMode True/False) to desired state
            if (ro_json.get('ReadOnlyMode') is not None) and (ro_json.ReadOnlyMode != device.read_only):
                ro_json = dc_obj.configure_access_mode(ro_json)
                if ro_json.get('ApiError'):
                    result[device.hostname].msg += ro_json.ApiError
                    return_code = 1
                    print(json.dumps(result[device.hostname]))
                    continue
                result[device.hostname].changed = True

            # configure proxy settings (changes reported in called function)
            ro_json = dc_obj.configure_proxy(ro_json, result[device.hostname])
            if ro_json.get('ApiError'):
                result[device.hostname].msg += ro_json.ApiError
                return_code = 1
                print(json.dumps(result[device.hostname]))
                continue

            # wait for a connection to establish before checking claim state

            for _ in range(10):
                if ro_json.ConnectionState != 'Connected':
                    sleep(1)
                    ro_json = dc_obj.get_status()

            result[device.hostname].msg += f"  AdminState     : {ro_json.AdminState}"
            result[device.hostname].msg += f"  ConnectionState: {ro_json.ConnectionState}"
            result[device.hostname].msg += f"  Claimed state  : {ro_json.AccountOwnershipState}"

            if ro_json.ConnectionState != 'Connected':
                return_code = 1
                continue
            else:
                print(ro_json.ConnectionState)
                (claim_resp, device_id, claim_code) = dc_obj.get_claim_info(ro_json)
                result[device.hostname].msg += f"  Id : {device_id}"

            if ro_json.AccountOwnershipState != 'Claimed':
                # attempt to claim
                (claim_resp, device_id, claim_code) = dc_obj.get_claim_info(ro_json)
                if claim_resp.get('ApiError'):
                    result[device.hostname].msg += claim_resp['ApiError']
                    return_code = 1
                    continue

                result[device.hostname].msg += f"  Id    : {device_id}"
                result[device.hostname].msg += f"  Token : {claim_code}"

                # Post claim_code and device_id
                kwargs.api_body= {'SecurityToken': claim_code, 'SerialNumber': device_id}
                kwargs.method  = 'post'
                kwargs.qtype   = 'device_claim'
                kwargs.uri     = 'asset/DeviceClaims'
                kwargs         = isight.api(kwargs.qtype).calls(kwargs)
                claim_result   = kwargs.results
                kwargs.serial.names.append(device_id)
                kwargs.resource_group.names.append(device.resource_group)
                result[device.hostname].changed= True
                result[device.hostname].serial = device_id

        kwargs.method  = 'get'
        kwargs.names   = kwargs.device_id.names
        kwargs.qtype   = 'asset_target'
        kwargs.uri     = 'asset/Targets'
        kwargs         = isight.api(kwargs.qtype).calls(kwargs)
        asset_targets  = kwargs.results
        kwargs.method  = 'get'
        kwargs.names   = numpy.unique(numpy.array(kwargs.resource_group.names))
        kwargs.qtype   = 'resource_group'
        kwargs.uri     = 'resource/Groups'
        kwargs         = isight.api(kwargs.qtype).calls(kwargs)
        resource_groups= kwargs.results

        for device in kwargs.device_list:
            indx = [e for e, d in enumerate(asset_targets) if result[device.hostname].serial in d.values()][0]
            print(indx)
            #exit()
            target_moid = asset_targets.results[indx].Moid
            device_registration = asset_targets.results[indx].Parent.Moid
            indx = [e for e, d in enumerate(resource_groups) if device.resource_group in d.values()][0]
            resource_group_moid = resource_groups.results[indx].moid
            device_registrations = re.search(
                r'\(([0-9a-z\'\,]+)\)', resource_groups.results[indx].selectors[0].selector).group(1)
            if not device_registration in device_registrations:
                appended_targets = device_registrations + "," + f"'{device_registration}'"
                kwargs.api_body = {
                    "Selectors":[
                        {
                            "ClassId": "resource.Selector",
                            "ObjectType": "resource.Selector",
                            "Selector": "/api/v1/asset/DeviceRegistrations?$filter=Moid in("f"{appended_targets})"
                        }
                    ]
                }
                kwargs.method= 'patch'
                kwargs.pmoid = resource_group_moid
                kwargs.qtype = 'resource_group'
                kwargs.uri   = 'resource/Groups'
                kwargs       = isight.api(kwargs.qtype).calls(kwargs)
                result[device.hostname]['Resource Group'] = device.resource_group
                result[device.hostname]['Resource Updated'] = True
                result[device.hostname].changed = True
            else:
                result[device.hostname]['Resource Group'] = device.resource_group
                result[device.hostname]['Resource Updated'] = False

            print('')
            print('-' * 60)
            for key, value in result.items():
                for k, v in value.items():
                    if key == 'msg':
                        msg_split = value.split('  ')
                        msg_split.sort()
                        for msg in msg_split:
                            if not msg == '':
                                print(msg)
                    else:
                        print(k, ':', v)
            print('-' * 60)
            print('')


        # logout of any sessions active after exception handling
        if ('dc_obj' in locals() or 'dc_obj' in globals()):
            dc_obj.logout()

    return return_code