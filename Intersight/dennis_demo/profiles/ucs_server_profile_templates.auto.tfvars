#______________________________________________
#
# UCS Server Profile Template Variables
#______________________________________________

ucs_server_profile_templates = {
  "VMware_M2_pxe" = {
    description     = "VMware_M2_pxe Server Profile Template"
    organization    = "dennis_demo"
    target_platform = "FIAttached"
    #___________________________
    #
    # Compute Configuration
    #___________________________
    bios_policy              = "VMware"
    boot_order_policy        = "VMware_M2_pxe"
    uuid_pool                = "VMware"
    power_policy             = "Server"
    virtual_media_policy     = ""
    #___________________________
    #
    # Management Configuration
    #___________________________
    certificate_management_policy = ""
    imc_access_policy             = "dennis_demo"
    ipmi_over_lan_policy          = "dennis_demo"
    local_user_policy             = "dennis_demo"
    serial_over_lan_policy        = "dennis_demo"
    snmp_policy                   = "dennis_demo"
    syslog_policy                 = "dennis_demo"
    virtual_kvm_policy            = "dennis_demo"
    #___________________________
    #
    # Storage Configuration
    #___________________________
    sd_card_policy = ""
    storage_policy = ""
    #___________________________
    #
    # Network Configuration
    #___________________________
    lan_connectivity_policy      = "VMware_LAN"
    san_connectivity_policy      = "VMware_SAN"
    tags = []
  }
}