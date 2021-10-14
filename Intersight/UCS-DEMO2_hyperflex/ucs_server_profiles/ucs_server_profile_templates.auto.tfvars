#______________________________________________
#
# UCS Server Profile Template Variables
#______________________________________________

ucs_server_profile_templates = {
  "compute-nodes" = {
    bios_policy                   = "HyperFlex"
    boot_order_policy             = "hx-compute"
    certificate_management_policy = ""
    description                   = "Service-Profile-Template-for-compute-servers"
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "HyperFlex"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2_hyperflex"
    san_connectivity_policy       = ""
    sd_card_policy                = ""
    serial_over_lan_policy        = "HyperFlex"
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
  "compute-nodes-m5" = {
    bios_policy                   = "HyperFlex-m5"
    boot_order_policy             = "hx-compute-m5"
    certificate_management_policy = ""
    description                   = "Service-Profile-Template-for-M5-compute-servers"
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "HyperFlex"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2_hyperflex"
    san_connectivity_policy       = ""
    sd_card_policy                = ""
    serial_over_lan_policy        = "HyperFlex"
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
  "hx-nodes" = {
    bios_policy                   = "HyperFlex"
    boot_order_policy             = "HyperFlex"
    certificate_management_policy = ""
    description                   = "Service-Profile-Template-for-HX-servers"
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "HyperFlex"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2_hyperflex"
    san_connectivity_policy       = ""
    sd_card_policy                = ""
    serial_over_lan_policy        = "HyperFlex"
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
  "hx-nodes-m5" = {
    bios_policy                   = "HyperFlex-m5"
    boot_order_policy             = "HyperFlex-m5"
    certificate_management_policy = ""
    description                   = "Service-Profile-Template-for-M5-HX-servers"
    imc_access_policy             = ""
    ipmi_over_lan_policy          = ""
    lan_connectivity_policy       = "HyperFlex"
    local_user_policy             = ""
    organization                  = "UCS-DEMO2_hyperflex"
    san_connectivity_policy       = ""
    sd_card_policy                = ""
    serial_over_lan_policy        = "HyperFlex"
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