#_________________________________________________________________________
#
# Intersight Power Policies Variables
# GUI Location: Configure > Policies > Create Policy > Power > Start
#_________________________________________________________________________

variable "power_policies" {
  default = {
    default = {
      description               = ""
      dynamic_power_rebalancing = "Enabled"
      power_allocation          = 0
      power_priority            = "Low"
      power_profiling           = "Enabled"
      power_redunancy           = "Grid"
      power_restore             = "AlwaysOff"
      power_save_mode           = "Enabled"
      tags                      = []
    }
  }
  description = <<-EOT
  key - Name of the Power Policy.
  * description - Description to Assign to the Policy.
  * dynamic_power_rebalancing - Sets the Dynamic Power Rebalancing of the System. This option is only supported for Cisco UCS X series Chassis.
    - Enabled - Set the value to Enabled.
    - Disabled - Set the value to Disabled.
  * power_allocation - Sets the Allocated Power Budget of the System (in Watts). This field is only supported for Cisco UCS X series Chassis.
  * power_priority - Sets the Power Priority of the System. This field is only supported for Cisco UCS X series servers.
    - Low - Set the value to Low.
    - Medium - Set the value to Medium.
    - High - Set the value to High.
  * power_profiling - Sets the Power Profiling of the Server. This field is only supported for Cisco UCS X series servers.
    - Enabled - Set the value to Enabled.
    - Disabled - Set the value to Disabled.
  * power_redunancy - Sets the Power Redundancy of the System. N+2 mode is only supported for Cisco UCS X series Chassis.
    - Grid - Grid Mode requires two power sources. If one source fails, the surviving PSUs connected to the other source provides power to the chassis.
    - NotRedundant - Power Manager turns on the minimum number of PSUs required to support chassis power requirements. No Redundant PSUs are maintained.
    - N+1 - Power Manager turns on the minimum number of PSUs required to support chassis power requirements plus one additional PSU for redundancy.
    - N+2 - Power Manager turns on the minimum number of PSUs required to support chassis power requirements plus two additional PSU for redundancy. This Mode is only supported for UCS X series Chassis.
  * power_restore - Sets the Power Restore State of the Server.
    - AlwaysOff - Set the Power Restore Mode to Off.
    - AlwaysOn - Set the Power Restore Mode to On.
    - LastState - Set the Power Restore Mode to LastState.
  * power_save_mode - Sets the Power Save mode of the System. This option is only supported for Cisco UCS X series Chassis.
    - Enabled - Set the value to Enabled.
    - Disabled - Set the value to Disabled.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description               = optional(string)
      dynamic_power_rebalancing = optional(string)
      power_allocation          = optional(number)
      power_priority            = optional(string)
      power_profiling           = optional(string)
      power_redunancy           = optional(string)
      power_restore             = optional(string)
      power_save_mode           = optional(string)
      tags                      = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Power Policies
# GUI Location: Configure > Policies > Create Policy > Power > Start
#_________________________________________________________________________

resource "intersight_power_policy" "power_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each = local.power_policies
  additional_properties = jsonencode(
    {
      DynamicRebalancing = each.value.dynamic_power_rebalancing
      PowerPriority      = each.value.power_priority
      PowerSaveMode      = each.value.power_save_mode
    }
  )
  allocated_budget    = each.value.power_allocation
  description         = each.value.description != "" ? each.value.description : "${each.key} Power Policy"
  name                = each.key
  power_profiling     = each.value.power_profiling
  power_restore_state = each.value.power_restore
  redundancy_mode     = each.value.power_redunancy
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
