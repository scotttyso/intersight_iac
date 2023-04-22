kwargs = {}
#=====================================================
# Determine the uri to Create
#=====================================================
if 'bulk' in kwargs.policy:                  uri = 'bulk/MoCloners'
elif 'firmware' in kwargs.purpose:
    if 'distributables' == kwargs.policy:uri = 'firmware/Distributables'
    elif 'eula' == kwargs.policy:        uri = 'firmware/Eulas'
    elif 'running' == kwargs.policy:     uri = 'firmware/RunningFirmwares'
    elif 'status' == kwargs.policy:      uri = 'firmware/RunningFirmwares'
    elif 'upgrade' == kwargs.policy:     uri = 'firmware/Upgrades'
    elif 'auth' == kwargs.policy:        uri = 'softwarerepository/Authorizations'
elif 'hcl_status' in kwargs.policy:    uri = 'cond/HclStatuses'
