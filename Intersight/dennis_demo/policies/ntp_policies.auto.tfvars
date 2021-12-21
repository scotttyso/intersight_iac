#______________________________________________
#
# NTP Policy Variables
#______________________________________________

ntp_policies = {
  "dennis-ucs" = {
    description  = "dennis-ucs NTP Policy"
    enabled      = true
    organization = "dennis_demo"
    timezone     = "America/New_York"
    ntp_servers = [
      "0.north-america.pool.ntp.org",
      "1.north-america.pool.ntp.org",
    ]
    tags         = []
  }
}