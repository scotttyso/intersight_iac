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
  # UCS Server Profiles Section - Locals
  #__________________________________________________________
  ucs_server_loop_1 = {
    for k, v in var.ucs_server_profiles : k => {
      action                        = v.action != null ? v.action : "No-op"
      adapter_policy                = v.adapter_policy != null ? v.adapter_policy : null
      assign_server                 = v.assign_server != null ? v.assign_server : false
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
      san_connectivity_policy       = v.san_connectivity_policy != null ? v.san_connectivity_policy : null
      sd_card_policy                = v.sd_card_policy != null ? v.sd_card_policy : null
      serial_number                 = v.serial_number != null ? v.serial_number : null
      serial_over_lan_policy        = v.serial_over_lan_policy != null ? v.serial_over_lan_policy : null
      smtp_policy                   = v.smtp_policy != null ? v.smtp_policy : null
      snmp_policy                   = v.snmp_policy != null ? v.snmp_policy : null
      ssh_policy                    = v.ssh_policy != null ? v.ssh_policy : null
      storage_policy                = v.storage_policy != null ? v.storage_policy : null
      syslog_policy                 = v.syslog_policy != null ? v.syslog_policy : null
      tags                          = v.tags != null ? v.tags : []
      target_platform               = v.target_platform != null ? v.target_platform : "FIAttached"
      ucs_server_profile_template   = v.ucs_server_profile_template != null ? v.ucs_server_profile_template : ""
      virtual_kvm_policy            = v.virtual_kvm_policy != null ? v.virtual_kvm_policy : null
      virtual_media_policy          = v.virtual_media_policy != null ? v.virtual_media_policy : null
      wait_for_completion           = v.wait_for_completion != null ? v.wait_for_completion : false
    }
  }


  #__________________________________________________________
  #
  # UCS Server Profile Templates Section - Locals
  #__________________________________________________________
  ucs_server_profile_templates = {
    for k, v in var.ucs_server_profile_templates : k => {
      adapter_policy                = v.adapter_policy != null ? v.adapter_policy : ""
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
      virtual_kvm_policy            = v.virtual_kvm_policy != null ? v.virtual_kvm_policy : ""
      virtual_media_policy          = v.virtual_media_policy != null ? v.virtual_media_policy : ""
    }
  }

  merge_with_templates = flatten([
    for k, v in local.ucs_server_loop_1 : [
      for key, value in local.ucs_server_profile_templates : {
        action = v.action
        adapter_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.adapter_policy, "_EMPTY"))
        ) > 0 ? v.adapter_policy : v.ucs_server_profile_template != "" ? value.adapter_policy : ""
        assign_server = v.assign_server
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
        smtp_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.smtp_policy, "_EMPTY"))
        ) > 0 ? v.smtp_policy : v.ucs_server_profile_template != "" ? value.smtp_policy : ""
        snmp_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.snmp_policy, "_EMPTY"))
        ) > 0 ? v.snmp_policy : v.ucs_server_profile_template != "" ? value.snmp_policy : ""
        ssh_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.ssh_policy, "_EMPTY"))
        ) > 0 ? v.ssh_policy : v.ucs_server_profile_template != "" ? value.ssh_policy : ""
        storage_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.storage_policy, "_EMPTY"))
        ) > 0 ? v.storage_policy : v.ucs_server_profile_template != "" ? value.storage_policy : ""
        syslog_policy = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.syslog_policy, "_EMPTY"))
        ) > 0 ? v.syslog_policy : v.ucs_server_profile_template != "" ? value.syslog_policy : ""
        tags = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.tags, "_EMPTY"))
        ) > 0 ? v.tags : v.ucs_server_profile_template != "" ? value.tags : ""
        target_platform = length(
          regexall("^[a-zA-Z0-9]", coalesce(v.target_platform, "_EMPTY"))
        ) > 0 ? v.target_platform : v.ucs_server_profile_template != "" ? value.target_platform : ""
        ucs_server_profile_template = v.ucs_server_profile_template
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

  ucs_server_profiles = {
    for k, v in local.merge_with_templates : v.key_name => v
  }

}

