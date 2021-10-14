#______________________________________________
#
# LAN Connectivity Policy Variables
#______________________________________________

lan_connectivity_policies = {
  "iSCSI-Boot" = {
    description                 = ""
    enable_azure_stack_host_qos = false
    iqn_allocation_type         = "None"
    iqn_pool                    = ""
    iqn_static_identifier       = ""
    organization                = "UCS-DEMO2_FPV-FlexPod"
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
      "00-Infra-A" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMWare"
        ethernet_network_control_policy = "Enable-CDP-LLDP"
        ethernet_network_group_policy   = "iSCSI-Boot_00-Infra-A"
        ethernet_qos_policy             = "default_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-Pool-A"
        name                            = "00-Infra-A"
        placement_pci_order             = 6
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "01-Infra-B" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMWare"
        ethernet_network_control_policy = "Enable-CDP-LLDP"
        ethernet_network_group_policy   = "iSCSI-Boot_01-Infra-B"
        ethernet_qos_policy             = "default_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-Pool-B"
        name                            = "01-Infra-B"
        placement_pci_order             = 5
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "02-iSCSI-A" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMWare"
        ethernet_network_control_policy = "Enable-CDP-LLDP"
        ethernet_network_group_policy   = "iSCSI-Boot_02-iSCSI-A"
        ethernet_qos_policy             = "default_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-Pool-A"
        name                            = "02-iSCSI-A"
        placement_pci_order             = 4
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "03-iSCSI-B" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMWare"
        ethernet_network_control_policy = "Enable-CDP-LLDP"
        ethernet_network_group_policy   = "iSCSI-Boot_03-iSCSI-B"
        ethernet_qos_policy             = "default_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-Pool-B"
        name                            = "03-iSCSI-B"
        placement_pci_order             = 3
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "04-APIC-vDS-A" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMware-HighTrf"
        ethernet_network_control_policy = "Enable-CDP-LLDP"
        ethernet_network_group_policy   = "iSCSI-Boot_04-APIC-vDS-A"
        ethernet_qos_policy             = "default_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-Pool-A"
        name                            = "04-APIC-vDS-A"
        placement_pci_order             = 2
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "05-APIC-vDS-B" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMware-HighTrf"
        ethernet_network_control_policy = "Enable-CDP-LLDP"
        ethernet_network_group_policy   = "iSCSI-Boot_05-APIC-vDS-B"
        ethernet_qos_policy             = "default_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MAC-Pool-B"
        name                            = "05-APIC-vDS-B"
        placement_pci_order             = 1
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
    }
  }
}