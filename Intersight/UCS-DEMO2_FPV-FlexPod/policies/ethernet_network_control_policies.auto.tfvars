#______________________________________________
#
# Ethernet Network Control Policy Variables
#______________________________________________

ethernet_network_control_policies = {
  "Enable-CDP-LLDP" = {
    action_on_uplink_fail = "linkDown"
    cdp_enable            = true
    description           = ""
    lldp_enable_receive   = true
    lldp_enable_transmit  = true
    mac_register_mode     = "nativeVlanOnly"
    mac_security_forge    = "allow"
    organization          = "UCS-DEMO2_FPV-FlexPod"
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