#______________________________________________
#
# Ethernet QoS Policy Variables
#______________________________________________

ethernet_qos_policies = {
  "default" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Best Effort"
    mtu                   = 1500
    organization          = "UCS-DEMO2_CAGIP"
    rate_limit            = 0
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
  "default_mtu9000" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Best Effort"
    mtu                   = 9000
    organization          = "UCS-DEMO2_CAGIP"
    rate_limit            = 0
    tags                  = []
  }
}