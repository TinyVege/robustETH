from bls import *
import ethFunction

######################################################################################################
# 构建信息
####################################################################################################
ids = [0,1,2,3,4,5,6,7,8,9]
clusterSize = 10

# 1. register 创建账户的公私钥对
secrets = []            #     
nodePublicKeys = []     # type = list<Tuple>
for i in ids:
    secret, nodePublicKey = (keygen1(i)) 
    secrets.append(secret)
    nodePublicKeys.append(nodePublicKey)



# 2. distributeShares 
shared_keysAll = [[0]*clusterSize for i in range(clusterSize)]            # list<list<Tuple>> 4 * 4 * 2
for i in range(clusterSize):
    secret = secrets[i]
    for j in range(clusterSize):
        shared_keysAll[i][j]= vss.shared_key(secret, nodePublicKeys[j])

# print(shared_keys)
sharesAll = []                                                            # 4 * 4; 因为包括自己的话是给n个人发
public_coefficientsAll = []                                               # 4 * 3  
for secret in secrets:
    shares, public_coefficients = vss.share(secret, n = 10, t = 7)           #vss.share只提供预定义的id，没有设置用户自定义id
    sharesAll.append(shares)
    public_coefficientsAll.append(public_coefficients)

# 生成encrypt_shares
encrypt_sharesAll = [[0]* clusterSize for i in range(clusterSize)]           

for i in range(clusterSize):
    for id in ids:
        encrypt_sharesAll[i][id] = vss.encrypt_share(sharesAll[i][id], id, shared_keysAll[i][id])

encrypt_sharesAllTx = [                      # n * n-1 = 4 * 3 ： 每个人都发，发3条
    [encrypt_sharesAll[i][j] for j in range(clusterSize) if i != j]         # 提取非对角线元素
    for i in range(clusterSize)
]        


#3. submitDispute
# 生成shared_key_proofs
# shared_key_proofs = []          #len = 4
# for i, publicKey in enumerate(nodePublicKeys):
#     shared_key_proofs.append(vss.shared_key_proof(secret, publicKey))
#     if i == nodeId:
#         print(f"*shared_key_proof{i} = {shared_key_proofs[i]}")
#     else:
#         print(f"shared_key_proof{i} = {shared_key_proofs[i]}")
        

#4. submit_key_share
# DLEQ
g1sis = []
h1sis = []
cs = []
rs = []
h2sis = []
for i in range(clusterSize):
    g1si = multiply(G1, secrets[i])    
    h1si = multiply(H1, secrets[i])  
    c, r = vss.dleq(G1, g1si, H1, h1si, secrets[i]) 

    h2si = multiply(H2, secrets[i])

    g1sis.append(g1si)
    h1sis.append(h1si)
    cs.append(c)
    rs.append(r)

    h2sis.append(h2si)

masterPublicKey = sum_points(h2sis)

#6. 
# 计算gskj
gskjs = []
ggskjs = []
h1gpkjs = []
h2gpkjs = []
csgpkj = []
rsgpkj = []


for i in range(clusterSize):
    s= 0
    for j in range(clusterSize):
        s = s + sharesAll[j][i]
    gskj = s % CURVE_ORDER
    ggskj = multiply(G1, gskj)
    h1gpkj = multiply(H1, gskj)
    c, r = vss.dleq(G1, ggskj, H1, h1gpkj, gskj)
    bls_pk = multiply(H2, gskj)

    gskjs.append(gskj)
    ggskjs.append(ggskj)
    h1gpkjs.append(h1gpkj)
    csgpkj.append(c)
    rsgpkj.append(r)
    h2gpkjs.append(bls_pk)


############# depositToGoerli
msg = 'depositToGoerli'
depositMessage = hash_to_G1(msg)

sigs_deposit = []
for i in range(7):          # i = 0 有问题，无法聚合
    sig = sign(gskjs[i+1], msg)
    sigs_deposit.append((i+1, sig))
signature_deposit = aggregate(sigs_deposit)



############# normalExit
balanceInfo = [2,2,2,2,2,2,2,2,2,2]
hex1 = keccak_256(
            abi_types = ['uint8[]'],
            values = [balanceInfo]) 
x1 = int.from_bytes(hex1, "big") % CURVE_ORDER 
msgP = multiply(G1, x1)

sigs_normalExit =[]
for i in range(7):
    sig = my_sign(gskjs[i+1], msgP)
    sigs_normalExit.append((i+1, sig))
signature_normalExit = aggregate(sigs_normalExit)




    

######################################################################################################
# 交易
####################################################################################################

print("deployment正在进行***************************")       # deployment gas_used = 4723256
ethFunction.deployment()     


print("register正在进行***************************")         # register gas_used = 236742
for i in range(clusterSize):
    print(f"node{i}正在进行注册，请稍后")
    ethFunction.register(clusterSize, [nodePublicKeys[i][0], nodePublicKeys[i][1]])


print("distributeShares正在进行***************************")
# test_list = [list(item) for item in test]

for i in range(clusterSize):
    print(f"node{i}正在进行distributeShares，请稍后")   #distributeShares gas_used = 185536
    ethFunction.distributeShares(i, nodePublicKeys[i][0], encrypt_sharesAllTx[i], public_coefficientsAll[i])        



print("submitKeyShare正在进行***************************")
for i in range(clusterSize):
    print(f"node{i}正在进行submitKeyShare，请稍后")   #submitKeyShare gas_used = 273369
    ethFunction.submitKeyShare(
            listIdx = i,
            publicKeyX = nodePublicKeys[i][0],
            keyShareG1 = h1sis[i],             
            keyShareG1CorrectnessProof = [cs[i], rs[i]],
            keyShareG2 = h2sis[i])
    

print("submitMasterPublicKey 正在进行***************************")
print(f"node0 正在进行 submitMasterPublicKey ，请稍后")   #submitMasterPublicKey gas_used = 355322
ethFunction.submitMasterPublicKey(publicKeyX = nodePublicKeys[0][0], masterPublicKey=masterPublicKey)
    


print("submitGpkj 正在进行***************************")
for i in range(clusterSize):
    print(f"node{i}正在进行 submitGpkj ，请稍后")   #submitGpkj gas_used = 430549
    ethFunction.submitGpkj(
        publicKeyX=nodePublicKeys[i][0], 
        listIdx=i,
        ggskj=ggskjs[i],
        encrypted_sharesQ=encrypt_sharesAllTx,
        commitmentsQ=public_coefficientsAll,
        h1gpkj=h1gpkjs[i],
        h1gpkjCorrectnessProof=[csgpkj[i], rsgpkj[i]],
        h2gpkj=h2gpkjs[i]
        )

print("depositToGoerli 正在进行***************************")
print(f"node0 正在进行 depositToGoerli ，请稍后")                   # depositMessage gas_used = 529106
ethFunction.depositToGoerli(                           
        publicKeyX = nodePublicKeys[0][0],
        signature=signature_deposit,              
        depositMessage=depositMessage     
        )


print("normalExit 正在进行***************************")     # normalExit gas_used = 200810
print(f"node0 正在进行 normalExit ，请稍后")  
ethFunction.normalExit(
        publicKeyX = nodePublicKeys[0][0], 
        balanceInfo=balanceInfo,
        signature=signature_normalExit)