#_________________________________________________________________________
#
# Intersight UCS Server Profile Variables
# GUI Location: Profiles > UCS Server Profile > Create UCS Server Profile
#_________________________________________________________________________

variable "ucs_server_profiles" {
  default = {
    default = {
      action                        = "No-op"
      adapter_configuration_policy  = ""
      bios_policy                   = ""
      boot_order_policy             = ""
      certificate_management_policy = ""
      description                   = ""
      device_connector_policy       = ""
      imc_access_policy             = ""
      ipmi_over_lan_policy          = ""
      lan_connectivity_policy       = ""
      ldap_policy                   = ""
      local_user_policy             = ""
      network_connectivity_policy   = ""
      ntp_policy                    = ""
      organization                  = "default"
      persistent_memory_policy      = ""
      power_policy                  = ""
      resource_pool                 = ""
      san_connectivity_policy       = ""
      sd_card_policy                = ""
      serial_number                 = ""
      serial_over_lan_policy        = ""
      server_assignment_mode        = "None"
      smtp_policy                   = ""
      snmp_policy                   = ""
      ssh_policy                    = ""
      static_uuid_address           = ""
      storage_policy                = ""
      syslog_policy                 = ""
      tags                          = []
      target_platform               = "FIAttached"
      uuid_pool                     = ""
      ucs_server_profile_template   = ""
      virtual_kvm_policy            = ""
      virtual_media_policy          = ""
      wait_for_completion           = false
    }
  }
  description = <<-EOT
  key - Name of the UCS Server Profile
  * action - Action to Perform on the Chassis Profile Assignment.  Options are:
    - Deploy
    - No-op
    - Unassign
  * adapter_configuration_policy - Name of the Adapter Configuration Policy to assign to the Profile.
  * bios_policy - Name of the BIOS Policy to assign to the Profile.
  * boot_order_policy - Name of the Boot Order Policy to assign to the Profile.
  * certificate_management_policy - Name of the Certificate Management Policy to assign to the Profile.
  * description - Description to Assign to the Profile.
  * device_connector_policy - Name of the Device Connector Policy to assign to the Profile.
  * imc_access_policy - Name of the IMC Access Policy to assign to the Profile.
  * ipmi_over_lan_policy - Name of the IPMI over LAN Policy to assign to the Profile.
  * lan_connectivity_policy - Name of the LAN Connectivity Policy to assign to the Profile.
  * ldap_policy - Name of the LDAP Policy to assign to the Profile.
  * local_user_policy - Name of the Local Users Policy to assign to the Profile.
  * network_connectivity_policy - Name of the Network Connectivity Policy to assign to the Profile.
  * ntp_policy - Name of the NTP Policy to assign to the Profile.
  * organization - Name of the Intersight Organization to assign this Profile to.  Default is default.
    -  https://intersight.com/an/settings/organizations/
  * persistent_memory_policy - Name of the Persistent Memory Policy to assign to the Profile.
  * power_policy - Name of the Power Policy to assign to the Profile.
  * resource_pool - Name of the Server Resource Pool to assign to the Policy.
  * san_connectivity_policy - Name of the SAN Connectivity Policy to assign to the Profile.
  * sd_card_policy - Name of the SD Card Policy to assign to the Profile.
  * serial_number - Serial Number of the Physical Server.
  * serial_over_lan_policy - Name of the Serial over LAN Policy to assign to the Profile.
  * server_assignment_mode - Source of the server assigned to the server profile. Values can be Static, Pool or None. Static is used if a server is attached directly to server profile. Pool is used if a resource pool is attached to server profile. None is used if no server or resource pool is attached to server profile.
    - None - No server is assigned to the server profile.
    - Pool - Server is assigned from a resource pool.
    - Static - Server is directly assigned to server profile using assign server.
  * smtp_policy - Name of the SMTP Policy to assign to the Profile.
  * snmp_policy - Name of the SNMP Policy to assign to the Profile.
  * ssh_policy - Name of the SSH Policy to assign to the Profile.
  * static_uuid_address - The UUID address for the server must include UUID prefix xxxxxxxx-xxxx-xxxx along with the UUID suffix of format xxxx-xxxxxxxxxxxx.  Joined with a "="
  * storage_policy - Name of the Storage Policy to assign to the Profile.
  * syslog_policy - Name of the Syslog Policy to assign to the Profile.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * target_platform - The platform for which the server profile is applicable. It can either be a server that is operating in standalone mode or which is attached to a Fabric Interconnect managed by Intersight.
    - FIAttached - (Default) - Servers which are connected to a Fabric Interconnect that is managed by Intersight.
    - Standalone - Servers which are operating in standalone mode i.e. not connected to a Fabric Interconnected.
  * uuid_pool - Name of a UUID Pool to Assign to the Policy.
  * ucs_server_profile_template - Name of the server template to apply to the server profile.
  * virtual_kvm_policy - Name of the Virtual KVM Policy to assign to the Profile.
  * virtual_media_policy - Name of the Virtual Media Policy to assign to the Profile.
  * wait_for_completion - This model object can trigger workflows. Use this option to wait for all running workflows to reach a complete state.
  EOT
  type = map(object(
    {
      action                        = optional(string)
      adapter_configuration_policy  = optional(string)
      bios_policy                   = optional(string)
      boot_order_policy             = optional(string)
      certificate_management_policy = optional(string)
      description                   = optional(string)
      device_connector_policy       = optional(string)
      imc_access_policy             = optional(string)
      ipmi_over_lan_policy          = optional(string)
      lan_connectivity_policy       = optional(string)
      ldap_policy                   = optional(string)
      local_user_policy             = optional(string)
      network_connectivity_policy   = optional(string)
      ntp_policy                    = optional(string)
      operating_system              = optional(string)
      organization                  = optional(string)
      persistent_memory_policy      = optional(string)
      power_policy                  = optional(string)
      resource_pool                 = optional(string)
      san_connectivity_policy       = optional(string)
      sd_card_policy                = optional(string)
      serial_number                 = optional(string)
      serial_over_lan_policy        = optional(string)
      server_assignment_mode        = optional(string)
      smtp_policy                   = optional(string)
      snmp_policy                   = optional(string)
      ssh_policy                    = optional(string)
      static_uuid_address           = optional(string)
      storage_policy                = optional(string)
      syslog_policy                 = optional(string)
      tags                          = optional(list(map(string)))
      target_platform               = optional(string)
      uuid_pool                     = optional(string)
      ucs_server_profile_template   = optional(string)
      virtual_kvm_policy            = optional(string)
      virtual_media_policy          = optional(string)
      wait_for_completion           = optional(bool)
    }
  ))
}

#_________________________________________________________________________
#
# Intersight UCS Server Profile Module
# GUI Location: Profiles > UCS Server Profile > Create UCS Server Profile
#_________________________________________________________________________

module "ucs_server_profiles" {
  depends_on = [
    local.org_moids,
  ]
  version                = ">=0.9.6"
  source                 = "terraform-cisco-modules/imm/intersight//modules/ucs_server_profiles"
  for_each               = local.ucs_server_profiles
  action                 = each.value.action
  description            = each.value.description != "" ? each.value.description : "${each.key} Server Profile."
  name                   = each.key
  org_moid               = local.org_moids[each.value.organization].moid
  server_assignment_mode = each.value.server_assignment_mode
  static_uuid_address    = each.value.static_uuid_address
  tags                   = length(each.value.tags) > 0 ? each.value.tags : local.tags
  target_platform        = each.value.target_platform == "Standalone" ? "Standalone" : "FIAttached"
  uuid_pool = each.value.uuid_pool != "" ? [
    {
      moid = local.uuid_pools[each.value.uuid_pool]
    }
  ] : []
  wait_for_completion = each.value.wait_for_completion
  assigned_server = each.value.server_assignment_mode == "Static" ? [
    {
      moid        = data.intersight_compute_physical_summary.server[each.key].results[0].moid
      object_type = data.intersight_compute_physical_summary.server[each.key].results[0].source_object_type
    }
  ] : []
  associated_server_pool = each.value.server_assignment_mode == "Pool" ? [
    {
      moid = local.resource_pools[each.value.resource_pool].moid
    }
  ] : []
}
