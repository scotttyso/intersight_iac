#!/usr/bin/python3
import crypt
import stdiomask

valid = False
while valid == False:
    password = stdiomask.getpass(prompt='Enter the password to encrypt: ')
    if not password == '':
        print(crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512)))
        valid = True
