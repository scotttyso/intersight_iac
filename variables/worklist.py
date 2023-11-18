#!/usr/bin/env python3
import json
#=====================================================
# Build Windows Timezone to IANA Dictionary
#=====================================================
windows_timezones = {}
file = './workflow.json'
data = json.load(open(file, 'r'))
print(json.dumps(data['Results'][0]['TypeDefinition'][0]['Properties']['Constraints']['EnumList'][140], indent=4))
exit()
