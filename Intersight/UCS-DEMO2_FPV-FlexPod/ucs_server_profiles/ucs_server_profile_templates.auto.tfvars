#______________________________________________
#
# UCS Server Profile Template Variables
#______________________________________________

ucs_server_profile_templates = {
  "iSCSI-Boot-A" = {
    bios_policy                   = "Virtual-Host"
    boot_order_policy             = "iSCSI-Boot"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "iSCSI-Boot"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2_FPV-FlexPod"
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
  "TestB" = {
    bios_policy                   = "Virtual-Host"
    boot_order_policy             = "iSCSI-Boot"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "iSCSI-Boot"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2_FPV-FlexPod"
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
  "testIscsi" = {
    bios_policy                   = "Virtual-Host"
    boot_order_policy             = "iSCSI-Boot"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "iSCSI-Boot"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2_FPV-FlexPod"
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