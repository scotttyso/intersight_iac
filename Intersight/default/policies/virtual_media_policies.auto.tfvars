#______________________________________________
#
# Virtual Media Policy Variables
#______________________________________________

virtual_media_policies = {
  "Asgard_vmedia" = {
    description                     = "Asgard_vmedia Virtual Media Policy"
    enable_low_power_usb            = true
    enable_virtual_media            = true
    enable_virtual_media_encryption = true
    organization                    = "default"
    tags                            = []
    virtual_media = {
      "Asgard_vmedia" = {
        device_type             = "cdd"
        file_location           = "http://jump1.rich.ciscolabs.com/esxi.iso"
        mount_options           = ""
        password                = 0
        protocol                = "https"
        username                = ""
      },
    }
  }
}