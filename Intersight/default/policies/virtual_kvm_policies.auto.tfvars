#______________________________________________
#
# Virtual KVM Policy Variables
#______________________________________________

virtual_kvm_policies = {
  "Asgard_vkvm" = {
    description               = "Asgard_vkvm Virtual KVM Policy"
    enable_local_server_video = true
    enable_video_encryption   = true
    enable_virtual_kvm        = true
    maximum_sessions          = 4
    organization              = "default"
    remote_port               = 2068
    tags                      = []
  }
}