#_________________________________________________________________________
#
# Intersight Power Policies Variables
# GUI Location: Configure > Policies > Create Policy > Power > Start
#_________________________________________________________________________

variable "power_policies" {
  default = {
    default = {
      allocated_budget    = 0
      description         = ""
      organization        = "default"
      power_profiling     = "Enabled"
      power_restore_state = "LastState"
      redundancy_mode     = "Grid"
      tags                = []
    }
  }
  description = <<-EOT
  key - Name of the Power Policy.
  * allocated_budget - Sets the Allocated Power Budget of the System (in Watts). This field is only supported for Cisco UCS X series Chassis.
  * description - Description to Assign to the Policy.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * power_profiling - Sets the Power Profiling of the Server. This field is only supported for Cisco UCS X series servers.
    - Enabled - Set the value to Enabled.
    - Disabled - Set the value to Disabled.
  * power_restore_state - Sets the Power Restore State of the Server.
    - AlwaysOff - Set the Power Restore Mode to Off.
    - AlwaysOn - Set the Power Restore Mode to On.
    - LastState - Set the Power Restore Mode to LastState.
  * redundancy_mode - Sets the Power Redundancy of the System. N+2 mode is only supported for Cisco UCS X series Chassis.
    - Grid - Grid Mode requires two power sources. If one source fails, the surviving PSUs connected to the other source provides power to the chassis.
    - NotRedundant - Power Manager turns on the minimum number of PSUs required to support chassis power requirements. No Redundant PSUs are maintained.
    - N+1 - Power Manager turns on the minimum number of PSUs required to support chassis power requirements plus one additional PSU for redundancy.
    - N+2 - Power Manager turns on the minimum number of PSUs required to support chassis power requirements plus two additional PSU for redundancy. This Mode is only supported for UCS X series Chassis.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      allocated_budget    = optional(number)
      description         = optional(string)
      organization        = optional(string)
      power_profiling     = optional(string)
      power_restore_state = optional(string)
      redundancy_mode     = optional(string)
      tags                = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Power Policies
# GUI Location: Configure > Policies > Create Policy > Power > Start
#_________________________________________________________________________

module "power_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies
  ]
  source              = "terraform-cisco-modules/imm/intersight//modules/power_policies"
  for_each            = local.power_policies
  allocated_budget    = each.value.allocated_budget
  description         = each.value.description != "" ? each.value.description : "${each.key} Power Policy."
  name                = each.key
  org_moid            = local.org_moids[each.value.organization].moid
  power_profiling     = each.value.power_profiling
  power_restore_state = each.value.power_restore_state
  redundancy_mode     = each.value.redundancy_mode
  tags                = length(each.value.tags) > 0 ? each.value.tags : local.tags
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].power_policy == each.key
  }
}
