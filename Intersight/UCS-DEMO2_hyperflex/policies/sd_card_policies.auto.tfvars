#______________________________________________
#
# SD Card Policy Variables
#______________________________________________

sd_card_policies = {
  "hx-compute" = {
    description        = "Recommended-Local-Disk-policy-for-HyperFlex-compute-servers"
    enable_os          = true
    organization       = "UCS-DEMO2_hyperflex"
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
  "hx-compute-m5" = {
    description        = "Recommended-Local-Disk-policy-for-M5-Compute-servers"
    enable_os          = true
    organization       = "UCS-DEMO2_hyperflex"
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
  "HyperFlex" = {
    description        = "Recommended-Local-Disk-policy-for-HyperFlex-servers"
    enable_os          = true
    organization       = "UCS-DEMO2_hyperflex"
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