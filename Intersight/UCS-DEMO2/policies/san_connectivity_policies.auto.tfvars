#______________________________________________
#
# SAN Connectivity Policy Variables
#______________________________________________

san_connectivity_policies = {
  "ESXi-OCB" = {
    description          = ""
    organization         = "UCS-DEMO2"
    target_platform             = "FIAttached"
    vhba_placement_mode  = "auto"
    wwnn_allocation_type = "POOL"
    wwnn_static_address  = ""
    wwnn_pool            = "NN-ESXi-OCB"
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
      "SAN-A" = {
        fibre_channel_adapter_policy = "VMWare"
        fibre_channel_network_policy = "ESXi-OCB_SAN-A"
        fibre_channel_qos_policy     = "default"
        name                         = "SAN-A"
        placement_pci_order          = 2
        placement_slot_id            = "MLOM"
        placement_switch_id          = "A"
        wwpn_allocation_type         = "POOL"
        wwpn_pool                    = "PN-ESXi-OCB-A"
      },
      "SAN-B" = {
        fibre_channel_adapter_policy = "VMWare"
        fibre_channel_network_policy = "ESXi-OCB_SAN-B"
        fibre_channel_qos_policy     = "default"
        name                         = "SAN-B"
        placement_pci_order          = 4
        placement_slot_id            = "MLOM"
        placement_switch_id          = "B"
        wwpn_allocation_type         = "POOL"
        wwpn_pool                    = "PN-ESXi-OCB-B"
      },
    }
  }
  "TEST-PLACEMENT-TEMPLATE_SCP" = {
    description          = ""
    organization         = "UCS-DEMO2"
    target_platform             = "FIAttached"
    vhba_placement_mode  = "auto"
    wwnn_allocation_type = "POOL"
    wwnn_static_address  = ""
    wwnn_pool            = "DEMO"
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
      "vhba0" = {
        fibre_channel_adapter_policy = "VMWare"
        fibre_channel_network_policy = "TEST-PLACEMENT-TEMPLATE_SCP_vhba0"
        fibre_channel_qos_policy     = "default"
        name                         = "vhba0"
        placement_pci_order          = 1
        placement_slot_id            = "MLOM"
        placement_switch_id          = "A"
        wwpn_allocation_type         = "POOL"
        wwpn_pool                    = "DEMO-SAN-A"
      },
    }
  }
}