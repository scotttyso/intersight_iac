defaults = {
  intersight = {
    moids        = true
    organization = "default"
    policies = {
      adapter_configuration = {
        adapter_ports       = 4
        enable_fip          = true
        enable_lldp         = true
        enable_port_channel = true
        fec_modes = [
          "cl91",
        ]
        name_suffix = ""
        pci_slot    = "MLOM"
      }
      bios = {
        acs_control_gpu1state                 = "platform-default"
        acs_control_gpu2state                 = "platform-default"
        acs_control_gpu3state                 = "platform-default"
        acs_control_gpu4state                 = "platform-default"
        acs_control_gpu5state                 = "platform-default"
        acs_control_gpu6state                 = "platform-default"
        acs_control_gpu7state                 = "platform-default"
        acs_control_gpu8state                 = "platform-default"
        acs_control_slot11state               = "platform-default"
        acs_control_slot12state               = "platform-default"
        acs_control_slot13state               = "platform-default"
        acs_control_slot14state               = "platform-default"
        adjacent_cache_line_prefetch          = "platform-default"
        advanced_mem_test                     = "platform-default"
        all_usb_devices                       = "platform-default"
        altitude                              = "platform-default"
        aspm_support                          = "platform-default"
        assert_nmi_on_perr                    = "platform-default"
        assert_nmi_on_serr                    = "platform-default"
        auto_cc_state                         = "platform-default"
        autonumous_cstate_enable              = "platform-default"
        baud_rate                             = "platform-default"
        bme_dma_mitigation                    = "platform-default"
        boot_option_num_retry                 = "platform-default"
        boot_option_re_cool_down              = "platform-default"
        boot_option_retry                     = "platform-default"
        boot_performance_mode                 = "platform-default"
        burst_and_postponed_refresh           = "platform-default"
        c1auto_demotion                       = "platform-default"
        c1auto_un_demotion                    = "platform-default"
        cbs_cmn_apbdis                        = "platform-default"
        cbs_cmn_cpu_cpb                       = "platform-default"
        cbs_cmn_cpu_gen_downcore_ctrl         = "platform-default"
        cbs_cmn_cpu_global_cstate_ctrl        = "platform-default"
        cbs_cmn_cpu_l1stream_hw_prefetcher    = "platform-default"
        cbs_cmn_cpu_l2stream_hw_prefetcher    = "platform-default"
        cbs_cmn_cpu_smee                      = "platform-default"
        cbs_cmn_cpu_streaming_stores_ctrl     = "platform-default"
        cbs_cmn_determinism_slider            = "platform-default"
        cbs_cmn_efficiency_mode_en            = "platform-default"
        cbs_cmn_fixed_soc_pstate              = "platform-default"
        cbs_cmn_gnb_nb_iommu                  = "platform-default"
        cbs_cmn_gnb_smu_df_cstates            = "platform-default"
        cbs_cmn_gnb_smucppc                   = "platform-default"
        cbs_cmn_mem_ctrl_bank_group_swap_ddr4 = "platform-default"
        cbs_cmn_mem_map_bank_interleave_ddr4  = "platform-default"
        cbs_cmnc_tdp_ctl                      = "platform-default"
        cbs_cpu_ccd_ctrl_ssp                  = "platform-default"
        cbs_cpu_core_ctrl                     = "platform-default"
        cbs_cpu_smt_ctrl                      = "platform-default"
        cbs_dbg_cpu_snp_mem_cover             = "platform-default"
        cbs_dbg_cpu_snp_mem_size_cover        = "platform-default"
        cbs_df_cmn_acpi_srat_l3numa           = "platform-default"
        cbs_df_cmn_dram_nps                   = "platform-default"
        cbs_df_cmn_mem_intlv                  = "platform-default"
        cbs_df_cmn_mem_intlv_size             = "platform-default"
        cbs_sev_snp_support                   = "platform-default"
        cdn_enable                            = "platform-default"
        cdn_support                           = "platform-default"
        channel_inter_leave                   = "platform-default"
        cisco_adaptive_mem_training           = "platform-default"
        cisco_debug_level                     = "platform-default"
        cisco_oprom_launch_optimization       = "platform-default"
        cisco_xgmi_max_speed                  = "platform-default"
        cke_low_policy                        = "platform-default"
        closed_loop_therm_throtl              = "platform-default"
        cmci_enable                           = "platform-default"
        config_tdp                            = "platform-default"
        config_tdp_level                      = "platform-default"
        console_redirection                   = "platform-default"
        core_multi_processing                 = "platform-default"
        cpu_energy_performance                = "platform-default"
        cpu_frequency_floor                   = "platform-default"
        cpu_pa_limit                          = "platform-default"
        cpu_perf_enhancement                  = "platform-default"
        cpu_performance                       = "platform-default"
        cpu_power_management                  = "platform-default"
        cr_qos                                = "platform-default"
        crfastgo_config                       = "platform-default"
        dcpmm_firmware_downgrade              = "platform-default"
        demand_scrub                          = "platform-default"
        direct_cache_access                   = "platform-default"
        dram_clock_throttling                 = "platform-default"
        dram_refresh_rate                     = "platform-default"
        dram_sw_thermal_throttling            = "platform-default"
        eadr_support                          = "platform-default"
        edpc_en                               = "platform-default"
        enable_clock_spread_spec              = "platform-default"
        enable_mktme                          = "platform-default"
        enable_sgx                            = "platform-default"
        enable_tme                            = "platform-default"
        energy_efficient_turbo                = "platform-default"
        eng_perf_tuning                       = "platform-default"
        enhanced_intel_speed_step_tech        = "platform-default"
        epoch_update                          = "platform-default"
        epp_enable                            = "platform-default"
        epp_profile                           = "platform-default"
        execute_disable_bit                   = "platform-default"
        extended_apic                         = "platform-default"
        flow_control                          = "platform-default"
        frb2enable                            = "platform-default"
        hardware_prefetch                     = "platform-default"
        hwpm_enable                           = "platform-default"
        imc_interleave                        = "platform-default"
        intel_dynamic_speed_select            = "platform-default"
        intel_hyper_threading_tech            = "platform-default"
        intel_speed_select                    = "platform-default"
        intel_turbo_boost_tech                = "platform-default"
        intel_virtualization_technology       = "platform-default"
        intel_vt_for_directed_io              = "platform-default"
        intel_vtd_coherency_support           = "platform-default"
        intel_vtd_interrupt_remapping         = "platform-default"
        intel_vtd_pass_through_dma_support    = "platform-default"
        intel_vtdats_support                  = "platform-default"
        ioh_error_enable                      = "platform-default"
        ioh_resource                          = "platform-default"
        ip_prefetch                           = "platform-default"
        ipv4http                              = "platform-default"
        ipv4pxe                               = "platform-default"
        ipv6http                              = "platform-default"
        ipv6pxe                               = "platform-default"
        kti_prefetch                          = "platform-default"
        legacy_os_redirection                 = "platform-default"
        legacy_usb_support                    = "platform-default"
        llc_alloc                             = "platform-default"
        llc_prefetch                          = "platform-default"
        lom_port0state                        = "platform-default"
        lom_port1state                        = "platform-default"
        lom_port2state                        = "platform-default"
        lom_port3state                        = "platform-default"
        lom_ports_all_state                   = "platform-default"
        lv_ddr_mode                           = "platform-default"
        make_device_non_bootable              = "platform-default"
        memory_bandwidth_boost                = "platform-default"
        memory_inter_leave                    = "platform-default"
        memory_mapped_io_above4gb             = "platform-default"
        memory_refresh_rate                   = "platform-default"
        memory_size_limit                     = "platform-default"
        memory_thermal_throttling             = "platform-default"
        mirroring_mode                        = "platform-default"
        mmcfg_base                            = "platform-default"
        name_suffix                           = ""
        network_stack                         = "platform-default"
        numa_optimized                        = "platform-default"
        nvmdimm_perform_config                = "platform-default"
        onboard10gbit_lom                     = "platform-default"
        onboard_gbit_lom                      = "platform-default"
        onboard_scu_storage_support           = "platform-default"
        onboard_scu_storage_sw_stack          = "platform-default"
        operation_mode                        = "platform-default"
        os_boot_watchdog_timer                = "platform-default"
        os_boot_watchdog_timer_policy         = "platform-default"
        os_boot_watchdog_timer_timeout        = "platform-default"
        out_of_band_mgmt_port                 = "platform-default"
        package_cstate_limit                  = "platform-default"
        panic_high_watermark                  = "platform-default"
        partial_cache_line_sparing            = "platform-default"
        partial_mirror_mode_config            = "platform-default"
        partial_mirror_percent                = "platform-default"
        partial_mirror_value1                 = "platform-default"
        partial_mirror_value2                 = "platform-default"
        partial_mirror_value3                 = "platform-default"
        partial_mirror_value4                 = "platform-default"
        patrol_scrub                          = "platform-default"
        patrol_scrub_duration                 = "platform-default"
        pc_ie_ras_support                     = "platform-default"
        pc_ie_ssd_hot_plug_support            = "platform-default"
        pch_usb30mode                         = "platform-default"
        pci_option_ro_ms                      = "platform-default"
        pci_rom_clp                           = "platform-default"
        pcie_ari_support                      = "platform-default"
        pcie_pll_ssc                          = "platform-default"
        pcie_slot_mraid1link_speed            = "platform-default"
        pcie_slot_mraid1option_rom            = "platform-default"
        pcie_slot_mraid2link_speed            = "platform-default"
        pcie_slot_mraid2option_rom            = "platform-default"
        pcie_slot_mstorraid_link_speed        = "platform-default"
        pcie_slot_mstorraid_option_rom        = "platform-default"
        pcie_slot_nvme1link_speed             = "platform-default"
        pcie_slot_nvme1option_rom             = "platform-default"
        pcie_slot_nvme2link_speed             = "platform-default"
        pcie_slot_nvme2option_rom             = "platform-default"
        pcie_slot_nvme3link_speed             = "platform-default"
        pcie_slot_nvme3option_rom             = "platform-default"
        pcie_slot_nvme4link_speed             = "platform-default"
        pcie_slot_nvme4option_rom             = "platform-default"
        pcie_slot_nvme5link_speed             = "platform-default"
        pcie_slot_nvme5option_rom             = "platform-default"
        pcie_slot_nvme6link_speed             = "platform-default"
        pcie_slot_nvme6option_rom             = "platform-default"
        pcie_slots_cdn_enable                 = "platform-default"
        pop_support                           = "platform-default"
        post_error_pause                      = "platform-default"
        post_package_repair                   = "platform-default"
        processor_c1e                         = "platform-default"
        processor_c3report                    = "platform-default"
        processor_c6report                    = "platform-default"
        processor_cstate                      = "platform-default"
        psata                                 = "platform-default"
        pstate_coord_type                     = "platform-default"
        putty_key_pad                         = "platform-default"
        pwr_perf_tuning                       = "platform-default"
        qpi_link_frequency                    = "platform-default"
        qpi_link_speed                        = "platform-default"
        qpi_snoop_mode                        = "platform-default"
        rank_inter_leave                      = "platform-default"
        redirection_after_post                = "platform-default"
        sata_mode_select                      = "platform-default"
        select_memory_ras_configuration       = "platform-default"
        select_ppr_type                       = "platform-default"
        serial_port_aenable                   = "platform-default"
        sev                                   = "platform-default"
        sgx_auto_registration_agent           = "platform-default"
        sgx_epoch0                            = "platform-default"
        sgx_epoch1                            = "platform-default"
        sgx_factory_reset                     = "platform-default"
        sgx_le_pub_key_hash0                  = "platform-default"
        sgx_le_pub_key_hash1                  = "platform-default"
        sgx_le_pub_key_hash2                  = "platform-default"
        sgx_le_pub_key_hash3                  = "platform-default"
        sgx_le_wr                             = "platform-default"
        sgx_package_info_in_band_access       = "platform-default"
        sgx_qos                               = "platform-default"
        sha1pcr_bank                          = "platform-default"
        sha256pcr_bank                        = "platform-default"
        single_pctl_enable                    = "platform-default"
        slot10link_speed                      = "platform-default"
        slot10state                           = "platform-default"
        slot11link_speed                      = "platform-default"
        slot11state                           = "platform-default"
        slot12link_speed                      = "platform-default"
        slot12state                           = "platform-default"
        slot13state                           = "platform-default"
        slot14state                           = "platform-default"
        slot1link_speed                       = "platform-default"
        slot1state                            = "platform-default"
        slot2link_speed                       = "platform-default"
        slot2state                            = "platform-default"
        slot3link_speed                       = "platform-default"
        slot3state                            = "platform-default"
        slot4link_speed                       = "platform-default"
        slot4state                            = "platform-default"
        slot5link_speed                       = "platform-default"
        slot5state                            = "platform-default"
        slot6link_speed                       = "platform-default"
        slot6state                            = "platform-default"
        slot7link_speed                       = "platform-default"
        slot7state                            = "platform-default"
        slot8link_speed                       = "platform-default"
        slot8state                            = "platform-default"
        slot9link_speed                       = "platform-default"
        slot9state                            = "platform-default"
        slot_flom_link_speed                  = "platform-default"
        slot_front_nvme10link_speed           = "platform-default"
        slot_front_nvme10option_rom           = "platform-default"
        slot_front_nvme11link_speed           = "platform-default"
        slot_front_nvme11option_rom           = "platform-default"
        slot_front_nvme12link_speed           = "platform-default"
        slot_front_nvme12option_rom           = "platform-default"
        slot_front_nvme13option_rom           = "platform-default"
        slot_front_nvme14option_rom           = "platform-default"
        slot_front_nvme15option_rom           = "platform-default"
        slot_front_nvme16option_rom           = "platform-default"
        slot_front_nvme17option_rom           = "platform-default"
        slot_front_nvme18option_rom           = "platform-default"
        slot_front_nvme19option_rom           = "platform-default"
        slot_front_nvme1link_speed            = "platform-default"
        slot_front_nvme1option_rom            = "platform-default"
        slot_front_nvme20option_rom           = "platform-default"
        slot_front_nvme21option_rom           = "platform-default"
        slot_front_nvme22option_rom           = "platform-default"
        slot_front_nvme23option_rom           = "platform-default"
        slot_front_nvme24option_rom           = "platform-default"
        slot_front_nvme2link_speed            = "platform-default"
        slot_front_nvme2option_rom            = "platform-default"
        slot_front_nvme3link_speed            = "platform-default"
        slot_front_nvme3option_rom            = "platform-default"
        slot_front_nvme4link_speed            = "platform-default"
        slot_front_nvme4option_rom            = "platform-default"
        slot_front_nvme5link_speed            = "platform-default"
        slot_front_nvme5option_rom            = "platform-default"
        slot_front_nvme6link_speed            = "platform-default"
        slot_front_nvme6option_rom            = "platform-default"
        slot_front_nvme7link_speed            = "platform-default"
        slot_front_nvme7option_rom            = "platform-default"
        slot_front_nvme8link_speed            = "platform-default"
        slot_front_nvme8option_rom            = "platform-default"
        slot_front_nvme9link_speed            = "platform-default"
        slot_front_nvme9option_rom            = "platform-default"
        slot_front_slot5link_speed            = "platform-default"
        slot_front_slot6link_speed            = "platform-default"
        slot_gpu1state                        = "platform-default"
        slot_gpu2state                        = "platform-default"
        slot_gpu3state                        = "platform-default"
        slot_gpu4state                        = "platform-default"
        slot_gpu5state                        = "platform-default"
        slot_gpu6state                        = "platform-default"
        slot_gpu7state                        = "platform-default"
        slot_gpu8state                        = "platform-default"
        slot_hba_link_speed                   = "platform-default"
        slot_hba_state                        = "platform-default"
        slot_lom1link                         = "platform-default"
        slot_lom2link                         = "platform-default"
        slot_mezz_state                       = "platform-default"
        slot_mlom_link_speed                  = "platform-default"
        slot_mlom_state                       = "platform-default"
        slot_mraid_link_speed                 = "platform-default"
        slot_mraid_state                      = "platform-default"
        slot_n10state                         = "platform-default"
        slot_n11state                         = "platform-default"
        slot_n12state                         = "platform-default"
        slot_n13state                         = "platform-default"
        slot_n14state                         = "platform-default"
        slot_n15state                         = "platform-default"
        slot_n16state                         = "platform-default"
        slot_n17state                         = "platform-default"
        slot_n18state                         = "platform-default"
        slot_n19state                         = "platform-default"
        slot_n1state                          = "platform-default"
        slot_n20state                         = "platform-default"
        slot_n21state                         = "platform-default"
        slot_n22state                         = "platform-default"
        slot_n23state                         = "platform-default"
        slot_n24state                         = "platform-default"
        slot_n2state                          = "platform-default"
        slot_n3state                          = "platform-default"
        slot_n4state                          = "platform-default"
        slot_n5state                          = "platform-default"
        slot_n6state                          = "platform-default"
        slot_n7state                          = "platform-default"
        slot_n8state                          = "platform-default"
        slot_n9state                          = "platform-default"
        slot_raid_link_speed                  = "platform-default"
        slot_raid_state                       = "platform-default"
        slot_rear_nvme1link_speed             = "platform-default"
        slot_rear_nvme1state                  = "platform-default"
        slot_rear_nvme2link_speed             = "platform-default"
        slot_rear_nvme2state                  = "platform-default"
        slot_rear_nvme3link_speed             = "platform-default"
        slot_rear_nvme3state                  = "platform-default"
        slot_rear_nvme4link_speed             = "platform-default"
        slot_rear_nvme4state                  = "platform-default"
        slot_rear_nvme5state                  = "platform-default"
        slot_rear_nvme6state                  = "platform-default"
        slot_rear_nvme7state                  = "platform-default"
        slot_rear_nvme8state                  = "platform-default"
        slot_riser1link_speed                 = "platform-default"
        slot_riser1slot1link_speed            = "platform-default"
        slot_riser1slot2link_speed            = "platform-default"
        slot_riser1slot3link_speed            = "platform-default"
        slot_riser2link_speed                 = "platform-default"
        slot_riser2slot4link_speed            = "platform-default"
        slot_riser2slot5link_speed            = "platform-default"
        slot_riser2slot6link_speed            = "platform-default"
        slot_sas_state                        = "platform-default"
        slot_ssd_slot1link_speed              = "platform-default"
        slot_ssd_slot2link_speed              = "platform-default"
        smee                                  = "platform-default"
        smt_mode                              = "platform-default"
        snc                                   = "platform-default"
        snoopy_mode_for2lm                    = "platform-default"
        snoopy_mode_for_ad                    = "platform-default"
        sparing_mode                          = "platform-default"
        sr_iov                                = "platform-default"
        streamer_prefetch                     = "platform-default"
        svm_mode                              = "platform-default"
        terminal_type                         = "platform-default"
        tpm_control                           = "platform-default"
        tpm_pending_operation                 = "platform-default"
        tpm_ppi_required                      = "platform-default"
        tpm_support                           = "platform-default"
        tsme                                  = "platform-default"
        txt_support                           = "platform-default"
        ucsm_boot_order_rule                  = "platform-default"
        ufs_disable                           = "platform-default"
        uma_based_clustering                  = "platform-default"
        upi_link_enablement                   = "platform-default"
        upi_power_management                  = "platform-default"
        usb_emul6064                          = "platform-default"
        usb_port_front                        = "platform-default"
        usb_port_internal                     = "platform-default"
        usb_port_kvm                          = "platform-default"
        usb_port_rear                         = "platform-default"
        usb_port_sd_card                      = "platform-default"
        usb_port_vmedia                       = "platform-default"
        usb_xhci_support                      = "platform-default"
        vga_priority                          = "platform-default"
        virtual_numa                          = "platform-default"
        vmd_enable                            = "platform-default"
        vol_memory_mode                       = "platform-default"
        work_load_config                      = "platform-default"
        xpt_prefetch                          = "platform-default"
        xpt_remote_prefetch                   = "platform-default"
      }
      boot_order = {
        boot_mode          = "Uefi"
        enable_secure_boot = false
        name_suffix        = ""
      }
      certificate_management = {
        name_suffix = ""
      }
      device_connector = {
        configuration_lockout = false
        name_suffix           = ""
      }
      ethernet_adapter = {
        completion_queue_count                   = 5
        completion_ring_size                     = 1
        enable_accelerated_receive_flow_steering = false
        enable_advanced_filter                   = false
        enable_geneve_offload                    = false
        enable_interrupt_scaling                 = false
        enable_nvgre_offload                     = false
        enable_vxlan_offload                     = false
        interrupt_coalescing_type                = "MIN"
        interrupt_mode                           = "MSIx"
        interrupt_timer                          = 125
        interrupts                               = 8
        name_suffix                              = ""
        receive_queue_count                      = 4
        receive_ring_size                        = 512
        receive_side_scaling_enable              = true
        roce_cos                                 = 6
        roce_enable                              = false
        roce_memory_regions                      = 0
        roce_queue_pairs                         = 0
        roce_resource_groups                     = 0
        roce_version                             = 1
        rss_enable_ipv4_hash                     = true
        rss_enable_ipv6_extensions_hash          = false
        rss_enable_ipv6_hash                     = true
        rss_enable_tcp_and_ipv4_hash             = true
        rss_enable_tcp_and_ipv6_extensions_hash  = false
        rss_enable_tcp_and_ipv6_hash             = true
        rss_enable_udp_and_ipv4_hash             = false
        rss_enable_udp_and_ipv6_hash             = false
        tcp_offload_large_recieve                = true
        tcp_offload_large_send                   = true
        tcp_offload_rx_checksum                  = true
        tcp_offload_tx_checksum                  = true
        transmit_queue_count                     = 1
        transmit_ring_size                       = 256
        uplink_failback_timeout                  = 5
      }
      ethernet_network = {
        default_vlan = 0
        name_suffix  = ""
        vlan_mode    = "ACCESS"
      }
      ethernet_network_control = {
        action_on_uplink_fail = "linkDown"
        cdp_enable            = false
        lldp_enable_receive   = false
        lldp_enable_transmit  = false
        mac_register_mode     = "nativeVlanOnly"
        mac_security_forge    = "allow"
        name_suffix           = ""
      }
      ethernet_network_group = {
        name_suffix = ""
      }
      ethernet_qos = {
        burst                 = 1024
        cos                   = 0
        enable_trust_host_cos = false
        mtu                   = 1500
        name_suffix           = ""
        priority              = "Best Effort"
        rate_limit            = 0
      }
      fc_zone = {
        fc_target_zoning_type = "SIMT"
        name_suffix           = ""
      }
      fibre_channel_adapter = {
        enable_fcp_error_recovery         = false
        error_detection_timeout           = 2000
        error_recovery_io_retry_timeout   = 5
        error_recovery_link_down_timeout  = 30000
        error_recovery_port_down_io_retry = 8
        error_recovery_port_down_timeout  = 10000
        flogi_retries                     = 8
        flogi_timeout                     = 4000
        interrupt_mode                    = "MSIx"
        io_throttle_count                 = 512
        lun_queue_depth                   = 20
        max_luns_per_target               = 1024
        name_suffix                       = ""
        plogi_retries                     = 8
        plogi_timeout                     = 20000
        receive_ring_size                 = 64
        resource_allocation_timeout       = 10000
        scsi_io_queue_count               = 1
        scsi_io_ring_size                 = 512
        transmit_ring_size                = 64
      }
      fibre_channel_network = {
        default_vlan_id = 0
        name_suffix     = ""
      }
      fibre_channel_qos = {
        burst               = 1024
        cos                 = 3
        max_data_field_size = 2112
        name_suffix         = ""
        rate_limit          = 0
      }
      flow_control = {
        name_suffix = ""
        priority    = "auto"
        receive     = "Disabled"
        send        = "Disabled"
      }
      imc_access = {
        inband_vlan_id             = 4
        ipv4_address_configuration = true
        ipv6_address_configuration = false
        name_suffix                = ""
      }
      ipmi_over_lan = {
        enabled     = true
        name_suffix = ""
        privilege   = "admin"
      }
      iscsi_adapter = {
        dhcp_timeout           = 60
        lun_busy_retry_count   = 15
        name_suffix            = ""
        tcp_connection_timeout = 15
      }
      iscsi_boot = {
        authentication      = ""
        dhcp_vendor_id_iqn  = ""
        initiator_ip_source = "Pool"
        name_suffix         = ""
        target_source_type  = "Auto"
      }
      iscsi_static_target = {
        name_suffix = ""
      }
      lan_connectivity = {
        enable_azure_stack_host_qos = false
        iqn_allocation_type         = "None"
        iqn_pool                    = ""
        iqn_static_identifier       = ""
        name_suffix                 = ""
        target_platform             = "FIAttached"
        vnic_placement_mode         = "custom"
        vnics = {
          cdn_source                      = "vnic"
          cdn_values                      = []
          enable_failover                 = false
          ethernet_adapter_policy         = ""
          ethernet_network_control_policy = ""
          ethernet_network_group_policy   = ""
          ethernet_network_policy         = ""
          ethernet_qos_policy             = ""
          iscsi_boot_policy               = ""
          mac_address_allocation_type     = "POOL"
          mac_address_pools               = []
          mac_addresses_static            = []
          placement_pci_links = [
            0,
          ]
          placement_pci_orders = [
            2,
            3,
          ]
          placement_slot_ids = [
            "MLOM",
          ]
          placement_switch_id = ""
          placement_uplink_ports = [
            0,
          ]
          usnic_adapter_policy                   = ""
          usnic_class_of_service                 = 5
          usnic_number_of_usnics                 = 0
          vmq_enable_virtual_machine_multi_queue = false
          vmq_enabled                            = false
          vmq_number_of_interrupts               = 16
          vmq_number_of_sub_vnics                = 64
          vmq_number_of_virtual_machine_queues   = 4
          vmq_vmmq_adapter_policy                = ""
        }
      }
      ldap = {
        base_settings = {
          timeout = 0
        }
        binding_parameters = {
          bind_dn     = ""
          bind_method = "LoginCredentials"
        }
        enable_encryption          = false
        enable_group_authorization = false
        enable_ldap                = true
        ldap_from_dns = {
          enable        = false
          search_domain = ""
          search_forest = ""
          source        = "Extracted"
        }
        name_suffix               = ""
        nested_group_search_depth = 128
        search_parameters = {
          attribute       = "CiscoAvPair"
          filter          = "samAccountName"
          group_attribute = "memberOf"
        }
        timeout                = 0
        user_search_precedence = "LocalUserDb"
      }
      link_aggregation = {
        lacp_rate          = "normal"
        name_suffix        = ""
        suspend_individual = false
      }
      link_control = {
        admin_state = "Enabled"
        mode        = "normal"
        name_suffix = ""
      }
      local_user = {
        always_send_user_password = false
        enable_password_expiry    = false
        enforce_strong_password   = true
        grace_period              = 0
        name_suffix               = ""
        notification_period       = 15
        password_expiry_duration  = 90
        password_history          = 5
      }
      multicast = {
        name_suffix             = ""
        querier_ip_address      = ""
        querier_ip_address_peer = ""
        querier_state           = "Disabled"
        snooping_state          = "Enabled"
      }
      network_connectivity = {
        dns_servers_v4 = [
          "208.67.220.220",
          "208.67.222.222",
        ]
        dns_servers_v6            = []
        enable_dynamic_dns        = false
        enable_ipv6               = false
        name_suffix               = ""
        obtain_ipv4_dns_from_dhcp = false
        obtain_ipv6_dns_from_dhcp = false
        tags                      = []
        update_domain             = ""
      }
      ntp = {
        enabled     = true
        name_suffix = ""
        ntp_servers = [
          "time-a-g.nist.gov",
          "time-b-g.nist.gov",
        ]
        tags     = []
        timezone = "Etc/GMT"
      }
      persistent_memory = {
        management_mode        = "configured-from-intersight"
        memory_mode_percentage = 0
        name_suffix            = ""
        namespaces = {
          mode             = "raw"
          socket_id        = 1
          socket_memory_id = "Not Applicable"
        }
        persistent_memory_type = "app-direct"
        retain_namespaces      = true
      }
      port = {
        device_model = "UCS-FI-6454"
        name_suffix  = ""
        port_channel_appliances = {
          admin_speed                     = "Auto"
          ethernet_network_control_policy = ""
          ethernet_network_group_policy   = ""
          mode                            = "trunk"
          priority                        = "Best Effort"
        }
        port_channel_ethernet_uplinks = {
          admin_speed                   = "Auto"
          ethernet_network_group_policy = ""
          flow_control_policy           = ""
          link_aggregation_policy       = ""
          link_control_policy           = ""
        }
        port_channel_fc_uplinks = {
          admin_speed  = "32Gbps"
          fill_pattern = "Arbff"
          vsan_id      = 1
        }
        port_channel_fcoe_uplinks = {
          admin_speed             = "Auto"
          link_aggregation_policy = ""
          link_control_policy     = ""
        }
        port_modes = {
          custom_mode = "FibreChannel"
        }
        port_role_appliances = {
          admin_speed                     = "Auto"
          ethernet_network_control_policy = ""
          ethernet_network_group_policy   = ""
          fec                             = "Auto"
          mode                            = "trunk"
          priority                        = "Best Effort"
        }
        port_role_ethernet_uplinks = {
          admin_speed                   = "Auto"
          ethernet_network_group_policy = ""
          fec                           = "Auto"
          flow_control_policy           = ""
          link_control_policy           = ""
        }
        port_role_fc_storage = {
          admin_speed = "16Gbps"
          vsan_id     = 1
        }
        port_role_fc_uplinks = {
          admin_speed  = "32Gbps"
          fill_pattern = "Arbff"
          vsan_id      = 1
        }
        port_role_fcoe_uplinks = {
          admin_speed         = "Auto"
          fec                 = "Auto"
          link_control_policy = ""
        }
      }
      power = {
        dynamic_power_rebalancing = "Enabled"
        extended_power_capacity   = "Enabled"
        name_suffix               = ""
        power_allocation          = 0
        power_priority            = "Low"
        power_profiling           = "Enabled"
        power_redundancy          = "Grid"
        power_restore             = "LastState"
        power_save_mode           = "Enabled"
      }
      san_connectivity = {
        name_suffix         = ""
        target_platform     = "FIAttached"
        vhba_placement_mode = "custom"
        vhbas = {
          fc_zone_policies               = []
          fibre_channel_adapter_policy   = ""
          fibre_channel_network_policies = []
          fibre_channel_qos_policy       = ""
          persistent_lun_bindings        = false
          placement_pci_link = [
            0,
          ]
          placement_pci_order = [
            0,
            1,
          ]
          placement_slot_id = [
            "MLOM",
          ]
          placement_switch_id = ""
          placement_uplink_port = [
            0,
          ]
          vhba_type            = "fc-initiator"
          wwpn_allocation_type = "POOL"
          wwpn_pools           = []
        }
        wwnn_allocation_type = "POOL"
        wwnn_pool            = ""
      }
      sd_card = {
        enable_diagnostics = false
        enable_drivers     = false
        enable_huu         = false
        enable_os          = false
        enable_scu         = false
        name_suffix        = ""
      }
      serial_over_lan = {
        baud_rate   = 115200
        com_port    = "com0"
        enabled     = true
        name_suffix = ""
        ssh_port    = 2400
      }
      smtp = {
        enable_smtp               = true
        mail_alert_recipients     = []
        minimum_severity          = "critical"
        name_suffix               = ""
        smtp_alert_sender_address = ""
        smtp_port                 = 25
      }
      snmp = {
        enable_snmp           = true
        name_suffix           = ""
        snmp_community_access = "Disabled"
        snmp_engine_input_id  = ""
        snmp_port             = 161
        system_contact        = ""
        system_location       = ""
      }
      ssh = {
        enable_ssh  = true
        name_suffix = ""
        ssh_port    = 22
        ssh_timeout = 1800
      }
      storage = {
        global_hot_spares        = ""
        name_suffix              = ""
        unused_disks_state       = "NoChange"
        use_jbod_for_vd_creation = false
      }
      switch_control = {
        ethernet_switching_mode      = "end-host"
        fc_switching_mode            = "end-host"
        mac_address_table_aging      = "Default"
        mac_aging_time               = 14500
        name_suffix                  = ""
        udld_message_interval        = 15
        udld_recovery_action         = "reset"
        vlan_port_count_optimization = false
      }
      syslog = {
        local_min_severity = "warning"
        name_suffix        = ""
        remote_logging = {
          enable           = false
          hostname         = "0.0.0.0"
          minimum_severity = "warning"
          port             = 514
          protocol         = "udp"
        }
      }
      system_qos = {
        name_suffix = ""
      }
      thermal = {
        fan_control_mode = "Balanced"
        name_suffix      = ""
      }
      virtual_kvm = {
        allow_tunneled_vkvm       = false
        enable_local_server_video = true
        enable_video_encryption   = true
        enable_virtual_kvm        = true
        maximum_sessions          = 4
        name_suffix               = ""
        remote_port               = 2068
      }
      virtual_media = {
        enable_low_power_usb            = true
        enable_virtual_media            = true
        enable_virtual_media_encryption = true
        name_suffix                     = ""
      }
      vlan = {
        name_suffix = ""
        vlans = {
          auto_allow_on_uplinks = false
          multicast_policy      = ""
          native_vlan           = false
        }
      }
      vsan = {
        name_suffix     = ""
        uplink_trunking = false
      }
    }
    pools = {
      assignment_order = "sequential"
      ip = {
        ipv4_config = {
          primary_dns = "208.67.220.220"
        }
        ipv6_config = {
          primary_dns = "2620:119:53::53"
        }
        name_suffix = ""
      }
      iqn = {
        iqn_blocks = {
          suffix = "ucs-host"
        }
        name_suffix = ""
        prefix      = ""
      }
      mac = {
        name_suffix = ""
      }
      resource = {
        name_suffix   = ""
        pool_type     = "Static"
        resource_type = "Server"
        server_type   = "Blades"
      }
      uuid = {
        name_suffix = ""
        prefix      = "000025B5-0000-0000"
      }
      wwnn = {
        name_suffix = ""
      }
      wwpn = {
        name_suffix = ""
      }
    }
    profiles = {
      chassis = {
        action              = "No-op"
        domain_type         = "instance"
        name_suffix         = ""
        target_platform     = "FIAttached"
        wait_for_completion = false
      }
      domain = {
        action      = "No-op"
        domain_type = "instance"
        name_suffix = ""
      }
      server = {
        action              = "No-op"
        name_suffix         = ""
        target_platform     = "FIAttached"
        wait_for_completion = false
      }
    }
    tags = [
      {
        key   = "easy-imm"
        value = "1.0.5"
      },
    ]
    templates = {
      server = {
        name_suffix         = ""
        target_platform     = "FIAttached"
        wait_for_completion = false
      }
    }
  }
}
intersight = {
  policies = {
    adapter_configuration = [
      {
        description         = "adapter Adapter Configuration Policy"
        enable_fip          = true
        enable_lldp         = true
        enable_port_channel = true
        fec_mode_1          = "cl91"
        fec_mode_2          = "cl91"
        fec_mode_3          = "cl91"
        fec_mode_4          = "cl91"
        name                = "adapter"
      },
    ]
    bios = [
      {
        description     = "Virtualization_tpm BIOS Policy"
        name            = "Virtualization_tpm"
        policy_template = "Virtualization_tpm"
      },
      {
        description     = "M6_Virtualization_tpm BIOS Policy"
        name            = "M6_Virtualization_tpm"
        policy_template = "M6_Virtualization_tpm"
      },
    ]
    boot_order = [
      {
        boot_devices = [
          {
            name        = "kvm"
            object_type = "boot.VirtualMedia"
            subtype     = "kvm-mapped-dvd"
          },
          {
            name        = "M2"
            object_type = "boot.LocalDisk"
            slot        = "MSTOR-RAID-1"
          },
          {
            interface_name = "mgmt-a"
            name           = "pxe"
            object_type    = "boot.Pxe"
          },
        ]
        boot_mode          = "Uefi"
        description        = "M2 Boot Order Policy"
        enable_secure_boot = false
        name               = "M2"
      },
      {
        boot_devices = [
          {
            name        = "kvm"
            object_type = "boot.VirtualMedia"
            subtype     = "kvm-mapped-dvd"
          },
          {
            name        = "M2"
            object_type = "boot.LocalDisk"
            slot        = "MSTOR-RAID-1"
          },
          {
            name        = "uefishell"
            object_type = "boot.UefiShell"
          },
        ]
        boot_mode          = "Uefi"
        description        = "M2-secure Boot Order Policy"
        enable_secure_boot = true
        name               = "M2-secure"
      },
      {
        boot_devices = [
          {
            name        = "kvm"
            object_type = "boot.VirtualMedia"
            subtype     = "kvm-mapped-dvd"
          },
          {
            name        = "mraid"
            object_type = "boot.LocalDisk"
            slot        = "MRAID"
          },
          {
            name        = "uefishell"
            object_type = "boot.UefiShell"
          },
        ]
        boot_mode          = "Uefi"
        description        = "MRAID Boot Order Policy"
        enable_secure_boot = true
        name               = "MRAID"
      },
    ]
    device_connector = [
      {
        configuration_lockout = false
        description           = "devcon Device Connector Policy"
        name                  = "devcon"
      },
    ]
    ethernet_adapter = [
      {
        description = "VMware Ethernet Adapter"
        name        = "VMware"
      },
    ]
    ethernet_network = [
      {
        default_vlan = "4"
        description  = "network Ethernet Network Policy"
        name         = "network"
        vlan_mode    = "ACCESS"
      },
    ]
    ethernet_network_control = [
      {
        action_on_uplink_fail = "linkDown"
        cdp_enable            = true
        description           = "ntwk-ctrl Ethernet Network Control Policy"
        mac_register_mode     = "nativeVlanOnly"
        mac_security_forge    = "allow"
        name                  = "ntwk-ctrl"
      },
    ]
    ethernet_network_group = [
      {
        allowed_vlans = "1-99"
        description   = "dvs Ethernet Network Group Policy"
        name          = "dvs"
      },
      {
        allowed_vlans = "5"
        description   = "mgmt Ethernet Network Group Policy"
        name          = "mgmt"
        native_vlan   = 5
      },
      {
        allowed_vlans = "6"
        description   = "migration Ethernet Network Group Policy"
        name          = "migration"
        native_vlan   = 6
      },
      {
        allowed_vlans = "7"
        description   = "storage Ethernet Network Group Policy"
        name          = "storage"
        native_vlan   = 7
      },
      {
        action_on_uplink_fail = "linkDown"
        allowed_vlans         = "1-99"
        description           = "Uplink Ethernet Network Group Policy"
        name                  = "uplink"
        native_vlan           = 1
      },
    ]
    ethernet_qos = [
      {
        burst                 = 10240
        description           = "Bronze Ethernet QoS Policy"
        enable_trust_host_cos = false
        mtu                   = 9000
        name                  = "Bronze"
        priority              = "Bronze"
        rate_limit            = 0
      },
      {
        burst                 = 10240
        description           = "Gold Ethernet QoS Policy"
        enable_trust_host_cos = false
        mtu                   = 9000
        name                  = "Gold"
        priority              = "Gold"
        rate_limit            = 0
      },
      {
        burst                 = 10240
        description           = "Platinum Ethernet QoS Policy"
        enable_trust_host_cos = false
        mtu                   = 9000
        name                  = "Platinum"
        priority              = "Platinum"
        rate_limit            = 0
      },
      {
        burst                 = 10240
        description           = "Silver Ethernet QoS Policy"
        enable_trust_host_cos = false
        mtu                   = 9000
        name                  = "Silver"
        priority              = "Silver"
        rate_limit            = 0
      },
    ]
    fc_zone = [
      {
        description           = "vsan-a FC Zone Policy"
        fc_target_zoning_type = "SIMT"
        name                  = "vsan-a"
        targets = [
          {
            name      = "netapp01"
            switch_id = "A"
            vsan_id   = 100
            wwpn      = "50:00:00:25:B5:0A:00:01"
          },
          {
            name      = "pure01"
            switch_id = "A"
            vsan_id   = 100
            wwpn      = "50:00:00:25:B5:0A:00:02"
          },
        ]
      },
      {
        description           = "vsan-b FC Zone Policy"
        fc_target_zoning_type = "SIMT"
        name                  = "vsan-b"
        targets = [
          {
            name      = "netapp01"
            switch_id = "A"
            vsan_id   = 200
            wwpn      = "50:00:00:25:B5:0B:00:01"
          },
          {
            name      = "pure01"
            switch_id = "B"
            vsan_id   = 200
            wwpn      = "50:00:00:25:B5:0B:00:02"
          },
        ]
      },
    ]
    fibre_channel_adapter = [
      {
        description = "VMware Fibre-Channel Adapter Policy"
        name        = "VMware"
      },
    ]
    fibre_channel_network = [
      {
        description = "vsan-a Fibre-Channel Network Policy"
        name        = "vsan-a"
        vsan_id     = 100
      },
      {
        description = "vsan-b Fibre-Channel Network Policy"
        name        = "vsan-b"
        vsan_id     = 200
      },
    ]
    fibre_channel_qos = [
      {
        description = "fc-qos Fibre-Channel QoS Policy"
        name        = "fc-qos"
      },
    ]
    flow_control = [
      {
        description = "flow-ctrl Flow Control Policy"
        name        = "flow-ctrl"
      },
    ]
    imc_access = [
      {
        description                = "kvm IMC Access Policy"
        inband_ip_pool             = "kvm-inband"
        inband_vlan_id             = 4
        ipv4_address_configuration = true
        ipv6_address_configuration = true
        name                       = "kvm"
        out_of_band_ip_pool        = "kvm-oob"
      },
    ]
    ipmi_over_lan = [
      {
        description = "ipmi IPMI over LAN Policy"
        name        = "ipmi"
        privilege   = "admin"
      },
    ]
    iscsi_adapter = [
      {
        description            = "adapter iSCSI Adapter Policy"
        dhcp_timeout           = 60
        lun_busy_retry_count   = 15
        name                   = "adapter"
        tcp_connection_timeout = 15
      },
    ]
    iscsi_boot = [
      {
        authentication          = "chap"
        description             = "boot iSCSI Boot Policy"
        initiator_ip_source     = "DHCP"
        iscsi_adapter_policy    = "adapter"
        name                    = "boot"
        primary_target_policy   = "target"
        secondary_target_policy = ""
        target_source_type      = "Static"
        username                = "iscsiuser"
      },
    ]
    iscsi_static_target = [
      {
        description = "target iSCSI Static Target Policy"
        ip_address  = "198.18.32.60"
        lun = {
          bootable = true
          lun_id   = 0
        }
        name        = "target"
        port        = 3260
        target_name = "iqn.1984-12.com.cisco:lnx1"
      },
    ]
    lan_connectivity = [
      {
        description                 = "lcp LAN Connectivity Policy"
        enable_azure_stack_host_qos = false
        name                        = "lcp"
        target_platform             = "FIAttached"
        vnics = [
          {
            ethernet_adapter_policy         = "VMware"
            ethernet_network_control_policy = "ntwk-ctrl"
            ethernet_network_group_policy   = "mgmt"
            ethernet_qos_policy             = "Silver"
            mac_address_pools = [
              "mac-a",
              "mac-b",
            ]
            names = [
              "mgmt-a",
              "mgmt-b",
            ]
            placement_pci_order = [
              2,
              3,
            ]
          },
          {
            ethernet_adapter_policy         = "VMware"
            ethernet_network_control_policy = "ntwk-ctrl"
            ethernet_network_group_policy   = "migration"
            ethernet_qos_policy             = "Bronze"
            mac_address_pools = [
              "mac-a",
              "mac-b",
            ]
            names = [
              "migration-a",
              "migration-b",
            ]
            placement_pci_order = [
              4,
              5,
            ]
          },
          {
            ethernet_adapter_policy         = "VMware"
            ethernet_network_control_policy = "ntwk-ctrl"
            ethernet_network_group_policy   = "storage"
            ethernet_qos_policy             = "Platinum"
            mac_address_pools = [
              "mac-a",
              "mac-b",
            ]
            names = [
              "storage-a",
              "storage-b",
            ]
            placement_pci_order = [
              6,
              7,
            ]
          },
          {
            ethernet_adapter_policy         = "VMware"
            ethernet_network_control_policy = "ntwk-ctrl"
            ethernet_network_group_policy   = "dvs"
            ethernet_qos_policy             = "Gold"
            mac_address_pools = [
              "mac-a",
              "mac-b",
            ]
            names = [
              "dvs-a",
              "dvs-b",
            ]
            placement_pci_order = [
              8,
              9,
            ]
          },
        ]
      },
    ]
    ldap = [
      {
        base_settings = {
          base_dn = "DC=example,DC=com"
          domain  = "example.com"
          timeout = 0
        }
        binding_parameters = {
          bind_method = "LoginCredentials"
        }
        description                = "ldap LDAP Policy"
        enable_encryption          = true
        enable_group_authorization = true
        enable_ldap                = true
        ldap_groups = [
          {
            group = "ucs-admins"
            role  = "admin"
          },
          {
            group = "netops"
            role  = "user"
          },
        ]
        ldap_servers = [
          {
            port   = 636
            server = "198.18.6.36"
          },
        ]
        name                      = "ldap"
        nested_group_search_depth = 128
        search_parameters = {
          attribute       = "CiscoAvPair"
          filter          = "sAMAccountName"
          group_attribute = "memberOf"
        }
        user_search_precedence = "LocalUserDb"
      },
    ]
    link_aggregation = [
      {
        description = "link-agg Link Aggregation Policy"
        name        = "link-agg"
      },
    ]
    link_control = [
      {
        description = "link-ctrl Link Control Policy"
        name        = "link-ctrl"
      },
    ]
    local_user = [
      {
        description = "users Local User Policy"
        local_users = [
          {
            enabled  = true
            password = 1
            role     = "admin"
            username = "admin"
          },
        ]
        name = "users"
        password_properties = {
          always_send_user_password = false
          enable_password_expiry    = true
          enforce_strong_password   = true
          grace_period              = 0
          notification_period       = 15
          password_expiry_duration  = 90
          password_history          = 0
        }
      },
    ]
    multicast = [
      {
        description = "mcast Multicast Policy"
        name        = "mcast"
      },
    ]
    network_connectivity = [
      {
        alternate_ipv4_dns_server = "208.67.222.222"
        alternate_ipv6_dns_server = "2620:119:35::35"
        description               = "dns Network Connectivity Policy"
        enable_ipv6               = true
        name                      = "dns"
        preferred_ipv4_dns_server = "208.67.220.220"
        preferred_ipv6_dns_server = "2620:119:53::53"
      },
    ]
    ntp = [
      {
        description = "ntp NTP Policy"
        enabled     = true
        name        = "ntp"
        ntp_servers = [
          "0.north-america.pool.ntp.org",
          "1.north-america.pool.ntp.org",
        ]
        timezone = "America/New_York"
      },
    ]
    persistent_memory = [
      {
        description            = "pmem Persistent Memory Policy"
        management_mode        = "configured-from-intersight"
        memory_mode_percentage = "50"
        name                   = "pmem"
        namespaces = [
          {
            capacity         = 1024
            mode             = "raw"
            name             = "cpu0"
            socket_id        = 1
            socket_memory_id = "Not Applicable"
          },
        ]
        persistent_memory_type = "app-direct"
        retain_namespaces      = true
      },
    ]
    port = [
      {
        description  = "default-ucs Port Policy"
        device_model = "UCS-FI-6454"
        names = [
          "default-ucs-a",
          "default-ucs-b",
        ]
        port_channel_ethernet_uplinks = [
          {
            admin_speed                   = "Auto"
            ethernet_network_group_policy = "uplink"
            flow_control_policy           = "flow-ctrl"
            interfaces = [
              {
                port_id = 53
              },
              {
                port_id = 54
              },
            ]
            link_aggregation_policy = "link-agg"
            link_control_policy     = "link-ctrl"
            pc_ids = [
              53,
              53,
            ]
          },
        ]
        port_channel_fc_uplinks = [
          {
            admin_speed  = "32Gbps"
            fill_pattern = "Arbff"
            interfaces = [
              {
                port_id = 1
              },
              {
                port_id = 2
              },
            ]
            pc_ids = [
              1,
              1,
            ]
            vsan_ids = [
              100,
              200,
            ]
          },
        ]
        port_modes = [
          {
            custom_mode = "FibreChannel"
            port_list = [
              1,
              4,
            ]
          },
        ]
        port_role_servers = [
          {
            port_list = "5-18"
          },
        ]
      },
    ]
    power = [
      {
        description      = "5108 Power Policy"
        name             = "5108"
        power_redundancy = "Grid"
      },
      {
        description               = "9508 Power Policy"
        dynamic_power_rebalancing = "Enabled"
        name                      = "9508"
        power_allocation          = 8400
        power_redundancy          = "Grid"
        power_save_mode           = "Enabled"
      },
      {
        description      = "Server Power Policy"
        name             = "Server"
        power_priority   = "Low"
        power_profiling  = "Enabled"
        power_redundancy = "Grid"
        power_restore    = "LastState"
      },
    ]
    san_connectivity = [
      {
        description     = "scp SAN Connectivity Policy"
        name            = "scp"
        target_platform = "FIAttached"
        vhbas = [
          {
            fibre_channel_adapter_policy = "VMware"
            fibre_channel_network_policies = [
              "vsan-a",
              "vsan-b",
            ]
            fibre_channel_qos_policy = "fc-qos"
            names = [
              "vhba-a",
              "vhba-b",
            ]
            placement_pci_order = [
              0,
              1,
            ]
            vhba_type = "fc-initiator"
            wwpn_pools = [
              "wwpn-a",
              "wwpn-b",
            ]
          },
        ]
        wwnn_pool = "wwnn"
      },
    ]
    sd_card = [
      {
        description        = "sdcard SD Card Policy"
        enable_diagnostics = false
        enable_drivers     = false
        enable_huu         = false
        enable_os          = true
        name               = "sdcard"
      },
    ]
    serial_over_lan = [
      {
        baud_rate   = 115200
        com_port    = "com0"
        description = "sol Serial over LAN Policy"
        name        = "sol"
        ssh_port    = 2400
      },
    ]
    smtp = [
      {
        description = "smtp SMTP Policy"
        mail_alert_recipients = [
          "admin@example.com",
          "infra-ops@example.com",
        ]
        minimum_severity          = "critical"
        name                      = "smtp"
        smtp_alert_sender_address = "intersight@example.com"
        smtp_port                 = 25
        smtp_server_address       = "mail.example.com"
      },
    ]
    snmp = [
      {
        description = "snmp SNMP Policy"
        name        = "snmp"
        port        = 161
        snmp_traps = [
          {
            destination_address = "198.18.1.61"
            port                = 162
            user                = "snmpadmin"
          },
        ]
        snmp_users = [
          {
            auth_password    = 1
            auth_type        = "SHA"
            name             = "snmpadmin"
            privacy_password = 1
            privacy_type     = "AES"
            security_level   = "AuthPriv"
          },
        ]
        system_contact  = "admin@example.com"
        system_location = "Example Corporation"
      },
    ]
    ssh = [
      {
        description = "ssh SSH Policy"
        name        = "ssh"
        ssh_port    = 22
        ssh_timeout = 1800
      },
    ]
    storage = [
      {
        description = "M2 Storage Policy"
        m2_configuration = {
          controller_slot = "MSTOR-RAID-1"
          enable          = true
        }
        name                     = "M2"
        unused_disks_state       = "NoChange"
        use_jbod_for_vd_creation = false
      },
      {
        description = "Raid1 Storage Policy"
        drive_groups = [
          {
            manual_drive_group = {
              drive_array_spans = [
                {
                  slots = "1-2"
                },
              ]
              name = "dg0"
            }
            raid_level = "Raid1"
            virtual_drives = [
              {
                boot_drive          = true
                expand_to_available = true
                name                = "vd0"
              },
            ]
          },
        ]
        name                     = "Raid1"
        unused_disks_state       = "Jbod"
        use_jbod_for_vd_creation = true
      },
    ]
    switch_control = [
      {
        description                  = "sw-ctrl Switch Control Policy"
        ethernet_switching_mode      = "end-host"
        fc_switching_mode            = "end-host"
        name                         = "sw-ctrl"
        vlan_port_count_optimization = false
      },
    ]
    syslog = [
      {
        description        = "syslog Syslog Policy"
        local_min_severity = "warning"
        name               = "syslog"
        remote_clients = [
          {
            enable       = true
            hostname     = "198.18.5.14"
            min_severity = "warning"
            port         = 514
            protocol     = "udp"
          },
          {
            enable       = true
            hostname     = "198.18.5.15"
            min_severity = "warning"
            port         = 514
            protocol     = "udp"
          },
        ]
      },
    ]
    system_qos = [
      {
        classes = [
          {
            bandwidth_percent  = 20
            cos                = 20
            mtu                = 9216
            multicast_optimize = false
            packet_drop        = false
            priority           = "Platinum"
            state              = "Enabled"
            weight             = 10
          },
          {
            bandwidth_percent  = 18
            cos                = 18
            mtu                = 9216
            multicast_optimize = false
            packet_drop        = false
            priority           = "Gold"
            state              = "Enabled"
            weight             = 9
          },
          {
            bandwidth_percent  = 20
            cos                = 20
            mtu                = 2240
            multicast_optimize = false
            packet_drop        = false
            priority           = "FC"
            state              = "Enabled"
            weight             = 10
          },
          {
            bandwidth_percent  = 18
            cos                = 18
            mtu                = 9216
            multicast_optimize = false
            packet_drop        = true
            priority           = "Silver"
            state              = "Enabled"
            weight             = 8
          },
          {
            bandwidth_percent  = 14
            cos                = 14
            mtu                = 9216
            multicast_optimize = false
            packet_drop        = true
            priority           = "Bronze"
            state              = "Enabled"
            weight             = 7
          },
          {
            bandwidth_percent  = 10
            cos                = 10
            mtu                = 9216
            multicast_optimize = false
            packet_drop        = false
            priority           = "Best Effort"
            state              = "Enabled"
            weight             = 5
          },
        ]
        description = "qos System QoS Policy"
        name        = "qos"
      },
    ]
    thermal = [
      {
        description      = "5108 Thermal Policy"
        fan_control_mode = "Balanced"
        name             = "5108"
      },
      {
        description      = "9508 Thermal Policy"
        fan_control_mode = "Balanced"
        name             = "9508"
      },
    ]
    virtual_kvm = [
      {
        allow_tunneled_vkvm       = false
        description               = "vkvm Virtual KVM Policy"
        enable_local_server_video = true
        enable_video_encryption   = true
        name                      = "vkvm"
        remote_port               = 2068
      },
    ]
    virtual_media = [
      {
        add_virtual_media = [
          {
            device_type   = "cdd"
            file_location = "https://198.18.1.1/vmware.iso"
            mount_options = "noauto"
            name          = "https-map"
            protocol      = "https"
          },
        ]
        description                     = "vmedia Virtual Media Policy"
        enable_low_power_usb            = true
        enable_virtual_media_encryption = true
        name                            = "vmedia"
      },
    ]
    vlan = [
      {
        auto_allow_on_uplinks = true
        description           = "vlans VLAN Policy"
        name                  = "vlans"
        vlans = [
          {
            multicast_policy = "mcast"
            name             = "default"
            vlan_list        = "1-99"
          },
        ]
      },
      {
        description = "vlan VLAN Policy"
        name        = "vlan"
        vlans = [
          {
            auto_allow_on_uplinks = true
            multicast_policy      = "mcast"
            name                  = "default"
            native_vlan           = true
            vlan_list             = "1"
          },
          {
            multicast_policy = "mcast"
            name             = "default"
            vlan_list        = "2-99"
          },
        ]
      },
    ]
    vsan = [
      {
        auto_allow_on_uplinks = true
        description           = "vsan-100 VSAN Policy"
        name                  = "vsan-100"
        vsans = [
          {
            fcoe_vlan_id = 100
            name         = "vsan-100"
            vsan_id      = 100
            vsan_scope   = "Uplink"
          },
        ]
      },
      {
        auto_allow_on_uplinks = true
        description           = "vsan-200 VSAN Policy"
        name                  = "vsan-200"
        vsans = [
          {
            fcoe_vlan_id = 200
            name         = "vsan-200"
            vsan_id      = 200
            vsan_scope   = "Uplink"
          },
        ]
      },
    ]
  }
  pools = {
    ip = [
      {
        assignment_order = "sequential"
        description      = "kvm IP Pool"
        ipv4_blocks = [
          {
            from = "198.18.1.10"
            size = 244
          },
        ]
        ipv4_configuration = {
          gateway       = "198.18.1.1"
          netmask       = "255.255.255.0"
          primary_dns   = "208.67.220.220"
          secondary_dns = ""
        }
        ipv6_blocks = [
          {
            from = "2001:db8::a"
            size = 1024
          },
        ]
        ipv6_configuration = {
          gateway       = "2001:db8::1"
          prefix        = 64
          primary_dns   = "2620:119:53::53"
          secondary_dns = "2620:119:35::35"
        }
        name = "kvm-inband"
      },
      {
        assignment_order = "sequential"
        description      = "kvm IP Pool"
        ipv4_blocks = [
          {
            from = "198.18.2.10"
            size = 244
          },
        ]
        ipv4_configuration = {
          gateway       = "198.18.2.1"
          netmask       = "255.255.255.0"
          primary_dns   = "208.67.220.220"
          secondary_dns = "208.67.222.222"
        }
        name = "kvm-oob"
      },
    ]
    mac = [
      {
        assignment_order = "sequential"
        description      = "mac-a MAC Pool"
        mac_blocks = [
          {
            from = "00:25:B5:0A:00:00"
            size = 1024
          },
        ]
        name = "mac-a"
      },
      {
        assignment_order = "sequential"
        description      = "mac-b MAC Pool"
        mac_blocks = [
          {
            from = "00:25:B5:0B:00:00"
            size = 1024
          },
        ]
        name = "mac-b"
      },
    ]
    uuid = [
      {
        assignment_order = "sequential"
        description      = "uuid UUID Pool"
        name             = "uuid"
        prefix           = "000025B5-0000-0000"
        uuid_blocks = [
          {
            from = "0000-000000000000"
            size = 1024
          },
        ]
      },
    ]
    wwnn = [
      {
        assignment_order = "sequential"
        description      = "wwnn WWNN Pool"
        name             = "wwnn"
        wwnn_blocks = [
          {
            from = "20:00:00:25:B5:00:00:00"
            size = 1024
          },
        ]
      },
    ]
    wwpn = [
      {
        assignment_order = "sequential"
        description      = "wwpn-a WWPN Pool"
        name             = "wwpn-a"
        wwpn_blocks = [
          {
            from = "20:00:00:25:B5:0A:00:00"
            size = 1024
          },
        ]
      },
      {
        assignment_order = "sequential"
        description      = "wwpn-b WWPN Pool"
        name             = "wwpn-b"
        wwpn_blocks = [
          {
            from = "20:00:00:25:B5:0B:00:00"
            size = 1024
          },
        ]
      },
    ]
  }
  profiles = {
    chassis = [
      {
        imc_access_policy = "kvm"
        power_policy      = "9508"
        snmp_policy       = "snmp"
        targets = [
          {
            description = "example-ucs-1 UCS Chassis Profile"
            name        = "example-ucs-1"
            serial      = "unknown"
          },
          {
            name   = "example-ucs-2"
            serial = "unknown"
          },
          {
            name   = "example-ucs-3"
            serial = "unknown"
          },
        ]
        thermal_policy = "9508"
      },
    ]
    domain = [
      {
        description                 = "example-ucs UCS Domain Profile"
        name                        = "example-ucs"
        network_connectivity_policy = "dns"
        ntp_policy                  = "ntp"
        port_policies = [
          "example-ucs-a",
          "example-ucs-b",
        ]
        serials = [
          "unknown",
          "unknown",
        ]
        snmp_policy           = "snmp"
        switch_control_policy = "sw-ctrl"
        syslog_policy         = "syslog"
        system_qos_policy     = "qos"
        vlan_policies = [
          "vlans",
        ]
        vsan_policies = [
          "vsan-200",
          "vsan-100",
        ]
      },
    ]
    server = [
      {
        targets = [
          {
            description = "esx-1 UCS Server Profile"
            name        = "esx-1"
            serial      = "unknown"
          },
          {
            description = "esx-2 UCS Server Profile"
            name        = "esx-2"
            serial      = "unknown"
          },
          {
            name   = "esx-3"
            serial = "unknown"
          },
          {
            name   = "esx-4"
            serial = "unknown"
          },
        ]
        ucs_server_profile_template = "virtualization"
      },
      {
        names_serials = [
          [
            "esx01",
          ],
          [
            "esx02",
          ],
          [
            "esx03",
          ],
        ]
        ucs_server_profile_template = "Virtualization-M2-pxe"
      },
    ]
  }
  templates = {
    server = [
      {
        bios_policy             = "M6_Virtualization_tpm"
        boot_order_policy       = "M2-secure"
        description             = "virtualization UCS Server Profile Template"
        imc_access_policy       = "kvm"
        ipmi_over_lan_policy    = "ipmi"
        lan_connectivity_policy = "lcp"
        local_user_policy       = "users"
        name                    = "virtualization"
        power_policy            = "Server"
        san_connectivity_policy = "scp"
        serial_over_lan_policy  = "sol"
        snmp_policy             = "snmp"
        storage_policy          = "M2"
        syslog_policy           = "syslog"
        uuid_pool               = "uuid"
        virtual_kvm_policy      = "vkvm"
        virtual_media_policy    = "vmedia"
      },
      {
        bios_policy                   = "Virtualization-M6"
        boot_order_policy             = "M2-pxe"
        certificate_management_policy = ""
        imc_access_policy             = "imc"
        ipmi_over_lan_policy          = "ipmi"
        lan_connectivity_policy       = "Virtualization"
        local_user_policy             = "users"
        name                          = "Virtualization-M2-pxe"
        power_policy                  = "server"
        san_connectivity_policy       = "Virtualization"
        sd_card_policy                = ""
        serial_over_lan_policy        = "sol"
        snmp_policy                   = "snmp"
        storage_policy                = "M2"
        syslog_policy                 = "syslog"
        tags                          = []
        uuid_pool                     = "uuid"
        virtual_kvm_policy            = "vkvm"
        virtual_media_policy          = "vmedia"
      },
    ]
  }
}