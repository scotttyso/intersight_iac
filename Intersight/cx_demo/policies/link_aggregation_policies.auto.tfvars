#______________________________________________
#
# Link Aggregation Policy Variables
#______________________________________________

link_aggregation_policies = {
  "asgard-ucs" = {
    description        = "asgard-ucs Link Aggregation Policy"
    lacp_rate          = "normal"
    organization       = "cx_demo"
    suspend_individual = false
    tags               = []
  }
}