#______________________________________________
#
# IP Pool Variables
#______________________________________________

ip_pools = {
  "hx-ext-mgmt" = {
    ipv4_block       = [
      {
        from = "10.60.10.240",
        to = "10.60.10.243",
      },
    ]
    ipv4_config      = {
      config = {
        gateway = "10.60.10.254",
        netmask = "255.255.255.0",
      }
    }
    ipv6_block       = []
    ipv6_config      = {}
    organization     = "UCS-DEMO2_hyperflex"
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