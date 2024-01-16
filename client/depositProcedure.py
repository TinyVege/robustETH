from bls import *
import stakingPoolFunctions
from threading import Thread
import time

def get_publicKeys(ids: List) -> List<int>, List<Tuple[int, int]>:
    secrets = []            #     
    nodePublicKeys = []     # type = list<Tuple>

    return secrets, nodePublicKeys
    


# 1. register 创建账户的公私钥对
secrets = []            #     
nodePublicKeys = []     # type = list<Tuple>
for i in ids:
    secret, nodePublicKey = (keygen1(i)) 
    secrets.append(secret)
    nodePublicKeys.append(nodePublicKey)

# print(f'secrets: {secrets}')
# print(f'nodePublicKeys: {nodePublicKeys}')