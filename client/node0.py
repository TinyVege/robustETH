from bls import *
import pubInfo

nodeId = 0
print("*******************************************************************")
print(f"当前node:node{nodeId}")
print("*******************************************************************")

ids = [nodeId,1,2,3]



# register phase

# 1. register 创建账户的公私钥对
secret, nodePublicKey = (keygen1(nodeId)) 

nodePublicKeys = pubInfo.nodePublicKeys

# 2。 distributeShares 
shared_key = []             # len = 4
for i, publicKey in enumerate(nodePublicKeys):
    shared_key.append(vss.shared_key(secret, publicKey))
    if i == nodeId :
        print(f"*shared_key[{i}] = {shared_key[i]}")
    else :
        print(f"shared_key[{i}] = {shared_key[i]}")

shares, public_coefficients = vss.share(secret, n = 4, t = 3)           #vss.share只提供预定义的id，没有设置用户自定义id
for i, share in enumerate(shares):
    if i == nodeId :
        print(f"*share[{i}] = {share}")
    else :
        print(f"share[{i}] = {share}")

for i, public_coefficient in enumerate(public_coefficients):
    print(f"public_coefficient[{i}] = {public_coefficient}")
       

# 生成encrypt_shares
encrypt_share = []           # len = 4

for id in ids:
    encrypt_share.append(vss.encrypt_share(shares[id], id, shared_key[id]))
    if id == nodeId:
        print(f"*encrypt_share{nodeId}-> {id} = {encrypt_share[id]}")
    else :
        print(f"encrypt_share{nodeId}-> {id} = {encrypt_share[id]}")

#3. submitDispute
# 生成shared_key_proofs
shared_key_proofs = []          #len = 4
for i, publicKey in enumerate(nodePublicKeys):
    shared_key_proofs.append(vss.shared_key_proof(secret, publicKey))
    if i == nodeId:
        print(f"*shared_key_proof{i} = {shared_key_proofs[i]}")
    else:
        print(f"shared_key_proof{i} = {shared_key_proofs[i]}")

#4. submit_key_share
# DLEQ
g1 = G1
h1 = H1
g1si = multiply(g1, secret)    
h1si = multiply(h1,secret)  
c, r = vss.dleq(g1, g1si, h1, h1si, secret) 
print(f"h1si : {h1si}")
print(f"proof : {c} , {r}")

# proof
print(vss.dleq_verify(g1, g1si, h1, h1si, c, r))     

# h2si
h2 = H2
h2si = multiply(h2, secret)                 
print(f"h2si : {h2si}")


#5. submitMasterPublicKey
h2sis = pubInfo.h2sis
mpk = sum_points(h2sis)
print(f"mpk : {mpk}")


#6. 
# 计算gskj

s00 = 3585611973553240888248772857893414771693814528677862619539987160630306051807
s10 = 3125287026058876526061632301757016857648376082569995292705892534537438536912
s20 = 14708682775186236744987415530628723401989501285565944285071717588064063222541
s30 = 12637721702488166134877164948325283499743176890204860038259854533797451159225
s1 = [s00, s10, s20, s30]

gsk0 = sum(s1) % CURVE_ORDER        
print(f'gsk1 = {gsk0}') 

ggskj = multiply(G1, gsk0)
print(f'ggskj = {ggskj}') 

h1gpkj = multiply(H1, gsk0)
print(f'h1gpkj = {h1gpkj}') 

c, r = vss.dleq(g1, ggskj, h1, h1gpkj, gsk0) # DLEQ(g; ggskj; h; gpkj; gskj)
print(f"proof : [{c} , {r}]")

bls_pk = multiply(H2, gsk0)
print(f'bls_pk = {bls_pk}') 


############# depositToGoerli

msg = 'depositToGoerli'
print(f'hash_to_G1(message) : {hash_to_G1(msg)}')

master_pk = (12781175847691717766458894404153475446260213039546938929734456762490414786711, 7502802716148286654235516336379034055011532021151447795283112568570758763197, 8502917524221845216306803278296883928973187631400775780353448781239601697174, 7504306695808014361777487330847098001094929705409543719127544804455075753435)


gskj1 = 7906611519886167088043373356711714181973462154901757554213359858217459110192
gskj2 = 5957287272879246714624579530673994930448755298903361821199513713441152884201
gskj3 = 6321087864426483951672198415234005687952383818607440692837709196124531796895

sig_1 = sign(gskj1, msg)
sig_2 = sign(gskj2, msg)
sig_3 = sign(gskj3, msg)

sig = aggregate([(1, sig_1), (2, sig_2), (3, sig_3)])
print(f'signature : {sig}')     


############# normalExit
hex1 = keccak_256(
            abi_types = ['uint8[]'],
            values = [[8,8,8,8]]) 
x1 = int.from_bytes(hex1, "big") % CURVE_ORDER 
msgP = multiply(G1, x1)

sig_1 = my_sign(gskj1, msgP)
sig_2 = my_sign(gskj2, msgP)
sig_3 = my_sign(gskj3, msgP)
sig = aggregate([(1, sig_1), (2, sig_2), (3, sig_3)])
print(f'signature : {sig}')     









