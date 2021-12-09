#__________________________________________________________
#
# Local Variables Section
#__________________________________________________________

locals {
  # Intersight Organization Variables
  organizations = var.organizations
  org_moids = {
    for v in sort(keys(data.intersight_organization_organization.org_moid)) : v => {
      moid = data.intersight_organization_organization.org_moid[v].results[0].moid
    }
  }

  # Tags for Deployment
  tags = var.tags

  #__________________________________________________________
  #
  # UCS Domain Profiles Section - Locals
  #__________________________________________________________
  ucs_domain_profiles = {
    for k, v in var.ucs_domain_profiles : k => {
      action          = v.action != null ? v.action : "No-op"
      assign_switches = v.assign_switches != null ? v.assign_switches : false
      device_model = length(
        regexall("(UCS-FI-6454|UCS-FI-64108)", coalesce(v.device_model, "EMPTY"))
      ) > 0 ? v.device_model : "UCS-FI-6454"
      description                 = v.description != null ? v.description : ""
      network_connectivity_policy = v.network_connectivity_policy != null ? v.network_connectivity_policy : ""
      ntp_policy                  = v.ntp_policy != null ? v.ntp_policy : ""
      organization                = v.organization != null ? v.organization : "default"
      port_policy_fabric_a        = v.port_policy_fabric_a != null ? v.port_policy_fabric_a : ""
      port_policy_fabric_b        = v.port_policy_fabric_b != null ? v.port_policy_fabric_b : ""
      serial_number_fabric_a      = v.serial_number_fabric_a != null ? v.serial_number_fabric_a : ""
      serial_number_fabric_b      = v.serial_number_fabric_b != null ? v.serial_number_fabric_b : ""
      snmp_policy                 = v.snmp_policy != null ? v.snmp_policy : ""
      switch_control_policy       = v.switch_control_policy != null ? v.switch_control_policy : ""
      syslog_policy               = v.syslog_policy != null ? v.syslog_policy : ""
      system_qos_policy           = v.system_qos_policy != null ? v.system_qos_policy : ""
      tags                        = v.tags != null ? v.tags : []
      vlan_policy_fabric_a        = v.vlan_policy_fabric_a != null ? v.vlan_policy_fabric_a : ""
      vlan_policy_fabric_b        = v.vlan_policy_fabric_b != null ? v.vlan_policy_fabric_b : ""
      vsan_policy_fabric_a        = v.vsan_policy_fabric_a != null ? v.vsan_policy_fabric_a : ""
      vsan_policy_fabric_b        = v.vsan_policy_fabric_b != null ? v.vsan_policy_fabric_b : ""
    }
  }

  ucs_domain_switch_a = {
    for k, v in local.ucs_domain_profiles : "${k}_A_SIDE" => {
      action                      = v.action
      assign_switches             = v.assign_switches
      device_model                = v.device_model
      description                 = v.description
      domain_profile              = k
      fabric                      = "A"
      network_connectivity_policy = v.network_connectivity_policy
      ntp_policy                  = v.ntp_policy
      organization                = v.organization
      port_policy                 = v.port_policy_fabric_a
      serial_number               = v.serial_number_fabric_a
      snmp_policy                 = v.snmp_policy
      switch_control_policy       = v.switch_control_policy
      syslog_policy               = v.syslog_policy
      system_qos_policy           = v.system_qos_policy
      tags                        = v.tags
      vlan_policy                 = v.vlan_policy_fabric_a
      vsan_policy                 = v.vsan_policy_fabric_a
    }
  }

  ucs_domain_switch_b = {
    for k, v in local.ucs_domain_profiles : "${k}_B_SIDE" => {
      action                      = v.action
      assign_switches             = v.assign_switches
      device_model                = v.device_model
      description                 = v.description
      domain_profile              = k
      fabric                      = "B"
      network_connectivity_policy = v.network_connectivity_policy
      ntp_policy                  = v.ntp_policy
      organization                = v.organization
      port_policy                 = v.port_policy_fabric_b
      serial_number               = v.serial_number_fabric_b
      snmp_policy                 = v.snmp_policy
      switch_control_policy       = v.switch_control_policy
      syslog_policy               = v.syslog_policy
      system_qos_policy           = v.system_qos_policy
      tags                        = v.tags
      vlan_policy                 = v.vlan_policy_fabric_b
      vsan_policy                 = v.vsan_policy_fabric_b
    }
  }

  merged_ucs_switches = merge(local.ucs_domain_switch_a, local.ucs_domain_switch_b)

}
