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
      organization = "default"
      tags         = []
      vlan_mode    = "ACCESS"
    }
  }
  description = <<-EOT
  key - Name of the Ethernet Network Group Policy
  * default_vlan - Default is 0.  Native VLAN ID of the virtual interface or the corresponding vethernet on the peer Fabric Interconnect to which the virtual interface is connected. Setting the ID to 0 will not associate any native VLAN to the traffic on the virtual interface.
  * description - Description for the Policy.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - Default is [].  List of Key/Value Pairs to Assign as Attributes to the Policy.
  * vlan_mode - Default is ACCESS.  Option to determine if the port can carry single VLAN (Access) or multiple VLANs (Trunk) traffic.
    - ACCESS - An access port carries traffic only for a single VLAN on the interface.
    - TRUNK - A trunk port can have two or more VLANs configured on the interface. It can carry traffic for several VLANs simultaneously.
  EOT
  type = map(object(
    {
      default_vlan = optional(number)
      description  = optional(string)
      organization = optional(string)
      tags         = optional(list(map(string)))
      vlan_mode    = optional(string)
    }
  ))
}

module "ethernet_network_policies" {
  depends_on = [
    local.org_moids
  ]
  version      = ">=0.9.6"
  source       = "terraform-cisco-modules/imm/intersight//modules/ethernet_network_policies"
  for_each     = local.ethernet_network_policies
  description  = each.value.description != "" ? each.value.description : "${each.key} Ethernet Network Policy."
  name         = each.key
  default_vlan = each.value.default_vlan
  org_moid     = local.org_moids[each.value.organization].moid
  tags         = length(each.value.tags) > 0 ? each.value.tags : local.tags
  vlan_mode    = each.value.vlan_mode
}
