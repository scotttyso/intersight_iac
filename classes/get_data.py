import os, sys, base64
try:
    from Crypto.Cipher import AES
except ImportError:
    sys.stdout.write('PyCrypto library is required to run this script.')
    sys.exit(1)
from hashlib import md5

def K(p, s, k, i):
    dtot = md5(p + s).digest()
    d = [dtot]
    while len(dtot) < i + k:
        d.append(md5(d[-1] + p + s).digest())
        dtot += d[-1]
    return (dtot[:k], dtot[k:k + i])

def E(ps, pa):
    s = os.urandom(8)
    k, i = K(ps, s, 32, 16)
    pl = 16 - len(pa) % 16
    if isinstance(pa, str):
        pp = pa + chr(pl) * pl
    else: pp = pa + bytearray([pl] * pl)
    c = AES.new(k, AES.MODE_CBC, i)
    ct = c.encrypt(pp)
    ep = base64.b64encode(b'Salted__' + s + ct)
    if type(ep) is not str: ep = ep.decode('utf8')
    return ep
