#______________________________________________
#
# UCS Domain Profile Variables
#______________________________________________

ucs_domain_profiles = {
  "UCS-DEMO2" = {
    action                      = "No-op"
    assign_switches             = false
    description                 = ""
    device_model                = ""
    network_connectivity_policy = "UCS-DEMO2"
    ntp_policy                  = "UCS-DEMO2"
    organization                = "UCS-DEMO2"
    port_policy_fabric_a        = "UCS-DEMO2-A"
    port_policy_fabric_b        = "UCS-DEMO2-B"
    snmp_policy                 = "UCS-DEMO2"
    serial_number_fabric_a      = ""
    serial_number_fabric_b      = ""
    switch_control_policy       = "UCS-DEMO2"
    syslog_policy               = "UCS-DEMO2"
    system_qos_policy           = "UCS-DEMO2"
    vlan_policy_fabric_a        = "UCS-DEMO2-A"
    vlan_policy_fabric_b        = "UCS-DEMO2-B"
    vsan_policy_fabric_a        = "UCS-DEMO2-A"
    vsan_policy_fabric_b        = "UCS-DEMO2-B"
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
}