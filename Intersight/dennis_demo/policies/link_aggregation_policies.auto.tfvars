#______________________________________________
#
# Link Aggregation Policy Variables
#______________________________________________

link_aggregation_policies = {
  "dennis-ucs" = {
    description        = "dennis-ucs Link Aggregation Policy"
    lacp_rate          = "normal"
    organization       = "dennis_demo"
    suspend_individual = false
    tags               = []
  }
}