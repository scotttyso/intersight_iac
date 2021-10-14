#______________________________________________
#
# IQN Pool Variables
#______________________________________________

iqn_pools = {
  "IQN-Pool" = {
    assignment_order  = "default"
    organization      = "UCS-DEMO2"
    prefix            = "iqn.2010-11.com.flexpod"
    iqn_suffix_blocks = [
      {
        from = "1",
        suffix = "aa13-6332-host",
        size = "16",
      },
    ]
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
  "ocb-poc" = {
    assignment_order  = "default"
    organization      = "UCS-DEMO2"
    prefix            = "iqn.2020.local.ocb-poc"
    iqn_suffix_blocks = [
      {
        from = "1",
        suffix = "esxi",
        size = "50",
      },
    ]
    tags = [
      {
        key = "easyucs_origin",
        value = "convert",
      },
      {
        key = "easyucs_version",
        value = "0.9.8",
      },
    ]
  }
}