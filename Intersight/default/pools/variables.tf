terraform {
  experiments = [module_variable_optional_attrs]
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
  description = "Tags to be Associated with Objects Created in Intersight."
  type        = list(map(string))
}


