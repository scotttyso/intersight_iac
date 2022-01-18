#_________________________________________________________________________
#
# Intersight Device Connector Policies Variables
# GUI Location: Configure > Policies > Create Policy > Device Connector
#_________________________________________________________________________

variable "device_connector_policies" {
  default = {
    default = {
      configuration_lockout = false
      description           = ""
      organization          = "default"
      tags                  = []
    }
  }
  description = <<-EOT
  key - Name of the Device Connector Policy.
  * configuration_lockout - Locks Down Configuration to Intersight Only.
  * description - Description to Assign to the Policy.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      configuration_lockout = optional(bool)
      description           = optional(string)
      organization          = optional(string)
      tags                  = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Device Connector Policies
# GUI Location: Configure > Policies > Create Policy > Device Connector
#_________________________________________________________________________

resource "intersight_deviceconnector_policy" "device_connector_policies" {
  depends_on = [
    local.org_moids
  ]
  for_each        = local.device_connector_policies
  description     = each.value.description != "" ? each.value.description : "${each.key} Device Connector Policy"
  lockout_enabled = each.value.configuration_lockout
  name            = each.key
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
}