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

module "network_connectivity_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  version        = ">=0.9.6"
  source         = "terraform-cisco-modules/imm/intersight//modules/network_connectivity_policies"
  for_each       = local.network_connectivity_policies
  description    = each.value.description != "" ? each.value.description : "${each.key} Network Connectivity (DNS) Policy."
  dns_servers_v4 = each.value.dns_servers_v4
  dns_servers_v6 = each.value.dns_servers_v6
  dynamic_dns    = each.value.enable_dynamic_dns
  ipv6_enable    = each.value.enable_ipv6
  name           = each.key
  org_moid       = local.org_moids[each.value.organization].moid
  tags           = length(each.value.tags) > 0 ? each.value.tags : local.tags
  update_domain  = each.value.update_domain
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].network_connectivity_policy == each.key
  }
}
