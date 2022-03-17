terraform {
  experiments = [module_variable_optional_attrs]
}

#__________________________________________________________
#
# Terraform Workspace Variables
#__________________________________________________________

variable "tfc_workspaces" {
  default = [
    {
      backend             = "remote"
      tfc_organization    = "default"
      domain_profiles_dir = "../ucs_domain_profiles/"
      domain_profiles_ws  = "default_ucs_domain_profiles"
      pools_dir           = "../pools/"
      pools_ws            = "default_pools"
    }
  ]
  description = <<-EOT
  * backend: Options are:
    - local - The backend is on the Local Machine
    - Remote - The backend is in TFCB.
  * tfc_organization: Name of the Terraform Cloud Organization
  * doman_profiles_dir: Name of the UCS Domain Profiles directory when the backend is local.
  * doman_profiles_ws: Name of the UCS Domain Profiles workspace in Terraform Cloud.
  * pools_dir: Name of the Pools directory when the backend is local.
  * pools_ws: Name of the Pools workspace in Terraform Cloud.
  EOT
  type = list(object(
    {
      backend             = string
      tfc_organization    = optional(string)
      domain_profiles_dir = optional(string)
      domain_profiles_ws  = optional(string)
      pools_dir           = optional(string)
      pools_ws            = optional(string)
    }
  ))
}


#__________________________________________________________
#
# Intersight Provider Variables
#__________________________________________________________

variable "apikey" {
  description = "Intersight API Key."
  sensitive   = true
  type        = string
}

variable "endpoint" {
  default     = "https://intersight.com"
  description = "Intersight URL."
  type        = string
}

variable "secretkey" {
  description = "Intersight Secret Key."
  sensitive   = true
  type        = string
}


#__________________________________________________________
#
# Global Variables
#__________________________________________________________

variable "organization" {
  default     = "default"
  description = "Intersight Organization Names to Apply Policy to.  https://intersight.com/an/settings/organizations/."
  type        = string
}

variable "tags" {
  default     = []
  description = "List of Key/Value Pairs to Assign as Attributes to the Policy."
  type        = list(map(string))
}
