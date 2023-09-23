#!/usr/bin/python3
#=============================================================================
# Source Modules
#=============================================================================
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
import sys
try:
    import crypt, stdiomask
except ImportError as e:
    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
    prRed(f" Module {e.name} is required to run this script")
    prRed(f" Install the module using the following: `pip install {e.name}`")
    sys.exit(1)

valid = False
while valid == False:
    password = stdiomask.getpass(prompt='Enter the password to encrypt: ')
    if not password == '':
        print(crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512)))
        valid = True
