
#______________________________________________
#
# IP Pool Variables
#______________________________________________

variable "ip_pools" {
  default = {
    default = {
      assignment_order = "default"
      description      = ""
      ipv4_blocks      = {}
      ipv4_config      = {}
      ipv6_blocks      = {}
      ipv6_config      = {}
      organization     = "default"
      tags             = []
    }
  }
  description = <<-EOT
  key - Name of the IP Pool.
  * Assignment order decides the order in which the next identifier is allocated.
    - default - (Default) Assignment order is decided by the system.
    - sequential - Identifiers are assigned in a sequential order.
  * description - Description to Assign to the Pool.
  * ipv4_blocks - Map of Addresses to Assign to the Pool.
    - from - Starting IPv4 Address.
    - size - Size of the IPv4 Address Pool
    - to - Ending IPv4 Address.
  * ipv4_config - IPv4 Configuration to assign to the ipv4_blocks.
    - gateway - Gateway to assign to the pool.
    - netmask - Netmask to assign to the pool.
    - primary_dns = Primary DNS Server to Assign to the Pool
    - secondary_dns = Secondary DNS Server to Assign to the Pool
  * ipv6_blocks - Map of Addresses to Assign to the Pool.
    - from - Starting IPv6 Address.
    - size - Size of the IPv6 Address Pool
    - to - Ending IPv6 Address.
  * ipv6_config - IPv6 Configuration to assign to the ipv6_blocks.
    - gateway - Gateway to assign to the pool.
    - netmask - Netmask to assign to the pool.
    - primary_dns = Primary DNS Server to Assign to the Pool
    - secondary_dns = Secondary DNS Server to Assign to the Pool
  * organization - Name of the Intersight Organization to assign this pool to.  Default is default.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Pool.
  EOT
  type = map(object(
    {
      assignment_order = optional(string)
      description      = optional(string)
      ipv4_blocks = optional(map(object(
        {
          from = string
          size = optional(number)
          to   = optional(string)
        }
      )))
      ipv4_config = optional(map(object(
        {
          gateway       = string
          netmask       = string
          primary_dns   = optional(string)
          secondary_dns = optional(string)
        }
      )))
      ipv6_blocks = optional(map(object(
        {
          from = string
          size = optional(number)
          to   = optional(string)
        }
      )))
      ipv6_config = optional(map(object(
        {
          gateway       = string
          prefix        = number
          primary_dns   = optional(string)
          secondary_dns = optional(string)
        }
      )))
      organization = optional(string)
      tags         = optional(list(map(string)))
    }
  ))
}


#____________________________________________________________
#
# Intersight Pools Module
# GUI Location: Pools > Create Pool
#____________________________________________________________

#______________________________________________
#
# IP Pools
#______________________________________________

resource "intersight_ippool_pool" "ip_pools" {
  depends_on = [
    local.org_moids
  ]
  for_each         = local.ip_pools
  assignment_order = each.value.assignment_order
  description      = each.value.description != "" ? each.value.description : "${each.key} IP Pool"
  name             = each.key
  dynamic "ip_v4_blocks" {
    for_each = each.value.ipv4_blocks
    content {
      from = ip_v4_blocks.value.from
      size = ip_v4_blocks.value.size != null ? ip_v4_blocks.value.size : null
      to   = ip_v4_blocks.value.to != null ? ip_v4_blocks.value.to : null
    }
  }
  dynamic "ip_v4_config" {
    for_each = each.value.ipv4_config
    content {
      gateway       = ip_v4_config.value.gateway
      netmask       = ip_v4_config.value.netmask
      primary_dns   = ip_v4_config.value.primary_dns != null ? ip_v4_config.value.primary_dns : null
      secondary_dns = ip_v4_config.value.secondary_dns != null ? ip_v4_config.value.secondary_dns : null
    }
  }
  dynamic "ip_v6_blocks" {
    for_each = each.value.ipv6_blocks
    content {
      from = ip_v6_blocks.value.from
      size = ip_v6_blocks.value.size != null ? tonumber(ip_v6_blocks.value.size) : null
      to   = ip_v6_blocks.value.to != null ? ip_v6_blocks.value.to : null
    }
  }
  dynamic "ip_v6_config" {
    for_each = each.value.ipv6_config
    content {
      gateway       = ip_v6_config.value.gateway
      prefix        = ip_v6_config.value.prefix
      primary_dns   = ip_v6_config.value.primary_dns != null ? ip_v6_config.value.primary_dns : "::"
      secondary_dns = ip_v6_config.value.secondary_dns != null ? ip_v6_config.value.secondary_dns : "::"
    }
  }
  organization {
    moid        = local.org_moids[each.value.organization].moid
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
