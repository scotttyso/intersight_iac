#______________________________________________
#
# Switch Control Policy Variables
#______________________________________________

switch_control_policies = {
  "UCS-DEMO2" = {
    description                  = ""
    mac_address_table_aging      = "Custom"
    mac_aging_time               = 14500
    organization                 = "UCS-DEMO2"
    udld_message_interval        = 15
    udld_recovery_action         = "reset"
    vlan_port_count_optimization = false
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