#_________________________________________________________________________
#
# Intersight UCS Server Profile Tempaltes Variables
# GUI Location: Profiles > UCS Server Template > Create UCS Server Template
#_________________________________________________________________________

variable "ucs_server_profile_templates" {
  default = {
    default = {
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
      operating_system              = "VMware"
      persistent_memory_policy      = ""
      power_policy                  = ""
      san_connectivity_policy       = ""
      sd_card_policy                = ""
      serial_over_lan_policy        = ""
      smtp_policy                   = ""
      snmp_policy                   = ""
      ssh_policy                    = ""
      storage_policy                = ""
      syslog_policy                 = ""
      tags                          = []
      target_platform               = "FIAttached"
      uuid_pool                     = ""
      virtual_kvm_policy            = ""
      virtual_media_policy          = ""
    }
  }
  description = <<-EOT
  key - Name of the UCS Server Profile Template
  * adapter_configuration_policy - Name of the Adapter Configuration Policy to assign to the Template.
  * bios_policy - Name of the BIOS Policy to assign to the Template.
  * boot_order_policy - Name of the Boot Order Policy to assign to the Template.
  * certificate_management_policy - Name of the Certificate Management Policy to assign to the Template.
  * description - Description to Assign to the Profile.
  * device_connector_policy - Name of the Device Connector Policy to assign to the Template.
  * imc_access_policy - Name of the IMC Access Policy to assign to the Template.
  * ipmi_over_lan_policy - Name of the IPMI over LAN Policy to assign to the Template.
  * lan_connectivity_policy - Name of the LAN Connectivity Policy to assign to the Template.
  * ldap_policy - Name of the LDAP Policy to assign to the Template.
  * local_user_policy - Name of the Local Users Policy to assign to the Template.
  * network_connectivity_policy - Name of the Network Connectivity Policy to assign to the Template.
  * ntp_policy - Name of the NTP Policy to assign to the Template.
  * operating_system - Operating System to Install on the Server.  Options are:
    - Linux
    - VMware - (Default)
    - Windows
  * persistent_memory_policy - Name of the Persistent Memory Policy to assign to the Template.
  * power_policy - Name of the Power Policy to assign to the Template.
  * san_connectivity_policy - Name of the SAN Connectivity Policy to assign to the Template.
  * sd_card_policy - Name of the SD Card Policy to assign to the Template.
  * serial_over_lan_policy - Name of the Serial over LAN Policy to assign to the Template.
  * smtp_policy - Name of the SMTP Policy to assign to the Template.
  * snmp_policy - Name of the SNMP Policy to assign to the Template.
  * ssh_policy - Name of the SSH Policy to assign to the Template.
  * storage_policy - Name of the Storage Policy to assign to the Template.
  * syslog_policy - Name of the Syslog Policy to assign to the Template.
  * tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * target_platform - The platform for which the server profile is applicable. It can either be a server that is operating in standalone mode or which is attached to a Fabric Interconnect managed by Intersight.
    - FIAttached - (Default) - Servers which are connected to a Fabric Interconnect that is managed by Intersight.
    - Standalone - Servers which are operating in standalone mode i.e. not connected to a Fabric Interconnected.
  * uuid_pool - Name of a UUID Pool to Assign to the Policy.
  * virtual_kvm_policy - Name of the Virtual KVM Policy to assign to the Template.
  * virtual_media_policy - Name of the Virtual Media Policy to assign to the Template.
  EOT
  type = map(object(
    {
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
      persistent_memory_policy      = optional(string)
      power_policy                  = optional(string)
      san_connectivity_policy       = optional(string)
      sd_card_policy                = optional(string)
      serial_over_lan_policy        = optional(string)
      smtp_policy                   = optional(string)
      snmp_policy                   = optional(string)
      ssh_policy                    = optional(string)
      storage_policy                = optional(string)
      syslog_policy                 = optional(string)
      tags                          = optional(list(map(string)))
      uuid_pool                     = optional(string)
      target_platform               = optional(string)
      virtual_kvm_policy            = optional(string)
      virtual_media_policy          = optional(string)
    }
  ))
}
