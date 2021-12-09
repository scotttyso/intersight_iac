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
  # Intersight Provider Variables
  endpoint = var.endpoint

  # Tags for Deployment
  tags = var.tags

  # Terraform Cloud Remote Resources - Profiles
  ucs_domain_policies = data.terraform_remote_state.domain.outputs.ucs_domain_profiles
  ucs_domain_switches = data.terraform_remote_state.domain.outputs.moids

  merged_profile_policies = {
    for k, v in local.ucs_domain_policies : k => {
      network_connectivity_policy = v.network_connectivity_policy
      ntp_policy                  = v.ntp_policy
      moid                        = local.ucs_domain_switches[k]
      object_type                 = "fabric.SwitchProfile"
      organization                = v.organization
      serial_number               = v.serial_number
      snmp_policy                 = v.snmp_policy
      switch_control_policy       = v.switch_control_policy
      syslog_policy               = v.syslog_policy
      system_qos_policy           = v.system_qos_policy
      vlan_policy                 = v.vlan_policy
      vsan_policy                 = v.vsan_policy
    }
  }

  #______________________________________________
  #
  # Multicast Variables Locals
  #______________________________________________
  multicast_policies = {
    for k, v in var.multicast_policies : k => {
      description             = v.description != null ? v.description : ""
      organization            = v.organization != null ? v.organization : "default"
      querier_ip_address      = v.querier_ip_address != null ? v.querier_ip_address : ""
      querier_ip_address_peer = v.querier_ip_address_peer != null ? v.querier_ip_address_peer : ""
      querier_state           = v.querier_state != null ? v.querier_state : "Disabled"
      snooping_state          = v.snooping_state != null ? v.snooping_state : "Enabled"
      tags                    = v.tags != null ? v.tags : []
    }
  }

  #__________________________________________________________
  #
  # VLAN Policy Section Locals
  #__________________________________________________________

  vlan_policies = {
    for k, v in var.vlan_policies : k => {
      description  = v.description != null ? v.description : ""
      organization = v.organization != null ? v.organization : "default"
      tags         = v.tags != null ? v.tags : []
      vlans        = v.vlans != null ? v.vlans : {}
    }
  }

  vlans_loop = flatten([
    for key, value in var.vlan_policies : [
      for v in value.vlans : {
        auto_allow_on_uplinks = v.auto_allow_on_uplinks != null ? v.auto_allow_on_uplinks : false
        multicast_policy      = v.multicast_policy != null ? v.multicast_policy : ""
        name                  = v.name != null ? v.name : ""
        native_vlan           = v.native_vlan != null ? v.native_vlan : false
        vlan_list             = v.vlan_list != null ? v.vlan_list : ""
        vlan_policy           = key
      }
    ]
  ])
  vlans = {
    for k, v in local.vlans_loop : k => v
  }

}
