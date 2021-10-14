#______________________________________________
#
# Ethernet QoS Policy Variables
#______________________________________________

ethernet_qos_policies = {
  "best-effort" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Best Effort"
    mtu                   = 1500
    organization          = "UCS-DEMO2_hyperflex"
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
  "bronze" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Bronze"
    mtu                   = 1500
    organization          = "UCS-DEMO2_hyperflex"
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
  "gold" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Gold"
    mtu                   = 1500
    organization          = "UCS-DEMO2_hyperflex"
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
  "platinum" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Platinum"
    mtu                   = 1500
    organization          = "UCS-DEMO2_hyperflex"
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
  "silver" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Silver"
    mtu                   = 1500
    organization          = "UCS-DEMO2_hyperflex"
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
  "default" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Best Effort"
    mtu                   = 1500
    organization          = "UCS-DEMO2_hyperflex"
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
  "bronze_mtu9000" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Bronze"
    mtu                   = 9000
    organization          = "UCS-DEMO2_hyperflex"
    rate_limit            = 0
    tags                  = []
  }
  "platinum_mtu9000" = {
    burst                 = 10240
    description           = ""
    enable_trust_host_cos = false
    priority              = "Platinum"
    mtu                   = 9000
    organization          = "UCS-DEMO2_hyperflex"
    rate_limit            = 0
    tags                  = []
  }
}