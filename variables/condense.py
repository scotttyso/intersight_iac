#!/usr/bin/env python3
import sys
file = sys.argv[1]

with open(file) as f:
    combined = "\\n".join(line.strip() for line in f)
output_file = open('ci_template.txt', 'w')
output_file.write(combined)
output_file.close
print('completed')
sys.exit(0)