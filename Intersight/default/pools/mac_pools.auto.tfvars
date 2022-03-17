#______________________________________________
#
# MAC Pool Variables
#______________________________________________

mac_pools = {
  "iac_A" = {
    assignment_order = "sequential"
    mac_blocks = {
      "1" = {
        from = "00:25:B5:0A:00:00"
        size = 1000
        # to   = "00:25:B5:0A:03:E7"
      },
    }
    tags = []
  }
  "iac_B" = {
    assignment_order = "sequential"
    mac_blocks = {
      "1" = {
        from = "00:25:B5:0B:00:00"
        size = 1000
        # to   = "00:25:B5:0B:03:E7"
      },
    }
    tags = []
  }
}