from Crypto.Util.number import long_to_bytes, bytes_to_long
from pwn import *

io = process("./gold")
io.sendlineafter(b"Enter your choice: ", b"42")
flag = io.recvuntil(b"Welcome", True)
for i in range(len(flag)):
	if flag[i] not in b'0123456789abcdef':
		break
flag = int(flag[:i].decode(), 16)

n = 32467577662003471034281394304638628909610297422094021879584115742794221695914928226094006777553186083128053826444847004915071918386112551981838138946636503520499887716410973711188568828746937902591339661588652116798230693294118783786817937180181464960683050642273151973622888525692185785627435178102772535529
p = 6327369635452734797574882228968661186208630682750010565343216094384118737722011883878689122863808521045957182002120341907925246528530213733587078609873299
q = 5131291442195056278216230685618846127213221556043525988513853948364722574400315196761293675541885955169105890073471489797861433254131005076366709987178771


from functools import reduce
def crt(m, a):
	s = 0
	prod = reduce(lambda acc, b: acc*b, m)
	for n_i, a_i in zip(m, a):
		p = prod // n_i
		s += a_i * pow(p, -1, n_i) * p
	return s % prod

def decrypt(ct, n, p, q):
	mp = int(pow(ct, (p+1)//4, p))
	mq = int(pow(ct, (q+1)//4, q))

	res1 = crt([p, q], [mp,  mq])
	res2 = crt([p, q], [mp, -mq])

	res = [res1, n-res1, res2, n-res2]

	return res


res = decrypt(flag, n, p, q)
print([long_to_bytes(ss)[::-1] for ss in res])

io.close()
