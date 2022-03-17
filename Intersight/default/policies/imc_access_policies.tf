#_________________________________________________________________________
#
# Intersight IMC Access Policies Variables
# GUI Location: Configure > Policies > Create Policy > IMC Access > Start
#_________________________________________________________________________

variable "imc_access_policies" {
  default = {
    default = {
      description                = ""
      inband_ip_pool             = ""
      inband_vlan_id             = 4
      ipv4_address_configuration = true
      ipv6_address_configuration = false
      out_of_band_ip_pool        = ""
      tags                       = []
    }
  }
  description = <<-EOT
  key - Name of the IMC Access Policy
  * description - Description to Assign to the Policy.
  * inband_ip_pool - Name of the IP Pool to Assign to the Inband Configuration of the IMC Access Policy.
  * inband_vlan_id - VLAN ID to Assign as the Inband Management VLAN for IMC Access.
  * ipv4_address_configuration - Flag to Enable or Disable the IPv4 Address Family for Poliices.
  * ipv6_address_configuration - Flag to Enable or Disable the IPv6 Address Family for Poliices.
  * out_of_band_ip_pool - Name of the IP Pool to Assign to the Out-of-Band Configuration of the IMC Access Policy.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description                = optional(string)
      inband_ip_pool             = optional(string)
      inband_vlan_id             = optional(number)
      ipv4_address_configuration = optional(bool)
      ipv6_address_configuration = optional(bool)
      out_of_band_ip_pool        = optional(string)
      tags                       = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# IMC Access Policies
# GUI Location: Configure > Policies > Create Policy > IMC Access > Start
#_________________________________________________________________________

resource "intersight_access_policy" "imc_access_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each    = local.imc_access_policies
  description = each.value.description != "" ? each.value.description : "${each.key} IMC Access Policy"
  inband_vlan = each.value.inband_vlan_id
  name        = each.key
  address_type {
    enable_ip_v4 = each.value.ipv4_address_configuration
    enable_ip_v6 = each.value.ipv6_address_configuration
    object_type  = "access.AddressType"
  }
  configuration_type {
    configure_inband      = each.value.inband_ip_pool != "" ? true : false
    configure_out_of_band = each.value.out_of_band_ip_pool != "" ? true : false
  }

  inband_ip_pool {
    moid        = each.value.inband_ip_pool != "" ? local.ip_pools[each.value.inband_ip_pool] : null
    object_type = "ippool.Pool"
  }
  organization {
    moid        = local.org_moid
    object_type = "organization.Organization"
  }
  out_of_band_ip_pool {
    moid        = each.value.out_of_band_ip_pool != "" ? local.ip_pools[each.value.out_of_band_ip_pool] : null
    object_type = "ippool.Pool"
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}
