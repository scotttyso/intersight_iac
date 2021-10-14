#______________________________________________
#
# UCS Server Profile Template Variables
#______________________________________________

ucs_server_profile_templates = {
  "CEPH" = {
    bios_policy                   = "CEPH"
    boot_order_policy             = "LOCAL-PXE"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = ""
    ipmi_over_lan_policy          = "IPMI-OSB3-DID"
    lan_connectivity_policy       = "CEPH"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2_CAGIP"
    san_connectivity_policy       = ""
    sd_card_policy                = ""
    serial_over_lan_policy        = "SOL-ENABLE"
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
  "CPTE" = {
    bios_policy                   = "Virtu-M5"
    boot_order_policy             = "LOCAL-PXE"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = ""
    ipmi_over_lan_policy          = "IPMI-OSB3-DID"
    lan_connectivity_policy       = "CPTE"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2_CAGIP"
    san_connectivity_policy       = ""
    sd_card_policy                = ""
    serial_over_lan_policy        = "SOL-ENABLE"
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
  "MGMT" = {
    bios_policy                   = "Virtu-M5"
    boot_order_policy             = "LOCAL-PXE"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = ""
    ipmi_over_lan_policy          = "IPMI-OSB3-DID"
    lan_connectivity_policy       = "CPTE"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2_CAGIP"
    san_connectivity_policy       = ""
    sd_card_policy                = ""
    serial_over_lan_policy        = "SOL-ENABLE"
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