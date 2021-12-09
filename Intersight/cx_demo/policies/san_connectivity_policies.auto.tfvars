#______________________________________________
#
# SAN Connectivity Policy Variables
#______________________________________________

san_connectivity_policies = {
  "VMware_SAN" = {
    description          = "VMware_SAN SAN Connectivity Policy"
    organization         = "cx_demo"
    target_platform      = "FIAttached"
    vhba_placement_mode  = "custom"
    wwnn_allocation_type = "POOL"
    wwnn_static_address  = ""
    wwnn_pool            = "VMware"
    tags                 = []
    vhbas = {
      "HBA-A" = {
        fibre_channel_adapter_policy = "VMware"
        fibre_channel_network_policy = "Fabric-A"
        fibre_channel_qos_policy     = "FC_QoS"
        name                         = "HBA-A"
        persistent_lun_bindings      = false
        wwpn_allocation_type         = "POOL"
        wwpn_pool                    = "VMware-A"
      },
      "HBA-B" = {
        fibre_channel_adapter_policy = "VMware"
        fibre_channel_network_policy = "Fabric-B"
        fibre_channel_qos_policy     = "FC_QoS"
        name                         = "HBA-B"
        persistent_lun_bindings      = false
        wwpn_allocation_type         = "POOL"
        wwpn_pool                    = "VMware-B"
      },
    }
  }
}