from bls import *


print("*******************************************************************")
print("当前是测试")
print("*******************************************************************")


data = [[1],[1000]]

hex1 = keccak_256(
            abi_types = ['uint8[]'],
            values = [[1]]) 
x1 = int.from_bytes(hex1, "big") % CURVE_ORDER 

p1 = multiply(G1, x1)
print(f'p1 = {p1}')


hex2 = keccak_256(
            abi_types = ['uint256[]'],
            values = [[1000]]) 
x2 = int.from_bytes(hex2, "big") % CURVE_ORDER 

p2 = multiply(G1, x2)
print(f'p2 = {p2}')

gskj1 = 7906611519886167088043373356711714181973462154901757554213359858217459110192
gskj2 = 5957287272879246714624579530673994930448755298903361821199513713441152884201
gskj3 = 6321087864426483951672198415234005687952383818607440692837709196124531796895
# sk = vss.recover([(1,gskj1), (2,gskj2), (3,gskj3)])

sig_1 = my_sign(gskj1, p1)
sig_2 = my_sign(gskj2, p1)
sig_3 = my_sign(gskj3, p1)
sig = aggregate([(1, sig_1), (2, sig_2), (3, sig_3)])



print(f'sig_1 + sig_2  = {add(sig_1, sig_2)}')
print(f'signature : {sig}')     

sig_1 = my_sign(gskj1, p2)
sig_2 = my_sign(gskj2, p2)
sig_3 = my_sign(gskj3, p2)
sig = aggregate([(1, sig_1), (2, sig_2), (3, sig_3)])

print(f'sig_1 + sig_2  = {add(sig_1, sig_2)}')
print(f'signature : {sig}')   

encrypt_sharesAll = [[0]* 3 for i in range(4)] 

for i in encrypt_sharesAll:
    print(i)












