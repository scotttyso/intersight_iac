#______________________________________________
#
# Virtual KVM Policy Variables
#______________________________________________

virtual_kvm_policies = {
  "dennis_demo" = {
    description               = "dennis_demo Virtual KVM Policy"
    enable_local_server_video = true
    enable_video_encryption   = true
    enable_virtual_kvm        = true
    maximum_sessions          = 4
    organization              = "dennis_demo"
    remote_port               = 2068
    tags                      = []
  }
}