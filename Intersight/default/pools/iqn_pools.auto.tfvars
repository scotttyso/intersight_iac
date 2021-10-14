#______________________________________________
#
# IQN Pool Variables
#______________________________________________

iqn_pools = {
  "Asgard_iqn_pool" = {
    assignment_order = "sequential"
    organization     = "default"
    prefix           = "iqn.1984-12.com.cisco"
    iqn_blocks = [
      {
        from = "1",
        size = "512",
        suffix = "ucs-host",
      },
    ]
    tags             = []
  }
}