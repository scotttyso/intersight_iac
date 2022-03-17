#_________________________________________________________________________
#
# Intersight Link Aggregation Policies Variables
# GUI Location: Configure > Policy > Create Policy > Link Aggregation
#_________________________________________________________________________

variable "link_aggregation_policies" {
  default = {
    default = {
      description        = ""
      lacp_rate          = "normal"
      suspend_individual = false
      tags               = []
    }
  }
  description = <<-EOT
  key - Name of the Link Aggregation Policy.
  * description - Description to Assign to the Policy.
  * lacp_rate - Flag used to indicate whether LACP PDUs are to be sent 'fast', i.e., every 1 second.
    - fast - The fast timeout rate is 1 second.
    - normal - (Default) - The normal timeout rate is 30 seconds.
  * suspend_individual - Flag tells the switch whether to suspend the port if it didn’t receive LACP PDU.  Default is false.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  EOT
  type = map(object(
    {
      description        = optional(string)
      lacp_rate          = optional(string)
      suspend_individual = optional(string)
      tags               = optional(list(map(string)))
    }
  ))
}


#_________________________________________________________________________
#
# Link Aggregation Policies
# GUI Location: Configure > Policy > Create Policy > Link Aggregation
#_________________________________________________________________________

resource "intersight_fabric_link_aggregation_policy" "link_aggregation_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each           = local.link_aggregation_policies
  description        = each.value.description != "" ? each.value.description : "${each.key} Link Aggregation Policy"
  name               = each.key
  lacp_rate          = each.value.lacp_rate
  suspend_individual = each.value.suspend_individual
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
