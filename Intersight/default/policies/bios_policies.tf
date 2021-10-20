#_________________________________________________________________________
#
# Intersight BIOS Policies Variables
# GUI Location: Configure > Policies > Create Policy > BIOS > Start
#_________________________________________________________________________

variable "bios_policies" {
  default = {
    default = {
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
      bios_template                         = ""
      bme_dma_mitigation                    = "platform-default"
      boot_option_num_retry                 = "platform-default"
      boot_option_re_cool_down              = "platform-default"
      boot_option_retry                     = "platform-default"
      boot_performance_mode                 = "platform-default"
      burst_and_postponed_refresh           = "platform-default"
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
      cpu_performance                       = "platform-default"
      cpu_power_management                  = "platform-default"
      cr_qos                                = "platform-default"
      crfastgo_config                       = "platform-default"
      dcpmm_firmware_downgrade              = "platform-default"
      demand_scrub                          = "platform-default"
      description                           = ""
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
      network_stack                         = "platform-default"
      numa_optimized                        = "platform-default"
      nvmdimm_perform_config                = "platform-default"
      onboard_gbit_lom                      = "platform-default"
      onboard_scu_storage_support           = "platform-default"
      onboard_scu_storage_sw_stack          = "platform-default"
      onboard10gbit_lom                     = "platform-default"
      operation_mode                        = "platform-default"
      organization                          = "default"
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
      single_pctl_enable                    = "platform-default"
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
      smee                                  = "platform-default"
      smt_mode                              = "platform-default"
      snc                                   = "platform-default"
      snoopy_mode_for_ad                    = "platform-default"
      snoopy_mode_for2lm                    = "platform-default"
      sparing_mode                          = "platform-default"
      sr_iov                                = "platform-default"
      streamer_prefetch                     = "platform-default"
      svm_mode                              = "platform-default"
      tags                                  = []
      terminal_type                         = "platform-default"
      tpm_control                           = "platform-default"
      tpm_pending_operation                 = "platform-default"
      tpm_support                           = "platform-default"
      tsme                                  = "platform-default"
      txt_support                           = "platform-default"
      ucsm_boot_order_rule                  = "platform-default"
      ufs_disable                           = "platform-default"
      uma_based_clustering                  = "platform-default"
      usb_emul6064                          = "platform-default"
      usb_port_front                        = "platform-default"
      usb_port_internal                     = "platform-default"
      usb_port_kvm                          = "platform-default"
      usb_port_rear                         = "platform-default"
      usb_port_sd_card                      = "platform-default"
      usb_port_vmedia                       = "platform-default"
      usb_xhci_support                      = "platform-default"
      vga_priority                          = "platform-default"
      vmd_enable                            = "platform-default"
      vol_memory_mode                       = "platform-default"
      work_load_config                      = "platform-default"
      xpt_prefetch                          = "platform-default"
    }
  }
  description = <<-EOT
  Intersight BIOS Variable Map.
  key - Name of the BIOS Policy
  *  description - Description to Assign to the Policy.
  * organization - Name of the Intersight Organization to assign this BIOS Policy to:
    - https://intersight.com/an/settings/organizations/
  *  tags - List of Key/Value Pairs to Assign as Attributes to the Policy.
  * acs_control_gpu1state - default is "platform-default".  BIOS Token for setting ACS Control GPU 1 configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * acs_control_gpu2state - default is "platform-default".  BIOS Token for setting ACS Control GPU 2 configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * acs_control_gpu3state - default is "platform-default".  BIOS Token for setting ACS Control GPU 3 configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * acs_control_gpu4state - default is "platform-default".  BIOS Token for setting ACS Control GPU 4 configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * acs_control_gpu5state - default is "platform-default".  BIOS Token for setting ACS Control GPU 5 configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * acs_control_gpu6state - default is "platform-default".  BIOS Token for setting ACS Control GPU 6 configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * acs_control_gpu7state - default is "platform-default".  BIOS Token for setting ACS Control GPU 7 configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * acs_control_gpu8state - default is "platform-default".  BIOS Token for setting ACS Control GPU 8 configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * acs_control_slot11state - default is "platform-default".  BIOS Token for setting ACS Control Slot 11 configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * acs_control_slot12state - default is "platform-default".  BIOS Token for setting ACS Control Slot 12 configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * acs_control_slot13state - default is "platform-default".  BIOS Token for setting ACS Control Slot 13 configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * acs_control_slot14state - default is "platform-default".  BIOS Token for setting ACS Control Slot 14 configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * adjacent_cache_line_prefetch - default is "platform-default".  BIOS Token for setting Adjacent Cache Line Prefetcher configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * advanced_mem_test - default is "platform-default".  BIOS Token for setting Enhanced Memory Test configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring AdvancedMemTest token.
    - disabled - Value - disabled for configuring AdvancedMemTest token.
    - enabled - Value - enabled for configuring AdvancedMemTest token.
  * all_usb_devices - default is "platform-default".  BIOS Token for setting All USB Devices configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * altitude - default is "platform-default".  BIOS Token for setting Altitude configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 300-m - Value - 300-m for configuring Altitude token.
    - 900-m - Value - 900-m for configuring Altitude token.
    - 1500-m - Value - 1500-m for configuring Altitude token.
    - 3000-m - Value - 3000-m for configuring Altitude token.
    - auto - Value - auto for configuring Altitude token.
  * aspm_support - default is "platform-default".  BIOS Token for setting ASPM Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring AspmSupport token.
    - disabled - Value - Disabled for configuring AspmSupport token.
    - Force L0s - Value - Force L0s for configuring AspmSupport token.
    - L1 Only - Value - L1 Only for configuring AspmSupport token.
  * assert_nmi_on_perr - default is "platform-default".  BIOS Token for setting Assert NMI on PERR configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * assert_nmi_on_serr - default is "platform-default".  BIOS Token for setting Assert NMI on SERR configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * auto_cc_state - default is "platform-default".  BIOS Token for setting Autonomous Core C State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * autonumous_cstate_enable - default is "platform-default".  BIOS Token for setting CPU Autonomous C State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * baud_rate - default is "platform-default".  BIOS Token for setting Baud Rate configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 9600 - Value - 9600 for configuring BaudRate token.
    - 19200 - Value - 19200 for configuring BaudRate token.
    - 38400 - Value - 38400 for configuring BaudRate token.
    - 57600 - Value - 57600 for configuring BaudRate token.
    - 115200 - Value - 115200 for configuring BaudRate token.
  * bios_template - Name of a BIOS Template to Configure.  Options are:
    - DSS - Analytics Database Systems.
    - HPC - High-Performance Computing.
    - Java - Java Application Servers.
    - OLTP - Online Transaction Processing
    - Virtualization - VMware.
  * bme_dma_mitigation - default is "platform-default".  BIOS Token for setting BME DMA Mitigation configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * boot_option_num_retry - default is "platform-default".  BIOS Token for setting Number of Retries configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 5 - Value - 5 for configuring BootOptionNumRetry token.
    - 13 - Value - 13 for configuring BootOptionNumRetry token.
    - Infinite - Value - Infinite for configuring BootOptionNumRetry token.
  * boot_option_re_cool_down - default is "platform-default".  BIOS Token for setting Cool Down Time (sec) configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 15 - Value - 15 for configuring BootOptionReCoolDown token.
    - 45 - Value - 45 for configuring BootOptionReCoolDown token.
    - 90 - Value - 90 for configuring BootOptionReCoolDown token.
  * boot_option_retry - default is "platform-default".  BIOS Token for setting Boot Option Retry configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * boot_performance_mode - default is "platform-default".  BIOS Token for setting Boot Performance Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Max Efficient - Value - Max Efficient for configuring BootPerformanceMode token.
    - Max Performance - Value - Max Performance for configuring BootPerformanceMode token.
    - Set by Intel NM - Value - Set by Intel NM for configuring BootPerformanceMode token.
  * burst_and_postponed_refresh - default is "platform-default".  BIOS Token for setting Burst and Postponed Refresh configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * cbs_cmn_apbdis - default is "platform-default".  BIOS Token for setting APBDIS configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 0 - Value - 0 for configuring CbsCmnApbdis token.
    - 1 - Value - 1 for configuring CbsCmnApbdis token.
    - Auto - Value - Auto for configuring CbsCmnApbdis token.
  * cbs_cmn_cpu_cpb - default is "platform-default".  BIOS Token for setting Core Performance Boost configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnCpuCpb token.
    - disabled - Value - disabled for configuring CbsCmnCpuCpb token.
  * cbs_cmn_cpu_gen_downcore_ctrl - default is "platform-default".  BIOS Token for setting Downcore Control configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnCpuGenDowncoreCtrl token.
    - FOUR (2 + 2) - Value - FOUR (2 + 2) for configuring CbsCmnCpuGenDowncoreCtrl token.
    - FOUR (4 + 0) - Value - FOUR (4 + 0) for configuring CbsCmnCpuGenDowncoreCtrl token.
    - SIX (3 + 3) - Value - SIX (3 + 3) for configuring CbsCmnCpuGenDowncoreCtrl token.
    - THREE (3 + 0) - Value - THREE (3 + 0) for configuring CbsCmnCpuGenDowncoreCtrl token.
    - TWO (1 + 1) - Value - TWO (1 + 1) for configuring CbsCmnCpuGenDowncoreCtrl token.
    - TWO (2 + 0) - Value - TWO (2 + 0) for configuring CbsCmnCpuGenDowncoreCtrl token.
  * cbs_cmn_cpu_global_cstate_ctrl - default is "platform-default".  BIOS Token for setting Global C State Control configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnCpuGlobalCstateCtrl token.
    - disabled - Value - disabled for configuring CbsCmnCpuGlobalCstateCtrl token.
    - enabled - Value - enabled for configuring CbsCmnCpuGlobalCstateCtrl token.
  * cbs_cmn_cpu_l1stream_hw_prefetcher - default is "platform-default".  BIOS Token for setting L1 Stream HW Prefetcher configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnCpuL1streamHwPrefetcher token.
    - disabled - Value - disabled for configuring CbsCmnCpuL1streamHwPrefetcher token.
    - enabled - Value - enabled for configuring CbsCmnCpuL1streamHwPrefetcher token.
  * cbs_cmn_cpu_l2stream_hw_prefetcher - default is "platform-default".  BIOS Token for setting L2 Stream HW Prefetcher configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnCpuL2streamHwPrefetcher token.
    - disabled - Value - disabled for configuring CbsCmnCpuL2streamHwPrefetcher token.
    - enabled - Value - enabled for configuring CbsCmnCpuL2streamHwPrefetcher token.
  * cbs_cmn_cpu_smee - default is "platform-default".  BIOS Token for setting CPU SMEE configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnCpuSmee token.
    - disabled - Value - disabled for configuring CbsCmnCpuSmee token.
    - enabled - Value - enabled for configuring CbsCmnCpuSmee token.
  * cbs_cmn_cpu_streaming_stores_ctrl - default is "platform-default".  BIOS Token for setting Streaming Stores Control configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnCpuStreamingStoresCtrl token.
    - disabled - Value - disabled for configuring CbsCmnCpuStreamingStoresCtrl token.
    - enabled - Value - enabled for configuring CbsCmnCpuStreamingStoresCtrl token.
  * cbs_cmn_determinism_slider - default is "platform-default".  BIOS Token for setting Determinism Slider configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnDeterminismSlider token.
    - Performance - Value - Performance for configuring CbsCmnDeterminismSlider token.
    - Power - Value - Power for configuring CbsCmnDeterminismSlider token.
  * cbs_cmn_efficiency_mode_en - default is "platform-default".  BIOS Token for setting Efficiency Mode Enable configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnEfficiencyModeEn token.
    - enabled - Value - Enabled for configuring CbsCmnEfficiencyModeEn token.
  * cbs_cmn_fixed_soc_pstate - default is "platform-default".  BIOS Token for setting Fixed SOC P-State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnFixedSocPstate token.
    - P0 - Value - P0 for configuring CbsCmnFixedSocPstate token.
    - P1 - Value - P1 for configuring CbsCmnFixedSocPstate token.
    - P2 - Value - P2 for configuring CbsCmnFixedSocPstate token.
    - P3 - Value - P3 for configuring CbsCmnFixedSocPstate token.
  * cbs_cmn_gnb_nb_iommu - default is "platform-default".  BIOS Token for setting IOMMU configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnGnbNbIommu token.
    - disabled - Value - disabled for configuring CbsCmnGnbNbIommu token.
    - enabled - Value - enabled for configuring CbsCmnGnbNbIommu token.
  * cbs_cmn_gnb_smu_df_cstates - default is "platform-default".  BIOS Token for setting DF C-States configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnGnbSmuDfCstates token.
    - disabled - Value - disabled for configuring CbsCmnGnbSmuDfCstates token.
    - enabled - Value - enabled for configuring CbsCmnGnbSmuDfCstates token.
  * cbs_cmn_gnb_smucppc - default is "platform-default".  BIOS Token for setting CPPC configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnGnbSmucppc token.
    - disabled - Value - disabled for configuring CbsCmnGnbSmucppc token.
    - enabled - Value - enabled for configuring CbsCmnGnbSmucppc token.
  * cbs_cmn_mem_ctrl_bank_group_swap_ddr4 - default is "platform-default".  BIOS Token for setting Bank Group Swap configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnMemCtrlBankGroupSwapDdr4 token.
    - disabled - Value - disabled for configuring CbsCmnMemCtrlBankGroupSwapDdr4 token.
    - enabled - Value - enabled for configuring CbsCmnMemCtrlBankGroupSwapDdr4 token.
  * cbs_cmn_mem_map_bank_interleave_ddr4 - default is "platform-default".  BIOS Token for setting Chipset Interleave configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmnMemMapBankInterleaveDdr4 token.
    - disabled - Value - disabled for configuring CbsCmnMemMapBankInterleaveDdr4 token.
  * cbs_cmnc_tdp_ctl - default is "platform-default".  BIOS Token for setting cTDP Control configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCmncTdpCtl token.
    - Manual - Value - Manual for configuring CbsCmncTdpCtl token.
  * cbs_cpu_ccd_ctrl_ssp - default is "platform-default".  BIOS Token for setting CCD Control configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 2 CCDs - Value - 2 CCDs for configuring CbsCpuCcdCtrlSsp token.
    - 3 CCDs - Value - 3 CCDs for configuring CbsCpuCcdCtrlSsp token.
    - 4 CCDs - Value - 4 CCDs for configuring CbsCpuCcdCtrlSsp token.
    - 6 CCDs - Value - 6 CCDs for configuring CbsCpuCcdCtrlSsp token.
    - Auto - Value - Auto for configuring CbsCpuCcdCtrlSsp token.
  * cbs_cpu_core_ctrl - default is "platform-default".  BIOS Token for setting CPU Downcore control configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCpuCoreCtrl token.
    - FIVE (5 + 0) - Value - FIVE (5 + 0) for configuring CbsCpuCoreCtrl token.
    - FOUR (4 + 0) - Value - FOUR (4 + 0) for configuring CbsCpuCoreCtrl token.
    - ONE (1 + 0) - Value - ONE (1 + 0) for configuring CbsCpuCoreCtrl token.
    - SEVEN (7 + 0) - Value - SEVEN (7 + 0) for configuring CbsCpuCoreCtrl token.
    - SIX (6 + 0) - Value - SIX (6 + 0) for configuring CbsCpuCoreCtrl token.
    - THREE (3 + 0) - Value - THREE (3 + 0) for configuring CbsCpuCoreCtrl token.
    - TWO (2 + 0) - Value - TWO (2 + 0) for configuring CbsCpuCoreCtrl token.
  * cbs_cpu_smt_ctrl - default is "platform-default".  BIOS Token for setting CPU SMT Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsCpuSmtCtrl token.
    - disabled - Value - disabled for configuring CbsCpuSmtCtrl token.
    - enabled - Value - enabled for configuring CbsCpuSmtCtrl token.
  * cbs_dbg_cpu_snp_mem_cover - default is "platform-default".  BIOS Token for setting SNP Memory Coverage configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsDbgCpuSnpMemCover token.
    - Custom - Value - Custom for configuring CbsDbgCpuSnpMemCover token.
    - disabled - Value - disabled for configuring CbsDbgCpuSnpMemCover token.
    - enabled - Value - enabled for configuring CbsDbgCpuSnpMemCover token.
  * cbs_dbg_cpu_snp_mem_size_cover - default is "platform-default".  BIOS Token for setting SNP Memory Size to Cover in MiB configuration (0 - 1048576 MiB).
  * cbs_df_cmn_acpi_srat_l3numa - default is "platform-default".  BIOS Token for setting ACPI SRAT L3 Cache As NUMA Domain configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsDfCmnAcpiSratL3numa token.
    - disabled - Value - disabled for configuring CbsDfCmnAcpiSratL3numa token.
    - enabled - Value - enabled for configuring CbsDfCmnAcpiSratL3numa token.
  * cbs_df_cmn_dram_nps - default is "platform-default".  BIOS Token for setting NUMA Nodes per Socket configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsDfCmnDramNps token.
    - NPS0 - Value - NPS0 for configuring CbsDfCmnDramNps token.
    - NPS1 - Value - NPS1 for configuring CbsDfCmnDramNps token.
    - NPS2 - Value - NPS2 for configuring CbsDfCmnDramNps token.
    - NPS4 - Value - NPS4 for configuring CbsDfCmnDramNps token.
  * cbs_df_cmn_mem_intlv - default is "platform-default".  BIOS Token for setting AMD Memory Interleaving configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CbsDfCmnMemIntlv token.
    - Channel - Value - Channel for configuring CbsDfCmnMemIntlv token.
    - Die - Value - Die for configuring CbsDfCmnMemIntlv token.
    - None - Value - None for configuring CbsDfCmnMemIntlv token.
    - Socket - Value - Socket for configuring CbsDfCmnMemIntlv token.
  * cbs_df_cmn_mem_intlv_size - default is "platform-default".  BIOS Token for setting AMD Memory Interleaving Size configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 256 Bytes - Value - 256 Bytes for configuring CbsDfCmnMemIntlvSize token.
    - 512 Bytes - Value - 512 Bytes for configuring CbsDfCmnMemIntlvSize token.
    - 1 KB - Value - 1 KiB for configuring CbsDfCmnMemIntlvSize token.
    - 2 KB - Value - 2 KiB for configuring CbsDfCmnMemIntlvSize token.
    - 4 KB - Value - 4 KiB for configuring CbsDfCmnMemIntlvSize token.
    - Auto - Value - Auto for configuring CbsDfCmnMemIntlvSize token.
  * cbs_sev_snp_support - default is "platform-default".  BIOS Token for setting SEV-SNP Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * cdn_enable - default is "platform-default".  BIOS Token for setting Consistent Device Naming configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * cdn_support - default is "platform-default".  BIOS Token for setting CDN Support for LOM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring CdnSupport token.
    - enabled - Value - enabled for configuring CdnSupport token.
    - LOMs Only - Value - LOMs Only for configuring CdnSupport token.
  * channel_inter_leave - default is "platform-default".  BIOS Token for setting Channel Interleaving configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 1-way - Value - 1-way for configuring ChannelInterLeave token.
    - 2-way - Value - 2-way for configuring ChannelInterLeave token.
    - 3-way - Value - 3-way for configuring ChannelInterLeave token.
    - 4-way - Value - 4-way for configuring ChannelInterLeave token.
    - auto - Value - auto for configuring ChannelInterLeave token.
  * cisco_adaptive_mem_training - default is "platform-default".  BIOS Token for setting Adaptive Memory Training configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * cisco_debug_level - default is "platform-default".  BIOS Token for setting BIOS Techlog Level configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Maximum - Value - Maximum for configuring CiscoDebugLevel token.
    - Minimum - Value - Minimum for configuring CiscoDebugLevel token.
    - Normal - Value - Normal for configuring CiscoDebugLevel token.
  * cisco_oprom_launch_optimization - default is "platform-default".  BIOS Token for setting OptionROM Launch Optimization configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * cisco_xgmi_max_speed - default is "platform-default".  BIOS Token for setting Cisco xGMI Max Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * cke_low_policy - default is "platform-default".  BIOS Token for setting CKE Low Policy configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - auto - Value - auto for configuring CkeLowPolicy token.
    - disabled - Value - disabled for configuring CkeLowPolicy token.
    - fast - Value - fast for configuring CkeLowPolicy token.
    - slow - Value - slow for configuring CkeLowPolicy token.
  * closed_loop_therm_throtl - default is "platform-default".  BIOS Token for setting Closed Loop Thermal Throttling configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * cmci_enable - default is "platform-default".  BIOS Token for setting Processor CMCI configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * config_tdp - default is "platform-default".  BIOS Token for setting Config TDP configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * config_tdp_level - default is "platform-default".  BIOS Token for setting Configurable TDP Level configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Level 1 - Value - Level 1 for configuring ConfigTdpLevel token.
    - Level 2 - Value - Level 2 for configuring ConfigTdpLevel token.
    - Normal - Value - Normal for configuring ConfigTdpLevel token.
  * console_redirection - default is "platform-default".  BIOS Token for setting Console Redirection configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - com-0 - Value - com-0 for configuring ConsoleRedirection token.
    - com-1 - Value - com-1 for configuring ConsoleRedirection token.
    - disabled - Value - disabled for configuring ConsoleRedirection token.
    - enabled - Value - enabled for configuring ConsoleRedirection token.
    - serial-port-a - Value - serial-port-a for configuring ConsoleRedirection token.
  * core_multi_processing - default is "platform-default".  BIOS Token for setting Core Multi Processing configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 1 - Value - 1 for configuring CoreMultiProcessing token.
    - 2 - Value - 2 for configuring CoreMultiProcessing token.
    - 3 - Value - 3 for configuring CoreMultiProcessing token.
    - 4 - Value - 4 for configuring CoreMultiProcessing token.
    - 5 - Value - 5 for configuring CoreMultiProcessing token.
    - 6 - Value - 6 for configuring CoreMultiProcessing token.
    - 7 - Value - 7 for configuring CoreMultiProcessing token.
    - 8 - Value - 8 for configuring CoreMultiProcessing token.
    - 9 - Value - 9 for configuring CoreMultiProcessing token.
    - 10 - Value - 10 for configuring CoreMultiProcessing token.
    - 11 - Value - 11 for configuring CoreMultiProcessing token.
    - 12 - Value - 12 for configuring CoreMultiProcessing token.
    - 13 - Value - 13 for configuring CoreMultiProcessing token.
    - 14 - Value - 14 for configuring CoreMultiProcessing token.
    - 15 - Value - 15 for configuring CoreMultiProcessing token.
    - 16 - Value - 16 for configuring CoreMultiProcessing token.
    - 17 - Value - 17 for configuring CoreMultiProcessing token.
    - 18 - Value - 18 for configuring CoreMultiProcessing token.
    - 19 - Value - 19 for configuring CoreMultiProcessing token.
    - 20 - Value - 20 for configuring CoreMultiProcessing token.
    - 21 - Value - 21 for configuring CoreMultiProcessing token.
    - 22 - Value - 22 for configuring CoreMultiProcessing token.
    - 23 - Value - 23 for configuring CoreMultiProcessing token.
    - 24 - Value - 24 for configuring CoreMultiProcessing token.
    - 25 - Value - 25 for configuring CoreMultiProcessing token.
    - 26 - Value - 26 for configuring CoreMultiProcessing token.
    - 27 - Value - 27 for configuring CoreMultiProcessing token.
    - 28 - Value - 28 for configuring CoreMultiProcessing token.
    - 29 - Value - 29 for configuring CoreMultiProcessing token.
    - 30 - Value - 30 for configuring CoreMultiProcessing token.
    - 31 - Value - 31 for configuring CoreMultiProcessing token.
    - 32 - Value - 32 for configuring CoreMultiProcessing token.
    - 33 - Value - 33 for configuring CoreMultiProcessing token.
    - 34 - Value - 34 for configuring CoreMultiProcessing token.
    - 35 - Value - 35 for configuring CoreMultiProcessing token.
    - 36 - Value - 36 for configuring CoreMultiProcessing token.
    - 37 - Value - 37 for configuring CoreMultiProcessing token.
    - 38 - Value - 38 for configuring CoreMultiProcessing token.
    - 39 - Value - 39 for configuring CoreMultiProcessing token.
    - 40 - Value - 40 for configuring CoreMultiProcessing token.
    - 41 - Value - 41 for configuring CoreMultiProcessing token.
    - 42 - Value - 42 for configuring CoreMultiProcessing token.
    - 43 - Value - 43 for configuring CoreMultiProcessing token.
    - 44 - Value - 44 for configuring CoreMultiProcessing token.
    - 45 - Value - 45 for configuring CoreMultiProcessing token.
    - 46 - Value - 46 for configuring CoreMultiProcessing token.
    - 47 - Value - 47 for configuring CoreMultiProcessing token.
    - 48 - Value - 48 for configuring CoreMultiProcessing token.
    - all - Value - all for configuring CoreMultiProcessing token.
  * cpu_energy_performance - default is "platform-default".  BIOS Token for setting Energy Performance configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - balanced-energy - Value - balanced-energy for configuring CpuEnergyPerformance token.
    - balanced-performance - Value - balanced-performance for configuring CpuEnergyPerformance token.
    - balanced-power - Value - balanced-power for configuring CpuEnergyPerformance token.
    - energy-efficient - Value - energy-efficient for configuring CpuEnergyPerformance token.
    - performance - Value - performance for configuring CpuEnergyPerformance token.
    - power - Value - power for configuring CpuEnergyPerformance token.
  * cpu_frequency_floor - default is "platform-default".  BIOS Token for setting Frequency Floor Override configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * cpu_performance - default is "platform-default".  BIOS Token for setting CPU Performance configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - custom - Value - custom for configuring CpuPerformance token.
    - enterprise - Value - enterprise for configuring CpuPerformance token.
    - high-throughput - Value - high-throughput for configuring CpuPerformance token.
    - hpc - Value - hpc for configuring CpuPerformance token.
  * cpu_power_management - default is "platform-default".  BIOS Token for setting Power Technology configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - custom - Value - custom for configuring CpuPowerManagement token.
    - disabled - Value - disabled for configuring CpuPowerManagement token.
    - energy-efficient - Value - energy-efficient for configuring CpuPowerManagement token.
    - performance - Value - performance for configuring CpuPowerManagement token.
  * cr_qos - default is "platform-default".  BIOS Token for setting CR QoS configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - Disabled for configuring CrQos token.
    - Mode 0 - Disable the PMem QoS Feature - Value - Mode 0 - Disable the PMem QoS Feature for configuring CrQos token.
    - Mode 1 - M2M QoS Enable and CHA QoS Disable - Value - Mode 1 - M2M QoS Enable and CHA QoS Disable for configuring CrQos token.
    - Mode 2 - M2M QoS Enable and CHA QoS Enable - Value - Mode 2 - M2M QoS Enable and CHA QoS Enable for configuring CrQos token.
    - Recipe 1 - Value - Recipe 1 for configuring CrQos token.
    - Recipe 2 - Value - Recipe 2 for configuring CrQos token.
    - Recipe 3 - Value - Recipe 3 for configuring CrQos token.
  * crfastgo_config - default is "platform-default".  BIOS Token for setting CR FastGo Config configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring CrfastgoConfig token.
    - Default - Value - Default for configuring CrfastgoConfig token.
    - Disable optimization - Value - Disable optimization for configuring CrfastgoConfig token.
    - Enable optimization - Value - Enable optimization for configuring CrfastgoConfig token.
    - Option 1 - Value - Option 1 for configuring CrfastgoConfig token.
    - Option 2 - Value - Option 2 for configuring CrfastgoConfig token.
    - Option 3 - Value - Option 3 for configuring CrfastgoConfig token.
    - Option 4 - Value - Option 4 for configuring CrfastgoConfig token.
    - Option 5 - Value - Option 5 for configuring CrfastgoConfig token.
  * dcpmm_firmware_downgrade - default is "platform-default".  BIOS Token for setting DCPMM Firmware Downgrade configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * demand_scrub - default is "platform-default".  BIOS Token for setting Demand Scrub configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * direct_cache_access - default is "platform-default".  BIOS Token for setting Direct Cache Access Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - auto - Value - auto for configuring DirectCacheAccess token.
    - disabled - Value - disabled for configuring DirectCacheAccess token.
    - enabled - Value - enabled for configuring DirectCacheAccess token.
  * dram_clock_throttling - default is "platform-default".  BIOS Token for setting DRAM Clock Throttling configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring DramClockThrottling token.
    - Balanced - Value - Balanced for configuring DramClockThrottling token.
    - Energy Efficient - Value - Energy Efficient for configuring DramClockThrottling token.
    - Performance - Value - Performance for configuring DramClockThrottling token.
  * dram_refresh_rate - default is "platform-default".  BIOS Token for setting DRAM Refresh Rate configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 1x - Value - 1x for configuring DramRefreshRate token.
    - 2x - Value - 2x for configuring DramRefreshRate token.
    - 3x - Value - 3x for configuring DramRefreshRate token.
    - 4x - Value - 4x for configuring DramRefreshRate token.
    - Auto - Value - Auto for configuring DramRefreshRate token.
  * dram_sw_thermal_throttling - default is "platform-default".  BIOS Token for setting DRAM SW Thermal Throttling configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * eadr_support - default is "platform-default".  BIOS Token for setting eADR Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring EadrSupport token.
    - disabled - Value - disabled for configuring EadrSupport token.
    - enabled - Value - enabled for configuring EadrSupport token.
  * edpc_en - default is "platform-default".  BIOS Token for setting IIO eDPC Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - Disabled for configuring EdpcEn token.
    - On Fatal Error - Value - On Fatal Error for configuring EdpcEn token.
    - On Fatal and Non-Fatal Errors - Value - On Fatal and Non-Fatal Errors for configuring EdpcEn token.
  * enable_clock_spread_spec - default is "platform-default".  BIOS Token for setting External SSC Enable configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * enable_mktme - default is "platform-default".  BIOS Token for setting Multikey Total Memory Encryption (MK-TME) configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * enable_sgx - default is "platform-default".  BIOS Token for setting Software Guard Extensions (SGX) configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * enable_tme - default is "platform-default".  BIOS Token for setting Total Memory Encryption (TME) configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * energy_efficient_turbo - default is "platform-default".  BIOS Token for setting Energy Efficient Turbo configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * eng_perf_tuning - default is "platform-default".  BIOS Token for setting Energy Performance Tuning configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - BIOS - Value - BIOS for configuring EngPerfTuning token.
    - OS - Value - OS for configuring EngPerfTuning token.
  * enhanced_intel_speed_step_tech - default is "platform-default".  BIOS Token for setting Enhanced Intel Speedstep (R) Technology configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * epoch_update - default is "platform-default".  BIOS Token for setting Select Owner EPOCH Input Type configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Change to New Random Owner EPOCHs - Value - Change to New Random Owner EPOCHs for configuring EpochUpdate token.
    - Manual User Defined Owner EPOCHs - Value - Manual User Defined Owner EPOCHs for configuring EpochUpdate token.
    - SGX Owner EPOCH activated - Value - SGX Owner EPOCH activated for configuring EpochUpdate token.
  * epp_enable - default is "platform-default".  BIOS Token for setting Processor EPP Enable configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * epp_profile - default is "platform-default".  BIOS Token for setting EPP Profile configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Balanced Performance - Value - Balanced Performance for configuring EppProfile token.
    - Balanced Power - Value - Balanced Power for configuring EppProfile token.
    - Performance - Value - Performance for configuring EppProfile token.
    - Power - Value - Power for configuring EppProfile token.
  * execute_disable_bit - default is "platform-default".  BIOS Token for setting Execute Disable Bit configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * extended_apic - default is "platform-default".  BIOS Token for setting Local X2 Apic configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring ExtendedApic token.
    - enabled - Value - enabled for configuring ExtendedApic token.
    - X2APIC - Value - X2APIC for configuring ExtendedApic token.
    - XAPIC - Value - XAPIC for configuring ExtendedApic token.
  * flow_control - default is "platform-default".  BIOS Token for setting Flow Control configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - none - Value - none for configuring FlowControl token.
    - rts-cts - Value - rts-cts for configuring FlowControl token.
  * frb2enable - default is "platform-default".  BIOS Token for setting FRB-2 Timer configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * hardware_prefetch - default is "platform-default".  BIOS Token for setting Hardware Prefetcher configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * hwpm_enable - default is "platform-default".  BIOS Token for setting CPU Hardware Power Management configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - Disabled for configuring HwpmEnable token.
    - HWPM Native Mode - Value - HWPM Native Mode for configuring HwpmEnable token.
    - HWPM OOB Mode - Value - HWPM OOB Mode for configuring HwpmEnable token.
    - NATIVE MODE - Value - NATIVE MODE for configuring HwpmEnable token.
    - Native Mode with no Legacy - Value - Native Mode with no Legacy for configuring HwpmEnable token.
    - OOB MODE - Value - OOB MODE for configuring HwpmEnable token.
  * imc_interleave - default is "platform-default".  BIOS Token for setting IMC Interleaving configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 1-way Interleave - Value - 1-way Interleave for configuring ImcInterleave token.
    - 2-way Interleave - Value - 2-way Interleave for configuring ImcInterleave token.
    - Auto - Value - Auto for configuring ImcInterleave token.
  * intel_dynamic_speed_select - default is "platform-default".  BIOS Token for setting Intel Dynamic Speed Select configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * intel_hyper_threading_tech - default is "platform-default".  BIOS Token for setting Intel HyperThreading Tech configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * intel_speed_select - default is "platform-default".  BIOS Token for setting Intel Speed Select configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Base - Value - Base for configuring IntelSpeedSelect token.
    - Config 1 - Value - Config 1 for configuring IntelSpeedSelect token.
    - Config 2 - Value - Config 2 for configuring IntelSpeedSelect token.
    - Config 3 - Value - Config 3 for configuring IntelSpeedSelect token.
    - Config 4 - Value - Config 4 for configuring IntelSpeedSelect token.
  * intel_turbo_boost_tech - default is "platform-default".  BIOS Token for setting Intel Turbo Boost Tech configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * intel_virtualization_technology - default is "platform-default".  BIOS Token for setting Intel (R) VT configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * intel_vt_for_directed_io - default is "platform-default".  BIOS Token for setting Intel VT for Directed IO configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * intel_vtd_coherency_support - default is "platform-default".  BIOS Token for setting Intel (R) VT-d Coherency Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * intel_vtd_interrupt_remapping - default is "platform-default".  BIOS Token for setting Intel (R) VT-d Interrupt Remapping configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * intel_vtd_pass_through_dma_support - default is "platform-default".  BIOS Token for setting Intel (R) VT-d PassThrough DMA Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * intel_vtdats_support - default is "platform-default".  BIOS Token for setting Intel VTD ATS Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * ioh_error_enable - default is "platform-default".  BIOS Token for setting IIO Error Enable configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - No - Value - No for configuring IohErrorEnable token.
    - Yes - Value - Yes for configuring IohErrorEnable token.
  * ioh_resource - default is "platform-default".  BIOS Token for setting IOH Resource Allocation configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - IOH0 24k IOH1 40k - Value - IOH0 24k IOH1 40k for configuring IohResource token.
    - IOH0 32k IOH1 32k - Value - IOH0 32k IOH1 32k for configuring IohResource token.
    - IOH0 40k IOH1 24k - Value - IOH0 40k IOH1 24k for configuring IohResource token.
    - IOH0 48k IOH1 16k - Value - IOH0 48k IOH1 16k for configuring IohResource token.
    - IOH0 56k IOH1 8k - Value - IOH0 56k IOH1 8k for configuring IohResource token.
  * ip_prefetch - default is "platform-default".  BIOS Token for setting DCU IP Prefetcher configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * ipv4http - default is "platform-default".  BIOS Token for setting IPV4 HTTP Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * ipv4pxe - default is "platform-default".  BIOS Token for setting IPv4 PXE Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * ipv6http - default is "platform-default".  BIOS Token for setting IPV6 HTTP Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * ipv6pxe - default is "platform-default".  BIOS Token for setting IPV6 PXE Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * kti_prefetch - default is "platform-default".  BIOS Token for setting KTI Prefetch configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring KtiPrefetch token.
    - disabled - Value - disabled for configuring KtiPrefetch token.
    - enabled - Value - enabled for configuring KtiPrefetch token.
  * legacy_os_redirection - default is "platform-default".  BIOS Token for setting Legacy OS Redirection configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * legacy_usb_support - default is "platform-default".  BIOS Token for setting Legacy USB Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - auto - Value - auto for configuring LegacyUsbSupport token.
    - disabled - Value - disabled for configuring LegacyUsbSupport token.
    - enabled - Value - enabled for configuring LegacyUsbSupport token.
  * llc_prefetch - default is "platform-default".  BIOS Token for setting LLC Prefetch configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * lom_port0state - default is "platform-default".  BIOS Token for setting LOM Port 0 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring LomPort0state token.
    - enabled - Value - enabled for configuring LomPort0state token.
    - Legacy Only - Value - Legacy Only for configuring LomPort0state token.
    - UEFI Only - Value - UEFI Only for configuring LomPort0state token.
  * lom_port1state - default is "platform-default".  BIOS Token for setting LOM Port 1 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring LomPort1state token.
    - enabled - Value - enabled for configuring LomPort1state token.
    - Legacy Only - Value - Legacy Only for configuring LomPort1state token.
    - UEFI Only - Value - UEFI Only for configuring LomPort1state token.
  * lom_port2state - default is "platform-default".  BIOS Token for setting LOM Port 2 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring LomPort2state token.
    - enabled - Value - enabled for configuring LomPort2state token.
    - Legacy Only - Value - Legacy Only for configuring LomPort2state token.
    - UEFI Only - Value - UEFI Only for configuring LomPort2state token.
  * lom_port3state - default is "platform-default".  BIOS Token for setting LOM Port 3 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring LomPort3state token.
    - enabled - Value - enabled for configuring LomPort3state token.
    - Legacy Only - Value - Legacy Only for configuring LomPort3state token.
    - UEFI Only - Value - UEFI Only for configuring LomPort3state token.
  * lom_ports_all_state - default is "platform-default".  BIOS Token for setting All Onboard LOM Ports configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * lv_ddr_mode - default is "platform-default".  BIOS Token for setting Low Voltage DDR Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - auto - Value - auto for configuring LvDdrMode token.
    - performance-mode - Value - performance-mode for configuring LvDdrMode token.
    - power-saving-mode - Value - power-saving-mode for configuring LvDdrMode token.
  * make_device_non_bootable - default is "platform-default".  BIOS Token for setting Make Device Non Bootable configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * memory_bandwidth_boost - default is "platform-default".  BIOS Token for setting Memory Bandwidth Boost configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * memory_inter_leave - default is "platform-default".  BIOS Token for setting Intel Memory Interleaving configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 1 Way Node Interleave - Value - 1 Way Node Interleave for configuring MemoryInterLeave token.
    - 2 Way Node Interleave - Value - 2 Way Node Interleave for configuring MemoryInterLeave token.
    - 4 Way Node Interleave - Value - 4 Way Node Interleave for configuring MemoryInterLeave token.
    - 8 Way Node Interleave - Value - 8 Way Node Interleave for configuring MemoryInterLeave token.
    - disabled - Value - disabled for configuring MemoryInterLeave token.
    - enabled - Value - enabled for configuring MemoryInterLeave token.
  * memory_mapped_io_above4gb - default is "platform-default".  BIOS Token for setting Memory Mapped IO above 4GiB configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * memory_refresh_rate - default is "platform-default".  BIOS Token for setting Memory Refresh Rate configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 1x Refresh - Value - 1x Refresh for configuring MemoryRefreshRate token.
    - 2x Refresh - Value - 2x Refresh for configuring MemoryRefreshRate token.
  * memory_size_limit - default is "platform-default".  BIOS Token for setting Memory Size Limit in GiB configuration (0 - 65535 GiB).
  * memory_thermal_throttling - default is "platform-default".  BIOS Token for setting Memory Thermal Throttling Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - CLTT with PECI - Value - CLTT with PECI for configuring MemoryThermalThrottling token.
    - disabled - Value - Disabled for configuring MemoryThermalThrottling token.
  * mirroring_mode - default is "platform-default".  BIOS Token for setting Mirroring Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - inter-socket - Value - inter-socket for configuring MirroringMode token.
    - intra-socket - Value - intra-socket for configuring MirroringMode token.
  * mmcfg_base - default is "platform-default".  BIOS Token for setting MMCFG BASE configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 1 GB - Value - 1 GiB for configuring MmcfgBase token.
    - 2 GB - Value - 2 GiB for configuring MmcfgBase token.
    - 2.5 GB - Value - 2.5 GiB for configuring MmcfgBase token.
    - 3 GB - Value - 3 GiB for configuring MmcfgBase token.
    - Auto - Value - Auto for configuring MmcfgBase token.
  * network_stack - default is "platform-default".  BIOS Token for setting Network Stack configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * numa_optimized - default is "platform-default".  BIOS Token for setting NUMA Optimized configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * nvmdimm_perform_config - default is "platform-default".  BIOS Token for setting NVM Performance Setting configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - BW Optimized - Value - BW Optimized for configuring NvmdimmPerformConfig token.
    - Balanced Profile - Value - Balanced Profile for configuring NvmdimmPerformConfig token.
    - Latency Optimized - Value - Latency Optimized for configuring NvmdimmPerformConfig token.
  * onboard10gbit_lom - default is "platform-default".  BIOS Token for setting Onboard 10Gbit LOM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * onboard_gbit_lom - default is "platform-default".  BIOS Token for setting Onboard Gbit LOM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * onboard_scu_storage_support - default is "platform-default".  BIOS Token for setting Onboard SCU Storage Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * onboard_scu_storage_sw_stack - default is "platform-default".  BIOS Token for setting Onboard SCU Storage SW Stack configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Intel RSTe - Value - Intel RSTe for configuring OnboardScuStorageSwStack token.
    - LSI SW RAID - Value - LSI SW RAID for configuring OnboardScuStorageSwStack token.
  * operation_mode - default is "platform-default".  BIOS Token for setting Operation Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Test Only - Value - Test Only for configuring OperationMode token.
    - Test and Repair - Value - Test and Repair for configuring OperationMode token.
  * os_boot_watchdog_timer - default is "platform-default".  BIOS Token for setting OS Boot Watchdog Timer configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * os_boot_watchdog_timer_policy - default is "platform-default".  BIOS Token for setting OS Boot Watchdog Timer Policy configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - do-nothing - Value - do-nothing for configuring OsBootWatchdogTimerPolicy token.
    - power-off - Value - power-off for configuring OsBootWatchdogTimerPolicy token.
    - reset - Value - reset for configuring OsBootWatchdogTimerPolicy token.
  * os_boot_watchdog_timer_timeout - default is "platform-default".  BIOS Token for setting OS Boot Watchdog Timer Timeout configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 5-minutes - Value - 5-minutes for configuring OsBootWatchdogTimerTimeout token.
    - 10-minutes - Value - 10-minutes for configuring OsBootWatchdogTimerTimeout token.
    - 15-minutes - Value - 15-minutes for configuring OsBootWatchdogTimerTimeout token.
    - 20-minutes - Value - 20-minutes for configuring OsBootWatchdogTimerTimeout token.
  * out_of_band_mgmt_port - default is "platform-default".  BIOS Token for setting Out-of-Band Mgmt Port configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * package_cstate_limit - default is "platform-default".  BIOS Token for setting Package C State Limit configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring PackageCstateLimit token.
    - C0 C1 State - Value - C0 C1 State for configuring PackageCstateLimit token.
    - C0/C1 - Value - C0/C1 for configuring PackageCstateLimit token.
    - C2 - Value - C2 for configuring PackageCstateLimit token.
    - C6 Non Retention - Value - C6 Non Retention for configuring PackageCstateLimit token.
    - C6 Retention - Value - C6 Retention for configuring PackageCstateLimit token.
    - No Limit - Value - No Limit for configuring PackageCstateLimit token.
  * panic_high_watermark - default is "platform-default".  BIOS Token for setting Panic and High Watermark configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - High - Value - High for configuring PanicHighWatermark token.
    - Low - Value - Low for configuring PanicHighWatermark token.
  * partial_cache_line_sparing - default is "platform-default".  BIOS Token for setting Partial Cache Line Sparing configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * partial_mirror_mode_config - default is "platform-default".  BIOS Token for setting Partial Memory Mirror Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring PartialMirrorModeConfig token.
    - Percentage - Value - Percentage for configuring PartialMirrorModeConfig token.
    - Value in GB - Value - Value in GiB for configuring PartialMirrorModeConfig token.
  * partial_mirror_percent - default is "platform-default".  BIOS Token for setting Partial Mirror Percentage configuration (0.00 - 50.00 Percentage).
  * partial_mirror_value1 - default is "platform-default".  BIOS Token for setting Partial Mirror1 Size in GiB configuration (0 - 65535 GiB).
  * partial_mirror_value2 - default is "platform-default".  BIOS Token for setting Partial Mirror2 Size in GiB configuration (0 - 65535 GiB).
  * partial_mirror_value3 - default is "platform-default".  BIOS Token for setting Partial Mirror3 Size in GiB configuration (0 - 65535 GiB).
  * partial_mirror_value4 - default is "platform-default".  BIOS Token for setting Partial Mirror4 Size in GiB configuration (0 - 65535 GiB).
  * patrol_scrub - default is "platform-default".  BIOS Token for setting Patrol Scrub configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring PatrolScrub token.
    - Enable at End of POST - Value - Enable at End of POST for configuring PatrolScrub token.
    - enabled - Value - enabled for configuring PatrolScrub token.
  * patrol_scrub_duration - default is "platform-default".  BIOS Token for setting Patrol Scrub Interval configuration (5 - 23 Hour).
  * pc_ie_ras_support - default is "platform-default".  BIOS Token for setting PCIe RAS Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * pc_ie_ssd_hot_plug_support - default is "platform-default".  BIOS Token for setting NVMe SSD Hot-Plug Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * pch_usb30mode - default is "platform-default".  BIOS Token for setting xHCI Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * pci_option_ro_ms - default is "platform-default".  BIOS Token for setting All PCIe Slots OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring PciOptionRoMs token.
    - enabled - Value - enabled for configuring PciOptionRoMs token.
    - Legacy Only - Value - Legacy Only for configuring PciOptionRoMs token.
    - UEFI Only - Value - UEFI Only for configuring PciOptionRoMs token.
  * pci_rom_clp - default is "platform-default".  BIOS Token for setting PCI ROM CLP configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * pcie_ari_support - default is "platform-default".  BIOS Token for setting PCIe ARI Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring PcieAriSupport token.
    - disabled - Value - disabled for configuring PcieAriSupport token.
    - enabled - Value - enabled for configuring PcieAriSupport token.
  * pcie_pll_ssc - default is "platform-default".  BIOS Token for setting PCIe PLL SSC configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring PciePllSsc token.
    - disabled - Value - Disabled for configuring PciePllSsc token.
    - ZeroPointFive - Value - ZeroPointFive for configuring PciePllSsc token.
  * pcie_slot_mraid1link_speed - default is "platform-default".  BIOS Token for setting MRAID1 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring PcieSlotMraid1linkSpeed token.
    - disabled - Value - Disabled for configuring PcieSlotMraid1linkSpeed token.
    - GEN1 - Value - GEN1 for configuring PcieSlotMraid1linkSpeed token.
    - GEN2 - Value - GEN2 for configuring PcieSlotMraid1linkSpeed token.
    - GEN3 - Value - GEN3 for configuring PcieSlotMraid1linkSpeed token.
    - GEN4 - Value - GEN4 for configuring PcieSlotMraid1linkSpeed token.
  * pcie_slot_mraid1option_rom - default is "platform-default".  BIOS Token for setting MRAID1 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * pcie_slot_mraid2link_speed - default is "platform-default".  BIOS Token for setting MRAID2 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring PcieSlotMraid2linkSpeed token.
    - disabled - Value - Disabled for configuring PcieSlotMraid2linkSpeed token.
    - GEN1 - Value - GEN1 for configuring PcieSlotMraid2linkSpeed token.
    - GEN2 - Value - GEN2 for configuring PcieSlotMraid2linkSpeed token.
    - GEN3 - Value - GEN3 for configuring PcieSlotMraid2linkSpeed token.
    - GEN4 - Value - GEN4 for configuring PcieSlotMraid2linkSpeed token.
  * pcie_slot_mraid2option_rom - default is "platform-default".  BIOS Token for setting MRAID2 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * pcie_slot_mstorraid_link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot MSTOR Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring PcieSlotMstorraidLinkSpeed token.
    - disabled - Value - Disabled for configuring PcieSlotMstorraidLinkSpeed token.
    - GEN1 - Value - GEN1 for configuring PcieSlotMstorraidLinkSpeed token.
    - GEN2 - Value - GEN2 for configuring PcieSlotMstorraidLinkSpeed token.
    - GEN3 - Value - GEN3 for configuring PcieSlotMstorraidLinkSpeed token.
    - GEN4 - Value - GEN4 for configuring PcieSlotMstorraidLinkSpeed token.
  * pcie_slot_mstorraid_option_rom - default is "platform-default".  BIOS Token for setting PCIe Slot MSTOR RAID OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * pcie_slot_nvme1link_speed - default is "platform-default".  BIOS Token for setting NVME 1 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring PcieSlotNvme1linkSpeed token.
    - disabled - Value - Disabled for configuring PcieSlotNvme1linkSpeed token.
    - GEN1 - Value - GEN1 for configuring PcieSlotNvme1linkSpeed token.
    - GEN2 - Value - GEN2 for configuring PcieSlotNvme1linkSpeed token.
    - GEN3 - Value - GEN3 for configuring PcieSlotNvme1linkSpeed token.
  * pcie_slot_nvme1option_rom - default is "platform-default".  BIOS Token for setting NVME 1 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * pcie_slot_nvme2link_speed - default is "platform-default".  BIOS Token for setting NVME 2 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring PcieSlotNvme2linkSpeed token.
    - disabled - Value - Disabled for configuring PcieSlotNvme2linkSpeed token.
    - GEN1 - Value - GEN1 for configuring PcieSlotNvme2linkSpeed token.
    - GEN2 - Value - GEN2 for configuring PcieSlotNvme2linkSpeed token.
    - GEN3 - Value - GEN3 for configuring PcieSlotNvme2linkSpeed token.
  * pcie_slot_nvme2option_rom - default is "platform-default".  BIOS Token for setting NVME 2 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * pcie_slot_nvme3link_speed - default is "platform-default".  BIOS Token for setting NVME 3 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring PcieSlotNvme3linkSpeed token.
    - disabled - Value - Disabled for configuring PcieSlotNvme3linkSpeed token.
    - GEN1 - Value - GEN1 for configuring PcieSlotNvme3linkSpeed token.
    - GEN2 - Value - GEN2 for configuring PcieSlotNvme3linkSpeed token.
    - GEN3 - Value - GEN3 for configuring PcieSlotNvme3linkSpeed token.
  * pcie_slot_nvme3option_rom - default is "platform-default".  BIOS Token for setting NVME 3 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * pcie_slot_nvme4link_speed - default is "platform-default".  BIOS Token for setting NVME 4 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring PcieSlotNvme4linkSpeed token.
    - disabled - Value - Disabled for configuring PcieSlotNvme4linkSpeed token.
    - GEN1 - Value - GEN1 for configuring PcieSlotNvme4linkSpeed token.
    - GEN2 - Value - GEN2 for configuring PcieSlotNvme4linkSpeed token.
    - GEN3 - Value - GEN3 for configuring PcieSlotNvme4linkSpeed token.
  * pcie_slot_nvme4option_rom - default is "platform-default".  BIOS Token for setting NVME 4 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * pcie_slot_nvme5link_speed - default is "platform-default".  BIOS Token for setting NVME 5 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring PcieSlotNvme5linkSpeed token.
    - disabled - Value - Disabled for configuring PcieSlotNvme5linkSpeed token.
    - GEN1 - Value - GEN1 for configuring PcieSlotNvme5linkSpeed token.
    - GEN2 - Value - GEN2 for configuring PcieSlotNvme5linkSpeed token.
    - GEN3 - Value - GEN3 for configuring PcieSlotNvme5linkSpeed token.
  * pcie_slot_nvme5option_rom - default is "platform-default".  BIOS Token for setting NVME 5 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * pcie_slot_nvme6link_speed - default is "platform-default".  BIOS Token for setting NVME 6 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring PcieSlotNvme6linkSpeed token.
    - disabled - Value - Disabled for configuring PcieSlotNvme6linkSpeed token.
    - GEN1 - Value - GEN1 for configuring PcieSlotNvme6linkSpeed token.
    - GEN2 - Value - GEN2 for configuring PcieSlotNvme6linkSpeed token.
    - GEN3 - Value - GEN3 for configuring PcieSlotNvme6linkSpeed token.
  * pcie_slot_nvme6option_rom - default is "platform-default".  BIOS Token for setting NVME 6 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * pop_support - default is "platform-default".  BIOS Token for setting Power ON Password configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * post_error_pause - default is "platform-default".  BIOS Token for setting POST Error Pause configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * post_package_repair - default is "platform-default".  BIOS Token for setting Post Package Repair configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - Disabled for configuring PostPackageRepair token.
    - Hard PPR - Value - Hard PPR for configuring PostPackageRepair token.
  * processor_c1e - default is "platform-default".  BIOS Token for setting Processor C1E configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * processor_c3report - default is "platform-default".  BIOS Token for setting Processor C3 Report configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * processor_c6report - default is "platform-default".  BIOS Token for setting Processor C6 Report configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * processor_cstate - default is "platform-default".  BIOS Token for setting CPU C State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * psata - default is "platform-default".  BIOS Token for setting P-SATA Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - AHCI - Value - AHCI for configuring Psata token.
    - disabled - Value - Disabled for configuring Psata token.
    - LSI SW RAID - Value - LSI SW RAID for configuring Psata token.
  * pstate_coord_type - default is "platform-default".  BIOS Token for setting P-STATE Coordination configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - HW ALL - Value - HW ALL for configuring PstateCoordType token.
    - SW ALL - Value - SW ALL for configuring PstateCoordType token.
    - SW ANY - Value - SW ANY for configuring PstateCoordType token.
  * putty_key_pad - default is "platform-default".  BIOS Token for setting Putty KeyPad configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - ESCN - Value - ESCN for configuring PuttyKeyPad token.
    - LINUX - Value - LINUX for configuring PuttyKeyPad token.
    - SCO - Value - SCO for configuring PuttyKeyPad token.
    - VT100 - Value - VT100 for configuring PuttyKeyPad token.
    - VT400 - Value - VT400 for configuring PuttyKeyPad token.
    - XTERMR6 - Value - XTERMR6 for configuring PuttyKeyPad token.
  * pwr_perf_tuning - default is "platform-default".  BIOS Token for setting Power Performance Tuning configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - bios - Value - BIOS for configuring PwrPerfTuning token.
    - os - Value - os for configuring PwrPerfTuning token.
    - peci - Value - peci for configuring PwrPerfTuning token.
  * qpi_link_frequency - default is "platform-default".  BIOS Token for setting QPI Link Frequency Select configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 6.4-gt/s - Value - 6.4-gt/s for configuring QpiLinkFrequency token.
    - 7.2-gt/s - Value - 7.2-gt/s for configuring QpiLinkFrequency token.
    - 8.0-gt/s - Value - 8.0-gt/s for configuring QpiLinkFrequency token.
    - 9.6-gt/s - Value - 9.6-gt/s for configuring QpiLinkFrequency token.
    - auto - Value - auto for configuring QpiLinkFrequency token.
  * qpi_link_speed - default is "platform-default".  BIOS Token for setting UPI Link Frequency Select configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 10.4GT/s - Value - 10.4GT/s for configuring QpiLinkSpeed token.
    - 11.2GT/s - Value - 11.2GT/s for configuring QpiLinkSpeed token.
    - 9.6GT/s - Value - 9.6GT/s for configuring QpiLinkSpeed token.
    - Auto - Value - Auto for configuring QpiLinkSpeed token.
  * qpi_snoop_mode - default is "platform-default".  BIOS Token for setting QPI Snoop Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - auto - Value - auto for configuring QpiSnoopMode token.
    - cluster-on-die - Value - cluster-on-die for configuring QpiSnoopMode token.
    - early-snoop - Value - early-snoop for configuring QpiSnoopMode token.
    - home-directory-snoop - Value - home-directory-snoop for configuring QpiSnoopMode token.
    - home-directory-snoop-with-osb - Value - home-directory-snoop-with-osb for configuring QpiSnoopMode token.
    - home-snoop - Value - home-snoop for configuring QpiSnoopMode token.
  * rank_inter_leave - default is "platform-default".  BIOS Token for setting Rank Interleaving configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 1-way - Value - 1-way for configuring RankInterLeave token.
    - 2-way - Value - 2-way for configuring RankInterLeave token.
    - 4-way - Value - 4-way for configuring RankInterLeave token.
    - 8-way - Value - 8-way for configuring RankInterLeave token.
    - auto - Value - auto for configuring RankInterLeave token.
  * redirection_after_post - default is "platform-default".  BIOS Token for setting Redirection After BIOS POST configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Always Enable - Value - Always Enable for configuring RedirectionAfterPost token.
    - Bootloader - Value - Bootloader for configuring RedirectionAfterPost token.
  * sata_mode_select - default is "platform-default".  BIOS Token for setting SATA Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - AHCI - Value - AHCI for configuring SataModeSelect token.
    - disabled - Value - Disabled for configuring SataModeSelect token.
    - LSI SW RAID - Value - LSI SW RAID for configuring SataModeSelect token.
  * select_memory_ras_configuration - default is "platform-default".  BIOS Token for setting Memory RAS Configuration configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - adddc-sparing - Value - adddc-sparing for configuring SelectMemoryRasConfiguration token.
    - lockstep - Value - lockstep for configuring SelectMemoryRasConfiguration token.
    - maximum-performance - Value - maximum-performance for configuring SelectMemoryRasConfiguration token.
    - mirror-mode-1lm - Value - mirror-mode-1lm for configuring SelectMemoryRasConfiguration token.
    - mirroring - Value - mirroring for configuring SelectMemoryRasConfiguration token.
    - partial-mirror-mode-1lm - Value - partial-mirror-mode-1lm for configuring SelectMemoryRasConfiguration token.
    - sparing - Value - sparing for configuring SelectMemoryRasConfiguration token.
  * select_ppr_type - default is "platform-default".  BIOS Token for setting PPR Type configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring SelectPprType token.
    - Hard PPR - Value - Hard PPR for configuring SelectPprType token.
    - Soft PPR - Value - Soft PPR for configuring SelectPprType token.
  * serial_port_aenable - default is "platform-default".  BIOS Token for setting Serial A Enable configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * sev - default is "platform-default".  BIOS Token for setting Secured Encrypted Virtualization configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 253 ASIDs - Value - 253 ASIDs for configuring Sev token.
    - 509 ASIDs - Value - 509 ASIDs for configuring Sev token.
    - Auto - Value - Auto for configuring Sev token.
  * sgx_auto_registration_agent - default is "platform-default".  BIOS Token for setting SGX Auto MP Registration Agent configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * sgx_epoch0 - default is "platform-default".  BIOS Token for setting SGX Epoch 0 configuration (0 - ffffffffffffffff Hash byte 7-0).
  * sgx_epoch1 - default is "platform-default".  BIOS Token for setting SGX Epoch 1 configuration (0 - ffffffffffffffff Hash byte 7-0).
  * sgx_factory_reset - default is "platform-default".  BIOS Token for setting SGX Factory Reset configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * sgx_le_pub_key_hash0 - default is "platform-default".  BIOS Token for setting SGX PubKey Hash0 configuration (0 - ffffffffffffffff Hash byte 7-0).
  * sgx_le_pub_key_hash1 - default is "platform-default".  BIOS Token for setting SGX PubKey Hash1 configuration (0 - ffffffffffffffff Hash byte 15-8).
  * sgx_le_pub_key_hash2 - default is "platform-default".  BIOS Token for setting SGX PubKey Hash2 configuration (0 - ffffffffffffffff Hash byte 23-16).
  * sgx_le_pub_key_hash3 - default is "platform-default".  BIOS Token for setting SGX PubKey Hash3 configuration (0 - ffffffffffffffff Hash byte 31-24).
  * sgx_le_wr - default is "platform-default".  BIOS Token for setting SGX Write Enable configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * sgx_package_info_in_band_access - default is "platform-default".  BIOS Token for setting SGX Package Information In-Band Access configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * sgx_qos - default is "platform-default".  BIOS Token for setting SGX QoS configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * single_pctl_enable - default is "platform-default".  BIOS Token for setting Single PCTL configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - No - Value - No for configuring SinglePctlEnable token.
    - Yes - Value - Yes for configuring SinglePctlEnable token.
  * slot10link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:10 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Slot10linkSpeed token.
    - disabled - Value - Disabled for configuring Slot10linkSpeed token.
    - GEN1 - Value - GEN1 for configuring Slot10linkSpeed token.
    - GEN2 - Value - GEN2 for configuring Slot10linkSpeed token.
    - GEN3 - Value - GEN3 for configuring Slot10linkSpeed token.
  * slot10state - default is "platform-default".  BIOS Token for setting Slot 10 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring Slot10state token.
    - enabled - Value - enabled for configuring Slot10state token.
    - Legacy Only - Value - Legacy Only for configuring Slot10state token.
    - UEFI Only - Value - UEFI Only for configuring Slot10state token.
  * slot11link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:11 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Slot11linkSpeed token.
    - disabled - Value - Disabled for configuring Slot11linkSpeed token.
    - GEN1 - Value - GEN1 for configuring Slot11linkSpeed token.
    - GEN2 - Value - GEN2 for configuring Slot11linkSpeed token.
    - GEN3 - Value - GEN3 for configuring Slot11linkSpeed token.
  * slot11state - default is "platform-default".  BIOS Token for setting Slot 11 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot12link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:12 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Slot12linkSpeed token.
    - disabled - Value - Disabled for configuring Slot12linkSpeed token.
    - GEN1 - Value - GEN1 for configuring Slot12linkSpeed token.
    - GEN2 - Value - GEN2 for configuring Slot12linkSpeed token.
    - GEN3 - Value - GEN3 for configuring Slot12linkSpeed token.
  * slot12state - default is "platform-default".  BIOS Token for setting Slot 12 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot13state - default is "platform-default".  BIOS Token for setting Slot 13 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot14state - default is "platform-default".  BIOS Token for setting Slot 14 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot1link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot: 1 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Slot1linkSpeed token.
    - disabled - Value - Disabled for configuring Slot1linkSpeed token.
    - GEN1 - Value - GEN1 for configuring Slot1linkSpeed token.
    - GEN2 - Value - GEN2 for configuring Slot1linkSpeed token.
    - GEN3 - Value - GEN3 for configuring Slot1linkSpeed token.
    - GEN4 - Value - GEN4 for configuring Slot1linkSpeed token.
  * slot1state - default is "platform-default".  BIOS Token for setting Slot 1 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring Slot1state token.
    - enabled - Value - enabled for configuring Slot1state token.
    - Legacy Only - Value - Legacy Only for configuring Slot1state token.
    - UEFI Only - Value - UEFI Only for configuring Slot1state token.
  * slot2link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot: 2 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Slot2linkSpeed token.
    - disabled - Value - Disabled for configuring Slot2linkSpeed token.
    - GEN1 - Value - GEN1 for configuring Slot2linkSpeed token.
    - GEN2 - Value - GEN2 for configuring Slot2linkSpeed token.
    - GEN3 - Value - GEN3 for configuring Slot2linkSpeed token.
    - GEN4 - Value - GEN4 for configuring Slot2linkSpeed token.
  * slot2state - default is "platform-default".  BIOS Token for setting Slot 2 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring Slot2state token.
    - enabled - Value - enabled for configuring Slot2state token.
    - Legacy Only - Value - Legacy Only for configuring Slot2state token.
    - UEFI Only - Value - UEFI Only for configuring Slot2state token.
  * slot3link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot: 3 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Slot3linkSpeed token.
    - disabled - Value - Disabled for configuring Slot3linkSpeed token.
    - GEN1 - Value - GEN1 for configuring Slot3linkSpeed token.
    - GEN2 - Value - GEN2 for configuring Slot3linkSpeed token.
    - GEN3 - Value - GEN3 for configuring Slot3linkSpeed token.
    - GEN4 - Value - GEN4 for configuring Slot3linkSpeed token.
  * slot3state - default is "platform-default".  BIOS Token for setting Slot 3 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring Slot3state token.
    - enabled - Value - enabled for configuring Slot3state token.
    - Legacy Only - Value - Legacy Only for configuring Slot3state token.
    - UEFI Only - Value - UEFI Only for configuring Slot3state token.
  * slot4link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot: 4 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Slot4linkSpeed token.
    - disabled - Value - Disabled for configuring Slot4linkSpeed token.
    - GEN1 - Value - GEN1 for configuring Slot4linkSpeed token.
    - GEN2 - Value - GEN2 for configuring Slot4linkSpeed token.
    - GEN3 - Value - GEN3 for configuring Slot4linkSpeed token.
    - GEN4 - Value - GEN4 for configuring Slot4linkSpeed token.
  * slot4state - default is "platform-default".  BIOS Token for setting Slot 4 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring Slot4state token.
    - enabled - Value - enabled for configuring Slot4state token.
    - Legacy Only - Value - Legacy Only for configuring Slot4state token.
    - UEFI Only - Value - UEFI Only for configuring Slot4state token.
  * slot5link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot: 5 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Slot5linkSpeed token.
    - disabled - Value - Disabled for configuring Slot5linkSpeed token.
    - GEN1 - Value - GEN1 for configuring Slot5linkSpeed token.
    - GEN2 - Value - GEN2 for configuring Slot5linkSpeed token.
    - GEN3 - Value - GEN3 for configuring Slot5linkSpeed token.
    - GEN4 - Value - GEN4 for configuring Slot5linkSpeed token.
  * slot5state - default is "platform-default".  BIOS Token for setting Slot 5 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring Slot5state token.
    - enabled - Value - enabled for configuring Slot5state token.
    - Legacy Only - Value - Legacy Only for configuring Slot5state token.
    - UEFI Only - Value - UEFI Only for configuring Slot5state token.
  * slot6link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot: 6 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Slot6linkSpeed token.
    - disabled - Value - Disabled for configuring Slot6linkSpeed token.
    - GEN1 - Value - GEN1 for configuring Slot6linkSpeed token.
    - GEN2 - Value - GEN2 for configuring Slot6linkSpeed token.
    - GEN3 - Value - GEN3 for configuring Slot6linkSpeed token.
    - GEN4 - Value - GEN4 for configuring Slot6linkSpeed token.
  * slot6state - default is "platform-default".  BIOS Token for setting Slot 6 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring Slot6state token.
    - enabled - Value - enabled for configuring Slot6state token.
    - Legacy Only - Value - Legacy Only for configuring Slot6state token.
    - UEFI Only - Value - UEFI Only for configuring Slot6state token.
  * slot7link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot: 7 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Slot7linkSpeed token.
    - disabled - Value - Disabled for configuring Slot7linkSpeed token.
    - GEN1 - Value - GEN1 for configuring Slot7linkSpeed token.
    - GEN2 - Value - GEN2 for configuring Slot7linkSpeed token.
    - GEN3 - Value - GEN3 for configuring Slot7linkSpeed token.
    - GEN4 - Value - GEN4 for configuring Slot7linkSpeed token.
  * slot7state - default is "platform-default".  BIOS Token for setting Slot 7 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring Slot7state token.
    - enabled - Value - enabled for configuring Slot7state token.
    - Legacy Only - Value - Legacy Only for configuring Slot7state token.
    - UEFI Only - Value - UEFI Only for configuring Slot7state token.
  * slot8link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot: 8 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Slot8linkSpeed token.
    - disabled - Value - Disabled for configuring Slot8linkSpeed token.
    - GEN1 - Value - GEN1 for configuring Slot8linkSpeed token.
    - GEN2 - Value - GEN2 for configuring Slot8linkSpeed token.
    - GEN3 - Value - GEN3 for configuring Slot8linkSpeed token.
    - GEN4 - Value - GEN4 for configuring Slot8linkSpeed token.
  * slot8state - default is "platform-default".  BIOS Token for setting Slot 8 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring Slot8state token.
    - enabled - Value - enabled for configuring Slot8state token.
    - Legacy Only - Value - Legacy Only for configuring Slot8state token.
    - UEFI Only - Value - UEFI Only for configuring Slot8state token.
  * slot9link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot: 9 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Slot9linkSpeed token.
    - disabled - Value - Disabled for configuring Slot9linkSpeed token.
    - GEN1 - Value - GEN1 for configuring Slot9linkSpeed token.
    - GEN2 - Value - GEN2 for configuring Slot9linkSpeed token.
    - GEN3 - Value - GEN3 for configuring Slot9linkSpeed token.
    - GEN4 - Value - GEN4 for configuring Slot9linkSpeed token.
  * slot9state - default is "platform-default".  BIOS Token for setting Slot 9 State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring Slot9state token.
    - enabled - Value - enabled for configuring Slot9state token.
    - Legacy Only - Value - Legacy Only for configuring Slot9state token.
    - UEFI Only - Value - UEFI Only for configuring Slot9state token.
  * slot_flom_link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:FLOM Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFlomLinkSpeed token.
    - disabled - Value - Disabled for configuring SlotFlomLinkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFlomLinkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFlomLinkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFlomLinkSpeed token.
  * slot_front_nvme10link_speed - default is "platform-default".  BIOS Token for setting Front NVME 10 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontNvme10linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontNvme10linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontNvme10linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontNvme10linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontNvme10linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotFrontNvme10linkSpeed token.
  * slot_front_nvme10option_rom - default is "platform-default".  BIOS Token for setting Front NVME 10 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme11link_speed - default is "platform-default".  BIOS Token for setting Front NVME 11 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontNvme11linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontNvme11linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontNvme11linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontNvme11linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontNvme11linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotFrontNvme11linkSpeed token.
  * slot_front_nvme11option_rom - default is "platform-default".  BIOS Token for setting Front NVME 11 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme12link_speed - default is "platform-default".  BIOS Token for setting Front NVME 12 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontNvme12linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontNvme12linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontNvme12linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontNvme12linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontNvme12linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotFrontNvme12linkSpeed token.
  * slot_front_nvme12option_rom - default is "platform-default".  BIOS Token for setting Front NVME 12 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme13option_rom - default is "platform-default".  BIOS Token for setting Front NVME 13 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme14option_rom - default is "platform-default".  BIOS Token for setting Front NVME 14 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme15option_rom - default is "platform-default".  BIOS Token for setting Front NVME 15 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme16option_rom - default is "platform-default".  BIOS Token for setting Front NVME 16 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme17option_rom - default is "platform-default".  BIOS Token for setting Front NVME 17 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme18option_rom - default is "platform-default".  BIOS Token for setting Front NVME 18 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme19option_rom - default is "platform-default".  BIOS Token for setting Front NVME 19 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme1link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Front NVME 1 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontNvme1linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontNvme1linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontNvme1linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontNvme1linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontNvme1linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotFrontNvme1linkSpeed token.
  * slot_front_nvme1option_rom - default is "platform-default".  BIOS Token for setting Front NVME 1 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme20option_rom - default is "platform-default".  BIOS Token for setting Front NVME 20 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme21option_rom - default is "platform-default".  BIOS Token for setting Front NVME 21 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme22option_rom - default is "platform-default".  BIOS Token for setting Front NVME 22 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme23option_rom - default is "platform-default".  BIOS Token for setting Front NVME 23 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme24option_rom - default is "platform-default".  BIOS Token for setting Front NVME 24 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme2link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Front NVME 2 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontNvme2linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontNvme2linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontNvme2linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontNvme2linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontNvme2linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotFrontNvme2linkSpeed token.
  * slot_front_nvme2option_rom - default is "platform-default".  BIOS Token for setting Front NVME 2 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme3link_speed - default is "platform-default".  BIOS Token for setting Front NVME 3 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontNvme3linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontNvme3linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontNvme3linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontNvme3linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontNvme3linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotFrontNvme3linkSpeed token.
  * slot_front_nvme3option_rom - default is "platform-default".  BIOS Token for setting Front NVME 3 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme4link_speed - default is "platform-default".  BIOS Token for setting Front NVME 4 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontNvme4linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontNvme4linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontNvme4linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontNvme4linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontNvme4linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotFrontNvme4linkSpeed token.
  * slot_front_nvme4option_rom - default is "platform-default".  BIOS Token for setting Front NVME 4 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme5link_speed - default is "platform-default".  BIOS Token for setting Front NVME 5 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontNvme5linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontNvme5linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontNvme5linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontNvme5linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontNvme5linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotFrontNvme5linkSpeed token.
  * slot_front_nvme5option_rom - default is "platform-default".  BIOS Token for setting Front NVME 5 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme6link_speed - default is "platform-default".  BIOS Token for setting Front NVME 6 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontNvme6linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontNvme6linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontNvme6linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontNvme6linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontNvme6linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotFrontNvme6linkSpeed token.
  * slot_front_nvme6option_rom - default is "platform-default".  BIOS Token for setting Front NVME 6 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme7link_speed - default is "platform-default".  BIOS Token for setting Front NVME 7 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontNvme7linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontNvme7linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontNvme7linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontNvme7linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontNvme7linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotFrontNvme7linkSpeed token.
  * slot_front_nvme7option_rom - default is "platform-default".  BIOS Token for setting Front NVME 7 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme8link_speed - default is "platform-default".  BIOS Token for setting Front NVME 8 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontNvme8linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontNvme8linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontNvme8linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontNvme8linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontNvme8linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotFrontNvme8linkSpeed token.
  * slot_front_nvme8option_rom - default is "platform-default".  BIOS Token for setting Front NVME 8 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_nvme9link_speed - default is "platform-default".  BIOS Token for setting Front NVME 9 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontNvme9linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontNvme9linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontNvme9linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontNvme9linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontNvme9linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotFrontNvme9linkSpeed token.
  * slot_front_nvme9option_rom - default is "platform-default".  BIOS Token for setting Front NVME 9 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_front_slot5link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Front1 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontSlot5linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontSlot5linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontSlot5linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontSlot5linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontSlot5linkSpeed token.
  * slot_front_slot6link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Front2 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotFrontSlot6linkSpeed token.
    - disabled - Value - Disabled for configuring SlotFrontSlot6linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotFrontSlot6linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotFrontSlot6linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotFrontSlot6linkSpeed token.
  * slot_gpu1state - default is "platform-default".  BIOS Token for setting GPU 1 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_gpu2state - default is "platform-default".  BIOS Token for setting GPU 2 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_gpu3state - default is "platform-default".  BIOS Token for setting GPU 3 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_gpu4state - default is "platform-default".  BIOS Token for setting GPU 4 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_gpu5state - default is "platform-default".  BIOS Token for setting GPU 5 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_gpu6state - default is "platform-default".  BIOS Token for setting GPU 6 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_gpu7state - default is "platform-default".  BIOS Token for setting GPU 7 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_gpu8state - default is "platform-default".  BIOS Token for setting GPU 8 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_hba_link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:HBA Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotHbaLinkSpeed token.
    - disabled - Value - Disabled for configuring SlotHbaLinkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotHbaLinkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotHbaLinkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotHbaLinkSpeed token.
  * slot_hba_state - default is "platform-default".  BIOS Token for setting PCIe Slot:HBA OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring SlotHbaState token.
    - enabled - Value - enabled for configuring SlotHbaState token.
    - Legacy Only - Value - Legacy Only for configuring SlotHbaState token.
    - UEFI Only - Value - UEFI Only for configuring SlotHbaState token.
  * slot_lom1link - default is "platform-default".  BIOS Token for setting PCIe LOM:1 Link configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_lom2link - default is "platform-default".  BIOS Token for setting PCIe LOM:2 Link configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_mezz_state - default is "platform-default".  BIOS Token for setting Slot Mezz State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring SlotMezzState token.
    - enabled - Value - enabled for configuring SlotMezzState token.
    - Legacy Only - Value - Legacy Only for configuring SlotMezzState token.
    - UEFI Only - Value - UEFI Only for configuring SlotMezzState token.
  * slot_mlom_link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:MLOM Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotMlomLinkSpeed token.
    - disabled - Value - Disabled for configuring SlotMlomLinkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotMlomLinkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotMlomLinkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotMlomLinkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotMlomLinkSpeed token.
  * slot_mlom_state - default is "platform-default".  BIOS Token for setting PCIe Slot MLOM OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring SlotMlomState token.
    - enabled - Value - enabled for configuring SlotMlomState token.
    - Legacy Only - Value - Legacy Only for configuring SlotMlomState token.
    - UEFI Only - Value - UEFI Only for configuring SlotMlomState token.
  * slot_mraid_link_speed - default is "platform-default".  BIOS Token for setting MRAID Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotMraidLinkSpeed token.
    - disabled - Value - Disabled for configuring SlotMraidLinkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotMraidLinkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotMraidLinkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotMraidLinkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotMraidLinkSpeed token.
  * slot_mraid_state - default is "platform-default".  BIOS Token for setting PCIe Slot MRAID OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n10state - default is "platform-default".  BIOS Token for setting PCIe Slot N10 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n11state - default is "platform-default".  BIOS Token for setting PCIe Slot N11 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n12state - default is "platform-default".  BIOS Token for setting PCIe Slot N12 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n13state - default is "platform-default".  BIOS Token for setting PCIe Slot N13 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n14state - default is "platform-default".  BIOS Token for setting PCIe Slot N14 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n15state - default is "platform-default".  BIOS Token for setting PCIe Slot N15 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n16state - default is "platform-default".  BIOS Token for setting PCIe Slot N16 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n17state - default is "platform-default".  BIOS Token for setting PCIe Slot N17 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n18state - default is "platform-default".  BIOS Token for setting PCIe Slot N18 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n19state - default is "platform-default".  BIOS Token for setting PCIe Slot N19 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n1state - default is "platform-default".  BIOS Token for setting PCIe Slot N1 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring SlotN1state token.
    - enabled - Value - enabled for configuring SlotN1state token.
    - Legacy Only - Value - Legacy Only for configuring SlotN1state token.
    - UEFI Only - Value - UEFI Only for configuring SlotN1state token.
  * slot_n20state - default is "platform-default".  BIOS Token for setting PCIe Slot N20 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n21state - default is "platform-default".  BIOS Token for setting PCIe Slot N21 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n22state - default is "platform-default".  BIOS Token for setting PCIe Slot N22 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n23state - default is "platform-default".  BIOS Token for setting PCIe Slot N23 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n24state - default is "platform-default".  BIOS Token for setting PCIe Slot N24 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n2state - default is "platform-default".  BIOS Token for setting PCIe Slot N2 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring SlotN2state token.
    - enabled - Value - enabled for configuring SlotN2state token.
    - Legacy Only - Value - Legacy Only for configuring SlotN2state token.
    - UEFI Only - Value - UEFI Only for configuring SlotN2state token.
  * slot_n3state - default is "platform-default".  BIOS Token for setting PCIe Slot N3 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n4state - default is "platform-default".  BIOS Token for setting PCIe Slot N4 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n5state - default is "platform-default".  BIOS Token for setting PCIe Slot N5 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n6state - default is "platform-default".  BIOS Token for setting PCIe Slot N6 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n7state - default is "platform-default".  BIOS Token for setting PCIe Slot N7 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n8state - default is "platform-default".  BIOS Token for setting PCIe Slot N8 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_n9state - default is "platform-default".  BIOS Token for setting PCIe Slot N9 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_raid_link_speed - default is "platform-default".  BIOS Token for setting RAID Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotRaidLinkSpeed token.
    - disabled - Value - Disabled for configuring SlotRaidLinkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotRaidLinkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotRaidLinkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotRaidLinkSpeed token.
  * slot_raid_state - default is "platform-default".  BIOS Token for setting PCIe Slot RAID OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_rear_nvme1link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Rear NVME 1 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotRearNvme1linkSpeed token.
    - disabled - Value - Disabled for configuring SlotRearNvme1linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotRearNvme1linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotRearNvme1linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotRearNvme1linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotRearNvme1linkSpeed token.
  * slot_rear_nvme1state - default is "platform-default".  BIOS Token for setting PCIe Slot:Rear NVME 1 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_rear_nvme2link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Rear NVME 2 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotRearNvme2linkSpeed token.
    - disabled - Value - Disabled for configuring SlotRearNvme2linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotRearNvme2linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotRearNvme2linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotRearNvme2linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotRearNvme2linkSpeed token.
  * slot_rear_nvme2state - default is "platform-default".  BIOS Token for setting PCIe Slot:Rear NVME 2 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_rear_nvme3link_speed - default is "platform-default".  BIOS Token for setting Rear NVME 3 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotRearNvme3linkSpeed token.
    - disabled - Value - Disabled for configuring SlotRearNvme3linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotRearNvme3linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotRearNvme3linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotRearNvme3linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotRearNvme3linkSpeed token.
  * slot_rear_nvme3state - default is "platform-default".  BIOS Token for setting PCIe Slot:Rear NVME 3 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_rear_nvme4link_speed - default is "platform-default".  BIOS Token for setting Rear NVME 4 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotRearNvme4linkSpeed token.
    - disabled - Value - Disabled for configuring SlotRearNvme4linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotRearNvme4linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotRearNvme4linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotRearNvme4linkSpeed token.
    - GEN4 - Value - GEN4 for configuring SlotRearNvme4linkSpeed token.
  * slot_rear_nvme4state - default is "platform-default".  BIOS Token for setting PCIe Slot:Rear NVME 4 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_rear_nvme5state - default is "platform-default".  BIOS Token for setting PCIe Slot:Rear NVME 5 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_rear_nvme6state - default is "platform-default".  BIOS Token for setting PCIe Slot:Rear NVME 6 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_rear_nvme7state - default is "platform-default".  BIOS Token for setting PCIe Slot:Rear NVME 7 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_rear_nvme8state - default is "platform-default".  BIOS Token for setting PCIe Slot:Rear NVME 8 OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * slot_riser1link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Riser1 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotRiser1linkSpeed token.
    - disabled - Value - Disabled for configuring SlotRiser1linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotRiser1linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotRiser1linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotRiser1linkSpeed token.
  * slot_riser1slot1link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Riser1 Slot1 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotRiser1slot1linkSpeed token.
    - disabled - Value - Disabled for configuring SlotRiser1slot1linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotRiser1slot1linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotRiser1slot1linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotRiser1slot1linkSpeed token.
  * slot_riser1slot2link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Riser1 Slot2 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotRiser1slot2linkSpeed token.
    - disabled - Value - Disabled for configuring SlotRiser1slot2linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotRiser1slot2linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotRiser1slot2linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotRiser1slot2linkSpeed token.
  * slot_riser1slot3link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Riser1 Slot3 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotRiser1slot3linkSpeed token.
    - disabled - Value - Disabled for configuring SlotRiser1slot3linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotRiser1slot3linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotRiser1slot3linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotRiser1slot3linkSpeed token.
  * slot_riser2link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Riser2 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotRiser2linkSpeed token.
    - disabled - Value - Disabled for configuring SlotRiser2linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotRiser2linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotRiser2linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotRiser2linkSpeed token.
  * slot_riser2slot4link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Riser2 Slot4 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotRiser2slot4linkSpeed token.
    - disabled - Value - Disabled for configuring SlotRiser2slot4linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotRiser2slot4linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotRiser2slot4linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotRiser2slot4linkSpeed token.
  * slot_riser2slot5link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Riser2 Slot5 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotRiser2slot5linkSpeed token.
    - disabled - Value - Disabled for configuring SlotRiser2slot5linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotRiser2slot5linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotRiser2slot5linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotRiser2slot5linkSpeed token.
  * slot_riser2slot6link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:Riser2 Slot6 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotRiser2slot6linkSpeed token.
    - disabled - Value - Disabled for configuring SlotRiser2slot6linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotRiser2slot6linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotRiser2slot6linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotRiser2slot6linkSpeed token.
  * slot_sas_state - default is "platform-default".  BIOS Token for setting PCIe Slot:SAS OptionROM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - disabled - Value - disabled for configuring SlotSasState token.
    - enabled - Value - enabled for configuring SlotSasState token.
    - Legacy Only - Value - Legacy Only for configuring SlotSasState token.
    - UEFI Only - Value - UEFI Only for configuring SlotSasState token.
  * slot_ssd_slot1link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:FrontSSD1 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotSsdSlot1linkSpeed token.
    - disabled - Value - Disabled for configuring SlotSsdSlot1linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotSsdSlot1linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotSsdSlot1linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotSsdSlot1linkSpeed token.
  * slot_ssd_slot2link_speed - default is "platform-default".  BIOS Token for setting PCIe Slot:FrontSSD2 Link Speed configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SlotSsdSlot2linkSpeed token.
    - disabled - Value - Disabled for configuring SlotSsdSlot2linkSpeed token.
    - GEN1 - Value - GEN1 for configuring SlotSsdSlot2linkSpeed token.
    - GEN2 - Value - GEN2 for configuring SlotSsdSlot2linkSpeed token.
    - GEN3 - Value - GEN3 for configuring SlotSsdSlot2linkSpeed token.
  * smee - default is "platform-default".  BIOS Token for setting SMEE configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * smt_mode - default is "platform-default".  BIOS Token for setting SMT Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring SmtMode token.
    - Off - Value - Off for configuring SmtMode token.
  * snc - default is "platform-default".  BIOS Token for setting Sub Numa Clustering configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Snc token.
    - disabled - Value - disabled for configuring Snc token.
    - enabled - Value - enabled for configuring Snc token.
  * snoopy_mode_for2lm - default is "platform-default".  BIOS Token for setting Snoopy Mode for 2LM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * snoopy_mode_for_ad - default is "platform-default".  BIOS Token for setting Snoopy Mode for AD configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * sparing_mode - default is "platform-default".  BIOS Token for setting Sparing Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - dimm-sparing - Value - dimm-sparing for configuring SparingMode token.
    - rank-sparing - Value - rank-sparing for configuring SparingMode token.
  * sr_iov - default is "platform-default".  BIOS Token for setting SR-IOV Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * streamer_prefetch - default is "platform-default".  BIOS Token for setting DCU Streamer Prefetch configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * svm_mode - default is "platform-default".  BIOS Token for setting SVM Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * terminal_type - default is "platform-default".  BIOS Token for setting Terminal Type configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - pc-ansi - Value - pc-ansi for configuring TerminalType token.
    - vt100 - Value - vt100 for configuring TerminalType token.
    - vt100-plus - Value - vt100-plus for configuring TerminalType token.
    - vt-utf8 - Value - vt-utf8 for configuring TerminalType token.
  * tpm_control - default is "platform-default".  BIOS Token for setting Trusted Platform Module State configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * tpm_pending_operation - default is "platform-default".  BIOS Token for setting TPM Pending Operation configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - None - Value - None for configuring TpmPendingOperation token.
    - TpmClear - Value - TpmClear for configuring TpmPendingOperation token.
  * tpm_support - default is "platform-default".  BIOS Token for setting TPM Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * tsme - default is "platform-default".  BIOS Token for setting Transparent Secure Memory Encryption configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring Tsme token.
    - disabled - Value - disabled for configuring Tsme token.
    - enabled - Value - enabled for configuring Tsme token.
  * txt_support - default is "platform-default".  BIOS Token for setting Intel Trusted Execution Technology Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * ucsm_boot_order_rule - default is "platform-default".  BIOS Token for setting Boot Order Rules configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Loose - Value - Loose for configuring UcsmBootOrderRule token.
    - Strict - Value - Strict for configuring UcsmBootOrderRule token.
  * ufs_disable - default is "platform-default".  BIOS Token for setting Uncore Frequency Scaling configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * uma_based_clustering - default is "platform-default".  BIOS Token for setting UMA Based Clustering configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Disable (All2All) - Value - Disable (All2All) for configuring UmaBasedClustering token.
    - Hemisphere (2-clusters) - Value - Hemisphere (2-clusters) for configuring UmaBasedClustering token.
  * usb_emul6064 - default is "platform-default".  BIOS Token for setting Port 60/64 Emulation configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * usb_port_front - default is "platform-default".  BIOS Token for setting USB Port Front configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * usb_port_internal - default is "platform-default".  BIOS Token for setting USB Port Internal configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * usb_port_kvm - default is "platform-default".  BIOS Token for setting USB Port KVM configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * usb_port_rear - default is "platform-default".  BIOS Token for setting USB Port Rear configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * usb_port_sd_card - default is "platform-default".  BIOS Token for setting USB Port SD Card configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * usb_port_vmedia - default is "platform-default".  BIOS Token for setting USB Port VMedia configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * usb_xhci_support - default is "platform-default".  BIOS Token for setting XHCI Legacy Support configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * vga_priority - default is "platform-default".  BIOS Token for setting VGA Priority configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Offboard - Value - Offboard for configuring VgaPriority token.
    - Onboard - Value - Onboard for configuring VgaPriority token.
    - Onboard VGA Disabled - Value - Onboard VGA Disabled for configuring VgaPriority token.
  * vmd_enable - default is "platform-default".  BIOS Token for setting VMD Enablement configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - enabled - Enables the BIOS setting.
    - disabled - Disables the BIOS setting.
  * vol_memory_mode - default is "platform-default".  BIOS Token for setting Volatile Memory Mode configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - 1LM - Value - 1LM for configuring VolMemoryMode token.
    - 2LM - Value - 2LM for configuring VolMemoryMode token.
  * work_load_config - default is "platform-default".  BIOS Token for setting Workload Configuration configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Balanced - Value - Balanced for configuring WorkLoadConfig token.
    - I/O Sensitive - Value - I/O Sensitive for configuring WorkLoadConfig token.
    - NUMA - Value - NUMA for configuring WorkLoadConfig token.
    - UMA - Value - UMA for configuring WorkLoadConfig token.
  * xpt_prefetch - default is "platform-default".  BIOS Token for setting XPT Prefetch configuration.
    - platform-default - Default value used by the platform for the BIOS setting.
    - Auto - Value - Auto for configuring XptPrefetch token.
    - disabled - Value - disabled for configuring XptPrefetch token.
    - enabled - Value - enabled for configuring XptPrefetch token.
  EOT
  type = map(object(
    {
      acs_control_gpu1state                 = optional(string)
      acs_control_gpu2state                 = optional(string)
      acs_control_gpu3state                 = optional(string)
      acs_control_gpu4state                 = optional(string)
      acs_control_gpu5state                 = optional(string)
      acs_control_gpu6state                 = optional(string)
      acs_control_gpu7state                 = optional(string)
      acs_control_gpu8state                 = optional(string)
      acs_control_slot11state               = optional(string)
      acs_control_slot12state               = optional(string)
      acs_control_slot13state               = optional(string)
      acs_control_slot14state               = optional(string)
      adjacent_cache_line_prefetch          = optional(string)
      advanced_mem_test                     = optional(string)
      all_usb_devices                       = optional(string)
      altitude                              = optional(string)
      aspm_support                          = optional(string)
      assert_nmi_on_perr                    = optional(string)
      assert_nmi_on_serr                    = optional(string)
      auto_cc_state                         = optional(string)
      autonumous_cstate_enable              = optional(string)
      baud_rate                             = optional(string)
      bios_template                         = optional(string)
      bme_dma_mitigation                    = optional(string)
      boot_option_num_retry                 = optional(string)
      boot_option_re_cool_down              = optional(string)
      boot_option_retry                     = optional(string)
      boot_performance_mode                 = optional(string)
      burst_and_postponed_refresh           = optional(string)
      cbs_cmn_apbdis                        = optional(string)
      cbs_cmn_cpu_cpb                       = optional(string)
      cbs_cmn_cpu_gen_downcore_ctrl         = optional(string)
      cbs_cmn_cpu_global_cstate_ctrl        = optional(string)
      cbs_cmn_cpu_l1stream_hw_prefetcher    = optional(string)
      cbs_cmn_cpu_l2stream_hw_prefetcher    = optional(string)
      cbs_cmn_cpu_smee                      = optional(string)
      cbs_cmn_cpu_streaming_stores_ctrl     = optional(string)
      cbs_cmn_determinism_slider            = optional(string)
      cbs_cmn_efficiency_mode_en            = optional(string)
      cbs_cmn_fixed_soc_pstate              = optional(string)
      cbs_cmn_gnb_nb_iommu                  = optional(string)
      cbs_cmn_gnb_smu_df_cstates            = optional(string)
      cbs_cmn_gnb_smucppc                   = optional(string)
      cbs_cmn_mem_ctrl_bank_group_swap_ddr4 = optional(string)
      cbs_cmn_mem_map_bank_interleave_ddr4  = optional(string)
      cbs_cmnc_tdp_ctl                      = optional(string)
      cbs_cpu_ccd_ctrl_ssp                  = optional(string)
      cbs_cpu_core_ctrl                     = optional(string)
      cbs_cpu_smt_ctrl                      = optional(string)
      cbs_dbg_cpu_snp_mem_cover             = optional(string)
      cbs_dbg_cpu_snp_mem_size_cover        = optional(string)
      cbs_df_cmn_acpi_srat_l3numa           = optional(string)
      cbs_df_cmn_dram_nps                   = optional(string)
      cbs_df_cmn_mem_intlv                  = optional(string)
      cbs_df_cmn_mem_intlv_size             = optional(string)
      cbs_sev_snp_support                   = optional(string)
      cdn_enable                            = optional(string)
      cdn_support                           = optional(string)
      channel_inter_leave                   = optional(string)
      cisco_adaptive_mem_training           = optional(string)
      cisco_debug_level                     = optional(string)
      cisco_oprom_launch_optimization       = optional(string)
      cisco_xgmi_max_speed                  = optional(string)
      cke_low_policy                        = optional(string)
      closed_loop_therm_throtl              = optional(string)
      cmci_enable                           = optional(string)
      config_tdp                            = optional(string)
      config_tdp_level                      = optional(string)
      console_redirection                   = optional(string)
      core_multi_processing                 = optional(string)
      cpu_energy_performance                = optional(string)
      cpu_frequency_floor                   = optional(string)
      cpu_performance                       = optional(string)
      cpu_power_management                  = optional(string)
      cr_qos                                = optional(string)
      crfastgo_config                       = optional(string)
      dcpmm_firmware_downgrade              = optional(string)
      demand_scrub                          = optional(string)
      description                           = optional(string)
      direct_cache_access                   = optional(string)
      dram_clock_throttling                 = optional(string)
      dram_refresh_rate                     = optional(string)
      dram_sw_thermal_throttling            = optional(string)
      eadr_support                          = optional(string)
      edpc_en                               = optional(string)
      enable_clock_spread_spec              = optional(string)
      enable_mktme                          = optional(string)
      enable_sgx                            = optional(string)
      enable_tme                            = optional(string)
      energy_efficient_turbo                = optional(string)
      eng_perf_tuning                       = optional(string)
      enhanced_intel_speed_step_tech        = optional(string)
      epoch_update                          = optional(string)
      epp_enable                            = optional(string)
      epp_profile                           = optional(string)
      execute_disable_bit                   = optional(string)
      extended_apic                         = optional(string)
      flow_control                          = optional(string)
      frb2enable                            = optional(string)
      hardware_prefetch                     = optional(string)
      hwpm_enable                           = optional(string)
      imc_interleave                        = optional(string)
      intel_dynamic_speed_select            = optional(string)
      intel_hyper_threading_tech            = optional(string)
      intel_speed_select                    = optional(string)
      intel_turbo_boost_tech                = optional(string)
      intel_virtualization_technology       = optional(string)
      intel_vt_for_directed_io              = optional(string)
      intel_vtd_coherency_support           = optional(string)
      intel_vtd_interrupt_remapping         = optional(string)
      intel_vtd_pass_through_dma_support    = optional(string)
      intel_vtdats_support                  = optional(string)
      ioh_error_enable                      = optional(string)
      ioh_resource                          = optional(string)
      ip_prefetch                           = optional(string)
      ipv4http                              = optional(string)
      ipv4pxe                               = optional(string)
      ipv6http                              = optional(string)
      ipv6pxe                               = optional(string)
      kti_prefetch                          = optional(string)
      legacy_os_redirection                 = optional(string)
      legacy_usb_support                    = optional(string)
      llc_prefetch                          = optional(string)
      lom_port0state                        = optional(string)
      lom_port1state                        = optional(string)
      lom_port2state                        = optional(string)
      lom_port3state                        = optional(string)
      lom_ports_all_state                   = optional(string)
      lv_ddr_mode                           = optional(string)
      make_device_non_bootable              = optional(string)
      memory_bandwidth_boost                = optional(string)
      memory_inter_leave                    = optional(string)
      memory_mapped_io_above4gb             = optional(string)
      memory_refresh_rate                   = optional(string)
      memory_size_limit                     = optional(string)
      memory_thermal_throttling             = optional(string)
      mirroring_mode                        = optional(string)
      mmcfg_base                            = optional(string)
      network_stack                         = optional(string)
      numa_optimized                        = optional(string)
      nvmdimm_perform_config                = optional(string)
      onboard_gbit_lom                      = optional(string)
      onboard_scu_storage_support           = optional(string)
      onboard_scu_storage_sw_stack          = optional(string)
      onboard10gbit_lom                     = optional(string)
      operation_mode                        = optional(string)
      organization                          = optional(string)
      os_boot_watchdog_timer                = optional(string)
      os_boot_watchdog_timer_policy         = optional(string)
      os_boot_watchdog_timer_timeout        = optional(string)
      out_of_band_mgmt_port                 = optional(string)
      package_cstate_limit                  = optional(string)
      panic_high_watermark                  = optional(string)
      partial_cache_line_sparing            = optional(string)
      partial_mirror_mode_config            = optional(string)
      partial_mirror_percent                = optional(string)
      partial_mirror_value1                 = optional(string)
      partial_mirror_value2                 = optional(string)
      partial_mirror_value3                 = optional(string)
      partial_mirror_value4                 = optional(string)
      patrol_scrub                          = optional(string)
      patrol_scrub_duration                 = optional(string)
      pc_ie_ras_support                     = optional(string)
      pc_ie_ssd_hot_plug_support            = optional(string)
      pch_usb30mode                         = optional(string)
      pci_option_ro_ms                      = optional(string)
      pci_rom_clp                           = optional(string)
      pcie_ari_support                      = optional(string)
      pcie_pll_ssc                          = optional(string)
      pcie_slot_mraid1link_speed            = optional(string)
      pcie_slot_mraid1option_rom            = optional(string)
      pcie_slot_mraid2link_speed            = optional(string)
      pcie_slot_mraid2option_rom            = optional(string)
      pcie_slot_mstorraid_link_speed        = optional(string)
      pcie_slot_mstorraid_option_rom        = optional(string)
      pcie_slot_nvme1link_speed             = optional(string)
      pcie_slot_nvme1option_rom             = optional(string)
      pcie_slot_nvme2link_speed             = optional(string)
      pcie_slot_nvme2option_rom             = optional(string)
      pcie_slot_nvme3link_speed             = optional(string)
      pcie_slot_nvme3option_rom             = optional(string)
      pcie_slot_nvme4link_speed             = optional(string)
      pcie_slot_nvme4option_rom             = optional(string)
      pcie_slot_nvme5link_speed             = optional(string)
      pcie_slot_nvme5option_rom             = optional(string)
      pcie_slot_nvme6link_speed             = optional(string)
      pcie_slot_nvme6option_rom             = optional(string)
      pop_support                           = optional(string)
      post_error_pause                      = optional(string)
      post_package_repair                   = optional(string)
      processor_c1e                         = optional(string)
      processor_c3report                    = optional(string)
      processor_c6report                    = optional(string)
      processor_cstate                      = optional(string)
      psata                                 = optional(string)
      pstate_coord_type                     = optional(string)
      putty_key_pad                         = optional(string)
      pwr_perf_tuning                       = optional(string)
      qpi_link_frequency                    = optional(string)
      qpi_link_speed                        = optional(string)
      qpi_snoop_mode                        = optional(string)
      rank_inter_leave                      = optional(string)
      redirection_after_post                = optional(string)
      sata_mode_select                      = optional(string)
      select_memory_ras_configuration       = optional(string)
      select_ppr_type                       = optional(string)
      serial_port_aenable                   = optional(string)
      sev                                   = optional(string)
      sgx_auto_registration_agent           = optional(string)
      sgx_epoch0                            = optional(string)
      sgx_epoch1                            = optional(string)
      sgx_factory_reset                     = optional(string)
      sgx_le_pub_key_hash0                  = optional(string)
      sgx_le_pub_key_hash1                  = optional(string)
      sgx_le_pub_key_hash2                  = optional(string)
      sgx_le_pub_key_hash3                  = optional(string)
      sgx_le_wr                             = optional(string)
      sgx_package_info_in_band_access       = optional(string)
      sgx_qos                               = optional(string)
      single_pctl_enable                    = optional(string)
      slot_flom_link_speed                  = optional(string)
      slot_front_nvme10link_speed           = optional(string)
      slot_front_nvme10option_rom           = optional(string)
      slot_front_nvme11link_speed           = optional(string)
      slot_front_nvme11option_rom           = optional(string)
      slot_front_nvme12link_speed           = optional(string)
      slot_front_nvme12option_rom           = optional(string)
      slot_front_nvme13option_rom           = optional(string)
      slot_front_nvme14option_rom           = optional(string)
      slot_front_nvme15option_rom           = optional(string)
      slot_front_nvme16option_rom           = optional(string)
      slot_front_nvme17option_rom           = optional(string)
      slot_front_nvme18option_rom           = optional(string)
      slot_front_nvme19option_rom           = optional(string)
      slot_front_nvme1link_speed            = optional(string)
      slot_front_nvme1option_rom            = optional(string)
      slot_front_nvme20option_rom           = optional(string)
      slot_front_nvme21option_rom           = optional(string)
      slot_front_nvme22option_rom           = optional(string)
      slot_front_nvme23option_rom           = optional(string)
      slot_front_nvme24option_rom           = optional(string)
      slot_front_nvme2link_speed            = optional(string)
      slot_front_nvme2option_rom            = optional(string)
      slot_front_nvme3link_speed            = optional(string)
      slot_front_nvme3option_rom            = optional(string)
      slot_front_nvme4link_speed            = optional(string)
      slot_front_nvme4option_rom            = optional(string)
      slot_front_nvme5link_speed            = optional(string)
      slot_front_nvme5option_rom            = optional(string)
      slot_front_nvme6link_speed            = optional(string)
      slot_front_nvme6option_rom            = optional(string)
      slot_front_nvme7link_speed            = optional(string)
      slot_front_nvme7option_rom            = optional(string)
      slot_front_nvme8link_speed            = optional(string)
      slot_front_nvme8option_rom            = optional(string)
      slot_front_nvme9link_speed            = optional(string)
      slot_front_nvme9option_rom            = optional(string)
      slot_front_slot5link_speed            = optional(string)
      slot_front_slot6link_speed            = optional(string)
      slot_gpu1state                        = optional(string)
      slot_gpu2state                        = optional(string)
      slot_gpu3state                        = optional(string)
      slot_gpu4state                        = optional(string)
      slot_gpu5state                        = optional(string)
      slot_gpu6state                        = optional(string)
      slot_gpu7state                        = optional(string)
      slot_gpu8state                        = optional(string)
      slot_hba_link_speed                   = optional(string)
      slot_hba_state                        = optional(string)
      slot_lom1link                         = optional(string)
      slot_lom2link                         = optional(string)
      slot_mezz_state                       = optional(string)
      slot_mlom_link_speed                  = optional(string)
      slot_mlom_state                       = optional(string)
      slot_mraid_link_speed                 = optional(string)
      slot_mraid_state                      = optional(string)
      slot_n10state                         = optional(string)
      slot_n11state                         = optional(string)
      slot_n12state                         = optional(string)
      slot_n13state                         = optional(string)
      slot_n14state                         = optional(string)
      slot_n15state                         = optional(string)
      slot_n16state                         = optional(string)
      slot_n17state                         = optional(string)
      slot_n18state                         = optional(string)
      slot_n19state                         = optional(string)
      slot_n1state                          = optional(string)
      slot_n20state                         = optional(string)
      slot_n21state                         = optional(string)
      slot_n22state                         = optional(string)
      slot_n23state                         = optional(string)
      slot_n24state                         = optional(string)
      slot_n2state                          = optional(string)
      slot_n3state                          = optional(string)
      slot_n4state                          = optional(string)
      slot_n5state                          = optional(string)
      slot_n6state                          = optional(string)
      slot_n7state                          = optional(string)
      slot_n8state                          = optional(string)
      slot_n9state                          = optional(string)
      slot_raid_link_speed                  = optional(string)
      slot_raid_state                       = optional(string)
      slot_rear_nvme1link_speed             = optional(string)
      slot_rear_nvme1state                  = optional(string)
      slot_rear_nvme2link_speed             = optional(string)
      slot_rear_nvme2state                  = optional(string)
      slot_rear_nvme3link_speed             = optional(string)
      slot_rear_nvme3state                  = optional(string)
      slot_rear_nvme4link_speed             = optional(string)
      slot_rear_nvme4state                  = optional(string)
      slot_rear_nvme5state                  = optional(string)
      slot_rear_nvme6state                  = optional(string)
      slot_rear_nvme7state                  = optional(string)
      slot_rear_nvme8state                  = optional(string)
      slot_riser1link_speed                 = optional(string)
      slot_riser1slot1link_speed            = optional(string)
      slot_riser1slot2link_speed            = optional(string)
      slot_riser1slot3link_speed            = optional(string)
      slot_riser2link_speed                 = optional(string)
      slot_riser2slot4link_speed            = optional(string)
      slot_riser2slot5link_speed            = optional(string)
      slot_riser2slot6link_speed            = optional(string)
      slot_sas_state                        = optional(string)
      slot_ssd_slot1link_speed              = optional(string)
      slot_ssd_slot2link_speed              = optional(string)
      slot10link_speed                      = optional(string)
      slot10state                           = optional(string)
      slot11link_speed                      = optional(string)
      slot11state                           = optional(string)
      slot12link_speed                      = optional(string)
      slot12state                           = optional(string)
      slot13state                           = optional(string)
      slot14state                           = optional(string)
      slot1link_speed                       = optional(string)
      slot1state                            = optional(string)
      slot2link_speed                       = optional(string)
      slot2state                            = optional(string)
      slot3link_speed                       = optional(string)
      slot3state                            = optional(string)
      slot4link_speed                       = optional(string)
      slot4state                            = optional(string)
      slot5link_speed                       = optional(string)
      slot5state                            = optional(string)
      slot6link_speed                       = optional(string)
      slot6state                            = optional(string)
      slot7link_speed                       = optional(string)
      slot7state                            = optional(string)
      slot8link_speed                       = optional(string)
      slot8state                            = optional(string)
      slot9link_speed                       = optional(string)
      slot9state                            = optional(string)
      smee                                  = optional(string)
      smt_mode                              = optional(string)
      snc                                   = optional(string)
      snoopy_mode_for_ad                    = optional(string)
      snoopy_mode_for2lm                    = optional(string)
      sparing_mode                          = optional(string)
      sr_iov                                = optional(string)
      streamer_prefetch                     = optional(string)
      svm_mode                              = optional(string)
      tags                                  = optional(list(map(string)))
      terminal_type                         = optional(string)
      tpm_control                           = optional(string)
      tpm_pending_operation                 = optional(string)
      tpm_support                           = optional(string)
      tsme                                  = optional(string)
      txt_support                           = optional(string)
      ucsm_boot_order_rule                  = optional(string)
      ufs_disable                           = optional(string)
      uma_based_clustering                  = optional(string)
      usb_emul6064                          = optional(string)
      usb_port_front                        = optional(string)
      usb_port_internal                     = optional(string)
      usb_port_kvm                          = optional(string)
      usb_port_rear                         = optional(string)
      usb_port_sd_card                      = optional(string)
      usb_port_vmedia                       = optional(string)
      usb_xhci_support                      = optional(string)
      vga_priority                          = optional(string)
      vmd_enable                            = optional(string)
      vol_memory_mode                       = optional(string)
      work_load_config                      = optional(string)
      xpt_prefetch                          = optional(string)
    }
  ))
}

module "bios_policies" {
  depends_on = [
    local.org_moids,
    local.merged_profile_policies,
  ]
  source      = "terraform-cisco-modules/imm/intersight//modules/bios_policies"
  for_each    = local.bios_policies
  description = each.value.description != "" ? each.value.description : "${each.key} BIOS Policy."
  name        = each.key
  org_moid    = local.org_moids[each.value.organization].moid
  profiles = {
    for k, v in local.merged_profile_policies : k => {
      moid        = v.moid
      object_type = v.object_type
    }
    if local.merged_profile_policies[k].bios_policy == each.key
  }
  tags = length(each.value.tags) > 0 ? each.value.tags : local.tags
  #+++++++++++++++++++++++++++++++
  # Boot Options Section
  #+++++++++++++++++++++++++++++++
  boot_option_num_retry        = each.value.boot_option_num_retry        # Number of Retries
  boot_option_re_cool_down     = each.value.boot_option_re_cool_down     # Cool Down Time (sec)
  boot_option_retry            = each.value.boot_option_retry            # Boot Option Retry
  ipv4http                     = each.value.ipv4http                     # IPv4 HTTP Support
  ipv4pxe                      = each.value.ipv4pxe                      # IPv4 PXE Support
  ipv6http                     = each.value.ipv6http                     # IPv6 HTTP Support
  ipv6pxe                      = each.value.ipv6pxe                      # IPv6 PXE Support
  network_stack                = each.value.network_stack                # Network Stack
  onboard_scu_storage_support  = each.value.onboard_scu_storage_support  # Onboard SCU Storage Support
  onboard_scu_storage_sw_stack = each.value.onboard_scu_storage_sw_stack # Onboard SCU Storage SW Stack
  pop_support                  = each.value.pop_support                  # Power ON Password
  psata                        = each.value.psata                        # P-SATA Mode
  sata_mode_select             = each.value.sata_mode_select             # SATA Mode
  vmd_enable                   = each.value.vmd_enable                   # VMD Enablement
  #+++++++++++++++++++++++++++++++
  # Intel Directed IO Section
  #+++++++++++++++++++++++++++++++
  intel_vt_for_directed_io = length(
    regexall("(DSS|HPC|Java)", each.value.bios_template)
  ) > 0 ? "disabled" : each.value.intel_vt_for_directed_io                           # Intel VT for Directed IO
  intel_vtd_coherency_support        = each.value.intel_vtd_coherency_support        # Intel(R) VT-d Coherency Support
  intel_vtd_interrupt_remapping      = each.value.intel_vtd_interrupt_remapping      # Intel(R) VT-d interrupt Remapping
  intel_vtd_pass_through_dma_support = each.value.intel_vtd_pass_through_dma_support # Intel(R) VT-d PassThrough DMA Support
  intel_vtdats_support               = each.value.intel_vtdats_support               # Intel VTD ATS Support
  #+++++++++++++++++++++++++++++++
  # LOM and PCIe Slots Section
  #+++++++++++++++++++++++++++++++
  acs_control_gpu1state          = each.value.acs_control_gpu1state          # ACS Control GPU 1
  acs_control_gpu2state          = each.value.acs_control_gpu2state          # ACS Control GPU 2
  acs_control_gpu3state          = each.value.acs_control_gpu3state          # ACS Control GPU 3
  acs_control_gpu4state          = each.value.acs_control_gpu4state          # ACS Control GPU 4
  acs_control_gpu5state          = each.value.acs_control_gpu5state          # ACS Control GPU 5
  acs_control_gpu6state          = each.value.acs_control_gpu6state          # ACS Control GPU 6
  acs_control_gpu7state          = each.value.acs_control_gpu7state          # ACS Control GPU 7
  acs_control_gpu8state          = each.value.acs_control_gpu8state          # ACS Control GPU 8
  acs_control_slot11state        = each.value.acs_control_slot11state        # ACS Control Slot 11
  acs_control_slot12state        = each.value.acs_control_slot12state        # ACS Control Slot 12
  acs_control_slot13state        = each.value.acs_control_slot13state        # ACS Control Slot 13
  acs_control_slot14state        = each.value.acs_control_slot14state        # ACS Control Slot 14
  cdn_support                    = each.value.cdn_support                    # CDN Support for LOM
  edpc_en                        = each.value.edpc_en                        # IIO eDPC Support
  enable_clock_spread_spec       = each.value.enable_clock_spread_spec       # External SSC Enable
  lom_port0state                 = each.value.lom_port0state                 # LOM Port 0 OptionROM
  lom_port1state                 = each.value.lom_port1state                 # LOM Port 1 OptionROM
  lom_port2state                 = each.value.lom_port2state                 # LOM Port 2 OptionROM
  lom_port3state                 = each.value.lom_port3state                 # LOM Port 3 OptionROM
  lom_ports_all_state            = each.value.lom_ports_all_state            # All Onboard LOM Ports
  pci_option_ro_ms               = each.value.pci_option_ro_ms               # All PCIe Slots OptionROM
  pci_rom_clp                    = each.value.pci_rom_clp                    # PCI ROM CLP
  pcie_ari_support               = each.value.pcie_ari_support               # PCI ARI Support
  pcie_pll_ssc                   = each.value.pcie_pll_ssc                   # PCI PLL SSC
  pcie_slot_mraid1link_speed     = each.value.pcie_slot_mraid1link_speed     # MRAID1 Link Speed
  pcie_slot_mraid1option_rom     = each.value.pcie_slot_mraid1option_rom     # MRAID1 OptionROM
  pcie_slot_mraid2link_speed     = each.value.pcie_slot_mraid2link_speed     # MRAID2 Link Speed
  pcie_slot_mraid2option_rom     = each.value.pcie_slot_mraid2option_rom     # MRAID2 OptionROM
  pcie_slot_mstorraid_link_speed = each.value.pcie_slot_mstorraid_link_speed # PCIe Slot MSTOR Link Speed
  pcie_slot_mstorraid_option_rom = each.value.pcie_slot_mstorraid_option_rom # PCIe Slot MSTOR RAID OptionROM
  pcie_slot_nvme1link_speed      = each.value.pcie_slot_nvme1link_speed      # NVME 1 Link Speed
  pcie_slot_nvme1option_rom      = each.value.pcie_slot_nvme1option_rom      # NVME 1 OptionROM
  pcie_slot_nvme2link_speed      = each.value.pcie_slot_nvme2link_speed      # NVME 2 Link Speed
  pcie_slot_nvme2option_rom      = each.value.pcie_slot_nvme2option_rom      # NVME 2 OptionROM
  pcie_slot_nvme3link_speed      = each.value.pcie_slot_nvme3link_speed      # NVME 3 Link Speed
  pcie_slot_nvme3option_rom      = each.value.pcie_slot_nvme3option_rom      # NVME 3 OptionROM
  pcie_slot_nvme4link_speed      = each.value.pcie_slot_nvme4link_speed      # NVME 4 Link Speed
  pcie_slot_nvme4option_rom      = each.value.pcie_slot_nvme4option_rom      # NVME 4 OptionROM
  pcie_slot_nvme5link_speed      = each.value.pcie_slot_nvme5link_speed      # NVME 5 Link Speed
  pcie_slot_nvme5option_rom      = each.value.pcie_slot_nvme5option_rom      # NVME 5 OptionROM
  pcie_slot_nvme6link_speed      = each.value.pcie_slot_nvme6link_speed      # NVME 6 Link Speed
  pcie_slot_nvme6option_rom      = each.value.pcie_slot_nvme6option_rom      # NVME 6 OptionROM
  slot10link_speed               = each.value.slot10link_speed               # PCIe Slot:10 Link Speed
  slot10state                    = each.value.slot10state                    # Slot 10 State
  slot11link_speed               = each.value.slot11link_speed               # PCIe Slot:11 Link Speed
  slot11state                    = each.value.slot11state                    # Slot 11 State
  slot12link_speed               = each.value.slot12link_speed               # PCIe Slot:12 Link Speed
  slot12state                    = each.value.slot12state                    # Slot 12 State
  slot13state                    = each.value.slot13state                    # Slot 13 State
  slot14state                    = each.value.slot14state                    # Slot 14 State
  slot1link_speed                = each.value.slot1link_speed                # PCIe Slot: 1 Link Speed
  slot1state                     = each.value.slot1state                     # Slot 1 State
  slot2link_speed                = each.value.slot2link_speed                # PCIe Slot: 2 Link Speed
  slot2state                     = each.value.slot2state                     # Slot 2 State
  slot3link_speed                = each.value.slot3link_speed                # PCIe Slot: 3 Link Speed
  slot3state                     = each.value.slot3state                     # Slot 3 State
  slot4link_speed                = each.value.slot4link_speed                # PCIe Slot: 4 Link Speed
  slot4state                     = each.value.slot4state                     # Slot 4 State
  slot5link_speed                = each.value.slot5link_speed                # PCIe Slot: 5 Link Speed
  slot5state                     = each.value.slot5state                     # Slot 5 State
  slot6link_speed                = each.value.slot6link_speed                # PCIe Slot: 6 Link Speed
  slot6state                     = each.value.slot6state                     # Slot 6 State
  slot7link_speed                = each.value.slot7link_speed                # PCIe Slot: 7 Link Speed
  slot7state                     = each.value.slot7state                     # Slot 7 State
  slot8link_speed                = each.value.slot8link_speed                # PCIe Slot: 8 Link Speed
  slot8state                     = each.value.slot8state                     # Slot 8 State
  slot9link_speed                = each.value.slot9link_speed                # PCIe Slot: 9 Link Speed
  slot9state                     = each.value.slot9state                     # Slot 9 State
  slot_flom_link_speed           = each.value.slot_flom_link_speed           # PCIe Slot:FLOM Link Speed
  slot_front_nvme10link_speed    = each.value.slot_front_nvme10link_speed    # Front NVME 10 Link Speed
  slot_front_nvme10option_rom    = each.value.slot_front_nvme10option_rom    # Front NVME 10 OptionROM
  slot_front_nvme11link_speed    = each.value.slot_front_nvme11link_speed    # Front NVME 11 Link Speed
  slot_front_nvme11option_rom    = each.value.slot_front_nvme11option_rom    # Front NVME 11 OptionROM
  slot_front_nvme12link_speed    = each.value.slot_front_nvme12link_speed    # Front NVME 12 Link Speed
  slot_front_nvme12option_rom    = each.value.slot_front_nvme12option_rom    # Front NVME 12 OptionROM
  slot_front_nvme13option_rom    = each.value.slot_front_nvme13option_rom    # Front NVME 13 OptionROM
  slot_front_nvme14option_rom    = each.value.slot_front_nvme14option_rom    # Front NVME 14 OptionROM
  slot_front_nvme15option_rom    = each.value.slot_front_nvme15option_rom    # Front NVME 15 OptionROM
  slot_front_nvme16option_rom    = each.value.slot_front_nvme16option_rom    # Front NVME 16 OptionROM
  slot_front_nvme17option_rom    = each.value.slot_front_nvme17option_rom    # Front NVME 17 OptionROM
  slot_front_nvme18option_rom    = each.value.slot_front_nvme18option_rom    # Front NVME 18 OptionROM
  slot_front_nvme19option_rom    = each.value.slot_front_nvme19option_rom    # Front NVME 19 OptionROM
  slot_front_nvme1link_speed     = each.value.slot_front_nvme1link_speed     # PCIe Slot:Front NVME 1 Link Speed
  slot_front_nvme1option_rom     = each.value.slot_front_nvme1option_rom     # Front NVME 1 OptionROM
  slot_front_nvme20option_rom    = each.value.slot_front_nvme20option_rom    # Front NVME 20 OptionROM
  slot_front_nvme21option_rom    = each.value.slot_front_nvme21option_rom    # Front NVME 21 OptionROM
  slot_front_nvme22option_rom    = each.value.slot_front_nvme22option_rom    # Front NVME 22 OptionROM
  slot_front_nvme23option_rom    = each.value.slot_front_nvme23option_rom    # Front NVME 23 OptionROM
  slot_front_nvme24option_rom    = each.value.slot_front_nvme24option_rom    # Front NVME 24 OptionROM
  slot_front_nvme2link_speed     = each.value.slot_front_nvme2link_speed     # PCIe Slot:Front NVME 2 Link Speed
  slot_front_nvme2option_rom     = each.value.slot_front_nvme2option_rom     # Front NVME 2 OptionROM
  slot_front_nvme3link_speed     = each.value.slot_front_nvme3link_speed     # Front NVME 3 Link Speed
  slot_front_nvme3option_rom     = each.value.slot_front_nvme3option_rom     # Front NVME 3 OptionROM
  slot_front_nvme4link_speed     = each.value.slot_front_nvme4link_speed     # Front NVME 4 Link Speed
  slot_front_nvme4option_rom     = each.value.slot_front_nvme4option_rom     # Front NVME 4 OptionROM
  slot_front_nvme5link_speed     = each.value.slot_front_nvme5link_speed     # Front NVME 5 Link Speed
  slot_front_nvme5option_rom     = each.value.slot_front_nvme5option_rom     # Front NVME 5 OptionROM
  slot_front_nvme6link_speed     = each.value.slot_front_nvme6link_speed     # Front NVME 6 Link Speed
  slot_front_nvme6option_rom     = each.value.slot_front_nvme6option_rom     # Front NVME 6 OptionROM
  slot_front_nvme7link_speed     = each.value.slot_front_nvme7link_speed     # Front NVME 7 Link Speed
  slot_front_nvme7option_rom     = each.value.slot_front_nvme7option_rom     # Front NVME 7 OptionROM
  slot_front_nvme8link_speed     = each.value.slot_front_nvme8link_speed     # Front NVME 8 Link Speed
  slot_front_nvme8option_rom     = each.value.slot_front_nvme8option_rom     # Front NVME 8 OptionROM
  slot_front_nvme9link_speed     = each.value.slot_front_nvme9link_speed     # Front NVME 9 Link Speed
  slot_front_nvme9option_rom     = each.value.slot_front_nvme9option_rom     # Front NVME 9 OptionROM
  slot_front_slot5link_speed     = each.value.slot_front_slot5link_speed     # PCIe Slot:Front1 Link Speed
  slot_front_slot6link_speed     = each.value.slot_front_slot6link_speed     # PCIe Slot:Front2 Link Speed
  slot_gpu1state                 = each.value.slot_gpu1state                 # GPU 1 OptionROM
  slot_gpu2state                 = each.value.slot_gpu2state                 # GPU 2 OptionROM
  slot_gpu3state                 = each.value.slot_gpu3state                 # GPU 3 OptionROM
  slot_gpu4state                 = each.value.slot_gpu4state                 # GPU 4 OptionROM
  slot_gpu5state                 = each.value.slot_gpu5state                 # GPU 5 OptionROM
  slot_gpu6state                 = each.value.slot_gpu6state                 # GPU 6 OptionROM
  slot_gpu7state                 = each.value.slot_gpu7state                 # GPU 7 OptionROM
  slot_gpu8state                 = each.value.slot_gpu8state                 # GPU 8 OptionROM
  slot_hba_link_speed            = each.value.slot_hba_link_speed            # PCIe Slot:HBA Link Speed
  slot_hba_state                 = each.value.slot_hba_state                 # PCIe Slot:HBA OptionROM
  slot_lom1link                  = each.value.slot_lom1link                  # PCIe LOM:1 Link
  slot_lom2link                  = each.value.slot_lom2link                  # PCIe LOM:2 Link
  slot_mezz_state                = each.value.slot_mezz_state                # Slot Mezz State
  slot_mlom_link_speed           = each.value.slot_mlom_link_speed           # PCIe Slot:MLOM Link Speed
  slot_mlom_state                = each.value.slot_mlom_state                # PCIe Slot MLOM OptionROM
  slot_mraid_link_speed          = each.value.slot_mraid_link_speed          # MRAID Link Speed
  slot_mraid_state               = each.value.slot_mraid_state               # PCIe Slot MRAID OptionROM
  slot_n10state                  = each.value.slot_n10state                  # PCIe Slot N10 OptionROM
  slot_n11state                  = each.value.slot_n11state                  # PCIe Slot N11 OptionROM
  slot_n12state                  = each.value.slot_n12state                  # PCIe Slot N12 OptionROM
  slot_n13state                  = each.value.slot_n13state                  # PCIe Slot N13 OptionROM
  slot_n14state                  = each.value.slot_n14state                  # PCIe Slot N14 OptionROM
  slot_n15state                  = each.value.slot_n15state                  # PCIe Slot N15 OptionROM
  slot_n16state                  = each.value.slot_n16state                  # PCIe Slot N16 OptionROM
  slot_n17state                  = each.value.slot_n17state                  # PCIe Slot N17 OptionROM
  slot_n18state                  = each.value.slot_n18state                  # PCIe Slot N18 OptionROM
  slot_n19state                  = each.value.slot_n19state                  # PCIe Slot N19 OptionROM
  slot_n1state                   = each.value.slot_n1state                   # PCIe Slot N1 OptionROM
  slot_n20state                  = each.value.slot_n20state                  # PCIe Slot N20 OptionROM
  slot_n21state                  = each.value.slot_n21state                  # PCIe Slot N21 OptionROM
  slot_n22state                  = each.value.slot_n22state                  # PCIe Slot N22 OptionROM
  slot_n23state                  = each.value.slot_n23state                  # PCIe Slot N23 OptionROM
  slot_n24state                  = each.value.slot_n24state                  # PCIe Slot N24 OptionROM
  slot_n2state                   = each.value.slot_n2state                   # PCIe Slot N2 OptionROM
  slot_n3state                   = each.value.slot_n3state                   # PCIe Slot N3 OptionROM
  slot_n4state                   = each.value.slot_n4state                   # PCIe Slot N4 OptionROM
  slot_n5state                   = each.value.slot_n5state                   # PCIe Slot N5 OptionROM
  slot_n6state                   = each.value.slot_n6state                   # PCIe Slot N6 OptionROM
  slot_n7state                   = each.value.slot_n7state                   # PCIe Slot N7 OptionROM
  slot_n8state                   = each.value.slot_n8state                   # PCIe Slot N8 OptionROM
  slot_n9state                   = each.value.slot_n9state                   # PCIe Slot N9 OptionROM
  slot_raid_link_speed           = each.value.slot_raid_link_speed           # RAID Link Speed
  slot_raid_state                = each.value.slot_raid_state                # PCIe Slot RAID OptionROM
  slot_rear_nvme1link_speed      = each.value.slot_rear_nvme1link_speed      # PCIe Slot:Rear NVME 1 Link Speed
  slot_rear_nvme1state           = each.value.slot_rear_nvme1state           # PCIe Slot:Rear NVME 1 OptionROM
  slot_rear_nvme2link_speed      = each.value.slot_rear_nvme2link_speed      # PCIe Slot:Rear NVME 2 Link Speed
  slot_rear_nvme2state           = each.value.slot_rear_nvme2state           # PCIe Slot:Rear NVME 2 OptionROM
  slot_rear_nvme3link_speed      = each.value.slot_rear_nvme3link_speed      # PCIe Slot:Rear NVME 3 Link Speed
  slot_rear_nvme3state           = each.value.slot_rear_nvme3state           # PCIe Slot:Rear NVME 3 OptionROM
  slot_rear_nvme4link_speed      = each.value.slot_rear_nvme4link_speed      # PCIe Slot:Rear NVME 4 Link Speed
  slot_rear_nvme4state           = each.value.slot_rear_nvme4state           # PCIe Slot:Rear NVME 4 OptionROM
  slot_rear_nvme5state           = each.value.slot_rear_nvme5state           # PCIe Slot:Rear NVME 5 OptionROM
  slot_rear_nvme6state           = each.value.slot_rear_nvme6state           # PCIe Slot:Rear NVME 6 OptionROM
  slot_rear_nvme7state           = each.value.slot_rear_nvme7state           # PCIe Slot:Rear NVME 7 OptionROM
  slot_rear_nvme8state           = each.value.slot_rear_nvme8state           # PCIe Slot:Rear NVME 8 OptionROM
  slot_riser1link_speed          = each.value.slot_riser1link_speed          # PCIe Slot:Riser1 Link Speed
  slot_riser1slot1link_speed     = each.value.slot_riser1slot1link_speed     # PCIe Slot:Riser1 Slot1 Link Speed
  slot_riser1slot2link_speed     = each.value.slot_riser1slot2link_speed     # PCIe Slot:Riser2 Slot1 Link Speed
  slot_riser1slot3link_speed     = each.value.slot_riser1slot3link_speed     # PCIe Slot:Riser3 Slot1 Link Speed
  slot_riser2link_speed          = each.value.slot_riser2link_speed          # PCIe Slot:Riser2 Link Speed
  slot_riser2slot4link_speed     = each.value.slot_riser2slot4link_speed     # PCIe Slot:Riser2 Slot4 Link Speed
  slot_riser2slot5link_speed     = each.value.slot_riser2slot5link_speed     # PCIe Slot:Riser2 Slot5 Link Speed
  slot_riser2slot6link_speed     = each.value.slot_riser2slot6link_speed     # PCIe Slot:Riser2 Slot6 Link Speed
  slot_sas_state                 = each.value.slot_sas_state                 # PCIe Slot:SAS OptionROM
  slot_ssd_slot1link_speed       = each.value.slot_ssd_slot1link_speed       # PCIe Slot:FrontSSD1 Link Speed
  slot_ssd_slot2link_speed       = each.value.slot_ssd_slot2link_speed       # PCIe Slot:FrontSSD2 Link Speed
  #+++++++++++++++++++++++++++++++
  # Main Section
  #+++++++++++++++++++++++++++++++
  post_error_pause = each.value.post_error_pause # POST Error Pause
  tpm_support      = each.value.tpm_support      # TPM Support
  #+++++++++++++++++++++++++++++++
  # Memory Section
  #+++++++++++++++++++++++++++++++
  advanced_mem_test                     = each.value.advanced_mem_test                     # Enhanced Memory Test
  bme_dma_mitigation                    = each.value.bme_dma_mitigation                    # BME DMA Mitigation
  burst_and_postponed_refresh           = each.value.burst_and_postponed_refresh           # Burst and Postponed Refresh
  cbs_cmn_cpu_smee                      = each.value.cbs_cmn_cpu_smee                      # CPU SMEE
  cbs_cmn_gnb_nb_iommu                  = each.value.cbs_cmn_gnb_nb_iommu                  # IOMMU
  cbs_cmn_mem_ctrl_bank_group_swap_ddr4 = each.value.cbs_cmn_mem_ctrl_bank_group_swap_ddr4 # Bank Group Swap
  cbs_cmn_mem_map_bank_interleave_ddr4  = each.value.cbs_cmn_mem_map_bank_interleave_ddr4  # Chipset Interleave
  cbs_dbg_cpu_snp_mem_cover             = each.value.cbs_dbg_cpu_snp_mem_cover             # SNP Memory Coverage
  cbs_dbg_cpu_snp_mem_size_cover        = each.value.cbs_dbg_cpu_snp_mem_size_cover        # SNP Memory Size to Cover in MiB
  cbs_df_cmn_dram_nps                   = each.value.cbs_df_cmn_dram_nps                   # NUMA Nodes per Socket
  cbs_df_cmn_mem_intlv                  = each.value.cbs_df_cmn_mem_intlv                  # AMD Memory Interleaving
  cbs_df_cmn_mem_intlv_size             = each.value.cbs_df_cmn_mem_intlv_size             # AMD Memory Interleaving Size
  cbs_sev_snp_support                   = each.value.cbs_sev_snp_support                   # SEV-SNP Support
  cke_low_policy                        = each.value.cke_low_policy                        # CKE Low Policy
  cr_qos                                = each.value.cr_qos                                # CR QoS
  crfastgo_config                       = each.value.crfastgo_config                       # CR FastGo Config
  dcpmm_firmware_downgrade              = each.value.dcpmm_firmware_downgrade              # DCPMM Firmware Downgrade
  dram_refresh_rate                     = each.value.dram_refresh_rate                     # DRAM Refresh Rate
  dram_sw_thermal_throttling            = each.value.dram_sw_thermal_throttling            # DRAM SW Thermal Throttling
  eadr_support                          = each.value.eadr_support                          # eADR Support
  lv_ddr_mode                           = each.value.lv_ddr_mode                           # Low Voltage DDR Mode
  memory_bandwidth_boost                = each.value.memory_bandwidth_boost                # Memory Bandwidth Boost
  memory_refresh_rate                   = each.value.memory_refresh_rate                   # Memory Refresh Rate
  memory_size_limit                     = each.value.memory_size_limit                     # Memory Size Limit in GiB
  memory_thermal_throttling             = each.value.memory_thermal_throttling             # Memory Thermal Throttling Mode
  mirroring_mode                        = each.value.mirroring_mode                        # Mirroring Mode
  numa_optimized                        = each.value.numa_optimized                        # NUMA Optimized
  nvmdimm_perform_config                = each.value.nvmdimm_perform_config                # NVM Performance Setting
  operation_mode                        = each.value.operation_mode                        # Operation Mode
  panic_high_watermark                  = each.value.panic_high_watermark                  # Panic and High Watermark
  partial_cache_line_sparing            = each.value.partial_cache_line_sparing            # Partial Cache Line Sparing
  partial_mirror_mode_config            = each.value.partial_mirror_mode_config            # Partial Memory Mirror Mode
  partial_mirror_percent                = each.value.partial_mirror_percent                # Partial Mirror Percentage
  partial_mirror_value1                 = each.value.partial_mirror_value1                 # Partial Mirror1 Size in GiB
  partial_mirror_value2                 = each.value.partial_mirror_value2                 # Partial Mirror2 Size in GiB
  partial_mirror_value3                 = each.value.partial_mirror_value3                 # Partial Mirror3 Size in GiB
  partial_mirror_value4                 = each.value.partial_mirror_value4                 # Partial Mirror4 Size in GiB
  pc_ie_ras_support                     = each.value.pc_ie_ras_support                     # PCIe RAS Support
  post_package_repair                   = each.value.post_package_repair                   # Post Package Repair
  select_memory_ras_configuration       = each.value.select_memory_ras_configuration       # Memory RAS Configuration
  select_ppr_type                       = each.value.select_ppr_type                       # PPR Type
  sev                                   = each.value.sev                                   # Secured Encrypted Virtualization
  smee                                  = each.value.smee                                  # SMEE
  snoopy_mode_for2lm                    = each.value.snoopy_mode_for2lm                    # Snoopy Mode for 2LM
  snoopy_mode_for_ad                    = each.value.snoopy_mode_for_ad                    # Snoopy Mode for AD
  sparing_mode                          = each.value.sparing_mode                          # Sparing Mode
  tsme                                  = each.value.tsme                                  # Transparent Secure Memory Encryption
  uma_based_clustering                  = each.value.uma_based_clustering                  # UMA Based Clustering
  vol_memory_mode                       = each.value.vol_memory_mode                       # Volatile Memory Mode
  #+++++++++++++++++++++++++++++++
  # PCI Section
  #+++++++++++++++++++++++++++++++
  aspm_support               = each.value.aspm_support               # ASPM Support
  ioh_resource               = each.value.ioh_resource               # IOH Resource Allocation
  memory_mapped_io_above4gb  = each.value.memory_mapped_io_above4gb  # Memory Mapped IO Above 4GiB
  mmcfg_base                 = each.value.mmcfg_base                 # MMCFG BASE
  onboard10gbit_lom          = each.value.onboard10gbit_lom          # Onboard 10Gbit LOM
  onboard_gbit_lom           = each.value.onboard_gbit_lom           # Onboard Gbit LOM
  pc_ie_ssd_hot_plug_support = each.value.pc_ie_ssd_hot_plug_support # NVMe SSD Hot-Plug Support
  sr_iov                     = each.value.sr_iov                     # SR-IOV Support
  vga_priority               = each.value.vga_priority               # VGA Priority
  #+++++++++++++++++++++++++++++++
  # Power and Performance Section
  #+++++++++++++++++++++++++++++++
  cbs_cmn_cpu_cpb                    = each.value.cbs_cmn_cpu_cpb                    # Core Performance Boost
  cbs_cmn_cpu_global_cstate_ctrl     = each.value.cbs_cmn_cpu_global_cstate_ctrl     # Global C State Control
  cbs_cmn_cpu_l1stream_hw_prefetcher = each.value.cbs_cmn_cpu_l1stream_hw_prefetcher # L1 Stream HW Prefetcher
  cbs_cmn_cpu_l2stream_hw_prefetcher = each.value.cbs_cmn_cpu_l2stream_hw_prefetcher # L2 Stream HW Prefetcher
  cbs_cmn_determinism_slider         = each.value.cbs_cmn_determinism_slider         # Determinism Slider
  cbs_cmn_efficiency_mode_en         = each.value.cbs_cmn_efficiency_mode_en         # Efficiency Mode Enable
  cbs_cmn_gnb_smucppc                = each.value.cbs_cmn_gnb_smucppc                # CPPC
  cbs_cmnc_tdp_ctl                   = each.value.cbs_cmnc_tdp_ctl                   # cTDP Control
  #+++++++++++++++++++++++++++++++
  # Processor Section
  #+++++++++++++++++++++++++++++++
  adjacent_cache_line_prefetch      = each.value.adjacent_cache_line_prefetch      # Adjacent Cache Line Prefetcher
  altitude                          = each.value.altitude                          # Altitude
  auto_cc_state                     = each.value.auto_cc_state                     # Autonomous Core C State
  autonumous_cstate_enable          = each.value.autonumous_cstate_enable          # CPU Autonomous C State
  boot_performance_mode             = each.value.boot_performance_mode             # Boot Performance Mode
  cbs_cmn_apbdis                    = each.value.cbs_cmn_apbdis                    # APBDIS
  cbs_cmn_cpu_gen_downcore_ctrl     = each.value.cbs_cmn_cpu_gen_downcore_ctrl     # Downcore Control
  cbs_cmn_cpu_streaming_stores_ctrl = each.value.cbs_cmn_cpu_streaming_stores_ctrl # Streaming Stores Control
  cbs_cmn_fixed_soc_pstate          = each.value.cbs_cmn_fixed_soc_pstate          # Fixed SOC P-State
  cbs_cmn_gnb_smu_df_cstates        = each.value.cbs_cmn_gnb_smu_df_cstates        # DF C-States
  cbs_cpu_ccd_ctrl_ssp              = each.value.cbs_cpu_ccd_ctrl_ssp              # CCD Control
  cbs_cpu_core_ctrl                 = each.value.cbs_cpu_core_ctrl                 # CPU Downcore Control
  cbs_cpu_smt_ctrl                  = each.value.cbs_cpu_smt_ctrl                  # CPU SMT Mode
  cbs_df_cmn_acpi_srat_l3numa       = each.value.cbs_df_cmn_acpi_srat_l3numa       # ACPI SRAT L3 Cache As NUMA Domain
  channel_inter_leave               = each.value.channel_inter_leave               # Channel Interleaving
  cisco_xgmi_max_speed              = each.value.cisco_xgmi_max_speed              # Cisco xGMI Max Speed
  closed_loop_therm_throtl          = each.value.closed_loop_therm_throtl          # Closed Loop Thermal Throttling
  cmci_enable                       = each.value.cmci_enable                       # Processor CMCI
  config_tdp                        = each.value.config_tdp                        # Config TDP
  config_tdp_level                  = each.value.config_tdp_level                  # Configurable TDP Level
  core_multi_processing             = each.value.core_multi_processing             # Core Multi Processing
  cpu_energy_performance            = each.value.cpu_energy_performance            # Energy Performance
  cpu_frequency_floor               = each.value.cpu_frequency_floor               # Frequency Floor Override
  cpu_performance                   = each.value.cpu_performance                   # CPU Performance
  cpu_power_management = length(
    regexall("(DSS|Java|OLTP|Virtualization)", each.value.bios_template)
  ) > 0 ? "custom" : each.value.cpu_power_management                         # Power Technology
  demand_scrub                   = each.value.demand_scrub                   # Demand Scrub
  direct_cache_access            = each.value.direct_cache_access            # Direct Cache Access Support
  dram_clock_throttling          = each.value.dram_clock_throttling          # DRAM Clock Throttling
  energy_efficient_turbo         = each.value.energy_efficient_turbo         # Energy Efficient Turbo
  eng_perf_tuning                = each.value.eng_perf_tuning                # Energy Performance Tuning
  enhanced_intel_speed_step_tech = each.value.enhanced_intel_speed_step_tech # Enhanced Intel Speedstep(R) Technology
  epp_enable                     = each.value.epp_enable                     # Processor EPP Enable
  epp_profile                    = each.value.epp_profile                    # EPP Profile
  execute_disable_bit            = each.value.execute_disable_bit            # Execute Disable Bit
  extended_apic                  = each.value.extended_apic                  # Local X2 Apic
  hardware_prefetch              = each.value.hardware_prefetch              # Hardware Prefetcher
  hwpm_enable                    = each.value.hwpm_enable                    # CPU Hardware Power Management
  imc_interleave                 = each.value.imc_interleave                 # IMC Interleaving
  intel_dynamic_speed_select     = each.value.intel_dynamic_speed_select     # Intel Dynamic Speed Select
  intel_hyper_threading_tech = length(
    regexall("(HPC)", each.value.bios_template)
  ) > 0 ? "disabled" : each.value.intel_hyper_threading_tech # Intel HyperThreading Tech
  intel_speed_select     = each.value.intel_speed_select     # Intel Speed Select
  intel_turbo_boost_tech = each.value.intel_turbo_boost_tech # Intel Turbo Boost Tech
  intel_virtualization_technology = length(                  # Intel(R) VT
    regexall("(HPC|Java)", each.value.bios_template)
  ) > 0 ? "disabled" : each.value.intel_virtualization_technology
  ioh_error_enable      = each.value.ioh_error_enable      # IIO Error Enable
  ip_prefetch           = each.value.ip_prefetch           # DCU IP Prefetcher
  kti_prefetch          = each.value.kti_prefetch          # KTI Prefetch
  llc_prefetch          = each.value.llc_prefetch          # LLC Prefetch
  memory_inter_leave    = each.value.memory_inter_leave    # Intel Memory Interleaving
  package_cstate_limit  = each.value.package_cstate_limit  # Package C State Limit
  patrol_scrub          = each.value.patrol_scrub          # Patrol Scrub
  patrol_scrub_duration = each.value.patrol_scrub_duration # Patrol Scrub Interval
  processor_c1e = length(                                  # Processor C1E
    regexall("(DSS|Java|OLTP|Virtualization)", each.value.bios_template)
  ) > 0 ? "disabled" : each.value.processor_c1e
  processor_c3report = length(
    regexall("(DSS|Java|OLTP|Virtualization)", each.value.bios_template)
  ) > 0 ? "disabled" : each.value.processor_c3report # Processor C3 Report
  processor_c6report = length(
    regexall("(DSS|Java|OLTP|Virtualization)", each.value.bios_template)
  ) > 0 ? "disabled" : each.value.processor_c6report # Processor C6 Report
  processor_cstate = length(
    regexall("(DSS|Java|OLTP|Virtualization)", each.value.bios_template)
  ) > 0 ? "disabled" : each.value.processor_cstate   # CPU C State
  pstate_coord_type  = each.value.pstate_coord_type  # P-State Coordination
  pwr_perf_tuning    = each.value.pwr_perf_tuning    # Power Performance Tuning
  qpi_link_speed     = each.value.qpi_link_speed     # UPI Link Frequency Select
  rank_inter_leave   = each.value.rank_inter_leave   # Rank Interleaving
  single_pctl_enable = each.value.single_pctl_enable # Single PCTL
  smt_mode           = each.value.smt_mode           # SMT Mode
  snc                = each.value.snc                # Sub Numa Clustering
  streamer_prefetch  = each.value.streamer_prefetch  # DCU Streamer Prefetch
  svm_mode           = each.value.svm_mode           # SVM Mode
  ufs_disable        = each.value.ufs_disable        # Uncore Frequency Scaling
  work_load_config = length(                         # Workload Configuration
    regexall("(HPC)", each.value.bios_template)
  ) > 0 ? "Balanced" : each.value.work_load_config
  xpt_prefetch = each.value.xpt_prefetch # XPT Prefetch
  #+++++++++++++++++++++++++++++++
  # QPI Section
  #+++++++++++++++++++++++++++++++
  qpi_link_frequency = each.value.qpi_link_frequency # QPI Link Frequency Select
  qpi_snoop_mode     = each.value.qpi_snoop_mode     # QPI Snoop Mode
  #+++++++++++++++++++++++++++++++
  # Serial Port Section
  #+++++++++++++++++++++++++++++++
  serial_port_aenable = each.value.serial_port_aenable # Serial A Enable
  #+++++++++++++++++++++++++++++++
  # Server Management Section
  #+++++++++++++++++++++++++++++++
  assert_nmi_on_perr              = each.value.assert_nmi_on_perr              # Assert NMI on PERR
  assert_nmi_on_serr              = each.value.assert_nmi_on_serr              # Assert NMI on SERR
  baud_rate                       = each.value.baud_rate                       # Baud Rate
  cdn_enable                      = each.value.cdn_enable                      # Consistent Device Naming
  cisco_adaptive_mem_training     = each.value.cisco_adaptive_mem_training     # Adaptive Memory Training
  cisco_debug_level               = each.value.cisco_debug_level               # BIOS Techlog Level
  cisco_oprom_launch_optimization = each.value.cisco_oprom_launch_optimization # OptionROM Launch Optimization
  console_redirection             = each.value.console_redirection             # Console Redirection
  flow_control                    = each.value.flow_control                    # Flow Control
  frb2enable                      = each.value.frb2enable                      # FRB-2 Timer
  legacy_os_redirection           = each.value.legacy_os_redirection           # Legacy OS Redirection
  os_boot_watchdog_timer          = each.value.os_boot_watchdog_timer          # OS Boot Watchdog Timer
  os_boot_watchdog_timer_policy   = each.value.os_boot_watchdog_timer_policy   # OS Boot Watchdog Timer Policy
  os_boot_watchdog_timer_timeout  = each.value.os_boot_watchdog_timer_timeout  # OS Boot Watchdog Timer Timeout
  out_of_band_mgmt_port           = each.value.out_of_band_mgmt_port           # Out-of-Band Mgmt Port
  putty_key_pad                   = each.value.putty_key_pad                   # Putty KeyPad
  redirection_after_post          = each.value.redirection_after_post          # Redirection After BIOS POST
  terminal_type                   = each.value.terminal_type                   # Terminal Type
  ucsm_boot_order_rule            = each.value.ucsm_boot_order_rule            # Boot Order Rules
  #+++++++++++++++++++++++++++++++
  # Trusted Platform Section
  #+++++++++++++++++++++++++++++++
  enable_mktme                    = each.value.enable_mktme                    # Multikey Total Memory Encryption (MK-TME)
  enable_sgx                      = each.value.enable_sgx                      # Software Guard Extensions
  enable_tme                      = each.value.enable_tme                      # Total Memory Encryption
  epoch_update                    = each.value.epoch_update                    # Select Owner EPOCH Input Type
  sgx_auto_registration_agent     = each.value.sgx_auto_registration_agent     # SGX Auto MP Registration Agent
  sgx_epoch0                      = each.value.sgx_epoch0                      # SGX Epoch 0
  sgx_epoch1                      = each.value.sgx_epoch1                      # SGX Epoch 1
  sgx_factory_reset               = each.value.sgx_factory_reset               # SGX Factory Reset
  sgx_le_pub_key_hash0            = each.value.sgx_le_pub_key_hash0            # SGX PubKey Hash0
  sgx_le_pub_key_hash1            = each.value.sgx_le_pub_key_hash1            # SGX PubKey Hash1
  sgx_le_pub_key_hash2            = each.value.sgx_le_pub_key_hash2            # SGX PubKey Hash2
  sgx_le_pub_key_hash3            = each.value.sgx_le_pub_key_hash3            # SGX PubKey Hash3
  sgx_le_wr                       = each.value.sgx_le_wr                       # SGX Write Eanble
  sgx_package_info_in_band_access = each.value.sgx_package_info_in_band_access # SGX Package Information In-Band Access
  sgx_qos                         = each.value.sgx_qos                         # SGX QoS
  tpm_control                     = each.value.tpm_control                     # Trusted Platform Module State
  tpm_pending_operation           = each.value.tpm_pending_operation           # TPM Pending Operation
  txt_support                     = each.value.txt_support                     # Intel Trusted Execution Technology Support
  #+++++++++++++++++++++++++++++++
  # USB Section
  #+++++++++++++++++++++++++++++++
  all_usb_devices          = each.value.all_usb_devices          # All USB Devices
  legacy_usb_support       = each.value.legacy_usb_support       # Legacy USB Support
  make_device_non_bootable = each.value.make_device_non_bootable # Make Device Non Bootable
  pch_usb30mode            = each.value.pch_usb30mode            # xHCI Mode
  usb_emul6064             = each.value.usb_emul6064             # Port 60/64 Emulation
  usb_port_front           = each.value.usb_port_front           # USB Port Front
  usb_port_internal        = each.value.usb_port_internal        # USB Port Internal
  usb_port_kvm             = each.value.usb_port_kvm             # USB Port KVM
  usb_port_rear            = each.value.usb_port_rear            # USB Port Rear
  usb_port_sd_card         = each.value.usb_port_sd_card         # USB Port SD Card
  usb_port_vmedia          = each.value.usb_port_vmedia          # USB Port VMedia
  usb_xhci_support         = each.value.usb_xhci_support         # XHCI Legacy Support
}
