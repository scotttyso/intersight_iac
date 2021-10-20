#_________________________________________________________________________
#
# Ethernet Adapter Policies
# GUI Location: Configure > Policies > Create Policy > Ethernet Adapter
#_________________________________________________________________________

variable "ethernet_adapter_policies" {
  default = {
    default = {
      adapter_template                         = ""
      completion_queue_count                   = 2
      completion_ring_size                     = 1
      description                              = ""
      enable_accelerated_receive_flow_steering = false
      enable_advanced_filter                   = false
      enable_geneve_offload                    = false
      enable_interrupt_scaling                 = false
      enable_nvgre_offload                     = false
      enable_vxlan_offload                     = false
      interrupt_coalescing_type                = "MIN"
      interrupt_mode                           = "MSIx"
      interrupt_timer                          = 125
      interrupts                               = 4
      organization                             = "default"
      receive_queue_count                      = 4
      receive_ring_size                        = 512
      receive_side_scaling_enable              = true
      roce_cos                                 = 5
      roce_enable                              = false
      roce_memory_regions                      = 131072
      roce_queue_pairs                         = 256
      roce_resource_groups                     = 4
      roce_version                             = 1
      rss_enable_ipv4_hash                     = true
      rss_enable_ipv6_extensions_hash          = false
      rss_enable_ipv6_hash                     = true
      rss_enable_tcp_and_ipv4_hash             = true
      rss_enable_tcp_and_ipv6_extensions_hash  = false
      rss_enable_tcp_and_ipv6_hash             = true
      rss_enable_udp_and_ipv4_hash             = false
      rss_enable_udp_and_ipv6_hash             = false
      tags                                     = []
      tcp_offload_large_recieve                = true
      tcp_offload_large_send                   = true
      tcp_offload_rx_checksum                  = true
      tcp_offload_tx_checksum                  = true
      transmit_queue_count                     = 1
      transmit_ring_size                       = 256
      uplink_failback_timeout                  = 5
    }
  }
  description = <<-EOT
  key - Name of the Ethernet Adapter Policy
  * adapter_template - Name of a Pre-Configured Adapter Policy.  Options are:
    - Linux
    - Linux-NVMe-RoCE
    - MQ
    - MQ-SMBd
    - SMBServer
    - SMBClient
    - Solaris
    - SRIOV
    - usNIC
    - usNICOracleRAC
    - VMWare
    - VMWarePassThru
    - WIN-AzureStack
    - Win-HPN
    - Win-HPN-SMBd
    - Windows
  * completion_queue_count - Default is 5. The number of completion queue resources to allocate. In general, the number of completion queue resources to allocate is equal to the number of transmit queue resources plus the number of receive queue resources.  Range is 1-2000.
  * completion_ring_size - Default is 1. The number of descriptors in each completion queue.  Range is 1-256.
  * description - Description for the Policy.
  * enable_accelerated_receive_flow_steerin - Default is false.  Status of Accelerated Receive Flow Steering on the virtual ethernet interface.
  * enable_advanced_filter - Default is false.  Enables advanced filtering on the interface.
  * enable_geneve_offload - Default is false.  GENEVE offload protocol allows you to create logical networks that span physical network boundaries by allowing any information to be encoded in a packet and passed between tunnel endpoints.
  * enable_interrupt_scaling - Default is false.  Enables Interrupt Scaling on the interface.
  * enable_nvgre_offload - Default is false.  Status of the Network Virtualization using Generic Routing Encapsulation on the virtual ethernet interface.
  * enable_vxlan_offload - Default is false.  Status of the Virtual Extensible LAN Protocol on the virtual ethernet interface.
  * interrupt_coalescing_type - Default is MIN.  Interrupt Coalescing Type. This can be one of the following:- MIN - The system waits for the time specified in the Coalescing Time field before sending another interrupt event IDLE - The system does not send an interrupt until there is a period of no activity lasting as least as long as the time specified in the Coalescing Time field.  Options are:
    - IDLE
    - MIN
  * interrupt_mode - Default is MSIx.  The preferred driver interrupt mode. This can be one of the following:
    - INTx - Line-based interrupt (INTx) mechanism similar to the one used in Legacy systems.
    - MSI - Message Signaled Interrupt (MSI) mechanism that treats messages as interrupts.
    - MSIx - Message Signaled Interrupt mechanism with the optional extension (MSIx).
  * interrupt_timer - Default is 125.  The time to wait between interrupts or the idle period that must be encountered before an interrupt is sent. To turn off interrupt coalescing, enter 0 (zero) in this field.  Range is 0-65535.
  * interrupts - Default is 8.  The number of interrupt resources to allocate. Typical value is be equal to the number of completion queue resources.  Range is 1-1024.
  * organization - Name of the Intersight Organization to assign this Policy to.
    - https://intersight.com/an/settings/organizations/
  * receive_queue_count - Default is 4.  The number of queue resources to allocate.  Range is 1-1000.
  * receive_ring_size - Default is 512.  The number of descriptors in each queue.  Range is 64-4096.
  * receive_side_scaling_enable - Default is true.  Receive Side Scaling allows the incoming traffic to be spread across multiple CPU cores.
  * roce_cos - Default is 6.  The Class of Service for RoCE on this virtual interface.  Options are:
    - 1
    - 2
    - 4
    - 5
    - 6
  * roce_enable - Default is false.  If enabled sets RDMA over Converged Ethernet (RoCE) on this virtual interface.
  * roce_memory_regions - Default is 0.  The number of memory regions per adapter. Recommended value = integer power of 2.  Range is 0-524288.
  * roce_queue_pairs - Default is 0.  The number of queue pairs per adapter. Recommended value = integer power of 2.  Range is 0-8192.
  * roce_version - Default is 1.  Configure RDMA over Converged Ethernet (RoCE) version on the virtual interface. Only RoCEv1 is supported on Cisco VIC 13xx series adapters and only RoCEv2 is supported on Cisco VIC 14xx series adapters.  Options are:
    - 1
    - 2
  * rss_enable_ipv4_hash - Default is true.  When enabled, the IPv4 address is used for traffic distribution.
  * rss_enable_ipv6_extensions_hash - Default is false.  When enabled, the IPv6 extensions are used for traffic distribution.
  * rss_enable_ipv6_hash - Default is true.  When enabled, the IPv6 address is used for traffic distribution.
  * rss_enable_tcp_and_ipv4_hash - Default is true.  When enabled, both the IPv4 address and TCP port number are used for traffic distribution.
  * rss_enable_tcp_and_ipv6_extensions_hash - Default is false.  When enabled, both the IPv6 extensions and TCP port number are used for traffic distribution.
  * rss_enable_tcp_and_ipv6_hash - Default is true.  When enabled, both the IPv6 address and TCP port number are used for traffic distribution.
  * rss_enable_udp_and_ipv4_hash - Default is false.  When enabled, both the IPv4 address and UDP port number are used for traffic distribution.
  * rss_enable_udp_and_ipv6_hash - Default is false.  When enabled, both the IPv6 address and UDP port number are used for traffic distribution.
  * tags - Default is [].  List of Key/Value Pairs to Assign as Attributes to the Policy.
  * tcp_offload_large_recieve - Default is true.  Enables the reassembly of segmented packets in hardware before sending them to the CPU.
  * tcp_offload_large_send - Default is true.  Enables the CPU to send large packets to the hardware for segmentation.
  * tcp_offload_rx_checksum - Default is true.  When enabled, the CPU sends all packet checksums to the hardware for validation.
  * tcp_offload_tx_checksum - Default is true.  When enabled, the CPU sends all packets to the hardware so that the checksum can be calculated.
  * transmit_queue_count - Default is 1.  The number of queue resources to allocate.  Range is 1-1000.
  * transmit_ring_size - Default is 256.  The number of descriptors in each queue.  Range is 64-4096.
  * uplink_failback_timeout - Default is 5.  Uplink Failback Timeout in seconds when uplink failover is enabled for a vNIC. After a vNIC has started using its secondary interface, this setting controls how long the primary interface must be available before the system resumes using the primary interface for the vNIC.  Range is 0-600.
  EOT
  type = map(object(
    {
      adapter_template                         = optional(string)
      completion_queue_count                   = optional(number)
      completion_ring_size                     = optional(number)
      description                              = optional(string)
      enable_accelerated_receive_flow_steering = optional(bool)
      enable_advanced_filter                   = optional(bool)
      enable_geneve_offload                    = optional(bool)
      enable_interrupt_scaling                 = optional(bool)
      enable_nvgre_offload                     = optional(bool)
      enable_vxlan_offload                     = optional(bool)
      interrupt_coalescing_type                = optional(string)
      interrupt_mode                           = optional(string)
      interrupt_timer                          = optional(number)
      interrupts                               = optional(number)
      organization                             = optional(string)
      receive_queue_count                      = optional(number)
      receive_ring_size                        = optional(number)
      receive_side_scaling_enable              = optional(bool)
      roce_cos                                 = optional(number)
      roce_enable                              = optional(bool)
      roce_memory_regions                      = optional(number)
      roce_queue_pairs                         = optional(number)
      roce_resource_groups                     = optional(number)
      roce_version                             = optional(number)
      rss_enable_ipv4_hash                     = optional(bool)
      rss_enable_ipv6_extensions_hash          = optional(bool)
      rss_enable_ipv6_hash                     = optional(bool)
      rss_enable_tcp_and_ipv4_hash             = optional(bool)
      rss_enable_tcp_and_ipv6_extensions_hash  = optional(bool)
      rss_enable_tcp_and_ipv6_hash             = optional(bool)
      rss_enable_udp_and_ipv4_hash             = optional(bool)
      rss_enable_udp_and_ipv6_hash             = optional(bool)
      tags                                     = optional(list(map(string)))
      tcp_offload_large_recieve                = optional(bool)
      tcp_offload_large_send                   = optional(bool)
      tcp_offload_rx_checksum                  = optional(bool)
      tcp_offload_tx_checksum                  = optional(bool)
      transmit_queue_count                     = optional(number)
      transmit_ring_size                       = optional(number)
      uplink_failback_timeout                  = optional(number)
    }
  ))
}

module "ethernet_adapter_policies" {
  depends_on = [
    local.org_moids
  ]
  source                                   = "terraform-cisco-modules/imm/intersight//modules/ethernet_adapter_policies"
  for_each                                 = local.ethernet_adapter_policies
  completion_queue_count                   = each.value.completion_queue_count
  completion_ring_size                     = each.value.completion_ring_size
  description                              = each.value.description
  enable_accelerated_receive_flow_steering = each.value.enable_accelerated_receive_flow_steering
  enable_advanced_filter                   = each.value.enable_advanced_filter
  enable_geneve_offload                    = each.value.enable_geneve_offload
  enable_interrupt_scaling                 = each.value.enable_interrupt_scaling
  enable_nvgre_offload                     = each.value.enable_nvgre_offload
  name                                     = each.key
  org_moid                                 = local.org_moids[each.value.organization].moid
  tags                                     = length(each.value.tags) > 0 ? each.value.tags : local.tags
  interrupt_coalescing_type                = each.value.interrupt_coalescing_type
  interrupt_mode                           = each.value.interrupt_mode
  interrupt_timer                          = each.value.interrupt_timer
  interrupts                               = each.value.interrupts
  receive_queue_count                      = each.value.receive_queue_count
  receive_ring_size                        = each.value.receive_ring_size
  receive_side_scaling_enable              = each.value.receive_side_scaling_enable
  rss_enable_ipv4_hash                     = each.value.rss_enable_ipv4_hash
  rss_enable_ipv6_extensions_hash          = each.value.rss_enable_ipv6_extensions_hash
  rss_enable_ipv6_hash                     = each.value.rss_enable_ipv6_hash
  rss_enable_tcp_and_ipv4_hash             = each.value.rss_enable_tcp_and_ipv4_hash
  rss_enable_tcp_and_ipv6_extensions_hash  = each.value.rss_enable_tcp_and_ipv6_extensions_hash
  rss_enable_tcp_and_ipv6_hash             = each.value.rss_enable_tcp_and_ipv6_hash
  rss_enable_udp_and_ipv4_hash             = each.value.rss_enable_udp_and_ipv4_hash
  rss_enable_udp_and_ipv6_hash             = each.value.rss_enable_udp_and_ipv6_hash
  roce_cos                                 = each.value.roce_cos
  roce_enable                              = each.value.roce_enable
  roce_memory_regions                      = each.value.roce_memory_regions
  roce_queue_pairs                         = each.value.roce_queue_pairs
  roce_resource_groups                     = each.value.roce_resource_groups
  roce_version                             = each.value.roce_version
  tcp_offload_large_recieve                = each.value.tcp_offload_large_recieve
  tcp_offload_large_send                   = each.value.tcp_offload_large_send
  tcp_offload_rx_checksum                  = each.value.tcp_offload_rx_checksum
  tcp_offload_tx_checksum                  = each.value.tcp_offload_tx_checksum
  transmit_queue_count                     = each.value.transmit_queue_count
  transmit_ring_size                       = each.value.transmit_ring_size
  uplink_failback_timeout                  = each.value.uplink_failback_timeout
  enable_vxlan_offload                     = each.value.enable_vxlan_offload
}
