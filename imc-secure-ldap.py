#!/usr/bin/env python3
import os
import pexpect
import re
import sys
import time
import yaml
password = os.getenv('password')
username = os.getenv('username')
password2 = os.getenv('password2')
username2 = os.getenv('username2')
dir = sys.argv[1]
ydata = yaml.safe_load(open(os.path.join(dir, 'configuration.yaml'), 'r'))
sys_shell = os.environ['SHELL']
sysPrompt = re.compile(r'([\w]+@[\w]+|[\w]+([/\w *]+)?#)')
child = pexpect.spawn(sys_shell, encoding='utf-8')
child.logfile_read = sys.stdout
child.sendline(f'ssh {username}@{ydata["jumphost"]} | tee {ydata["jumphost"]}.txt')
child.expect('txt')
login_check = False
while login_check == False:
    i = child.expect(['Are you sure you want to continue', 'Password:', sysPrompt])
    if i == 0: child.sendline('yes')
    elif i == 1: child.sendline(password)
    elif i == 2: login_check = True

for host in ydata['hostnames']:
    child.sendline(f'ssh {username2}@{host}')
    child.expect(host)
    child.expect(host)
    login_check = False
    while login_check == False:
        i = child.expect(['Are you sure you want to continue', r'[pP]assword:', '#'])
        if i == 0: child.sendline('yes')
        elif i == 1: child.sendline(password2)
        elif i == 2: login_check = True
    for cmd in ydata['cmds']:
        child.sendline(cmd)
        i = child.expect(['invalid command', sysPrompt])
        if i == 0:
            print('\n!!!error with command!!!\n')
            sys.exit(1)
    file = '{}'.format(os.path.join(dir, 'certificates.txt'))
    certs = open(file, 'r')
    child.sendline('scope ldap')
    child.expect(sysPrompt)
    child.sendline('scope secure')
    child.expect(sysPrompt)
    child.sendline('secure-ldap enabled paste')
    child.expect('Please paste the LDAP CA')
    for line in certs:
        child.sendline(line.strip())
        #time.sleep(1)
    child.send(chr(4))
    child.expect(sysPrompt)
    child.sendline('commit')
    time.sleep(3)
    child.sendline('exit')
    child.expect(sysPrompt)
    child.sendline('exit')
    child.expect(sysPrompt)
    child.sendline('exit')
    child.expect('closed')
    child.expect(sysPrompt)
