#_________________________________________________________________________
#
# Ethernet Network Control Policies
# GUI Location: Configure > Policies > Create Policy > Ethernet Network Control
#_________________________________________________________________________

variable "ethernet_network_control_policies" {
  default = {
    default = {
      action_on_uplink_fail = "linkDown"
      base_template         = ""
      cdp_enable            = false
      description           = ""
      lldp_enable_receive   = false
      lldp_enable_transmit  = false
      mac_register_mode     = "nativeVlanOnly"
      mac_security_forge    = "allow"
      organization          = "default"
      tags                  = []
    }
  }
  description = <<-EOT
  key - Name of the Policy
  * action_on_uplink_fail - Default is linkDown.  Determines the state of the virtual interface (vethernet / vfc) on the switch when a suitable uplink is not pinned.  Options are:
    - linkDown
    - warning
    Important! If the Action on Uplink is set to Warning, the switch will not fail over if uplink connectivity is lost.
  * base-template - This is a shortcut with the base recommendation settings.  Options are:
    - both_enabled
    - cdp_enabled
    - lldp_enabled
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
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - Default is [].  List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      action_on_uplink_fail = optional(string)
      base_template         = optional(string)
      cdp_enable            = optional(bool)
      description           = optional(string)
      lldp_enable_receive   = optional(bool)
      lldp_enable_transmit  = optional(bool)
      mac_register_mode     = optional(string)
      mac_security_forge    = optional(string)
      organization          = optional(string)
      tags                  = optional(list(map(string)))
    }
  ))
}

module "ethernet_network_control_policies" {
  depends_on = [
    local.org_moids
  ]
  version               = ">=0.9.6"
  source                = "terraform-cisco-modules/imm/intersight//modules/ethernet_network_control_policies"
  for_each              = local.ethernet_network_control_policies
  action_on_uplink_fail = each.value.action_on_uplink_fail
  cdp_enable            = each.value.cdp_enable
  description           = each.value.description != "" ? each.value.description : "${each.key} Ethernet Network Control Policy."
  lldp_enable_receive   = each.value.lldp_enable_receive
  lldp_enable_transmit  = each.value.lldp_enable_transmit
  mac_register_mode     = each.value.mac_register_mode
  mac_security_forge    = each.value.mac_security_forge
  name                  = each.key
  org_moid              = local.org_moids[each.value.organization].moid
  tags                  = length(each.value.tags) > 0 ? each.value.tags : local.tags
}
