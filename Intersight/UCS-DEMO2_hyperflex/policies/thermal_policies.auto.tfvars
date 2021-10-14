#______________________________________________
#
# Thermal Policy Variables
#______________________________________________

thermal_policies = {
  "HyperFlex" = {
    description      = "Recommended-Power-control-policy-for-HyperFlex-servers"
    fan_control_mode = "Balanced"
    organization     = "UCS-DEMO2_hyperflex"
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