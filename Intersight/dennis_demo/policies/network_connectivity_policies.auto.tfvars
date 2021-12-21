#______________________________________________
#
# Network Connectivity Policy Variables
#______________________________________________

network_connectivity_policies = {
  "dennis-ucs" = {
    description               = "dennis-ucs Network Connectivity Policy"
    enable_ipv6               = false
    organization              = "dennis_demo"
    update_domain             = ""
    dns_servers_v4 = [
      "208.67.220.220",
    ]
    tags = []
  }
}