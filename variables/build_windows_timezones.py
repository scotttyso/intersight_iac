#!/usr/bin/env python3
import json
import lxml.etree as ET
#=====================================================
# Build Windows Timezone to IANA Dictionary
#=====================================================
windows_timezones = {}
file = './windowsZones.xml'
doc = ET.parse(file)
for zone in doc.xpath('//mapZone'):
    attrib = zone.attrib
    if attrib['territory'] == '001':
        windows_timezones[attrib['other']] = attrib['type']
print(json.dumps(windows_timezones, indent=4))
wr_file = open('./windowsTimeZones.json', 'w')
wr_file.write(json.dumps(windows_timezones, indent=4))
wr_file.close()
exit()
