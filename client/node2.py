from bls import *

nodeId = 2
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


# 2222222222222 distributeShares 
shared_key = []             # len = 4
for i, publicKey in enumerate(nodePublicKeys):
    # def shared_key(sk, other_pk: PointG1) -> PointG1:
    publicKey = (publicKey[0], publicKey[1])                # 转换为Tuple[int, int]
    temp = vss.shared_key(secret, publicKey)
    shared_key.append(temp)
    if i == nodeId :
        print(f"*shared_key[{i}] = {temp}")
    else :
        print(f"shared_key[{i}] = {temp}")


shares, public_coefficients = vss.share(secret, 4, 3)           # vss.share中的id是连续的，还需要改进
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
       

# 生成encrypt_shares
receiver_ids = [0,1,2,3]
encrypt_share = []           # len = 4
# decrypt_share = []           # len = 4
for id in receiver_ids:
    encrypt_share.append(vss.encrypt_share(shares[id], id, shared_key[id]))
    # decrypt_share.append(vss.decrypt_share(encrypt_share[id], id, shared_key[id]))
    # print(f"shares{id} : {shares[id]}, decrypt_share{id} : {decrypt_share[id]}, {shares[id] == decrypt_share[id]}")
    if id == nodeId:
        print(f"*encrypt_share{nodeId}-> {id} = {encrypt_share[id]}")

    else :
        print(f"encrypt_share{nodeId}-> {id} = {encrypt_share[id]}")

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
h1si = multiply(h1,secret)                 

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
s02 = 17829424065354678616817661890723266172036513269480050524099309641230040577879
s12 = 21679552453201673544378420826921759125996140484448641043440457357589535910441
s22 = 4926605538558103676855165138158004110868910710401070050644256013698179039068
s32 = 5298190959443341321066143165385515698643919635405668890411899074075014348047
s2 = [s02, s12, s22, s32]
gsk2 = sum(s2) % CURVE_ORDER
print(f'gsk2 = {gsk2}')     # 

ggskj = multiply(G1, gsk2)
print(f'ggskj = {ggskj}') 

h1gpkj = multiply(H1, gsk2)
print(f'h1gpkj = {h1gpkj}') # 

c, r = vss.dleq(g1, ggskj, h1, h1gpkj, gsk2) # DLEQ(g; ggskj; h; gpkj; gskj)
print(f"proof : [{c} , {r}]")

bls_pk = multiply(H2, gsk2)
print(f'bls_pk = {bls_pk}') 