#______________________________________________
#
# BIOS Policy Variables
#______________________________________________

bios_policies = {
  "HyperFlex" = {
    bios_template = ""
    description   = ""
    organization  = "UCS-DEMO2_hyperflex"
    tags         = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
    # BIOS Customization Settings
    altitude = "auto",
    console_redirection = "serial-port-a",
    cpu_energy_performance = "performance",
    cpu_performance = "hpc",
    cpu_power_management = "performance",
    direct_cache_access = "enabled",
    intel_virtualization_technology = "enabled",
    intel_vt_for_directed_io = "enabled",
    intel_vtd_coherency_support = "disabled",
    intel_vtd_interrupt_remapping = "enabled",
    memory_mapped_io_above4gb = "enabled",
    out_of_band_mgmt_port = "enabled",
    processor_c1e = "disabled",
    processor_c3report = "disabled",
    processor_c6report = "disabled",
    processor_cstate = "disabled",
    serial_port_aenable = "enabled",
  }
  "HyperFlex-m5" = {
    bios_template = ""
    description   = ""
    organization  = "UCS-DEMO2_hyperflex"
    tags         = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
    # BIOS Customization Settings
    altitude = "auto",
    console_redirection = "serial-port-a",
    cpu_energy_performance = "performance",
    cpu_performance = "hpc",
    cpu_power_management = "performance",
    direct_cache_access = "enabled",
    imc_interleave = "Auto",
    intel_virtualization_technology = "enabled",
    intel_vt_for_directed_io = "enabled",
    intel_vtd_coherency_support = "disabled",
    intel_vtd_interrupt_remapping = "enabled",
    llc_prefetch = "disabled",
    lom_port0state = "disabled",
    lom_port1state = "disabled",
    lom_ports_all_state = "disabled",
    memory_mapped_io_above4gb = "enabled",
    out_of_band_mgmt_port = "enabled",
    processor_c1e = "disabled",
    processor_c3report = "disabled",
    processor_c6report = "disabled",
    processor_cstate = "disabled",
    serial_port_aenable = "enabled",
    snc = "disabled",
    xpt_prefetch = "disabled",
  }
  "HyperFlex-nvme" = {
    bios_template = ""
    description   = ""
    organization  = "UCS-DEMO2_hyperflex"
    tags         = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
    # BIOS Customization Settings
    altitude = "auto",
    console_redirection = "serial-port-a",
    cpu_energy_performance = "performance",
    cpu_performance = "hpc",
    cpu_power_management = "performance",
    direct_cache_access = "enabled",
    imc_interleave = "Auto",
    intel_virtualization_technology = "enabled",
    intel_vt_for_directed_io = "enabled",
    intel_vtd_coherency_support = "disabled",
    intel_vtd_interrupt_remapping = "enabled",
    llc_prefetch = "disabled",
    lom_port0state = "disabled",
    lom_port1state = "disabled",
    lom_ports_all_state = "disabled",
    memory_mapped_io_above4gb = "enabled",
    out_of_band_mgmt_port = "enabled",
    processor_c1e = "disabled",
    processor_c3report = "disabled",
    processor_c6report = "disabled",
    processor_cstate = "disabled",
    serial_port_aenable = "enabled",
    snc = "disabled",
    vmd_enable = "enabled",
    xpt_prefetch = "disabled",
  }
}