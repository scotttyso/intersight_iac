#!/usr/bin/env python3

import re
import sys
file = sys.argv[1]
outfile = open('newfile.py', 'w')
with open(file) as f:
    for line in f:
        outfile.write(line.replace("['", '.').replace("']", ''))
outfile.close()
f.close()
exit()