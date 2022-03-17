#_________________________________________________________________________
#
# Intersight Switch Control Policies Variables
# GUI Location: Configure > Policy > Create Policy > Switch Control
#_________________________________________________________________________

variable "switch_control_policies" {
  default = {
    default = {
      description                  = ""
      ethernet_switching_mode      = "end-host"
      fc_switching_mode            = "end-host"
      mac_address_table_aging      = "Default"
      mac_aging_time               = 14500
      tags                         = []
      udld_message_interval        = 15
      udld_recovery_action         = "none"
      vlan_port_count_optimization = false
    }
  }
  description = <<-EOT
  key - Name of the Link Control Policy.
  * description - Description to Assign to the Policy.
  * ethernet_switching_mode - Enable or Disable Ethernet End Host Switching Mode.
    - end-host - In end-host mode, the fabric interconnects appear to the upstream devices as end hosts with multiple links.  In this mode, the switch does not run Spanning Tree Protocol and avoids loops by following a set of rules for traffic forwarding.  In case of ethernet switching mode - Ethernet end-host mode is also known as Ethernet host virtualizer.
    - switch - In switch mode, the switch runs Spanning Tree Protocol to avoid loops, and broadcast and multicast packets are handled in the traditional way.This is the traditional switch mode.
  * fc_switching_mode - Enable or Disable FC End Host Switching Mode.
    - end-host - In end-host mode, the fabric interconnects appear to the upstream devices as end hosts with multiple links.  In this mode, the switch does not run Spanning Tree Protocol and avoids loops by following a set of rules for traffic forwarding.  In case of ethernet switching mode - Ethernet end-host mode is also known as Ethernet host virtualizer.
    - switch - In switch mode, the switch runs Spanning Tree Protocol to avoid loops, and broadcast and multicast packets are handled in the traditional way.This is the traditional switch mode.
  * mac_address_table_aging - This specifies one of the option to configure the MAC address aging time.
    - Custom - This option allows the the user to configure the MAC address aging time on the switch. For Switch Model UCS-FI-6454 or higher, the valid range is 120 to 918000 seconds and the switch will set the lower multiple of 5 of the given time.
    - Default - (Default) This option sets the default MAC address aging time to 14500 seconds for End Host mode.
    - Never - This option disables the MAC address aging process and never allows the MAC address entries to get removed from the table.
  * mac_aging_time  - Define the MAC address aging time in seconds.  Range is between 120 to 918000, in multiples of 5, when mac_aging_option is set to Custom.
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
      ethernet_switching_mode      = optional(string)
      fc_switching_mode            = optional(string)
      mac_address_table_aging      = optional(string)
      mac_aging_time               = optional(number)
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

resource "intersight_fabric_switch_control_policy" "switch_control_policies" {
  depends_on = [
    local.org_moid,
    local.ucs_domain_policies
  ]
  for_each                       = local.switch_control_policies
  description                    = each.value.description != "" ? each.value.description : "${each.key} Switch Control Policy"
  ethernet_switching_mode        = each.value.ethernet_switching_mode
  fc_switching_mode              = each.value.fc_switching_mode
  name                           = each.key
  vlan_port_optimization_enabled = each.value.vlan_port_count_optimization
  mac_aging_settings {
    mac_aging_option = each.value.mac_address_table_aging
    mac_aging_time   = each.value.mac_address_table_aging == "Custom" ? each.value.mac_aging_time : null
  }
  organization {
    moid        = local.org_moid
    object_type = "organization.Organization"
  }
  udld_settings {
    message_interval = each.value.udld_message_interval
    recovery_action  = each.value.udld_recovery_action
  }
  dynamic "profiles" {
    for_each = { for k, v in local.ucs_domain_policies : k => v if local.ucs_domain_policies[k].switch_control_policy == each.key }
    content {
      moid        = profiles.value.moid
      object_type = profiles.value.object_type
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
