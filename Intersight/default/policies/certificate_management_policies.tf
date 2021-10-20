#____________________________________________________________________________
#
# Intersight Adapter Configuration Policies Variables
# GUI Location: Configure > Policies > Create Policy > Adapter Configuration
#____________________________________________________________________________

variable "adapter_configuration_policies" {
  default = {
    default = {
      description         = ""
      enable_fip          = true
      enable_lldp         = true
      enable_port_channel = true
      fec_mode_1          = "cl91"
      fec_mode_2          = "cl91"
      fec_mode_3          = "cl91"
      fec_mode_4          = "cl91"
      organization        = "default"
      tags                = []
    }
  }
  description = <<-EOT
  key - Name of the Adapter Configuration Policy.
  * description - Description to Assign to the Policy.
  * enable_fip - If Selected, then FCoE Initialization Protocol (FIP) mode is enabled. FIP mode ensures that the adapter is compatible with current FCoE standards.
  * enable_lldp - If Selected, then Link Layer Discovery Protocol (LLDP) enables all the Data Center Bridging Capability Exchange protocol (DCBX) functionality, which includes FCoE, priority based flow control.
  * enable_port_channel - When Port Channel is enabled, two vNICs and two vHBAs are available for use on the adapter card.
    When disabled, four vNICs and four vHBAs are available for use on the adapter card. Disabling port channel reboots the server.
    Port Channel is supported only for Cisco VIC 1455/1457 adapters.
  * fec_mode_[1-4] - DCE Interface [1-4] Forward Error Correction (FEC) mode setting for the DCE interfaces of the adapter.
    FEC mode settings are supported on Cisco VIC 14xx adapters. FEC mode 'cl74' is unsupported for Cisco VIC 1495/1497.
    This setting will be ignored for unsupported adapters and for unavailable DCE interfaces.
    - cl74 - Use cl74 standard as FEC mode setting. 'Clause 74' aka FC-FEC ('FireCode' FEC) offers simple,
      low-latency protection against 1 burst/sparse bit error, but it is not good for random errors.
    - cl91 - (Default) Use cl91 standard as FEC mode setting. 'Clause 91' aka RS-FEC ('ReedSolomon' FEC) offers better
      error protection against bursty and random errors but adds latency.
    - Off - Disable FEC mode on the DCE Interface.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description         = optional(string)
      enable_fip          = optional(bool)
      enable_lldp         = optional(bool)
      enable_port_channel = optional(bool)
      fec_mode_1          = optional(string)
      fec_mode_2          = optional(string)
      fec_mode_3          = optional(string)
      fec_mode_4          = optional(string)
      organization        = optional(string)
      tags                = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Adapter Configuration Policies
# GUI Location: Configure > Policies > Create Policy > Adapter Configuration
#_________________________________________________________________________

module "adapter_configuration_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  source              = "terraform-cisco-modules/imm/intersight//modules/adapter_configuration_policies"
  for_each            = local.adapter_configuration_policies
  description         = each.value.description != "" ? each.value.description : "${each.key} Adapter Configuration Policy."
  enable_fip          = each.value.enable_fip
  enable_lldp         = each.value.enable_lldp
  enable_port_channel = each.value.enable_port_channel
  fec_mode_1          = each.value.fec_mode_1
  fec_mode_2          = each.value.fec_mode_2
  fec_mode_3          = each.value.fec_mode_3
  fec_mode_4          = each.value.fec_mode_4
  name                = each.key
  org_moid            = local.org_moids[each.value.organization].moid
  tags                = length(each.value.tags) > 0 ? each.value.tags : local.tags
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].device_connector_policy == each.key
  }
}
