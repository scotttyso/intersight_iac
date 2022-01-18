#______________________________________________
#
# Link Aggregation Policy Variables
#______________________________________________

link_aggregation_policies = {
  "demo-ucs" = {
    description        = "demo-ucs Link Aggregation Policy"
    lacp_rate          = "normal"
    organization       = "default"
    suspend_individual = false
    tags               = []
  }
}