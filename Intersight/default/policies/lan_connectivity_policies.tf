#_________________________________________________________________________
#
# Intersight LAN Connectivity Policies Variables
# GUI Location: Configure > Policies > Create Policy > LAN Connectivity
#_________________________________________________________________________

variable "lan_connectivity_policies" {
  default = {
    default = {
      description                 = ""
      enable_azure_stack_host_qos = false
      iqn_allocation_type         = "None"
      iqn_pool                    = ""
      iqn_static_identifier       = ""
      tags                        = []
      target_platform             = "FIAttached"
      vnic_placement_mode         = "custom"
      vnics = {
        default = {
          cdn_source                             = "vnic"
          cdn_value                              = ""
          enable_failover                        = false
          ethernet_adapter_policy                = "**REQUIRED**"
          ethernet_network_control_policy        = "**REQUIRED**"
          ethernet_network_group_policy          = ""
          ethernet_network_policy                = ""
          ethernet_qos_policy                    = "**REQUIRED**"
          iscsi_boot_policy                      = ""
          mac_address_allocation_type            = "POOL"
          mac_address_pool                       = ""
          mac_address_static                     = ""
          name                                   = "vnic"
          placement_pci_link                     = 0
          placement_pci_order                    = 0
          placement_slot_id                      = "MLOM"
          placement_switch_id                    = "None"
          placement_uplink_port                  = 0
          usnic_adapter_policy                   = ""
          usnic_class_of_service                 = 5
          usnic_number_of_usnics                 = 0
          vmq_enable_virtual_machine_multi_queue = false
          vmq_enabled                            = false
          vmq_number_of_interrupts               = 16
          vmq_number_of_sub_vnics                = 64
          vmq_number_of_virtual_machine_queues   = 4
          vmq_vmmq_adapter_policy                = ""
        }
      }
    }
  }
  description = <<-EOT
  key - Name of the LAN Connectivity Policy.
  * description - Description to Assign to the Policy.
  * enable_azure_stack_host_qos -  Default is false.  Enabling AzureStack-Host QoS on an adapter allows the user to carve out traffic classes for RDMA traffic which ensures that a desired portion of the bandwidth is allocated to it.
  * iqn_allocation_type - Default is None.  Allocation Type of iSCSI Qualified Name.  Options are:
    - None
    - Pool
    - Static
  * iqn_pool - IQN Pool to Assign to the Policy.
  * iqn_static_identifier - User provided static iSCSI Qualified Name (IQN) for use as initiator identifiers by iSCSI vNICs.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * target_platform - The platform for which the server profile is applicable. It can either be:
    - Standalone - a server that is operating independently
    - FIAttached - A Server attached to a Intersight Managed Domain.
  * vnic_placement_mode - Default is custom.  The mode used for placement of vNICs on network adapters. Options are:
    - auto
    - custom
  * vnics - List of VNICs to add to the LAN Connectivity Policy.
    - cdn_source - Default is vnic.  Source of the CDN. It can either be user specified or be the same as the vNIC name.
      1. user - Source of the CDN is specified by the user.
      2. vnic - Source of the CDN is the same as the vNIC name.
    - cdn_value - The CDN value entered in case of user defined mode.
    - enable_failover - Default is false.  Setting this to true ensures that the traffic failover from one uplink to another auotmatically in case of an uplink failure. It is applicable for Cisco VIC adapters only which are connected to Fabric Interconnect cluster. The uplink if specified determines the primary uplink in case of a failover.
    - ethernet_adapter_policy - The Name of the Ethernet Adapter Policy to Assign to the vNIC.
    - ethernet_network_control_policy - The Name of the Ethernet Network Control Policy to Assign to the vNIC.
    - ethernet_network_group_policy - The Name of the Ethernet Network Group Policy to Assign to the vNIC.  This Policy is for FIAttached Only.
    - ethernet_network_policy - The Name of the Ethernet Network Policy to Assign to the vNIC.  This is for Standalone Only.
    - ethernet_qos_policy - The Name of the Ethernet QoS Policy to Assign to the vNIC.
    - iscsi_boot_policy - The Name of the iSCSI Boot Policy to Assign to the vNIC.
    - mac_address_allocation_type - Default is POOL.  Type of allocation selected to assign a MAC address for the vnic.
      1. POOL - The user selects a pool from which the mac/wwn address will be leased for the Virtual Interface.
      2. STATIC - The user assigns a static mac/wwn address for the Virtual Interface.
    - mac_address_pool - The Name of the MAC Address Pool to Assign to the vNIC.
    - mac_address_static - The MAC address must be in hexadecimal format xx:xx:xx:xx:xx:xx.To ensure uniqueness of MACs in the LAN fabric, you are strongly encouraged to use thefollowing MAC prefix 00:25:B5:xx:xx:xx.
    - name - Name of the vNIC.
    - placement_pci_link - Default is 0.  The PCI Link used as transport for the virtual interface. All VIC adapters have a single PCI link except VIC 1385 which has two.
    - placement_pci_order - Default is 0.  The order in which the virtual interface is brought up. The order assigned to an interface should be unique for all the Ethernet and Fibre-Channel interfaces on each PCI link on a VIC adapter. The maximum value of PCI order is limited by the number of virtual interfaces (Ethernet and Fibre-Channel) on each PCI link on a VIC adapter. All VIC adapters have a single PCI link except VIC 1385 which has two.
    - placement_slot_id - Default is MLOM.  PCIe Slot where the VIC adapter is installed. Supported values are (1-15) and MLOM.
    - placement_switch_id - Default is None.  The fabric port to which the vNICs will be associated.
      1. A - Fabric A of the FI cluster.
      2. B - Fabric B of the FI cluster.
      3. None - Fabric Id is not set to either A or B for the standalone case where the server is not connected to Fabric Interconnects. The value 'None' should be used.
    - placement_uplink_port - Default is 0.  Adapter port on which the virtual interface will be created.  This attribute is for Standalone Servers Only.
    - usnic_adapter_policy - Name of the Ethernet Adapter Policy to Assign to the uSNIC Settings.
    - usnic_class_of_service -  Default is 5.  Class of Service to be used for traffic on the usNIC.  Valid Range is 0-6.
    - usnic_number_of_usnics -  Default is 0.  Number of usNIC interfaces to be created.  Range is 0-255.
    - vmq_enable_virtual_machine_multi_queue -  Default is false.  Enables Virtual Machine Multi-Queue feature on the virtual interface. VMMQ allows configuration of multiple I/O queues for a single VM and thus distributes traffic across multiple CPU cores in a VM.
    - vmq_enabled -Default is false.  Enables VMQ feature on the virtual interface.
    - vmq_number_of_interrupts -  Default is 16.  The number of interrupt resources to be allocated. Recommended value is the number of CPU threads or logical processors available in the server.  Range is 1-514.
    - vmq_number_of_sub_vnics -  Default is 64.  The number of sub vNICs to be created.  Range is 0-64.
    - vmq_number_of_virtual_machine_queues -  Default is 4.  The number of hardware Virtual Machine Queues to be allocated. The number of VMQs per adapter must be one more than the maximum number of VM NICs.  Range is 1-128.
    - vmq_vmmq_adapter_policy -  Ethernet Adapter policy to be associated with the VMQ vNICs. The Transmit Queue and Receive Queue resource value of VMMQ adapter policy should be greater than or equal to the configured number of sub vNICs.
  EOT
  type = map(object(
    {
      description                 = optional(string)
      enable_azure_stack_host_qos = optional(bool)
      iqn_allocation_type         = optional(string)
      iqn_pool                    = optional(string)
      iqn_static_identifier       = optional(string)
      tags                        = optional(list(map(string)))
      target_platform             = optional(string)
      vnic_placement_mode         = optional(string)
      vnics = optional(map(object(
        {
          cdn_source                             = optional(string)
          cdn_value                              = optional(string)
          enable_failover                        = optional(bool)
          ethernet_adapter_policy                = string
          ethernet_network_control_policy        = string
          ethernet_network_group_policy          = optional(string)
          ethernet_network_policy                = optional(string)
          ethernet_qos_policy                    = string
          iscsi_boot_policy                      = optional(string)
          mac_address_allocation_type            = optional(string)
          mac_address_pool                       = optional(string)
          mac_address_static                     = optional(string)
          name                                   = string
          placement_pci_link                     = optional(number)
          placement_pci_order                    = optional(number)
          placement_slot_id                      = optional(string)
          placement_switch_id                    = optional(string)
          placement_uplink_port                  = optional(number)
          usnic_adapter_policy                   = optional(string)
          usnic_class_of_service                 = optional(number)
          usnic_number_of_usnics                 = optional(number)
          vmq_enable_virtual_machine_multi_queue = optional(bool)
          vmq_enabled                            = optional(bool)
          vmq_number_of_interrupts               = optional(number)
          vmq_number_of_sub_vnics                = optional(number)
          vmq_number_of_virtual_machine_queues   = optional(number)
          vmq_vmmq_adapter_policy                = optional(string)
        }
      )))
    }
  ))
}


#_________________________________________________________________________
#
# LAN Connectivity Policies
# GUI Location: Configure > Policies > Create Policy > LAN Connectivity
#_________________________________________________________________________

resource "intersight_vnic_lan_connectivity_policy" "lan_connectivity_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each            = var.lan_connectivity_policies
  description         = each.value.description != "" ? each.value.description : "${each.key} LAN Connectivity Policy"
  azure_qos_enabled   = each.value.enable_azure_stack_host_qos
  iqn_allocation_type = each.value.iqn_allocation_type
  name                = each.key
  placement_mode      = each.value.vnic_placement_mode
  static_iqn_name     = each.value.iqn_allocation_type == "Static" ? each.value.iqn_static_identifier : ""
  target_platform     = each.value.target_platform
  organization {
    moid        = local.org_moid
    object_type = "organization.Organization"
  }
  dynamic "iqn_pool" {
    for_each = each.value.iqn_allocation_type == "Pool" ? [local.iqn_pools[each.value.iqn_pool]] : []
    content {
      moid = iqn_pool.value
    }
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}


#_________________________________________________________________________
#
# LAN Connectivity Policy - Create vNICs
# GUI Location: Configure > Policies > Create Policy > LAN Connectivity
#_________________________________________________________________________

resource "intersight_vnic_eth_if" "vnics" {
  depends_on = [
    local.org_moid,
    intersight_vnic_eth_adapter_policy.ethernet_adapter_policies,
    intersight_fabric_eth_network_control_policy.ethernet_network_control_policies,
    intersight_fabric_eth_network_group_policy.ethernet_network_group_policies,
    intersight_vnic_eth_network_policy.ethernet_network_policies,
    intersight_vnic_eth_qos_policy.ethernet_qos_policies,
    intersight_vnic_iscsi_boot_policy.iscsi_boot_policies,
    intersight_vnic_lan_connectivity_policy.lan_connectivity_policies
  ]
  for_each           = local.vnics
  failover_enabled   = each.value.enable_failover
  mac_address_type   = each.value.mac_address_allocation_type
  name               = each.value.name
  order              = each.value.placement_pci_order
  static_mac_address = each.value.mac_address_allocation_type == "STATIC" ? each.value.mac_address_static : null
  cdn {
    value     = each.value.cdn_source == "user" ? each.value.cdn_value : each.value.name
    nr_source = each.value.cdn_source
  }
  eth_adapter_policy {
    moid = intersight_vnic_eth_adapter_policy.ethernet_adapter_policies[
      each.value.ethernet_adapter_policy
    ].moid
  }
  eth_qos_policy {
    moid = intersight_vnic_eth_qos_policy.ethernet_qos_policies[
      each.value.ethernet_qos_policy
    ].moid
  }
  fabric_eth_network_control_policy {
    moid = intersight_fabric_eth_network_control_policy.ethernet_network_control_policies[
      each.value.ethernet_network_control_policy
    ].moid
  }
  lan_connectivity_policy {
    moid = intersight_vnic_lan_connectivity_policy.lan_connectivity_policies[
      each.value.lan_connectivity_policy
    ].moid
  }
  placement {
    id        = each.value.placement_slot_id
    pci_link  = each.value.placement_pci_link
    switch_id = each.value.placement_switch_id
    uplink    = each.value.placement_uplink_port
  }
  usnic_settings {
    cos      = each.value.usnic_class_of_service
    nr_count = each.value.usnic_number_of_usnics
    usnic_adapter_policy = length(
      regexall("[a-zA-Z0-9]+", each.value.usnic_adapter_policy)
      ) > 0 ? intersight_vnic_eth_adapter_policy.ethernet_adapter_policies[
      each.value.usnic_adapter_policy
    ].moid : ""
  }
  vmq_settings {
    enabled             = each.value.vmq_enabled
    multi_queue_support = each.value.vmq_enable_virtual_machine_multi_queue
    num_interrupts      = each.value.vmq_number_of_interrupts
    num_vmqs            = each.value.vmq_number_of_virtual_machine_queues
    num_sub_vnics       = each.value.vmq_number_of_sub_vnics
    vmmq_adapter_policy = length(
      regexall("[a-zA-Z0-9]+", each.value.vmq_vmmq_adapter_policy)
      ) > 0 ? intersight_vnic_eth_adapter_policy.ethernet_adapter_policies[
      each.value.vmq_vmmq_adapter_policy
    ].moid : ""
  }
  dynamic "eth_network_policy" {
    for_each = length(
      regexall("[a-zA-Z0-9]+", each.value.ethernet_network_policy)
      ) > 0 ? [intersight_vnic_eth_network_policy.ethernet_network_policies[
        each.value.ethernet_network_policy
    ].moid] : []
    content {
      moid = eth_network_policy.value
    }
  }
  dynamic "fabric_eth_network_group_policy" {
    for_each = length(
      regexall("[a-zA-Z0-9]+", each.value["ethernet_network_group_policy"])
      ) > 0 ? [intersight_fabric_eth_network_group_policy.ethernet_network_group_policies[
        each.value.ethernet_network_group_policy
    ].moid] : []
    content {
      moid = fabric_eth_network_group_policy.value
    }
  }
  dynamic "iscsi_boot_policy" {
    for_each = length(
      regexall("[a-zA-Z0-9]+", each.value.iscsi_boot_policy)
      ) > 0 ? [intersight_vnic_iscsi_boot_policy.iscsi_boot_policies[
        each.value.iscsi_boot_policy
    ].moid] : []
    content {
      moid = iscsi_boot_policy.value
    }
  }
  dynamic "mac_pool" {
    for_each = each.value.mac_address_allocation_type == "POOL" ? [
      local.mac_pools[each.value.mac_address_pool]
    ] : []
    content {
      moid = mac_pool.value
    }
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}
