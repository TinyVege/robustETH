from bls import *
import ethFunction
import time
from threading import Thread

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


    

#####################################################################################################
# 交易
####################################################################################################

print("deployment正在进行***************************")       # deployment gas_used = 4723256
ethFunction.deployment()     


#初始区块与时间
time_start = time.time()
print(f'开始时间为 : {time_start}')


print("register正在进行***************************")         # register gas_used = 236742
for i in range(clusterSize):
    worker = Thread(target=ethFunction.register, 
                    args=(i, 
                          clusterSize, 
                          [nodePublicKeys[i][0], 
                           nodePublicKeys[i][1]]), 
                    daemon=False)
    worker.start()


current_block_number = ethFunction.get_latest_block_number()
print(f'当前区块号是 : {current_block_number}')
ethFunction.log_loop(current_block_number, 12)
print(f'registration phase 结束')
print()


print("distributeShares正在进行***************************")
# test_list = [list(item) for item in test]

for i in range(clusterSize):
    worker = Thread(target=ethFunction.distributeShares, 
                    args=(i, 
                          nodePublicKeys[i][0], 
                          encrypt_sharesAllTx[i], 
                          public_coefficientsAll[i]), 
                    daemon=False)
    worker.start()



current_block_number = ethFunction.get_latest_block_number()
print(f'当前区块号是 : {current_block_number}')
ethFunction.log_loop(current_block_number, 12)
print(f'distributeShares phase 结束')
print()


print("submitKeyShare正在进行***************************")
for i in range(clusterSize):
    worker = Thread(target=ethFunction.submitKeyShare, 
                    args=(i,
            nodePublicKeys[i][0],
            h1sis[i],             
            [cs[i], rs[i]],
            h2sis[i]), 
            daemon=False)
    worker.start()   


current_block_number = ethFunction.get_latest_block_number()
print(f'当前区块号是 : {current_block_number}')
ethFunction.log_loop(current_block_number, 12)
print(f'submitKeyShare phase 结束')
print()
    

print("submitMasterPublicKey 正在进行***************************")
ethFunction.submitMasterPublicKey(listIdx= 0, publicKeyX = nodePublicKeys[0][0], masterPublicKey=masterPublicKey)


current_block_number = ethFunction.get_latest_block_number()
print(f'当前区块号是 : {current_block_number}')
ethFunction.log_loop(current_block_number, 12)
print(f'submitMasterPublicKey phase 结束')
print()


print("submitGpkj 正在进行***************************")
for i in range(clusterSize):
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

current_block_number = ethFunction.get_latest_block_number()
print(f'当前区块号是 : {current_block_number}')
ethFunction.log_loop(current_block_number, 12)
print(f'submitGpkj phase 结束')
print()


print("depositToGoerli 正在进行***************************")
ethFunction.depositToGoerli(
        listIdx=0,                           
        publicKeyX = nodePublicKeys[0][0],
        signature=signature_deposit,              
        depositMessage=depositMessage     
        )

current_block_number = ethFunction.get_latest_block_number()
print(f'当前区块号是 : {current_block_number}')
ethFunction.log_loop(current_block_number, 12)
print(f'depositToGoerli phase 结束')
print()


time_end = time.time()
print(f'结束时间为 : {time_end}')
    
print(f'持续时间为 : {time_end - time_start}')
