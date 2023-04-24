#!/usr/bin/env python3

from copy import deepcopy
from classes import ezfunctions
from classes import validating
from classes.vmw import cluster
from classes.vmw import datacenter
from classes.vmw import datastore
from classes.vmw import host
from classes.vmw import network
from classes.vmw import ssl_helper
from classes.vmw import util
from dotmap import DotMap
from pyVmomi import vim # pyright: ignore
from vmware.vapi.vsphere.client import create_vsphere_client
import numpy
import pyVim.connect
import re
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global options for debugging
print_payload = False
print_response_always = True
print_response_on_fail = True

# Log levels 0 = None, 1 = Class only, 2 = Line
log_level = 2

# Exception Classes
class InsufficientArgs(Exception): pass
class ErrException(Exception): pass
class InvalidArg(Exception): pass
class LoginFailed(Exception): pass


# Class must be instantiated with Variables
class api(object):
    def __init__(self, type):
        self.type = type
    #=====================================================
    # ESX Host Initialization
    #=====================================================
    def esx(self, pargs, **kwargs):
        #=====================================================
        # Send Begin Notification
        #=====================================================
        validating.begin_section('vCenter', self.type)
        time.sleep(2)
        #=====================================================
        # Load Variables and Login to Storage Array
        #=====================================================
        kwargs['Variable'] = 'esx_password'
        kwargs = ezfunctions.sensitive_var_value(**kwargs)
        pargs.esx.password = kwargs['var_value']
        for k, v in pargs.server_profiles.items():
            esx_host = k + '.' + pargs.dns_domains[0]
            print(f"\n{'-'*91}\n")
            print(f"   Beginning Base Configuration for {esx_host}. Including dns, ntp, ssh, and vibs.")
            print(f"\n{'-'*91}\n")
            time.sleep(2)
            pargs.hostname     = esx_host
            pargs.hostPassword = 'esx_password'
            pargs.username     = 'root'
            pargs.hostPrompt   = f'root\\@{k}\\:'
            child, kwargs      = ezfunctions.child_login(pargs, **kwargs)
            #=====================================================
            # Get TPM Key if Installed
            #=====================================================
            child.sendline('esxcli system settings encryption get')
            tpm_installed = False
            cmd_check = False
            while cmd_check == False:
                regex1 = re.compile('Mode: TPM')
                i = child.expect([regex1, pargs.hostPrompt])
                if i == 0: tpm_installed = True
                elif i == 1: cmd_check == True
            if tpm_installed == True:
                child.sendline('esxcli system settings encryption recovery list')
                cmd_check = False
                while cmd_check == False:
                    regex1 = re.compile('(\\{[A-Z\\d\\-]+\\})[ ]+([A-Z\\d\\-]+)\r')
                    i = child.expect([regex1, pargs.hostPrompt])
                    if i == 0:
                        v['recovery_id'] = (child.match).group(1)
                        v['recovery_key'] = (child.match).group(2)
                    elif i == 1: cmd_check == True
                    child.sendline('')
            #=====================================================
            # Enable DNS, NTP, SSH Shell, and WGET
            #=====================================================
            ntp_cfg = 'esxcli system ntp set '
            for ntp in pargs.ntp_servers: ntp_cfg = ntp_cfg + f'--server {ntp} '
            ntp_cfg = ntp_cfg + '--enabled true'
            cmds = [
                'vim-cmd hostsvc/enable_ssh > /dev/null 2>&1',
                'chkconfig SSH on > /dev/null 2>&1',
                'esxcli network firewall ruleset set -e true -r httpClient',
                f'esxcli system hostname set --fqdn={esx_host}'
                f'esxcli network ip dns search add -d {pargs.dns_domains[0]}',
                'vim-cmd hostsvc/enable_ssh',
                'vim-cmd hostsvc/enable_esx_shell',
                'vim-cmd hostsvc/advopt/update UserVars.SuppressShellWarning long 1',
                ntp_cfg, 'cd /tmp'
            ]
            for cmd in cmds:
                child.sendline(cmd)
                child.expect(pargs.hostPrompt)
            for dns in pargs.dns_servers:
                child.sendline(f'esxcli network ip dns server add -s {dns}')
                child.expect(pargs.hostPrompt)
            for domain_name in pargs.dns_domains:
                child.sendline(f'esxcli network ip dns search add -d {domain_name}')
                child.expect(pargs.hostPrompt)
            #=====================================================
            # Install VIBs
            #=====================================================
            pargs.repository_server = 'rdp1.rich.ciscolabs.com'
            pargs.repository_path = '/'
            pargs.vib_files = [
                'Broadcom-lsi-mr3_7.719.02.00-1OEM.700.1.0.15843807_18724954.zip',
                'Cisco-nenic_1.0.45.0-1OEM.700.1.0.15843807_20904742.zip',
                'Cisco-nfnic_5.0.0.37-1OEM.700.1.0.15843807_20873938.zip',
                'NetAppNasPlugin2.0.1.zip'
            ]
            reboot_required = False
            for vib in pargs.vib_files:
                repo_url = ezfunctions.repo_url_test(vib, pargs)
                child.sendline(f'rm -f {vib}')
                child.expect(pargs.hostPrompt)
                child.sendline(f'wget --no-check-certificate {repo_url}')
                child.expect('saved')
                child.expect(pargs.hostPrompt)
                if re.search('(Broadcom|Cisco)', vib): child.sendline(f'esxcli software component apply -d /tmp/{vib}')
                else: child.sendline(f'esxcli software vib install -d /tmp/{vib}')
                cmd_check = False
                while cmd_check == False:
                    regex1 = re.compile(f"(Components Installed: [a-zA-Z\\-\\_\\.]+)\r")
                    regex2 = re.compile('(Message: [a-zA-Z\\d ,]+\\.)\r')
                    regex3 = re.compile('Reboot Required: true')
                    i = child.expect([regex1, regex2, regex3, pargs.hostPrompt])
                    if   i == 0: print(f'\n\n    {(child.match).group(1)}\n\n')
                    elif i == 1: print(f'\n\n    VIB {vib} install message is {(child.match).group(1)}\n\n')
                    elif i == 2: reboot_required = True
                    elif i == 3: cmd_check = True
            child.sendline('esxcfg-advcfg -s 0 /Misc/HppManageDegradedPaths')
            child.expect(pargs.hostPrompt)
            if reboot_required == True:
                child.sendline('reboot')
                child.expect('closed')
            else:
                child.sendline('exit')
                child.expect('closed')
            print(f"\n{'-'*91}\n")
            print(f"   Completed Base Configuration for {esx_host}")
            print(f"\n{'-'*91}\n")
            time.sleep(2)
        child.close()
        print(pargs.server_profiles)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section('vCenter', self.type)
        return kwargs, pargs

    #=====================================================
    # vCenter Configuration
    #=====================================================
    def vcenter(self, pargs, **kwargs):
        #=====================================================
        # Send Begin Notification
        #=====================================================
        validating.begin_section(self.type, 'Host')
        time.sleep(2)
        #=====================================================
        # Load Variables and Login to vCenter API's
        #=====================================================
        pargs.esx.username            = 'root'
        pargs.vcenter.datacenter.name = 'NETAPP'
        pargs.vcenter.server          = 'vcenter.rich.ciscolabs.com'
        pargs.vcenter.username        = 'administrator@rich.local'
        kwargs['Variable'] = 'esx_password'
        kwargs = ezfunctions.sensitive_var_value(**kwargs)
        pargs.esx.password = kwargs['var_value']
        kwargs['Variable'] = 'vcenter_password'
        kwargs = ezfunctions.sensitive_var_value(**kwargs)
        pargs.vcenter.password = kwargs['var_value']

        # Connect to VIM API Endpoint on vCenter system
        context = ssl_helper.get_unverified_context()
        service_instance = pyVim.connect.SmartConnect(host=pargs.vcenter.server,
                                                      user=pargs.vcenter.username,
                                                      pwd =pargs.vcenter.password,
                                                      sslContext=context)
        # Connect to vAPI Endpoint on vCenter system
        session = ssl_helper.get_unverified_session()
        client = create_vsphere_client(server  =pargs.vcenter.server,
                                       username=pargs.vcenter.username,
                                       password=pargs.vcenter.password,
                                       session=session)
        context = util.Context(service_instance, client)
        #==============================================
        # Configure Data Center
        #==============================================
        dcFound, pargs = datacenter.detect_datacenter(context, pargs)
        if dcFound == False:
            pargs = datacenter.create_datacenter(context, pargs)
        #==============================================
        # Configure Cluster
        #==============================================
        models = []
        for k, v in pargs.server_profiles.items(): models.append(v['model'])
        models = numpy.unique(numpy.array(models))
        for cluster_name in models:
            clusterFound, pargs = cluster.detect_cluster(context, cluster_name, pargs)
            if clusterFound == False:
                pargs = cluster.create_cluster_vapi2(context, cluster_name, pargs)
        #==============================================
        # Find Cluster Host Folder and Existing Hosts
        #==============================================
        pargs = host.host_folders(context, pargs)
        #print(pargs.vcenter.host.folder)

        esx_hosts = []
        for i in pargs.server_profiles.keys():
            esx_hosts.append(i + '.' + pargs.dns_domains[0])
        pargs = host.detect_hosts(context, esx_hosts, pargs)
        #==============================================
        # Add ESXi Hosts to DC And Move to Cluster
        #==============================================
        for k, v in pargs.server_profiles.items():
            esx_host = k + '.' + pargs.dns_domains[0]
            index = [i for i, d in enumerate(pargs.host_summaries) if esx_host in d.name]
            if len(index) == 0:
                pargs = host.create_host_vapi(context, esx_host, pargs)
                host.move_host_into_cluster_vim(context, v['model'], esx_host, pargs)
            else:
                pargs.esxhosts[esx_host].moid = pargs.host_summaries[index[0]].host
        #print(pargs.esxhosts)

        datastore.create_vmfs_datastore(context, pargs)
        #=====================================================
        # Send End Notification and return kwargs
        #=====================================================
        validating.end_section(self.type, 'Host')
        return kwargs, pargs

