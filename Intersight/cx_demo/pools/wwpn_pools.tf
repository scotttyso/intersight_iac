
#______________________________________________
#
# WWPN Pool Variables
#______________________________________________

variable "wwpn_pools" {
  default = {
    default = {
      assignment_order = "default"
      description      = ""
      organization     = "default"
      pool_purpose     = "WWPN"
      tags             = []
      id_blocks = {
        default = {
          from = "20:00:00:25:B5:0A:00:00"
          size = 1000
          to   = "20:00:00:25:B5:0A:03:E7"
        }
      }
    }
  }
  description = <<-EOT
  key - Name of the Fibre-Channel Pool.
  * Assignment order decides the order in which the next identifier is allocated.
    - default - Assignment order is decided by the system - Default value.
    - sequential - Identifiers are assigned in a sequential order.
  * description - Description to Assign to the Pool.
  * id_blocks - Map of Addresses to Assign to the Pool.
    - from - Staring WWxN Address.  An Example is "20:00:00:25:B5:0A:00:00".
    - size - Size of WWxN Pool.  An Example is 1000.
    - to - Ending WWxN Address.  An Example is "20:00:00:25:B5:0A:03:E7".
  * pool_purpose - What type of Fiber-Channel Pool is this.  Options are:
    - WWNN
    - WWPN - (Default)
  * organization - Name of the Intersight Organization to assign this pool to.  Default is default.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Pool.
  EOT
  type = map(object(
    {
      assignment_order = optional(string)
      description      = optional(string)
      id_blocks = optional(map(object(
        {
          from = string
          size = optional(number)
          to   = optional(string)
        }
      )))
      organization = optional(string)
      pool_purpose = optional(string)
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
# WWPN Pools
#______________________________________________

module "wwpn_pools" {
  depends_on = [
    local.org_moids
  ]
  version          = ">=0.9.6"
  source           = "terraform-cisco-modules/imm/intersight//modules/fc_pools"
  for_each         = local.wwpn_pools
  assignment_order = each.value.assignment_order
  description      = each.value.description != "" ? each.value.description : "${each.value.organization} ${each.key} ${each.value.pool_purpose} Pool."
  id_blocks        = each.value.id_blocks
  name             = each.key
  org_moid         = local.org_moids[each.value.organization].moid
  pool_purpose     = each.value.pool_purpose
  tags             = each.value.tags != [] ? each.value.tags : local.tags
}
