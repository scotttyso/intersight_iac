#______________________________________________
#
# Link Aggregation Policy Variables
#______________________________________________

link_aggregation_policies = {
  "UCS-DEMO2" = {
    description        = ""
    lacp_rate          = "normal"
    organization       = "UCS-DEMO2"
    suspend_individual = false
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
  "lacp_pol" = {
    description        = ""
    lacp_rate          = "fast"
    organization       = "UCS-DEMO2"
    suspend_individual = true
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
}