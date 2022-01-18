
#______________________________________________
#
# UUID Pool Variables
#______________________________________________

variable "uuid_pools" {
  default = {
    default = { # The Pool Name will be {each.key}.  In this case it would be default if left like this.
      assignment_order = "default"
      description      = ""
      organization     = "default"
      prefix           = "000025B5-0000-0000"
      tags             = []
      uuid_blocks = {
        default = {
          from = "0000-000000000000"
          size = 1000
          to   = "0000-0000000003E7"
        }
      }
    }
  }
  description = <<-EOT
  key - Name of the UUID Pool.
  * Assignment order decides the order in which the next identifier is allocated.
    - default - (Default) Assignment order is decided by the system.
    - sequential - Identifiers are assigned in a sequential order.
  * description - Description to Assign to the Pool.
  * prefix - Prefix to assign to the UUID Pool..  The default is "000025B5-0000-0000".
  * uuid_blocks - Map of Addresses to Assign to the Pool.
    - from - Starting UUID Address.  An Example is "0000-000000000000".
    - size - Size of UUID Pool.  An Example is 1000.
    - to - Ending UUID Address.  An Example is "0000-0000000003E7".
  * organization - Name of the Intersight Organization to assign this pool to.  Default is default.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Pool.
  EOT
  type = map(object(
    {
      assignment_order = optional(string)
      description      = optional(string)
      organization     = optional(string)
      prefix           = optional(string)
      tags             = optional(list(map(string)))
      uuid_blocks = optional(map(object(
        {
          from = string
          size = optional(number)
          to   = optional(string)
        }
      )))
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
# UUID Pools
#______________________________________________

resource "intersight_uuidpool_pool" "uuid_pools" {
  depends_on = [
    local.org_moids
  ]
  for_each         = local.uuid_pools
  assignment_order = each.value.assignment_order
  description      = each.value.description != "" ? each.value.description : "${each.key} UUID Pool"
  name             = each.key
  prefix           = each.value.prefix
  dynamic "uuid_suffix_blocks" {
    for_each = each.value.uuid_blocks
    content {
      object_type = "uuidpool.UuidBlock"
      from        = uuid_suffix_blocks.value.from
      size        = uuid_suffix_blocks.value.size != null ? uuid_suffix_blocks.value.size : null
      to          = uuid_suffix_blocks.value.to != null ? uuid_suffix_blocks.value.to : null
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
