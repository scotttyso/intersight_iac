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
    organization          = "UCS-DEMO2_ClientA"
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
  "5Gb-platinum" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Platinum"
    mtu                   = 1500
    organization          = "UCS-DEMO2_ClientA"
    rate_limit            = 5000
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
  "1Gb-bronze" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Best Effort"
    mtu                   = 1500
    organization          = "UCS-DEMO2_ClientA"
    rate_limit            = 1000
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
  "100Mb" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Best Effort"
    mtu                   = 1500
    organization          = "UCS-DEMO2_ClientA"
    rate_limit            = 100
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
  "5Gb-platinum_mtu9000" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Platinum"
    mtu                   = 9000
    organization          = "UCS-DEMO2_ClientA"
    rate_limit            = 5000
    tags                  = []
  }
  "default_mtu9000" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Best Effort"
    mtu                   = 9000
    organization          = "UCS-DEMO2_ClientA"
    rate_limit            = 0
    tags                  = []
  }
}