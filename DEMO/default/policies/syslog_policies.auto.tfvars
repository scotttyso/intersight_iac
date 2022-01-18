#______________________________________________
#
# Syslog Policy Variables
#______________________________________________

syslog_policies = {
  "default" = {
    description        = "default Syslog Policy"
    local_min_severity = "warning"
    organization       = "default"
    remote_clients = [
      {
        enabled      = false
        hostname     = "0.0.0.0"
        min_severity = "warning"
        port         = 514
        protocol     = "udp"
      },
      {
        enabled      = false
        hostname     = "0.0.0.0"
        min_severity = "warning"
        port         = 514
        protocol     = "udp"
      }
    ]
    tags = []
  }
}