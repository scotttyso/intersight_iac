#______________________________________________
#
# UCS Domain Profile Variables
#______________________________________________

ucs_domain_profiles = {
  "dennis-ucs" = {
    action                      = "No-op"
    assign_switches             = false
    description                 = "dennis-ucs UCS Domain Profile"
    device_model                = "UCS-FI-6454"
    network_connectivity_policy = "dennis-ucs"
    ntp_policy                  = "dennis-ucs"
    organization                = "dennis_demo"
    port_policy_fabric_a        = "dennis-ucs-a"
    port_policy_fabric_b        = "dennis-ucs-b"
    snmp_policy                 = "dennis_demo_domain"
    serial_number_fabric_a      = ""
    serial_number_fabric_b      = ""
    switch_control_policy       = "dennis-ucs"
    syslog_policy               = "dennis_demo_domain"
    system_qos_policy           = "dennis-ucs"
    vlan_policy_fabric_a        = "dennis-ucs"
    vlan_policy_fabric_b        = "dennis-ucs"
    vsan_policy_fabric_a        = "dennis-ucs-A"
    vsan_policy_fabric_b        = "dennis-ucs-B"
    tags         = []
  }
}