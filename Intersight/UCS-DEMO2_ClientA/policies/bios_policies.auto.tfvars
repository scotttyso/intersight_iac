#______________________________________________
#
# BIOS Policy Variables
#______________________________________________

bios_policies = {
  "ESX" = {
    bios_template = ""
    description   = ""
    organization  = "UCS-DEMO2_ClientA"
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
    enhanced_intel_speed_step_tech = "disabled",
    execute_disable_bit = "enabled",
    intel_hyper_threading_tech = "enabled",
    intel_turbo_boost_tech = "disabled",
    intel_virtualization_technology = "enabled",
    intel_vt_for_directed_io = "enabled",
    intel_vtd_interrupt_remapping = "enabled",
  }
}