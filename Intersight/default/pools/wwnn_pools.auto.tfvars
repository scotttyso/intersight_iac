#______________________________________________
#
# WWNN Pool Variables
#______________________________________________

wwnn_pools = {
  "Asgard_wwnn_pool" = {
    assignment_order = "sequential"
    id_blocks        = [
      {
        from = "20:00:00:25:B5:00:00:00",
        to = "20:00:00:25:B5:00:02:00",
      },
    ]
    organization     = "default"
    pool_purpose     = "WWNN"
    tags             = []
  }
}