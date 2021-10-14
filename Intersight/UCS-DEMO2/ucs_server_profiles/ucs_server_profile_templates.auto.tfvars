#______________________________________________
#
# UCS Server Profile Template Variables
#______________________________________________

ucs_server_profile_templates = {
  "ESXI-ISCSI-AUTO" = {
    bios_policy                   = ""
    boot_order_policy             = "ISCSI"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = "ADMIN_inband"
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "ISCSI-BOOT-2"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2"
    san_connectivity_policy       = ""
    sd_card_policy                = ""
    serial_over_lan_policy        = ""
    snmp_policy                   = ""
    storage_policy                = ""
    target_platform               = "FI-Attached"
    syslog_policy                 = ""
    virtual_kvm_policy            = "default"
    virtual_media_policy          = "ESXI7.0"
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
  "ESXI-OCB-POC" = {
    bios_policy                   = ""
    boot_order_policy             = "ISCSI"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "ISCSI-BOOT"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2"
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
  "ESXI-VCF-MGMT" = {
    bios_policy                   = ""
    boot_order_policy             = "SDCard"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "ESXI-VCF-MGMT_LCP"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2"
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
  "ESXI-VCF-WLD" = {
    bios_policy                   = ""
    boot_order_policy             = "VCF-iSCSI"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "ESXI-VCF-WLD_LCP"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2"
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
  "ESXI-VCF-WLD-FC" = {
    bios_policy                   = ""
    boot_order_policy             = "FC"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "ESXI-VCF-WLD-FC_LCP"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2"
    san_connectivity_policy       = "ESXi-OCB"
    sd_card_policy                = ""
    serial_over_lan_policy        = ""
    snmp_policy                   = ""
    storage_policy                = ""
    target_platform               = "FI-Attached"
    syslog_policy                 = ""
    virtual_kvm_policy            = "default"
    virtual_media_policy          = "ESXI7.0"
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
  "TEST-PLACEMENT-TEMPLATE" = {
    bios_policy                   = ""
    boot_order_policy             = "default"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "TEST-PLACEMENT-TEMPLATE_LCP"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2"
    san_connectivity_policy       = "TEST-PLACEMENT-TEMPLATE_SCP"
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
  "testinroot" = {
    bios_policy                   = ""
    boot_order_policy             = "testIscsi"
    certificate_management_policy = ""
    description                   = ""
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "Toto"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2"
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