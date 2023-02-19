from copy import deepcopy
from intersight.api import access_api
#from intersight.api import adapter_api
#from intersight.api import asset_api
from intersight.api import bios_api
from intersight.api import boot_api
#from intersight.api import certificatemanagement_api
from intersight.api import compute_api
#from intersight.api import cond_api
#from intersight.api import deviceconnector_api
from intersight.api import fabric_api
from intersight.api import fcpool_api
from intersight.api import iam_api
from intersight.api import ipmioverlan_api
from intersight.api import ippool_api
from intersight.api import kvm_api
from intersight.api import macpool_api
#from intersight.api import memory_api
from intersight.api import networkconfig_api
from intersight.api import ntp_api
from intersight.api import organization_api
from intersight.api import power_api
#from intersight.api import resourcepool_api
#from intersight.api import sdcard_api
from intersight.api import server_api
#from intersight.api import smtp_api
from intersight.api import snmp_api
from intersight.api import sol_api
#from intersight.api import ssh_api
from intersight.api import storage_api
from intersight.api import syslog_api
from intersight.api import thermal_api
from intersight.api import uuidpool_api
from intersight.api import vmedia_api
from intersight.api import vnic_api
from intersight.exceptions import ApiException
import credentials
import json
import re
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

serial_regex = re.compile('^[A-Z]{3}[2-3][\\d]([0][1-9]|[1-4][0-9]|[5][1-3])[\\dA-Z]{4}$')

class intersight_api(object):
    def __init__(self, type):
        self.type = type

    def api_results(self, apiQuery):
        api_dict = {}
        api_list = []
        empty = False
        if apiQuery.get('Results'):
            for i in apiQuery['Results']:
                iMoid = i['Moid']
                iName = i['Name']
                idict = {iName:{'Moid':iMoid}}
                api_dict.update(idict)
                api_list.append(iName)
            return empty, api_dict, api_list
        else:
            empty = True
            return empty, api_dict, api_list

    def bios(self, **kwargs):
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies']['bios']

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = bios_api.BiosApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_bios_policy_list(**query_args).data)
            empty, bios_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                bpolicy = deepcopy(item)
                template = item['bios_template']
                bpolicy.pop('bios_template')
                for k, v in item.items():
                    if type(v) == int or type(v) == float: bpolicy[k] = str(v)
                if re.search('(analytical|Data|DSS|HPC|Java)', template):
                    bpolicy.update({'intel_vt_for_directed_io':'disabled'})
                if re.search('(DB|M6_HPC)(_tpm)?$', template):
                    bpolicy.update({
                        'memory_refresh_rate':'1x',
                        'patrol_scrub':'custom'
                    })
                if re.search('(DSS|Java|OLTP|Virtualization)(_tpm)?$', template):
                    bpolicy.update({
                        'cpu_power_management':'custom',
                        'processor_c3report':'disabled',
                        'processor_cstate':'disabled'
                    })
                if re.search('(DSS|M6_HPC|Java|OLTP|DB|Virtualization)(_tpm)?', template):
                    bpolicy.update({
                        'processor_c1e':'disabled',
                        'processor_c6report':'disabled'
                    })
                if re.search('^(HPC|Java)(_tpm)?$', template):
                    bpolicy.update({'intel_virtualization_technology':'disabled'})
                if re.search('M6_[a-zA-Z\\_]+(_tpm)?', template):
                    bpolicy.update({'cpu_perf_enhancement':'Auto'})
                if re.search('(M6_)?(analytical_DB|Data|HPC)(_tpm)?', template):
                    bpolicy.update({'work_load_config':'Balanced'})
                if re.search('(M6_HPC|relational_DB)(_tpm)?', template):
                    bpolicy.update({'memory_inter_leave':'1 Way Node Interleave'})
                if re.search('M6_[a-zA-Z\\_]+(_tpm)?', template):
                    bpolicy.update({'cpu_perf_enhancement':'Auto'})
                if re.search('^((M6_)?(analytical_DB|HPC))(_tpm)?$', template):
                    bpolicy.update({'intel_hyper_threading_tech':'disabled'})
                if re.search('^((M6_)?(HPC|relational_DB))(_tpm)?', template):
                    bpolicy.update({
                        'energy_efficient_turbo':'disabled',
                        'llc_alloc':'enabled',
                        'snc':'enabled',
                        'upi_power_management':'enabled',
                        'xpt_prefetch':'enabled',
                    })
                if re.search('_tpm', template):
                    bpolicy.update({'tpm_control':'enabled','tpm_support':'enabled'})
                api_body = {}
                api_body.update(bpolicy)
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_bios_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling BiosApi->create_bios_policy: %s\n" % e)
                    sys.exit(1)

    def boot_order(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = boot_api.BootApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_boot_precision_policy_list(**query_args).data)
            empty, boot_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_boot_precision_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling BootApi->create_boot_precision_policy: %s\n" % e)
                    sys.exit(1)

    def chassis(self, **kwargs):
        print(f'skipping {self.type} for now')

    def empty_results(self, apiQuery):
            print(f"The API Query Results were empty for {apiQuery['ObjectType']}.  Exiting...")
            exit()

    def domain_profiles(self, **kwargs):
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        profiles  = kwargs['immDict']['orgs'][org]['intersight']['profiles']['domain']

        def get_switch_moid(serial):
            api_filter = f"Serial eq '{serial}'"
            api_args   = dict(filter= api_filter, _preload_content = False)
            api_query  = json.loads(api_handle.get_fabric_element_identity_list(**api_args).data)
            if not api_query['Results'] == None:
                return api_query['Results'][0]['Moid']

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        for item in profiles:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_fabric_switch_cluster_profile_list(**query_args).data)
            empty, domain_profiles,domain_profile_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'class_id':'fabric.SwitchClusterProfile', 'object_type':'fabric.SwitchClusterProfile'})
                if item.get('description'):
                    api_body.update({'description':item.get('description')})
                api_body.update({'name':item['name']})
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_fabric_switch_cluster_profile(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling FabricApi->create_fabric_switch_cluster_profile: %s\n" % e)
                    sys.exit(1)
                cluster_moid = api_post['Moid']
            else: cluster_moid = domain_profiles[item['name']]['Moid']
            fabrics = ['A', 'B']
            for x in range(0,2):
                sw_name = f"{item['name']}-{fabrics[x]}"
                query_filter = f"Name eq '{sw_name}' and Parent.Moid eq '{cluster_moid}'"
                query_args   = dict(filter=query_filter, _preload_content = False)
                api_query    = json.loads(api_handle.get_fabric_switch_profile_list(**query_args).data)
                swempty, sw_profiles,sw_profiles_names = intersight_api('api_results').api_results(api_query)
                if swempty == True:
                    api_body = {}
                    api_body.update({'class_id':'fabric.SwitchProfile', 'object_type':'fabric.SwitchProfile'})
                    api_body.update({'name':f"{item['name']}-{fabrics[x]}"})
                    api_body.update({'SwitchClusterProfile':{
                        'class_id':'mo.MoRef','moid':cluster_moid,'object_type':'fabric.SwitchClusterProfile'
                    }})
                    if item.get('serial_numbers'):
                        if re.search(serial_regex, item['serial_numbers'][x]): serial_true = True
                        else: serial_true = False
                    if serial_true == True:
                        switch_moid = get_switch_moid(item['serial_numbers'][x])
                        api_body.update({'AssignedSwitch':{
                            'class_id':'mo.MoRef','moid':switch_moid,'object_type':'network.Element'
                        }})
                    try:
                        api_args = dict(_preload_content = False)
                        api_post = json.loads(api_handle.create_fabric_switch_profile(api_body, **api_args).data)
                        print(json.dumps(api_post, indent=4))
                    except ApiException as e:
                        print("Exception when calling FabricApi->create_fabric_switch_profile: %s\n" % e)
                        sys.exit(1)
                    kwargs[sw_name] = {'Moid':api_post['Moid']}
                else: kwargs[sw_name] = {'Moid':sw_profiles[sw_name]['Moid']}
        # return kwargs
        return kwargs
    
    def ethernet_adapter(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = vnic_api.VnicApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_vnic_eth_adapter_policy_list(**query_args).data)
            empty, eth_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_vnic_eth_adapter_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling VnicApi->create_vnic_eth_adapter_policy: %s\n" % e)
                    sys.exit(1)

    def ethernet_network_control(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_fabric_eth_network_control_policy_list(**query_args).data)
            empty, eth_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_fabric_eth_network_control_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling FabricApi->create_fabric_eth_network_control_policy: %s\n" % e)
                    sys.exit(1)

    def ethernet_network_group(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_fabric_eth_network_group_policy_list(**query_args).data)
            empty, eth_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_fabric_eth_network_group_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling FabricApi->create_fabric_eth_network_group_policy: %s\n" % e)
                    sys.exit(1)

    def ethernet_qos(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = vnic_api.VnicApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_vnic_eth_qos_policy_list(**query_args).data)
            empty, eth_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_vnic_eth_qos_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling VnicApi->create_vnic_eth_qos_policy: %s\n" % e)
                    sys.exit(1)

    def fc(self, **kwargs):
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        if self.type == 'WWPN':
            pools = kwargs['immDict']['orgs'][org]['intersight']['pools']['wwpn']
        else: pools = kwargs['immDict']['orgs'][org]['intersight']['pools']['wwnn']

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = fcpool_api.FcpoolApi(api_client)
        for item in pools:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_fcpool_pool_list(**query_args).data)
            empty, fc_pools,fc_pools_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                if item.get('assignment_order'): api_body.update({'assignment_order':item['assignment_order']})
                else: api_body.update({'assignment_order':'sequential'})
                api_body.update({'class_id':'fcpool.Pool', 'object_type':'fcpool.Pool'})
                if item.get('description'):
                    api_body.update({'description':item.get('description')})
                api_body.update({'name':item['name']})
                api_body.update({'pool_purpose':self.type})
                if item.get('id_blocks'):
                    api_body.update({'IdBlocks':[]})
                    for i in item['id_blocks']:
                        api_body['IdBlocks'].append({
                            'ClassId':'fcpool.Block',
                            'ObjectType':'fcpool.Block',
                            'From':i['from'],
                            'Size':i['size']
                        })
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_fcpool_pool(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling FcpoolApi->create_fcpool_pool: %s\n" % e)
                    sys.exit(1)

    def fibre_channel_adapter(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = vnic_api.VnicApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_vnic_fc_adapter_policy_list(**query_args).data)
            empty, fc_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_vnic_fc_adapter_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling VnicApi->create_vnic_fc_adapter_policy: %s\n" % e)
                    sys.exit(1)

    def fibre_channel_network(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = vnic_api.VnicApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_vnic_fc_network_policy_list(**query_args).data)
            empty, fc_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_vnic_fc_network_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling VnicApi->create_vnic_fc_network_policy: %s\n" % e)
                    sys.exit(1)

    def fibre_channel_qos(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = vnic_api.VnicApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_vnic_fc_qos_policy_list(**query_args).data)
            empty, fc_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_vnic_fc_qos_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling VnicApi->create_vnic_fc_qos_policy: %s\n" % e)
                    sys.exit(1)

    def flow_control(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_fabric_flow_control_policy_list(**query_args).data)
            empty, flow_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_fabric_flow_control_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling FabricApi->create_fabric_flow_control_policy: %s\n" % e)
                    sys.exit(1)

    def imc_access(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = access_api.AccessApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_access_policy_list(**query_args).data)
            empty, imc_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_access_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling AccessApi->create_access_policy: %s\n" % e)
                    sys.exit(1)

    def ip(self, **kwargs):
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        pools     = kwargs['immDict']['orgs'][org]['intersight']['pools']['ip']

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = ippool_api.IppoolApi(api_client)
        for item in pools:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_ippool_pool_list(**query_args).data)
            empty, ip_pools,ip_pools_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                if item.get('assignment_order'): api_body.update({'assignment_order':item['assignment_order']})
                else: api_body.update({'assignment_order':'sequential'})
                api_body.update({'class_id':'ippool.Pool', 'object_type':'ippool.Pool'})
                if item.get('description'):
                    api_body.update({'description':item.get('description')})
                api_body.update({'name':item['name']})
                if item.get('ipv4_blocks'):
                    api_body.update({'IpV4Blocks':[]})
                    for i in item['ipv4_blocks']:
                        api_body['IpV4Blocks'].append({
                            'ClassId':'ippool.IpV4Block',
                            'ObjectType':'ippool.IpV4Block',
                            'From':i['from'],
                            'Size':i['size']
                        })
                if item.get('ipv4_configuration'):
                    api_body.update({'IpV4Config':{
                        'ClassId':'ippool.IpV4Config',
                        'ObjectType':'ippool.IpV4Config',
                        'Gateway':item['ipv4_configuration']['gateway'],
                        'Netmask':item['ipv4_configuration']['prefix'],
                        'PrimaryDns':item['ipv4_configuration']['primary_dns'],
                        'SecondaryDns':item['ipv4_configuration']['secondary_dns']
                    }})
                if item.get('ipv6_blocks'):
                    api_body.update({'IpV6Blocks':[]})
                    for i in item['ipv6_blocks']:
                        api_body['IpV6Blocks'].append({
                            'ClassId':'ippool.IpV6Block',
                            'ObjectType':'ippool.IpV6Block',
                            'From':i['from'],
                            'Size':i['size']
                        })
                if item.get('ipv6_configuration'):
                    api_body.update({'IpV6Config':{
                        'ClassId':'ippool.IpV6Config',
                        'ObjectType':'ippool.IpV6Config',
                        'Gateway':item['ipv6_configuration']['gateway'],
                        'Netmask':item['ipv6_configuration']['prefix'],
                        'PrimaryDns':item['ipv6_configuration']['primary_dns'],
                        'SecondaryDns':item['ipv6_configuration']['secondary_dns']
                    }})
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_ippool_pool(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling IppoolApi->create_ippool_pool: %s\n" % e)
                    sys.exit(1)

    def ipmi_over_lan(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = ipmioverlan_api.IpmioverlanApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_ipmioverlan_policy_list(**query_args).data)
            empty, boot_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_ipmioverlan_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling IpmioverlanApi->create_ipmioverlan_policy: %s\n" % e)
                    sys.exit(1)

    def lan_connectivity(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = vnic_api.VnicApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_vnic_lan_connectivity_policy_list(**query_args).data)
            empty, lan_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_vnic_lan_connectivity_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling VnicApi->create_vnic_lan_connectivity_policy: %s\n" % e)
                    sys.exit(1)

    def link_aggregation(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_fabric_link_aggregation_policy_list(**query_args).data)
            empty, link_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_fabric_link_aggregation_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling FabricApi->create_fabric_link_aggregation_policy: %s\n" % e)
                    sys.exit(1)

    def link_control(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_fabric_link_control_policy_list(**query_args).data)
            empty, link_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_fabric_link_control_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling FabricApi->create_fabric_link_control_policy: %s\n" % e)
                    sys.exit(1)

    def local_user(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = iam_api.IamApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_iam_end_point_user_policy_list(**query_args).data)
            empty, local_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_iam_end_point_user_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling IamApi->create_iam_end_point_user_policy: %s\n" % e)
                    sys.exit(1)

    def mac(self, **kwargs):
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        pools     = kwargs['immDict']['orgs'][org]['intersight']['pools']['mac']

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = macpool_api.MacpoolApi(api_client)
        for item in pools:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_macpool_pool_list(**query_args).data)
            empty, mac_pools,mac_pools_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                if item.get('assignment_order'): api_body.update({'assignment_order':item['assignment_order']})
                else: api_body.update({'assignment_order':'sequential'})
                api_body.update({'class_id':'macpool.Pool', 'object_type':'macpool.Pool'})
                if item.get('description'):
                    api_body.update({'description':item.get('description')})
                api_body.update({'name':item['name']})
                if item.get('mac_blocks'):
                    api_body.update({'MacBlocks':[]})
                    for i in item['mac_blocks']:
                        api_body['MacBlocks'].append({
                            'ClassId':'macpool.Block',
                            'ObjectType':'macpool.Block',
                            'From':i['from'],
                            'Size':i['size']
                        })
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_macpool_pool(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling MacpoolApi->create_macpool_pool: %s\n" % e)
                    sys.exit(1)

    def multicast(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_fabric_multicast_policy_list(**query_args).data)
            empty, mcast_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_fabric_multicast_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling FabricApi->create_fabric_multicast_policy: %s\n" % e)
                    sys.exit(1)

    def network_connectivity(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = networkconfig_api.NetworkconfigApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_networkconfig_policy_list(**query_args).data)
            empty, dns_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_networkconfig_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling NetworkconfigApi->create_networkconfig_policy: %s\n" % e)
                    sys.exit(1)

    def ntp(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = ntp_api.NtpApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_ntp_policy_list(**query_args).data)
            empty, ntp_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_ntp_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling NtpApi->create_ntp_policy: %s\n" % e)
                    sys.exit(1)

    def organizations(self, **kwargs):
        args        = kwargs['args']
        home        = kwargs['home']

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = organization_api.OrganizationApi(api_client)
        api_args   = dict(_preload_content = False)
        api_query = json.loads(api_handle.get_organization_organization_list(**api_args).data)
        empty, org_moids, org_names = intersight_api('api_results').api_results(api_query)
        if empty == True: intersight_api('api_results').empty_results(api_query)
        kwargs['org_moids'] = org_moids
        kwargs['org_names'] = org_names
        return kwargs

    def port(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_fabric_port_policy_list(**query_args).data)
            empty, port_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_fabric_port_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling FabricApi->create_fabric_port_policy: %s\n" % e)
                    sys.exit(1)

    def power(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = power_api.PowerApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_power_policy_list(**query_args).data)
            empty, power_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_power_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling PowerApi->create_power_policy: %s\n" % e)
                    sys.exit(1)

    def san_connectivity(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = vnic_api.VnicApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_vnic_san_connectivity_policy_list(**query_args).data)
            empty, san_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_vnic_san_connectivity_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling VnicApi->create_vnic_san_connectivity_policy: %s\n" % e)
                    sys.exit(1)

    def serial_over_lan(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = sol_api.SolApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_sol_policy_list(**query_args).data)
            empty, sol_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_sol_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling SolApi->create_sol_policy: %s\n" % e)
                    sys.exit(1)

    def server(self, **kwargs):
        print(f'skipping {self.type} for now')

    def snmp(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = snmp_api.SnmpApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_snmp_policy_list(**query_args).data)
            empty, snmp_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_snmp_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling SnmpApi->create_snmp_policy: %s\n" % e)
                    sys.exit(1)

    def storage(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = storage_api.StorageApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_storage_storage_policy_list(**query_args).data)
            empty, storage_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_storage_storage_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling StorageApi->create_storage_storage_policy: %s\n" % e)
                    sys.exit(1)

    def switch_control(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_fabric_switch_control_policy_list(**query_args).data)
            empty, ctrl_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_fabric_switch_control_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling FabricApi->create_fabric_switch_control_policy: %s\n" % e)
                    sys.exit(1)

    def syslog(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = syslog_api.SyslogApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_syslog_policy_list(**query_args).data)
            empty, log_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_syslog_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling SyslogApi->create_syslog_policy: %s\n" % e)
                    sys.exit(1)

    def system_qos(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_fabric_system_qos_policy_list(**query_args).data)
            empty, qos_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_fabric_system_qos_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling FabricApi->create_fabric_system_qos_policy: %s\n" % e)
                    sys.exit(1)

    def thermal(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = thermal_api.ThermalApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_thermal_policy_list(**query_args).data)
            empty, thermal_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_thermal_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling ThermalApi->create_thermal_policy: %s\n" % e)
                    sys.exit(1)

    def uuid(self, **kwargs):
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        pools     = kwargs['immDict']['orgs'][org]['intersight']['pools']['uuid']

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = uuidpool_api.UuidpoolApi(api_client)
        for item in pools:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_uuidpool_pool_list(**query_args).data)
            empty, uuid_pools,uuid_pools_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                if item.get('assignment_order'): api_body.update({'assignment_order':item['assignment_order']})
                else: api_body.update({'assignment_order':'sequential'})
                api_body.update({'class_id':'uuidpool.Pool', 'object_type':'uuidpool.Pool'})
                if item.get('description'):
                    api_body.update({'description':item.get('description')})
                api_body.update({'name':item['name']})
                api_body.update({'prefix':item['prefix']})
                if item.get('uuid_blocks'):
                    api_body.update({'UuidSuffixBlocks':[]})
                    for i in item['uuid_blocks']:
                        api_body['UuidSuffixBlocks'].append({
                            'ClassId':'uuidpool.UuidBlock',
                            'ObjectType':'uuidpool.UuidBlock',
                            'From':i['from'],
                            'Size':i['size']
                        })
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_uuidpool_pool(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling uuidpool_api->create_uuidpool_pool: %s\n" % e)
                    sys.exit(1)

    def virtual_kvm(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = kvm_api.KvmApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_kvm_policy_list(**query_args).data)
            empty, kvm_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_kvm_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling KvmApi->create_kvm_policy: %s\n" % e)
                    sys.exit(1)

    def virtual_media(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = vmedia_api.VmediaApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_vmedia_policy_list(**query_args).data)
            empty, vmedia_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_vmedia_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling VmediaApi->create_boot_precision_policy: %s\n" % e)
                    sys.exit(1)

    def vlan(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_fabric_eth_network_policy_list(**query_args).data)
            empty, vlan_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_fabric_eth_network_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling FabricApi->create_fabric_eth_network_policy: %s\n" % e)
                    sys.exit(1)

    def vsan(self, **kwargs):
        print(f'skipping {self.type} for now')
        return 'empty'
        args      = kwargs['args']
        home      = kwargs['home']
        org       = kwargs['org']
        org_moids = kwargs['org_moids']
        policies  = kwargs['immDict']['orgs'][org]['intersight']['policies'][self.type]

        # Login to Intersight API
        api_client = credentials.config_credentials(home, args)
        api_handle = fabric_api.FabricApi(api_client)
        for item in policies:
            query_filter = f"Name eq '{item['name']}' and Organization.Moid eq '{org_moids[org]['Moid']}'"
            query_args   = dict(filter=query_filter, _preload_content = False)
            api_query    = json.loads(api_handle.get_fabric_fc_network_policy_list(**query_args).data)
            empty, vsan_policies, policy_names = intersight_api('api_results').api_results(api_query)
            if empty == True:
                api_body = {}
                api_body.update({'organization':{
                    'class_id':'mo.MoRef','moid':org_moids[org]['Moid'],'object_type':'organization.Organization'
                }})
                try:
                    api_args = dict(_preload_content = False)
                    api_post = json.loads(api_handle.create_fabric_fc_network_policy(api_body, **api_args).data)
                    print(json.dumps(api_post, indent=4))
                except ApiException as e:
                    print("Exception when calling FabricApi->create_fabric_fc_network_policy: %s\n" % e)
                    sys.exit(1)

    def wwnn(self, **kwargs):
        intersight_api('WWNN').fc(**kwargs)
    
    def wwpn(self, **kwargs):
        intersight_api('WWPN').fc(**kwargs)

