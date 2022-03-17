#_________________________________________________________________________
#
# Intersight UCS Chassis Profile Variables
# GUI Location: Profiles > UCS Chassis Profile > Create UCS Chassis Profile
#_________________________________________________________________________

variable "ucs_chassis_profiles" {
  default = {
    default = {
      action              = "No-op"
      assign_chassis      = false
      imc_access_policy   = ""
      power_policy        = ""
      snmp_policy         = ""
      target_platform     = "FIAttached"
      thermal_policy      = ""
      description         = ""
      serial_number       = ""
      tags                = []
      wait_for_completion = false
    }
  }
  description = <<-EOT
  key - Name for the Chassis.
  * action - Action to Perform on the Chassis Profile Assignment.  Options are:
    - Deploy
    - No-op
    - Unassign
  * assign_chassis - Set flag to True to Assign the Profile to a Physical Chassis Serial Number.
  * description - Description for the Profile.
  * imc_access_policy - Name of the IMC Access Policy to Assign.
  * power_policy - Name of the Power Policy to Assign.
  * serial_number - Serial Number of the Chassis to Assign.
  * snmp_policy - Name of the SNMP Policy to Assign.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * target_platform - The platform for which the chassis profile is applicable. It can either be a chassis that is operating in standalone mode or which is attached to a Fabric Interconnect managed by Intersight.
    - FIAttached - Chassis which are connected to a Fabric Interconnect that is managed by Intersight.
  * thermal_policy - Name of the Thermal Policy to Assign.
  * wait_for_completion -
  EOT
  type = map(object(
    {
      action              = optional(string)
      assign_chassis      = optional(bool)
      description         = optional(string)
      imc_access_policy   = optional(string)
      power_policy        = optional(string)
      serial_number       = optional(string)
      snmp_policy         = optional(string)
      target_platform     = optional(string)
      thermal_policy      = optional(string)
      tags                = optional(list(map(string)))
      wait_for_completion = optional(bool)
    }
  ))
}


#_________________________________________________________________________
#
# Intersight UCS Chassis Profile Module
# GUI Location: Profiles > UCS Chassis Profile > Create UCS Chassis Profile
#_________________________________________________________________________

resource "intersight_chassis_profile" "ucs_chassis_profiles" {
  depends_on = [
    local.org_moid
  ]
  for_each            = local.ucs_chassis_profiles
  action              = each.value.action
  description         = each.value.description != "" ? each.value.description : "${each.key} Chassis Profile."
  name                = each.key
  target_platform     = each.value.target_platform == "Standalone" ? "Standalone" : "FIAttached"
  type                = "instance"
  wait_for_completion = each.value.wait_for_completion
  organization {
    moid        = local.org_moid
    object_type = "organization.Organization"
  }
  dynamic "assigned_chassis" {
    for_each = each.value.assign_chassis == true ? [
      {
        moid = data.intersight_equipment_chassis.chassis[each.key].results[0].moid
      }
    ] : []
    content {
      moid = assigned_chassis.value.moid
    }
  }
  dynamic "policy_bucket" {
    for_each = [for s in each.value.policy_bucket : s if s != null]
    content {
      moid        = policy_bucket.value.moid
      object_type = policy_bucket.value.object_type
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
