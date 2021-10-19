#______________________________________________
#
# iSCSI Boot Policy Variables
#______________________________________________

iscsi_boot_policies = {
  "Asgard_boot" = {
    description         = "Asgard_boot iSCSI Boot Policy"
    initiator_ip_pool   = ""
    initiator_ip_source = "Static"
    initiator_static_ip_v4_config = {
      subnet_mask     = "255.255.255.0"
      default_gateway = "198.18.1.1"
      ip_address      = ""
      primary_dns     = "198.18.1.15"
      secondary_dns   = ""
    }
    iscsi_adapter_policy    = "Asgard_adapter"
    organization            = "default"
    primary_target_policy   = "Asgard_target"
    secondary_target_policy = "Asgard_target"
    target_source_type      = "Static"
    tags                    = []
  }
}