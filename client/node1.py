from bls import *

nodeId = 1
print("*******************************************************************")
print(f"当前node:node{nodeId}")
print("*******************************************************************")


#1111111111111 register 创建账户的公私钥对
secret, nodePublicKey = (keygen1(nodeId)) 

nodePublicKeys = [
    (2322232518476478355082179417627945840901717750665249866684479270698742700263, 973931943303135868888114463333031069134546660265761666065623192082481578704),
    (11857375388377339159917146126754708647444152272095756164728292003396664855507, 11576282137752257579123107959164751060099665303122339147293900962084264876601),
    (12045861018111163016402813231563781346382350605582967587696925944172364694240, 17606293752344037251875084774171510583963480224546691281838600315533276074197),
    (18521109374924651388713669376116860968875531691095625704239289808976999301562, 17641507992449572398451865167662908033960239081359237823783491188583710040058)
]


# 2222222222222 distributeShares (未加密)
shared_key = []             # len = 4
for i, publicKey in enumerate(nodePublicKeys):
    # def shared_key(sk, other_pk: PointG1) -> PointG1:
    temp = vss.shared_key(secret, publicKey)
    shared_key.append(temp)
    if i == nodeId :
        print(f"*shared_key[{i}] = {temp}")
    else :
        print(f"shared_key[{i}] = {temp}")


shares, public_coefficients = vss.share(secret, 4, 3)
for i, share in enumerate(shares):
    if i == nodeId :
        print(f"*share[{i}] = {share}")
    else :
        print(f"share[{i}] = {share}")

for i, public_coefficient in enumerate(public_coefficients):
    if i == nodeId :
        print(f"*public_coefficient[{i}] = {public_coefficient}")
    else :
        print(f"public_coefficient[{i}] = {public_coefficient}")

# # 生成encrypt_shares
receiver_ids = [0,1,2,3]
encrypt_share = []           # len = 4
for id in receiver_ids:
    encrypt_share.append(vss.encrypt_share(shares[id], id, shared_key[id]))
    if id == nodeId:
        print(f"*encrypt_share{id} = {encrypt_share[id]}")
    else :
        print(f"encrypt_share{id} = {encrypt_share[id]}")

# 生成shared_key_proofs
shared_key_proofs = []          #len = 4
for i, publicKey in enumerate(nodePublicKeys):
    # def shared_key_proof(sk, other_pk: PointG1) -> Tuple[int, int]:
    temp = vss.shared_key_proof(secret, publicKey)
    shared_key_proofs.append(temp)
    if i == nodeId:
        print(f"*shared_key_proof{i} = {temp}")
    else:
        print(f"shared_key_proof{i} = {temp}")


#4444444444444444 submit_key_share(uint256[2] memory key_share_G1, uint256[2] memory key_share_G1_correctness_proof, uint256[4] memory key_share_G2)
# def dleq(g1: PointG1, h1: PointG1, g2: PointG1, h2: PointG1, alpha: int) -> Tuple[int, int]:
g1 = G1    
g1si = multiply(g1, secret)  
h1 = H1    
h1si = multiply(h1, secret)                 

c, r = vss.dleq(g1, g1si, h1, h1si, secret) 

print(f"h1si : {h1si}")
print(f"proof : {c} , {r}")

# def dleq_verify(g1: PointG1, h1: PointG1, g2: PointG1, h2: PointG1, challenge: int, response: int):
print(vss.dleq_verify(g1, g1si, h1, h1si, c, r))     

h2 = H2
h2si = multiply(h2, secret)                 

print(f"h2si : {h2si}")


#6. 
# 计算gskj

s01 = 14422012033630247742596060406003771439032344765156159913731229685479734480284
s11 = 17372042400907016401196998432839414209833671866596697679839537518596552841773
s21 = 8998267423182753888937627220560841968017270219541283649168332836094936466858
s31 = 10890775405844699499805498787822236742186904104439684998870668191197852312511
s1 = [s01, s11, s21, s31]


gsk1 = sum(s1) % CURVE_ORDER        
print(f'gsk1 = {gsk1}') 

# ggskj = multiply(G1, gsk1)
# print(f'ggskj = {ggskj}') 

# h1gpkj = multiply(H1, gsk1)
# print(f'h1gpkj = {h1gpkj}') 

# c, r = vss.dleq(g1, ggskj, h1, h1gpkj, gsk1) # DLEQ(g; ggskj; h; gpkj; gskj)
# print(f"proof : [{c} , {r}]")

# bls_pk = multiply(H2, gsk1)
# print(f'bls_pk = {bls_pk}') 



