from isdk_pools import isdk_pools
from intersight.api import bulk_api
from intersight.api import chassis_api
from intersight.api import compute_api
from intersight.api import equipment_api
from intersight.api import fabric_api
from intersight.api import networkconfig_api
from intersight.api import ntp_api
from intersight.api import server_api
from intersight.api import snmp_api
from intersight.exceptions import ApiException
import credentials
import json
import re
import sys
import time
import urllib3
import validating
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global options for debugging
print_payload = False
print_response_always = False
print_response_on_fail = True

serial_regex = re.compile('^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$')

class isdk_profiles(object):
    def __init__(self, type):
        self.type = type

    #=====================================================
    # Create/Patch Chassis Profiles
    #=====================================================
    def chassis_profiles(self, **kwargs):
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        profiles  = kwargs['immDict']['orgs'][org]['profiles']['chassis']
        #=====================================================
        # Get Chassis Moids based on Serial Number
        #=====================================================
        def get_chassis_moid(name, serial):
            api_handle = equipment_api.EquipmentApi(api_client)
            api_filter = f"Serial eq '{serial}'"
            api_args   = dict(filter= api_filter, _preload_content = False)
            api_query  = json.loads(api_handle.get_equipment_chassis_list(**api_args).data)
            if not api_query['Results'] == None: return api_query['Results'][0]['Moid']
            else: validating.error_serial_number(name, serial)
        #=====================================================
        # Get Existing Profiles
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = chassis_api.ChassisApi(api_client)
        org_moid = org_moids[org]['Moid']
        get_policy = api_handle.get_chassis_profile_list
        empty, chassis_profiles = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        pmoids = {}
        validating.begin_section('Chassis Profiles')
        for item in profiles:
            for i in item['targets']:
                #=====================================================
                # Get Policies Moids
                #=====================================================
                policy_list = jsonVars['chassis_profile']['policy_list']
                if not kwargs.get('full_policy_list'):
                    kwargs['full_policy_list'] = {}
                kwargs = isdk_pools('get').get_api_policy_list(api_client, org_moid, policy_list, **kwargs)
                #=====================================================
                # Construct API Body Payload
                #=====================================================
                api_body = {'class_id':'chassis.Profile', 'object_type':'chassis.Profile'}
                if i.get('description'): api_body.update({'description':i.get('description')})
                api_body.update({'name':i['name']})
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                if i.get('serial_number'):
                    if re.search(serial_regex, i['serial_number']): serial_true = True
                    else: serial_true = False
                if serial_true == True:
                    serial_true += 1
                    chassis_moid = get_chassis_moid(i['name'], i['serial_number'])
                    api_body.update({'assigned_chassis':{
                        'class_id':'mo.MoRef','moid':chassis_moid,'object_type':'equipment.Chassis'
                    }})
                #=====================================================
                # Add Policies to the Policy Bucket
                #=====================================================
                for pt in policy_list:
                    add_policy = False
                    if item.get(pt):
                        if len(item[pt]) > 0: add_policy = True
                    if add_policy == True:
                        if not api_body.get('policy_bucket'): api_body.update({'policy_bucket':[]})
                        if not kwargs['full_policy_list'][pt].get(item[pt]):
                            validating.error_policy_exist(pt, item[pt], item['name'], 'Chassis', 'Profile')
                        pdict = kwargs['full_policy_list'][pt][item[pt]]
                        pbucket = {'class_id':'mo.MoRef'}
                        if pt == 'imc_access_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'access.Policy'})
                        elif pt == 'power_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'power.Policy'})
                        elif pt == 'snmp_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'snmp.Policy'})
                        elif pt == 'thermal_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'thermal.Policy'})
                        api_body['policy_bucket'].append(pbucket)
                #=====================================================
                # Create or Patch the Profile via the Intersight API
                #=====================================================
                try:
                    api_args = dict(_preload_content = False)
                    if not chassis_profiles.get(i['name']):
                        api_method = 'create'
                        api_call = json.loads(api_handle.create_chassis_profile(api_body, **api_args).data)
                        pro_moid = api_call['Moid']
                    else:
                        api_method = 'patch'
                        pro_moid = chassis_profiles[i['name']]['Moid']
                        api_call = json.loads(api_handle.patch_chassis_profile(pro_moid, api_body, **api_args).data)
                    if print_response_always == True: print(json.dumps(api_call, indent=4))
                    validating.completed_item('Chassis Profile', i['name'], api_method, pro_moid)
                    pmoids.update({i['name']:pro_moid})
                except ApiException as e:
                    print(f"Exception when calling ChassisApi->{api_method}_chassis_profile: {e}\n")
                    sys.exit(1)
            #=====================================================
            # Deploy Chassis Profiles
            #=====================================================
            if serial_true == 1:
                if item.get('action'):
                    if item['action'] == 'Deploy':
                        api_body = {'action':'Deploy'}
                        try:
                            api_call = json.loads(
                                api_handle.patch_chassis_profile(pro_moid, api_body, **api_args).data)
                        except ApiException as e:
                            print(f"Exception when Deploying Chassis Profile {i['name']}: {e}\n")
                            sys.exit(1)
        for item in profiles:
            for i in item['targets']:
                if item.get('action'):
                    if item['action'] == 'Deploy':
                        print(f'Beginning Profile Deployment for {i["name"]}')
                        pname = i['name']
                        pro_moid = pmoids[i['name']]
                        time.sleep(120)
                        deploy_complete = False
                        while deploy_complete == False:
                            try:
                                query_args = dict(_preload_content = False)
                                api_query  = json.loads(
                                    api_handle.get_chassis_profile_by_moid(pro_moid, **query_args).data)
                                if api_query['ConfigContext']['ControlAction'] == 'No-op': deploy_complete = True
                                else:
                                    validating.deploy_notification('Chassis', pname)
                            except ApiException as e:
                                print(f"Exception when Waiting for Chassis Profile {pname}: {e}\n")
                                sys.exit(1)
                            time.sleep(120)
        validating.end_section('Chassis Profiles')
        # Return kwargs
        return kwargs
    
    #=====================================================
    # Create/Patch Domain Profiles
    #=====================================================
    def domain_profiles(self, **kwargs):
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        profiles  = kwargs['immDict']['orgs'][org]['profiles']['domain']
        #=====================================================
        # Get Switch Moides based on Serial Number
        #=====================================================
        def get_switch_moid(name, serial):
            api_filter = f"Serial eq '{serial}'"
            api_args   = dict(filter= api_filter, _preload_content = False)
            api_query  = json.loads(api_handle.get_fabric_element_identity_list(**api_args).data)
            if not api_query['Results'] == None: return api_query['Results'][0]['Moid']
            else: validating.error_serial_number(name, serial)
        #=====================================================
        # Login to Intersight API
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        validating.begin_section('Domain Profiles')
        for item in profiles:
            pname = item['name']
            org_moid = org_moids[org]['Moid']
            #=====================================================
            # Confirm if the Policy Already Exists
            #=====================================================
            get_policy = api_handle.get_fabric_switch_cluster_profile_list
            empty, domain_profiles = isdk_pools('get').get_api(get_policy, pname, org_moid)
            #=====================================================
            # Construct API Body Payload
            #=====================================================
            api_body = {'class_id':'fabric.SwitchClusterProfile', 'object_type':'fabric.SwitchClusterProfile'}
            if item.get('description'): api_body.update({'description':item.get('description')})
            api_body.update({'name':item['name']})
            api_body.update({'organization':{
                'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
            }})
            #=====================================================
            # Create or Patch the Policy via the Intersight API
            #=====================================================
            try:
                api_args = dict(_preload_content = False)
                if empty == True:
                    api_method = 'create'
                    api_call = json.loads(api_handle.create_fabric_switch_cluster_profile(api_body, **api_args).data)
                    pro_moid = api_call['Moid']
                else:
                    api_method = 'patch'
                    pro_moid = domain_profiles[item['name']]['Moid']
                    api_call = json.loads(api_handle.patch_fabric_switch_cluster_profile(pro_moid, api_body, **api_args).data)
                if print_response_always == True: print(json.dumps(api_call, indent=4))
                validating.completed_item('Domain Profile', item['name'], api_method, pro_moid)
            except ApiException as e:
                print("Exception when calling FabricApi->%s_fabric_switch_cluster_profile: %s\n" % (api_method, e))
                sys.exit(1)
            # Begin Switch Profiles
            get_policy   = api_handle.get_fabric_switch_profile_list
            query_filter = f"Parent.Moid eq '{pro_moid}'"
            swempty, sw_profiles = isdk_pools('get').get_subtype(get_policy, query_filter)
            fabrics = ['A', 'B']
            sw_names = []
            serial_true = 0
            for x in range(0,2):
                sw_name = f"{item['name']}-{fabrics[x]}"
                sw_names.append(sw_name)
                api_body = {'class_id':'fabric.SwitchProfile', 'object_type':'fabric.SwitchProfile'}
                api_body.update({'name':f"{item['name']}-{fabrics[x]}"})
                api_body.update({'SwitchClusterProfile':{
                    'class_id':'mo.MoRef','moid':pro_moid,'object_type':'fabric.SwitchClusterProfile'
                }})
                if item.get('serial_numbers'):
                    if re.search(serial_regex, item['serial_numbers'][x]): serial_true = True
                    else: serial_true = False
                if serial_true == True:
                    serial_true += 1
                    switch_moid = get_switch_moid(sw_name, item['serial_numbers'][x])
                    api_body.update({'AssignedSwitch':{
                        'class_id':'mo.MoRef','moid':switch_moid,'object_type':'network.Element'
                    }})
                try:
                    api_args = dict(_preload_content = False)
                    if swempty == True:
                        api_method = 'create'
                        api_call = json.loads(api_handle.create_fabric_switch_profile(api_body, **api_args).data)
                        sw_moid  = api_call['Moid']
                    else:
                        api_method = 'patch'
                        sw_moid  = sw_profiles[sw_name]['Moid']
                        api_call = json.loads(api_handle.patch_fabric_switch_profile(sw_moid, api_body, **api_args).data)
                    if print_response_always == True: print(json.dumps(api_call, indent=4))
                    validating.completed_item('Domain Profile', sw_name, api_method, sw_moid)
                except ApiException as e:
                    print(f"Exception when calling FabricApi->{api_method}_fabric_switch_profile: {e}\n")
                    sys.exit(1)
                kwargs[sw_name] = sw_moid
            #=====================================================
            # Attach Switch Profiles to the Policies
            #=====================================================
            for i in range(0,len(sw_names)):
                #=====================================================
                # Get Policies Moids
                #=====================================================
                policy_list = jsonVars['domain_profile']['policy_list']
                if not kwargs.get('full_policy_list'):
                    kwargs['full_policy_list'] = {}
                kwargs = isdk_pools('get').get_api_policy_list(api_client, org_moid, policy_list, **kwargs)
                sw = sw_names[i]
                sw_moid = kwargs[sw]
                profile = {'class_id':'mo.MoRef','moid':sw_moid,'object_type':'fabric.SwitchProfile'}
                for pt in policy_list:
                    add_policy = False
                    if item.get(pt):
                        if len(item[pt]) > 0: add_policy = True
                    if add_policy == True:
                        if re.search('(port|vlan|vsan)', pt):
                            if len(item[pt]) == 2:
                                if not kwargs['full_policy_list'][pt].get(item[pt][i]):
                                    validating.error_policy_exist(pt, item[pt][i], item['name'], 'Domain', 'Profile')
                                pdict = kwargs['full_policy_list'][pt][item[pt][i]]
                            else:
                                if not kwargs['full_policy_list'][pt].get(item[pt][0]):
                                    validating.error_policy_exist(pt, item[pt][i], item['name'], 'Domain', 'Profile')
                                pdict = kwargs['full_policy_list'][pt][item[pt][0]]
                        else:
                            if not kwargs['full_policy_list'][pt].get(item[pt]):
                                validating.error_policy_exist(pt, item[pt], item['name'], 'Domain', 'Profile')
                            pdict = kwargs['full_policy_list'][pt][item[pt]]
                        pol_moid = pdict['Moid']
                        if pdict.get('profiles'): pol_profiles = pdict['profiles']
                        else: pol_profiles = []
                        pol_profiles.append(profile)
                        result = []
                        for z in pol_profiles:
                            if z not in result: result.append(z)
                        api_body = {'profiles':result}
                        if pt == 'network_connectivity_policy': api_body.update({'object_type':'networkconfig.Policy'})
                        elif pt == 'ntp_policy': api_body.update({'object_type':'ntp.Policy'})
                        elif pt == 'port_policies': api_body.update({'object_type':'fabric.PortPolicy'})
                        elif pt == 'snmp_policy': api_body.update({'object_type':'snmp.Policy'})
                        elif pt == 'switch_control_policy': api_body.update({'object_type':'fabric.SwitchControlPolicy'})
                        elif pt == 'system_qos_policy': api_body.update({'object_type':'fabric.SystemQosPolicy'})
                        elif pt == 'vlan_policy': api_body.update({'object_type':'fabric.EthNetworkPolicy'})
                        elif pt == 'vsan_policy': api_body.update({'object_type':'fabric.FcNetworkPolicy'})
                        if pt == 'network_connectivity_policy': api_handle = networkconfig_api.NetworkconfigApi(api_client)
                        elif pt == 'ntp_policy': api_handle = ntp_api.NtpApi(api_client)
                        elif pt == 'snmp_policy': api_handle = snmp_api.SnmpApi(api_client)
                        elif re.search('(port|switch|qos|vlan|vsan)', pt): api_handle = fabric_api.FabricApi(api_client)
                        try:
                            if pt == 'network_connectivity_policy':
                                api_call = json.loads(
                                    api_handle.patch_networkconfig_policy(pol_moid, api_body, **api_args).data)
                            elif pt == 'ntp_policy':
                                api_call = json.loads(api_handle.patch_ntp_policy(pol_moid, api_body, **api_args).data)
                            elif pt == 'port_policies':
                                api_call = json.loads(
                                    api_handle.patch_fabric_port_policy(pol_moid, api_body, **api_args).data)
                            elif pt == 'snmp_policy':
                                api_call = json.loads(api_handle.patch_snmp_policy(pol_moid, api_body, **api_args).data)
                            elif pt == 'switch_control_policy':
                                api_call = json.loads(
                                    api_handle.patch_fabric_switch_control_policy(pol_moid, api_body, **api_args).data)
                            elif pt == 'system_qos_policy':
                                api_call = json.loads(
                                    api_handle.patch_fabric_system_qos_policy(pol_moid, api_body, **api_args).data)
                            elif pt == 'vlan_policies':
                                api_call = json.loads(
                                    api_handle.patch_fabric_eth_network_policy(pol_moid, api_body, **api_args).data)
                            elif pt == 'vsan_policies':
                                api_call = json.loads(
                                    api_handle.patch_fabric_fc_network_policy(pol_moid, api_body, **api_args).data)
                            if print_response_always == True: print(json.dumps(api_call, indent=4))
                        except ApiException as e:
                            print(f"Exception when patching {item['name']} with {pt}: {e}\n")
                            sys.exit(1)
            # Deploy Domain Profile if Hardware is Assigned
            if serial_true == 2:
                if item.get('action'):
                    if item['action'] == 'Deploy':
                        for i in range(0,len(sw_names)):
                            sw = sw_names[i]
                            sw_moid = kwargs[sw]
                            print(f'Beginning Profile Deployment for {sw}')
                            api_body = {'action':'Deploy'}
                            try:
                                api_call = json.loads(
                                    api_handle.patch_fabric_switch_profile(sw_moid, api_body, **api_args).data)
                            except ApiException as e:
                                print(f"Exception when Deploying {sw}: {e}\n")
                                sys.exit(1)
                        time.sleep(120)
                        for i in range(0,len(sw_names)):
                            sw = sw_names[i]
                            sw_moid = kwargs[sw]
                            deploy_complete = False
                            while deploy_complete == False:
                                try:
                                    query_args = dict(_preload_content = False)
                                    api_query  = json.loads(
                                        api_handle.get_fabric_switch_profile_by_moid(sw_moid, **query_args).data)
                                    if api_query['ConfigContext']['ControlAction'] == 'No-op': deploy_complete = True
                                    else:
                                        validating.deploy_notification('Domain', item['name'])
                                except ApiException as e:
                                    print(f"Exception when Deploying {sw}, {sw_moid}: {e}\n")
                                    sys.exit(1)
                                if deploy_complete == False:
                                    time.sleep(120)
        validating.end_section('Domain Profiles')
        # Return kwargs
        return kwargs
    
    #=====================================================
    # Create/Patch Server Profiles
    #=====================================================
    def server_profiles(self, **kwargs):
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        profiles  = kwargs['immDict']['orgs'][org]['profiles']['server']
        templates = kwargs['immDict']['orgs'][org]['templates']['server']
        #=====================================================
        # Get Chassis Moids based on Serial Number
        #=====================================================
        def get_server_moid(name, serial):
            api_filter = f"Serial eq '{serial}'"
            api_args   = dict(filter= api_filter, _preload_content = False)
            api_handle = compute_api.ComputeApi(api_client)
            api_query  = json.loads(api_handle.get_compute_physical_summary_list(**api_args).data)
            if not api_query['Results'] == None:
                moid = api_query['Results'][0]['Moid']
                server_object = api_query['Results'][0]['SourceObjectType']
                return moid, server_object
            else: validating.error_serial_number(name, serial)
        #=====================================================
        # Get Existing Profiles
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = server_api.ServerApi(api_client)
        org_moid = org_moids[org]['Moid']
        get_policy = api_handle.get_server_profile_list
        empty, server_profiles = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        #=====================================================
        # Get Existing Templates
        #=====================================================
        org_moid = org_moids[org]['Moid']
        get_policy = api_handle.get_server_profile_template_list
        empty, server_templates = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        #=====================================================
        # Get Policies Moids
        #=====================================================
        policy_list = jsonVars['server_profile']['policy_list']
        if not kwargs.get('full_policy_list'):
            kwargs['full_policy_list'] = {}
        kwargs = isdk_pools('get').get_api_policy_list(api_client, org_moid, policy_list, **kwargs)
        pro_moids = {}
        validating.begin_section('Server Profiles')
        for item in profiles:
            for i in item['targets']:
                #=====================================================
                # Construct API Body Payload
                #=====================================================
                api_body = {'class_id':'server.Profile', 'object_type':'server.Profile'}
                if i.get('description'): api_body.update({'description':i.get('description')})
                api_body.update({'name':i['name']})
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                if i.get('serial_number'):
                    if re.search(serial_regex, i['serial_number']): serial_true = True
                    else: serial_true = False
                if serial_true == True:
                    serial_true += 1
                    server_moid,server_object = get_server_moid(i['name'], i['serial_number'])
                    api_body.update({'assigned_server':{
                        'class_id':'mo.MoRef','moid':server_moid,'object_type':server_object
                    }})
                create_from_template = False
                if item.get('create_from_template'):
                    if item['create_from_template'] == True: create_from_template = True
                if create_from_template == False:
                    template_policy = False
                    template = item['ucs_server_profile_template']
                    for x in templates:
                        if x['name'] == template:
                            template_policy = True
                            temp_pol = x
                    if item.get('target_platform'): api_body.update({'target_platform':item['target_platform']})
                    elif template_policy == True:
                        api_body.update({'target_platform':temp_pol['target_platform']})
                    for pt in policy_list:
                        add_policy = False
                        if item.get(pt):
                            if len(item[pt]) > 0:
                                add_policy = True
                                policy = item[pt]
                        else:
                            if template_policy == True:
                                if temp_pol.get(pt):
                                    if len(temp_pol[pt]) > 0:
                                        add_policy = True
                                        policy = temp_pol[pt]
                        if add_policy == True:
                            if not api_body.get('policy_bucket'): api_body.update({'policy_bucket':[]})
                            if not kwargs['full_policy_list'][pt].get(policy):
                                validating.error_policy_exist(pt, policy, item['name'], 'Server', 'Template')
                            pdict = kwargs['full_policy_list'][pt][policy]
                            #=====================================================
                            # Add Policies to the Policy Bucket
                            #=====================================================
                            pbucket = {'class_id':'mo.MoRef'}
                            if pt == 'adapter_configuration_policy':
                                pbucket.update({'moid':pdict['Moid'],'object_type':'adapter.ConfigPolicy'})
                            elif pt == 'bios_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'bios.Policy'})
                            elif pt == 'boot_order_policy':
                                pbucket.update({'moid':pdict['Moid'],'object_type':'boot.PrecisionPolicy'})
                            elif pt == 'certificate_management_policy':
                                pbucket.update({'moid':pdict['Moid'],'object_type':'certificatemanagement.Policy'})
                            elif pt == 'device_connector_policy':
                                pbucket.update({'moid':pdict['Moid'],'object_type':'deviceconnector.Policy'})
                            elif pt == 'imc_access_policy':
                                pbucket.update({'moid':pdict['Moid'],'object_type':'access.Policy'})
                            elif pt == 'ipmi_over_lan_policy':
                                pbucket.update({'moid':pdict['Moid'],'object_type':'ipmioverlan.Policy'})
                            elif pt == 'lan_connectivity_policy':
                                pbucket.update({'moid':pdict['Moid'],'object_type':'vnic.LanConnectivityPolicy'})
                            elif pt == 'ldap_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'iam.LdapPolicy'})
                            elif pt == 'local_user_policy':
                                pbucket.update({'moid':pdict['Moid'],'object_type':'iam.EndPointUserPolicy'})
                            elif pt == 'network_connectivity_policy':
                                pbucket.update({'moid':pdict['Moid'],'object_type':'networkconfig.Policy'})
                            elif pt == 'ntp_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'ntp.Policy'})
                            elif pt == 'power_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'power.Policy'})
                            elif pt == 'san_connectivity_policy':
                                pbucket.update({'moid':pdict['Moid'],'object_type':'vnic.SanConnectivityPolicy'})
                            elif pt == 'serial_over_lan_policy':
                                pbucket.update({'moid':pdict['Moid'],'object_type':'sol.Policy'})
                            elif pt == 'smtp_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'smtp.Policy'})
                            elif pt == 'snmp_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'snmp.Policy'})
                            elif pt == 'ssh_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'ssh.Policy'})
                            elif pt == 'storage_policy':
                                pbucket.update({'moid':pdict['Moid'],'object_type':'storage.StoragePolicy'})
                            elif pt == 'syslog_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'syslog.Policy'})
                            elif pt == 'uuid_pool': pbucket.update({'moid':pdict['Moid'],'object_type':'uuidpool.Pool'})
                            elif pt == 'virtual_kvm_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'kvm.Policy'})
                            elif pt == 'virtual_media_policy':
                                pbucket.update({'moid':pdict['Moid'],'object_type':'vmedia.Policy'})
                            api_body['policy_bucket'].append(pbucket)
                #=====================================================
                # Create or Patch the Template via the Intersight API
                #=====================================================
                if create_from_template == True:
                    create_profile = False
                    if not server_templates.get(template):
                        validating.error_policy_exist(
                            'ucs_server_profile_template', template, i['name'], 'Server', 'Profile')
                    tmoid = server_templates[template]['Moid']
                    if not server_profiles.get(i['name']): create_profile = True
                    if create_profile == True:
                        bulk_body = {
                            'sources':{'moid':tmoid,'object_type':'server.ProfileTemplate'},
                            'targets':{'name':i['name'],'object_type':'server.Profile'}
                        }
                        try:
                            api_handle = bulk_api.BulkApi(api_client)
                            api_args = dict(_preload_content = False)
                            api_call = json.loads(api_handle.create_bulk_mo_cloner(bulk_body, **api_args).data)
                            if print_response_always == True: print(json.dumps(api_call, indent=4))
                        except ApiException as e:
                            print(f"Exception when calling BulkApi->create_bulk_mo_cloner: {e}\n")
                            sys.exit(1)
                        time.sleep(5)
                        api_handle = server_api.ServerApi(api_client)
                        get_policy = api_handle.get_server_profile_list
                        empty, serverp = isdk_pools('get').get_api(get_policy, i['name'], org_moid)
                        server_profiles.update({[i['name']]:{'Moid':serverp[i['name']]['Moid']}})
                try:
                    api_handle = server_api.ServerApi(api_client)
                    api_args = dict(_preload_content = False)
                    if not server_profiles.get(i['name']):
                        api_method = 'create'
                        api_call = json.loads(api_handle.create_server_profile(api_body, **api_args).data)
                        pro_moid = api_call['Moid']
                    else:
                        api_method = 'patch'
                        pro_moid = server_profiles[i['name']]['Moid']
                        api_call = json.loads(api_handle.patch_server_profile(pro_moid, api_body, **api_args).data)
                    if print_response_always == True: print(json.dumps(api_call, indent=4))
                    validating.completed_item(self.type, i['name'], api_method, pro_moid)
                except ApiException as e:
                    print(f"Exception when calling ServerApi->{api_method}_server_profile: {e}\n")
                    sys.exit(1)
                pro_moids.update({i['name']:pro_moid})
                #=====================================================
                # Deploy Server Profiles
                #=====================================================
                if serial_true == 1:
                    if item.get('action'):
                        if item['action'] == 'Deploy':
                            api_body = {'action':'Deploy'}
                            try:
                                api_call = json.loads(
                                    api_handle.patch_server_profile(pro_moid, api_body, **api_args).data)
                            except ApiException as e:
                                print(f"Exception when Deploying Server Profile {i['name']}: {e}\n")
                                sys.exit(1)
        for item in profiles:
            for i in item['targets']:
                if item.get('action'):
                    if item['action'] == 'Deploy':
                        print(f'Beginning Profile Deployment for {i["name"]}')
                        pname = i['name']
                        pro_moid = pro_moids[i['name']]
                        time.sleep(120)
                        deploy_complete = False
                        while deploy_complete == False:
                            try:
                                query_args = dict(_preload_content = False)
                                api_query  = json.loads(
                                    api_handle.get_server_profile_by_moid(pro_moid, **query_args).data)
                                if api_query['ConfigContext']['ControlAction'] == 'No-op': deploy_complete = True
                                else:
                                    validating.deploy_notification('Server', i['name'])
                            except ApiException as e:
                                print(f"Exception when Waiting for Server Profile {pname}: {e}\n")
                                sys.exit(1)
                            time.sleep(120)

        validating.end_section('Server Profiles')
        #=====================================================
        # Return kwargs
        return kwargs
    
    #=====================================================
    # Create/Patch Server Templates
    #=====================================================
    def server_templates(self, **kwargs):
        args      = kwargs['args']
        jsonVars  = kwargs['ezData']['policies']['allOf'][1]['properties']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        templates  = kwargs['immDict']['orgs'][org]['templates']['server']
        #=====================================================
        # Get Existing Templates
        #=====================================================
        api_client = credentials.config_credentials(home, args)
        api_handle = server_api.ServerApi(api_client)
        org_moid = org_moids[org]['Moid']
        get_policy = api_handle.get_server_profile_template_list
        empty, server_templates = isdk_pools('get').get_api(get_policy, 'ALLP', org_moid)
        #=====================================================
        # Get Policies Moids
        #=====================================================
        policy_list = jsonVars['server_profile']['policy_list']
        if not kwargs.get('full_policy_list'):
            kwargs['full_policy_list'] = {}
        kwargs = isdk_pools('get').get_api_policy_list(api_client, org_moid, policy_list, **kwargs)
        validating.begin_section(self.type)
        for item in templates:
            create_template = False
            if item.get('create_template'):
                if item['create_template'] == True: create_template = True
            if create_template == True:
                #=====================================================
                # Construct API Body Payload
                #=====================================================
                api_body = {
                    'class_id':'server.ProfileTemplate',
                    'object_type':'server.ProfileTemplate',
                    'target_platform':item['target_platform']
                    }
                if item.get('description'): api_body.update({'description':item.get('description')})
                api_body.update({'name':item['name']})
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                for pt in policy_list:
                    add_policy = False
                    if item.get(pt):
                        if len(item[pt]) > 0: add_policy = True
                    if add_policy == True:
                        if not api_body.get('policy_bucket'): api_body.update({'policy_bucket':[]})
                        if not kwargs['full_policy_list'][pt].get(item[pt]):
                            validating.error_policy_exist(pt, item[pt], item['name'], 'Server', 'Template')
                        pdict = kwargs['full_policy_list'][pt][item[pt]]
                        #=====================================================
                        # Add Policies to the Policy Bucket
                        #=====================================================
                        pbucket = {'class_id':'mo.MoRef'}
                        if pt == 'adapter_configuration_policy':
                            pbucket.update({'moid':pdict['Moid'],'object_type':'adapter.ConfigPolicy'})
                        elif pt == 'bios_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'bios.Policy'})
                        elif pt == 'boot_order_policy':
                            pbucket.update({'moid':pdict['Moid'],'object_type':'boot.PrecisionPolicy'})
                        elif pt == 'certificate_management_policy':
                            pbucket.update({'moid':pdict['Moid'],'object_type':'certificatemanagement.Policy'})
                        elif pt == 'device_connector_policy':
                            pbucket.update({'moid':pdict['Moid'],'object_type':'deviceconnector.Policy'})
                        elif pt == 'imc_access_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'access.Policy'})
                        elif pt == 'ipmi_over_lan_policy':
                            pbucket.update({'moid':pdict['Moid'],'object_type':'ipmioverlan.Policy'})
                        elif pt == 'lan_connectivity_policy':
                            pbucket.update({'moid':pdict['Moid'],'object_type':'vnic.LanConnectivityPolicy'})
                        elif pt == 'ldap_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'iam.LdapPolicy'})
                        elif pt == 'local_user_policy':
                            pbucket.update({'moid':pdict['Moid'],'object_type':'iam.EndPointUserPolicy'})
                        elif pt == 'network_connectivity_policy':
                            pbucket.update({'moid':pdict['Moid'],'object_type':'networkconfig.Policy'})
                        elif pt == 'ntp_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'ntp.Policy'})
                        elif pt == 'power_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'power.Policy'})
                        elif pt == 'san_connectivity_policy':
                            pbucket.update({'moid':pdict['Moid'],'object_type':'vnic.SanConnectivityPolicy'})
                        elif pt == 'serial_over_lan_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'sol.Policy'})
                        elif pt == 'smtp_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'smtp.Policy'})
                        elif pt == 'snmp_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'snmp.Policy'})
                        elif pt == 'ssh_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'ssh.Policy'})
                        elif pt == 'storage_policy':
                            pbucket.update({'moid':pdict['Moid'],'object_type':'storage.StoragePolicy'})
                        elif pt == 'syslog_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'syslog.Policy'})
                        elif pt == 'uuid_pool': pbucket.update({'moid':pdict['Moid'],'object_type':'uuidpool.Pool'})
                        elif pt == 'virtual_kvm_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'kvm.Policy'})
                        elif pt == 'virtual_media_policy': pbucket.update({'moid':pdict['Moid'],'object_type':'vmedia.Policy'})
                        api_body['policy_bucket'].append(pbucket)
                #=====================================================
                # Create or Patch the Template via the Intersight API
                #=====================================================
                try:
                    api_args = dict(_preload_content = False)
                    if not server_templates.get(item['name']):
                        api_method = 'create'
                        api_call = json.loads(api_handle.create_server_profile_template(api_body, **api_args).data)
                        pro_moid = api_call['Moid']
                    else:
                        api_method = 'patch'
                        pro_moid = server_templates[item['name']]['Moid']
                        api_call = json.loads(api_handle.patch_server_profile_template(pro_moid, api_body, **api_args).data)
                    if print_response_always == True: print(json.dumps(api_call, indent=4))
                    validating.completed_item(self.type, item['name'], api_method, pro_moid)
                except ApiException as e:
                    print(f"Exception when calling ServerApi->{api_method}_server_profile_template: {e}\n")
                    sys.exit(1)

        validating.end_section(self.type)
        #=====================================================
        # Return kwargs
        return kwargs
