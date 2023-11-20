from bls import *
import hashlib

print("*******************************************************************")
print("当前是测试")
print("*******************************************************************")


msg = 'test message'
msg_hash = hashlib.sha3_256(msg.encode()).digest()

master_pk = (12781175847691717766458894404153475446260213039546938929734456762490414786711, 7502802716148286654235516336379034055011532021151447795283112568570758763197, 8502917524221845216306803278296883928973187631400775780353448781239601697174, 7504306695808014361777487330847098001094929705409543719127544804455075753435)


gskj1 = 7906611519886167088043373356711714181973462154901757554213359858217459110192
blspk1 = (multiply(H2, gskj1))
gskj2 = 5957287272879246714624579530673994930448755298903361821199513713441152884201
blspk2 = (multiply(H2, gskj2))
gskj3 = 6321087864426483951672198415234005687952383818607440692837709196124531796895
# sk = vss.recover([(1,gskj1), (2,gskj2), (3,gskj3)])
# print(sk)
# print(sign(sk,msg_hash))

print(f'blspk1 + blspk2 = {add(blspk1,blspk2)}')

sig_1 = sign(gskj1, msg_hash)
sig_2 = sign(gskj2, msg_hash)
sig_3 = sign(gskj3, msg_hash)

print(f'sig_1 + sig_2  = {add(sig_1, sig_2)}')

sig = aggregate([(1, sig_1), (2, sig_2), (3, sig_3)])

# print(f'signature : {sig}')     
print(f'hash_to_G1(message) : {hash_to_G1(msg_hash)}')
# print(f'bls_pk : {master_pk}')
# check_pairing(signature, G2, hash_to_G1(message), bls_pk)



