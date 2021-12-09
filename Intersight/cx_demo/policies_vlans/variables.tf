terraform {
  experiments = [module_variable_optional_attrs]
}

#__________________________________________________________
#
# Terraform Cloud Variables
#__________________________________________________________

variable "tfc_organization" {
  description = "Terraform Cloud Organization Name."
  type        = string
}

variable "ws_ucs_domain_profiles" {
  default     = "ucs_domain_profiles"
  description = "Name of the UCS Domain Profiles workspace."
  type        = string
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

variable "organizations" {
  default     = ["default"]
  description = "Intersight Organization Names."
  type        = set(string)
}

variable "tags" {
  default     = []
  description = "List of Key/Value Pairs to Assign as Attributes to the Policy."
  type        = list(map(string))
}


