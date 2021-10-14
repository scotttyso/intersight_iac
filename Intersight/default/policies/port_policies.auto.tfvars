#______________________________________________
#
# Port Policy Variables
#______________________________________________

port_policies = {
  "asgard-ucs_A" = {
    description  = "asgard-ucs Port Policy"
    device_model = "UCS-FI-64108"
    organization = "default"
    port_channel_appliances = {
      "95" = {
        admin_speed                     = "Auto"
        ethernet_network_control_policy = "Asgard_netwk_ctrl"
        ethernet_network_group_policy   = "Asgard_Storage"
        interfaces = [
          {
            port_id          = 95
            slot_id          = 1
          },
          {
            port_id          = 96
            slot_id          = 1
          },
        ]
        mode     = "trunk"
        priority = "Platinum"
      }
    }
    port_channel_ethernet_uplinks = {
      "97" = {
        admin_speed         = "Auto"
        flow_control_policy = "asgard-ucs_flow_ctrl"
        interfaces = [
          {
            port_id          = 97
            slot_id          = 1
          },
          {
            port_id          = 98
            slot_id          = 1
          },
        ]
        link_aggregation_policy = "asgard-ucs_link_agg"
        link_control_policy     = "asgard-ucs_link_ctrl"
      }
    }
    port_channel_fc_uplinks = {
      "1" = {
        admin_speed  = "32Gbps"
        fill_pattern = "Arbff"
        interfaces = [
          {
            port_id          = 1
            slot_id          = 1
          },
          {
            port_id          = 2
            slot_id          = 1
          },
        ]
        vsan_id = "100"
      }
    }
    port_channel_fcoe_uplinks = {
      "99" = {
        admin_speed = "Auto"
        interfaces = [
          {
            port_id          = 99
            slot_id          = 1
          },
          {
            port_id          = 100
            slot_id          = 1
          },
        ]
        link_aggregation_policy = "asgard-ucs_link_agg"
        link_control_policy     = "asgard-ucs_link_ctrl"
      }
    }
    port_modes = [
      {
        custom_mode = "FibreChannel"
        port_list   = [1, 4]
        slot_id     = 1
      }
    ]
    port_role_appliances = {
      "1" = {
        admin_speed                     = "Auto"
        ethernet_network_control_policy = "Asgard_netwk_ctrl"
        ethernet_network_group_policy   = "Asgard_Storage"
        fec                             = "Auto"
        mode                            = "trunk"
        port_list                       = "94"
        priority                        = "Platinum"
        slot_id                         = 1
      }
    }
    port_role_ethernet_uplinks = {
      "1" = {
        admin_speed         = "Auto"
        fec                 = "Auto"
        flow_control_policy = "asgard-ucs_flow_ctrl"
        link_control_policy = "asgard-ucs_link_ctrl"
        port_list           = "101"
        slot_id             = 1
      }
    }
    port_role_fc_uplinks = {
      "1" = {
        admin_speed      = "32Gbps"
        fill_pattern     = "Arbff"
        port_list        = "3"
        slot_id          = 1
        vsan_id          = "100"
      }
    }
    port_role_fcoe_uplinks = {
      "1" = {
        admin_speed         = "Auto"
        fec                 = "Auto"
        link_control_policy = "asgard-ucs_link_ctrl"
        port_list           = "102"
        slot_id             = 1
      }
    }
    port_role_servers = {
      "1" = {
        port_list           = "5-36"
        slot_id             = 1
      }
    }
    tags         = []
  }
  "asgard-ucs_B" = {
    description  = "asgard-ucs Port Policy"
    device_model = "UCS-FI-64108"
    organization = "default"
    port_channel_appliances = {
      "95" = {
        admin_speed                     = "Auto"
        ethernet_network_control_policy = "Asgard_netwk_ctrl"
        ethernet_network_group_policy   = "Asgard_Storage"
        interfaces = [
          {
            port_id          = 95
            slot_id          = 1
          },
          {
            port_id          = 96
            slot_id          = 1
          },
        ]
        mode     = "trunk"
        priority = "Platinum"
      }
    }
    port_channel_ethernet_uplinks = {
      "97" = {
        admin_speed         = "Auto"
        flow_control_policy = "asgard-ucs_flow_ctrl"
        interfaces = [
          {
            port_id          = 97
            slot_id          = 1
          },
          {
            port_id          = 98
            slot_id          = 1
          },
        ]
        link_aggregation_policy = "asgard-ucs_link_agg"
        link_control_policy     = "asgard-ucs_link_ctrl"
      }
    }
    port_channel_fc_uplinks = {
      "1" = {
        admin_speed  = "32Gbps"
        fill_pattern = "Arbff"
        interfaces = [
          {
            port_id          = 1
            slot_id          = 1
          },
          {
            port_id          = 2
            slot_id          = 1
          },
        ]
        vsan_id = "200"
      }
    }
    port_channel_fcoe_uplinks = {
      "99" = {
        admin_speed = "Auto"
        interfaces = [
          {
            port_id          = 99
            slot_id          = 1
          },
          {
            port_id          = 100
            slot_id          = 1
          },
        ]
        link_aggregation_policy = "asgard-ucs_link_agg"
        link_control_policy     = "asgard-ucs_link_ctrl"
      }
    }
    port_modes = [
      {
        custom_mode = "FibreChannel"
        port_list   = [1, 4]
        slot_id     = 1
      }
    ]
    port_role_appliances = {
      "1" = {
        admin_speed                     = "Auto"
        ethernet_network_control_policy = "Asgard_netwk_ctrl"
        ethernet_network_group_policy   = "Asgard_Storage"
        fec                             = "Auto"
        mode                            = "trunk"
        port_list                       = "94"
        priority                        = "Platinum"
        slot_id                         = 1
      }
    }
    port_role_ethernet_uplinks = {
      "1" = {
        admin_speed         = "Auto"
        fec                 = "Auto"
        flow_control_policy = "asgard-ucs_flow_ctrl"
        link_control_policy = "asgard-ucs_link_ctrl"
        port_list           = "101"
        slot_id             = 1
      }
    }
    port_role_fc_uplinks = {
      "1" = {
        admin_speed      = "32Gbps"
        fill_pattern     = "Arbff"
        port_list        = "3"
        slot_id          = 1
        vsan_id          = "200"
      }
    }
    port_role_fcoe_uplinks = {
      "1" = {
        admin_speed         = "Auto"
        fec                 = "Auto"
        link_control_policy = "asgard-ucs_link_ctrl"
        port_list           = "102"
        slot_id             = 1
      }
    }
    port_role_servers = {
      "1" = {
        port_list           = "5-36"
        slot_id             = 1
      }
    }
    tags         = []
  }
}