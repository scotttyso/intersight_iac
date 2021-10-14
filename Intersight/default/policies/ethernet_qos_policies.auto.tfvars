#______________________________________________
#
# Ethernet QoS Policy Variables
#______________________________________________

ethernet_qos_policies = {
  "Asgard_Management" = {
    burst                 = 1024
    description           = "Asgard_Management Ethernet QoS Policy"
    enable_trust_host_cos = false
    priority              = "Silver"
    mtu                   = 9216
    organization          = "default"
    rate_limit            = 0
    tags                  = []
  }
  "Asgard_Migration" = {
    burst                 = 1024
    description           = "Asgard_Migration Ethernet QoS Policy"
    enable_trust_host_cos = false
    priority              = "Bronze"
    mtu                   = 9216
    organization          = "default"
    rate_limit            = 0
    tags                  = []
  }
  "Asgard_Storage" = {
    burst                 = 1024
    description           = "Asgard_Storage Ethernet QoS Policy"
    enable_trust_host_cos = false
    priority              = "Platinum"
    mtu                   = 9216
    organization          = "default"
    rate_limit            = 0
    tags                  = []
  }
  "Asgard_VMs" = {
    burst                 = 1024
    description           = "Asgard_VMs Ethernet QoS Policy"
    enable_trust_host_cos = false
    priority              = "Gold"
    mtu                   = 9216
    organization          = "default"
    rate_limit            = 0
    tags                  = []
  }
}