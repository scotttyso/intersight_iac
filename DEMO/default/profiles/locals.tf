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

  # Terraform Cloud Remote Resources - Policies
  adapter_configuration_policies  = lookup(data.terraform_remote_state.policies.outputs, "adapter_configuration_policies", {})
  bios_policies                   = lookup(data.terraform_remote_state.policies.outputs, "bios_policies", {})
  boot_order_policies             = lookup(data.terraform_remote_state.policies.outputs, "boot_order_policies", {})
  certificate_management_policies = lookup(data.terraform_remote_state.policies.outputs, "certificate_management_policies", {})
  device_connector_policies       = lookup(data.terraform_remote_state.policies.outputs, "device_connector_policies", {})
  imc_access_policies             = lookup(data.terraform_remote_state.policies.outputs, "imc_access_policies", {})
  ipmi_over_lan_policies          = lookup(data.terraform_remote_state.policies.outputs, "ipmi_over_lan_policies", {})
  lan_connectivity_policies       = lookup(data.terraform_remote_state.policies.outputs, "lan_connectivity_policies", {})
  ldap_policies                   = lookup(data.terraform_remote_state.policies.outputs, "ldap_policies", {})
  local_user_policies             = lookup(data.terraform_remote_state.policies.outputs, "local_user_policies", {})
  network_connectivity_policies   = lookup(data.terraform_remote_state.policies.outputs, "network_connectivity_policies", {})
  ntp_policies                    = lookup(data.terraform_remote_state.policies.outputs, "ntp_policies", {})
  persistent_memory_policies      = lookup(data.terraform_remote_state.policies.outputs, "persistent_memory_policies", {})
  port_policies                   = lookup(data.terraform_remote_state.policies.outputs, "port_policies", {})
  power_policies                  = lookup(data.terraform_remote_state.policies.outputs, "power_policies", {})
  san_connectivity_policies       = lookup(data.terraform_remote_state.policies.outputs, "san_connectivity_policies", {})
  serial_over_lan_policies        = lookup(data.terraform_remote_state.policies.outputs, "serial_over_lan_policies", {})
  smtp_policies                   = lookup(data.terraform_remote_state.policies.outputs, "smtp_policies", {})
  snmp_policies                   = lookup(data.terraform_remote_state.policies.outputs, "snmp_policies", {})
  ssh_policies                    = lookup(data.terraform_remote_state.policies.outputs, "ssh_policies", {})
  storage_policies                = lookup(data.terraform_remote_state.policies.outputs, "storage_policies", {})
  switch_control_policies         = lookup(data.terraform_remote_state.policies.outputs, "switch_control_policies", {})
  syslog_policies                 = lookup(data.terraform_remote_state.policies.outputs, "syslog_policies", {})
  system_qos_policies             = lookup(data.terraform_remote_state.policies.outputs, "system_qos_policies", {})
  thermal_policies                = lookup(data.terraform_remote_state.policies.outputs, "thermal_policies", {})
  virtual_kvm_policies            = lookup(data.terraform_remote_state.policies.outputs, "virtual_kvm_policies", {})
  virtual_media_policies          = lookup(data.terraform_remote_state.policies.outputs, "virtual_media_policies", {})
  vsan_policies                   = lookup(data.terraform_remote_state.policies.outputs, "vsan_policies", {})

  # Terraform Cloud Remote Resources - Policies VLANs
  vlan_policies = lookup(data.terraform_remote_state.policies.outputs, "vlan_policies", {})

  # Terraform Cloud Remote Resources - Pools
  resource_pools = lookup(data.terraform_remote_state.pools.outputs, "resource_pools", {})
  uuid_pools     = lookup(data.terraform_remote_state.pools.outputs, "uuid_pools", {})

  # Tags for Deployment
  tags = var.tags

  #__________________________________________________________
  #
  # UCS Chassis Profiles Section - Locals
  #__________________________________________________________

  chassis_policies_loop_1 = {
    for k, v in var.ucs_chassis_profiles : k => {
      action              = v.action != null ? v.action : "No-op"
      assign_chassis      = v.assign_chassis != null ? v.assign_chassis : false
      description         = v.description != null ? v.description : ""
      organization        = v.organization != null ? v.organization : "default"
      imc_access_policy   = v.imc_access_policy != null ? v.imc_access_policy : ""
      power_policy        = v.power_policy != null ? v.power_policy : ""
      serial_number       = v.serial_number != null ? v.serial_number : ""
      snmp_policy         = v.snmp_policy != null ? v.snmp_policy : ""
      thermal_policy      = v.thermal_policy != null ? v.thermal_policy : ""
      tags                = v.tags != null ? v.tags : []
      target_platform     = v.target_platform != null ? v.target_platform : "FIAttached"
      wait_for_completion = v.wait_for_completion != null ? v.wait_for_completion : false
    }
  }
  chassis_policies_loop_2 = {
    for k, v in local.chassis_policies_loop_1 : k => {
      action         = v.action
      assign_chassis = v.assign_chassis
      description    = v.description
      organization   = v.organization
      imc_access_policy = v.imc_access_policy != "" ? {
        moid        = local.imc_access_policies[v.imc_access_policy]
        object_type = "access.Policy"
      } : null
      power_policy = v.power_policy != "" ? {
        moid        = local.power_policies[v.power_policy]
        object_type = "power.Policy"
      } : null
      serial_number = v.serial_number
      snmp_policy = v.snmp_policy != "" ? {
        moid        = local.snmp_policies[v.snmp_policy]
        object_type = "snmp.Policy"
      } : null
      thermal_policy = v.thermal_policy != "" ? {
        moid        = local.thermal_policies[v.thermal_policy]
        object_type = "thermal.Policy"
      } : null
      tags                = v.tags
      target_platform     = v.target_platform
      wait_for_completion = v.wait_for_completion
    }
  }

  ucs_chassis_profiles = {
    for k, v in local.chassis_policies_loop_2 : k => {
      action              = v.action
      assign_chassis      = v.assign_chassis
      description         = v.description
      organization        = v.organization
      policy_bucket       = toset(flatten([v.imc_access_policy, v.power_policy, v.snmp_policy, v.thermal_policy]))
      serial_number       = v.serial_number
      tags                = v.tags
      target_platform     = v.target_platform
      wait_for_completion = v.wait_for_completion
    }
  }


  #__________________________________________________________
  #
  # UCS Domain Profiles Section - Locals
  #__________________________________________________________
  # ucs_domain_profiles = {
  #   for k, v in var.ucs_domain_profiles : k => {
  #     action          = v.action != null ? v.action : "No-op"
  #     assign_switches = v.assign_switches != null ? v.assign_switches : false
  #     device_model = length(
  #       regexall("(UCS-FI-6454|UCS-FI-64108)", coalesce(v.device_model, "EMPTY"))
  #     ) > 0 ? v.device_model : "UCS-FI-6454"
  #     description                 = v.description != null ? v.description : ""
  #     network_connectivity_policy = v.network_connectivity_policy != null ? v.network_connectivity_policy : ""
  #     ntp_policy                  = v.ntp_policy != null ? v.ntp_policy : ""
  #     organization                = v.organization != null ? v.organization : "default"
  #     port_policy_fabric_a        = v.port_policy_fabric_a != null ? v.port_policy_fabric_a : ""
  #     port_policy_fabric_b        = v.port_policy_fabric_b != null ? v.port_policy_fabric_b : ""
  #     serial_number_fabric_a      = v.serial_number_fabric_a != null ? v.serial_number_fabric_a : ""
  #     serial_number_fabric_b      = v.serial_number_fabric_b != null ? v.serial_number_fabric_b : ""
  #     snmp_policy                 = v.snmp_policy != null ? v.snmp_policy : ""
  #     switch_control_policy       = v.switch_control_policy != null ? v.switch_control_policy : ""
  #     syslog_policy               = v.syslog_policy != null ? v.syslog_policy : ""
  #     system_qos_policy           = v.system_qos_policy != null ? v.system_qos_policy : ""
  #     tags                        = v.tags != null ? v.tags : []
  #     vlan_policy_fabric_a        = v.vlan_policy_fabric_a != null ? v.vlan_policy_fabric_a : ""
  #     vlan_policy_fabric_b        = v.vlan_policy_fabric_b != null ? v.vlan_policy_fabric_b : ""
  #     vsan_policy_fabric_a        = v.vsan_policy_fabric_a != null ? v.vsan_policy_fabric_a : ""
  #     vsan_policy_fabric_b        = v.vsan_policy_fabric_b != null ? v.vsan_policy_fabric_b : ""
  #   }
  # }

  # ucs_domain_switch_a_loop = {
  #   for k, v in local.ucs_domain_profiles : "${k}_A_SIDE" => {
  #     action                      = v.action
  #     assign_switches             = v.assign_switches
  #     device_model                = v.device_model
  #     description                 = v.description
  #     domain_profile              = k
  #     fabric                      = "A"
  #     organization                = v.organization
  #     serial_number               = v.serial_number_fabric_a
  #     tags                        = v.tags
  #     network_connectivity_policy = v.network_connectivity_policy != "" ? {
  #       moid        = local.network_connectivity_policies[v.network_connectivity_policy]
  #       object_type = "networkconfig.Policy"
  #     } : null
  #     ntp_policy = v.ntp_policy != "" ? {
  #       moid        = local.ntp_policies[v.ntp_policy]
  #       object_type = "ntp.Policy"
  #     } : null
  #     port_policy = v.port_policy_fabric_a != "" ? {
  #       moid        = local.port_policies[v.port_policy_fabric_a]
  #       object_type = "fabric.PortPolicy"
  #     } : null
  #     snmp_policy = v.snmp_policy != "" ? {
  #       moid        = local.snmp_policies[v.snmp_policy]
  #       object_type = "snmp.Policy"
  #     } : null
  #     switch_control_policy = v.switch_control_policy != "" ? {
  #       moid        = local.switch_control_policies[v.switch_control_policy]
  #       object_type = "fabric.SwitchControlPolicy"
  #     } : null
  #     syslog_policy = v.syslog_policy != "" ? {
  #       moid        = local.syslog_policies[v.syslog_policy]
  #       object_type = "syslog.Policy"
  #     } : null
  #     system_qos_policy = v.system_qos_policy != "" ? {
  #       moid        = local.system_qos_policies[v.system_qos_policy]
  #       object_type = "fabric.SystemQosPolicy"
  #     } : null
  #     vlan_policy = v.vlan_policy_fabric_a != "" ? {
  #       moid        = local.vlan_policies[v.vlan_policy_fabric_a]
  #       object_type = "fabric.Vlan"
  #     } : null
  #     vsan_policy = v.vsan_policy_fabric_a != "" ? {
  #       moid        = local.vsan_policies[v.vsan_policy_fabric_a]
  #       object_type = "fabric.Vsan"
  #     } : null
  #   }
  # }

  # ucs_domain_switch_a = {
  #   for k, v in local.ucs_domain_switch_a_loop : k => {
  #     action                      = v.action
  #     assign_switches             = v.assign_switches
  #     device_model                = v.device_model
  #     description                 = v.description
  #     domain_profile              = v.domain_profile
  #     fabric                      = v.fabric
  #     organization                = v.organization
  #     policy_bucket = toset(flatten(
  #       [
  #         v.network_connectivity_policy,
  #         v.ntp_policy,
  #         v.port_policy,
  #         v.snmp_policy,
  #         v.switch_control_policy,
  #         v.syslog_policy,
  #         v.system_qos_policy,
  #         v.vlan_policy,
  #         v.vsan_policy
  #       ]
  #     ))
  #     serial_number               = v.serial_number
  #     tags                        = v.tags
  #   }
  # }

  # ucs_domain_switch_b_loop = {
  #   for k, v in local.ucs_domain_profiles : "${k}_B_SIDE" => {
  #     action                      = v.action
  #     assign_switches             = v.assign_switches
  #     device_model                = v.device_model
  #     description                 = v.description
  #     domain_profile              = k
  #     fabric                      = "B"
  #     organization                = v.organization
  #     serial_number               = v.serial_number_fabric_b
  #     tags                        = v.tags
  #     network_connectivity_policy = v.network_connectivity_policy != "" ? {
  #       moid        = local.network_connectivity_policies[v.network_connectivity_policy]
  #       object_type = "networkconfig.Policy"
  #     } : null
  #     ntp_policy = v.ntp_policy != "" ? {
  #       moid        = local.ntp_policies[v.ntp_policy]
  #       object_type = "ntp.Policy"
  #     } : null
  #     port_policy = v.port_policy_fabric_b != "" ? {
  #       moid        = local.port_policies[v.port_policy_fabric_b]
  #       object_type = "fabric.PortPolicy"
  #     } : null
  #     snmp_policy = v.snmp_policy != "" ? {
  #       moid        = local.snmp_policies[v.snmp_policy]
  #       object_type = "snmp.Policy"
  #     } : null
  #     switch_control_policy = v.switch_control_policy != "" ? {
  #       moid        = local.switch_control_policies[v.switch_control_policy]
  #       object_type = "fabric.SwitchControlPolicy"
  #     } : null
  #     syslog_policy = v.syslog_policy != "" ? {
  #       moid        = local.syslog_policies[v.syslog_policy]
  #       object_type = "syslog.Policy"
  #     } : null
  #     system_qos_policy = v.system_qos_policy != "" ? {
  #       moid        = local.system_qos_policies[v.system_qos_policy]
  #       object_type = "fabric.SystemQosPolicy"
  #     } : null
  #     vlan_policy = v.vlan_policy_fabric_b != "" ? {
  #       moid        = local.vlan_policies[v.vlan_policy_fabric_b]
  #       object_type = "fabric.Vlan"
  #     } : null
  #     vsan_policy = v.vsan_policy_fabric_b != "" ? {
  #       moid        = local.vsan_policies[v.vsan_policy_fabric_b]
  #       object_type = "fabric.Vsan"
  #     } : null
  #   }
  # }

  # ucs_domain_switch_b = {
  #   for k, v in local.ucs_domain_switch_b_loop : k => {
  #     action                      = v.action
  #     assign_switches             = v.assign_switches
  #     device_model                = v.device_model
  #     description                 = v.description
  #     domain_profile              = v.domain_profile
  #     fabric                      = v.fabric
  #     organization                = v.organization
  #     policy_bucket = toset(flatten(
  #       [
  #         v.network_connectivity_policy,
  #         v.ntp_policy,
  #         v.port_policy,
  #         v.snmp_policy,
  #         v.switch_control_policy,
  #         v.syslog_policy,
  #         v.system_qos_policy,
  #         v.vlan_policy,
  #         v.vsan_policy
  #       ]
  #     ))
  #     serial_number               = v.serial_number
  #     tags                        = v.tags
  #   }
  # }

  # merged_ucs_switches = merge(local.ucs_domain_switch_a, local.ucs_domain_switch_b)

  #__________________________________________________________
  #
  # UCS Server Profiles Section - Locals
  #__________________________________________________________
  ucs_server_loop_1 = {
    for k, v in var.ucs_server_profiles : k => {
      action                        = v.action != null ? v.action : "No-op"
      adapter_configuration_policy  = v.adapter_configuration_policy != null ? v.adapter_configuration_policy : null
      bios_policy                   = v.bios_policy != null ? v.bios_policy : null
      boot_order_policy             = v.boot_order_policy != null ? v.boot_order_policy : null
      certificate_management_policy = v.certificate_management_policy != null ? v.certificate_management_policy : null
      description                   = v.description != null ? v.description : null
      device_connector_policy       = v.device_connector_policy != null ? v.device_connector_policy : null
      imc_access_policy             = v.imc_access_policy != null ? v.imc_access_policy : null
      ipmi_over_lan_policy          = v.ipmi_over_lan_policy != null ? v.ipmi_over_lan_policy : null
      lan_connectivity_policy       = v.lan_connectivity_policy != null ? v.lan_connectivity_policy : null
      ldap_policy                   = v.ldap_policy != null ? v.ldap_policy : null
      local_user_policy             = v.local_user_policy != null ? v.local_user_policy : null
      network_connectivity_policy   = v.network_connectivity_policy != null ? v.network_connectivity_policy : null
      ntp_policy                    = v.ntp_policy != null ? v.ntp_policy : null
      organization                  = v.organization != null ? v.organization : "default"
      persistent_memory_policy      = v.persistent_memory_policy != null ? v.persistent_memory_policy : null
      power_policy                  = v.power_policy != null ? v.power_policy : null
      resource_pool                 = v.resource_pool != null ? v.resource_pool : ""
      san_connectivity_policy       = v.san_connectivity_policy != null ? v.san_connectivity_policy : null
      sd_card_policy                = v.sd_card_policy != null ? v.sd_card_policy : null
      serial_number                 = v.serial_number != null ? v.serial_number : null
      serial_over_lan_policy        = v.serial_over_lan_policy != null ? v.serial_over_lan_policy : null
      server_assignment_mode        = v.server_assignment_mode != null ? v.server_assignment_mode : "None"
      smtp_policy                   = v.smtp_policy != null ? v.smtp_policy : null
      snmp_policy                   = v.snmp_policy != null ? v.snmp_policy : null
      ssh_policy                    = v.ssh_policy != null ? v.ssh_policy : null
      static_uuid_address           = v.static_uuid_address != null ? v.static_uuid_address : ""
      storage_policy                = v.storage_policy != null ? v.storage_policy : null
      syslog_policy                 = v.syslog_policy != null ? v.syslog_policy : null
      tags                          = v.tags != null ? v.tags : []
      target_platform = v.target_platform != null && (
        v.ucs_server_profile_template == null || v.ucs_server_profile_template == ""
      ) ? v.target_platform : v.ucs_server_profile_template == null || v.ucs_server_profile_template == "" ? "FIAttached" : null
      ucs_server_profile_template = v.ucs_server_profile_template != null ? v.ucs_server_profile_template : ""
      uuid_pool                   = v.uuid_pool != null ? v.uuid_pool : ""
      virtual_kvm_policy          = v.virtual_kvm_policy != null ? v.virtual_kvm_policy : null
      virtual_media_policy        = v.virtual_media_policy != null ? v.virtual_media_policy : null
      wait_for_completion         = v.wait_for_completion != null ? v.wait_for_completion : false
    }
  }


  #__________________________________________________________
  #
  # UCS Server Profile Templates Section - Locals
  #__________________________________________________________
  ucs_server_profile_templates = {
    for k, v in var.ucs_server_profile_templates : k => {
      adapter_configuration_policy  = v.adapter_configuration_policy != null ? v.adapter_configuration_policy : ""
      bios_policy                   = v.bios_policy != null ? v.bios_policy : ""
      boot_order_policy             = v.boot_order_policy != null ? v.boot_order_policy : ""
      certificate_management_policy = v.certificate_management_policy != null ? v.certificate_management_policy : ""
      description                   = v.description != null ? v.description : ""
      device_connector_policy       = v.device_connector_policy != null ? v.device_connector_policy : ""
      imc_access_policy             = v.imc_access_policy != null ? v.imc_access_policy : ""
      ipmi_over_lan_policy          = v.ipmi_over_lan_policy != null ? v.ipmi_over_lan_policy : ""
      lan_connectivity_policy       = v.lan_connectivity_policy != null ? v.lan_connectivity_policy : ""
      ldap_policy                   = v.ldap_policy != null ? v.ldap_policy : ""
      local_user_policy             = v.local_user_policy != null ? v.local_user_policy : ""
      network_connectivity_policy   = v.network_connectivity_policy != null ? v.network_connectivity_policy : ""
      ntp_policy                    = v.ntp_policy != null ? v.ntp_policy : ""
      operating_system              = v.operating_system != null ? v.operating_system : "VMware"
      organization                  = v.organization != null ? v.organization : "default"
      persistent_memory_policy      = v.persistent_memory_policy != null ? v.persistent_memory_policy : ""
      power_policy                  = v.power_policy != null ? v.power_policy : ""
      san_connectivity_policy       = v.san_connectivity_policy != null ? v.san_connectivity_policy : ""
      sd_card_policy                = v.sd_card_policy != null ? v.sd_card_policy : ""
      serial_over_lan_policy        = v.serial_over_lan_policy != null ? v.serial_over_lan_policy : ""
      smtp_policy                   = v.smtp_policy != null ? v.smtp_policy : ""
      snmp_policy                   = v.snmp_policy != null ? v.snmp_policy : ""
      ssh_policy                    = v.ssh_policy != null ? v.ssh_policy : ""
      storage_policy                = v.storage_policy != null ? v.storage_policy : ""
      syslog_policy                 = v.syslog_policy != null ? v.syslog_policy : ""
      tags                          = v.tags != null ? v.tags : []
      target_platform               = v.target_platform != null ? v.target_platform : "FIAttached"
      uuid_pool                     = v.uuid_pool != null ? v.uuid_pool : ""
      virtual_kvm_policy            = v.virtual_kvm_policy != null ? v.virtual_kvm_policy : ""
      virtual_media_policy          = v.virtual_media_policy != null ? v.virtual_media_policy : ""
    }
  }

  merge_with_templates = flatten([
    for k, v in local.ucs_server_loop_1 : [
      for key, value in local.ucs_server_profile_templates : {
        action = v.action
        adapter_configuration_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.adapter_configuration_policy, "_EMPTY"))
        ) > 0 ? v.adapter_configuration_policy : v.ucs_server_profile_template != "" ? value.adapter_configuration_policy : ""
        bios_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.bios_policy, "_EMPTY"))
        ) > 0 ? v.bios_policy : v.ucs_server_profile_template != "" ? value.bios_policy : ""
        boot_order_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.boot_order_policy, "_EMPTY"))
        ) > 0 ? v.boot_order_policy : v.ucs_server_profile_template != "" ? value.boot_order_policy : ""
        certificate_management_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.certificate_management_policy, "_EMPTY"))
        ) > 0 ? v.certificate_management_policy : v.ucs_server_profile_template != "" ? value.certificate_management_policy : ""
        description = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.description, "_EMPTY"))
        ) > 0 ? v.description : v.ucs_server_profile_template != "" ? value.description : ""
        device_connector_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.device_connector_policy, "_EMPTY"))
        ) > 0 ? v.device_connector_policy : v.ucs_server_profile_template != "" ? value.device_connector_policy : ""
        imc_access_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.imc_access_policy, "_EMPTY"))
        ) > 0 ? v.imc_access_policy : v.ucs_server_profile_template != "" ? value.imc_access_policy : ""
        ipmi_over_lan_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.ipmi_over_lan_policy, "_EMPTY"))
        ) > 0 ? v.ipmi_over_lan_policy : v.ucs_server_profile_template != "" ? value.ipmi_over_lan_policy : ""
        lan_connectivity_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.lan_connectivity_policy, "_EMPTY"))
        ) > 0 ? v.lan_connectivity_policy : v.ucs_server_profile_template != "" ? value.lan_connectivity_policy : ""
        ldap_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.ldap_policy, "_EMPTY"))
        ) > 0 ? v.ldap_policy : v.ucs_server_profile_template != "" ? value.ldap_policy : ""
        local_user_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.local_user_policy, "_EMPTY"))
        ) > 0 ? v.local_user_policy : v.ucs_server_profile_template != "" ? value.local_user_policy : ""
        network_connectivity_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.network_connectivity_policy, "_EMPTY"))
        ) > 0 ? v.network_connectivity_policy : v.ucs_server_profile_template != "" ? value.network_connectivity_policy : ""
        ntp_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.ntp_policy, "_EMPTY"))
        ) > 0 ? v.ntp_policy : v.ucs_server_profile_template != "" ? value.ntp_policy : ""
        organization = v.organization != null ? v.organization : v.ucs_server_profile_template != "" ? value.organization : ""
        persistent_memory_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.persistent_memory_policy, "_EMPTY"))
        ) > 0 ? v.persistent_memory_policy : v.ucs_server_profile_template != "" ? value.persistent_memory_policy : ""
        key_name = k
        power_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.power_policy, "_EMPTY"))
        ) > 0 ? v.power_policy : v.ucs_server_profile_template != "" ? value.power_policy : ""
        resource_pool = v.resource_pool
        san_connectivity_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.san_connectivity_policy, "_EMPTY"))
        ) > 0 ? v.san_connectivity_policy : v.ucs_server_profile_template != "" ? value.san_connectivity_policy : ""
        sd_card_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.sd_card_policy, "_EMPTY"))
        ) > 0 ? v.sd_card_policy : v.ucs_server_profile_template != "" ? value.sd_card_policy : ""
        serial_number = v.serial_number
        serial_over_lan_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.serial_over_lan_policy, "_EMPTY"))
        ) > 0 ? v.serial_over_lan_policy : v.ucs_server_profile_template != "" ? value.serial_over_lan_policy : ""
        server_assignment_mode = v.server_assignment_mode
        smtp_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.smtp_policy, "_EMPTY"))
        ) > 0 ? v.smtp_policy : v.ucs_server_profile_template != "" ? value.smtp_policy : ""
        snmp_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.snmp_policy, "_EMPTY"))
        ) > 0 ? v.snmp_policy : v.ucs_server_profile_template != "" ? value.snmp_policy : ""
        ssh_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.ssh_policy, "_EMPTY"))
        ) > 0 ? v.ssh_policy : v.ucs_server_profile_template != "" ? value.ssh_policy : ""
        static_uuid_address = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.static_uuid_address, "_EMPTY"))
        ) > 0 ? v.static_uuid_address : ""
        storage_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.storage_policy, "_EMPTY"))
        ) > 0 ? v.storage_policy : v.ucs_server_profile_template != "" ? value.storage_policy : ""
        syslog_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.syslog_policy, "_EMPTY"))
        ) > 0 ? v.syslog_policy : v.ucs_server_profile_template != "" ? value.syslog_policy : ""
        tags = length(v.tags
        ) > 0 ? v.tags : v.ucs_server_profile_template != [] ? value.tags : []
        target_platform = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.target_platform, "_EMPTY"))
        ) > 0 ? v.target_platform : v.ucs_server_profile_template != "" ? value.target_platform : "FIAttached"
        ucs_server_profile_template = v.ucs_server_profile_template
        uuid_pool = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.uuid_pool, "_EMPTY"))
        ) > 0 ? v.uuid_pool : v.ucs_server_profile_template != "" ? value.uuid_pool : ""
        virtual_kvm_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.virtual_kvm_policy, "_EMPTY"))
        ) > 0 ? v.virtual_kvm_policy : v.ucs_server_profile_template != "" ? value.virtual_kvm_policy : ""
        virtual_media_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.virtual_media_policy, "_EMPTY"))
        ) > 0 ? v.virtual_media_policy : v.ucs_server_profile_template != "" ? value.virtual_media_policy : ""
        wait_for_completion = v.wait_for_completion != null ? v.wait_for_completion : false
      } if v.ucs_server_profile_template == key || v.ucs_server_profile_template == ""
    ]
  ])

  ucs_server_merged = {
    for k, v in local.merge_with_templates : v.key_name => v
  }

  server_bucket_loop = {
    for k, v in local.ucs_server_merged : k => {
      action                      = v.action
      description                 = v.description
      organization                = v.organization
      resource_pool               = v.resource_pool
      serial_number               = v.serial_number
      server_assignment_mode      = v.server_assignment_mode
      static_uuid_address         = v.static_uuid_address
      tags                        = v.tags
      target_platform             = v.target_platform
      ucs_server_profile_template = v.ucs_server_profile_template
      uuid_pool                   = v.uuid_pool
      wait_for_completion         = v.wait_for_completion
      adapter_configuration_policy = v.adapter_configuration_policy != "" ? {
        moid        = local.adapter_configuration_policies[v.adapter_configuration_policy]
        object_type = "adapter.ConfigPolicy"
      } : null
      bios_policy = v.bios_policy != "" ? {
        moid        = local.bios_policies[v.bios_policy]
        object_type = "bios.Policy"
      } : null
      boot_order_policy = v.boot_order_policy != "" ? {
        moid        = local.boot_order_policies[v.boot_order_policy]
        object_type = "boot.PrecisionPolicy"
      } : null
      certificate_management_policy = v.certificate_management_policy != "" ? {
        moid        = local.certificate_management_policies[v.certificate_management_policy]
        object_type = "certificatemanagement.Policy"
      } : null
      device_connector_policy = v.device_connector_policy != "" ? {
        moid        = local.device_connector_policies[v.device_connector_policy]
        object_type = "deviceconnector.Policy"
      } : null
      imc_access_policy = v.imc_access_policy != "" ? {
        moid        = local.imc_access_policies[v.imc_access_policy]
        object_type = "access.Policy"
      } : null
      ipmi_over_lan_policy = v.ipmi_over_lan_policy != "" ? {
        moid        = local.ipmi_over_lan_policies[v.ipmi_over_lan_policy]
        object_type = "ipmioverlan.Policy"
      } : null
      lan_connectivity_policy = v.lan_connectivity_policy != "" ? {
        moid        = local.lan_connectivity_policies[v.lan_connectivity_policy]
        object_type = "vnic.LanConnectivityPolicy"
      } : null
      ldap_policy = v.ldap_policy != "" ? {
        moid        = local.ldap_policies[v.ldap_policy]
        object_type = "iam.LdapPolicy"
      } : null
      local_user_policy = v.local_user_policy != "" ? {
        moid        = local.local_user_policies[v.local_user_policy]
        object_type = "iam.EndPointUserPolicy"
      } : null
      network_connectivity_policy = v.network_connectivity_policy != "" ? {
        moid        = local.network_connectivity_policies[v.network_connectivity_policy]
        object_type = "networkconfig.Policy"
      } : null
      ntp_policy = v.ntp_policy != "" ? {
        moid        = local.ntp_policies[v.ntp_policy]
        object_type = "ntp.Policy"
      } : null
      persistent_memory_policy = v.persistent_memory_policy != "" ? {
        moid        = local.persistent_memory_policies[v.persistent_memory_policy]
        object_type = "memory.PersistentMemoryPolicy"
      } : null
      power_policy = v.power_policy != "" ? {
        moid        = local.power_policies[v.power_policy]
        object_type = "power.Policy"
      } : null
      san_connectivity_policy = v.san_connectivity_policy != "" ? {
        moid        = local.san_connectivity_policies[v.san_connectivity_policy]
        object_type = "vnic.SanConnectivityPolicy"
      } : null
      serial_over_lan_policy = v.serial_over_lan_policy != "" ? {
        moid        = local.serial_over_lan_policies[v.serial_over_lan_policy]
        object_type = "sol.Policy"
      } : null
      smtp_policy = v.smtp_policy != "" ? {
        moid        = local.smtp_policies[v.smtp_policy]
        object_type = "smtp.Policy"
      } : null
      snmp_policy = v.snmp_policy != "" ? {
        moid        = local.snmp_policies[v.snmp_policy]
        object_type = "snmp.Policy"
      } : null
      ssh_policy = v.ssh_policy != "" ? {
        moid        = local.ssh_policies[v.ssh_policy]
        object_type = "ssh.Policy"
      } : null
      storage_policy = v.storage_policy != "" ? {
        moid        = local.storage_policies[v.storage_policy]
        object_type = "storage.StoragePolicy"
      } : null
      syslog_policy = v.syslog_policy != "" ? {
        moid        = local.syslog_policies[v.syslog_policy]
        object_type = "syslog.Policy"
      } : null
      virtual_kvm_policy = v.virtual_kvm_policy != "" ? {
        moid        = local.virtual_kvm_policies[v.virtual_kvm_policy]
        object_type = "kvm.Policy"
      } : null
      virtual_media_policy = v.virtual_media_policy != "" ? {
        moid        = local.virtual_media_policies[v.virtual_media_policy]
        object_type = "vmedia.Policy"
      } : null
    }
  }

  ucs_server_profiles = {
    for k, v in local.server_bucket_loop : k => {
      action       = v.action
      description  = v.description
      organization = v.organization
      policy_bucket = toset(flatten(
        [
          v.adapter_configuration_policy,
          v.bios_policy,
          v.boot_order_policy,
          v.certificate_management_policy,
          v.device_connector_policy,
          v.imc_access_policy,
          v.ipmi_over_lan_policy,
          v.lan_connectivity_policy,
          v.ldap_policy,
          v.local_user_policy,
          v.network_connectivity_policy,
          v.ntp_policy,
          v.persistent_memory_policy,
          v.power_policy,
          v.san_connectivity_policy,
          v.serial_over_lan_policy,
          v.smtp_policy,
          v.snmp_policy,
          v.ssh_policy,
          v.storage_policy,
          v.syslog_policy,
          v.virtual_kvm_policy,
          v.virtual_media_policy
        ]
      ))
      resource_pool               = v.resource_pool
      serial_number               = v.serial_number
      server_assignment_mode      = v.server_assignment_mode
      static_uuid_address         = v.static_uuid_address
      tags                        = v.tags
      target_platform             = v.target_platform
      ucs_server_profile_template = v.ucs_server_profile_template
      uuid_pool                   = v.uuid_pool
      wait_for_completion         = v.wait_for_completion
    }
  }

}
