#______________________________________________
#
# SSH Policy Variables
#______________________________________________

ssh_policies = {
  "Asgard_ssh" = {
    description  = "Asgard_ssh SSH Policy"
    enable_ssh   = true
    organization = "default"
    ssh_port     = 22
    ssh_timeout  = 1800
    tags         = []
  }
}