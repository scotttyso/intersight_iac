#______________________________________________
#
# UCS Domain Profile Variables
#______________________________________________

ucs_domain_profiles = {
  "asgard-ucs" = {
    action                      = "No-op"
    assign_switches             = false
    description                 = "asgard-ucs UCS Domain Profile"
    device_model                = "UCS-FI-64108"
    network_connectivity_policy = "Asgard_dns"
    ntp_policy                  = "Asgard_ntp"
    organization                = "default"
    port_policy_fabric_a        = "asgard-ucs_A"
    port_policy_fabric_b        = "asgard-ucs_B"
    snmp_policy                 = "Asgard_snmp"
    serial_number_fabric_a      = ""
    serial_number_fabric_b      = ""
    switch_control_policy       = "asgard-ucs_sw_ctrl"
    syslog_policy               = "Asgard_syslog_domain"
    system_qos_policy           = "asgard-ucs_qos"
    vlan_policy_fabric_a        = "asgard-ucs_vlans"
    vlan_policy_fabric_b        = "asgard-ucs_vlans"
    vsan_policy_fabric_a        = "asgard-ucs_A"
    vsan_policy_fabric_b        = "asgard-ucs_B"
    tags         = []
  }
}