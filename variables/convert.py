#!/usr/bin/env python3
import json
import re
file = json.load(open('./windowsLocals.json', 'r'))
#languages = []
#count = 1
#for line in file:
#    line = line.strip()
#    x = line.split('\t')
#    ldict = dict(
#        code      = x[3].split(': ')[0],
#        language  = x[1],
#        local     = (x[3].split(': ')[1]).strip(),
#    )
#    if len(x) > 5:
#        if ';' in x[5]:
#            list1 = []; list2 = []; y = x[5].split('; ')
#            for i in y:
#                list1.append(i.split(': ')[0])
#                list2.append((i.split(': ')[1]).strip())
#            ldict.update(dict(
#                secondary_language = list1,
#                secondary_local    = list2,
#            ))
#        else:
#            ldict.update(dict(
#                secondary_language = x[5].split(': ')[0],
#                secondary_local    = (x[5].split(': ')[1]).strip(),
#            ))
#    languages.append(ldict)
#    count += 1
#print(json.dumps(languages, indent=4))
llist = []
for e in file:
    if e.get('local'): llist.append(re.search('(\\(.*\\))', e['local']).group(1))
    #if e.get('local'): llist.append(e['local'])
print(json.dumps(llist, indent=2))