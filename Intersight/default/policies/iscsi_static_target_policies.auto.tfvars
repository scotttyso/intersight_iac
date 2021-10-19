#______________________________________________
#
# iSCSI Static Target Policy Variables
#______________________________________________

iscsi_static_target_policies = {
  "Asgard_target" = {
    description  = "Asgard_target iSCSI Static Target Policy"
    ip_address   = "10.101.128.21"
    port         = 3260
    lun = [
      {
        bootable = true
        lun_id   = 0
      }
    ]
    organization = "default"
    target_name  = "iqn.1984-12.com.cisco:win-server1"
    tags         = []
  }
}