#________________________________________________________________
#
# Fibre Channel Network Policies
# GUI Location: Policies > Create Policy > Fibre Channel Network
#________________________________________________________________

variable "fibre_channel_network_policies" {
  default = {
    default = {
      default_vlan_id = 0
      description     = ""
      organization    = "default"
      tags            = []
      vsan_id         = 4
    }
  }
  description = <<-EOT
  key - Name of the Fibre Channel Network Policy
  * default_vlan_id - Default is 0.  Only required for Standalone Servers.  Default VLAN of the virtual interface in Standalone Rack server. Setting the value to 0 is equivalent to None and will not associate any Default VLAN to the traffic on the virtual interface (0-4094).
  * description - Description for the Policy.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - Default is [].  List of Key/Value Pairs to Assign as Attributes to the Policy.
  * vsan_id - Required.  VSAN ID of the virtual interface in FI attached server (1-4094).
  EOT
  type = map(object(
    {
      default_vlan_id = optional(number)
      description     = optional(string)
      organization    = optional(string)
      tags            = optional(list(map(string)))
      vsan_id         = number
    }
  ))
}

#_______________________________________________________________________________
#
# Fibre-Channel Network Policies
# GUI Location: Configure > Policies > Create Policy > Fibre-Channel Network
#_______________________________________________________________________________

resource "intersight_vnic_fc_network_policy" "fibre_channel_network_policies" {
  depends_on = [
    local.org_moids
  ]
  for_each    = local.fibre_channel_network_policies
  description = each.value.description != "" ? each.value.description : "${each.key} Fibre Channel Network Policy"
  name        = each.key
  organization {
    moid        = local.org_moids[each.value.organization].moid
    object_type = "organization.Organization"
  }
  vsan_settings {
    default_vlan_id = each.value.default_vlan_id
    id              = each.value.vsan_id
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}
