#______________________________________________
#
# iSCSI Boot Policy Variables
#______________________________________________

iscsi_boot_policies = {
  "esxi3_ISCSI-BOOT-A" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iscsi-initiator-pool"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = "default"
    organization                     = "UCS-DEMO2"
    primary_target_policy            = ""
    secondary_target_policy          = ""
    target_source_type               = "Static"
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
  "esxi3_ISCSI-BOOT-B" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iscsi-initiator-pool"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = "default"
    organization                     = "UCS-DEMO2"
    primary_target_policy            = ""
    secondary_target_policy          = ""
    target_source_type               = "Static"
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
  "ESXI-ISCSI-AUTO_ISCSI-BOOT-A" = {
    description                      = ""
    dhcp_vendor_id_iqn               = "CISCO_IBOOT"
    initiator_ip_pool                = ""
    initiator_ip_source              = "DHCP"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = "default"
    organization                     = "UCS-DEMO2"
    primary_target_policy            = ""
    secondary_target_policy          = ""
    target_source_type               = "Auto"
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
  "ESXI-ISCSI-AUTO_ISCSI-BOOT-B" = {
    description                      = ""
    dhcp_vendor_id_iqn               = "CISCO_IBOOT"
    initiator_ip_pool                = ""
    initiator_ip_source              = "DHCP"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = "default"
    organization                     = "UCS-DEMO2"
    primary_target_policy            = ""
    secondary_target_policy          = ""
    target_source_type               = "Auto"
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
  "ESXI-OCB-POC_ISCSI-BOOT-A" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iscsi-initiator-pool"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = "default"
    organization                     = "UCS-DEMO2"
    primary_target_policy            = "ESXI-OCB-POC_ISCSI-BOOT-A_1"
    secondary_target_policy          = ""
    target_source_type               = "Static"
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
  "ESXI-OCB-POC_ISCSI-BOOT-B" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iscsi-initiator-pool"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = "default"
    organization                     = "UCS-DEMO2"
    primary_target_policy            = "ESXI-OCB-POC_ISCSI-BOOT-B_1"
    secondary_target_policy          = ""
    target_source_type               = "Static"
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
  "ESXI-VCF-WLD_ETH2-BOOT-iSCSI" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iscsi-initiator-pool"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = "default"
    organization                     = "UCS-DEMO2"
    primary_target_policy            = "ESXI-VCF-WLD_ETH2-BOOT-iSCSI_1"
    secondary_target_policy          = ""
    target_source_type               = "Static"
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
  "ESXI-VCF-WLD_ETH3-BOOT-iSCSI" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iscsi-initiator-pool"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = "default"
    organization                     = "UCS-DEMO2"
    primary_target_policy            = "ESXI-VCF-WLD_ETH3-BOOT-iSCSI_1"
    secondary_target_policy          = ""
    target_source_type               = "Static"
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
  "testinroot_vnicIscsi" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iscsi-initiator-pool"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = "default"
    organization                     = "UCS-DEMO2"
    primary_target_policy            = ""
    secondary_target_policy          = ""
    target_source_type               = "Static"
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