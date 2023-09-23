#!/usr/bin/env python3
import re
import sys
file = sys.argv[1]

with open(file) as f:
    combined = "".join(line.rstrip('\n') for line in f)
output_file = open('catemplate.txt', 'w')
output_file.write(combined)
output_file.close
print('completed')
sys.exit(0)