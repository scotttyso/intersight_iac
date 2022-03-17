#_________________________________________________________________________
#
# Ethernet Network Policies - Standalone Servers
# GUI Location: Configure > Policies > Create Policy > Ethernet Network
#_________________________________________________________________________

variable "ethernet_network_policies" {
  default = {
    default = {
      default_vlan = 0
      description  = ""
      tags         = []
      vlan_mode    = "ACCESS"
    }
  }
  description = <<-EOT
  key - Name of the Ethernet Network Group Policy
  * default_vlan - Default is 0.  Native VLAN ID of the virtual interface or the corresponding vethernet on the peer Fabric Interconnect to which the virtual interface is connected. Setting the ID to 0 will not associate any native VLAN to the traffic on the virtual interface.
  * description - Description for the Policy.
  * tags - Default is [].  List of Key/Value Pairs to Assign as Attributes to the Policy.
  * vlan_mode - Default is ACCESS.  Option to determine if the port can carry single VLAN (Access) or multiple VLANs (Trunk) traffic.
    - ACCESS - An access port carries traffic only for a single VLAN on the interface.
    - TRUNK - A trunk port can have two or more VLANs configured on the interface. It can carry traffic for several VLANs simultaneously.
  EOT
  type = map(object(
    {
      default_vlan = optional(number)
      description  = optional(string)
      tags         = optional(list(map(string)))
      vlan_mode    = optional(string)
    }
  ))
}

#_______________________________________________________________________________
#
# Ethernet Network Policies
# GUI Location: Configure > Policies > Create Policy > Ethernet Network
#_______________________________________________________________________________

resource "intersight_vnic_eth_network_policy" "ethernet_network_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each    = local.ethernet_network_policies
  description = each.value.description != "" ? each.value.description : "${each.key} Ethernet Network Policy."
  name        = each.key
  organization {
    moid        = local.org_moid
    object_type = "organization.Organization"
  }
  vlan_settings {
    allowed_vlans = "" # CSCvx98712.  This is no longer valid for the policy
    default_vlan  = each.value.default_vlan
    mode          = each.value.vlan_mode
    object_type   = "vnic.VlanSettings"
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}
