#______________________________________________
#
# LAN Connectivity Policy Variables
#______________________________________________

lan_connectivity_policies = {
  "CEPH" = {
    description                 = ""
    enable_azure_stack_host_qos = false
    iqn_allocation_type         = "None"
    iqn_pool                    = ""
    iqn_static_identifier       = ""
    organization                = "UCS-DEMO2_CAGIP"
    vnic_placement_mode         = "custom"
    target_platform             = "FIAttached"
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
    vnics = {
      "ADMIN" = {
        cdn_source                      = "vnic"
        enable_failover                 = true
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_network_group_policy   = "VG-ADMIN-SRV"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "ADMIN"
        placement_pci_order             = 1
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "CEPH-BE" = {
        cdn_source                      = "vnic"
        enable_failover                 = true
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_network_group_policy   = "CEPH_CEPH-BE"
        ethernet_qos_policy             = "default_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "CEPH-BE"
        placement_pci_order             = 3
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "CEPH-FE" = {
        cdn_source                      = "vnic"
        enable_failover                 = true
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_network_group_policy   = "CEPH_CEPH-FE"
        ethernet_qos_policy             = "default_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "CEPH-FE"
        placement_pci_order             = 2
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
    }
  }
  "CPTE" = {
    description                 = ""
    enable_azure_stack_host_qos = false
    iqn_allocation_type         = "None"
    iqn_pool                    = ""
    iqn_static_identifier       = ""
    organization                = "UCS-DEMO2_CAGIP"
    vnic_placement_mode         = "custom"
    target_platform             = "FIAttached"
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
    vnics = {
      "ADMIN" = {
        cdn_source                      = "vnic"
        enable_failover                 = true
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_network_group_policy   = "VG-ADMIN-SRV"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "ADMIN"
        placement_pci_order             = 1
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "ADMIN-CLI-A" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "ADMIN-CLI-A"
        placement_pci_order             = 6
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "ADMIN-CLI-B" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "ADMIN-CLI-B"
        placement_pci_order             = 7
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "CEPH-FE" = {
        cdn_source                      = "vnic"
        enable_failover                 = true
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_network_group_policy   = "CPTE_CEPH-FE"
        ethernet_qos_policy             = "default_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "CEPH-FE"
        placement_pci_order             = 3
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "LAN-CACIB-A" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "LAN-CACIB-A"
        placement_pci_order             = 12
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "LAN-CACIB-B" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "LAN-CACIB-B"
        placement_pci_order             = 13
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "LAN-CAPS-A" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "LAN-CAPS-A"
        placement_pci_order             = 8
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "LAN-CAPS-B" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "LAN-CAPS-B"
        placement_pci_order             = 9
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "LAN-CATS-A" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "LAN-CATS-A"
        placement_pci_order             = 10
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "LAN-CATS-B" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "LAN-CATS-B"
        placement_pci_order             = 11
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "LAN-SILCA-A" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_network_group_policy   = "VG-SILCA"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "LAN-SILCA-A"
        placement_pci_order             = 4
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "LAN-SILCA-B" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_network_group_policy   = "VG-SILCA"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "LAN-SILCA-B"
        placement_pci_order             = 5
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "OS-PRIVATE" = {
        cdn_source                      = "vnic"
        enable_failover                 = true
        ethernet_adapter_policy         = "Linux"
        ethernet_network_control_policy = "default"
        ethernet_network_group_policy   = "CPTE_OS-PRIVATE"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-OSB3-DID"
        name                            = "OS-PRIVATE"
        placement_pci_order             = 2
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
    }
  }
}