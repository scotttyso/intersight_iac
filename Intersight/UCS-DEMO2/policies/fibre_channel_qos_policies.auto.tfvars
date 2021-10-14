#______________________________________________
#
# Fibre Channel QoS Policy Variables
#______________________________________________

fibre_channel_qos_policies = {
  "default" = {
    burst               = 10240
    description         = ""
    max_data_field_size = 2112
    organization        = "UCS-DEMO2"
    rate_limit          = 0
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