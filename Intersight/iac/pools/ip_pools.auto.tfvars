#______________________________________________
#
# IP Pool Variables
#______________________________________________

ip_pools = {
  "VMware_KVM" = {
    assignment_order = "sequential"
    ipv4_blocks = {
      "1" = {
        from = "198.18.0.10"
        size = 245
        # to   = "198.18.0.254"
      },
    }
    ipv4_config = {
      config = {
        gateway       = "198.18.0.1"
        netmask       = "255.255.255.0"
        primary_dns   = "208.67.220.220"
        secondary_dns = ""
      }
    }
    ipv6_blocks  = {}
    ipv6_configs = {}
    tags         = []
  }
}