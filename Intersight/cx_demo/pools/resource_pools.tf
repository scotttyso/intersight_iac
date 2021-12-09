
#______________________________________________
#
# Resource Pool Variables
#______________________________________________

variable "resource_pools" {
  default = {
    default = { # The Pool Name will be {each.key}.  In this case it would be default if left like this.
      assignment_order   = "default"
      description        = ""
      organization       = "default"
      pool_type          = "Static"
      resource_type      = "Server"
      serial_number_list = ["**REQUIRED**"]
      server_type        = "Blades"
      tags               = []
    }
  }
  description = <<-EOT
  key - Name of the Resource Pool.
  * Assignment order decides the order in which the next identifier is allocated.
    - default - (Default) Assignment order is decided by the system.
    - sequential - Identifiers are assigned in a sequential order.
  * description - Description to Assign to the Pool.
  * organization - Name of the Intersight Organization to assign this pool to.  Default is default.
    - https://intersight.com/an/settings/organizations/
  * pool_type - The resource management type in the pool, it can be either static or dynamic.
    - Dynamic - The resources in the pool will be updated dynamically based on the condition.
    - Static - The resources in the pool will not be changed until user manually update it.
  * resource_type - The type of the resource present in the pool, example 'server' its combination of RackUnit and Blade.
    - None - The resource cannot consider for Resource Pool.
    - Server - Resource Pool holds the server kind of resources, example - RackServer, Blade.
  * serial_number_list - A List of Compute Serial Numbers to assign to the policy.  These must be the same type of server. Cannot be some blades and some rackmounts.
  * server_type - The Server type to add to the selection filter field.
    - Blades - A Blade Server.
    - RackUnits - A Rackmount Server.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Pool.
  EOT
  type = map(object(
    {
      assignment_order   = optional(string)
      description        = optional(string)
      organization       = optional(string)
      pool_type          = optional(string)
      resource_type      = optional(string)
      serial_number_list = set(string)
      server_type        = optional(string)
      tags               = optional(list(map(string)))
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
# Resource Pools
#______________________________________________

module "resource_pools" {
  depends_on = [
    local.org_moids
  ]
  version            = ">=0.9.6"
  source             = "terraform-cisco-modules/imm/intersight//modules/resource_pools"
  for_each           = local.resource_pools
  assignment_order   = each.value.assignment_order
  description        = each.value.description != "" ? each.value.description : "${each.value.organization} ${each.key} Resource Pool."
  name               = each.key
  org_moid           = local.org_moids[each.value.organization].moid
  pool_type          = each.value.pool_type
  resource_type      = each.value.resource_type
  serial_number_list = each.value.serial_number_list
  server_type        = each.value.server_type
  tags               = each.value.tags != [] ? each.value.tags : local.tags
}
