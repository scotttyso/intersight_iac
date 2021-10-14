#______________________________________________
#
# Flow Control Policy Variables
#______________________________________________

flow_control_policies = {
  "UCS-DEMO2" = {
    description  = ""
    organization = "UCS-DEMO2"
    priority     = "auto"
    receive      = "Disabled"
    send         = "Disabled"
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
  "flow_ctrl" = {
    description  = ""
    organization = "UCS-DEMO2"
    priority     = "auto"
    receive      = "Enabled"
    send         = "Enabled"
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
  "flow_ctrl2" = {
    description  = ""
    organization = "UCS-DEMO2"
    priority     = "on"
    receive      = "Disabled"
    send         = "Disabled"
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