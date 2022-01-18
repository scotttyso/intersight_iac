variable "ucs_domain_profiles" {
  default = {
    default = {
      action                      = "No-op"
      assign_switches             = false
      description                 = ""
      device_model                = "UCS-FI-6454"
      network_connectivity_policy = ""
      ntp_policy                  = ""
      organization                = ""
      port_policy_fabric_a        = ""
      port_policy_fabric_b        = ""
      snmp_policy                 = ""
      serial_number_fabric_a      = ""
      serial_number_fabric_b      = ""
      switch_control_policy       = ""
      syslog_policy               = ""
      system_qos_policy           = ""
      tags                        = []
      vlan_policy_fabric_a        = ""
      vlan_policy_fabric_b        = ""
      vsan_policy_fabric_a        = ""
      vsan_policy_fabric_b        = ""
    }
  }
  description = <<-EOT
  Intersight UCS Domain Profile Variable Map.
  * action - Action to Perform on the Chassis Profile Assignment.  Options are:
    - Deploy
    - No-op
    - Unassign
  * assign_switches - Flag to define if the physical FI's should be assigned to the policy.  Default is false.
  * description - Description to Assign to the Profile.
  * device_model - This field specifies the device model that this Port Policy is being configured for.
    - UCS-FI-6454 - (Default) - The standard 4th generation UCS Fabric Interconnect with 54 ports.
    - UCS-FI-64108 - The expanded 4th generation UCS Fabric Interconnect with 108 ports.
    - unknown - Unknown device type, usage is TBD.
  * network_connectivity_policy - Name of the Network Connectivity Policy to assign to the Profile.
  * ntp_policy - Name of the Network Connectivity Policy to assign to the Profile.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * port_policy_fabric_a - Name of the Port Policy to assign to Fabric A.
  * port_policy_fabric_b - Name of the Port Policy to assign to Fabric B.
  * snmp_policy - Name of the SNMP Policy to assign to the Profile.
  * serial_number_fabric_a - Serial Number for Fabric Interconnect A.
  * serial_number_fabric_b - Serial Number for Fabric Interconnect B.
  * switch_control_policy - Name of the Switch Control Policy to assign to the Profile.
  * syslog_policy - Name of the Syslog Policy to assign to the Profile.
  * system_qos_policy - Name of the System QoS Policy to assign to the Profile.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * vlan_policy_fabric_a - Name of the VLAN Policy to assign to Fabric A.
  * vlan_policy_fabric_b - Name of the VLAN Policy to assign to Fabric B.
  * vsan_policy_fabric_a - Name of the VSAN Policy to assign to Fabric A.
  * vsan_policy_fabric_b - Name of the VSAN Policy to assign to Fabric B.
  EOT
  type = map(object(
    {
      action                      = optional(string)
      assign_switches             = optional(bool)
      description                 = optional(string)
      device_model                = optional(string)
      network_connectivity_policy = optional(string)
      ntp_policy                  = optional(string)
      organization                = optional(string)
      port_policy_fabric_a        = optional(string)
      port_policy_fabric_b        = optional(string)
      snmp_policy                 = optional(string)
      serial_number_fabric_a      = optional(string)
      serial_number_fabric_b      = optional(string)
      switch_control_policy       = optional(string)
      syslog_policy               = optional(string)
      system_qos_policy           = optional(string)
      tags                        = optional(list(map(string)))
      vlan_policy_fabric_a        = optional(string)
      vlan_policy_fabric_b        = optional(string)
      vsan_policy_fabric_a        = optional(string)
      vsan_policy_fabric_b        = optional(string)
    }
  ))
}

#_________________________________________________________________________
#
# Intersight UCS Domain Profile
# GUI Location: Profiles > UCS Domain Profile > Create UCS Domain Profile
#_________________________________________________________________________

resource "intersight_fabric_switch_cluster_profile" "ucs_domain_profiles" {
  depends_on = [
    local.org_moids
  ]
  for_each    = local.ucs_domain_profiles
  description = each.value.description != "" ? each.value.description : "${each.key} UCS Domain Profile"
  name        = each.key
  type        = "instance"
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


#______________________________________________
#
# Create Fabric Interconnect Switch Profiles
#______________________________________________

resource "intersight_fabric_switch_profile" "ucs_domain_switches" {
  depends_on = [
    data.intersight_network_element_summary.fis,
    local.org_moids,
    intersight_fabric_switch_cluster_profile.ucs_domain_profiles
  ]
  for_each    = local.merged_ucs_switches
  action      = each.value.action
  description = "${each.key} Fabric Interconnect ${each.value.fabric}"
  name        = "${each.key}-${each.value.fabric}"
  type        = "instance"
  switch_cluster_profile {
    moid = intersight_fabric_switch_cluster_profile.ucs_domain_profiles[
      each.value.domain_profile
    ].moid
  }
  dynamic "assigned_switch" {
    for_each = each.value.assign_switches == true ? [
      data.intersight_network_element_summary.fis[each.key
    ].results.0.moid] : []
    content {
      moid = assigned_switch.value
    }
  }
  # Need to wait for a Bug fix to the API to Support Policy Buckets with Domain Profiles
  # dynamic "policy_bucket" {
  #   for_each = [for s in each.value.policy_bucket : s if s != null]
  #   content {
  #     moid        = policy_bucket.value.moid
  #     object_type = policy_bucket.value.object_type
  #   }
  # }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}
