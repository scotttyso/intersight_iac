#______________________________________________
#
# SD Card Policy Variables
#______________________________________________

sd_card_policies = {
  "vSAN-RAW" = {
    description        = ""
    enable_os          = true
    organization       = "UCS-DEMO2"
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