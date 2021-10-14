#______________________________________________
#
# Syslog Policy Variables
#______________________________________________

syslog_policies = {
  "UCS-DEMO2_domain" = {
    description        = ""
    local_min_severity = "critical"
    organization       = "UCS-DEMO2"
    remote_clients    = [
      {
        enabled      = true
        hostname     = "10.60.7.122"
        min_severity = "informational"
        port         = 514
        protocol     = "udp"
      },
    ]
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