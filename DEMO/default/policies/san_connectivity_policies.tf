#_________________________________________________________________________
#
# Intersight SAN Connectivity Policies Variables
# GUI Location: Configure > Policies > Create Policy > SAN Connectivity
#_________________________________________________________________________

variable "san_connectivity_policies" {
  default = {
    default = {
      description          = ""
      organization         = "default"
      tags                 = []
      target_platform      = "FIAttached"
      vhba_placement_mode  = "custom"
      wwnn_allocation_type = "POOL"
      wwnn_pool            = ""
      wwnn_static_address  = ""
      vhbas = {
        default = {
          fibre_channel_adapter_policy = "**REQUIRED**"
          fibre_channel_network_policy = "**REQUIRED**"
          fibre_channel_qos_policy     = "**REQUIRED**"
          name                         = "vhba"
          persistent_lun_bindings      = false
          placement_pci_link           = 0
          placement_pci_order          = 0
          placement_slot_id            = "MLOM"
          placement_switch_id          = "None"
          placement_uplink_port        = 0
          vhba_type                    = "fc-initiator"
          wwpn_allocation_type         = "POOL"
          wwpn_pool                    = ""
          wwpn_static_address          = ""
        }
      }
    }
  }
  description = <<-EOT
  key - Name of the SAN Connectivity Policy.
  * description - Description to Assign to the Policy.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * target_platform - The platform for which the server profile is applicable. It can either be:
    - FIAttached (Default) - A Server attached to a Intersight Managed Domain.
    - Standalone - a server that is operating independently
  * vhba_placement_mode - The mode used for placement of vNICs on network adapters. It can either be Auto or Custom.
    - auto - The placement of the vNICs / vHBAs on network adapters is automatically determined by the system.
    - custom (Default) - The placement of the vNICs / vHBAs on network adapters is manually chosen by the user.
  * wwnn_allocation_type - Type of allocation selected to assign a WWNN address for the server node.
    - POOL (Default) - The user selects a pool from which the mac/wwn address will be leased for the Virtual Interface.
    - STATIC - The user assigns a static mac/wwn address for the Virtual Interface.
  * wwnn_pool - WWNN Pool to Assign to the Policy.
  * wwnn_static_address - The WWNN address for the server node must be in hexadecimal format xx:xx:xx:xx:xx:xx:xx:xx.Allowed ranges are 20:00:00:00:00:00:00:00 to 20:FF:FF:FF:FF:FF:FF:FF or from 50:00:00:00:00:00:00:00 to 5F:FF:FF:FF:FF:FF:FF:FF.To ensure uniqueness of WWN's in the SAN fabric, you are strongly encouraged to use the WWN prefix - 20:00:00:25:B5:xx:xx:xx.
  * vhbas - List of vHBAs to add to the SAN Connectivity Policy.
    - fibre_channel_adapter_policy - The Name of the Fibre Channel Adapter Policy to Assign to the vHBA.
    - fibre_channel_network_policy - The Name of the Fibre Channel Network Policy to Assign to the vHBA.
    - fibre_channel_qos_policy - The Name of the Fibre Channel QoS Policy to Assign to the vHBA.
    - name - Name of the virtual fibre channel interface.
    - persistent_lun_bindings - Default is false.  Enables retention of LUN ID associations in memory until they are manually cleared.
    - placement_pci_link - Default is 0.  The PCI Link used as transport for the virtual interface. All VIC adapters have a single PCI link except VIC 1385 which has two.
    - placement_pci_order - Default is 0.  The order in which the virtual interface is brought up. The order assigned to an interface should be unique for all the Ethernet and Fibre-Channel interfaces on each PCI link on a VIC adapter. The maximum value of PCI order is limited by the number of virtual interfaces (Ethernet and Fibre-Channel) on each PCI link on a VIC adapter. All VIC adapters have a single PCI link except VIC 1385 which has two.
    - placement_slot_id - Default is MLOM.  PCIe Slot where the VIC adapter is installed. Supported values are (1-15) and MLOM.
    - placement_switch_id - The fabric port to which the vNICs will be associated.
      1. A - Fabric A of the FI cluster.
      2. B - Fabric B of the FI cluster.
      3. None (Default) - Fabric Id is not set to either A or B for the standalone case where the server is not connected to Fabric Interconnects. The value 'None' should be used.
    - placement_uplink_port - Default is 0.  Adapter port on which the virtual interface will be created.  This attribute is for Standalone Servers Only.
    - vhba_type - VHBA Type configuration for SAN Connectivity Policy. This configuration is supported only on Cisco VIC 14XX series and higher series of adapters.
      1. fc-initiator (Default) - The default value set for vHBA Type Configuration. Fc-initiator specifies vHBA as a consumer of storage. Enables SCSI commands to transfer data and status information between host and target storage systems.
      2. fc-nvme-initiator - Fc-nvme-initiator specifies vHBA as a consumer of storage. Enables NVMe-based message commands to transfer data and status information between host and target storage systems.
      3. fc-nvme-target - Fc-nvme-target specifies vHBA as a provider of storage volumes to initiators. Enables NVMe-based message commands to transfer data and status information between host and target storage systems. Currently tech-preview, only enabled with an asynchronous driver.
      4. fc-target - Fc-target specifies vHBA as a provider of storage volumes to initiators. Enables SCSI commands to transfer data and status information between host and target storage systems. fc-target is enabled only with an asynchronous driver.
    - wwpn_allocation_type -  Type of allocation selected to assign a WWPN address to the vhba.
      1. POOL - The user selects a pool from which the mac/wwn address will be leased for the Virtual Interface.
      2. STATIC - The user assigns a static mac/wwn address for the Virtual Interface.
    - wwpn_static_address -  The WWPN address must be in hexadecimal format xx:xx:xx:xx:xx:xx:xx:xx.  Allowed ranges are 20:00:00:00:00:00:00:00 to 20:FF:FF:FF:FF:FF:FF:FF or from 50:00:00:00:00:00:00:00 to 5F:FF:FF:FF:FF:FF:FF:FF.  To ensure uniqueness of WWN's in the SAN fabric, you are strongly encouraged to use the WWN prefix - 20:00:00:25:B5:xx:xx:xx.
  EOT
  type = map(object(
    {
      description          = optional(string)
      organization         = optional(string)
      tags                 = optional(list(map(string)))
      target_platform      = optional(string)
      vhba_placement_mode  = optional(string)
      wwnn_allocation_type = optional(string)
      wwnn_pool            = optional(string)
      wwnn_static_address  = optional(string)
      vhbas = optional(map(object(
        {
          fibre_channel_adapter_policy = string
          fibre_channel_network_policy = string
          fibre_channel_qos_policy     = string
          name                         = string
          persistent_lun_bindings      = optional(bool)
          placement_pci_link           = optional(number)
          placement_pci_order          = optional(number)
          placement_slot_id            = optional(string)
          placement_switch_id          = optional(string)
          placement_uplink_port        = optional(number)
          vhba_type                    = optional(string)
          wwpn_allocation_type         = optional(string)
          wwpn_pool                    = optional(string)
          wwpn_static_address          = optional(string)
        }
      )))
    }
  ))
}


#_________________________________________________________________________
#
# SAN Connectivity Policies
# GUI Location: Configure > Policies > Create Policy > SAN Connectivity
#_________________________________________________________________________

resource "intersight_vnic_san_connectivity_policy" "san_connectivity_policies" {
  depends_on = [
    local.org_moids
  ]
  for_each            = local.san_connectivity_policies
  description         = each.value.description != "" ? each.value.description : "${each.key} SAN Connectivity Policy"
  name                = each.key
  placement_mode      = each.value.vhba_placement_mode
  static_wwnn_address = each.value.wwnn_allocation_type == "STATIC" ? each.value.wwnn_static_address : ""
  target_platform     = each.value.target_platform
  wwnn_address_type   = each.value.wwnn_allocation_type
  organization {
    moid        = local.org_moids[each.value.organization].moid
    object_type = "organization.Organization"
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
  dynamic "wwnn_pool" {
    for_each = each.value.wwnn_allocation_type == "POOL" ? [local.wwnn_pools[each.value.wwnn_pool]] : []
    content {
      moid = wwnn_pool.value
    }
  }
}


#_________________________________________________________________________
#
# SAN Connectivity Policy - Create vHBAs
# GUI Location: Configure > Policies > Create Policy > SAN Connectivity
#_________________________________________________________________________

resource "intersight_vnic_fc_if" "vhbas" {
  depends_on = [
    local.org_moids,
    intersight_vnic_fc_adapter_policy.fibre_channel_adapter_policies,
    intersight_vnic_fc_network_policy.fibre_channel_network_policies,
    intersight_vnic_fc_qos_policy.fibre_channel_qos_policies,
    intersight_vnic_san_connectivity_policy.san_connectivity_policies
  ]
  for_each            = local.vhbas
  name                = each.value.name
  order               = each.value.placement_pci_order
  persistent_bindings = each.value.persistent_lun_bindings
  static_wwpn_address = each.value.wwpn_allocation_type == "STATIC" ? each.value.wwpn_static_address : ""
  type                = each.value.vhba_type
  wwpn_address_type   = each.value.wwpn_allocation_type
  fc_adapter_policy {
    moid = intersight_vnic_fc_adapter_policy.fibre_channel_adapter_policies[
      each.value.fibre_channel_adapter_policy
    ].moid
  }
  fc_network_policy {
    moid = intersight_vnic_fc_network_policy.fibre_channel_network_policies[
      each.value.fibre_channel_network_policy
    ].moid
  }
  fc_qos_policy {
    moid = intersight_vnic_fc_qos_policy.fibre_channel_qos_policies[
      each.value.fibre_channel_qos_policy
    ].moid
  }
  san_connectivity_policy {
    moid = intersight_vnic_san_connectivity_policy.san_connectivity_policies[
      each.value.san_connectivity_policy
    ].moid
  }
  placement {
    id        = each.value.placement_slot_id
    pci_link  = each.value.placement_pci_link
    switch_id = each.value.placement_switch_id
    uplink    = each.value.placement_uplink_port
  }
  dynamic "wwpn_pool" {
    for_each = each.value.wwpn_allocation_type == "POOL" ? [local.wwpn_pools[each.value.wwpn_pool]] : []
    content {
      moid = wwpn_pool.value
    }
  }
}
