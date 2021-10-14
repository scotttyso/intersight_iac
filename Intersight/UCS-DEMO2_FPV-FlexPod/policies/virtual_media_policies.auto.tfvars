#______________________________________________
#
# Virtual Media Policy Variables
#______________________________________________

virtual_media_policies = {
  "KLK" = {
    description                     = ""
    enable_low_power_usb            = false
    enable_virtual_media_encryption = false
    organization                    = "UCS-DEMO2_FPV-FlexPod"
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
    vmedia_mounts                   = []
  }
}