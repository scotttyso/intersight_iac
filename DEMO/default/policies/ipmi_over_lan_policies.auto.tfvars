#______________________________________________
#
# IPMI over LAN Policy Variables
#______________________________________________

ipmi_over_lan_policies = {
  "default" = {
    description  = "default IPMI over LAN Policy"
    enabled      = true
    ipmi_key     = 1
    organization = "default"
    privilege    = "admin"
    tags         = []
  }
}