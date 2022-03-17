#______________________________________________
#
# Virtual Media Policy Variables
#______________________________________________

virtual_media_policies = {
  "iac-standalone_vmedia" = {
    description                     = "iac-standalone_vmedia Virtual Media Policy"
    enable_low_power_usb            = true
    enable_virtual_media            = true
    enable_virtual_media_encryption = false
    tags                            = []
    virtual_media = {
      "iac-standalone_vmedia" = {
        device_type   = "nfs"
        file_location = "192.168.1.5"
        mount_options = ""
        password      = 0
        protocol      = "nfs"
        username      = ""
      },
    }
  }
}