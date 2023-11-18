#!/usr/bin/env python3
import json
#=====================================================
# Build Windows Timezone to IANA Dictionary
#=====================================================
windows_timezones = {}
file = './windowsLocals.json'
data = json.load(open(file, 'r'))
elist = []
for e in data:
    #print(e)
    elist.append({
        "ClassId": "workflow.EnumEntry",
        "Label": e['language'],
        "ObjectType": "workflow.EnumEntry",
        "Value": e['language']
    })
print(json.dumps(elist, indent=4))
exit()
