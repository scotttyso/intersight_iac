#______________________________________________
#
# Ethernet QoS Policy Variables
#______________________________________________

ethernet_qos_policies = {
  "iac-standalone_qos" = {
    description           = "iac-standalone_qos Ethernet QoS Policy"
    enable_trust_host_cos = false
    mtu                   = 1500
    rate_limit            = 0
    tags                  = []
  }
}