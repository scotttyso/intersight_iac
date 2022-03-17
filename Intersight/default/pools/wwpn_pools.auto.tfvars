#______________________________________________
#
# WWPN Pool Variables
#______________________________________________

wwpn_pools = {
  "iac_A" = {
    assignment_order = "sequential"
    id_blocks = {
      "1" = {
        from = "20:00:00:25:B5:0A:00:00"
        size = 1000
        # to   = "20:00:00:25:B5:0A:03:E7"
      },
    }
    tags = []
  }
  "iac_B" = {
    assignment_order = "sequential"
    id_blocks = {
      "1" = {
        from = "20:00:00:25:B5:0B:00:00"
        size = 1000
        # to   = "20:00:00:25:B5:0B:03:E7"
      },
    }
    tags = []
  }
}