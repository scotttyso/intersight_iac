"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016-2018. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware, Inc.'

import pyVim.task
from com.vmware.vcenter_client import Cluster, Folder
from pyVmomi import vim # pyright: ignore


#=====================================================
# Function - Create Cluster using vAPIv2
#=====================================================
def create_cluster_vapi2(context, cluster_name, pargs):
    """Create a cluster from the Datacenter managed object."""

    # Get the host folder for the Datacenter using the save identifier
    datacenter = pargs.vcenter.datacenter.moid

    folder_summaries = context.client.vcenter.Folder.list(
        Folder.FilterSpec(type=Folder.Type.HOST, datacenters=set([datacenter])))
    folder = folder_summaries[0].folder

    # Create a managed object from the folder identifier
    folder_mo = vim.Folder(folder, context.soap_stub)

    # Configure Cluster Spec for DRS and HA
    cluster_spec = vim.cluster.ConfigSpecEx()
    # Enable DRS
    drs_spec = vim.cluster.DrsConfigInfo()
    drs_spec.enabled = True
    drs_spec.defaultVmBehavior = 'fullyAutomated'
    # Enable HA
    ha_spec = vim.cluster.DasConfigInfo()
    ha_spec.enabled = True
    ha_spec.hostMonitoring = vim.cluster.DasConfigInfo.ServiceState.enabled
    ha_spec.failoverLevel = 1
    # Add drs_spec and ha_spec to the cluster_spec
    cluster_spec.dasConfig = ha_spec
    cluster_spec.drsConfig = drs_spec
    cluster_mo = folder_mo.CreateClusterEx(cluster_name, spec=cluster_spec)
    pargs.vcenter.cluster[cluster_name].moid = cluster_mo

    print("Created Cluster '{}' ({})".format(cluster_mo._moId, cluster_name))
    return pargs


#=====================================================
# Function - Find Cluster and obtain Moid
#=====================================================
def detect_cluster(context, cluster_name, pargs):
    """Find the cluster to run the vcenter samples"""
    filter_spec = Cluster.FilterSpec(names =set([cluster_name]),
                                     datacenters =set([pargs.vcenter.datacenter.moid]))
    cluster_summaries = context.client.vcenter.Cluster.list(filter_spec)

    if len(cluster_summaries) > 0:
        cluster = cluster_summaries[0].cluster
        pargs.vcenter.cluster[cluster_name].moid = cluster
        print("Detected cluster '{}' as {}".format(cluster_name, cluster))
        return True, pargs
    else:
        print("Cluster '{}' not found".format(cluster_name))
        return False, pargs


#=====================================================
# Function - Remove Cluster
#=====================================================
def remove_cluster(context):
    """Delete cluster after vcenter sample run"""
    cluster1_name = context.testbed.config['CLUSTER1_NAME']
    names = set([cluster1_name])

    cluster_summaries = context.client.vcenter.Cluster.list(
        Cluster.FilterSpec(names=names))
    print("Found '{}' Clusters matching names {}".
          format(len(cluster_summaries), ", ".join(["'{}'".
                                                   format(n) for n in names])))

    if len(cluster_summaries) < 1:
        return

    # Delete the cluster using the managed object
    cluster = cluster_summaries[0].cluster
    cluster_mo = vim.ClusterComputeResource(cluster, context.soap_stub)

    print("Deleting Cluster '{}' ({})".format(cluster, cluster1_name))
    task = cluster_mo.Destroy()
    pyVim.task.WaitForTask(task)


def setup_cluster_vim(context):
    """Create a cluster using only the VIM API"""
    cluster1_name = context.testbed.config['CLUSTER1_NAME']

    # Get the host folder for the Datacenter2 using the save identifier
    datacenter_name = context.testbed.config['DATACENTER2_NAME']

    for entity in context.service_instance.content.rootFolder.childEntity:
        if isinstance(entity,
                      vim.Datacenter) and entity.name == datacenter_name:
            folder_mo = entity.hostFolder
            cluster_mo = folder_mo.CreateClusterEx(cluster1_name,
                                                   vim.cluster.ConfigSpecEx())

            print("Created Cluster '{}' ({})".format(cluster_mo._moId,
                                                     cluster1_name))

            context.testbed.entities['CLUSTER_IDS'] = {
                cluster1_name: cluster_mo._moId
            }
            break

