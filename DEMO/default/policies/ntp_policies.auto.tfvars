#______________________________________________
#
# NTP Policy Variables
#______________________________________________

ntp_policies = {
  "demo-ucs" = {
    description  = "demo-ucs NTP Policy"
    enabled      = true
    organization = "default"
    timezone     = "America/New_York"
    ntp_servers = [
      "0.north-america.pool.ntp.org",
      "1.north-america.pool.ntp.org",
    ]
    tags = []
  }
}