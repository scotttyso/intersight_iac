#__________________________________________________________
#
# Adapter Configuration Policy Outputs
#__________________________________________________________

output "adapter_configuration_policies" {
  description = "Moid's of the Adapter Configuration Policies."
  value = var.adapter_configuration_policies != {} ? { for v in sort(
    keys(intersight_adapter_config_policy.adapter_configuration_policies)
  ) : v => intersight_adapter_config_policy.adapter_configuration_policies[v].moid } : {}
}


#__________________________________________________________
#
# BIOS Policy Outputs
#__________________________________________________________

output "bios_policies" {
  description = "Moid's of the BIOS Policies."
  value = var.bios_policies != {} ? { for v in sort(
    keys(intersight_bios_policy.bios_policies)
  ) : v => intersight_bios_policy.bios_policies[v].moid } : {}
}


#__________________________________________________________
#
# Boot Order Policy Outputs
#__________________________________________________________

output "boot_order_policies" {
  description = "Moid's of the Boot Order Policies."
  value = var.boot_order_policies != {} ? { for v in sort(
    keys(intersight_boot_precision_policy.boot_order_policies)
  ) : v => intersight_boot_precision_policy.boot_order_policies[v].moid } : {}
}


#__________________________________________________________
#
# Certificate Management Policy Outputs
#__________________________________________________________

output "certificate_management_policies" {
  description = "Moid's of the Certificate Management Policies."
  value = var.certificate_management_policies != {} ? { for v in sort(
    keys(intersight_certificatemanagement_policy.certificate_management_policies)
  ) : v => intersight_certificatemanagement_policy.certificate_management_policies[v].moid } : {}
}


#__________________________________________________________
#
# Device Connector Policy Outputs
#__________________________________________________________

output "device_connector_policies" {
  description = "Moid's of the Device Connector Policies."
  value = var.device_connector_policies != {} ? { for v in sort(
    keys(intersight_deviceconnector_policy.device_connector_policies)
  ) : v => intersight_deviceconnector_policy.device_connector_policies[v].moid } : {}
}


#__________________________________________________________
#
# IMC Access Policy Outputs
#__________________________________________________________

output "imc_access_policies" {
  description = "Moid's of the IMC Access Policies."
  value = var.imc_access_policies != {} ? { for v in sort(
    keys(intersight_access_policy.imc_access_policies)
  ) : v => intersight_access_policy.imc_access_policies[v].moid } : {}
}


#__________________________________________________________
#
# IPMI over LAN Policy Outputs
#__________________________________________________________

output "ipmi_over_lan_policies" {
  description = "Moid's of the IPMI over LAN Policies."
  value = var.ipmi_over_lan_policies != {} ? { for v in sort(
    keys(intersight_ipmioverlan_policy.ipmi_over_lan_policies)
  ) : v => intersight_ipmioverlan_policy.ipmi_over_lan_policies[v].moid } : {}
}


#__________________________________________________________
#
# LAN Connectivity Policy Outputs
#__________________________________________________________

output "lan_connectivity_policies" {
  description = "Moid's of the LAN Connectivity Policies."
  value = var.lan_connectivity_policies != {} ? { for v in sort(
    keys(intersight_vnic_lan_connectivity_policy.lan_connectivity_policies)
  ) : v => intersight_vnic_lan_connectivity_policy.lan_connectivity_policies[v].moid } : {}
}


#__________________________________________________________
#
# LDAP Policy Outputs
#__________________________________________________________

output "ldap_policies" {
  description = "Moid's of the LDAP Policies."
  value = var.ldap_policies != {} ? { for v in sort(
    keys(intersight_iam_ldap_policy.ldap_policies)
  ) : v => intersight_iam_ldap_policy.ldap_policies[v].moid } : {}
}


#__________________________________________________________
#
# Local User Policy Outputs
#__________________________________________________________

output "local_user_policies" {
  description = "Moid's of the Local User Policies."
  value = var.local_user_policies != {} ? { for v in sort(
    keys(intersight_iam_end_point_user_policy.local_user_policies)
  ) : v => intersight_iam_end_point_user_policy.local_user_policies[v].moid } : {}
}


#__________________________________________________________
#
# Merged Profile Outputs
#__________________________________________________________

output "ucs_domain_policies" {
  value = local.ucs_domain_policies
}


#__________________________________________________________
#
# Network Connectivity Policy Outputs
#__________________________________________________________

output "network_connectivity_policies" {
  description = "Moid's of the Network Connectivity Policies."
  value = var.network_connectivity_policies != {} ? { for v in sort(
    keys(intersight_networkconfig_policy.network_connectivity_policies)
  ) : v => intersight_networkconfig_policy.network_connectivity_policies[v].moid } : {}
}


#__________________________________________________________
#
# NTP Policy Outputs
#__________________________________________________________

output "ntp_policies" {
  description = "Moid's of the NTP Policies."
  value = var.ntp_policies != {} ? { for v in sort(
    keys(intersight_ntp_policy.ntp_policies)
  ) : v => intersight_ntp_policy.ntp_policies[v].moid } : {}
}


#__________________________________________________________
#
# Persistent Memory Policy Outputs
#__________________________________________________________

output "persistent_memory_policies" {
  description = "Moid's of the Persistent Memory Policies."
  value = var.persistent_memory_policies != {} ? { for v in sort(
    keys(intersight_memory_persistent_memory_policy.persistent_memory_policies)
  ) : v => intersight_memory_persistent_memory_policy.persistent_memory_policies[v].moid } : {}
}


#__________________________________________________________
#
# Port Policy Outputs
#__________________________________________________________

output "port_policies" {
  description = "Moid's of the Port Policies."
  value = var.port_policies != {} ? { for v in sort(
    keys(intersight_fabric_port_policy.port_policies)
  ) : v => intersight_fabric_port_policy.port_policies[v].moid } : {}
}


#__________________________________________________________
#
# Power Policy Outputs
#__________________________________________________________

output "power_policies" {
  description = "Moid's of the Power Policies."
  value = var.power_policies != {} ? { for v in sort(
    keys(intersight_power_policy.power_policies)
  ) : v => intersight_power_policy.power_policies[v].moid } : {}
}


#__________________________________________________________
#
# SAN Connectivity Policy Outputs
#__________________________________________________________

output "san_connectivity_policies" {
  description = "Moid's of the SAN Connectivity Policies."
  value = var.san_connectivity_policies != {} ? { for v in sort(
    keys(intersight_vnic_san_connectivity_policy.san_connectivity_policies)
  ) : v => intersight_vnic_san_connectivity_policy.san_connectivity_policies[v].moid } : {}
}


#__________________________________________________________
#
# Serial over LAN Policy Outputs
#__________________________________________________________

output "serial_over_lan_policies" {
  description = "Moid's of the Serial over LAN Policies."
  value = var.serial_over_lan_policies != {} ? { for v in sort(
    keys(intersight_sol_policy.serial_over_lan_policies)
  ) : v => intersight_sol_policy.serial_over_lan_policies[v].moid } : {}
}


#__________________________________________________________
#
# SMTP Policy Outputs
#__________________________________________________________

output "smtp_policies" {
  description = "Moid's of the SMTP Policies."
  value = var.smtp_policies != {} ? { for v in sort(
    keys(intersight_smtp_policy.smtp_policies)
  ) : v => intersight_smtp_policy.smtp_policies[v].moid } : {}
}


#__________________________________________________________
#
# SNMP Policy Outputs
#__________________________________________________________

output "snmp_policies" {
  description = "Moid's of the SNMP Policies."
  value = var.snmp_policies != {} ? { for v in sort(
    keys(intersight_snmp_policy.snmp_policies)
  ) : v => intersight_snmp_policy.snmp_policies[v].moid } : {}
}


#__________________________________________________________
#
# SSH Policy Outputs
#__________________________________________________________

output "ssh_policies" {
  description = "Moid's of the SSH Policies."
  value = var.ssh_policies != {} ? { for v in sort(
    keys(intersight_ssh_policy.ssh_policies)
  ) : v => intersight_ssh_policy.ssh_policies[v].moid } : {}
}


#__________________________________________________________
#
# Storage Policy Outputs
#__________________________________________________________

output "storage_policies" {
  description = "Moid's of the Storage Policies."
  value = var.storage_policies != {} ? { for v in sort(
    keys(intersight_storage_storage_policy.storage_policies)
  ) : v => intersight_storage_storage_policy.storage_policies[v].moid } : {}
}


#__________________________________________________________
#
# Switch Control Policy Outputs
#__________________________________________________________

output "switch_control_policies" {
  description = "Moid's of the Switch Control Policies."
  value = var.switch_control_policies != {} ? { for v in sort(
    keys(intersight_fabric_switch_control_policy.switch_control_policies)
  ) : v => intersight_fabric_switch_control_policy.switch_control_policies[v].moid } : {}
}


#__________________________________________________________
#
# Syslog Policy Outputs
#__________________________________________________________

output "syslog_policies" {
  description = "Moid's of the Syslog Policies."
  value = var.syslog_policies != {} ? { for v in sort(
    keys(intersight_syslog_policy.syslog_policies)
  ) : v => intersight_syslog_policy.syslog_policies[v].moid } : {}
}


#__________________________________________________________
#
# System QoS Policy Outputs
#__________________________________________________________

output "system_qos_policies" {
  description = "Moid's of the System QoS Policies."
  value = var.system_qos_policies != {} ? { for v in sort(
    keys(intersight_fabric_system_qos_policy.system_qos_policies)
  ) : v => intersight_fabric_system_qos_policy.system_qos_policies[v].moid } : {}
}


#__________________________________________________________
#
# Thermal Policy Outputs
#__________________________________________________________

output "thermal_policies" {
  description = "Moid's of the Thermal Policies."
  value = var.thermal_policies != {} ? { for v in sort(
    keys(intersight_thermal_policy.thermal_policies)
  ) : v => intersight_thermal_policy.thermal_policies[v].moid } : {}
}


#__________________________________________________________
#
# Virtual KVM Policy Outputs
#__________________________________________________________

output "virtual_kvm_policies" {
  description = "Moid's of the Virtual KVM Policies."
  value = var.virtual_kvm_policies != {} ? { for v in sort(
    keys(intersight_kvm_policy.virtual_kvm_policies)
  ) : v => intersight_kvm_policy.virtual_kvm_policies[v].moid } : {}
}


#__________________________________________________________
#
# Virtual Media Policy Outputs
#__________________________________________________________

output "virtual_media_policies" {
  description = "Moid's of the Virtual Media Policies."
  value = var.virtual_media_policies != {} ? { for v in sort(
    keys(intersight_vmedia_policy.virtual_media_policies)
  ) : v => intersight_vmedia_policy.virtual_media_policies[v].moid } : {}
}


#__________________________________________________________
#
# VLAN Policy Outputs
#__________________________________________________________

output "vlan_policies" {
  description = "moid of the VLAN Policies."
  value = var.vlan_policies != {} ? { for v in sort(
    keys(intersight_fabric_eth_network_policy.vlan_policies)
  ) : v => intersight_fabric_eth_network_policy.vlan_policies[v].moid } : {}
}


#__________________________________________________________
#
# VSAN Policy Outputs
#__________________________________________________________

output "vsan_policies" {
  description = "Moid's of the VSAN Policies."
  value = var.vsan_policies != {} ? { for v in sort(
    keys(intersight_fabric_fc_network_policy.vsan_policies)
  ) : v => intersight_fabric_fc_network_policy.vsan_policies[v].moid } : {}
}
