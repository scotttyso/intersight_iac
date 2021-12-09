#______________________________________________
#
# WWPN Pool Variables
#______________________________________________

wwpn_pools = {
  "VMware-A" = {
    assignment_order = "sequential"
    id_blocks = {
      "1" = {
        from = "20:00:00:25:B5:A5:A0:00"
        size = 1000
        # to   = "20:00:00:25:B5:A5:A3:E7"
      },
    }
    organization = "cx_demo"
    pool_purpose = "WWPN"
    tags         = []
  }
  "VMware-B" = {
    assignment_order = "sequential"
    id_blocks = {
      "1" = {
        from = "20:00:00:25:B5:A5:B0:00"
        size = 1000
        # to   = "20:00:00:25:B5:A5:B3:E7"
      },
    }
    organization = "cx_demo"
    pool_purpose = "WWPN"
    tags         = []
  }
}