#______________________________________________
#
# UUID Pool Variables
#______________________________________________

uuid_pools = {
  "VMware" = {
    assignment_order = "sequential"
    prefix           = "000025B5-0000-0000"
    uuid_blocks = {
      "1" = {
        from = "0000-000000000000"
        size = 1000
        # to   = "0000-0000000003E7"
      },
    }
    organization = "default"
    tags         = []
  }
}