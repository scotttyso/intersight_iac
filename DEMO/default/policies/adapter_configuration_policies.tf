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
      pci_slot            = "MLOM"
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
  * pci_slot - PCIe slot where the VIC adapter is installed. Supported values are (1-15) and MLOM.
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
      pci_slot            = optional(string)
      tags                = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Adapter Configuration Policies
# GUI Location: Configure > Policies > Create Policy > Adapter Configuration
#_________________________________________________________________________

resource "intersight_adapter_config_policy" "adapter_configuration_policies" {
  depends_on = [
    local.org_moids
  ]
  for_each    = local.adapter_configuration_policies
  description = each.value.description != "" ? each.value.description : "${each.key} Adapter Configuration Policy."
  name        = each.key
  organization {
    moid        = local.org_moids[each.value.organization].moid
    object_type = "organization.Organization"
  }
  settings {
    object_type = "adapter.AdapterConfig"
    slot_id     = each.value.pci_slot
    dce_interface_settings = [
      {
        additional_properties = ""
        class_id              = "adapter.DceInterfaceSettings"
        fec_mode              = each.value.fec_mode_1
        interface_id          = 0
        object_type           = "adapter.DceInterfaceSettings"
      },
      {
        additional_properties = ""
        class_id              = "adapter.DceInterfaceSettings"
        fec_mode              = each.value.fec_mode_2
        interface_id          = 1
        object_type           = "adapter.DceInterfaceSettings"
      },
      {
        additional_properties = ""
        class_id              = "adapter.DceInterfaceSettings"
        fec_mode              = each.value.fec_mode_3
        interface_id          = 2
        object_type           = "adapter.DceInterfaceSettings"
      },
      {
        additional_properties = ""
        class_id              = "adapter.DceInterfaceSettings"
        fec_mode              = each.value.fec_mode_4
        interface_id          = 3
        object_type           = "adapter.DceInterfaceSettings"
      },
    ]
    eth_settings {
      lldp_enabled = each.value.enable_lldp
      object_type  = "adapter.EthSettings"
    }
    fc_settings {
      fip_enabled = each.value.enable_fip
      object_type = "adapter.FcSettings"
    }
    port_channel_settings {
      enabled     = each.value.enable_port_channel
      object_type = "adapter.PortChannelSettings"
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
