#______________________________________________
#
# BIOS Policy Variables
#______________________________________________

bios_policies = {
  "CEPH" = {
    bios_template = ""
    description   = "BIOS-Policy-for-Analytics-Database-Decision-Support-System-on-Cisco-UCS-M5-Servers-with-VT-Enabled-for-CEPH"
    organization  = "UCS-DEMO2_CAGIP"
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
    cisco_adaptive_mem_training = "enabled",
    cpu_energy_performance = "performance",
    cpu_power_management = "custom",
    intel_vt_for_directed_io = "enabled",
    processor_c1e = "disabled",
    processor_c3report = "disabled",
    processor_c6report = "disabled",
    processor_cstate = "disabled",
    work_load_config = "I/O Sensitive",
  }
  "DSS-M5" = {
    bios_template = ""
    description   = "BIOS-Policy-for-Analytics-Database-Decision-Support-System-on-Cisco-UCS-M5-Servers"
    organization  = "UCS-DEMO2_CAGIP"
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
    cisco_adaptive_mem_training = "enabled",
    cpu_energy_performance = "performance",
    cpu_power_management = "custom",
    intel_vt_for_directed_io = "disabled",
    processor_c1e = "disabled",
    processor_c3report = "disabled",
    processor_c6report = "disabled",
    processor_cstate = "disabled",
    work_load_config = "I/O Sensitive",
  }
  "Virtu-M5" = {
    bios_template = ""
    description   = "BIOS-Policy-for-Virtualization-on-Cisco-UCS-M5-Servers"
    organization  = "UCS-DEMO2_CAGIP"
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
    cisco_adaptive_mem_training = "enabled",
    cpu_power_management = "custom",
    processor_c1e = "disabled",
    processor_c3report = "disabled",
    processor_c6report = "disabled",
    processor_cstate = "disabled",
  }
}