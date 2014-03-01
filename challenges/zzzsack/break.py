import json
P = 0x200000000000000000000000000000000000000000000000000000000000000004d

pub = json.load(open('public','r'))
cipher = json.load(open('encrypted','r'))

def test(U):
    B = [(x*U)%P for x in pub]
    B = sorted(B)

    tot = 0
    for x in B:
        if x <= tot:
            return False
        tot += x
    return True

def findKey():
    for i, a in enumerate(pub):
        print 'testing vec', i
        ainv = pow(a, P-2, P)
        for si in range(1,258):
            U = ainv*si
            if test(U):
                return U
    assert(0)

priv = findKey()
import zzzsack

print zzzsack.decrypt(cipher, pub, priv)