#______________________________________________
#
# Network Connectivity (DNS) Policy Variables
#______________________________________________

network_connectivity_policies = {
  "UCS-DEMO2" = {
    description               = ""
    enable_ipv6               = true
    organization              = "UCS-DEMO2"
    update_domain             = ""
    dns_servers_v4 = [
      "1.2.3.4",
      "144.254.71.184"
    ]
    dns_servers_v6 = [
      "2001:420:44f0::1",
      "::"
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