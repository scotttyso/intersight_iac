#_________________________________________________________________________
#
# Intersight Multicast Policy Variables
# GUI Location: Configure > Policies > Create Policy > Multicast > Start
#_________________________________________________________________________

variable "multicast_policies" {
  default = {
    default = {
      description             = ""
      querier_ip_address      = ""
      querier_ip_address_peer = ""
      querier_state           = "Disabled"
      snooping_state          = "Enabled"
      tags                    = []
    }
  }
  description = <<-EOT
  key - Name of the Multicast Policy.
  * description - Description to Assign to the Policy.
  * querier_ip_address - IP Address of the IGMP Querier to Assign to the VLAN through this Policy.
  * querier_ip_address_peer - Used to define the IGMP Querier IP address of the peer switch.
  * querier_state - Administrative state of the IGMP Querier for the VLANs Assigned to this Policy.  Options are:
    - Disabled - (Default)
    - Enabled
  * snooping_state - Administrative State for Snooping for the VLANs Assigned to this Policy.
    - Disabled
    - Enabled - (Default)
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description             = optional(string)
      querier_ip_address      = optional(string)
      querier_ip_address_peer = optional(string)
      querier_state           = optional(string)
      snooping_state          = optional(string)
      tags                    = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Intersight Multicast Policy
# GUI Location: Create > Policy > Create Policy > Multicast > Start
#_________________________________________________________________________

resource "intersight_fabric_multicast_policy" "multicast_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each                = local.multicast_policies
  description             = each.value.description != "" ? each.value.description : "${each.key} Multicast Policy"
  name                    = each.key
  querier_ip_address      = each.value.querier_ip_address
  querier_ip_address_peer = each.value.querier_ip_address_peer
  querier_state           = each.value.querier_state
  snooping_state          = each.value.snooping_state
  organization {
    moid        = local.org_moid
    object_type = "organization.Organization"
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}
