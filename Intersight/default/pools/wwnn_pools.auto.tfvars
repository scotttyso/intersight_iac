#______________________________________________
#
# WWNN Pool Variables
#______________________________________________

wwnn_pools = {
  "iac_wwnn_pool" = {
    assignment_order = "sequential"
    id_blocks = {
      "1" = {
        from = "20:00:00:25:B5:00:00:00"
        size = 1000
        # to   = "20:00:00:25:B5:00:03:E7"
      },
    }
    tags = []
  }
}