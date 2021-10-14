#______________________________________________
#
# Thermal Policy Variables
#______________________________________________

thermal_policies = {
  "POWER-OSB3-DID" = {
    description      = ""
    fan_control_mode = "Balanced"
    organization     = "UCS-DEMO2_CAGIP"
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