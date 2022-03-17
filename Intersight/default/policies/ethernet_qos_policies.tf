#_________________________________________________________________________
#
# Ethernet QoS Policies
# GUI Location: Configure > Policies > Create Policy > Ethernet QoS
#_________________________________________________________________________

variable "ethernet_qos_policies" {
  default = {
    default = {
      burst                 = 10240
      cos                   = 0
      description           = ""
      enable_trust_host_cos = false
      mtu                   = 1500
      priority              = "Best Effort"
      rate_limit            = 0
      tags                  = []
    }
  }
  description = <<-EOT
  key - Name of the Ethernet QoS Policy
  * burst - Default is 1024.  The burst traffic, in bytes, allowed on the vNIC.  Value can be between 1024-1000000.
  * cos - Default is 0.  Class of Service to be associated to the traffic on the virtual interface.  Value can be between 0-6. For FIAttached this should always be 0.
  * description - Description for the Policy.
  * enable_trust_host_cos - Default is false.  Enables usage of the Class of Service provided by the operating system.
  * mtu - Default is 1500.  The Maximum Transmission Unit (MTU) or packet size that the virtual interface accepts.  Value can be between 1500-9000.
  * priority - Default is 'Best Effort'.  The priortity matching the System QoS specified in the fabric profile.  Options are:
    - Platinum
    - Gold
    - Silver
    - Bronze
    - Best Effort
    - FC
  * rate_limit - Default is 0.  The value in Mbps (0-10G/40G/100G depending on Adapter Model) to use for limiting the data rate on the virtual interface. Setting this to zero will turn rate limiting off.  Range is between 0-100000.
  * tags - Default is [].  List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      burst                 = optional(number)
      cos                   = optional(number)
      description           = optional(string)
      enable_trust_host_cos = optional(bool)
      priority              = optional(string)
      mtu                   = optional(number)
      rate_limit            = optional(number)
      tags                  = optional(list(map(string)))
    }
  ))
}

#_______________________________________________________________________________
#
# Ethernet QoS Policies
# GUI Location: Configure > Policies > Create Policy > Ethernet QoS
#_______________________________________________________________________________

resource "intersight_vnic_eth_qos_policy" "ethernet_qos_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each       = local.ethernet_qos_policies
  burst          = each.value.burst
  cos            = each.value.cos
  description    = each.value.description != "" ? each.value.description : "${each.key} Ethernet QoS Policy"
  mtu            = each.value.mtu
  name           = each.key
  priority       = each.value.priority
  rate_limit     = each.value.rate_limit
  trust_host_cos = each.value.enable_trust_host_cos
  organization {
    moid        = local.org_moid
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
