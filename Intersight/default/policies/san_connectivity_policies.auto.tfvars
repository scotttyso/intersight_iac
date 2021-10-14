#______________________________________________
#
# SAN Connectivity Policy Variables
#______________________________________________

san_connectivity_policies = {
  "Asgard_san" = {
    description          = "Asgard_san SAN Connectivity Policy"
    organization         = "default"
    target_platform             = "FIAttached"
    vhba_placement_mode  = "custom"
    wwnn_allocation_type = "POOL"
    wwnn_static_address  = ""
    wwnn_pool            = "Asgard_wwnn_pool"
    tags                 = []
    vhbas = {
      "HBA-A" = {
        fibre_channel_adapter_policy = "Asgard_VMWare"
        fibre_channel_network_policy = "Asgard_A"
        fibre_channel_qos_policy     = "Asgard_qos"
        name                         = "HBA-A"
        persistent_lun_bindings      = "True"
        placement_pci_link           = 0
        placement_pci_order          = 8
        placement_slot_id            = "MLOM"
        placement_switch_id          = "A"
        vhba_type                    = "fc-initiator"
        wwpn_allocation_type         = "POOL"
        wwpn_pool                    = "Asgard_A"
        wwpn_static_address          = ""
      },
      "HBA-B" = {
        fibre_channel_adapter_policy = "Asgard_VMWare"
        fibre_channel_network_policy = "Asgard_B"
        fibre_channel_qos_policy     = "Asgard_qos"
        name                         = "HBA-B"
        persistent_lun_bindings      = "True"
        placement_pci_link           = 0
        placement_pci_order          = 9
        placement_slot_id            = "MLOM"
        placement_switch_id          = "B"
        vhba_type                    = "fc-initiator"
        wwpn_allocation_type         = "POOL"
        wwpn_pool                    = "Asgard_B"
        wwpn_static_address          = ""
      },
    }
  }
}