#______________________________________________
#
# Virtual Media Policy Variables
#______________________________________________

virtual_media_policies = {
  "ESXI7.0" = {
    description                     = ""
    enable_low_power_usb            = false
    enable_virtual_media_encryption = false
    organization                    = "UCS-DEMO2"
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
    vmedia_mounts = [
      {
        device_type             = "cdd",
        hostname                = "192.168.20.13",
        name                    = "ESXI7.0",
        protocol                = "http",
        remote_file             = "customesxi.iso",
        remote_path             = "/",
        username                = "root"
      },
    ]
  }
  "test_writeable" = {
    description                     = ""
    enable_low_power_usb            = false
    enable_virtual_media_encryption = false
    organization                    = "UCS-DEMO2"
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