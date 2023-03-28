#!/usr/bin/env python3

#=============================================================================
# Source Modules
#=============================================================================
from copy import deepcopy
from dotmap import DotMap
import ipaddress
import json
import numpy
import re
import sys
import validating

sys.path.insert(0, './classes')
from classes import ezfunctions
from classes import netapp
from classes import nxos
import isdk
#=====================================================================================
# Please Refer to the "Notes" in the relevant column headers in the input Spreadhseet
# for detailed information on the Arguments used by this Class.
#=====================================================================================
#=======================================================
# IMM Class
#=======================================================
class imm(object):
    def __init__(self, type):
        self.type = type

    #=============================================================================
    # Function - Build Policies - BIOS
    #=============================================================================
    def bios(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).upper()
        btemplates = []
        for i in pargs.server_profiles:
            gen = i['gen']
            tpm = i['tpm']
            if gen == 'M5' and tpm == 'True': btemplates.append('Virtualization_tpm')
            elif gen == 'M5': btemplates.append('Virtualization')
            elif re.search('M(6|7)', gen) and tpm == 'True': btemplates.append(f'{gen}_Virtualization_tpm')
            elif re.search('M(6|7)', gen): btemplates.append(f'{gen}_Virtualization')
        btemplates = numpy.unique(numpy.array(btemplates))
        for i in btemplates:
            polVars = dict(
                baud_rate           = 115200,
                console_redirection = f'serial-port-a',
                description         = f'{pargs.ppfx}{i} {descr} Policy',
                execute_disable_bit = f'disabled',
                lv_ddr_mode         = f'auto',
                name                = f'{pargs.ppfx}{i}',
                serial_port_aenable = f'enabled',
                terminal_type       = f'vt100',
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policies - BIOS
    #=============================================================================
    def boot_order(self, pargs, **kwargs):
        return kwargs, pargs
        # Build Dictionary
        btemlates = []
        for i in pargs.server_profiles:
            gen = i['gen']
            tpm = i['tpm']
            if gen == 'M5' and tpm == 'True': btemlates.append('Virtualization_tpm')
            elif gen == 'M5': btemlates.append('Virtualization')
            elif re.search('M(6|7)', gen) and tpm == 'True': btemlates.append(f'{gen}_Virtualization_tpm')
            elif re.search('M(6|7)', gen): btemlates.append(f'{gen}_Virtualization')
        btemplates = numpy.unique(numpy.array(btemplates))
        for i in btemplates:
            polVars = dict(
                baud_rate           = 115200,
                console_redirection = f'serial-port-a',
                description         = f'{pargs.ppfx}{i} BIOS Policy',
                execute_disable_bit = f'disabled',
                lv_ddr_mode         = f'auto',
                name                = f'{pargs.ppfx}{i}',
                serial_port_aenable = f'enabled',
                terminal_type       = f'vt100',
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Network Connectivity
    #=============================================================================
    def domain(self, pargs, **kwargs):
        # Build Dictionary
        polVars = dict(
            action                      = 'Deploy',
            description                 = f"{pargs.name} Domain Profile",
            name                        = pargs.name,
            network_connectivity_policy = f'{pargs.ppfx}dns',
            ntp_policy                  = f'{pargs.ppfx}ntp',
            port_policies               = [f'{pargs.name}-A', f'{pargs.name}-B'],
            serial_numbers              = pargs.serials,
            snmp_policy                 = f'{pargs.ppfx}snmp-domain',
            switch_control_policy       = f'{pargs.ppfx}sw-ctrl',
            syslog_policy               = f'{pargs.ppfx}syslog-domain',
            system_qos_policy           = f'{pargs.ppfx}qos',
            vlan_policies               = f'{pargs.ppfx}vlans',
        )
        if re.search('(fc|fc-nvme)', pargs.dtype):
            polVars.update({'vsan_policies': [f'{pargs.ppfx}vsan-{pargs.vsans[0]}', f'{pargs.ppfx}vsan-{pargs.vsans[1]}']})
        # Add Policy Variables to immDict
        kwargs['class_path'] = f'profiles,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Ethernet Adapter
    #=============================================================================
    def ethernet_adapter(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['16RxQs-4G', '16RxQs-5G', 'VMware', 'VMware-High-Trf']
        for i in plist:
            polVars = dict(
                adapter_template = i,
                description      = f'{pargs.ppfx}{i} {descr} Policy',
                name             = f'{pargs.ppfx}{i}',
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Ethernet Network Control
    #=============================================================================
    def ethernet_network_control(self, pargs, **kwargs):
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
                description          = f'{pargs.ppfx}{i} {descr} Policy',
                name                 = f'{pargs.ppfx}{i}',
                lldp_receive_enable  = lldpe,
                lldp_transmit_enable = lldpe,
                mac_register_mode    = 'nativeVlanOnly',
                mac_security_forge   = 'allow',
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Ethernet Network Control
    #=============================================================================
    def ethernet_network_group(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        vlans = []
        for i in pargs.vlans: vlans.append(i['vlan_id'])
        for i in pargs.ranges:
            vrange = ezfunctions.vlan_list_full(i['vlan_list'])
            vlans.extend(vrange)
        pargs.vlan = {}
        pargs.vlan['all_vlans'] = ezfunctions.vlan_list_format(numpy.unique(numpy.array(vlans)))
        for i in pargs.vlans:
            if   i['type'] == 'inband': pargs.vlan.update({'mgmt':i['vlan_id']})
            elif i['type'] == 'iscsi': pargs.vlan.update({'iscsi':i['vlan_id']})
            elif i['type'] == 'migration': pargs.vlan.update({'migration':i['vlan_id']})
            elif i['type'] == 'nfs': pargs.vlan.update({'nfs':i['vlan_id']})
            elif i['type'] == 'nvme': pargs.vlan.update({'nvme':i['vlan_id']})
        storage = []
        if pargs.vlan.get('iscsi'): storage.append(pargs.vlan['iscsi'])
        if pargs.vlan.get('nfs'): storage.append(pargs.vlan['nfs'])
        if pargs.vlan.get('nvme'): storage.append(pargs.vlan['nvme'])
        pargs.vlan['storage'] = ezfunctions.vlan_list_format(storage)
        plist = ['mgmt', 'migration', 'storage', 'all_vlans']
        for i in plist:
            if re.search('(mgmt|migration)', i): nvlan = pargs.vlan[i]
            elif 'storage' == i:
                if pargs.vlan.get('iscsi'): nvlan = pargs.vlan['iscsi']
            else: nvlan = 1
            polVars = dict(
                allowed_vlans = f'{pargs.vlan[i]}',
                description   = f'{pargs.ppfx}{i} {descr} Policy',
                name          = f'{pargs.ppfx}{i}',
                native_vlan   = nvlan,
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Ethernet QoS
    #=============================================================================
    def ethernet_qos(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['Bronze', 'Gold', 'Platinum', 'Silver']
        for i in plist:
            polVars = dict(
                enable_trust_host_cos = False,
                burst        = 10240,
                description  = f'{pargs.ppfx}{i} {descr} Policy',
                name         = f'{pargs.ppfx}{i}',
                mtu          = 9000,
                priority     = i,
                rate_limit   = 0,
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Pools - WWNN/WWPN
    #=============================================================================
    def fc(self, pargs, **kwargs):
        # Build Dictionary
        polVars = dict(
            description = f'{pargs.ppfx}wwnn Pool',
            name        = f'{pargs.ppfx}wwnn',
            id_blocks   = [{
                'from':f'20:00:00:25:B5:{pargs.pool_prefix}:00:00',
                'size':1024
            }],
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'pools,wwnn'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)

        # Loop through WWPN Pools
        flist = ['A', 'B']
        for i in flist:
            polVars.update(dict(
                description = f'{pargs.ppfx}wwpn-{i.lower()} Pool',
                name        = f'{pargs.ppfx}wwpn-{i.lower()}',
            ))
            polVars['id_blocks'][0].update({'from':f'20:00:00:25:B5:{pargs.pool_prefix}:{i}0:00'})
            kwargs['class_path'] = f'pools,wwpn'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Fibre-Channel Adapter
    #=============================================================================
    def fibre_channel_adapter(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['VMware', 'FCNVMeInitiator']
        for i in plist:
            polVars = dict(
                adapter_template = i,
                description      = f'{pargs.ppfx}{i} {descr} Policy',
                name             = f'{pargs.ppfx}{i}',
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Fibre-Channel Network
    #=============================================================================
    def fc_zone(self, pargs, **kwargs):
        return kwargs, pargs
        descr = (self.type.replace('_', ' ')).title()
        fabrics = ['A', 'B']
        for x in range(0,len(pargs.wwpn_targets)):
            # Build Dictionary
            polVars = dict(
                description           = f'{pargs.ppfx}vsan-{pargs.vsans[x]} {descr} Policy',
                fc_target_members     = [],
                fc_target_zoning_type = 'SIMT',
                name                  = f'{pargs.ppfx}vsan-{pargs.vsans[x]}',
            )
            for i in pargs.wwpn_targets[fabrics[x]]:
                polVars['fc_target_members'].append(dict(
                    name      = i['name'],
                    switch_id = fabrics[x],
                    vsan_id   = pargs.vsans[x],
                    wwpn      = i['wwpn']
                ))

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Fibre-Channel Network
    #=============================================================================
    def fibre_channel_network(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        for i in pargs.vsans:
            polVars = dict(
                description = f'{pargs.ppfx}vsan-{i} {descr} Policy',
                name        = f'{pargs.ppfx}vsan-{i}',
                vsan_id     = i,
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Fibre-Channel QoS
    #=============================================================================
    def fibre_channel_qos(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['fc-qos']
        for i in plist:
            polVars = dict(
                max_data_field_size = 2112,
                burst        = 10240,
                description  = f'{pargs.ppfx}{i} {descr} Policy',
                name         = f'{pargs.ppfx}{i}',
                mtu          = 9000,
                rate_limit   = 0,
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Flow Control
    #=============================================================================
    def flow_control(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.ppfx}flow-ctrl {descr} Policy',
            name        = f'{pargs.ppfx}flow-ctrl',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - IMC Access
    #=============================================================================
    def imc_access(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description         = f'{pargs.ppfx}kvm {descr} Policy',
            inband_ip_pool      = f'kvm-inband',
            inband_vlan_id      = pargs.vlan['mgmt'],
            out_of_band_ip_pool = 'kvm-ooband',
            name                = f'{pargs.ppfx}kvm',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Pools - IP
    #=============================================================================
    def ip(self, pargs, **kwargs):
        pdns = pargs.dns_servers[0]
        sdns = ''
        if len(pargs.dns_servers) == 2: sdns = pargs.dns_servers[1]
        # Build Dictionary
        band = ['inband', 'ooband']
        for i in band:
            match = False
            for x in pargs.vlans:
                if x['type'] == i:
                    y = x['pool_range'].split('-')
                    z = y[0].split('.')
                    kwargs['defaultGateway'] = x['gateway']
                    kwargs['subnetMask'] = x['netmask']
                    kwargs['ip_version'] = 'v4'
                    kwargs['pool_from']  = y[0]
                    kwargs['pool_to'] = f'{z[0]}.{z[1]}.{z[2]}.{y[1]}'
                    validating.error_subnet_check(**kwargs)
                    match = True
            if match == False:
                kwargs['networks'] = []
                for x in pargs.vlans:
                    kwargs['networks'].append(x['network'])
                validating.error_subnet_not_found(**kwargs)
            size = int(ipaddress.IPv4Address(kwargs['pool_to'])) - int(ipaddress.IPv4Address(kwargs['pool_from'])) + 1
            polVars = dict(
                description = f'{pargs.ppfx}kvm-{i} IP Pool',
                name        = f'{pargs.ppfx}kvm-{i}',
                ipv4_blocks = [{
                    'from':kwargs['pool_from'],
                    'size':size
                }],
                ipv4_configuration = [dict(
                    gateway       = kwargs['defaultGateway'],
                    netmask       = kwargs['subnetMask'],
                    primary_dns   = pdns,
                    secondary_dns = sdns
                )],
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'pools,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - IPMI over LAN
    #=============================================================================
    def ipmi_over_lan(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.ppfx}ipmi {descr} Policy',
            name        = f'{pargs.ppfx}ipmi',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - LAN Connectivity
    #=============================================================================
    def lan_connectivity(self, pargs, **kwargs):
        # Build Dictionary
        descr     = (self.type.replace('_', ' ')).title()
        pci_order = pargs.pci_order
        polVars = dict(
            description          = f'{pargs.ppfx}lcp {descr} Policy',
            name                 = f'{pargs.ppfx}lcp',
            target_platform      = 'FIAttached',
            vnics                = [],
        )
        plist = ['mgmt-Silver', 'migration-Bronze', 'storage-Platinum', 'dvs-Gold']
        for i in plist:
            pname = i.split('-')[0]
            pqos  = i.split('-')[1]
            if 'dvs' in pname: pgroup = 'all_vlans'
            else: pgroup = pname
            if re.search('(dvs|migration)', i): adapter_policy = 'VMware-High-Trf'
            elif 'storage' in i and pargs.vic_gen == 'gen4': adapter_policy = '16RxQs-4G'
            elif 'storage' in i and pargs.vic_gen == 'gen5': adapter_policy = '16RxQs-5G'
            else: adapter_policy = 'VMware'
            polVars['vnics'].append(dict(
                ethernet_adapter_policy         = adapter_policy,
                ethernet_network_control_policy = 'cdp',
                ethernet_network_group_policy   = pgroup,
                ethernet_qos_policy             = pqos,
                names                           = [f'{pname}-a', f'{pname}-b'],
                mac_address_pools               = [f'{pname}-a', f'{pname}-b'],
                placement_pci_order             = [pci_order, pci_order + 1],
            ))
            pci_order += 2
        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        pargs.pci_order = pci_order
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Link Aggregation
    #=============================================================================
    def link_aggregation(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.ppfx}link-agg {descr} Policy',
            name        = f'{pargs.ppfx}link-agg',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Link Control
    #=============================================================================
    def link_control(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.ppfx}link-ctrl {descr} Policy',
            name        = f'{pargs.ppfx}link-ctrl',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Local User
    #=============================================================================
    def local_user(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.ppfx}users {descr} Policy',
            name        = f'{pargs.ppfx}users',
            users       = [dict(
                enabled  = True,
                password = 1,
                role     = 'admin',
                username = pargs.local_user
            )]
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Pools - MAC
    #=============================================================================
    def mac(self, pargs, **kwargs):
        # Build Dictionary
        flist = ['a', 'b']
        nlist = ['1-2-dvs', 'A-B-mgmt', 'C-D-migration', 'E-F-storage', ]
        for i in nlist:
            for x in range(0,len(flist)):
                n = i.split('-')
                pool = n[2]
                polVars = dict(
                    description = f'{pargs.ppfx}{pool}-{flist[x]} Pool',
                    name        = f'{pargs.ppfx}{pool}-{flist[x]}',
                    mac_blocks  = [{
                        'from':f'00:25:B5:{pargs.pool_prefix}:{n[x]}0:00',
                        'size':1024
                    }],
                )

                # Add Policy Variables to immDict
                kwargs['class_path'] = f'pools,{self.type}'
                kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Multicast
    #=============================================================================
    def multicast(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.ppfx}mcast {descr} Policy',
            name        = f'{pargs.ppfx}mcast',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Network Connectivity
    #=============================================================================
    def network_connectivity(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description    = f'{pargs.ppfx}dns {descr} Policy',
            name           = f'{pargs.ppfx}dns',
            dns_servers_v4 = pargs.dns_servers,
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,network_connectivity'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - NTP
    #=============================================================================
    def ntp(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.ppfx}ntp {descr} Policy',
            name        = f'{pargs.ppfx}ntp',
            ntp_servers = pargs.ntp_servers,
            timezone    = pargs.timezone,
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,ntp'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Port
    #=============================================================================
    def port(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        ports = []
        for i in (pargs.uplinks.split('/')[-1]).split('-'):
            ports.append({'port_id':int(i)})
        epc = int((pargs.uplinks.split('/')[-1]).split('-')[0])
        polVars = dict(
            description  = f'{pargs.name} {descr} Policy',
            device_model = pargs.device_model,
            names        = [f'{pargs.name}-A', f'{pargs.name}-B'],
            port_channel_ethernet_uplinks = [dict(
                admin_speed                   = 'Auto',
                ethernet_network_group_policy = 'all_vlans',
                flow_control_policy           = 'flow-ctrl',
                interfaces                    = ports,
                link_aggregation_policy       = 'link-agg',
                link_control_policy           = 'link-ctrl',
                pc_ids                        = [epc, epc],
            )]
        )
        configure_fc = False
        if re.search('(fc|fc-nvme)', pargs.dtype): configure_fc = True
        if configure_fc == True:
            ports = []
            x     = pargs.fc_ports.split('/')
            for i in (x[-1]).split('-'):
                ports.append({'port_id':i})
            if pargs.swmode == 'end-host':
                fpc = int((x[-1]).split('-')[0])
                polVars.update(dict(
                    port_channel_fc_uplinks = [dict(
                        admin_speed  = '32Gbps',
                        fill_pattern = 'Idle',
                        interfaces   = ports,
                        pc_ids       = [fpc, fpc],
                        vsan_ids     = pargs.vsans
                    )]
                ))
                if len(x) == 3:
                    for i in polVars['port_channel_fc_uplinks']['interfaces']:
                        i.update({'breakout_port_id':x[2]})
            else:
                ports = x[-1]
                polVars.update(dict(
                    port_role_fc_storage = [dict(
                        admin_speed  = '32Gbps',
                        port_list    = ports,
                        vsan_ids     = pargs.vsans
                    )]
                ))
                if len(x) == 3:
                    polVars['port_role_fc_storage'].update({'breakout_port_id':x[2]})
            if len(x) == 3:
                polVars.update(dict(
                    port_modes = [dict(
                        custom_mode = f'BreakoutFibreChannel{pargs.breakout_speed}',
                        port_list   = [35, 36]
                    )]
                ))
            else:
                ports = int(x[-1].split('-')[0])
                porte = int(x[-1].split('-')[1])
                if porte > 12: port_end = 16
                elif porte > 8: port_end = 12
                elif porte > 4: port_end = 8
                else: port_end = 4
                polVars.update(dict(
                    port_modes = [dict(
                        custom_mode = 'FibreChannel',
                        port_list   = [1, port_end]
                    )]
                ))
        polVars.update({'port_role_servers':[]})
        for i in pargs.server_profiles:
            if len(i['ports'].split('/')) == 3:
                bp = int(i['ports'].split('/'))[2]
                polVars['port_modes'].append(dict(
                    custom_mode = f'BreakoutEthernet{pargs.breakout_speed}',
                    port_list   = [bp, bp]
                ))
                polVars['port_role_servers'].append(dict(
                    breakout_port_id      = bp,
                    connected_device_type = i['equipment'],
                    device_number         = i['identifier'],
                    port_list             = i['ports'].split('/')[-1]
                ))
            else:
                polVars['port_role_servers'].append(dict(
                    connected_device_type = i['equipment'],
                    device_number         = i['identifier'],
                    port_list             = i['ports'].split('/')[-1]
                ))
        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Power
    #=============================================================================
    def power(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['9508', 'Server']
        for i in plist:
            polVars = dict(
                description      = f'{pargs.ppfx}{i} {descr} Policy',
                name             = f'{pargs.ppfx}{i}',
                power_allocation = 8400,
                power_redundancy = 'Grid',
            )
            if i == 'Server': polVars.update({'power_restore':'LastState'})

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - SAN Connectivity
    #=============================================================================
    def san_connectivity(self, pargs, **kwargs):
        # Build Dictionary
        descr     = (self.type.replace('_', ' ')).title()
        pci_order = pargs.pci_order
        polVars = dict(
            description          = f'{pargs.ppfx}scp {descr} Policy',
            name                 = f'{pargs.ppfx}scp',
            target_platform      = 'FIAttached',
            vhbas                = [],
            wwnn_allocation_type = 'POOL',
            wwnn_pool            = f'{pargs.ppfx}wwnn',
        )
        ncount = 1
        if   pargs.dtype == 'fc': adapter_list = ['VMware']
        elif pargs.dtype == 'fc-nvme': adapter_list = ['VMware', 'FCNVMeInitiator']
        for x in range(0,len(adapter_list)):
            polVars['vhbas'].append(dict(
                fibre_channel_adapter_policy   = adapter_list[x],
                fibre_channel_network_policies = [f'vsan-{pargs.vsans[0]}', f'vsan-{pargs.vsans[1]}'],
                fibre_channel_qos_policy       = 'fc-qos',
                names                          = [f'vhba{ncount}', f'vhba{ncount + 1}'],
                placement_pci_order            = [pci_order, pci_order + 1],
                wwpn_allocation_type           = 'POOL',
                wwpn_pools                     = [f'wwpn-a', f'wwpn-b'],
            ))
            ncount += 2
            pci_order += 2
            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Serial over LAN
    #=============================================================================
    def serial_over_lan(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.ppfx}sol {descr} Policy',
            name        = f'{pargs.ppfx}sol',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - SNMP
    #=============================================================================
    def snmp(self, pargs, **kwargs):
        # Build Dictionary
        polVars = dict(
            description     = f'{pargs.ppfx}snmp Policy',
            enable_snmp     = True,
            name            = f'{pargs.ppfx}snmp',
            snmp_traps      = [],
            snmp_users      = [dict(
                auth_password    = 1,
                auth_type        = 'SHA',
                name             = pargs.snmp_user,
                privacy_password = 1,
                privacy_type     = 'AES',
                security_level   = 'AuthPriv'
            )],
            system_contact  = pargs.snmp_contact,
            system_location = pargs.snmp_location,
        )
        for i in pargs.snmp_servers:
            polVars['snmp_traps'].append(dict(
                destination_address = i,
                port                = 162,
                user                = pargs.snmp_user
            ))

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,snmp'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        polVars.update({
            'description':f'{pargs.ppfx}snmp-domain Policy',
            'name':f'{pargs.ppfx}snmp-domain'
        })
        kwargs['class_path'] = f'policies,snmp'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Storage
    #=============================================================================
    def storage(self, pargs, **kwargs):
        return kwargs, pargs
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['9508', 'Server']
        for i in plist:
            polVars = dict(
                description      = f'{pargs.ppfx}{i} {descr} Policy',
                name             = f'{pargs.ppfx}{i}',
                power_allocation = 8400,
                power_redundancy = 'Grid',
            )
            if i == 'Server': polVars.update({'power_restore':'LastState'})

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Switch Control
    #=============================================================================
    def switch_control(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description       = f'{pargs.ppfx}sw-ctrl {descr} Policy',
            fc_switching_mode = pargs.swmode,
            name              = f'{pargs.ppfx}sw-ctrl',
            vlan_port_count_optimization = True,
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,switch_control'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Syslog
    #=============================================================================
    def syslog(self, pargs, **kwargs):
        # Build Dictionary
        polVars = dict(
            description = f'{pargs.ppfx}syslog Policy',
            local_logging = dict(
                minimum_severity = 'warning',
            ),
            name            = f'{pargs.ppfx}syslog',
            remote_logging      = [],
        )
        for i in pargs.log_servers:
            polVars['remote_logging'].append(dict(
                enable           = True,
                hostname         = i,
                minimum_severity = 'informational',
            ))

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,syslog'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        polVars.update({
            'description':f'{pargs.ppfx}syslog-domain Policy',
            'name':f'{pargs.ppfx}syslog-domain'
        })
        kwargs['class_path'] = f'policies,syslog'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - System QoS
    #=============================================================================
    def system_qos(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        polVars = dict(
            description = f'{pargs.ppfx}qos {descr} Policy',
            classes     = [],
            name        = f'{pargs.ppfx}qos',
        )
        for k, v in kwargs['ezData']['ezimm']['allOf'][1]['properties']['systemQos'].items():
            cDict = {'priority':k}
            cDict.update(v)
            polVars['classes'].append(cDict)

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Thermal
    #=============================================================================
    def thermal(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).title()
        plist = ['9508']
        for i in plist:
            polVars = dict(
                fan_control_mode = 'Balanced',
                description      = f'{pargs.ppfx}{i} {descr} Policy',
                name             = f'{pargs.ppfx}{i}',
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Pools - MAC
    #=============================================================================
    def uuid(self, pargs, **kwargs):
        # Build Dictionary
        polVars = dict(
            description = f'{pargs.ppfx}uuid Pool',
            name        = f'{pargs.ppfx}uuid',
            prefix      = '000025B5-0000-0000',
            uuid_blocks = [{
                'from':f'{pargs.pool_prefix}00-000000000000',
                'size':1024
            }],
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'pools,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Virtual KVM
    #=============================================================================
    def virtual_kvm(self, pargs, **kwargs):
        # Build Dictionary
        polVars = dict(
            allow_tunneled_vkvm = True,
            description         = f'{pargs.ppfx}vkvm Virtual KVM Policy',
            name                = f'{pargs.ppfx}vkvm',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - Virtual Media
    #=============================================================================
    def virtual_media(self, pargs, **kwargs):
        descr = (self.type.replace('_', ' ')).title()
        # Build Dictionary
        polVars = dict(
            description         = f'{pargs.ppfx}vmedia {descr} Policy',
            name                = f'{pargs.ppfx}vmedia',
        )

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - VLAN
    #=============================================================================
    def vlan(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).upper()
        polVars = dict(
            description = f'{pargs.ppfx}vlans {descr} Policy',
            name        = f'{pargs.ppfx}vlans',
            vlans       = [dict(
                auto_allow_on_uplinks = True,
                multicast_policy      = 'mcast',
                name                  = 'default',
                native_vlan           = True,
                vlan_list             = 1
            )]
        )
        for i in pargs.vlans:
            if not int(i['vlan_id']) == 1:
                polVars['vlans'].append(dict(
                    multicast_policy = 'mcast',
                    name             = i['name'],
                    vlan_list        = i['vlan_id']
                ))
        for i in pargs.ranges:
            vfull = ezfunctions.vlan_list_full(i['vlan_list'])
            if 1 in vfull: vfull.remove(1)
            vlan_list = ezfunctions.vlan_list_format(vfull)
            polVars['vlans'].append(dict(
                multicast_policy = 'mcast',
                name             = i['name'],
                vlan_list        = vlan_list
            ))
        # Add Policy Variables to immDict
        kwargs['class_path'] = f'policies,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Build Policy - VSAN
    #=============================================================================
    def vsan(self, pargs, **kwargs):
        # Build Dictionary
        descr = (self.type.replace('_', ' ')).upper()
        if pargs.swmode == 'end-host': vsan_scope = 'Uplink'
        else: vsan_scope = 'Common'
        for i in pargs.vsans:
            polVars = dict(
                description = f'{pargs.ppfx}vsan-{i} {descr} Policy',
                name        = f'{pargs.ppfx}vsan-{i}',
                vsans       = [dict(
                    fcoe_vlan_id = i,
                    name         = f'{pargs.ppfx}vsan-{i}',
                    vsan_id      = i,
                    vsan_scope   = vsan_scope
                )]
            )

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'policies,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


#=======================================================
# Storage Class
#=======================================================
class storage(object):
    def __init__(self, type):
        self.type = type
    #=============================================================================
    # Function - NetApp - AutoSupport
    #=============================================================================
    def autosupport(self, pargs, **kwargs):
        # Build Dictionary
        jDict = kwargs['immDict']['wizard']['ontap_mgmt'][0]
        polVars = {
            'contact_support':True,
            'enabled':True,
            'from':jDict['from_address'],
            'is_minimal':False,
            'mail_hosts':jDict['mail_hosts'].split(','),
            'transport':jDict['transport'],
            'to':jDict['to_addresses'].split(','),
        }
        if jDict.get('proxy_url'):
            polVars.update({'proxy_url':jDict['proxy_url']})

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'netapp,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        pargs.apiBody = polVars
        kwargs, pargs = eval(f"netapp.api(self.type).{self.type}(pargs, **kwargs)")
        return kwargs, pargs


    #=============================================================================
    # Function - NetApp - Broadcast Domains
    #=============================================================================
    def broadcast_domain(self, pargs, **kwargs):
        # Build Dictionary
        for i in pargs.vlans:
            if re.search('(inband|iscsi|nvme|nfs)', i['type']):
                if i['type'] == 'inband': mtu = 1500
                else: mtu = 9000
                polVars = { "name": i['name'], "mtu": mtu }

                # Add Policy Variables to immDict
                kwargs['class_path'] = f'netapp,{self.type}'
                kwargs = ezfunctions.ez_append(polVars, **kwargs)
        
        polVars = { "name": "Default", "mtu": 9000}
        # Add Policy Variables to immDict
        kwargs['class_path'] = f'netapp,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        #print(kwargs['immDict']['orgs']['terratest'])
        pargs.item = kwargs['immDict']['orgs']['terratest']['netapp']['broadcast_domain']
        kwargs, pargs = eval(f"netapp.api(self.type).{self.type}(pargs, **kwargs)")
        return kwargs, pargs


    #=============================================================================
    # Function - NetApp - Cluster
    #=============================================================================
    def cluster(self, pargs, **kwargs):
        # Build Dictionary
        jDict1 = kwargs['immDict']['wizard']['ontap'][0]
        jDict2 = kwargs['immDict']['wizard']['ontap_mgmt'][0]
        pargs.netapp.snmp_contact  = jDict2['snmp_contact']
        pargs.netapp.snmp_location = jDict2['snmp_location']
        polVars = dict(
            contact     = pargs.netapp.snmp_contact,
            dns_domains = pargs.dns_domains,
            license     = dict(keys = []),
            location    = pargs.netapp.snmp_location,
            management_interfaces = [
                dict(
                    name = "cluster-mgmt",
                    ip = dict(
                        address = pargs.ooband['controller'][0]
                ))
            ],
            name = jDict1['cluster_name'],
            name_servers = pargs.dns_servers,
            ntp_servers  = pargs.ntp_servers,
            timezone     = pargs.timezone
        )
        if kwargs['immDict']['wizard'].get('license'):
            licenses = []
            for i in kwargs['immDict']['wizard']['license']: licenses.append(i['license_value'])
            polVars.update({'license':{'keys':[licenses]}})

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'netapp,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        #print(kwargs['immDict']['orgs']['terratest'])
        pargs.item = kwargs['immDict']['orgs']['terratest']['netapp']['cluster'][0]
        # Comment out for Testing
        #kwargs, pargs = eval(f"netapp.api(self.type).cluster_init(pargs, **kwargs)")
        kwargs, pargs = eval(f"netapp.api(self.type).{self.type}(pargs, **kwargs)")
        return kwargs, pargs


    #=============================================================================
    # Function - NetApp - Nodes
    #=============================================================================
    def nodes(self, pargs, **kwargs):
        # Build Dictionary
        for node in pargs.netapp.node_list:
            polVars = {'interfaces': {'lacp':[], 'vlan':[]}, 'name': node, 'storage_aggregates': []}
            aggregate = '{}_1'.format(node.replace('-', '_'))
            agg = { "block_storage": {"primary": {"disk_count": pargs.netapp.disk_count}}, "name": aggregate }
            polVars['storage_aggregates'].append(agg)
            aggPort = {
                "broadcast_domain": {"name": "Default"},
                "enabled": True,
                "lag": { "mode": "multimode_lacp", "distribution_policy": "mac", "member_ports": []},
                "type": "lag"
            }
            for i in pargs.netapp.data_ports:
                aggPort['lag']['member_ports'].append({"name": i})
            polVars['interfaces']['lacp'].append(aggPort)
            if re.search('(fc|fc-nvme)', pargs.dtype):
                polVars['interfaces'].update({'fcp':[]})
                for i in pargs.netapp.fcp_ports:
                    fcpPort = { "enabled": True, "name": i, "speed": {"configured":pargs.netapp.fcp_speed} }
                    polVars['interfaces']['fcp'].append(fcpPort)
            for i in pargs.vlans:
                if re.search('(inband|nfs|iscsi|nvme)', i['type']):
                    vlanPort = {
                        "broadcast_domain": {"name": i['name']},
                        #"name": f"a0a-{i['vlan_id']}",
                        "type": "vlan",
                        "vlan": { "base_port": {"name": 'a0a'}, "tag": i['vlan_id'] }
                    }
                    polVars['interfaces']['vlan'].append(vlanPort)

            # Add Policy Variables to immDict
            kwargs['class_path'] = f'netapp,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        pargs.item = kwargs['immDict']['orgs']['terratest']['netapp']['nodes']
        kwargs, pargs = eval(f"netapp.api(self.type).{self.type}(pargs, **kwargs)")
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - NetApp - Schedulers
    #=============================================================================
    def schedule(self, pargs, **kwargs):
        # Build Dictionary
        polVars = {
            "cluster": pargs.netapp.cluster,
            "cron": {"minutes":[15]},
            "name": "15min",
            "svm":{"name":pargs.netapp.data_svm}
        }
        # Add Policy Variables to immDict
        kwargs['class_path'] = f'netapp,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - NetApp - SNMP
    #=============================================================================
    def snmp(self, pargs, **kwargs):
        # Build Dictionary
        jDict = kwargs['immDict']['wizard']['ontap_mgmt'][0]
        polVars = {
            "auth_traps_enabled": True,
            "enabled": True,
            "traps_enabled": True,
            "trigger_test_trap": True,
            "traps": [{
                "host": jDict['trap_server'],
                "user": { "name": jDict['username'] }
            }],
            "users": [{
                "authentication_method": "usm",
                "name": jDict['username'],
                "owner": {"name": pargs.netapp.cluster},
                "snmpv3": {
                    "authentication_protocol": "sha",
                    "privacy_protocol": "aes128"
                }
            }]
        }

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'netapp,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - NetApp - SVM
    #=============================================================================
    def svm(self, pargs, **kwargs):
        # Build Dictionary
        #=====================================================
        # Configure Aggregates
        #=====================================================
        agg1 = deepcopy(pargs.netapp.node01).replace('-', '_') + '_1'
        agg2 = deepcopy(pargs.netapp.node02).replace('-', '_') + '_1'
        #=====================================================
        # Create Infra SVM
        #=====================================================
        if ':' in pargs.inband.network: ifamily = 'ipv6'
        else: ifamily = 'ipv4'
        polVars = {
            "aggregates": [ {"name": agg1}, {"name": agg2} ],
            "name": pargs.netapp.data_svm,
            "dns":{"domains": pargs.dns_domains, "servers": pargs.dns_servers},
            "routes": [{
                "destination": {
                    "address":'0.0.0.0',
                    "family": ifamily,
                    "netmask": 0
                },
                "gateway": pargs.inband.gateway,
            }]
        }
        for p in pargs.netapp.protocols: polVars.update({p:{"allowed": True, "enabled": True}})

        #=====================================================
        # Configure Infra SVM Interfaces
        #=====================================================
        def configure_interfaces(x, pargs, **kwargs):
            ip_address = pargs.vconfig['controller'][x]
            if ':' in ip_address: ifamily = 'ipv6'
            else: ifamily = 'ipv4'
            if 'inband'  == pargs.vconfig['type']: servicePolicy = 'default-management'
            elif 'iscsi' == pargs.vconfig['type']: servicePolicy = 'default-data-iscsi'
            elif 'nfs'   == pargs.vconfig['type']: servicePolicy = 'default-data-files'
            elif 'nvme'  == pargs.vconfig['type']: servicePolicy = 'default-data-nvme-tcp'
            home_port = f"a0a-{pargs.vconfig['vlan_id']}"
            services = 'data_nfs'
            # data-iscsi,data-nfs,data-cifs,data-flexcache,data-nvme-tcp
            #"ip": { "address": ip_address, "family": ifamily, "netmask": pargs.vconfig['prefix'] },
            if 'inband' == pargs.vconfig['type'] and x == 1: proceed = False
            else: proceed = True
            if proceed == True:
                pargs.polVars = {
                    "enabled": True,
                    "dns_zone": pargs.dns_domains[0],
                    "ip": { "address": ip_address, "netmask": pargs.vconfig['prefix'] },
                    "location": {
                        "auto_revert": True,
                        "failover": "home_port_only",
                        "home_node": {"name":pargs.netapp.node_list[x]},
                        "home_port": {"name":home_port, "node":{"name":pargs.netapp.node_list[x]}},
                    },
                    "name": pargs.netapp.intf_name,
                    "scope": "svm",
                    "service_policy": servicePolicy,
                }
            if re.search('(iscsi|nvme)', pargs.vconfig['type']):
                pargs.polVars['location'].pop('auto_revert')
                pargs.polVars['location'].pop('failover')
            return kwargs, pargs

        # Next Section
        polVars['data_interfaces'] = []
        #pargs.letter = {'iscsi':1,'nvme':1}
        for v in pargs.vlans:
            node_count = 1
            for x in range(0,len(pargs.netapp.node_list)):
                if re.search('(inband|iscsi|nfs|nvme)', v['type']):
                    if re.search('(inband|nfs)', v['type']):
                        pargs.netapp.intf_name = f"{v['type']}-lif-0{x+1}-a0a-{v['vlan_id']}"
                    elif re.search('(iscsi|nvme)', v['type']):
                        #{(chr(ord('@')+pargs.letter[v['type']])).lower()}
                        pargs.netapp.intf_name = f"{v['type']}-lif-0{x+1}-a0a-{v['vlan_id']}"
                        if node_count == 2: pargs.letter[v['type']] += 1
                        node_count += 1
                    pargs.vconfig = deepcopy(v)
                    kwargs, pargs = configure_interfaces(x, pargs, **kwargs)
                    if len(pargs.polVars) > 0:
                        polVars['data_interfaces'].append(pargs.polVars)
        if re.search('fc(-nvme)?', pargs.dtype):
            polVars['fcp_interfaces'] = []
            def configure_fcports(x, pargs, **kwargs):
                pargs.polVars = []
                for i in pargs.netapp.fcp_ports:
                    for x in range(0,len(pargs.netapp.node_list)):
                        if pargs.netapp.data_protocol == 'fc-nvme': name = f'fcp-nvme-lif-0{x+1}-{i}'
                        else: name = f'fcp-lif-0{x+1}-{i}'
                        pVars = {
                            "data_protocol": pargs.netapp.data_protocol,
                            "enabled": True,
                            "location": {
                                "home_port": {"name":i, "node":{"name":pargs.netapp.node_list[x]}},
                            },
                            "name": name,
                        }
                        pargs.polVars.append(pVars)
                return kwargs, pargs
            if pargs.dtype == 'fc':
                pargs.netapp.data_protocol = 'fcp'
                kwargs, pargs = configure_fcports(x, pargs, **kwargs)
                polVars['fcp_interfaces'].extend(pargs.polVars)
            else:
                fcp_temp = pargs.netapp.fcp_ports
                half = len(fcp_temp)//2
                pargs.netapp.fcp_ports = fcp_temp[:half]
                pargs.netapp.data_protocol = 'fcp'
                kwargs, pargs = configure_fcports(x, pargs, **kwargs)
                polVars['fcp_interfaces'].extend(pargs.polVars)
                pargs.netapp.fcp_ports = fcp_temp[half:]
                pargs.netapp.data_protocol = pargs.dtype
                kwargs, pargs = configure_fcports(x, pargs, **kwargs)
                polVars['fcp_interfaces'].extend(pargs.polVars)

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'netapp,{self.type}'
        kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        pargs.item = kwargs['immDict']['orgs']['terratest']['netapp']['svm']
        kwargs, pargs = eval(f"netapp.api(self.type).{self.type}(pargs, **kwargs)")
        return kwargs, pargs


    #=============================================================================
    # Function - NetApp - Storage Volumes
    #=============================================================================
    def volumes(self, pargs, **kwargs):
        for node in pargs.netapp.node_list:
            aggregate = '{}_1'.format(node.replace('-', '_'))
            if node == pargs.netapp.node01:
                rootm = '{}_m01'.format(node.replace('-', '_'), )
            else: rootm = '{}_m02'.format(node.replace('-', '_'), )
            # Build Dictionary
            polVars = {
                "aggregates": [{"name": aggregate}],
                "encryption": True,
                "name": rootm,
                "size": "1GB",
                "svm":{"name":pargs.netapp.data_svm},
                "type":"DP"
            }
            # Add Policy Variables to immDict
            kwargs['class_path'] = f'netapp,{self.type}'
            kwargs = ezfunctions.ez_append(polVars, **kwargs)
        #=====================================================
        # Return pargs and kwargs
        #=====================================================
        return kwargs, pargs


#=======================================================
# Wizard Class
#=======================================================
class wizard(object):
    def __init__(self, type):
        self.type = type

    #=============================================================================
    # Function - Build the Converged Stack
    #=============================================================================
    def build_environment(self, **kwargs):
        pargs = DotMap()
        #=====================================================
        # Credentials
        #=====================================================
        jDict = kwargs['immDict']['wizard']['credentials'][0]
        pargs.nxosuser = jDict['nxos_username']
        pargs.stguser  = jDict['netapp_username']
        pargs.vctruser = jDict['vcenter_username']
        #=====================================================
        # DHCP, DNS, NTP, Organization
        #=====================================================
        jDict = kwargs['immDict']['wizard']['dhcp_dns_ntp'][0]
        pargs.dns_servers = [jDict['dns_server1']]
        pargs.dns_domains = jDict['dns_domains'].split(',')
        pargs.ntp_servers = [jDict['ntp_server1']]
        pargs.timezone    = jDict['timezone']
        if jDict.get('dhcp_server1'): pargs.dhcp_servers = [jDict['dhcp_server1']]
        if jDict.get('dhcp_server2'): pargs.dhcp_servers.append(jDict['dhcp_server2'])
        if jDict.get('dns_server2'): pargs.dns_servers.append(jDict['dns_server2'])
        if jDict.get('ntp_server2'): pargs.ntp_servers.append(jDict['ntp_server2'])
        #==================================
        # VLANs
        #==================================
        pargs.vlans = []
        for i in kwargs['immDict']['wizard']['vlans']:
            i = DotMap(deepcopy(i))
            netwk = '%s' % ipaddress.IPv4Network(i.network, strict=False)
            vDict = dict(
                configure = i.configure_network,
                gateway   = i.network.split('/')[0],
                name      = i.name,
                netmask   = ((ipaddress.IPv4Network(netwk)).with_netmask).split('/')[1],
                network   = netwk,
                prefix    = i.network.split('/')[1],
                switch    = i.switch_type,
                type      = i.vlan_type,
                vlan_id   = i.vlan_id,
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
            if i.get('controller_range'): vDict.update({'controller':iprange(i.controller_range)})
            if i.get('pool_range') and re.search('(inband|ooband)', i.vlan_type):
                vDict.update({'pool':iprange(i.pool_range)})
            if i.get('server_range'): vDict.update({'server':iprange(i.server_range)})
            pargs.vlans.append(vDict)
        pargs.inband = DotMap()
        pargs.ooband = DotMap()
        for i in pargs.vlans:
            i = DotMap(deepcopy(i))
            if re.search('(inband|ooband)', i.type):
                pargs[i.type].update(i)
        pargs.ranges = []
        for i in kwargs['immDict']['wizard']['ranges']:
            i = DotMap(deepcopy(i))
            pargs.ranges.append(dict(
                configure = i.configure_network,
                name      = i.name_prefix,
                vlan_list = i.vlan_range
            ))
        #=====================================================
        # IMM Domain
        #=====================================================
        jDict   = kwargs['immDict']['wizard']['imm_domain'][0]
        pargs.dtype   = jDict['deployment_type']
        pargs.name    = jDict['name']
        pargs.org     = jDict['organization']
        pargs.serials = [jDict['fabric_a_serial'], jDict['fabric_b_serial']]
        pargs.uplinks = jDict['uplink_ports']
        ports = jDict['uplink_ports'].split('/')[-1]
        if '-' in jDict['uplink_ports']:
            pstart = ports.split('-')[0]
            plast = ports.split('-')[1]
            plist = []
            for x in range(int(pstart),int(plast)+1):
                plist.append(x)
            pargs.uplink_list = plist
        else: pargs.uplink_list = ports.split(',')
        pargs.tags    = kwargs['ezData']['tags']
        kwargs['org'] = pargs.org
        if jDict.get('breakout_speed'): pargs.breakout_speed = jDict['breakout_speed']
        else: pargs.breakout_speed = '25G'
        #=====================================================
        # NetApp Cluster
        #=====================================================
        jDict      = DotMap(deepcopy(kwargs['immDict']['wizard']['ontap'][0]))
        pargs.netapp            = DotMap()
        pargs.netapp.hostPrompt = r'[\w]+::>'
        pargs.netapp.banner     = jDict.login_banner
        pargs.netapp.cluster    = jDict.cluster_name
        pargs.netapp.data_ports = deepcopy(jDict.data_ports).split(',')
        pargs.netapp.data_speed = jDict.data_speed
        pargs.netapp.data_svm   = deepcopy(jDict.data_svm)
        pargs.netapp.fcp_ports  = deepcopy(jDict.fcp_ports).split(',')
        pargs.netapp.fcp_speed  = jDict.fcp_speed
        pargs.netapp.node01     = jDict.node01
        pargs.netapp.node02     = jDict.node02
        pargs.netapp.node_list  = [deepcopy(jDict.node01), deepcopy(jDict.node02)]
        pargs.netapp.user       = pargs.stguser
        pargs.netapp.protocols  = []
        for i in pargs.vlans:
            i = DotMap(deepcopy(i))
            if re.search('(iscsi|nfs|nvme)', i.type):
                if 'nvme' in i.type: pargs.netapp.protocols.append('nvme_of')
                else: pargs.netapp.protocols.append(i.type)
        if 'fc' in pargs.dtype: pargs.netapp.protocols.append('fcp')
        pargs.netapp.protocols = numpy.unique(numpy.array(pargs.netapp.protocols))
        pargs.host = deepcopy(pargs.netapp.node01)
        #==================================
        # Get Disk Information
        #==================================
        uri = 'storage/disks'
        json_data = netapp.get(uri, pargs, **kwargs)
        pargs.netapp.disk_count = json_data['num_records'] - 1
        disk_name = json_data['records'][0]['name']
        uri = f'storage/disks/{disk_name}'
        json_data = netapp.get(uri, pargs, **kwargs)
        pargs.netapp.disk_type = json_data['type'].upper()
        print(f'disk count is {pargs.netapp.disk_count}')
        print(f'disk type is {pargs.netapp.disk_type}')
        #==================================
        # Get Moids for Fabric Switches
        #==================================
        pargs.apiMethod    = 'get'
        pargs.policy       = 'serial_number'
        pargs.purpose      = 'domain'
        pargs.names        = pargs.serials
        kwargs             = isdk.api('serial_number').calls(pargs, **kwargs)
        pargs.serial_moids = kwargs['pmoids']
        pargs.device_model = pargs.serial_moids[pargs.serials[0]]['Model']
        #==================================
        # Management Protocols
        #==================================
        jDict = kwargs['immDict']['wizard']['mgmt'][0]
        pargs.log_servers   = [jDict['syslog_server1']]
        pargs.snmp_contact  = jDict['snmp_contact']
        pargs.snmp_location = jDict['snmp_location']
        pargs.snmp_servers  = [jDict['snmp_server1']]
        pargs.snmp_user     = jDict['username']
        if jDict.get('syslog_server2'): pargs.log_servers.append(jDict['syslog_server2'])
        if jDict.get('snmp_server2'): pargs.snmp_servers.append(jDict['snmp_server2'])
        #==================================
        # Pools and Policies
        #==================================
        jDict = kwargs['immDict']['wizard']['imm_policy'][0]
        pargs.local_user   = jDict['local_user']
        pargs.pool_prefix  = jDict['pool_id_prefix']
        if jDict.get('policy_prefix'): pargs.ppfx = jDict['policy_prefix']
        else: pargs.ppfx = ''
        #==================================
        # Server Profiles
        #==================================
        pargs.server_profiles = []
        for i in kwargs['immDict']['wizard']['imm_profiles']:
            i = DotMap(deepcopy(i))
            pargs.server_profiles.append(dict(
                count      = i.profile_count,
                cpu        = i.cpu_vendor,
                identifier = i.identifier,
                equipment  = i.equipment_type,
                gen        = i.generation,
                ports      = i.domain_ports,
                profile    = i.profile_start,
                tpm        = i.tpm,
                vic_gen    = i.vic_generation,
            ))
        # Comment out for Testing
        #kwargs, pargs = nxos.nxos.config(self, pargs, **kwargs)
        #=====================================================
        # Confirm if Fibre-Channel is in Use
        #=====================================================
        if re.search('(fc|fc-nvme)', pargs.dtype):
            jDict          = kwargs['immDict']['wizard']['imm_fc'][0]
            pargs.fc_ports = jDict['fc_ports']
            pargs.swmode   = jDict['switch_mode']
            pargs.vsans    = [jDict['vsan_a'], jDict['vsan_b']]
            if jDict.get('breakout_speed'): pargs.breakout_speed = jDict['breakout_speed']
            else: pargs.breakout_speed = '32G'
        #==================================
        # Begin Configuration Creation
        #==================================
        plist = list(kwargs['ezData']['pools']['allOf'][1]['properties'].keys())
        plist.remove('resource')
        plist.extend(list(kwargs['ezData']['policies']['allOf'][1]['properties'].keys()))
        pop_list = kwargs['ezData']['ezimm']['allOf'][1]['properties']['converged.pop_list']['enum']
        for i in pop_list: plist.remove(i)
        pop_list = kwargs['ezData']['ezimm']['allOf'][1]['properties']['converged.fc_pop_list']['enum']
        if re.search('fc(-nvme)?', pargs.dtype):
            if pargs.sw_mode == 'end-host': plist.remove('fc_zone')
        else:
            for i in pop_list: plist.remove(i)
        pargs.pci_order = 0
        plist = ['autosupport', 'broadcast_domain', 'cluster', 'nodes', 'schedule', 'snmp', 'svm']
        plist = ['svm']
        for i in plist:
            kwargs, pargs = eval(f"storage(i).{i}(pargs, **kwargs)")
        #plist = ['port']
        #for i in plist:
        #    kwargs, pargs = eval(f"imm(i).{i}(pargs, **kwargs)")
        #kwargs, pargs = imm('domain').domain(pargs, **kwargs)
        #print(json.dumps(kwargs['immDict']['orgs'], indent=4))
        #=====================================================
        # Return kwargs
        #=====================================================
        return kwargs, pargs


    #=============================================================================
    # Function - Wizard Worksheet Policy Settings
    #=============================================================================
    def settings(self, **kwargs):
        # Get Variables from Library
        kwargs['validateData'] = kwargs['ezData'][f'wizard.{self.type}']['allOf'][1]['properties']
        # Build Dictionary of Policy Variables
        polVars = ezfunctions.process_kwargs(**kwargs)

        # Add Policy Variables to immDict
        kwargs['class_path'] = f'{self.type}'
        kwargs = ezfunctions.ez_append_wizard(polVars, **kwargs)
        return kwargs
