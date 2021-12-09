#______________________________________________
#
# UCS Server Profile Template Variables
#______________________________________________

ucs_server_profile_templates = {
  "VMware_M2" = {
    description     = "VMware_M2 Server Profile Template"
    organization    = "cx_demo"
    target_platform = ""
    #___________________________
    #
    # Compute Configuration
    #___________________________
    bios_policy          = "VMware"
    boot_order_policy    = "VMware_M2"
    virtual_media_policy = ""
    #___________________________
    #
    # Management Configuration
    #___________________________
    ipmi_over_lan_policy   = "cx_demo"
    local_user_policy      = "cx_demo"
    serial_over_lan_policy = "cx_demo"
    snmp_policy            = "cx_demo"
    syslog_policy          = "cx_demo"
    virtual_kvm_policy     = "cx_demo"
    #___________________________
    #
    # Storage Configuration
    #___________________________
    sd_card_policy = ""
    storage_policy = "M2_Raid"
    #___________________________
    #
    # Network Configuration
    #___________________________
    lan_connectivity_policy = "VMware_LAN"
    san_connectivity_policy = "VMware_SAN"
    tags                    = []
  }
}