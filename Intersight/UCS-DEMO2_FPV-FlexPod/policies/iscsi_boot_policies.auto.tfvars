#______________________________________________
#
# iSCSI Boot Policy Variables
#______________________________________________

iscsi_boot_policies = {
  "iSCSI-Boot-A_iSCSI-Boot-A" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iSCSI-IP-Pool-A"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = ""
    organization                     = "UCS-DEMO2_FPV-FlexPod"
    primary_target_policy            = "iSCSI-Boot-A_iSCSI-Boot-A_1"
    secondary_target_policy          = "iSCSI-Boot-A_iSCSI-Boot-A_2"
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
  "iSCSI-Boot-A_iSCSI-Boot-B" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iSCSI-IP-Pool-B"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = ""
    organization                     = "UCS-DEMO2_FPV-FlexPod"
    primary_target_policy            = "iSCSI-Boot-A_iSCSI-Boot-B_1"
    secondary_target_policy          = "iSCSI-Boot-A_iSCSI-Boot-B_2"
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
  "TEst_temp_iSCSI-Boot-A" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iscsi-initiator-pool"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = ""
    organization                     = "UCS-DEMO2_FPV-FlexPod"
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
  "TEst_temp_iSCSI-Boot-B" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iscsi-initiator-pool"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = ""
    organization                     = "UCS-DEMO2_FPV-FlexPod"
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
  "TestB_iSCSI-Boot-A" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iSCSI-IP-Pool-A"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = ""
    organization                     = "UCS-DEMO2_FPV-FlexPod"
    primary_target_policy            = "TestB_iSCSI-Boot-A_1"
    secondary_target_policy          = "TestB_iSCSI-Boot-A_2"
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
  "TestB_iSCSI-Boot-B" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iSCSI-IP-Pool-B"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = ""
    organization                     = "UCS-DEMO2_FPV-FlexPod"
    primary_target_policy            = "TestB_iSCSI-Boot-B_1"
    secondary_target_policy          = "TestB_iSCSI-Boot-B_2"
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
  "testIscsi_iSCSI-Boot-A" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iSCSI-IP-Pool-A"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = ""
    organization                     = "UCS-DEMO2_FPV-FlexPod"
    primary_target_policy            = "testIscsi_iSCSI-Boot-A_1"
    secondary_target_policy          = "testIscsi_iSCSI-Boot-A_2"
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
  "testIscsi_iSCSI-Boot-B" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iSCSI-IP-Pool-B"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = ""
    organization                     = "UCS-DEMO2_FPV-FlexPod"
    primary_target_policy            = "testIscsi_iSCSI-Boot-B_1"
    secondary_target_policy          = "testIscsi_iSCSI-Boot-B_2"
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
  "TUTU_iSCSI-Boot-A" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iscsi-initiator-pool"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = ""
    organization                     = "UCS-DEMO2_FPV-FlexPod"
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
  "TUTU_iSCSI-Boot-B" = {
    description                      = ""
    dhcp_vendor_id_iqn               = ""
    initiator_ip_pool                = "iscsi-initiator-pool"
    initiator_ip_source              = "Pool"
    initiator_static_ip_address      = ""
    iscsi_adapter_policy             = ""
    organization                     = "UCS-DEMO2_FPV-FlexPod"
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