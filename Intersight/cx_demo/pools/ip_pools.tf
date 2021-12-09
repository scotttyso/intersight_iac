
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

module "ip_pools" {
  depends_on = [
    local.org_moids
  ]
  version          = ">=0.9.6"
  source           = "terraform-cisco-modules/imm/intersight//modules/ip_pools"
  for_each         = local.ip_pools
  assignment_order = each.value.assignment_order
  description      = each.value.description != "" ? each.value.description : "${each.value.organization} ${each.key} IP Pool."
  ipv4_blocks      = each.value.ipv4_blocks
  ipv4_config      = each.value.ipv4_config
  ipv6_blocks      = each.value.ipv6_blocks
  ipv6_config      = each.value.ipv6_config
  name             = each.key
  org_moid         = local.org_moids[each.value.organization].moid
  tags             = each.value.tags != [] ? each.value.tags : local.tags
}
