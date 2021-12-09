#______________________________________________
#
# Ethernet Network Control Policy Variables
#______________________________________________

ethernet_network_control_policies = {
  "LLDP" = {
    action_on_uplink_fail = "linkDown"
    cdp_enable            = false
    description           = "LLDP Ethernet Network Control Policy"
    lldp_enable_receive   = true
    lldp_enable_transmit  = true
    mac_register_mode     = "nativeVlanOnly"
    mac_security_forge    = "allow"
    organization          = "cx_demo"
    tags                  = []
  }
}