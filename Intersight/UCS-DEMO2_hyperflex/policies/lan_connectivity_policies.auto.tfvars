#______________________________________________
#
# LAN Connectivity Policy Variables
#______________________________________________

lan_connectivity_policies = {
  "HyperFlex" = {
    description                 = "Recommended-LAN-connectivity-policy-for-HyperFlex-servers"
    enable_azure_stack_host_qos = false
    iqn_allocation_type         = "None"
    iqn_pool                    = ""
    iqn_static_identifier       = ""
    organization                = "UCS-DEMO2_hyperflex"
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
      "hv-mgmt-a" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "HyperFlex"
        ethernet_network_control_policy = "HyperFlex-infra"
        ethernet_network_group_policy   = "HyperFlex_hv-mgmt-a"
        ethernet_qos_policy             = "silver"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "hv-mgmt-a"
        name                            = "hv-mgmt-a"
        placement_pci_order             = 1
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "hv-mgmt-b" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "HyperFlex"
        ethernet_network_control_policy = "HyperFlex-infra"
        ethernet_network_group_policy   = "HyperFlex_hv-mgmt-b"
        ethernet_qos_policy             = "silver"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "hv-mgmt-b"
        name                            = "hv-mgmt-b"
        placement_pci_order             = 2
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "hv-vmotion-a" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "HyperFlex"
        ethernet_network_control_policy = "HyperFlex-infra"
        ethernet_network_group_policy   = "HyperFlex_hv-vmotion-a"
        ethernet_qos_policy             = "bronze_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "hv-vmotion-a"
        name                            = "hv-vmotion-a"
        placement_pci_order             = 7
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "hv-vmotion-b" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "HyperFlex"
        ethernet_network_control_policy = "HyperFlex-infra"
        ethernet_network_group_policy   = "HyperFlex_hv-vmotion-b"
        ethernet_qos_policy             = "bronze_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "hv-vmotion-b"
        name                            = "hv-vmotion-b"
        placement_pci_order             = 8
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "storage-data-a" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "HyperFlex"
        ethernet_network_control_policy = "HyperFlex-infra"
        ethernet_network_group_policy   = "HyperFlex_storage-data-a"
        ethernet_qos_policy             = "platinum_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "storage-data-a"
        name                            = "storage-data-a"
        placement_pci_order             = 3
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "storage-data-b" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "HyperFlex"
        ethernet_network_control_policy = "HyperFlex-infra"
        ethernet_network_group_policy   = "HyperFlex_storage-data-b"
        ethernet_qos_policy             = "platinum_mtu9000"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "storage-data-b"
        name                            = "storage-data-b"
        placement_pci_order             = 4
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
      "vm-network-a" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "HyperFlex"
        ethernet_network_control_policy = "HyperFlex-vm"
        ethernet_network_group_policy   = "HyperFlex_vm-network-a"
        ethernet_qos_policy             = "gold"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "vm-network-a"
        name                            = "vm-network-a"
        placement_pci_order             = 5
        placement_slot_id               = "MLOM"
        placement_switch_id             = "A"
      },
      "vm-network-b" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "HyperFlex"
        ethernet_network_control_policy = "HyperFlex-vm"
        ethernet_network_group_policy   = "HyperFlex_vm-network-b"
        ethernet_qos_policy             = "gold"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "vm-network-b"
        name                            = "vm-network-b"
        placement_pci_order             = 6
        placement_slot_id               = "MLOM"
        placement_switch_id             = "B"
      },
    }
  }
}