#_________________________________________________________________________
#
# Intersight Persistent Memory Policies Variables
# GUI Location: Configure > Policies > Create Policy > Persistent Memory
#_________________________________________________________________________

variable "persistent_memory_policies" {
  default = {
    default = {
      description            = ""
      management_mode        = "configured-from-intersight"
      memory_mode_percentage = 0
      namespaces             = {}
      organization           = "default"
      persistent_memory_type = "app-direct"
      retain_namespaces      = true
      tags                   = []
    }
  }
  description = <<-EOT
  key - Name of the Persistent Memory Policy.
  * description - Description to Assign to the Policy.
  * management_mode - Management Mode of the policy. This can be either Configured from Intersight or Configured from Operating System.
    - configured-from-intersight - The Persistent Memory Modules are configured from Intersight thorugh Persistent Memory policy.
    - configured-from-operating-system - The Persistent Memory Modules are configured from operating system thorugh OS tools.
  GOALS
  * memory_mode_percentage - Volatile memory percentage.  Range is 0-100.
  * persistent_memory_type - Type of the Persistent Memory configuration where the Persistent Memory Modules are combined in an interleaved set or not.
    - app-direct - The App Direct interleaved Persistent Memory type.
    - app-direct-non-interleaved - The App Direct non-interleaved Persistent Memory type.
  NAMESPACES
  * namespaces -   Namespace is a partition made in one or more Persistent Memory Regions. You can create a namespace in Raw or Block mode.
    Key - Name of the Logical Namespace
    - capacity - Capacity of this Namespace that is created or modified.
    - mode - Mode of this Namespace that is created or modified.
      * block - The block mode of Persistent Memory Namespace.
      * raw - (Default) The raw mode of Persistent Memory Namespace.
    - socket_id - Socket ID of the region on which this Namespace will apply.
      * 1 - (Default) The first CPU socket in a server.
      * 2 - The second CPU socket in a server.
      * 3 - The third CPU socket in a server.
      * 4 - The fourth CPU socket in a server.
    - socket_memory_id - Socket Memory ID of the region on which this Namespace will apply.
      This is only applicable if running in app-direct-non-interleaved mode.  Options are:
      * "Not Applicable" - (Default) - The socket memory ID is not applicable if app-direct persistent memory type is selected in the goal
      * 2 - The second socket memory ID within a socket in a server.
      * 4 - The fourth socket memory ID within a socket in a server.
      * 6 - The sixth socket memory ID within a socket in a server.
      * 8 - The eighth socket memory ID within a socket in a server.
      * 10 - The tenth socket memory ID within a socket in a server.
      * 12 - The twelfth socket memory ID within a socket in a server.
  * retain_namespaces - Persistent Memory Namespaces to be retained or not.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description            = optional(string)
      management_mode        = optional(string)
      memory_mode_percentage = optional(number)
      namespaces = optional(map(object(
        {
          capacity         = number
          mode             = optional(string)
          socket_id        = optional(number)
          socket_memory_id = optional(string)

        }
      )))
      organization           = optional(string)
      persistent_memory_type = optional(string)
      retain_namespaces      = optional(bool)
      tags                   = optional(list(map(string)))
    }
  ))
}

variable "secure_passphrase" {
  default     = ""
  description = <<-EOT
  Secure passphrase to be applied on the Persistent Memory Modules on the server. The allowed characters are:
    - a-z, A-Z, 0-9 and special characters: \u0021, &, #, $, %, +, ^, @, _, *, -.
  EOT
  sensitive   = true
  type        = string
}


#_________________________________________________________________________
#
# Persistent Memory Policies
# GUI Location: Configure > Policies > Create Policy > Persistent Memory
#_________________________________________________________________________

module "persistent_memory_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  version         = ">=0.9.6"
  source          = "terraform-cisco-modules/imm/intersight//modules/persistent_memory_policies"
  for_each        = local.persistent_memory_policies
  description     = each.value.description != "" ? each.value.description : "${each.key} Persistent Memory Policy."
  management_mode = each.value.management_mode
  name            = each.key
  org_moid        = local.org_moids[each.value.organization].moid
  # Goals
  memory_mode_percentage = each.value.memory_mode_percentage
  persistent_memory_type = each.value.persistent_memory_type
  # Namespaces
  namespaces        = each.value.namespaces
  retain_namespaces = each.value.retain_namespaces
  secure_passphrase = var.secure_passphrase
  tags              = length(each.value.tags) > 0 ? each.value.tags : local.tags
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].persistent_memory_policy == each.key
  }
}
