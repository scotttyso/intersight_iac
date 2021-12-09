#__________________________________________________________
#
# Local Variables Section
#__________________________________________________________

locals {
  # Intersight Organization Variables
  organizations = var.organizations
  org_moids = {
    for v in sort(keys(data.intersight_organization_organization.org_moid)) : v => {
      moid = data.intersight_organization_organization.org_moid[v].results[0].moid
    }
  }

  # Tags for Deployment
  tags = var.tags

  #__________________________________________________________
  #
  # UCS Chassis Profiles Section - Locals
  #__________________________________________________________
  ucs_chassis_profiles = {
    for k, v in var.ucs_chassis_profiles : k => {
      action              = v.action != null ? v.action : "No-op"
      assign_chassis      = v.assign_chassis != null ? v.assign_chassis : false
      description         = v.description != null ? v.description : ""
      organization        = v.organization != null ? v.organization : "default"
      imc_access_policy   = v.imc_access_policy != null ? v.imc_access_policy : ""
      power_policy        = v.power_policy != null ? v.power_policy : ""
      serial_number       = v.serial_number != null ? v.serial_number : ""
      snmp_policy         = v.snmp_policy != null ? v.snmp_policy : ""
      thermal_policy      = v.thermal_policy != null ? v.thermal_policy : ""
      tags                = v.tags != null ? v.tags : []
      target_platform     = v.target_platform != null ? v.target_platform : "FIAttached"
      wait_for_completion = v.wait_for_completion != null ? v.wait_for_completion : false
    }
  }


}
