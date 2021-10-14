#______________________________________________
#
# Ethernet QoS Policy Variables
#______________________________________________

ethernet_qos_policies = {
  "Standalone_qos" = {
    description           = "Standalone_qos Ethernet QoS Policy"
    enable_trust_host_cos = false
    mtu                   = 1500
    organization          = "Standalone"
    rate_limit            = 0
    tags                  = []
  }
}