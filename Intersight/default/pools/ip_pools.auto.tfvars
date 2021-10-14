#______________________________________________
#
# IP Pool Variables
#______________________________________________

ip_pools = {
  "Asgard_ip_pool" = {
    assignment_order = "sequential"
    ipv4_block       = [
      {
        from = "198.18.0.10",
        to = "198.18.0.170",
      },
    ]
    ipv4_config      = {
      config = {
        gateway = "198.18.0.1",
        netmask = "255.255.255.0",
        primary_dns = "208.67.220.220",
        secondary_dns = "208.67.222.222",
      }
    }
    ipv6_block       = [
      {
        from = "2001:0002::10",
        size = "160",
      },
    ]
    ipv6_config      = {
      config = {
        gateway = "2001:2::1",
        prefix = "64",
        primary_dns = "2620:119:35::35",
        secondary_dns = "2620:119:53::53",
      }
    }
    organization     = "default"
    tags             = []
  }
}