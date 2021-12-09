#______________________________________________
#
# LAN Connectivity Policy Variables
#______________________________________________

lan_connectivity_policies = {
  "VMware_LAN" = {
    description                 = "VMware_LAN LAN Connectivity Policy"
    enable_azure_stack_host_qos = false
    iqn_allocation_type         = "None"
    organization                = "cx_demo"
    vnic_placement_mode         = "custom"
    target_platform             = "FIAttached"
    tags                        = []
    vnics = {
      "MGMT-A" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMware"
        ethernet_network_control_policy = "LLDP"
        ethernet_network_group_policy   = "MGMT"
        ethernet_qos_policy             = "Silver"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MGMT-A"
        name                            = "MGMT-A"
      },
      "MGMT-B" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMware"
        ethernet_network_control_policy = "LLDP"
        ethernet_network_group_policy   = "MGMT"
        ethernet_qos_policy             = "Silver"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "MGMT-B"
        name                            = "MGMT-B"
      },
      "VMOTION-A" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMware"
        ethernet_network_control_policy = "LLDP"
        ethernet_network_group_policy   = "VMOTION"
        ethernet_qos_policy             = "Bronze"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "VMOTION-A"
        name                            = "VMOTION-A"
      },
      "VMOTION-B" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMware"
        ethernet_network_control_policy = "LLDP"
        ethernet_network_group_policy   = "VMOTION"
        ethernet_qos_policy             = "Bronze"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "VMOTION-B"
        name                            = "VMOTION-B"
      },
      "STORAGE-A" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMware"
        ethernet_network_control_policy = "LLDP"
        ethernet_network_group_policy   = "STORAGE"
        ethernet_qos_policy             = "Platinum"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "STORAGE-A"
        name                            = "STORAGE-A"
      },
      "STORAGE-B" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMware"
        ethernet_network_control_policy = "LLDP"
        ethernet_network_group_policy   = "STORAGE"
        ethernet_qos_policy             = "Platinum"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "STORAGE-B"
        name                            = "STORAGE-B"
      },
      "DATA-A" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMware"
        ethernet_network_control_policy = "LLDP"
        ethernet_network_group_policy   = "DATA"
        ethernet_qos_policy             = "Gold"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "DATA-A"
        name                            = "DATA-A"
      },
      "DATA-B" = {
        cdn_source                      = "vnic"
        enable_failover                 = false
        ethernet_adapter_policy         = "VMware"
        ethernet_network_control_policy = "LLDP"
        ethernet_network_group_policy   = "DATA"
        ethernet_qos_policy             = "Gold"
        mac_address_allocation_type     = "POOL"
        mac_address_pool                = "DATA-B"
        name                            = "DATA-B"
      },
    }
  }
}