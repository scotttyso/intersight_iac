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

module "device_connector_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  source                = "terraform-cisco-modules/imm/intersight//modules/device_connector_policies"
  for_each              = local.device_connector_policies
  configuration_lockout = each.value.configuration_lockout
  description           = each.value.description != "" ? each.value.description : "${each.key} Device Connector Policy."
  name                  = each.key
  org_moid              = local.org_moids[each.value.organization].moid
  tags                  = length(each.value.tags) > 0 ? each.value.tags : local.tags
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].device_connector_policy == each.key
  }
}
