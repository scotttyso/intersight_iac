#______________________________________________
#
# Link Aggregation Policy Variables
#______________________________________________

link_aggregation_policies = {
  "asgard-ucs_link_agg" = {
    description        = "asgard-ucs_link_agg Link Aggregation Policy"
    lacp_rate          = "normal"
    organization       = "Asgard"
    suspend_individual = false
    tags               = []
  }
}