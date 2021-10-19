#______________________________________________
#
# iSCSI Adapter Policy Variables
#______________________________________________

iscsi_adapter_policies = {
  "Asgard_adapter" = {
    description            = "Asgard_adapter iSCSI Adapter Policy"
    dhcp_timeout           = 60
    lun_busy_retry_count   = 15
    organization           = "default"
    tcp_connection_timeout = 15
    tags                   = []
  }
}