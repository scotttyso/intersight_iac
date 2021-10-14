#______________________________________________
#
# Virtual KVM Policy Variables
#______________________________________________

virtual_kvm_policies = {
  "default" = {
    description               = ""
    enable_local_server_video = true
    enable_video_encryption   = false
    enable_virtual_kvm        = true
    maximum_sessions          = 4
    organization              = "UCS-DEMO2_hyperflex"
    remote_port               = 2068
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