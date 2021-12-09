#_________________________________________________________________________
#
# Intersight System QoS Policies Variables
# GUI Location: Configure > Policy > Create Policy > System QoS > Start
#_________________________________________________________________________

variable "system_qos_policies" {
  default = {
    default = {
      classes = {
        default = {
          bandwidth_percent  = 0
          cos                = 0
          mtu                = 1500
          multicast_optimize = false
          packet_drop        = true
          state              = "Disabled"
          weight             = 0
        }
      }
      description  = ""
      organization = "default"
      tags         = []
    }
  }
  description = <<-EOT
  key - Name of the System QoS Policy.
  * classes - System QoS Classes to Configure for the Domain.  When configuring the System Classes Must be Configured in the Following Order:
    - classes_key - Name of the priority class.  You must configure all the following classes:
      1. Best Effort
      2. Bronze
      3. FC
      4. Gold
      5. Platinum
      6. Silver
    - bandwidth_percent - Percentage of bandwidth Assigned to traffic traffic tagged with this Class.
    - cos - Class of service Assigned to the System QoS Class.
      1. Best Effort - By default is 255 and cannot be changed.
      2. Bronze - By default is 1.
      3. FC - By default is 3 and cannot be changed.
      4. Gold - By default is 4.
      5. Platinum - By default is 5.
      6. Silver - By default is 2.
    - mtu - Maximum transmission unit (MTU) is the largest size packet or frame,that can be sent in a packet- or frame-based network such as the Internet.  Range is 1500-9216.
      1. FC is 2240 and cannot be changed
      2. All other priorities have a default of 1500 but can be configured in the range of 1500 to 9216.
    - multicast_optimize - Default is false.  If enabled, this QoS class will be optimized to send multiple packets.
    - state - Administrative state for the QoS class.
      1. Disabled - Admin configured Disabled State.
      2. Enabled - Admin configured Enabled State.
      Note: "Best Effort" and "FC" Classes are "Enabled" and cannot be "Disabled".
    - weight - The weight of the QoS Class controls the distribution of bandwidth between QoS Classes,with the same priority after the Guarantees for the QoS Classes are reached.  Default is 1.
      1. Best Effort - By default is 5.
      2. Bronze - By default is 7.
      3. FC - By default is 5.
      4. Gold - By default is 9.
      5. Platinum - By default is 10.
      6. Silver - By default is 8.
  * description - Description to Assign to the Policy.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      classes = optional(map(object(
        {
          bandwidth_percent  = optional(number)
          cos                = optional(number)
          mtu                = optional(number)
          multicast_optimize = optional(bool)
          packet_drop        = optional(bool)
          state              = optional(string)
          weight             = optional(number)
        }
      )))
      description  = optional(string)
      organization = optional(string)
      tags         = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# System QoS Policies
# GUI Location: Configure > Policy > Create Policy > System QoS > Start
#_________________________________________________________________________

module "system_qos_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  version     = ">=0.9.6"
  source      = "terraform-cisco-modules/imm/intersight//modules/system_qos_policies"
  for_each    = var.system_qos_policies
  classes     = each.value.classes != null ? each.value.classes : {}
  description = each.value.description != null ? each.value.description : "${each.key} System QoS Policy."
  name        = each.key
  org_moid    = each.value.organization != null ? local.org_moids[each.value.organization].moid : local.org_moids["default"].moid
  tags        = each.value.tags != null ? each.value.tags : []
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].system_qos_policy == each.key
  }
}
