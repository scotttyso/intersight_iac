#!/usr/bin/env python3

#=============================================================================
# Source Modules
#=============================================================================
from copy import deepcopy
from dotmap import DotMap
import difflib
import ipaddress
import json
import numpy
import os
import re
import requests
import socket
import sys
import time
import validatingv2 as validating
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, './classes')
from classes import ezfunctionsv2 as ezfunctions
from classes import netapp
from classes import isight
#=======================================================
# IMM Class
#=======================================================
class imm(object):
    def __init__(self, type):
        self.type = type

    #=============================================================================
    # Function - Build Policies - BIOS
    #=============================================================================
    def bios(self, kwargs):
        # Build Dictionary
        descr     = (self.type.replace('_', ' ')).upper()
        btemplates= []
        dataset   = []
        for k, v in kwargs.servers.items():
            dataset.append(f"{v.gen}_{v.cpu}_{v.tpm}")
        models = numpy.unique(numpy.array(dataset))
        for i in models:
            gen, cpu, tpm = i.split('_')
            if tpm == True:btemplates.append(f'{gen}-{cpu}-virtual-tpm')
            else: btemplates.append(f'{gen}-{cpu}-virtual')
        btemplates = list(numpy.unique(numpy.array(btemplates)))
        for i in btemplates:
            polVars = dict(
                baud_rate           = 115200,
                bios_template       = i,
                console_redirection = f'serial-port-a',
                description         = f'{kwargs.domain.policies.prefix}{i} {descr} Policy',
                name                = f'{kwargs.domain.policies.prefix}{i}',
                serial_port_aenable = f'enabled',
                terminal_type       = f'vt100',
            )

            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policies - Boot Order
    #=============================================================================
    def boot_order(self, kwargs):
        # Build Dictionary
        ptypes = []
        if 'fc' in kwargs.dtype: ptypes.append('fcp')
        for i in kwargs.vlans:
            if not i.vlan_type in ptypes and re.search('iscsi', i.vlan_type): ptypes.append(i.vlan_type)
        for i in ptypes:
            polVars = {
                'boot_devices': [{
                    'enabled': True,
                    'name': 'kvm',
                    'object_type': 'boot.VirtualMedia',
                    'sub_type': 'kvm-mapped-dvd'
                }],
                'boot_mode': 'Uefi',
                'description': f'{i} Boot Policy',
                'enable_secure_boot': True,
                'name': f'{kwargs.domain.policies.prefix}{i}-boot',
            }
            if 'fcp' in i:
                fabrics = ['a', 'b']
                for x in range(0,len(fabrics)):
                    for k,v in kwargs.immDict.orgs[kwargs.org].storage.items():
                        for e in v:
                            for s in e['wwpns'][chr(ord('@')+x+1).lower()]:
                                polVars['boot_devices'].append({
                                    'enabled': True,
                                    'interface_name': f'vhba{x+1}',
                                    'name':  e.svm + '-' + s.interface,
                                    'object_type': 'boot.San',
                                    'slot':'MLOM',
                                    'wwpn': s.wwpn
                                })
            elif 'iscsi' in i:
                fabrics = ['a', 'b']
                for fab in fabrics:
                        polVars['boot_devices'].append({
                            'enabled': True,
                            'interface_name': f'storage-{fab}',
                            'name': f'storage-{fab}',
                            'object_type': 'boot.Iscsi',
                            'slot':'MLOM'
                        })
            polVars['boot_devices'].append({
                'enabled': True,
                'name': 'cimc',
                'object_type': 'boot.VirtualMedia',
                'sub_type': 'cimc-mapped-dvd'
            })
            polVars['boot_devices'].append({
                'enabled': True,
                'name': 'uefishell',
                'object_type': 'boot.UefiShell'
            })
            
            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Profiles - Chassis
    #=============================================================================
    def chassis(self, kwargs):
        # Build Dictionary
        for k, v in kwargs.chassis.items():
            polVars = dict(
                action            = 'Deploy',
                imc_access_policy = f'{kwargs.domain.policies.prefix}kvm',
                power_policy      = f'{kwargs.domain.policies.prefix}{k}',
                snmp_policy       = f'{kwargs.domain.policies.prefix}snmp',
                thermal_policy    = f'{kwargs.domain.policies.prefix}{k}',
                targets           = [],
            )
            for i in v:
                polVars['targets'].append(dict(
                    description   = f'{i.domain}-{i.identity} Chassis Profile',
                    name          = f'{i.domain}-{i.identity}',
                    serial_number = i.serial
                ))
            
            # Add Policy Variables to immDict
            kwargs.class_path = f'profiles,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Profiles - Chassis
    #=============================================================================
    def compute_environment(self, kwargs):
        kwargs.servers  = DotMap([])
        #=====================================================
        # Server Dictionary Function
        #=====================================================
        def server_dictionary(i, kwargs):
            kwargs.method    = 'get'
            kwargs.api_filter= f"Ancestors/any(t:t/Moid eq '{i.Moid}')"
            kwargs.qtype     = 'processor'
            kwargs.uri       = 'processor/Units'
            kwargs= isight.api(kwargs.qtype).calls(kwargs)
            cpu   = kwargs.results[0]
            kwargs.qtype = 'tpm'
            kwargs.uri   = 'equipment/Tpms'
            kwargs= isight.api(kwargs.qtype).calls(kwargs)
            tpmd  = kwargs.results
            kwargs.qtype= 'adapter'
            kwargs.uri  = 'adapter/Units'
            kwargs = isight.api(kwargs.qtype).calls(kwargs)
            vic    = kwargs.results
            kwargs.pop('api_filter')
            if 'Intel' in cpu.Vendor: cv = 'intel'
            else: cv = 'amd'
            vics = []
            for e in vic:
                if re.search('(V5)', e.Model): vic_generation = 'gen5'
                else: vic_generation = 'gen4'
                if 'MLOM' in e.PciSlot: vic_slot = 'MLOM'
                else: vic_slot = re.search('SlotId:(\\d)', vic).group(1)
                vics.append(DotMap(vic_gen= vic_generation, vic_slot=vic_slot))

            sg = re.search('-(M[\\d])', i.Model).group(1)
            if type(vics[0].vic_slot) == str: vs1= (vics[0].vic_slot).lower()
            else: vs1= vics[0].vic_slot
            if len(vics) == 2:
                if type(vics[1].vic_slot) == str: vs2= (vics[1].vic_slot).lower()
                else: vs2= vics[1].vic_slot
            if len(tpmd) > 0:
                tpm = '-tpm'
                if len(vics) == 2:
                    template = f"{sg}-{cv}-tpm-vic-{vics[0].vic_gen}-{vs1}-{vs2}"
                else: template = f"{sg}-{cv}-tpm-vic-{vics[0].vic_gen}-{vs1}"
            else:
                tpm = ''
                if len(vics) == 2:
                    template = f"{sg}-{cv}-vic-{vics[0].vic_gen}-{vs1}-{vs2}"
                else: template = f"{sg}-{cv}-vic-{vics[0].vic_gen}-{vs1}"
            kwargs.servers[i.Serial] = DotMap(
                chassis_id  = i.ChassisId,
                chassis_moid= i.Parent.Moid,
                cpu         = cv,
                domain      = kwargs.domain.name,
                firmware    = i.Firmware,
                gen         = sg,
                moid        = i.Moid,
                model       = i.Model,
                object_type = i.SourceObjectType,
                serial      = i.Serial,
                server_id   = i.ServerId,
                slot        = i.SlotId,
                template    = template,
                tpm         = tpm,
                vics        = vics
            )
            if i.SourceObjectType == 'compute.RackUnit':
                kwargs.servers[i.Serial].pop('chassis_moid')
            return kwargs

        #=====================================================
        # Build Domain Dictionaries
        #=====================================================
        if kwargs.domain:
            kwargs.chassis= DotMap([])
            kwargs.method = 'get'
            kwargs.names  = [kwargs.domain.serial_numbers[0]]
            kwargs.qtype  = 'serial_number'
            kwargs.uri    = 'network/Elements'
            kwargs        = isight.api(kwargs.qtype).calls(kwargs)
            pmoids        = kwargs.pmoids

            for k, v in pmoids.items():
                reg_device = v.registered_device
            kwargs.api_filter= f"RegisteredDevice.Moid eq '{reg_device}'"
            kwargs.uri       = 'equipment/Chasses'
            kwargs           = isight.api(kwargs.qtype).calls(kwargs)
            chassis_pmoids   = kwargs.pmoids
            kwargs.uri       = 'compute/PhysicalSummaries'
            kwargs           = isight.api(kwargs.qtype).calls(kwargs)
            rack_pmoids      = kwargs.pmoids
            kwargs.pop('api_filter')
            #=====================================================
            # Build Chassis Dictionary
            #=====================================================
            models = []
            for k, v in chassis_pmoids.items():
                models.append(str(v.model).lower())
            models = numpy.unique(numpy.array(models))
            for model in models:
                kwargs.chassis[model] = []
            for k, v in chassis_pmoids.items():
                model = str(v.model).lower()
                kwargs.chassis[model].append(DotMap(
                    domain  = kwargs.domain.name,
                    identity= v.id,
                    serial  = k
                ))

            #=====================================================
            # Build Server Dictionaries - Domain
            #=====================================================
            for k, v in chassis_pmoids.items():
                for e in v.blades:
                    kwargs.method='get_by_moid'
                    kwargs.qtype = 'serial_number'
                    kwargs.uri   = 'compute/PhysicalSummaries'
                    kwargs.pmoid = e.moid
                    kwargs = isight.api(kwargs.qtype).calls(kwargs)
                    kwargs = server_dictionary(kwargs.results, kwargs)
            for k, v in rack_pmoids.items():
                kwargs.method='get_by_moid'
                kwargs.qtype = 'serial_number'
                kwargs.uri   = 'compute/PhysicalSummaries'
                kwargs.pmoid = e.moid
                kwargs = isight.api(kwargs.qtype).calls(kwargs)
                kwargs = server_dictionary(kwargs.results, kwargs)
        else:
            #=====================================================
            # Build Server Dictionaries - Standalone
            #=====================================================
            kwargs.method= 'get'
            kwargs.names = kwargs.serial_numbers
            kwargs.qtype = 'serial_number'
            kwargs.uri   = 'compute/PhysicalSummaries'
            kwargs = isight.api(kwargs.qtype).calls(kwargs)
            for i in kwargs.results:
                kwargs = server_dictionary(i, kwargs)


        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Profiles - Domain
    #=============================================================================
    def domain(self, kwargs):
        # Build Dictionary
        polVars = dict(
            action                     = 'Deploy',
            description                = f'{kwargs.domain.name} Domain Profile',
            name                       = kwargs.domain.name,
            network_connectivity_policy= f'{kwargs.domain.policies.prefix}dns',
            ntp_policy                 = f'{kwargs.domain.policies.prefix}ntp',
            port_policies              = [f'{kwargs.domain.name}-A', f'{kwargs.domain.name}-B'],
            serial_numbers             = kwargs.domain.serial_numbers,
            snmp_policy                = f'{kwargs.domain.policies.prefix}snmp-domain',
            switch_control_policy      = f'{kwargs.domain.policies.prefix}sw-ctrl',
            syslog_policy              = f'{kwargs.domain.policies.prefix}syslog-domain',
            system_qos_policy          = f'{kwargs.domain.policies.prefix}qos',
            vlan_policies              = f'{kwargs.domain.policies.prefix}vlans',
        )
        if re.search('(fc|fc-nvme)', kwargs.dtype):
            polVars['vsan_policies'] = []
            for i in kwargs.domain.vsans:
                polVars['vsan_policies'].append(f'{kwargs.domain.policies.prefix}vsan-{i}')
        # Add Policy Variables to immDict
        kwargs.class_path = f'profiles,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Ethernet Adapter
    #=============================================================================
    def ethernet_adapter(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['16RxQs-4G', '16RxQs-5G', 'VMware', 'VMware-High-Trf']
        for i in plist:
            polVars = dict(
                adapter_template = i,
                description      = f'{kwargs.domain.policies.prefix}{i} {descr} Policy',
                name             = f'{kwargs.domain.policies.prefix}{i}',
            )

            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Ethernet Network Control
    #=============================================================================
    def ethernet_network_control(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['cdp', 'cdp-lldp', 'lldp']
        for i in plist:
            if 'cdp' in i: cdpe = True
            else: cdpe = False
            if 'lldp' in i: lldpe = True
            else: lldpe = False
            polVars = dict(
                cdp_enable           = cdpe,
                description          = f'{kwargs.domain.policies.prefix}{i} {descr} Policy',
                name                 = f'{kwargs.domain.policies.prefix}{i}',
                lldp_receive_enable  = lldpe,
                lldp_transmit_enable = lldpe,
                mac_register_mode    = 'nativeVlanOnly',
                mac_security_forge   = 'allow',
            )

            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Ethernet Network Group
    #=============================================================================
    def ethernet_network_group(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        vlans = []
        for i in kwargs.vlans: vlans.append(i.vlan_id)
        for i in kwargs.ranges:
            vrange = ezfunctions.vlan_list_full(i.vlan_list)
            vlans.extend(vrange)
        kwargs.vlan = DotMap()
        kwargs.vlan.iscsi     = []
        kwargs.vlan.mgmt      = ''
        kwargs.vlan.migration = ''
        kwargs.vlan.nfs       = ''
        kwargs.vlan.nvme      = []
        kwargs.vlan['all_vlans'] = ezfunctions.vlan_list_format(list(numpy.unique(numpy.array(vlans))))
        for i in kwargs.vlans:
            if   i.vlan_type == 'inband': kwargs.vlan.mgmt = i.vlan_id
            elif i.vlan_type == 'iscsi': kwargs.vlan.iscsi.append(i.vlan_id)
            elif i.vlan_type == 'migration': kwargs.vlan.migration = i.vlan_id
            elif i.vlan_type == 'nfs': kwargs.vlan.nfs = i.vlan_id
            elif i.vlan_type == 'nvme': kwargs.vlan.nvme.append(i.vlan_id)
        if len(kwargs.vlan.iscsi) == 2 and len(kwargs.vlan.nvme) == 2:
            kwargs.vlan.storage_a = ezfunctions.vlan_list_format(sorted(
                [kwargs.vlan.nfs, kwargs.vlan.iscsi[0], kwargs.vlan.nvme[0]]))
            kwargs.vlan.storage_b = ezfunctions.vlan_list_format(sorted(
                [kwargs.vlan.nfs, kwargs.vlan.iscsi[1], kwargs.vlan.nvme[1]]))
        else:
            kwargs.vlan.storage_a = kwargs.vlan.nfs
            kwargs.vlan.storage_b = kwargs.vlan.nfs
        plist = ['mgmt', 'migration', 'storage-a', 'storage-b', 'all_vlans']
        for i in plist:
            if re.search('(mgmt|migration)', i) and len(str(kwargs.vlan[i])) > 0: nvlan = kwargs.vlan[i]
            elif 'storage-a' == i and len(kwargs.vlan.iscsi) == 2:
                nvlan = kwargs.vlan.iscsi[0]
            elif 'storage-b' == i and len(kwargs.vlan.iscsi) == 2:
                nvlan = kwargs.vlan.iscsi[1]
            else: nvlan = 1
            vlan_name = i.replace('-', '_')
            polVars = dict(
                allowed_vlans = f'{kwargs.vlan[vlan_name]}',
                description   = f'{kwargs.domain.policies.prefix}{i} {descr} Policy',
                name          = f'{kwargs.domain.policies.prefix}{i}',
                native_vlan   = nvlan,
            )
            
            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Ethernet QoS
    #=============================================================================
    def ethernet_qos(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['Best Effort', 'Bronze', 'Gold', 'Platinum', 'Silver']
        for i in plist:
            name = i.replace(' ', '-')
            polVars = dict(
                enable_trust_host_cos= False,
                burst        = 10240,
                description  = f'{kwargs.domain.policies.prefix}{name} {descr} Policy',
                name         = f'{kwargs.domain.policies.prefix}{name}',
                mtu          = 9000,
                priority     = i,
                rate_limit   = 0,
            )

            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Pools - WWNN/WWPN
    #=============================================================================
    def fc(self, kwargs):
        # Build Dictionary
        polVars = dict(
            assignment_order = 'sequential',
            description      = f'{kwargs.domain.policies.prefix}wwnn Pool',
            name             = f'{kwargs.domain.policies.prefix}wwnn',
            id_blocks        = [{
                'from':f'20:00:00:25:B5:{kwargs.domain.pools.prefix}:00:00',
                'size':1024
            }],
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'pools,wwnn'
        kwargs = ezfunctions.ez_append(polVars, kwargs)

        # Loop through WWPN Pools
        flist = ['A', 'B']
        for i in flist:
            polVars.update(dict(
                description = f'{kwargs.domain.policies.prefix}wwpn-{i.lower()} Pool',
                name        = f'{kwargs.domain.policies.prefix}wwpn-{i.lower()}',
            ))
            polVars['id_blocks'][0].update({'from':f'20:00:00:25:B5:{kwargs.domain.pools.prefix}:{i}0:00'})
            kwargs.class_path = f'pools,wwpn'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - FC Zone
    #=============================================================================
    def fc_zone(self, kwargs):
        descr = (self.type.replace('_', ' ')).title()
        fabrics = ['a', 'b']
        kwargs.fc_zone = []
        for x in range(0,len(fabrics)):
            if len(kwargs.domain.vsans) == 2: vsan = kwargs.domain.vsans[x]
            else: vsan = kwargs.domain.vsans[0]
            name = f'{kwargs.domain.policies.prefix}fabric-{fabrics[x]}-vsan-{vsan}'
            # Build Dictionary
            polVars = dict(
                description           = f'{name} {descr} Policy',
                fc_target_zoning_type = 'SIMT',
                name                  = name,
                targets               = [],
            )
            kwargs.storage = kwargs.immDict.orgs[kwargs.org].storage
            for k, v in kwargs.storage.items():
                for e in v:
                    for i in e.wwpns[fabrics[x]]:
                        polVars['targets'].append(dict(
                            name      = e.svm + '-' + i.interface,
                            switch_id = (fabrics[x]).upper(),
                            vsan_id   = vsan,
                            wwpn      = i.wwpn
                        ))
                    kwargs.fc_zone.append(polVars['name'])

            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Fibre-Channel Adapter
    #=============================================================================
    def fibre_channel_adapter(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['VMware', 'FCNVMeInitiator']
        for i in plist:
            polVars = dict(
                adapter_template = i,
                description      = f'{kwargs.domain.policies.prefix}{i} {descr} Policy',
                name             = f'{kwargs.domain.policies.prefix}{i}',
            )

            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Fibre-Channel Network
    #=============================================================================
    def fibre_channel_network(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        for i in kwargs.domain.vsans:
            polVars = dict(
                description = f'{kwargs.domain.policies.prefix}vsan-{i} {descr} Policy',
                name        = f'{kwargs.domain.policies.prefix}vsan-{i}',
                vsan_id     = i,
            )

            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Fibre-Channel QoS
    #=============================================================================
    def fibre_channel_qos(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['fc-qos']
        for i in plist:
            polVars = dict(
                max_data_field_size = 2112,
                burst               = 10240,
                description         = f'{kwargs.domain.policies.prefix}{i} {descr} Policy',
                name                = f'{kwargs.domain.policies.prefix}{i}',
                rate_limit          = 0,
            )

            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policies - Firmware
    #=============================================================================
    def firmware(self, kwargs):
        # Build Dictionary
        descr   = (self.type.replace('_', ' ')).upper()
        dataset = []
        fw = kwargs.domain.firmware
        fw_name = (fw.replace(')', '')).replace('(', '-')
        kwargs.firmware_policy_name = fw_name
        for k, v in kwargs.servers.items():
            dataset.append(v.model)
        models = numpy.unique(numpy.array(dataset))
        polVars = dict(
            description       = f'{kwargs.domain.policies.prefix}{fw_name} {descr} Policy',
            model_bundle_combo= [],
            name              = f'{kwargs.domain.policies.prefix}{fw_name}',
            target_platform   = 'FIAttached'
        )
        for i in models:
            polVars['model_bundle_combo'].append(dict(
                bundle_version= fw,
                model_family  = i
            ))

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Flow Control
    #=============================================================================
    def flow_control(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.domain.policies.prefix}flow-ctrl {descr} Policy',
            name        = f'{kwargs.domain.policies.prefix}flow-ctrl',
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - IMC Access
    #=============================================================================
    def imc_access(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description         = f'{kwargs.domain.policies.prefix}kvm {descr} Policy',
            inband_ip_pool      = f'kvm-inband',
            inband_vlan_id      = kwargs.inband.vlan_id,
            out_of_band_ip_pool = 'kvm-ooband',
            name                = f'{kwargs.domain.policies.prefix}kvm',
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Pools - IP
    #=============================================================================
    def ip(self, kwargs):
        pdns = kwargs.dns_servers[0]
        sdns = ''
        if len(kwargs.dns_servers) >= 2: sdns = kwargs.dns_servers[1]
        # Build Dictionary
        for i in kwargs.vlans:
            if re.search('(inband|iscsi|ooband)', i.vlan_type):
                if not kwargs.pools.ip.get(i.vlan_type):
                    kwargs.pools.ip[i.vlan_type] = []
                if re.search('inband|ooband', i.vlan_type):
                    name = f'{kwargs.domain.policies.prefix}kvm-{i.vlan_type}'
                    pool_from = i.pool[0]
                    pool_to   = i.pool[-1]
                else:
                    name = f'{kwargs.domain.policies.prefix}iscsi-vlan{i.vlan_id}'
                    pool_from = i.server[0]
                    pool_to   = i.server[-1]
                kwargs['defaultGateway'] = i.gateway
                kwargs['subnetMask']     = i.netmask
                kwargs['ip_version']     = 'v4'
                kwargs['pool_from']      = pool_from
                kwargs['pool_to']        = pool_to
                validating.error_subnet_check(kwargs)
                size = int(ipaddress.IPv4Address(pool_to)) - int(ipaddress.IPv4Address(pool_from)) + 1
                polVars = dict(
                    assignment_order = 'sequential',
                    description      = f'{name} IP Pool',
                    name             = f'{name}',
                    ipv4_blocks      = [{
                        'from':pool_from,
                        'size':size
                    }],
                    ipv4_configuration = [dict(
                        gateway       = i.gateway,
                        netmask       = i.netmask,
                        primary_dns   = pdns,
                        secondary_dns = sdns
                    )],
                )
                kwargs.pools.ip[i.vlan_type].append(polVars['name'])
                # Add Policy Variables to immDict
                kwargs.class_path = f'pools,{self.type}'
                kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Pools - IQN
    #=============================================================================
    def iqn(self, kwargs):
        # Build Dictionary
        polVars = dict(
            assignment_order = 'sequential',
            description      = f'{kwargs.domain.policies.prefix}iscsi IQN Pool',
            name             = f'{kwargs.domain.policies.prefix}iscsi',
            prefix           = f'iqn.1984-12.com.cisco',
            iqn_blocks       = [{
                'from': 0,
                'size': 1024,
                'suffix': 'ucs-host'
            }],
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'pools,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - IPMI over LAN
    #=============================================================================
    def ipmi_over_lan(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.domain.policies.prefix}ipmi {descr} Policy',
            name        = f'{kwargs.domain.policies.prefix}ipmi',
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - iSCSI Adapter
    #=============================================================================
    def iscsi_adapter(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description            = f'{kwargs.domain.policies.prefix}iadapter {descr} Policy',
            dhcp_timeout           = 60,
            name                   = f'{kwargs.domain.policies.prefix}iadapter',
            lun_busy_retry_count   = 15,
            tcp_connection_timeout = 15,
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - iSCSI Boot
    #=============================================================================
    def iscsi_boot(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        fabrics = ['a', 'b']
        list_of_list = []
        for i in range(0, len(kwargs.iscsi.targets), 2): list_of_list.append(kwargs.iscsi.targets[i:i+2])
        #half = kwargs.iscsi.targets // 2
        kwargs.a.targets  = list_of_list[0]
        kwargs.b.targets  = list_of_list[1]
        kwargs.iscsi.boot = []
        for x in range(0,len(fabrics)):
            pool = kwargs.pools.ip.iscsi[x]
            polVars = dict(
                description             = f'{kwargs.domain.policies.prefix}{pool} {descr} Policy',
                initiator_ip_source     = 'Pool',
                initiator_ip_pool       = kwargs.pools.ip.iscsi[x], 
                iscsi_adapter_policy    = f'{kwargs.domain.policies.prefix}iadapter',
                name                    = f'{kwargs.domain.policies.prefix}{pool}',
                primary_target_policy   = kwargs[fabrics[x]].targets[0],
                secondary_target_policy = kwargs[fabrics[x]].targets[1],
                target_source_type      = f'Static',
            )
            kwargs.iscsi.boot.append(polVars['name'])

            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - iSCSI Target
    #=============================================================================
    def iscsi_static_target(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        kwargs.iscsi.targets = []
        for k, v in kwargs.immDict.orgs[kwargs.org].storage.items():
            for e in v:
                for i in e.iscsi.interfaces:
                    name = e.svm + ':' + i.interface
                    polVars = dict(
                        description = f'{name} {descr} Policy',
                        ip_address  = i.ip_address,
                        luns        = [{
                            'bootable':True,
                            'lun_id':0
                        }],
                        name        = f'{name}',
                        port        = 3260,
                        target_name = v[0].iscsi.iqn,
                    )
                    kwargs.iscsi.targets.append(name)
                    
                    # Add Policy Variables to immDict
                    kwargs.class_path = f'policies,{self.type}'
                    kwargs = ezfunctions.ez_append(polVars, kwargs)
       
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - LAN Connectivity
    #=============================================================================
    def lan_connectivity(self, kwargs):
        # Build Dictionary
        vics  = []
        for k, v in kwargs.servers.items():
            if len(v.vics) == 2: vics = f'{v.vics[0].vic_gen}:{v.vics[0].vic_slot}-{v.vics[1].vic_slot}'
            else: vics = f'{v.vics[0].vic_gen}:{v.vics[0].vic_slot}'

        kwargs.vic_details= list(numpy.unique(numpy.array(vics)))
        lan_policies = ['lcp']
        for i in kwargs.vlans:
            if i.vlan_type == 'iscsi':
                lan_policies.append('lcp-iscsi')
                break
        for g in kwargs.vic_details:
            for lcp in lan_policies:
                descr    = (self.type.replace('_', ' ')).title()
                ga       = g.split(':')
                gen      = ga[0]
                name     = (f'{lcp}-vic-{g}').lower()
                pci_order= kwargs.pci_order
                slots    = (ga[1]).split('-')
                polVars  = dict(
                    description          = f'{kwargs.domain.policies.prefix}{name} {descr} Policy',
                    iqn_pool             = '',
                    name                 = f'{kwargs.domain.policies.prefix}{name}',
                    target_platform      = 'FIAttached',
                    vnics                = [],
                )
                if re.search('iscsi', lcp):
                    polVars['iqn_pool'] = f'{kwargs.domain.policies.prefix}iscsi'
                else: polVars.pop('iqn_pool')
                plist = ['mgmt-Silver', 'migration-Bronze', 'storage-Platinum', 'dvs-Gold']
                vnic_count = 0
                for i in plist:
                    vname = i.split('-')[0]
                    pqos  = i.split('-')[1]
                    if 'dvs' in vname: pgroups = ['all_vlans']
                    elif 'storage' in vname: pgroups = [f'{vname}-a', f'{vname}-b']
                    else: pgroups = [vname]
                    if re.search('(dvs|migration)', i): adapter_policy = 'VMware-High-Trf'
                    elif 'storage' in i and gen == 'gen4': adapter_policy = '16RxQs-4G'
                    elif 'storage' in i and gen == 'gen5': adapter_policy = '16RxQs-5G'
                    else: adapter_policy = 'VMware'
                    if len(slots) == 1: placement_order = pci_order, pci_order + 1,
                    else: placement_order = pci_order, pci_order
                    polVars['vnics'].append(dict(
                        ethernet_adapter_policy        = adapter_policy,
                        ethernet_network_control_policy= 'cdp',
                        ethernet_network_group_policies= pgroups,
                        ethernet_qos_policy            = pqos,
                        iscsi_boot_policies            = [],
                        names                          = [f'{vname}-a', f'{vname}-b'],
                        mac_address_pools              = [f'{vname}-a', f'{vname}-b'],
                        placement_pci_order            = placement_order,
                        placement_slot_ids             = slots
                    ))
                    if 'storage' in vname and 'iscsi' in lcp:
                        polVars['vnics'][vnic_count].update({'iscsi_boot_policies': kwargs.iscsi.boot})
                    else: polVars['vnics'][vnic_count].pop('iscsi_boot_policies')
                    if len(slots) == 1: pci_order += 2
                    else: pci_order += 1
                    vnic_count += 1
                
                # Add Policy Variables to immDict
                kwargs.class_path = f'policies,{self.type}'
                kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        kwargs.pci_order = pci_order
        return kwargs


    #=============================================================================
    # Function - Build Policy - Link Aggregation
    #=============================================================================
    def link_aggregation(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.domain.policies.prefix}link-agg {descr} Policy',
            name        = f'{kwargs.domain.policies.prefix}link-agg',
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Link Control
    #=============================================================================
    def link_control(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.domain.policies.prefix}link-ctrl {descr} Policy',
            name        = f'{kwargs.domain.policies.prefix}link-ctrl',
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Local User
    #=============================================================================
    def local_user(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.domain.policies.prefix}users {descr} Policy',
            name        = f'{kwargs.domain.policies.prefix}users',
            users       = [dict(
                enabled  = True,
                password = 1,
                role     = 'admin',
                username = kwargs.domain.policies.local_user
            )]
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Pools - MAC
    #=============================================================================
    def mac(self, kwargs):
        # Build Dictionary
        flist = ['a', 'b']
        nlist = ['1-2-dvs', 'A-B-mgmt', 'C-D-migration', 'E-F-storage', ]
        for i in nlist:
            for x in range(0,len(flist)):
                n = i.split('-')
                pool = n[2]
                polVars = dict(
                    assignment_order = 'sequential',
                    description      = f'{kwargs.domain.policies.prefix}{pool}-{flist[x]} Pool',
                    name             = f'{kwargs.domain.policies.prefix}{pool}-{flist[x]}',
                    mac_blocks       = [{
                        'from':f'00:25:B5:{kwargs.domain.pools.prefix}:{n[x]}0:00',
                        'size':1024
                    }],
                )

                # Add Policy Variables to immDict
                kwargs.class_path = f'pools,{self.type}'
                kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Multicast
    #=============================================================================
    def multicast(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.domain.policies.prefix}mcast {descr} Policy',
            name        = f'{kwargs.domain.policies.prefix}mcast',
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Network Connectivity
    #=============================================================================
    def network_connectivity(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description    = f'{kwargs.domain.policies.prefix}dns {descr} Policy',
            name           = f'{kwargs.domain.policies.prefix}dns',
            dns_servers_v4 = kwargs.dns_servers,
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,network_connectivity'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - NTP
    #=============================================================================
    def ntp(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.domain.policies.prefix}ntp {descr} Policy',
            name        = f'{kwargs.domain.policies.prefix}ntp',
            ntp_servers = kwargs.ntp_servers,
            timezone    = kwargs.timezone,
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,ntp'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Port
    #=============================================================================
    def port(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        ports = []
        for i in kwargs.domain.eth_uplinks:
            ports.append({'port_id':int(i.split('/')[-1])})
        x = str(kwargs.domain.eth_uplinks[0]).split('/')
        if len(x) == 3: pc_id = '1' + x[1] + x[2]
        else: pc_id = x[-1]
        pc_id = int(pc_id)
        polVars = dict(
            description  = f'{kwargs.domain.name} {descr} Policy',
            device_model = kwargs.domain.device_model,
            names        = [f'{kwargs.domain.name}-A', f'{kwargs.domain.name}-B'],
            port_channel_ethernet_uplinks = [dict(
                admin_speed                   = 'Auto',
                ethernet_network_group_policy = f'{kwargs.domain.policies.prefix}all_vlans',
                flow_control_policy           = f'{kwargs.domain.policies.prefix}flow-ctrl',
                interfaces                    = ports,
                link_aggregation_policy       = f'{kwargs.domain.policies.prefix}link-agg',
                link_control_policy           = f'{kwargs.domain.policies.prefix}link-ctrl',
                pc_ids                        = [pc_id, pc_id],
            )]
        )
        if re.search('(fc|fc-nvme)', kwargs.dtype):
            ports= []
            x    = kwargs.domain.fcp_uplink_ports[0].split('/')
            for i in kwargs.domain.fcp_uplink_ports:
                ports.append({'port_id':int(i.split('/')[-1])})
            if kwargs.swmode == 'end-host':
                if len(x) == 3: pc_id = '1' + x[1] + x[2]
                else: pc_id = x[-1]
                polVars.update(dict(
                    port_channel_fc_uplinks = [dict(
                        admin_speed  = kwargs.domain.fcp_uplink_speed,
                        fill_pattern = 'Idle',
                        interfaces   = ports,
                        pc_ids       = [pc_id, pc_id],
                        vsan_ids     = kwargs.domain.vsans
                    )]
                ))
                if len(x) == 3:
                    for i in polVars['port_channel_fc_uplinks']['interfaces']:
                        i.update({'breakout_port_id':x[2]})
            else:
                ports = x[-1]
                polVars.update(dict(
                    port_role_fc_storage = [dict(
                        admin_speed  = kwargs.domain.fcp_uplink_speed,
                        port_list    = ports,
                        vsan_ids     = kwargs.domain.vsans
                    )]
                ))
                if len(x) == 3:
                    polVars['port_role_fc_storage'].update({'breakout_port_id':x[2]})
            if len(x) == 3:
                port_start = int(kwargs.domain.fcp_uplink_ports[0].split('/')[-2])
                port_end   = int(kwargs.domain.fcp_uplink_ports[-1].split('/')[-2])
                polVars.update(dict(
                    port_modes = [dict(
                        custom_mode = f'BreakoutFibreChannel{kwargs.breakout_speed.fc}',
                        port_list   = [port_start, port_end]
                    )]
                ))
            else:
                port_start = int(kwargs.domain.fcp_uplink_ports[0].split('/')[-1])
                port_end   = int(kwargs.domain.fcp_uplink_ports[-1].split('/')[-1])
                if port_start < 15: port_start = 1
                if port_end > 12: port_end = 16
                elif port_end > 8: port_end = 12
                elif port_end > 4: port_end = 8
                else: port_end = 4
                polVars.update(dict(
                    port_modes = [dict(
                        custom_mode = 'FibreChannel',
                        port_list   = [port_start, port_end]
                    )]
                ))
        polVars.update({'port_role_servers':[]})
        for i in kwargs.domain.profiles:
                if len(i.domain_ports[0].split('/')) == 3:
                    port_start= int(i.domain_ports[0].split('/'))[2]
                    port_end  = int(i.domain_ports[-1].split('/'))[2]
                    polVars['port_modes'].append(dict(
                        custom_mode = f'BreakoutEthernet{kwargs.breakout_speed.eth}',
                        port_list   = [port_start, port_end]
                    ))
                    for e in i.domain_ports:
                        polVars['port_role_servers'].append(dict(
                            breakout_port_id      = e.split('/')[-2],
                            connected_device_type = i.equipment_type,
                            device_number         = i.identifier,
                            port_list             = e.split('/')[-1]
                        ))
                else:
                    ports = []
                    for e in i.domain_ports: ports.append(int(e.split('/')[-1]))
                    port_list = ezfunctions.vlan_list_format(ports)
                    polVars['port_role_servers'].append(dict(
                        connected_device_type = i.equipment_type,
                        device_number         = i.identifier,
                        port_list             = port_list
                    ))

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Power
    #=============================================================================
    def power(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        power_list = []
        for i in kwargs.chassis:
            power_list.append(i)
        power_list.append('server')
        for i in power_list:
            polVars = dict(
                description      = f'{kwargs.domain.policies.prefix}{i} {descr} Policy',
                name             = f'{kwargs.domain.policies.prefix}{i}',
                power_allocation = 0,
                power_redundancy = 'Grid',
            )
            if i == 'server': polVars.update({'power_restore':'LastState'})
            if '9508' in i: polVars['power_allocation'] = 8400
            else: polVars.pop('power_allocation')

            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - SAN Connectivity
    #=============================================================================
    def san_connectivity(self, kwargs):
        # Build Dictionary
        descr     = (self.type.replace('_', ' ')).title()
        pci_order = kwargs.pci_order
        for g in kwargs.vic_details:
            gen      = g.split(':')[0]
            name     = (f'scp-vic-{g}').lower()
            slots    = (g.split(':')[1]).split('-')
            polVars = dict(
                description          = f'{kwargs.domain.policies.prefix}{name} {descr} Policy',
                name                 = f'{kwargs.domain.policies.prefix}{name}',
                target_platform      = 'FIAttached',
                vhbas                = [],
                wwnn_allocation_type = 'POOL',
                wwnn_pool            = f'{kwargs.domain.policies.prefix}wwnn',
            )
            ncount = 1
            if   kwargs.dtype == 'fc': adapter_list = ['VMware']
            elif kwargs.dtype == 'fc-nvme': adapter_list = ['VMware', 'FCNVMeInitiator']
            vcount = 0
            network_policies = []
            for v in kwargs.domain.vsans:
                network_policies.append(f'vsan-{v}')

            
            if len(slots) == 1: placement_order = pci_order, pci_order + 1,
            else: placement_order = pci_order, pci_order,
            for x in range(0,len(adapter_list)):
                polVars['vhbas'].append(dict(
                    fc_zone_policies              = [],
                    fibre_channel_adapter_policy  = adapter_list[x],
                    fibre_channel_network_policies= network_policies,
                    fibre_channel_qos_policy      = 'fc-qos',
                    names                         = [f'vhba{ncount}', f'vhba{ncount + 1}'],
                    placement_pci_order           = placement_order,
                    wwpn_allocation_type          = 'POOL',
                    wwpn_pools                    = [f'wwpn-a', f'wwpn-b'],
                    placement_slot_ids            = slots
                ))
                if 'switch' in kwargs.domain.switch_mode:
                    polVars['vhbas'][vcount].update({'fc_zone_policies': kwargs.fc_zone})
                else: polVars['vhbas'][vcount].pop('fc_zone_policies')
                ncount += 2
                vcount += 1
                if len(slots) == 1: pci_order += 2
                else: pci_order += 1
                
                # Add Policy Variables to immDict
                kwargs.class_path = f'policies,{self.type}'
                kwargs = ezfunctions.ez_append(polVars, kwargs)
        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Serial over LAN
    #=============================================================================
    def serial_over_lan(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.domain.policies.prefix}sol {descr} Policy',
            name        = f'{kwargs.domain.policies.prefix}sol',
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Profiles - Server
    #=============================================================================
    def server(self, kwargs):
        #=====================================================
        # Server Profile IP settings Function
        #=====================================================
        def server_profile_networks(name, p, kwargs):
            #=====================================================
            # Send Error Message if IP Range isn't long enough
            #=====================================================
            def error_ip_range(i):
                prRed(f'!!! ERROR !!!\nNot Enough IPs in Range {i.server} for {name}')
                sys.exit(1)

            #=====================================================
            # Send Error Message if Server Range is missing
            #=====================================================
            def error_server_range(i):
                prRed(f'!!! ERROR !!!\nDid Not Find Server IP Range defined for {i.vlan_type}:{i.name}:{i.vlan_id}')
                sys.exit(1)

            #=====================================================
            # Dictionary of IP Settings for Server
            #=====================================================
            def ipdict(i, ipindex):
                idict = dict(
                    gateway  = i.gateway,
                    ip       = i.server[ipindex],
                    netmask  = i.netmask,
                    prefix   = i.prefix,
                    vlan     = i.vlan_id,
                    vlan_name= i.name,
                )
                return idict
            
            #=====================================================
            # Obtain the Index of the Starting IP Address
            #=====================================================
            ipindex = kwargs.inband.server.index(p.inband_start)
            if 'compute.Blade' in kwargs.server_profiles[name].object_type:
                ipindex = ipindex + int(kwargs.server_profiles[name].slot) - 1

            #=====================================================
            # Loop thru the VLANs
            #=====================================================
            for i in kwargs.vlans:
                if re.search('(inband|iscsi|migration|nfs|nvme)', i.vlan_type):
                    if not i.server: error_server_range(i)
                    if not len(i.server) >= ipindex: error_ip_range(i)
                if re.search('(iscsi|nvme)', i.vlan_type):
                    if not kwargs.server_profiles[name].get(i.vlan_type):
                        kwargs.server_profiles[name].update({i.vlan_type:[]})
                    idict = ipdict(i, ipindex)
                    kwargs.server_profiles[name][i.vlan_type].append(idict)
                if re.search('(inband|migration|nfs)', i.vlan_type):
                    idict = ipdict(i, ipindex)
                    kwargs.server_profiles[name][i.vlan_type] = idict
            return kwargs
        
        #=====================================================
        # Build Server Profiles
        #=====================================================
        if 'fc' in kwargs.dtype: t = 'fcp'
        else: t = 'iscsi'
        templates = []
        for k, v in kwargs.servers.items():
            templates.append(v.template)
        templates = numpy.unique(numpy.array(templates))
        for template in templates:
            polVars = dict(
                action                     = 'Deploy',
                create_from_template       = True,
                targets                    = [],
                ucs_server_profile_template= f'{t}-' + template
            )
            for k,v in kwargs.servers.items():
                if template == v.template:
                    if v.object_type == 'compute.Blade':
                        equipment_type= 'Chassis'
                        identifier    = v.chassis_id
                    else:
                        equipment_type= 'RackServer'
                        identifier    = v.server_id
                    for p in kwargs.domain.profiles:
                        if equipment_type == p.equipment_type and int(identifier) == int(p.identifier):
                            if equipment_type == 'RackServer':
                                pstart = p.profile_start
                            else:
                                suffix = int(p.suffix_digits)
                                pprefix= p.profile_start[:-(suffix)]
                                pstart = int(p.profile_start[-(suffix):])
                            break
                    if equipment_type == 'RackServer': name = pstart
                    else: name = f"{pprefix}{str(pstart+v.slot-1).zfill(suffix)}"

                    if template == template:
                        polVars['targets'].append(dict(
                            description  = f"{name} Server Profile.",
                            name         = name,
                            serial_number= k
                        ))
                        kwargs.server_profiles[name] = v
                        kwargs = server_profile_networks(name, p, kwargs)
                    
            polVars['targets']  = sorted(polVars['targets'], key=lambda item: item['name'])
            kwargs.class_path= f'profiles,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)

        kwargs.server_profiles = dict(sorted(kwargs.server_profiles.items()))
        for k, v in kwargs.server_profiles.items():
            polVars = {}
            for a, b in v.items():
                polVars[a] = b
            polVars = deepcopy(v)
            polVars.update(deepcopy({'name':k}))
            kwargs.class_path= f'wizard,server_profiles'
            kwargs = ezfunctions.ez_append(polVars, kwargs)

        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - SNMP
    #=============================================================================
    def snmp(self, kwargs):
        # Build Dictionary
        polVars = dict(
            description     = f'{kwargs.domain.policies.prefix}snmp Policy',
            enable_snmp     = True,
            name            = f'{kwargs.domain.policies.prefix}snmp',
            snmp_traps      = [],
            snmp_users      = [dict(
                auth_password    = 1,
                auth_type        = 'SHA',
                name             = kwargs.domain.policies.snmp.username,
                privacy_password = 1,
                privacy_type     = 'AES',
                security_level   = 'AuthPriv'
            )],
            system_contact  = kwargs.domain.policies.snmp.contact,
            system_location = kwargs.domain.policies.snmp.location,
        )
        for i in kwargs.domain.policies.snmp.servers:
            polVars['snmp_traps'].append(dict(
                destination_address = i,
                port                = 162,
                user                = kwargs.domain.policies.snmp.username
            ))

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,snmp'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        polVars.update({
            'description':f'{kwargs.domain.policies.prefix}snmp-domain Policy',
            'name':f'{kwargs.domain.policies.prefix}snmp-domain'
        })
        kwargs.class_path = f'policies,snmp'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Storage
    #=============================================================================
    def storage(self, kwargs):
        return kwargs
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['9508', 'Server']
        for i in plist:
            polVars = dict(
                description      = f'{kwargs.domain.policies.prefix}{i} {descr} Policy',
                name             = f'{kwargs.domain.policies.prefix}{i}',
                power_allocation = 8400,
                power_redundancy = 'Grid',
            )
            if i == 'Server': polVars.update({'power_restore':'LastState'})

            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Switch Control
    #=============================================================================
    def switch_control(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        if 'fc' in kwargs.dtype: switch_mode = kwargs.domain.switch_mode
        else: switch_mode = 'end-host'
        polVars = dict(
            description       = f'{kwargs.domain.policies.prefix}sw-ctrl {descr} Policy',
            fc_switching_mode = switch_mode,
            name              = f'{kwargs.domain.policies.prefix}sw-ctrl',
            vlan_port_count_optimization = True,
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,switch_control'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Syslog
    #=============================================================================
    def syslog(self, kwargs):
        # Build Dictionary
        polVars = dict(
            description = f'{kwargs.domain.policies.prefix}syslog Policy',
            local_logging = dict(
                minimum_severity = 'warning',
            ),
            name            = f'{kwargs.domain.policies.prefix}syslog',
            remote_logging      = [],
        )
        for i in kwargs.domain.policies.syslog.servers:
            polVars['remote_logging'].append(dict(
                enable           = True,
                hostname         = i,
                minimum_severity = 'informational',
            ))

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,syslog'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        polVars.update({
            'description':f'{kwargs.domain.policies.prefix}syslog-domain Policy',
            'name':f'{kwargs.domain.policies.prefix}syslog-domain'
        })
        kwargs.class_path = f'policies,syslog'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - System QoS
    #=============================================================================
    def system_qos(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{kwargs.domain.policies.prefix}qos {descr} Policy',
            classes     = [],
            name        = f'{kwargs.domain.policies.prefix}qos',
        )
        for k, v in kwargs.ezData['ezimm'].allOf[1].properties['systemQos'].items():
            cDict = {'priority':k}
            cDict.update(v)
            polVars['classes'].append(cDict)

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Templates - Server
    #=============================================================================
    def templates(self, kwargs):
        # Build Dictionary
        template_types = []
        server_profiles = []
        for k, v in kwargs.servers.items(): server_profiles.append(v.template)
        server_profiles = list(numpy.unique(numpy.array(server_profiles)))
        if 'fc' in kwargs.dtype: template_types.append('fcp')
        for i in kwargs.vlans:
            if i.vlan_type == 'iscsi':
                template_types.append('iscsi')
        template_types = list(numpy.unique(numpy.array(template_types)))
        fw = kwargs.firmware_policy_name
        for t in template_types:
            for p in server_profiles:
                bios_policy = p.split('-vic')[0] + '-virtual'
                bios_policy = bios_policy.replace('-tpm', '')
                if 'tpm' in p:
                    bios_policy = bios_policy + '-tpm'
                name = f'{t}-' + p
                if 'iscsi' in t: lcp = 'lcp-iscsi-vic-' + p.split('vic-')[1].replace('-', ':')
                else: lcp = 'lcp-vic-' + p.split('vic-')[1].replace('-', ':')
                scp = 'scp-vic-' + p.split('vic-')[1].replace('-', ':')
                polVars = dict(
                    bios_policy             = bios_policy,
                    boot_order_policy       = f'{kwargs.domain.policies.prefix}{t}-boot',
                    description             = f'{name} Server Template',
                    firmware_policy         = f'{kwargs.domain.policies.prefix}{fw}',
                    imc_access_policy       = f'{kwargs.domain.policies.prefix}kvm',
                    lan_connectivity_policy = f'{kwargs.domain.policies.prefix}{lcp}',
                    local_user_policy       = f'{kwargs.domain.policies.prefix}users',
                    name                    = name,
                    power_policy            = f'{kwargs.domain.policies.prefix}server',
                    san_connectivity_policy = f'',
                    serial_over_lan_policy  = f'{kwargs.domain.policies.prefix}sol',
                    snmp_policy             = f'{kwargs.domain.policies.prefix}snmp',
                    syslog_policy           = f'{kwargs.domain.policies.prefix}syslog',
                    uuid_pool               = f'{kwargs.domain.policies.prefix}uuid',
                    virtual_kvm_policy      = f'{kwargs.domain.policies.prefix}vkvm',
                    virtual_media_policy    = f'{kwargs.domain.policies.prefix}vmedia',
                )
                if 'M5' in p: polVars.pop('power_policy')
                if 'fcp' in t: polVars.update({'san_connectivity_policy': f'{kwargs.domain.policies.prefix}{scp}'})
                else: polVars.pop('san_connectivity_policy')
                
                # Add Policy Variables to immDict
                kwargs.class_path = f'{self.type},server'
                kwargs = ezfunctions.ez_append(polVars, kwargs)
        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Thermal
    #=============================================================================
    def thermal(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        for i in kwargs.chassis:
            polVars = dict(
                fan_control_mode = 'Balanced',
                description      = f'{kwargs.domain.policies.prefix}{i} {descr} Policy',
                name             = f'{kwargs.domain.policies.prefix}{i}',
            )

            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Pools - MAC
    #=============================================================================
    def uuid(self, kwargs):
        # Build Dictionary
        polVars = dict(
            assignment_order = 'sequential',
            description      = f'{kwargs.domain.policies.prefix}uuid Pool',
            name             = f'{kwargs.domain.policies.prefix}uuid',
            prefix           = '000025B5-0000-0000',
            uuid_blocks      = [{
                'from':f'{kwargs.domain.pools.prefix}00-000000000000',
                'size':1024
            }],
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'pools,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Virtual KVM
    #=============================================================================
    def virtual_kvm(self, kwargs):
        # Build Dictionary
        polVars = dict(
            allow_tunneled_vkvm = True,
            description         = f'{kwargs.domain.policies.prefix}vkvm Virtual KVM Policy',
            name                = f'{kwargs.domain.policies.prefix}vkvm',
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - Virtual Media
    #=============================================================================
    def virtual_media(self, kwargs):
        descr = (self.type.replace('_', ' ')).title()
        # Build Dictionary
        polVars = dict(
            description         = f'{kwargs.domain.policies.prefix}vmedia {descr} Policy',
            name                = f'{kwargs.domain.policies.prefix}vmedia',
        )

        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - VLAN
    #=============================================================================
    def vlan(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).upper()
        polVars = dict(
            description = f'{kwargs.domain.policies.prefix}vlans {descr} Policy',
            name        = f'{kwargs.domain.policies.prefix}vlans',
            vlans       = [dict(
                auto_allow_on_uplinks = True,
                multicast_policy      = 'mcast',
                name                  = 'default',
                native_vlan           = True,
                vlan_list             = 1
            )]
        )
        for i in kwargs.vlans:
            if not int(i.vlan_id) == 1:
                polVars['vlans'].append(dict(
                    multicast_policy = 'mcast',
                    name             = i['name'],
                    vlan_list        = i.vlan_id
                ))
        for i in kwargs.ranges:
            vfull = ezfunctions.vlan_list_full(i.vlan_list)
            if 1 in vfull: vfull.remove(1)
            vlan_list = ezfunctions.vlan_list_format(vfull)
            polVars['vlans'].append(dict(
                multicast_policy = 'mcast',
                name             = i['name'],
                vlan_list        = vlan_list
            ))
        # Add Policy Variables to immDict
        kwargs.class_path = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policy - VSAN
    #=============================================================================
    def vsan(self, kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).upper()
        if kwargs.swmode == 'end-host': vsan_scope = 'Uplink'
        else: vsan_scope = 'Storage'
        for i in kwargs.vsans:
            polVars = dict(
                description = f'{kwargs.domain.policies.prefix}vsan-{i} {descr} Policy',
                name        = f'{kwargs.domain.policies.prefix}vsan-{i}',
                vsans       = [dict(
                    fcoe_vlan_id = i,
                    name         = f'{kwargs.domain.policies.prefix}vsan-{i}',
                    vsan_id      = i,
                    vsan_scope   = vsan_scope
                )]
            )

            # Add Policy Variables to immDict
            kwargs.class_path = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, kwargs)
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


#=======================================================
# Wizard Class
#=======================================================
class wizard(object):
    def __init__(self, type):
        self.type = type

    #=============================================================================
    # Function - Converged Stack - Build IMM Domain Dictionaries
    #=============================================================================
    def build_imm_domain(self, kwargs):
        #==================================
        # Configure Domain Policies
        #==================================
        policy_list = kwargs.ezData['ezimm'].allOf[1].properties['list_domains'].enum
        policy_list.remove('domain')
        policy_list.insert(0, 'ethernet_network_group')
        policy_list.sort()
        if not re.search('fc(-nvme)?', kwargs.dtype): policy_list.pop('vsan')
        for k, v in kwargs.imm.domain.items():
            for i in policy_list:
                kwargs.domain = v
                kwargs.domain.name = k
                if kwargs.domain.policies.prefix == None:
                    kwargs.domain.policies.prefix = ''
                kwargs = eval(f'imm(i).{i}(kwargs)')

        #==================================
        # Configure Domain Profiles
        #==================================
        kwargs = imm('domain').domain(kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        kwargs.policy_list = policy_list
        return kwargs


    #=============================================================================
    # Function - Converged Stack - Build IMM Dictionaries
    #=============================================================================
    def build_imm_servers(self, kwargs):
        #==================================
        # Configure IMM Pools
        #==================================
        pool_list = list(kwargs.ezData['pools'].allOf[1].properties.keys())
        pool_list.remove('resource')
        for k, v in kwargs.imm.domain.items():
            for i in pool_list:
                kwargs.domain = v
                kwargs.domain.name = k
                if kwargs.domain.policies.prefix == None:
                    kwargs.domain.policies.prefix = ''
                kwargs = eval(f'imm(i).{i}(kwargs)')

        #==================================
        # Modify the Policy List
        #==================================
        policy_list = list((kwargs.ezData.policies.allOf[1].properties).keys())
        ezData = kwargs.ezData['ezimm'].allOf[1].properties
        pop_list = ezData['converged.pop_list'].enum
        for i in pop_list: policy_list.remove(i)
        pop_list = ezData['converged.fc_pop_list'].enum

        if re.search('fc(-nvme)?', kwargs.dtype):
            if kwargs.sw_mode == 'end-host': policy_list.remove('fc_zone')
        else:
            for i in pop_list: policy_list.remove(i)

        if 'iscsi_boot' in policy_list:
            policy_list.remove('iscsi_static_target')
            policy_list.insert((policy_list.index('iscsi_boot') - 1), 'iscsi_static_target')
        pop_list = ['ethernet_network_group', 'snmp', 'syslog']
        for i in pop_list:
            if kwargs.immDict.orgs.get(kwargs.org):
                if kwargs.immDict.orgs[kwargs.org].get('policies'):
                    if kwargs.immDict.orgs[kwargs.org].policies.get(i):
                        policy_list.remove(i)
        kwargs.policy_list = policy_list

        #==================================
        # Configure IMM Policies
        #==================================
        for k, v in kwargs.imm.domain.items():
            kwargs.domain = v
            kwargs.domain.name = k
            if kwargs.domain.policies.prefix == None:
                kwargs.domain.policies.prefix = ''
            #kwargs = imm('compute_environment').compute_environment(kwargs)
            #print(kwargs.chassis.toDict())
            #print(kwargs.servers.toDict())
            kwargs.chassis = DotMap({'ucsb-5108-ac2': [{'domain': 'r142c', 'identity': 1, 'serial': 'FOX2528PK0Z'}], 'ucsx-9508': [{'domain': 'r142c', 'identity': 2, 'serial': 'FOX2501P0BF'}]})
            kwargs.servers = DotMap({'FCH21427CHB': {'chassis_id': '1', 'chassis_moid': '63a1ec0d76752d31353e06dd', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M5', 'moid': '63c64eeb76752d3135626948', 'model': 'UCSB-B200-M5', 'object_type': 'compute.Blade', 'serial': 'FCH21427CHB', 'server_id': 0, 'slot': 7, 'template': 'M5-intel-vic-gen4-mlom', 'tpm': '', 'vics': [{'vic_gen': 'gen4', 'vic_slot': 'MLOM'}]}, 'FCH213271VU': {'chassis_id': '1', 'chassis_moid': '63a1ec0d76752d31353e06dd', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M5', 'moid': '63c6513e76752d313562f0cc', 'model': 'UCSB-B200-M5', 'object_type': 'compute.Blade', 'serial': 'FCH213271VU', 'server_id': 0, 'slot': 3, 'template': 'M5-intel-vic-gen4-mlom', 'tpm': '', 'vics': [{'vic_gen': 'gen4', 'vic_slot': 'MLOM'}]}, 'FCH222974YZ': {'chassis_id': '1', 'chassis_moid': '63a1ec0d76752d31353e06dd', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M5', 'moid': '63c6559676752d313564167f', 'model': 'UCSB-B200-M5', 'object_type': 'compute.Blade', 'serial': 'FCH222974YZ', 'server_id': 0, 'slot': 2, 'template': 'M5-intel-vic-gen4-mlom', 'tpm': '', 'vics': [{'vic_gen': 'gen4', 'vic_slot': 'MLOM'}]}, 'FLM2509002F': {'chassis_id': '1', 'chassis_moid': '63a1ec0d76752d31353e06dd', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M5', 'moid': '63c655c476752d31356420ff', 'model': 'UCSB-B200-M5', 'object_type': 'compute.Blade', 'serial': 'FLM2509002F', 'server_id': 0, 'slot': 8, 'template': 'M5-intel-vic-gen4-mlom', 'tpm': '', 'vics': [{'vic_gen': 'gen4', 'vic_slot': 'MLOM'}]}, 'FCH21427JG8': {'chassis_id': '1', 'chassis_moid': '63a1ec0d76752d31353e06dd', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M5', 'moid': '63c65d7276752d313565f3bc', 'model': 'UCSB-B200-M5', 'object_type': 'compute.Blade', 'serial': 'FCH21427JG8', 'server_id': 0, 'slot': 5, 'template': 'M5-intel-vic-gen4-mlom', 'tpm': '', 'vics': [{'vic_gen': 'gen4', 'vic_slot': 'MLOM'}]}, 'FCH243974V2': {'chassis_id': '2', 'chassis_moid': '63a1ec1076752d31353e0780', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M6', 'moid': '63a1ecb176752d31353e3720', 'model': 'UCSX-210C-M6', 'object_type': 'compute.Blade', 'serial': 'FCH243974V2', 'server_id': 0, 'slot': 8, 'template': 'M6-intel-tpm-vic-gen4-mlom', 'tpm': '-tpm', 'vics': [{'vic_gen': 'gen4', 'vic_slot': 'MLOM'}]}, 'FCH24397500': {'chassis_id': '2', 'chassis_moid': '63a1ec1076752d31353e0780', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M6', 'moid': '63a1ecb276752d31353e377d', 'model': 'UCSX-210C-M6', 'object_type': 'compute.Blade', 'serial': 'FCH24397500', 'server_id': 0, 'slot': 7, 'template': 'M6-intel-tpm-vic-gen4-mlom', 'tpm': '-tpm', 'vics': [{'vic_gen': 'gen4', 'vic_slot': 'MLOM'}]}, 'FCH243974WZ': {'chassis_id': '2', 'chassis_moid': '63a1ec1076752d31353e0780', 'cpu': 'intel', 'domain': 'r142c', 'firmware': '5.1(0.230054)', 'gen': 'M6', 'moid': '63a1ed0476752d31353e4938', 'model': 'UCSX-210C-M6', 'object_type': 'compute.Blade', 'serial': 'FCH243974WZ', 'server_id': 0, 'slot': 6, 'template': 'M6-intel-tpm-vic-gen4-mlom', 'tpm': '-tpm', 'vics': [{'vic_gen': 'gen4', 'vic_slot': 'MLOM'}]}})
            kwargs.pci_order = 0
            for i in policy_list:
                kwargs = eval(f'imm(i).{i}(kwargs)')

        kwargs.qtype_list = policy_list
        #=====================================================
        # Configure Templates/Chassis/Server Profiles
        #=====================================================
        profiles_list = ['templates', 'chassis', 'server']
        for p in profiles_list:
            kwargs = eval(f'imm(p).{p}(kwargs)')
        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Converged Stack - Build Storage Dictionaries
    #=============================================================================
    def build_netapp(self, kwargs):
        #=====================================================
        # Build NetApp Dictionaries
        #=====================================================
        plist = ['cluster']
        for name,items in kwargs.netapp.cluster.items():
            for i in plist:
                kwargs = eval(f'netapp.build(i).{i}(items, name, kwargs)')
        #==================================
        # Configure NetApp
        #==================================
        plist= ['cluster']
        for i in plist:
            kwargs = eval(f'netapp.api(i).{i}(kwargs)')

        # Add Policy Variables to immDict
        idict = kwargs.storage.toDict()
        for k, v in idict.items():
            for a, b in v.items():
                kwargs.class_path = f'storage,appliances'
                kwargs = ezfunctions.ez_append(b, kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Converged Stack - Credentials - DHCP - DNS - NTP Attributes
    #=============================================================================
    def dns_ntp(self, kwargs):
        #=====================================================
        # DHCP, DNS, NTP, Organization
        #=====================================================
        i = kwargs.immDict.wizard.protocols[0]
        kwargs.dns_servers = i.dns_servers
        kwargs.dns_domains = i.dns_domains
        kwargs.ntp_servers = i.ntp_servers
        kwargs.timezone    = i.timezone
        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Converged Stack - IMM Attributes
    #=============================================================================
    def imm(self, kwargs):
        #=====================================================
        # Intersight Attributes
        #=====================================================
        for item in kwargs.immDict.wizard.intersight:
            item = DotMap(item)
            kwargs.dtype  = item.deployment_type
            kwargs.org    = item.organization
            for i in item.domains:
                i = DotMap(i)
                kwargs.imm.pool.prefix    = item.pools.prefix
                kwargs.imm.policies       = item.policies
                kwargs.imm.domain[i.name] = DotMap(
                    eth_breakout_speed = i.eth_breakout_speed,
                    eth_uplinks        = i.eth_uplink_ports,
                    firmware           = item.server_firmware,
                    organization       = item.organization,
                    policies           = item.policies,
                    pools              = item.pools,
                    profiles           = i.profiles,
                    serial_numbers     = i.serial_numbers,
                    tags               = kwargs.ezData.tags
                )
                #==================================
                # Build Domain Network Dictionary
                #==================================
                fabrics = ['A', 'B']
                for x in range(0,2):
                    kwargs.network.imm[f'{i.name}-{fabrics[x]}'] = DotMap(
                        data_ports  = i.eth_uplink_ports,
                        data_speed  = i.eth_uplink_speed,
                        mgmt_port   = i.network.management,
                        network_port= i.network.data[x],
                        port_channel=True
                    )

                #==================================
                # Get Moids for Fabric Switches
                #==================================
                kwargs.method = 'get'
                kwargs.qtype = 'serial_number'
                kwargs.uri   = 'network/Elements'
                kwargs.names = kwargs.imm.domain[i.name].serial_numbers
                kwargs       = isight.api('serial_number').calls(kwargs)
                serial_moids = kwargs.pmoids
                serial       = kwargs.imm.domain[i.name].serial_numbers[0]
                kwargs.imm.domain[i.name].device_model     = serial_moids[serial]['model']
                kwargs.imm.domain[i.name].registered_device= serial_moids[serial]['registered_device']

                #=====================================================
                # Confirm if Fibre-Channel is in Use
                #=====================================================
                if re.search('(fc|fc-nvme)', kwargs.dtype):
                    kwargs.imm.domain[i.name].fcp_uplink_ports= i.fcp_uplink_ports
                    kwargs.imm.domain[i.name].fcp_uplink_speed= i.fcp_uplink_speed
                    kwargs.imm.domain[i.name].switch_mode     = i.switch_mode
                    kwargs.imm.domain[i.name].vsans           = i.vsans
        
        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Converged Stack - NetApp Attributes
    #=============================================================================
    def netapp(self, kwargs):
        #==================================
        # Build Cluster Dictionary
        #==================================
        kwargs.netapp.cluster = DotMap()
        kwargs.storage = DotMap()
        for item in kwargs.immDict.wizard.netapp:
            for i in item.clusters:
                kwargs.storage[i.name][i.svm.name] = DotMap(
                    cluster= i.name,
                    name   = f"{i.name}:{i.svm.name}",
                    svm    = i.svm.name,
                    vendor = 'netapp'
                )
                cname = i.name
                sname = i.svm.name
                rootv = (i.svm.name).replace('-', '_').lower() + '_root'
                kwargs.netapp.cluster[cname] = DotMap(
                    autosupport= item.autosupport,
                    banner     = item.login_banner,
                    host_prompt= r'[\w]+::>',
                    nodes      = i.nodes,
                    protocols  = kwargs.protocols,
                    snmp       = item.snmp,
                    svm        = DotMap(
                        agg1     = i.nodes.node01.replace('-', '_').lower() + '_1',
                        agg2     = i.nodes.node02.replace('-', '_').lower() + '_1',
                        name     = i.svm.name,
                        m01      = rootv + '_m01',
                        m02      = rootv + '_m02',
                        protocols= kwargs.protocols,
                        rootv    = rootv,
                        volumes  = i.svm.volumes
                    ),
                    username = item.username
                )
                kwargs.netapp.cluster[cname].nodes.node_list = [i.nodes.node01, i.nodes.node02]
                #==================================
                # Build Cluster Network Dictionary
                #==================================
                nodes = kwargs.netapp.cluster[cname].nodes.node_list
                for x in range(0,len(nodes)):
                    kwargs.network.storage[nodes[x]] = DotMap(
                        data_ports  = i.nodes.data_ports,
                        data_speed  = i.nodes.data_speed,
                        mgmt_port   = i.nodes.network.management,
                        network_port= i.nodes.network.data[x],
                        port_channel=True
                    )

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Build Policies - BIOS
    #=============================================================================
    def os_install(self, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section(self.type, 'Install')
        kwargs.org_moid= kwargs.org_moids[kwargs.org].moid
        kwargs.models  = []
        for i in  kwargs.immDict.orgs[kwargs.org].wizard.os_configuration:
            kwargs.models.append(i.model)
        kwargs.models   = list(numpy.unique(numpy.array(kwargs.models)))

        # TEMP FIX for Dev Environment - Remove
        kwargs.files_dir= '/mnt/c/Users/tyscott/Downloads/'
        dir_files = os.listdir(kwargs.files_dir)
        dir_files.sort()
        file_types = ['Broadcom', 'Custom-Cisco','NetAppNas', 'nenic', 'nfnic', 'ucs-scu']
        for ftype in file_types:
            for f in dir_files:
                if os.path.isfile(kwargs.files_dir + os.sep + f):
                    if ftype in f: kwargs.files[ftype] = f

        kwargs.repo_server= socket.getfqdn()
        # TEMP FIX for Dev Environment - Remove
        kwargs.repo_server= 'rdp1.rich.ciscolabs.com'
        kwargs.repo_path  = '/'
        kwargs.scu_version= (kwargs.files['ucs-scu'].split('.iso')[0]).split('-')[2]
        kwargs.os_iso     = kwargs.files['Custom-Cisco']
        kwargs.os_name    = re.search('(ESXi-\\d.\\d(\\.\\d)?)', kwargs.files['Custom-Cisco']).group(1)
        jvars = kwargs.ezData.operatingSystem.allOf[1].properties[kwargs.os_name]
        kwargs.os_config  = jvars.config
        kwargs.os_vendor  = jvars.vendor
        kwargs.os_version = jvars.version

        #==================================
        # Get ESXi Root Password
        #==================================
        kwargs.sensitive_var = 'esxi_password'
        kwargs = ezfunctions.sensitive_var_value(kwargs)
        kwargs.esxi_password = kwargs.var_value

        #==================================
        # Get Org Software Repo
        #==================================
        kwargs.method    = 'get'
        kwargs.names     = ['user-catalog']
        kwargs.qtype     = 'org_repository'
        kwargs.uri       = 'softwarerepository/Catalogs'
        kwargs           = isight.api(kwargs.qtype).calls(kwargs)
        kwargs.repository= kwargs.pmoids['user-catalog'].moid

        #==================================
        # Get Existing SCU Repositories
        #==================================
        kwargs.api_filter= f"Catalog.Moid eq '{kwargs.repository}'"
        kwargs.names     = [f'scu-{kwargs.scu_version}']
        kwargs.qtype     = 'server_configuration_utility'
        kwargs.uri       = 'firmware/ServerConfigurationUtilityDistributables'
        kwargs           = isight.api(kwargs.qtype).calls(kwargs)

        #==================================
        # Create/Patch SCU Repo apiBody
        #==================================
        kwargs.apiBody = server_config_utility_repo(kwargs)
        if kwargs.pmoids.get(kwargs.apiBody['Name']):
            kwargs.method = 'patch'
            kwargs.pmoid     = kwargs.pmoids[kwargs.apiBody['Name']].moid
        else: kwargs.method = 'post'
        kwargs    = isight.api(self.type).calls(kwargs)
        kwargs.scu_moid = kwargs.pmoid

        #==================================
        # Test Repo URL for File
        #==================================
        repo_url = f'https://{kwargs.repo_server}{kwargs.repo_path}{kwargs.scu_iso}'
        try:
            r = requests.head(repo_url, allow_redirects=True, verify=False, timeout=10)
        except requests.RequestException as e:
            prRed(f"!!! ERROR !!!\n  Exception when calling {repo_url}:\n {e}\n")
            sys.exit(1)


        #==================================
        # Confirm if OS Repo Exists
        #==================================
        kwargs.method    = 'get'
        kwargs.names     = [kwargs.os_name]
        kwargs.qtype     = 'operating_system'
        kwargs.uri       = 'softwarerepository/OperatingSystemFiles'
        kwargs           = isight.api(kwargs.qtype).calls(kwargs)
        kwargs.os_repos  = kwargs.pmoids

        #==================================
        # Get OS Catalog
        #==================================
        kwargs.api_filter= f"Name eq 'shared'"
        kwargs.method    = 'get'
        kwargs.qtype     = 'os_catalog'
        kwargs.uri       = 'softwarerepository/OperatingSystemFiles'
        kwargs           = isight.api(kwargs.qtype).calls(kwargs)
        kwargs.os_catalog= kwargs.pmoids.shared.moid
        kwargs.pop('api_filter')

        #==================================
        # Create/Patch OS Repo apiBody
        #==================================
        kwargs.apiBody = os_software_repo(kwargs)
        if kwargs.pmoids.get(kwargs.apiBody['Name']):
            kwargs.method = 'patch'
            kwargs.pmoid     = kwargs.pmoids[kwargs.apiBody['Name']].moid
        else: kwargs.method = 'post'

        kwargs = isight.api(self.type).calls(kwargs)
        kwargs.os_moid = kwargs.pmoid
        repo_url = f'https://{kwargs.repo_server}{kwargs.repo_path}{kwargs.os_iso}'

        #==================================
        # Test Repo URL for File
        #==================================
        try:
            r = requests.head(repo_url, allow_redirects=True, verify=False, timeout=10)
        except requests.RequestException as e:
            prRed(f"!!! ERROR !!!\n  Exception when calling {repo_url}:\n {e}\n")
            sys.exit(1)
        #size = r.headers.get('content-length', -1)

        #==========================================
        # Deploy Operating System for each Profile
        #==========================================
        kwargs.san_target = kwargs.immDict.orgs[kwargs.org].storage.appliances[0].wwpns.a[0].wwpn

        # TEMP FIX for cabling issue - Remove
        kwargs.san_target = kwargs.immDict.orgs[kwargs.org].storage.appliances[0].wwpns.a[1].wwpn
        print(json.dumps(kwargs.immDict.orgs[kwargs.org].wizard.os_configuration, indent=4))
        for i in kwargs.immDict.orgs[kwargs.org].wizard.os_configuration:
            for k, v in i.items():
                kwargs.server_profiles[i.name][k] = v
        
        for k,v in kwargs.server_profiles.items():
            indx           = [e for e, d in enumerate(v.macs) if 'mgmt-a' in d.values()][0]
            kwargs.mgmt_mac= v.macs[indx].mac
            kwargs.fqdn    = k + '.' + kwargs.dns_domains[0]
            if re.search('(esx03)', k):
                kwargs.apiBody = os_installation_body(k, v, kwargs)
                kwargs.method= 'post'
                kwargs.qtype = self.type
                kwargs.uri   = 'os/Installs'
                prGreen(f"      * host {k}: initiator: {v.wwpns[0].wwpn}\n"\
                        f"        target: {kwargs.san_target}\n"\
                        f"        mac: {kwargs.mgmt_mac}")
                kwargs = isight.api(self.type).calls(kwargs)
                kwargs.server_profiles[k].os_install = { 'moid': kwargs.pmoid, 'workflow': ''}

        time.sleep(60)
        #=================================================
        # Monitor OS Installation until Complete
        #=================================================
        for k,v in  kwargs.server_profiles.items():
            if re.search('(esx03)', k):
                kwargs.api_filter= f"Name eq '{k}-osinstall'"
                kwargs.method    = 'get'
                kwargs.qtype     = self.type
                kwargs.uri       = 'workflow/WorkflowInfos'
                kwargs           = isight.api(self.type).calls(kwargs)
                kwargs.pop('api_filter')
                v.os_install.workflow = kwargs.results[len(kwargs.results)-1]['WorkflowInfo'].Moid
                install_complete = False
                while install_complete == False:
                    kwargs.method= 'get_by_moid'
                    kwargs.pmoid = v.os_install.workflow
                    kwargs.qtype = 'workflow_info'
                    kwargs.uri   = 'workflow/WorkflowInfos'
                    kwargs = isight.api(self.type).calls(kwargs)
                    if kwargs.results.Status == 'COMPLETED':
                        install_complete = True
                        prGreen(f'    - Completed Operating System Installation for {k}.')
                    elif re.search('(FAILED|TERMINATED|TIME_OUT)', kwargs.results.Status):
                        kwargs.upgrade.failed.update({k:v.moid})
                        prRed(f'!!! FAILED !!! Operating System Installation for Server Profile {k} failed.')
                        install_complete = True
                    else:
                        progress= kwargs.results.Progress
                        status  = kwargs.results.Status
                        prCyan(f'      * Operating System Installation for {k}.')
                        prCyan(f'        Status is {status} Progress is {progress}, Waiting 120 seconds.')
                        time.sleep(120)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'Install')
        return kwargs

    #=============================================================================
    # Function - Build Server Identies for Zoning host/igroups
    #=============================================================================
    def server_identities(self, kwargs):
        #=====================================================
        # Get Server Profile Names and Moids
        #=====================================================
        kwargs.names = []
        for i in kwargs.immDict.orgs[kwargs.org].wizard.server_profiles:
            kwargs.server_profiles[i.name] = DotMap()
            for k, v in i.items():
                kwargs.server_profiles[i.name][k] = v
            kwargs.server_profiles[i.name]['hardware_moid'] = i.moid
            kwargs.server_profiles[i.name].pop('moid')
            kwargs.names.append(i.name)
        kwargs.names.sort()
        kwargs.server_profiles = DotMap(dict(sorted(kwargs.server_profiles.items())))
        
        kwargs.method = 'get'
        kwargs.qtype  = 'server'
        kwargs.uri    = 'server/Profiles'
        kwargs        = isight.api(kwargs.ptype).calls(kwargs)
        for k, v in kwargs.pmoids.items():
            kwargs.server_profiles[k].moid = v.moid
        
        for k, v in kwargs.server_profiles.items():
            kwargs.method    = 'get'
            kwargs.api_filter= f"Profile.Moid eq '{v.moid}'"
            kwargs.qtype = 'vnics'
            kwargs.uri   = 'vnic/EthIfs'
            kwargs = isight.api(kwargs.qtype).calls(kwargs)
            r = kwargs.results
            mac_list = []
            kwargs.server_profiles[k].macs = []
            kwargs.eth_moids = []
            for s in r:
                s = DotMap(s)
                kwargs.eth_moids.append(s.FabricEthNetworkGroupPolicy[0].Moid)
                mac_list.append(dict(
                    mac   = s.MacAddress,
                    name  = s.Name,
                    order = s.Order,
                    switch= s.Placement.SwitchId,
                    vgroup= s.FabricEthNetworkGroupPolicy[0].Moid
            ))
            kwargs.server_profiles[k].macs = sorted(mac_list, key=lambda k: (k['order']))
        
            #=====================================================
            # Get WWPN's for vHBAs and Add to Profile Map if fc
            #=====================================================
            if 'fc' in kwargs.dtype:
                kwargs.api_filter= f"Profile.Moid eq '{v.moid}'"
                kwargs.qtype     = 'vhbas'
                kwargs.uri       = 'vnic/FcIfs'
                kwargs = isight.api(kwargs.qtype).calls(kwargs)
                r = kwargs.results
                wwpn_list = []
                for s in r:
                    s = DotMap(s)
                    wwpn_list.append(dict(
                        switch= s.Placement.SwitchId,
                        name  = s.Name,
                        order = s.Order,
                        wwpn  = s.Wwpn
                ))
                kwargs.server_profiles[k].wwpns = (sorted(wwpn_list, key=lambda k: (k['order'])))
        
            #=====================================================
            # Get IQN for Host and Add to Profile Map if iscsi
            #=====================================================
            if re.search('(iscsi|nvme-tcp)', kwargs.dtype):
                kwargs.api_filter= f"Profile.Moid eq '{v.moid}'"
                kwargs.method    = 'get'
                kwargs.api_filter= f"AssignedToEntity.Moid eq '{v.moid}'"
                kwargs.qtype     = 'iqn'
                kwargs.uri       = 'iqnpool/Pools'
                kwargs = isight.api(kwargs.qtype).calls(kwargs)
                r = DotMap(kwargs.results)
                kwargs.server_profiles[k].iqn = r.IqnId
        kwargs.pop('api_filter')
        kwargs.server_profile = DotMap(kwargs.server_profiles)

        # Query API for Ethernet Network Policies and Add to Server Profile Dictionaries
        kwargs.eth_moids = numpy.unique(numpy.array(kwargs.eth_moids))
        kwargs.method= 'get_by_moid'
        kwargs.qtype = 'ethernet_network_group'
        kwargs.uri   = 'fabric/EthNetworkGroupPolicies'
        server_settings = deepcopy(kwargs.server_profiles)
        for i in kwargs.eth_moids:
            kwargs.pmoid = i
            isight.api(kwargs.qtype).calls(kwargs)
            results = DotMap(kwargs.results)
            for k, v in server_settings.items():
                for e in v.macs:
                    if e.vgroup == results.Moid:
                        vgroup = e.vgroup
                        indx = [e for e, d in enumerate(v.macs) if vgroup in d.values()]
                        for ix in indx:
                            kwargs.server_profiles[k].macs[ix]['vlan_group']= results.Name
                            kwargs.server_profiles[k].macs[ix]['allowed']   = results.VlanSettings.AllowedVlans
                            kwargs.server_profiles[k].macs[ix]['native']    = results.VlanSettings.NativeVlan


        #=====================================================
        # Run Lun Creation Class
        #=====================================================
        #kwargs = netapp.build('lun').lun(kwargs)

        for k, v in kwargs.server_profiles.items():
            polVars = v.toDict()

            # Add Policy Variables to immDict
            kwargs.class_path = f'wizard,os_configuration'
            kwargs = ezfunctions.ez_append(polVars, kwargs)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


    #=============================================================================
    # Function - Converged Stack - VLAN Attributes
    #=============================================================================
    def vlans(self, kwargs):
        protocols   = []
        kwargs.vlans = []
        for i in kwargs.immDict.wizard.vlans:
            #==================================
            # Add i.vlan_type to protocols
            #==================================
            if re.search('(iscsi|nfs|nvme)', i.vlan_type):
                if 'nvme' in i.vlan_type: protocols.append('nvme_of')
                else: protocols.append(i.vlan_type)

            #==================================
            # Build VLAN Dictionary
            #==================================
            netwk = '%s' % ipaddress.IPv4Network(i.network, strict=False)
            vDict = DotMap(
                configure_l2= i.configure_l2,
                configure_l3= i.configure_l3,
                gateway     = i.network.split('/')[0],
                name        = i.name,
                netmask     = ((ipaddress.IPv4Network(netwk)).with_netmask).split('/')[1],
                network     = netwk,
                prefix      = i.network.split('/')[1],
                switch_type = i.switch_type,
                vlan_id     = i.vlan_id,
                vlan_type   = i.vlan_type,
            )
            def iprange(xrange):
                ipsplit = xrange.split('-')
                ip1 = ipsplit[0]
                ips = []
                a = ip1.split('.')
                for x in range(int(ip1.split('.')[-1]), int(ipsplit[1])+1):
                    ipaddress = f'{a[0]}.{a[1]}.{a[2]}.{x}'
                    ips.append(ipaddress)
                return ips
            if i.ranges.get('controller'): vDict.controller = iprange(i.ranges.controller)
            if i.ranges.get('pool') and re.search('(inband|ooband)', i.vlan_type):
                vDict.pool = iprange(i.ranges.pool)
            if i.ranges.get('server'): vDict.server = iprange(i.ranges.server)
            kwargs.vlans.append(vDict)

        #==================================
        # Build VLAN Ranges Dictionary
        #==================================
        kwargs.ranges = []
        for i in kwargs.immDict.wizard.vlan_ranges:
            kwargs.ranges.append(DotMap(
                configure_l2= i.configure_l2,
                name        = i.name_prefix,
                vlan_list   = i.vlan_range
            ))

        #==================================
        # Build inband|nfs|ooband Dict
        #==================================
        for i in kwargs.vlans:
            if re.search('(inband|nfs|ooband)', i.vlan_type):
                kwargs[i.vlan_type] = i

        #==================================
        # Build Protocols Dictionary
        #==================================
        if 'fc' in kwargs.dtype: protocols.append('fcp')
        protocols = list(numpy.unique(numpy.array(protocols)))
        kwargs.protocols = []
        for i in protocols: kwargs.protocols.append(i)

        #=====================================================
        # Return kwargs and kwargs
        #=====================================================
        return kwargs


#=======================================================
# IMM Class
#=======================================================
class fw_os(object):
    def __init__(self, type):
        self.type = type

    #=============================================================================
    # Function - Build Policies - BIOS
    #=============================================================================
    def firmware(self, kwargs):
        #=====================================================
        # Load Variables and Send Begin Notification
        #=====================================================
        validating.begin_section(self.type, 'Install')
        kwargs.models = []
        for k,v in  kwargs.server_profiles.items():
            kwargs.models.append(v['model'])
        kwargs.models = list(numpy.unique(numpy.array(kwargs.models)))
        #==================================
        # Get CCO Password and Root
        #==================================
        kwargs.sensitive_var = 'cco_password'
        kwargs = ezfunctions.sensitive_var_value(kwargs)
        kwargs.cco_password = kwargs['var_value']
        #==================================
        # Get Firmware Moids
        #==================================
        kwargs.method = 'get'
        kwargs.qtype = 'distributables'
        kwargs.uri = self.type
        kwargs.fw_version = '5.1(0.230054)'
        sw_moids = {}
        for m in kwargs.models:
            kwargs.api_filter = f"Version eq '{kwargs.fw_version}' and contains(SupportedModels, '{m}')"
            kwargs = isight.api(self.type).calls(kwargs)
            sw_moids.update({m:{'Moid':kwargs.results[0].Moid}})
        kwargs.pop('api_filter')
        #==================================
        # Software Repository Auth
        #==================================
        kwargs.apiBody = {
            'object_type': 'softwarerepository.Authorization',
            'password': kwargs.cco_password,
            'repository_type': 'Cisco',
            'user_id': kwargs.cco_user
        }
        kwargs.method = 'post'
        kwargs.qtype    = 'auth'
        kwargs.uri   = 'firmware'
        kwargs = isight.api(self.type).calls(kwargs)
        #==================================
        # Software Eula
        #==================================
        kwargs.method = 'get_by_moid'
        kwargs.pmoid     = kwargs.results[0]['AccountMoid']
        kwargs.qtype    = 'eula'
        kwargs.uri   = 'firmware'
        kwargs = isight.api(self.type).calls(kwargs)
        if not kwargs.results:
            kwargs.apiBody   = {'class_id': 'firmware.Eula', 'object_type': 'firmware.Eula'}
            kwargs.method = 'post'
            kwargs = isight.api(self.type).calls(kwargs)
        #==================================
        # Upgrade Firmware
        #==================================
        for k,v in  kwargs.server_profiles.items():
            #==================================
            # Check Firmware Version
            #==================================
            if v.firmware == kwargs.fw_version:
                prGreen(f'Server Profile {k} - Server {v.serial} running Target Firmware {v.firmware}.')
            else:
                kwargs.apiBody = {
                    'class_id': 'firmware.Upgrade',
                    'direct_download': {
                        'class_id': 'firmware.DirectDownload',
                        'object_type': 'firmware.DirectDownload',
                        'upgradeoption': 'upgrade_full'
                    },
                    'distributable': {
                        'class_id': 'mo.MoRef',
                        'moid': sw_moids[v.model].Moid,
                        'object_type': 'firmware.Distributable'
                    },
                    'network_share': {'object_type': 'firmware.NetworkShare'},
                    'object_type': 'firmware.Upgrade',
                    'server': {
                        'class_id': 'mo.MoRef',
                        'moid': v.moid,
                        'object_type': v.object_type
                    },
                    'upgrade_type': 'direct_upgrade',
                }
                #==================================
                # Upgrade Firmware
                #==================================
                kwargs.method = 'post'
                kwargs.qtype = 'upgrade'
                kwargs.server = k
                kwargs.serial = v.serial
                kwargs.uri = self.type
                kwargs = isight.api(self.type).calls(kwargs)
                if kwargs['running']:
                    kwargs.method = 'get'
                    kwargs.api_filter = f"Server.Moid eq '{v.moid}'"
                    kwargs.srv_moid  = v.moid
                    kwargs = isight.api(self.type).calls(kwargs)
                    kwargs.pop('api_filter')
                    kwargs.upgrade[k].moid   = kwargs.pmoids[v.moid].Moid
                    kwargs.upgrade[k].status = kwargs.pmoids[v.moid].UpgradeStatus.Moid
                else:
                    kwargs.upgrade[k].moid   = kwargs.results.Moid
                    kwargs.upgrade[k].status = kwargs.results.UpgradeStatus.Moid
        #==================================
        # Power Cycle the Server
        #==================================
        #def power_cycle(v, kwargs):
        #    kwargs.method    = 'get'
        #    kwargs.api_filter= f"Server.Moid eq '{v.moid}'"
        #    kwargs.qtype     = 'server_settings'
        #    kwargs.uri       = 'compute/ServerSettings'
        #    kwargs = isight.api('server').calls(kwargs)
        #    pmoid = kwargs['pmoid']
        #    kwargs.pop('api_filter')
        #    kwargs.apiBody   = {'AdminPowerState': 'PowerCycle'}
        #    kwargs.method = 'patch'
        #    kwargs = isight.api('server').calls(kwargs)
        #    return kwargs
        #=================================================
        # Monitor Firmware Upgrade until Complete
        #=================================================
        for k, v in  kwargs.server_profiles.items():
            if not v.firmware == kwargs.fw_version:
                upgrade_complete = False
                while upgrade_complete == False:
                    kwargs.method = 'get_by_moid'
                    kwargs.pmoid     = kwargs.upgrade[k].status
                    kwargs.qtype    = 'status'
                    kwargs.uri   = self.type
                    kwargs = isight.api(self.type).calls(kwargs)
                    if kwargs.results['Overallstatus'] == 'success':
                        upgrade_complete = True
                        prGreen(f'    - Completed Firmware Upgrade for {k}.')
                    elif kwargs.results['Overallstatus'] == 'failed':
                        kwargs.upgrade.failed.update({k:v.moid})
                        prRed(f'!!! FAILED !!! Firmware Upgrade for Server Profile {k}: Server {v.serial} failed.')
                        upgrade_complete = True
                    else: 
                        prCyan(f'      * Firmware Upgrade still ongoing for {k}.  Waiting 120 seconds.')
                        time.sleep(120)

        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'Install')
        return kwargs

#=============================================================================
# Function - Build apiBody for Operating System Installation
#=============================================================================
def os_installation_body(k, v, kwargs):
    apiBody = {
        'Answers': {
            'Hostname': kwargs.fqdn,
            'IpConfigType': 'static',
            'IpConfiguration': {
                'IpV4Config': {
                    'Gateway': v.inband.gateway,
                    'IpAddress': v.inband.ip,
                    'Netmask': v.inband.netmask,
                    'ObjectType': 'comm.IpV4Interface'
                }, 'ObjectType': 'os.Ipv4Configuration',
            },
            "IsRootPasswordCrypted": False,
            'Nameserver': kwargs.dns_servers[0],
            'NetworkDevice': kwargs.mgmt_mac,
            'ObjectType': 'os.Answers',
            'RootPassword': kwargs.esxi_password,
            'Source': 'Template'
        },
        'ConfigurationFile': { 'Moid': kwargs.os_config,
            'ObjectType': 'os.ConfigurationFile',
        },
        'image': { 'Moid': kwargs.os_moid,
            'ObjectType': 'softwarerepository.OperatingSystemFile',
        },
        'install_method': 'vMedia',
        'install_target': {
            'InitiatorWwpn': v.wwpns[0].wwpn,
            'LunId': 0,
            'ObjectType': 'os.FibreChannelTarget',
            'TargeWwpn': kwargs.san_target
        },
        'Name': f'{k}-osinstall',
        'ObjectType': 'os.Install',
        'organization': { 'Moid': kwargs.org_moid,
            'ObjectType': 'organization.Organization',
        },
        'OsduImage': {
            'Moid': kwargs.scu_moid,
            'ObjectType': 'firmware.ServerConfigurationUtilityDistributable',
        },
        'OverrideSecureBoot': True,
        'Server': { 'Moid': v.moid, 'ObjectType': v.object_type}
    }
    return apiBody

#=============================================================================
# Function - Build apiBody for Operating System Software Repository
#=============================================================================
def os_software_repo(kwargs):
    apiBody = { 'Catalog': { 'Moid': kwargs.repository,
            'ObjectType': 'softwarerepository.Catalog'
        },
        'Description': f'{kwargs.os_name} Server Configuration Utility',
        'Name': kwargs.os_name,
        'ObjectType': 'softwarerepository.OperatingSystemFile',
        'Source': {
            'LocationLink': f'https://{kwargs.repo_server}{kwargs.repo_path}{kwargs.os_iso}',
            'ObjectType': 'softwarerepository.HttpServer',
        },
        'Vendor': kwargs.os_vendor, 'Version': kwargs.os_version
    }
    return apiBody

#=============================================================================
# Function - Build apiBody for Server Configuration Utility Repository
#=============================================================================
def server_config_utility_repo(kwargs):
    apiBody = {
        'Catalog': { 'Moid': kwargs.repository,
            'ObjectType': 'softwarerepository.Catalog'
        },
        'Description': f'scu-{kwargs.scu_version} Server Configuration Utility',
        'Name': f'scu-{kwargs.scu_version}',
        'ObjectType': 'firmware.ServerConfigurationUtilityDistributable',
        'Source': {
            'LocationLink': f'https://{kwargs.repo_server}{kwargs.repo_path}{kwargs.scu_iso}',
            'ObjectType': 'softwarerepository.HttpServer',
        },
        'SupportedModels': kwargs.models,
        'Vendor': 'Cisco', 'Version': kwargs.scu_version
    }
    return apiBody

#=====================================================
# Print Color Functions
#=====================================================
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk))
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
