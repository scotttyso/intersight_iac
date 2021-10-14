#______________________________________________
#
# Fibre Channel Adapter Policy Variables
#______________________________________________

fibre_channel_adapter_policies = {
  "default" = {
    description                       = "default-adapter-policy"
    error_detection_timeout           = 2000
    enable_fcp_error_recovery         = false
    error_recovery_io_retry_timeout   = 5
    error_recovery_link_down_timeout  = 30000
    error_recovery_port_down_io_retry = 30
    error_recovery_port_down_timeout  = 30000
    flogi_retries                     = 8
    flogi_timeout                     = 4000
    interrupt_mode                    = "MSIx"
    io_throttle_count                 = 256
    lun_queue_depth                   = 20
    max_luns_per_target               = 1024
    organization                      = "UCS-DEMO2"
    plogi_retries                     = 8
    plogi_timeout                     = 20000
    resource_allocation_timeout       = 10000
    receive_ring_size                 = 64
    scsi_io_queue_count               = 1
    scsi_io_ring_size                 = 512
    transmit_ring_size                = 64
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
  "FCNVMeInitiator" = {
    description                       = "Recommended-adapter-settings-for-FC-NVMe-Initiator-Mode"
    error_detection_timeout           = 2000
    enable_fcp_error_recovery         = false
    error_recovery_io_retry_timeout   = 5
    error_recovery_link_down_timeout  = 30000
    error_recovery_port_down_io_retry = 30
    error_recovery_port_down_timeout  = 30000
    flogi_retries                     = 8
    flogi_timeout                     = 4000
    interrupt_mode                    = "MSIx"
    io_throttle_count                 = 256
    lun_queue_depth                   = 20
    max_luns_per_target               = 1024
    organization                      = "UCS-DEMO2"
    plogi_retries                     = 8
    plogi_timeout                     = 20000
    resource_allocation_timeout       = 10000
    receive_ring_size                 = 64
    scsi_io_queue_count               = 16
    scsi_io_ring_size                 = 512
    transmit_ring_size                = 64
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
  "FCNVMeTarget" = {
    description                       = "Recommended-adapter-settings-for-FC-NVMe-Target-Mode"
    error_detection_timeout           = 2000
    enable_fcp_error_recovery         = false
    error_recovery_io_retry_timeout   = 5
    error_recovery_link_down_timeout  = 30000
    error_recovery_port_down_io_retry = 30
    error_recovery_port_down_timeout  = 30000
    flogi_retries                     = 8
    flogi_timeout                     = 4000
    interrupt_mode                    = "MSIx"
    io_throttle_count                 = 256
    lun_queue_depth                   = 20
    max_luns_per_target               = 1024
    organization                      = "UCS-DEMO2"
    plogi_retries                     = 8
    plogi_timeout                     = 20000
    resource_allocation_timeout       = 10000
    receive_ring_size                 = 2048
    scsi_io_queue_count               = 16
    scsi_io_ring_size                 = 512
    transmit_ring_size                = 64
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
  "Initiator" = {
    description                       = "Recommended-adapter-settings-for-FC-Initiator-Mode"
    error_detection_timeout           = 2000
    enable_fcp_error_recovery         = false
    error_recovery_io_retry_timeout   = 5
    error_recovery_link_down_timeout  = 30000
    error_recovery_port_down_io_retry = 30
    error_recovery_port_down_timeout  = 10000
    flogi_retries                     = 8
    flogi_timeout                     = 4000
    interrupt_mode                    = "MSIx"
    io_throttle_count                 = 256
    lun_queue_depth                   = 20
    max_luns_per_target               = 1024
    organization                      = "UCS-DEMO2"
    plogi_retries                     = 8
    plogi_timeout                     = 20000
    resource_allocation_timeout       = 10000
    receive_ring_size                 = 64
    scsi_io_queue_count               = 1
    scsi_io_ring_size                 = 512
    transmit_ring_size                = 64
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
  "Linux" = {
    description                       = "Recommended-adapter-settings-for-Linux"
    error_detection_timeout           = 2000
    enable_fcp_error_recovery         = false
    error_recovery_io_retry_timeout   = 5
    error_recovery_link_down_timeout  = 30000
    error_recovery_port_down_io_retry = 30
    error_recovery_port_down_timeout  = 30000
    flogi_retries                     = 8
    flogi_timeout                     = 4000
    interrupt_mode                    = "MSIx"
    io_throttle_count                 = 256
    lun_queue_depth                   = 20
    max_luns_per_target               = 1024
    organization                      = "UCS-DEMO2"
    plogi_retries                     = 8
    plogi_timeout                     = 20000
    resource_allocation_timeout       = 10000
    receive_ring_size                 = 64
    scsi_io_queue_count               = 1
    scsi_io_ring_size                 = 512
    transmit_ring_size                = 64
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
  "Solaris" = {
    description                       = "Recommended-adapter-settings-for-Solaris"
    error_detection_timeout           = 2000
    enable_fcp_error_recovery         = false
    error_recovery_io_retry_timeout   = 5
    error_recovery_link_down_timeout  = 30000
    error_recovery_port_down_io_retry = 30
    error_recovery_port_down_timeout  = 30000
    flogi_retries                     = 8
    flogi_timeout                     = 4000
    interrupt_mode                    = "MSIx"
    io_throttle_count                 = 256
    lun_queue_depth                   = 20
    max_luns_per_target               = 1024
    organization                      = "UCS-DEMO2"
    plogi_retries                     = 8
    plogi_timeout                     = 20000
    resource_allocation_timeout       = 10000
    receive_ring_size                 = 64
    scsi_io_queue_count               = 1
    scsi_io_ring_size                 = 512
    transmit_ring_size                = 64
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
  "Target" = {
    description                       = "Recommended-adapter-settings-for-FC-Target-Mode"
    error_detection_timeout           = 2000
    enable_fcp_error_recovery         = false
    error_recovery_io_retry_timeout   = 5
    error_recovery_link_down_timeout  = 30000
    error_recovery_port_down_io_retry = 30
    error_recovery_port_down_timeout  = 30000
    flogi_retries                     = 8
    flogi_timeout                     = 4000
    interrupt_mode                    = "MSIx"
    io_throttle_count                 = 256
    lun_queue_depth                   = 20
    max_luns_per_target               = 1024
    organization                      = "UCS-DEMO2"
    plogi_retries                     = 8
    plogi_timeout                     = 20000
    resource_allocation_timeout       = 10000
    receive_ring_size                 = 2048
    scsi_io_queue_count               = 1
    scsi_io_ring_size                 = 512
    transmit_ring_size                = 64
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
  "VMWare" = {
    description                       = "Recommended-adapter-settings-for-VMWare"
    error_detection_timeout           = 2000
    enable_fcp_error_recovery         = false
    error_recovery_io_retry_timeout   = 5
    error_recovery_link_down_timeout  = 30000
    error_recovery_port_down_io_retry = 30
    error_recovery_port_down_timeout  = 10000
    flogi_retries                     = 8
    flogi_timeout                     = 4000
    interrupt_mode                    = "MSIx"
    io_throttle_count                 = 256
    lun_queue_depth                   = 20
    max_luns_per_target               = 1024
    organization                      = "UCS-DEMO2"
    plogi_retries                     = 8
    plogi_timeout                     = 20000
    resource_allocation_timeout       = 10000
    receive_ring_size                 = 64
    scsi_io_queue_count               = 1
    scsi_io_ring_size                 = 512
    transmit_ring_size                = 64
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
  "Windows" = {
    description                       = "Recommended-adapter-settings-for-Windows"
    error_detection_timeout           = 2000
    enable_fcp_error_recovery         = false
    error_recovery_io_retry_timeout   = 5
    error_recovery_link_down_timeout  = 30000
    error_recovery_port_down_io_retry = 30
    error_recovery_port_down_timeout  = 30000
    flogi_retries                     = 8
    flogi_timeout                     = 4000
    interrupt_mode                    = "MSIx"
    io_throttle_count                 = 256
    lun_queue_depth                   = 20
    max_luns_per_target               = 1024
    organization                      = "UCS-DEMO2"
    plogi_retries                     = 8
    plogi_timeout                     = 20000
    resource_allocation_timeout       = 10000
    receive_ring_size                 = 64
    scsi_io_queue_count               = 1
    scsi_io_ring_size                 = 512
    transmit_ring_size                = 64
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
  "WindowsBoot" = {
    description                       = "Recommended-adapter-settings-for-Windows-SAN-Boot"
    error_detection_timeout           = 2000
    enable_fcp_error_recovery         = false
    error_recovery_io_retry_timeout   = 5
    error_recovery_link_down_timeout  = 30000
    error_recovery_port_down_io_retry = 30
    error_recovery_port_down_timeout  = 5000
    flogi_retries                     = 8
    flogi_timeout                     = 4000
    interrupt_mode                    = "MSIx"
    io_throttle_count                 = 256
    lun_queue_depth                   = 20
    max_luns_per_target               = 1024
    organization                      = "UCS-DEMO2"
    plogi_retries                     = 8
    plogi_timeout                     = 4000
    resource_allocation_timeout       = 10000
    receive_ring_size                 = 64
    scsi_io_queue_count               = 1
    scsi_io_ring_size                 = 512
    transmit_ring_size                = 64
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