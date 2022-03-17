#_________________________________________________________________________
#
# Fibre Channel Adapter Polies
# GUI Location: Configure > Policies > Create Policy > Fibre Channel Adapter
#_________________________________________________________________________

variable "fibre_channel_adapter_policies" {
  default = {
    default = {
      adapter_template                  = ""
      description                       = ""
      error_detection_timeout           = 2000
      enable_fcp_error_recovery         = false
      error_recovery_io_retry_timeout   = 5
      error_recovery_link_down_timeout  = 30000
      error_recovery_port_down_io_retry = 8
      error_recovery_port_down_timeout  = 10000
      flogi_retries                     = 8
      flogi_timeout                     = 4000
      interrupt_mode                    = "MSIx"
      io_throttle_count                 = 256
      lun_queue_depth                   = 20
      max_luns_per_target               = 1024
      plogi_retries                     = 8
      plogi_timeout                     = 20000
      receive_ring_size                 = 64
      resource_allocation_timeout       = 10000
      scsi_io_queue_count               = 1
      scsi_io_ring_size                 = 512
      tags                              = []
      transmit_ring_size                = 64
    }
  }
  description = <<-EOT
  key - Name of the Fibre Channel Adapter Policy
  * adapter_template - Name of a Pre-Configured Adapter Policy.  Options are:
    - FCNVMeInitiator
    - FCNVMeTarget
    - Initiator
    - Linux
    - Solaris
    - Target
    - VMware
    - WindowsBoot
    - Windows
  * description - Description for the Policy.
  * error_detection_timeout - Default is 2000.  Error Detection Timeout, also referred to as EDTOV, is the number of milliseconds to wait before the system assumes that an error has occurred.
  * enable_fcp_error_recovery - Default is false.  Enables Fibre Channel Error recovery.
  * error_recovery_port_down_io_retry - Default is 8.  The number of times an I/O request to a port is retried because the port is busy before the system decides the port is unavailable.  Range is 0-255.
  * error_recovery_io_retry_timeout - Default is 5.  The number of seconds the adapter waits before aborting the pending command and resending the same IO request. Range is 1-59.
  * error_recovery_link_down_timeout - Default is 30000.  The number of milliseconds the port should actually be down before it is marked down and fabric connectivity is lost.  Range is 0-240000.
  * error_recovery_port_down_timeout - Default is 10000.  The number of milliseconds a remote Fibre Channel port should be offline before informing the SCSI upper layer that the port is unavailable. For a server with a VIC adapter running ESXi, the recommended value is 10000. For a server with a port used to boot a Windows OS from the SAN, the recommended value is 5000 milliseconds.  Range is 0-240000.
  * flogi_retries - Default is 8.  The number of times that the system tries to log in to the fabric after the first failure.  A Value greater than 0.
  * flogi_timeout - Default is 4000.  The number of milliseconds that the system waits before it tries to log in again.  Range is 1000-255000.
  * interrupt_mode - Default is MSIx.  The preferred driver interrupt mode. This can be one of the following:
    - INTx - Line-based interrupt (INTx) mechanism similar to the one used in Legacy systems.
    - MSI - Message Signaled Interrupt (MSI) mechanism that treats messages as interrupts.
    - MSIx - Message Signaled Interrupt mechanism with the optional extension (MSIx).
  * io_throttle_count - Default is 512.  The maximum number of data or control I/O operations that can be pending for the virtual interface at one time. If this value is exceeded, the additional I/O operations wait in the queue until the number of pending I/O operations decreases and the additional operations can be processed.  Range is 1-1024.
  * lun_queue_depth - Default is 20.  The number of commands that the HBA can send and receive in a single transmission per LUN.  Range is 1-254.
  * max_luns_per_target - Default is 1024.  The maximum number of LUNs that the Fibre Channel driver will export or show. The maximum number of LUNs is usually controlled by the operating system running on the server.  Rnage is 1-1024.
  * plogi_retries - Default is 8.  The number of times that the system tries to log in to a port after the first failure.  Range is 0-255.
  * plogi_timeout - Default is 20000.  The number of milliseconds that the system waits before it tries to log in again.  Range is 1000-255000.
  * receive_ring_size - Default is 64.  The number of descriptors in each queue.  Range is 64-2048.
  * resource_allocation_timeout - Default is 10000.  Resource Allocation Timeout, also referred to as RATOV, is the number of milliseconds to wait before the system assumes that a resource cannot be properly allocated.  Range is 5000-100000.
  * scsi_io_queue_count - Default is 1.  The number of SCSI I/O queue resources the system should allocate.  Range is 1-245.
  * scsi_io_ring_size - Default is 512.  The number of descriptors in each SCSI I/O queue.  Range is 64-512.
  * tags - Default is [].  List of Key/Value Pairs to Assign as Attributes to the Policy.
  * transmit_ring_size - Default is 64.  The number of descriptors in each queue.  Range is 64-2048.
  EOT
  type = map(object(
    {
      adapter_template                  = optional(string)
      description                       = optional(string)
      error_detection_timeout           = optional(number)
      enable_fcp_error_recovery         = optional(bool)
      error_recovery_io_retry_timeout   = optional(number)
      error_recovery_link_down_timeout  = optional(number)
      error_recovery_port_down_io_retry = optional(number)
      error_recovery_port_down_timeout  = optional(number)
      flogi_retries                     = optional(number)
      flogi_timeout                     = optional(number)
      interrupt_mode                    = optional(string)
      io_throttle_count                 = optional(number)
      lun_queue_depth                   = optional(number)
      max_luns_per_target               = optional(number)
      plogi_retries                     = optional(number)
      plogi_timeout                     = optional(number)
      receive_ring_size                 = optional(number)
      resource_allocation_timeout       = optional(number)
      scsi_io_queue_count               = optional(number)
      scsi_io_ring_size                 = optional(number)
      tags                              = optional(list(map(string)))
      transmit_ring_size                = optional(number)
    }
  ))
}

#_______________________________________________________________________________
#
# Fibre-Channel Adapter Policies
# GUI Location: Configure > Policies > Create Policy > Fibre-Channel Adapter
#_______________________________________________________________________________

resource "intersight_vnic_fc_adapter_policy" "fibre_channel_adapter_policies" {
  depends_on = [
    local.org_moid
  ]
  for_each                    = local.fibre_channel_adapter_policies
  description                 = each.value.description != "" ? each.value.description : "${each.key} Fibre Channel Adapter Policy"
  error_detection_timeout     = each.value.error_detection_timeout
  io_throttle_count           = each.value.io_throttle_count
  lun_count                   = each.value.max_luns_per_target
  lun_queue_depth             = each.value.lun_queue_depth
  name                        = each.key
  resource_allocation_timeout = each.value.resource_allocation_timeout
  error_recovery_settings {
    enabled           = each.value.enable_fcp_error_recovery
    io_retry_count    = each.value.error_recovery_port_down_io_retry
    io_retry_timeout  = each.value.error_recovery_io_retry_timeout
    link_down_timeout = each.value.error_recovery_link_down_timeout
    port_down_timeout = each.value.error_recovery_port_down_timeout
  }
  flogi_settings {
    retries = each.value.flogi_retries
    timeout = each.value.flogi_timeout
  }
  interrupt_settings {
    mode = each.value.interrupt_mode
  }
  organization {
    moid        = local.org_moid
    object_type = "organization.Organization"
  }
  plogi_settings {
    retries = each.value.plogi_retries
    timeout = each.value.plogi_timeout
  }
  rx_queue_settings {
    ring_size = each.value.receive_ring_size
  }
  scsi_queue_settings {
    nr_count  = each.value.scsi_io_queue_count
    ring_size = each.value.scsi_io_ring_size
  }
  tx_queue_settings {
    ring_size = each.value.transmit_ring_size
  }
  dynamic "tags" {
    for_each = length(each.value.tags) > 0 ? each.value.tags : local.tags
    content {
      key   = tags.value.key
      value = tags.value.value
    }
  }
}
