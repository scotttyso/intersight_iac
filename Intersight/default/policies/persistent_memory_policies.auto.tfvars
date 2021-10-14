#______________________________________________
#
# Persistent Memory Policy Variables
#______________________________________________

persistent_memory_policies = {
  "Asgard_persistent_memory" = {
    description            = "Asgard_persistent_memory Persistent Memory Policy"
    organization           = "default"
    management_mode        = "configured-from-intersight"
    # GOALS
    memory_mode_percentage = 10
    persistent_memory_type = "app-direct"
    # NAMESPACES
    namespaces = {
      "socket_1" = {
        capacity         = 512000
        mode             = "block"
        socket_id        = 1
        socket_memory_id = "Not Applicable"
      },
      "socket_2" = {
        capacity         = 512000
        mode             = "block"
        socket_id        = 2
        socket_memory_id = "Not Applicable"
      },
    }
    retain_namespaces  = true
    tags                     = []
  }
}