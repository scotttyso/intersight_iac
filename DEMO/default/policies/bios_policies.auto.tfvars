#______________________________________________
#
# BIOS Policy Variables
#______________________________________________

bios_policies = {
  "M5_VMware" = {
    bios_template = "Virtualization"
    description   = "M5_VMware BIOS Policy"
    organization  = "default"
    tags          = []
    # BIOS Customization Settings
    execute_disable_bit = "disabled",
    lv_ddr_mode         = "Auto",
    serial_port_aenable = "disabled",
  }
  "M5_VMware_tpm" = {
    bios_template = "Virtualization_tpm"
    description   = "M5_VMware_tpm BIOS Policy"
    organization  = "default"
    tags          = []
    # BIOS Customization Settings
    execute_disable_bit = "disabled",
    lv_ddr_mode         = "Auto",
    serial_port_aenable = "disabled",
  }
  "M6_VMware_tpm" = {
    bios_template = "M6_Virtualization_tpm"
    description   = "M6_VMware_tpm BIOS Policy"
    organization  = "default"
    tags          = []
    # BIOS Customization Settings
    execute_disable_bit = "disabled",
    lv_ddr_mode         = "Auto",
    serial_port_aenable = "disabled",
  }
}