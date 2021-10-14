#______________________________________________
#
# Flow Control Policy Variables
#______________________________________________

flow_control_policies = {
  "asgard-ucs_flow_ctrl" = {
    description  = "asgard-ucs_flow_ctrl Flow Control Policy"
    organization = "default"
    priority     = "auto"
    receive      = "Enabled"
    send         = "Enabled"
    tags         = []
  }
}