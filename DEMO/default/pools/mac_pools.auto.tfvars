#______________________________________________
#
# MAC Pool Variables
#______________________________________________

mac_pools = {
  "DATA-A" = {
    assignment_order = "sequential"
    mac_blocks = {
      "1" = {
        from = "00:25:B5:00:10:00"
        size = 1000
        # to   = "00:25:B5:00:13:E7"
      },
    }
    organization = "default"
    tags         = []
  }
  "DATA-B" = {
    assignment_order = "sequential"
    mac_blocks = {
      "1" = {
        from = "00:25:B5:00:20:00"
        size = 1000
        # to   = "00:25:B5:00:23:E7"
      },
    }
    organization = "default"
    tags         = []
  }
  "MGMT-A" = {
    assignment_order = "sequential"
    mac_blocks = {
      "1" = {
        from = "00:25:B5:00:A0:00"
        size = 1000
        # to   = "00:25:B5:00:A3:E7"
      },
    }
    organization = "default"
    tags         = []
  }
  "MGMT-B" = {
    assignment_order = "sequential"
    mac_blocks = {
      "1" = {
        from = "00:25:B5:00:B0:00"
        size = 1000
        # to   = "00:25:B5:00:B3:E7"
      },
    }
    organization = "default"
    tags         = []
  }
  "VMOTION-A" = {
    assignment_order = "sequential"
    mac_blocks = {
      "1" = {
        from = "00:25:B5:00:C0:00"
        size = 1000
        # to   = "00:25:B5:00:C3:E7"
      },
    }
    organization = "default"
    tags         = []
  }
  "VMOTION-B" = {
    assignment_order = "sequential"
    mac_blocks = {
      "1" = {
        from = "00:25:B5:00:D0:00"
        size = 1000
        # to   = "00:25:B5:00:D3:E7"
      },
    }
    organization = "default"
    tags         = []
  }
  "STORAGE-A" = {
    assignment_order = "sequential"
    mac_blocks = {
      "1" = {
        from = "00:25:B5:00:E0:00"
        size = 1000
        # to   = "00:25:B5:00:E3:E7"
      },
    }
    organization = "default"
    tags         = []
  }
  "STORAGE-B" = {
    assignment_order = "sequential"
    mac_blocks = {
      "1" = {
        from = "00:25:B5:00:F0:00"
        size = 1000
        # to   = "00:25:B5:00:F3:E7"
      },
    }
    organization = "default"
    tags         = []
  }
}