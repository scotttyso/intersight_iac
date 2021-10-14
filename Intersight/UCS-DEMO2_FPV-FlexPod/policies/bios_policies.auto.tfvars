#______________________________________________
#
# BIOS Policy Variables
#______________________________________________

bios_policies = {
  "Virtual-Host" = {
    bios_template = ""
    description   = ""
    organization  = "UCS-DEMO2_FPV-FlexPod"
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
    cdn_enable = "enabled",
    cpu_energy_performance = "performance",
    cpu_frequency_floor = "enabled",
    dram_clock_throttling = "Performance",
    lv_ddr_mode = "performance-mode",
    processor_c1e = "disabled",
    processor_c3report = "disabled",
    processor_cstate = "disabled",
  }
}