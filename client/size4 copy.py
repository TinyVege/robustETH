from bls import *
import ethFunction
from threading import Thread
import time


######################################################################################################
# 构建信息
####################################################################################################
ids = [0,1,2,3]
clusterSize = 4 

# 1. register 创建账户的公私钥对
secrets = []            #     
nodePublicKeys = []     # type = list<Tuple>
for i in ids:
    secret, nodePublicKey = (keygen1(i)) 
    secrets.append(secret)
    nodePublicKeys.append(nodePublicKey)

# print(f'secrets: {secrets}')
# print(f'nodePublicKeys: {nodePublicKeys}')


# 2。 distributeShares 
shared_keysAll = [[0]*clusterSize for i in range(clusterSize)]            # list<list<Tuple>> 4 * 4 * 2
for i in range(clusterSize):
    secret = secrets[i]
    for j in range(clusterSize):
        shared_keysAll[i][j]= vss.shared_key(secret, nodePublicKeys[j])

# print(shared_keys)
sharesAll = []                                                            # 4 * 4; 因为包括自己的话是给n个人发
public_coefficientsAll = []                                               # 4 * 3  
for secret in secrets:
    shares, public_coefficients = vss.share(secret, n = 4, t = 3)           #vss.share只提供预定义的id，没有设置用户自定义id
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
for i in range(3):          # i = 0 有问题，无法聚合
    sig = sign(gskjs[i+1], msg)
    sigs_deposit.append((i+1, sig))
signature_deposit = aggregate(sigs_deposit)



############# normalExit
balanceInfo = [1,1,1,1]
hex1 = keccak_256(
            abi_types = ['uint8[]'],
            values = [balanceInfo]) 
x1 = int.from_bytes(hex1, "big") % CURVE_ORDER 
msgP = multiply(G1, x1)

sigs_normalExit =[]
for i in range(3):
    sig = my_sign(gskjs[i+1], msgP)
    sigs_normalExit.append((i+1, sig))
signature_normalExit = aggregate(sigs_normalExit)



############## slashExit
slashContents = [[1],[1000]]            # slashContents


hexslashContents1 = keccak_256(
            abi_types = ['uint8[]'],
            values = [[1]]) 
xslashContents1 = int.from_bytes(hexslashContents1, "big") % CURVE_ORDER 
pslashContents1 = multiply(G1, xslashContents1)         # HslashContents1


sigs_slashContents1 = []
for i in range(3):          # i = 0 有问题，从1开始无法聚合;Q = 3
    sig = my_sign(gskjs[i+1], pslashContents1)
    sigs_slashContents1.append((i+1, sig))
slashContentsSignature1 = aggregate(sigs_slashContents1)    # slashContentsSignature1

slashProof1 = sigs_slashContents1[0][1]                         # slashProof1 = 1，2
for i in range(1):  # t = 1
    slashProof1 = add(slashProof1, sigs_slashContents1[i+1][1])


# 计算HslashContents2
hexslashContents2 = keccak_256(
            abi_types = ['uint256[]'],
            values = [[1000]]) 
xhexslashContents2 = int.from_bytes(hexslashContents2, "big") % CURVE_ORDER 
pslashContents2 = multiply(G1, xhexslashContents2)                   # HslashContents2


sigs_slashContents2 = []
for i in range(3):          # i = 0 有问题，无法聚合;Q = 3
    sig = my_sign(gskjs[i+1], pslashContents2)
    sigs_slashContents2.append((i+1, sig))
slashContentsSignature2 = aggregate(sigs_slashContents2)    # slashContentsSignature2

slashProof2 = sigs_slashContents2[0][1]                       # slashProof2 = 1,2
for i in range(1):  # t = 1
    slashProof2 = add(slashProof2, sigs_slashContents2[i+1][1])


faultyPublicKeyX = []
for i in range(2):                              # t+1 = 2
    faultyPublicKeyX.append(nodePublicKeys[i+1][0])


mutiBlsPK = multiply(H2, gskjs[1])
for i in range(1):                           # t=1
    # print(i)
    mutiBlsPK = add(mutiBlsPK, multiply(H2, gskjs[i+2]))


slashContents = slashContents
print(f'slashContents = {slashContents}')

slashProof1 = [slashProof1[0], slashProof1[1]]
slashProof2 = [slashProof2[0], slashProof2[1]]
slashProof = [slashProof1, slashProof2]
print(f'slashProof = {slashProof}')

faultyPublicKeyX =faultyPublicKeyX
print(f'faultyPublicKeyX = {faultyPublicKeyX}')

mutiBlsPK = mutiBlsPK
mutiBlsPK = [mutiBlsPK[0], mutiBlsPK[1], mutiBlsPK[2], mutiBlsPK[3]]
print(f'mutiBlsPK = {mutiBlsPK}')


slashContentsSignature1 = [slashContentsSignature1[0],slashContentsSignature1[1]]
slashContentsSignature2 = [slashContentsSignature2[0], slashContentsSignature2[1]]
slashContentsSignature = [slashContentsSignature1, slashContentsSignature2]
print(f'slashContentsSignature = {slashContentsSignature}')

balanceInfo = balanceInfo          # [1,1,1,1]
print(f'balanceInfo = {balanceInfo}')

balanceInfoSignature = signature_normalExit
balanceInfoSignature = [balanceInfoSignature[0], balanceInfoSignature[1]]
print(f'balanceInfoSignature = {balanceInfoSignature}')

for i in range(clusterSize):
    h1gpkjs[i] = [h1gpkjs[i][0], h1gpkjs[i][1]]

print(h1gpkjs)





###################### laggingTrigExit
# laggingTrigExit(
#         uint256 publicKeyX,
#         uint256 listIdx,
#         uint256[] memory exitInfo,              // 包含了balanceInfo
#         uint256[] memory exitInfoSig
#     )

# exitInfo = [1]
# hexslashContents2 = keccak_256(
#             abi_types = ['uint256'],
#             values = exitInfo) 
# xhexexitInfo = int.from_bytes(hexslashContents2, "big") % CURVE_ORDER 
# pexitInfo = multiply(G1, xhexexitInfo)                   # HslashContents2

# exitInfoSig = my_sign(gskjs[0], pexitInfo)


######################################################################################################
# 交易
####################################################################################################

print("deployment正在进行***************************")       # deployment gas_used = 4723256
ethFunction.deployment()          # 先部署然后再测时间


print("register正在进行***************************")         # register gas_used = 236742
for i in range(4):
    worker = Thread(target=ethFunction.register, 
                    args=(i, 
                          clusterSize, 
                          [nodePublicKeys[i][0], 
                           nodePublicKeys[i][1]]), 
                    daemon=False)
    worker.start()

time.sleep(40)

print(f'registration phase 结束')
print()


print("distributeShares正在进行***************************")
for i in range(clusterSize):
    worker = Thread(target=ethFunction.distributeShares, 
                    args=(i, 
                          nodePublicKeys[i][0], 
                          encrypt_sharesAllTx[i], 
                          public_coefficientsAll[i]), 
                    daemon=False)
    worker.start()     


time.sleep(40)
print(f'distributeShares phase 结束')
print()


print("submitKeyShare正在进行***************************")
for i in range(4):
    worker = Thread(target=ethFunction.submitKeyShare, 
                    args=(i,
            nodePublicKeys[i][0],
            h1sis[i],             
            [cs[i], rs[i]],
            h2sis[i]), 
            daemon=False)
    worker.start()   


time.sleep(40)
print(f'submitKeyShare phase 结束')
print()
    

print("submitMasterPublicKey 正在进行***************************")
ethFunction.submitMasterPublicKey(listIdx= 0, publicKeyX = nodePublicKeys[0][0], masterPublicKey=masterPublicKey)


time.sleep(40)
print(f'submitMasterPublicKey phase 结束')
print()


print("submitGpkj 正在进行***************************")
for i in range(4):
    worker = Thread(target=ethFunction.submitGpkj, 
                    args=(
        nodePublicKeys[i][0], 
        i,
        ggskjs[i],
        encrypt_sharesAllTx,
        public_coefficientsAll,
        h1gpkjs[i],
        [csgpkj[i], rsgpkj[i]],
        h2gpkjs[i]), 
            daemon=False)
    worker.start() 

time.sleep(40)
print(f'submitGpkj phase 结束')
print()


print("depositToGoerli 正在进行***************************")
ethFunction.depositToGoerli(
        listIdx=0,                           
        publicKeyX = nodePublicKeys[0][0],
        signature=signature_deposit,              
        depositMessage=depositMessage     
        )

time.sleep(40)
print(f'depositToGoerli phase 结束')
print()




# # print("normalExit 正在进行***************************")     # normalExit gas_used = 200810
# # print(f"node0 正在进行 normalExit ，请稍后")  
# # print(f'publicKeyX = {nodePublicKeys[0][0]},
#     # balanceInfo = {balanceInfo},              
#     # signature = {signature_normalExit}')
# # ethFunction.normalExit(
# #         publicKeyX = nodePublicKeys[0][0], 
# #         balanceInfo=balanceInfo,
# #         signature=signature_normalExit)



print("slashExit 正在进行***************************")     # slashExit gas_used = 
ethFunction.slashExit(
    listIdx=0,
    publicKeyX=nodePublicKeys[0][0],
    slashContents=slashContents,
    slashProof=slashProof,
    faultyPublicKeyX=faultyPublicKeyX,
    mutiBlsPK=mutiBlsPK,
    slashContentsSignature=slashContentsSignature,
    balanceInfo=balanceInfo,
    balanceInfoSignature=balanceInfoSignature)

# print("laggingExit 正在进行***************************")     # slashExit gas_used = 
# ethFunction.laggingTrigExit(
#     listIdx=0,
#     publicKeyX=nodePublicKeys[0][0],
#     exitInfo=exitInfo,
#     exitInfoSig=exitInfoSig
#     )