#_________________________________________________________________________
#
# Intersight Network Connectivity Policies Variables
# GUI Location: Configure > Policies > Create Policy > Network Connectivity
#_________________________________________________________________________

variable "network_connectivity_policies" {
  default = {
    default = {
      description               = ""
      dns_servers_v4            = ["208.67.220.220", "208.67.222.222"]
      dns_servers_v6            = []
      enable_dynamic_dns        = false
      enable_ipv6               = false
      obtain_ipv4_dns_from_dhcp = false
      obtain_ipv6_dns_from_dhcp = false
      organization              = "default"
      tags                      = []
      update_domain             = ""
    }
  }
  description = <<-EOT
  key - Name of the Network Connectivity Policy.
  * description - Description to Assign to the Policy.
  * dns_servers_v4 - List of IPv4 DNS Servers for this DNS Policy.
  * dns_servers_v6 - List of IPv6 DNS Servers for this DNS Policy.
  * enable_dynamic_dns - Flag to Enable or Disable Dynamic DNS on the Policy.  Meaning obtain DNS Servers from DHCP Service.
  * enable_ipv6 - Flag to Enable or Disable IPv6 on the Policy.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * update_domain - Name of the Domain to Update when using Dynamic DNS for the Policy.
  EOT
  type = map(object(
    {
      description               = optional(string)
      dns_servers_v4            = optional(set(string))
      dns_servers_v6            = optional(set(string))
      enable_dynamic_dns        = optional(bool)
      enable_ipv6               = optional(bool)
      obtain_ipv4_dns_from_dhcp = optional(bool)
      obtain_ipv6_dns_from_dhcp = optional(bool)
      organization              = optional(string)
      tags                      = optional(list(map(string)))
      update_domain             = optional(string)
    }
  ))
}


#_________________________________________________________________________
#
# Network Connectivity Policies
# GUI Location: Configure > Policies > Create Policy > Network Connectivity
#_________________________________________________________________________

resource "intersight_networkconfig_policy" "network_connectivity_policies" {
  depends_on = [
    local.org_moids,
    local.ucs_domain_policies
  ]
  for_each                 = local.network_connectivity_policies
  alternate_ipv4dns_server = length(each.value.dns_servers_v4) > 1 ? tolist(each.value.dns_servers_v4)[1] : null
  alternate_ipv6dns_server = length(each.value.dns_servers_v6) > 1 ? tolist(each.value.dns_servers_v6)[1] : null
  description              = each.value.description != "" ? each.value.description : "${each.key} Network Connectivity Policy"
  dynamic_dns_domain       = each.value.update_domain
  enable_dynamic_dns       = each.value.enable_dynamic_dns
  enable_ipv4dns_from_dhcp = each.value.enable_dynamic_dns == true ? true : false
  enable_ipv6              = each.value.enable_ipv6
  enable_ipv6dns_from_dhcp = each.value.enable_ipv6 == true && each.value.enable_dynamic_dns == true ? true : false
  preferred_ipv4dns_server = length(each.value.dns_servers_v4) > 0 ? tolist(each.value.dns_servers_v4)[0] : null
  preferred_ipv6dns_server = length(each.value.dns_servers_v6) > 0 ? tolist(each.value.dns_servers_v6)[0] : null
  name                     = each.key
  organization {
    moid        = local.org_moids[each.value.organization].moid
    object_type = "organization.Organization"
  }
  dynamic "profiles" {
    for_each = { for k, v in local.ucs_domain_policies : k => v if local.ucs_domain_policies[k].network_connectivity_policy == each.key }
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
