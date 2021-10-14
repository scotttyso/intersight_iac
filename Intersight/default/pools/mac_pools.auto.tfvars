#______________________________________________
#
# MAC Pool Variables
#______________________________________________

mac_pools = {
  "Asgard_A" = {
    assignment_order = "sequential"
    mac_blocks       = [
      {
        from = "00:25:B5:0A:00:00"
        to = "00:25:B5:0A:02:00"
      },
    ]
    organization     = "default"
    tags             = []
  }
  "Asgard_B" = {
    assignment_order = "sequential"
    mac_blocks       = [
      {
        from = "00:25:B5:0B:00:00"
        to = "00:25:B5:0B:02:00"
      },
    ]
    organization     = "default"
    tags             = []
  }
}