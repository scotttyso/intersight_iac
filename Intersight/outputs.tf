output "domain_profiles" {
  description = "Domain Profile Outputs: including cluster and switch Moids, policy assignments."
  value       = module.domain_profiles
}

output "policies" {
  description = "The Name of Each Policy Created with it's respective Moid."
  value       = module.policies
}

output "pools" {
  description = "The Name of Each Pool Created with it's respective Moid."
  value       = module.pools
}

output "profiles" {
  description = "The Name of Each Profile Created with it's respective Moid."
  value       = module.profiles
}
