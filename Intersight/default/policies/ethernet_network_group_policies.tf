#_____________________________________________________________________________
#
# Ethernet Network Group Policies (VLAN Groups)
# GUI Location: Configure > Policies > Create Policy > Ethernet Network Group
#_____________________________________________________________________________

variable "ethernet_network_group_policies" {
  default = {
    default = {
      allowed_vlans = "1"
      description   = ""
      native_vlan   = null
      organization  = "default"
      tags          = []
    }
  }
  description = <<-EOT
  key - Name of the Ethernet Network Group Policy
  * allowed_vlans - List of VLAN's to Add to the VLAN Group Policy.
  * description - Description for the Policy.
  * native_vlan - VLAN to Assign as the Native VLAN.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - Default is [].  List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      allowed_vlans = optional(string)
      description   = optional(string)
      native_vlan   = optional(number)
      organization  = optional(string)
      tags          = optional(list(map(string)))
    }
  ))
}

module "ethernet_network_group_policies" {
  depends_on = [
    local.org_moids
  ]
  source        = "terraform-cisco-modules/imm/intersight//modules/ethernet_network_group_policies"
  for_each      = local.ethernet_network_group_policies
  allowed_vlans = each.value.allowed_vlans
  description   = each.value.description != "" ? each.value.description : "${each.key} Ethernet Network Group Policy."
  name          = each.key
  native_vlan   = each.value.native_vlan
  org_moid      = local.org_moids[each.value.organization].moid
  tags          = length(each.value.tags) > 0 ? each.value.tags : local.tags
}
