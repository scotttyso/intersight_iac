#_________________________________________________________________________
#
# Ethernet Network Control Policies
# GUI Location: Configure > Policies > Create Policy > Ethernet Network Control
#_________________________________________________________________________

variable "ethernet_network_control_policies" {
  default = {
    default = {
      action_on_uplink_fail = "linkDown"
      cdp_enable            = false
      description           = ""
      lldp_enable_receive   = false
      lldp_enable_transmit  = false
      mac_register_mode     = "nativeVlanOnly"
      mac_security_forge    = "allow"
      tags                  = []
    }
  }
  description = <<-EOT
  key - Name of the Policy
  * action_on_uplink_fail - Default is linkDown.  Determines the state of the virtual interface (vethernet / vfc) on the switch when a suitable uplink is not pinned.  Options are:
    - linkDown
    - warning
    Important! If the Action on Uplink is set to Warning, the switch will not fail over if uplink connectivity is lost.
  * cdp_enable - Default is false.  Flag to Enable or Disable CDP on an interface.
  * description - Description for the Policy.
  * lldp_enable_receive - Default is false.  Determines if the LLDP frames can be received by an interface on the switch.
  * lldp_enable_transmit - Default is false.  Determines if the LLDP frames can be transmitted by an interface on the switch.
  * mac_register_mode - Default is nativeVlanOnly.  Determines the MAC addresses that have to be registered with the switch.  Options are:
    - allVlans
    - nativeVlanOnly
  * mac_security_forge - Default is allow.  Determines if the MAC forging is allowed or denied on an interface.  Options are:
    - allow
    - deny
  * tags - Default is [].  List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      action_on_uplink_fail = optional(string)
      cdp_enable            = optional(bool)
      description           = optional(string)
      lldp_enable_receive   = optional(bool)
      lldp_enable_transmit  = optional(bool)
      mac_register_mode     = optional(string)
      mac_security_forge    = optional(string)
      tags                  = optional(list(map(string)))
    }
  ))
}

#_______________________________________________________________________________
#
# Ethernet Network Control Policies
# GUI Location: Configure > Policies > Create Policy > Ethernet Network Control
#_______________________________________________________________________________

resource "intersight_fabric_eth_network_control_policy" "ethernet_network_control_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each              = local.ethernet_network_control_policies
  cdp_enabled           = each.value.cdp_enable
  description           = each.value.description != "" ? each.value.description : "${each.key} Ethernet Network Control Policy"
  forge_mac             = each.value.mac_security_forge
  mac_registration_mode = each.value.mac_register_mode
  name                  = each.key
  uplink_fail_action    = each.value.action_on_uplink_fail
  lldp_settings {
    object_type      = "fabric.LldpSettings"
    receive_enabled  = each.value.lldp_enable_receive
    transmit_enabled = each.value.lldp_enable_transmit
  }
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
