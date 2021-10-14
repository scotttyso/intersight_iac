#______________________________________________
#
# UCS Server Profile Template Variables
#______________________________________________

ucs_server_profile_templates = {
  "TEST123" = {
    bios_policy                   = ""
    boot_order_policy             = "default"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = ""
    local_user_policy             = ""
    organization                  = "UCS-DEMO2_Toto3_Toto33_Toto333"
    san_connectivity_policy       = ""
    sd_card_policy                = ""
    serial_over_lan_policy        = ""
    snmp_policy                   = ""
    storage_policy                = ""
    target_platform               = "FI-Attached"
    syslog_policy                 = ""
    virtual_kvm_policy            = "default"
    virtual_media_policy          = ""
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