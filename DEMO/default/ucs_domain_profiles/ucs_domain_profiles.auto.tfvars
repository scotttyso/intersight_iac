#______________________________________________
#
# UCS Domain Profile Variables
#______________________________________________

ucs_domain_profiles = {
  "demo-ucs" = {
    action                      = "No-op"
    assign_switches             = false
    description                 = "demo-ucs UCS Domain Profile"
    device_model                = "UCS-FI-6454"
    network_connectivity_policy = "demo-ucs"
    ntp_policy                  = "demo-ucs"
    organization                = "default"
    port_policy_fabric_a        = "demo-ucs-a"
    port_policy_fabric_b        = "demo-ucs-b"
    snmp_policy                 = "default_domain"
    serial_number_fabric_a      = ""
    serial_number_fabric_b      = ""
    switch_control_policy       = "demo-ucs"
    syslog_policy               = "default_domain"
    system_qos_policy           = "demo-ucs"
    vlan_policy_fabric_a        = "demo-ucs"
    vlan_policy_fabric_b        = "demo-ucs"
    vsan_policy_fabric_a        = "demo-ucs-A"
    vsan_policy_fabric_b        = "demo-ucs-B"
    tags                        = []
  }
}