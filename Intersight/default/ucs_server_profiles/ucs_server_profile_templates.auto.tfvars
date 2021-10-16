#______________________________________________
#
# UCS Server Profile Template Variables
#______________________________________________

ucs_server_profile_templates = {
  "Asgard_template" = {
    description     = "Asgard_template UCS Server Profile Template"
    organization    = "default"
    target_platform = "FIAttached"
    #___________________________
    #
    # Compute Configuration
    #___________________________
    bios_policy                = "Asgard_Virtualization"
    boot_order_policy          = ""
    power_policy               = "Asgard_Server"
    virtual_media_policy       = "Asgard_vmedia"
    #___________________________
    #
    # Management Configuration
    #___________________________
    certificate_management_policy = ""
    imc_access_policy             = "Asgard_imc_access"
    ipmi_over_lan_policy          = "Asgard_ipmi"
    local_user_policy             = "Asgard_local_users"
    serial_over_lan_policy        = "Asgard_sol"
    snmp_policy                   = "Asgard_snmp"
    syslog_policy                 = "Asgard_syslog_domain"
    virtual_kvm_policy            = "Asgard_vkvm"
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
    lan_connectivity_policy      = ""
    san_connectivity_policy      = "Asgard_san"
    tags = []
  }
}