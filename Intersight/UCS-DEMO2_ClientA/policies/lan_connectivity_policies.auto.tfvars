#______________________________________________
#
# LAN Connectivity Policy Variables
#______________________________________________

lan_connectivity_policies = {
  "ESX" = {
    description                 = ""
    enable_azure_stack_host_qos = false
    iqn_allocation_type         = "None"
    iqn_pool                    = ""
    iqn_static_identifier       = ""
    organization                = "UCS-DEMO2_ClientA"
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
      "vmdata1-gold" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMWare"
        ethernet_network_control_policy = "CDP-enable"
        ethernet_network_group_policy   = "ESX_vmdata1-gold"
        ethernet_qos_policy             = "5Gb-platinum"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "ESX"
        name                            = "vmdata1-gold"
        placement_pci_order             = 5
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "vmdata2-gold" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMWare"
        ethernet_network_control_policy = "CDP-enable"
        ethernet_network_group_policy   = "ESX_vmdata2-gold"
        ethernet_qos_policy             = "5Gb-platinum"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "ESX"
        name                            = "vmdata2-gold"
        placement_pci_order             = 6
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "vmdata3-bronze" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMWare"
        ethernet_network_control_policy = "CDP-enable"
        ethernet_network_group_policy   = "ESX_vmdata3-bronze"
        ethernet_qos_policy             = "1Gb-bronze"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "ESX"
        name                            = "vmdata3-bronze"
        placement_pci_order             = 7
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "vmdata4-bronze" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMWare"
        ethernet_network_control_policy = "CDP-enable"
        ethernet_network_group_policy   = "ESX_vmdata4-bronze"
        ethernet_qos_policy             = "1Gb-bronze"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "ESX"
        name                            = "vmdata4-bronze"
        placement_pci_order             = 8
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "vmkernel" = {
        cdn_source                      = "vnic"
        enable_failover                 = true
        ethernet_adapter_policy         = "VMWare"
        ethernet_network_control_policy = "CDP-enable"
        ethernet_qos_policy             = "100Mb"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "ESX"
        name                            = "vmkernel"
        placement_pci_order             = 3
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "Vmotion" = {
        cdn_source                      = "vnic"
        enable_failover                 = true
        ethernet_adapter_policy         = "VMWare"
        ethernet_network_control_policy = "CDP-enable"
        ethernet_network_group_policy   = "ESX_Vmotion"
        ethernet_qos_policy             = "5Gb-platinum_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "ESX"
        name                            = "Vmotion"
        placement_pci_order             = 1
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
    }
  }
  "test-easyucs-conversion_LCP" = {
    description                 = ""
    enable_azure_stack_host_qos = false
    iqn_allocation_type         = "None"
    iqn_pool                    = ""
    iqn_static_identifier       = ""
    organization                = "UCS-DEMO2_ClientA"
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
      "eth0" = {
        enable_failover                 = true
        ethernet_adapter_policy         = "VMWare"
        ethernet_network_control_policy = "CDP-LLDP-ENABLE"
        ethernet_network_group_policy   = "ADMIN"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "DEMO"
        name                            = "eth0"
        placement_pci_order             = 1
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "eth1" = {
        enable_failover                 = true
        ethernet_adapter_policy         = "VMWare"
        ethernet_network_control_policy = "default"
        ethernet_network_group_policy   = "test-easyucs-conversion_LCP_eth1"
        ethernet_qos_policy             = "5Gb-platinum"
        mac_address_allocation_type     = "STATIC"
        mac_address_static              = "12:34:56:78:90:AB"
        name                            = "eth1"
        placement_pci_order             = 2
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "eth3" = {
        enable_failover                 = false
        ethernet_adapter_policy         = "default"
        ethernet_network_control_policy = "default"
        ethernet_network_group_policy   = "test-easyucs-conversion_LCP_eth3"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "STATIC"
        mac_address_static              = "12:34:56:78:90:AB"
        name                            = "eth3"
        placement_pci_order             = 3
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "eth4" = {
        enable_failover                 = false
        ethernet_adapter_policy         = "default"
        ethernet_network_control_policy = "default"
        ethernet_network_group_policy   = "test-easyucs-conversion_LCP_eth4"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "ESX"
        name                            = "eth4"
        placement_pci_order             = 4
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "eth5" = {
        enable_failover                 = false
        ethernet_adapter_policy         = "default"
        ethernet_network_control_policy = "default"
        ethernet_network_group_policy   = "test-easyucs-conversion_LCP_eth5"
        ethernet_qos_policy             = "default_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "ESX"
        name                            = "eth5"
        placement_pci_order             = 5
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "eth6" = {
        enable_failover                 = true
        ethernet_adapter_policy         = "default"
        ethernet_network_control_policy = "default"
        ethernet_network_group_policy   = "test-easyucs-conversion_LCP_eth6"
        ethernet_qos_policy             = "default"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "ESX"
        name                            = "eth6"
        placement_pci_order             = 6
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
    }
  }
}