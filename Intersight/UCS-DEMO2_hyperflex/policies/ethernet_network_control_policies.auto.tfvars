#______________________________________________
#
# Ethernet Network Control Policy Variables
#______________________________________________

ethernet_network_control_policies = {
  "HyperFlex-infra" = {
    action_on_uplink_fail = "linkDown"
    cdp_enable            = true
    description           = "Network-Control-policy-for-infrastructure-vNICs-HyperFlex-servers"
    lldp_enable_receive   = false
    lldp_enable_transmit  = false
    mac_register_mode     = "nativeVlanOnly"
    mac_security_forge    = "allow"
    organization          = "UCS-DEMO2_hyperflex"
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
  "HyperFlex-vm" = {
    action_on_uplink_fail = "linkDown"
    cdp_enable            = true
    description           = "Network-Control-policy-for-VM-vNICs-on-HyperFlex-servers"
    lldp_enable_receive   = false
    lldp_enable_transmit  = false
    mac_register_mode     = "nativeVlanOnly"
    mac_security_forge    = "allow"
    organization          = "UCS-DEMO2_hyperflex"
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