#______________________________________________
#
# Ethernet Adapter Policy Variables
#______________________________________________

ethernet_adapter_policies = {
  "VMWare" = {
    completion_queue_count                   = 2
    completion_ring_size                     = 1
    enable_advanced_filter                   = false
    enable_accelerated_receive_flow_steering = false
    enable_interrupt_scaling                 = false
    enable_geneve_offload                    = false
    enable_nvgre_offload                     = false
    enable_vxlan_offload                     = false
    description                              = "Recommended-adapter-settings-for-VMWare"
    interrupt_coalescing_type                = "MIN"
    interrupt_mode                           = "MSIx"
    interrupt_timer                          = 125
    interrupts                               = 4
    organization                             = "UCS-DEMO2_FPV-FlexPod"
    roce_cos                                 = 5
    roce_enable                              = false
    roce_memory_regions                      = 0
    roce_queue_pairs                         = 0
    roce_resource_groups                     = 0
    receive_side_scaling_enable              = false
    rss_enable_ipv4_hash                     = true
    rss_enable_ipv6_extensions_hash          = false
    rss_enable_ipv6_hash                     = true
    rss_enable_tcp_and_ipv4_hash             = true
    rss_enable_tcp_and_ipv6_extensions_hash  = false
    rss_enable_tcp_and_ipv6_hash             = true
    rss_enable_udp_and_ipv4_hash             = false
    rss_enable_udp_and_ipv6_hash             = false
    receive_queue_count                      = 1
    receive_ring_size                        = 512
    tcp_offload_large_recieve                = true
    tcp_offload_large_send                   = true
    tcp_offload_rx_checksum                  = true
    tcp_offload_tx_checksum                  = true
    transmit_queue_count                     = 1
    transmit_ring_size                       = 256
    uplink_failback_timeout                  = 5
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
  "VMware-HighTrf" = {
    completion_queue_count                   = 16
    completion_ring_size                     = 1
    enable_advanced_filter                   = false
    enable_accelerated_receive_flow_steering = false
    enable_interrupt_scaling                 = false
    enable_geneve_offload                    = false
    enable_nvgre_offload                     = false
    enable_vxlan_offload                     = false
    description                              = ""
    interrupt_coalescing_type                = "MIN"
    interrupt_mode                           = "MSIx"
    interrupt_timer                          = 125
    interrupts                               = 18
    organization                             = "UCS-DEMO2_FPV-FlexPod"
    roce_cos                                 = 5
    roce_enable                              = false
    roce_memory_regions                      = 0
    roce_queue_pairs                         = 0
    roce_resource_groups                     = 0
    receive_side_scaling_enable              = true
    rss_enable_ipv4_hash                     = true
    rss_enable_ipv6_extensions_hash          = false
    rss_enable_ipv6_hash                     = true
    rss_enable_tcp_and_ipv4_hash             = true
    rss_enable_tcp_and_ipv6_extensions_hash  = false
    rss_enable_tcp_and_ipv6_hash             = true
    rss_enable_udp_and_ipv4_hash             = false
    rss_enable_udp_and_ipv6_hash             = false
    receive_queue_count                      = 8
    receive_ring_size                        = 4096
    tcp_offload_large_recieve                = true
    tcp_offload_large_send                   = true
    tcp_offload_rx_checksum                  = true
    tcp_offload_tx_checksum                  = true
    transmit_queue_count                     = 8
    transmit_ring_size                       = 4096
    uplink_failback_timeout                  = 5
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