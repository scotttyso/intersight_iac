#______________________________________________
#
# SAN Connectivity Policy Variables
#______________________________________________

san_connectivity_policies = {
  "ESX" = {
    description          = ""
    organization         = "UCS-DEMO2_ClientA"
    target_platform             = "FIAttached"
    vhba_placement_mode  = "auto"
    wwnn_allocation_type = "POOL"
    wwnn_static_address  = ""
    wwnn_pool            = "ESX"
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
    vhbas = {
      "vfc0" = {
        fibre_channel_adapter_policy = "VMWare"
        fibre_channel_network_policy = "ESX_vfc0"
        fibre_channel_qos_policy     = "default"
        name                         = "vfc0"
        placement_pci_order          = 2
        placement_slot_id            = "MLOM"
        placement_switch_id          = "A"
        wwpn_allocation_type         = "POOL"
        wwpn_pool                    = "ESX-WWPN"
      },
      "vfc1" = {
        fibre_channel_adapter_policy = "VMWare"
        fibre_channel_network_policy = "ESX_vfc1"
        fibre_channel_qos_policy     = "default"
        name                         = "vfc1"
        placement_pci_order          = 4
        placement_slot_id            = "MLOM"
        placement_switch_id          = "B"
        wwpn_allocation_type         = "POOL"
        wwpn_pool                    = "ESX-WWPN"
      },
    }
  }
}