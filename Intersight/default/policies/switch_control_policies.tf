#_________________________________________________________________________
#
# Intersight Switch Control Policies Variables
# GUI Location: Configure > Policy > Create Policy > Switch Control
#_________________________________________________________________________

variable "switch_control_policies" {
  default = {
    default = {
      description                  = ""
      mac_address_table_aging      = "Default"
      mac_aging_time               = 14500
      organization                 = "default"
      tags                         = []
      udld_message_interval        = 15
      udld_recovery_action         = "none"
      vlan_port_count_optimization = false
    }
  }
  description = <<-EOT
  key - Name of the Link Control Policy.
  * description - Description to Assign to the Policy.
  * mac_address_table_aging - This specifies one of the option to configure the MAC address aging time.
    - Custom - This option allows the the user to configure the MAC address aging time on the switch. For Switch Model UCS-FI-6454 or higher, the valid range is 120 to 918000 seconds and the switch will set the lower multiple of 5 of the given time.
    - Default - (Default) This option sets the default MAC address aging time to 14500 seconds for End Host mode.
    - Never - This option disables the MAC address aging process and never allows the MAC address entries to get removed from the table.
  * mac_aging_time  - Define the MAC address aging time in seconds.  Range is between 120 to 918000, in multiples of 5, when mac_aging_option is set to Custom.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * udld_message_interval - Configures the time between UDLD probe messages on ports that are in advertisement mode and arecurrently determined to be bidirectional.  Valid values are from 7 to 90 seconds.  Default is 15.
  * udld_recovery_action - UDLD recovery when enabled, attempts to bring an UDLD error-disabled port out of reset.
    - none - (Default) No action is taken when a port has been disabled.
    - reset - The switch will attempt to bring a UDLD error-disabled port back online.
  * vlan_port_count_optimization - To enable or disable the VLAN port count optimization.  Default is false.
  EOT
  type = map(object(
    {
      description                  = optional(string)
      mac_address_table_aging      = optional(string)
      mac_aging_time               = optional(number)
      organization                 = optional(string)
      tags                         = optional(list(map(string)))
      udld_message_interval        = optional(number)
      udld_recovery_action         = optional(string)
      vlan_port_count_optimization = optional(bool)
    }
  ))
}


#_________________________________________________________________________
#
# Switch Control Policies
# GUI Location: Configure > Policy > Create Policy > Switch Control
#_________________________________________________________________________

module "switch_control_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  source                = "terraform-cisco-modules/imm/intersight//modules/switch_control_policies"
  for_each              = local.switch_control_policies
  description           = each.value.description != "" ? each.value.description : "${each.key} Switch Control Policy."
  name                  = each.key
  mac_aging_option      = each.value.mac_address_table_aging
  mac_aging_time        = each.value.mac_aging_time
  udld_message_interval = each.value.udld_message_interval
  udld_recovery_action  = each.value.udld_recovery_action
  vlan_optimization     = each.value.vlan_port_count_optimization
  org_moid              = local.org_moids[each.value.organization].moid
  tags                  = length(each.value.tags) > 0 ? each.value.tags : local.tags
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].switch_control_policy == each.key
  }
}


