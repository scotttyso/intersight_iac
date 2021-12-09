#______________________________________________
#
# NTP Policy Variables
#______________________________________________

ntp_policies = {
  "asgard-ucs" = {
    description  = "asgard-ucs NTP Policy"
    enabled      = true
    organization = "canada"
    timezone     = "America/New_York"
    ntp_servers = [
      "0.north-america.pool.ntp.org",
      "1.north-america.pool.ntp.org",
    ]
    tags = []
  }
}