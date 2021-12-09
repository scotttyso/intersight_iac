#______________________________________________
#
# Network Connectivity Policy Variables
#______________________________________________

network_connectivity_policies = {
  "asgard-ucs" = {
    description   = "asgard-ucs Network Connectivity Policy"
    enable_ipv6   = false
    organization  = "cx_demo"
    update_domain = ""
    dns_servers_v4 = [
      "208.67.220.220",
    ]
    tags = []
  }
}