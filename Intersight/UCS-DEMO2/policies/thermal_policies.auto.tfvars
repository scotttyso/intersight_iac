#______________________________________________
#
# Thermal Policy Variables
#______________________________________________

thermal_policies = {
  "default" = {
    description      = ""
    fan_control_mode = "Balanced"
    organization     = "UCS-DEMO2"
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
  "No-Power-Cap" = {
    description      = ""
    fan_control_mode = "Balanced"
    organization     = "UCS-DEMO2"
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