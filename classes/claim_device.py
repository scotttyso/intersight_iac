#=============================================================================
# Source Modules
#=============================================================================
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
import sys
try:
    from classes import device_connector, isight, pcolor
    from dotmap import DotMap
    from time import sleep
    import json, numpy, re
except ImportError as e:
    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
    prRed(f" Module {e.name} is required to run this script")
    prRed(f" Install the module using the following: `pip install {e.name}`")
    sys.exit(1)

def claim_targets(kwargs):
    return_code = 0
    result = DotMap()

    resource_groups = []
    for i in kwargs.yaml.device_list: resource_groups.append(i.resource_group)
    names= "', '".join(numpy.unique(numpy.array(resource_groups))).strip("', '")

    kwargs.api_filter= f"Name in ('{names}')"
    kwargs.method    = 'get'
    kwargs.qtype     = 'resource_group'
    kwargs.uri       = 'resource/Groups'
    kwargs           = isight.api(kwargs.qtype).calls(kwargs)
    resource_groups  = kwargs.pmoids
    kwargs.pop('api_filter')

    for i in kwargs.yaml.device_list:
        for e in i.devices:
            device = DotMap(
                device_type   = i.device_type,
                hostname      = e,
                password      = kwargs.password,
                resource_group= i.resource_group,
                script_path   = kwargs.script_path,
                username      = kwargs.username)
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
            #elif device.device_type == 'imc':
            #    dc_obj = device_connector.ucs_device_connector(device)
            else:
                result[device.hostname].msg += "  Unknown device_type %s" % device.device_type
                return_code = 1
                pcolor.Cyan(json.dumps(result[device.hostname]))
                continue
            
            if not dc_obj.logged_in:
                result[device.hostname].msg += "  Login error"
                return_code = 1
                pcolor.Cyan(json.dumps(result[device.hostname]))
                continue

            ro_json = DotMap(dc_obj.configure_connector())

            if not ro_json.AdminState:
                return_code = 1
                if ro_json.get('ApiError'):
                    result[device.hostname].msg += ro_json.ApiError
                pcolor.Cyan(json.dumps(result[device.hostname]))
                continue

            # set access mode (ReadOnlyMode True/False) to desired state
            if (ro_json.get('ReadOnlyMode') is not None) and (ro_json.ReadOnlyMode != device.read_only):
                ro_json = dc_obj.configure_access_mode(ro_json)
                if ro_json.get('ApiError'):
                    result[device.hostname].msg += ro_json.ApiError
                    return_code = 1
                    pcolor.Cyan(json.dumps(result[device.hostname]))
                    continue
                result[device.hostname].changed = True

            # configure proxy settings (changes reported in called function)
            ro_json = dc_obj.configure_proxy(ro_json, result[device.hostname])
            if ro_json.get('ApiError'):
                result[device.hostname].msg += ro_json.ApiError
                return_code = 1
                pcolor.Cyan(json.dumps(result[device.hostname]))
                continue

            # wait for a connection to establish before checking claim state

            for _ in range(10):
                if ro_json.ConnectionState != 'Connected': sleep(1); ro_json = dc_obj.get_status()

            result[device.hostname].msg += f"  AdminState     : {ro_json.AdminState}"
            result[device.hostname].msg += f"  ConnectionState: {ro_json.ConnectionState}"
            result[device.hostname].msg += f"  Claimed state  : {ro_json.AccountOwnershipState}"

            if ro_json.ConnectionState != 'Connected': return_code = 1; continue
            else:
                pcolor.Cyan(ro_json.ConnectionState)
                (claim_resp, device_id, claim_code) = dc_obj.get_claim_info(ro_json)
                result[device.hostname].msg += f"  Id : {device_id}"

            if ro_json.AccountOwnershipState != 'Claimed':
                # attempt to claim
                (claim_resp, device_id, claim_code) = dc_obj.get_claim_info(ro_json)
                if claim_resp.get('ApiError'):
                    result[device.hostname].msg += claim_resp['ApiError']
                    return_code = 1; continue

                result[device.hostname].msg += f"  Id    : {device_id}"
                result[device.hostname].msg += f"  Token : {claim_code}"

                # Post claim_code and device_id
                kwargs.api_body= {'SecurityToken': claim_code, 'SerialNumber': device_id}
                kwargs.method  = 'post'
                kwargs.qtype   = 'device_claim'
                kwargs.uri     = 'asset/DeviceClaims'
                kwargs         = isight.api(kwargs.qtype).calls(kwargs)
                reg_moid       = kwargs.results.Moid
                result[device.hostname].reg_moid = reg_moid
                result[device.hostname].changed= True
                result[device.hostname].serial = device_id
            else:
                kwargs.method    = 'get'
                kwargs.api_filter= f'contains(Serial,{device_id})'
                kwargs.qtype     = 'device_registration'
                kwargs.uri       = 'asset/DeviceRegistrations'
                kwargs           = isight.api(kwargs.qtype).calls(kwargs)
                reg_moid         = kwargs.results[0].Moid
                result[device.hostname].reg_moid = reg_moid
                result[device.hostname].changed= False
                result[device.hostname].serial = device_id

        if re.search(r'\(([0-9a-z\'\,]+)\)', resource_groups[i.resource_group].selectors[0].Selector):
            device_registrations= re.search(
                r'\(([0-9a-z\'\,]+)\)', resource_groups[i.resource_group].selectors[0].Selector).group(1)
        else: device_registrations= ''
        result[s]['Resource Group'] = i.resource_group
        for s in i.devices:
            # 5f4bc8d86f72612d3035521a
            if not result[s].reg_moid in device_registrations:
                if len(device_registrations) > 0:
                    appended_targets = device_registrations + "," + f"'{result[s].reg_moid}'"
                else: appended_targets = f"'{result[s].reg_moid}'"
                result[s]['Resource Updated'] = True
            else: result[s]['Resource Updated'] = False

        kwargs.api_body = { "Selectors":[{
            "ClassId": "resource.Selector",
            "ObjectType": "resource.Selector",
            "Selector": "/api/v1/asset/DeviceRegistrations?$filter=Moid in("f"{appended_targets})"
        }] }
        kwargs.method= 'patch'
        kwargs.pmoid = resource_groups[i.resource_group].moid
        kwargs.qtype = 'resource_group'
        kwargs.uri   = 'resource/Groups'
        kwargs       = isight.api(kwargs.qtype).calls(kwargs)

    pcolor.Cyan(f'\n{"-" * 60}')
    for key, value in result.items():
        for k, v in value.items():
            if key == 'msg':
                msg_split = value.split('  ')
                msg_split.sort()
                for msg in msg_split:
                    if not msg == '': pcolor.Cyan(msg)
            else: pcolor.Cyan(k, ':', v)
    pcolor.Cyan(f'\n{"-" * 60}')

    # logout of any sessions active after exception handling
    if ('dc_obj' in locals() or 'dc_obj' in globals()): dc_obj.logout()
    kwargs.result = result
    kwargs.return_code= return_code
    return kwargs
