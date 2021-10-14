#______________________________________________
#
# Network Connectivity Policy Variables
#______________________________________________

network_connectivity_policies = {
  "Asgard_dns" = {
    description               = "Asgard_dns Network Connectivity Policy"
    enable_ipv6               = false
    organization              = "Asgard"
    update_domain             = ""
    dns_servers_v4 = [
      "208.67.220.220",
      "10.101.128.16"
    ]
    tags = []
  }
}