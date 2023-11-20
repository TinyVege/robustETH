from web3 import Web3
from contract import bytecode, abi, private_keys
from hexbytes import HexBytes
import time


infura_url = 'https://goerli.infura.io/v3/ed685130fe964c39aca273439462b5ed'
w3 = Web3(Web3.HTTPProvider(infura_url))


private_keys = private_keys
accts = []
for key in private_keys:
    accts.append(w3.eth.account.from_key(key))

contractAddress = ''          

def deployment():
    StakingPool  = w3.eth.contract(bytecode=bytecode, abi=abi)

    # Deploy a contract using `transact` + the signer middleware:
    deployment_tx = StakingPool.constructor().build_transaction({
        "from": accts[0].address,
        "nonce": w3.eth.get_transaction_count(accts[0].address),
        
    }) 
    signed_tx = w3.eth.account.sign_transaction(deployment_tx, private_key=accts[0].key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    gas_used = receipt["gasUsed"]
    transactionHash = receipt["transactionHash"]
    blockNumber = receipt["blockNumber"]

    print(f'from : {accts[0].address}')
    print(f'blockNumber = {blockNumber}')
    print(f'deployment gas_used = {gas_used}')    
    print(f'transactionHash = {transactionHash.hex()}') 

    global contractAddress
    contractAddress = receipt["contractAddress"]
   

def register(listIdx, clusterSize, nodePublicKey):
    staingPool = w3.eth.contract(address=contractAddress, abi=abi)

    # Manually build and sign a transaction:
    register_tx = staingPool.functions.register(listIdx, clusterSize, nodePublicKey).build_transaction({
        "from": accts[listIdx].address,
        "nonce": w3.eth.get_transaction_count(accts[listIdx].address),
        "value": 2000000000000000,
    })
    signed_tx = w3.eth.account.sign_transaction(register_tx, private_key=accts[listIdx].key)

    # Send the raw transaction:
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    gas_used = receipt["gasUsed"]
    transactionHash = receipt["transactionHash"]
    blockNumber = receipt["blockNumber"]

    print()
    print(f'from : {accts[listIdx].address}')
    print(f"node{listIdx}正在进行注册，请稍后")
    print(f'listIdx = {listIdx}, clusterSize = {clusterSize}, nodePublicKey = {[nodePublicKey[0], nodePublicKey[1]]}')
    print(f'blockNumber = {blockNumber}')
    print(f'register gas_used = {gas_used}')
    print(f'transactionHash = {transactionHash.hex()}')
    

def distributeShares(
        listIdx, 
        publicKeyX, 
        encryptedShares, 
        commitments):
    staingPool = w3.eth.contract(address=contractAddress, abi=abi)

    # Manually build and sign a transaction:
    distributeShares_tx = staingPool.functions.distributeShares(
        listIdx, 
        publicKeyX, 
        encryptedShares, 
        commitments).build_transaction({
        "from": accts[listIdx].address,
        "nonce": w3.eth.get_transaction_count(accts[listIdx].address),
    })
    signed_tx = w3.eth.account.sign_transaction(distributeShares_tx, private_key=accts[listIdx].key)

    # Send the raw transaction:
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    gas_used = receipt["gasUsed"]
    transactionHash = receipt["transactionHash"]
    blockNumber = receipt["blockNumber"]

    print()
    print(f'from : {accts[listIdx].address}')
    print(f"node{listIdx}正在进行distributeShares，请稍后")   #distributeShares gas_used = 185536
    print(f'listIdx = {listIdx}, publicKeyX = {publicKeyX}, encryptedShares = {encryptedShares}, commitments = {commitments}')
    print(f'blockNumber = {blockNumber}')
    print(f'distributeShares gas_used = {gas_used}')
    print(f'transactionHash = {transactionHash.hex()}')
    
# def submitDispute(
#         issuerPublicKeyX,                                                           
#         disputerPublicKeyX,                                                         
#         issuerListIdx,
#         disputerListIdx,                                                          
#         encrypted_shares,
#         commitments,
#         sharedKey,
#         sharedKeyCorrectnessProof):
#     staingPool = w3.eth.contract(address=contractAddress, abi=abi)

#     # Manually build and sign a transaction:
#     submitDispute_tx = staingPool.functions.submitDispute(
#         issuerPublicKeyX,                                                           
#         disputerPublicKeyX,                                                         
#         issuerListIdx,
#         disputerListIdx,                                                          
#         encrypted_shares,
#         commitments,
#         sharedKey,
#         sharedKeyCorrectnessProof).build_transaction({
#         "from": acct.address,
#         "nonce": w3.eth.get_transaction_count(acct.address),
#     })
#     signed_tx = w3.eth.account.sign_transaction(submitDispute_tx, private_key=acct.key)

#     # Send the raw transaction:
#     tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
#     receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
#     gas_used = receipt["gasUsed"]
#     transactionHash = receipt["transactionHash"]
#     print(f'register gas_used = {gas_used}')
#     print(f'transactionHash = {transactionHash.hex()}')
    
def submitKeyShare(
        listIdx,
        publicKeyX,
        keyShareG1,             
        keyShareG1CorrectnessProof,
        keyShareG2):
    
    staingPool = w3.eth.contract(address=contractAddress, abi=abi)

    # Manually build and sign a transaction:
    submitKeyShare_tx = staingPool.functions.submitKeyShare(
        listIdx, 
        publicKeyX,
        keyShareG1, 
        keyShareG1CorrectnessProof, 
        keyShareG2).build_transaction({
        "from": accts[listIdx].address,
        "nonce": w3.eth.get_transaction_count(accts[listIdx].address),
    })
    signed_tx = w3.eth.account.sign_transaction(submitKeyShare_tx, private_key=accts[listIdx].key)

    # Send the raw transaction:
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    gas_used = receipt["gasUsed"]
    transactionHash = receipt["transactionHash"]
    blockNumber = receipt["blockNumber"]
    
    print()
    print(f'from : {accts[listIdx].address}')
    print(f"node{listIdx}正在进行submitKeyShare, 请稍后")   #submitKeyShare gas_used = 273369
    print(f'listIdx = {listIdx}, publicKeyX = {publicKeyX}, keyShareG1 = {keyShareG1}, keyShareG1CorrectnessProof = { keyShareG1CorrectnessProof}, keyShareG2 = {keyShareG2}')
    print(f'blockNumber = {blockNumber}')
    print(f'submitKeyShare gas_used = {gas_used}')
    print(f'transactionHash = {transactionHash.hex()}')

def submitMasterPublicKey(listIdx, publicKeyX, masterPublicKey):
    staingPool = w3.eth.contract(address=contractAddress, abi=abi)
    print()

    # Manually build and sign a transaction:
    submitMasterPublicKey_tx = staingPool.functions.submitMasterPublicKey(publicKeyX, masterPublicKey).build_transaction({
        "from": accts[listIdx].address,
        "nonce": w3.eth.get_transaction_count(accts[listIdx].address)
    })
    signed_tx = w3.eth.account.sign_transaction(submitMasterPublicKey_tx, private_key=accts[listIdx].key)

    # Send the raw transaction:
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    gas_used = receipt["gasUsed"]
    transactionHash = receipt["transactionHash"]
    blockNumber = receipt["blockNumber"]

    print()
    print(f'from : {accts[listIdx].address}')
    print(f"node{listIdx} 正在进行 submitMasterPublicKey ，请稍后")   #submitMasterPublicKey gas_used = 355322
    print(f'publicKeyX = {publicKeyX}, masterPublicKey = {masterPublicKey}')
    print(f'blockNumber = {blockNumber}')
    print(f'submitMasterPublicKey gas_used = {gas_used}')
    print(f'transactionHash = {transactionHash.hex()}')

def submitGpkj(
        publicKeyX,
        listIdx,
        ggskj,                  
        encrypted_sharesQ,       # qualified
        commitmentsQ,         
        h1gpkj,                   
        h1gpkjCorrectnessProof,
        h2gpkj                   
        ):
    staingPool = w3.eth.contract(address=contractAddress, abi=abi)

    # Manually build and sign a transaction:
    submitGpkj_tx = staingPool.functions.submitGpkj(
        publicKeyX, 
        listIdx,
        ggskj,
        encrypted_sharesQ,
        commitmentsQ,
        h1gpkj,
        h1gpkjCorrectnessProof,
        h2gpkj
        ).build_transaction({
        "from": accts[listIdx].address,
        "nonce": w3.eth.get_transaction_count(accts[listIdx].address)
    })
    signed_tx = w3.eth.account.sign_transaction(submitGpkj_tx, private_key=accts[listIdx].key)

    # Send the raw transaction:
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    gas_used = receipt["gasUsed"]
    transactionHash = receipt["transactionHash"]
    blockNumber = receipt["blockNumber"]

    print()
    print(f'from : {accts[listIdx].address}')
    print(f"node{listIdx}正在进行 submitGpkj ，请稍后")   #submitGpkj gas_used = 430549
    print(f'publicKeyX = {publicKeyX}, listIdx = {listIdx}, ggskj = {ggskj}, encrypted_sharesQ = {encrypted_sharesQ}, commitmentsQ = {commitmentsQ}, h1gpkj = {h1gpkj}, h1gpkjCorrectnessProof = {h1gpkjCorrectnessProof}, h2gpkj = {h2gpkj}')
    print(f'blockNumber = {blockNumber}')
    print(f'submitGpkj gas_used = {gas_used}')
    print(f'transactionHash = {transactionHash.hex()}')
    
def depositToGoerli(  
        listIdx,                         
        publicKeyX,                     
        signature,              
        depositMessage                 
        ):
    staingPool = w3.eth.contract(address=contractAddress, abi=abi)

    # Manually build and sign a transaction:
    depositToGoerli_tx = staingPool.functions.depositToGoerli(
        publicKeyX, 
        signature,
        depositMessage,
        ).build_transaction({
        "from": accts[listIdx].address,
        "nonce": w3.eth.get_transaction_count(accts[listIdx].address)
    })
    signed_tx = w3.eth.account.sign_transaction(depositToGoerli_tx, private_key=accts[listIdx].key)

    # Send the raw transaction:
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    gas_used = receipt["gasUsed"]
    transactionHash = receipt["transactionHash"]
    blockNumber = receipt["blockNumber"]

    print()
    print(f'from : {accts[listIdx].address}')
    print(f"node{listIdx} 正在进行 depositToGoerli ，请稍后")                   # depositMessage gas_used = 529106
    print(f'publicKeyX = {publicKeyX}, signature = {signature}, depositMessage = {depositMessage}')
    print(f'blockNumber = {blockNumber}')
    print(f'register gas_used = {gas_used}')
    print(f'transactionHash = {transactionHash.hex()}')

# def normalExit(
#         publicKeyX, 
#         balanceInfo,
#         signature):
    
#     staingPool = w3.eth.contract(address=contractAddress, abi=abi)

#     # Manually build and sign a transaction:
#     normalExit_tx = staingPool.functions.normalExit(
#         publicKeyX, 
#         balanceInfo,
#         signature,
#         ).build_transaction({
#         "from": acct.address,
#         "nonce": w3.eth.get_transaction_count(acct.address)
#     })
#     signed_tx = w3.eth.account.sign_transaction(normalExit_tx, private_key=acct.key)

#     # Send the raw transaction:
#     tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
#     receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
#     gas_used = receipt["gasUsed"]
#     transactionHash = receipt["transactionHash"]
#     print(f'register gas_used = {gas_used}')
#     print(f'transactionHash = {transactionHash.hex()}')

def slashExit(
        listIdx,
        publicKeyX, 
        slashContents,       
        slashProof,       
        faultyPublicKeyX,            
        mutiBlsPK,             
        slashContentsSignature,     
        balanceInfo,               
        balanceInfoSignature):

    staingPool = w3.eth.contract(address=contractAddress, abi=abi)

    # Manually build and sign a transaction:
    slashExit_tx = staingPool.functions.slashExit(
        listIdx, 
        publicKeyX,
        slashContents,
        slashProof,       
        faultyPublicKeyX,            
        mutiBlsPK,             
        slashContentsSignature,     
        balanceInfo,               
        balanceInfoSignature
        ).build_transaction({
        "from": accts[listIdx].address,
        "nonce": w3.eth.get_transaction_count(accts[listIdx].address)
        
    })
    signed_tx = w3.eth.account.sign_transaction(slashExit_tx, private_key=accts[listIdx].key)

    # Send the raw transaction:
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    gas_used = receipt["gasUsed"]
    transactionHash = receipt["transactionHash"]
    blockNumber = receipt["blockNumber"]

    print(f'from : {accts[listIdx].address}')
    print(f"node0 正在进行 slashExit ，请稍后")  
    print(f"publicKeyX = {publicKeyX},slashContents = {slashContents}, slashProof = {slashProof}, faultyPublicKeyX = {faultyPublicKeyX}, mutiBlsPK = {mutiBlsPK}, slashContentsSignature = {slashContentsSignature}, balanceInfo = {balanceInfo}, balanceInfoSignature = {balanceInfoSignature}")
    print(f'blockNumber = {blockNumber}')
    print(f'slashExit gas_used = {gas_used}')
    print(f'transactionHash = {transactionHash.hex()}')


def laggingTrigExit(
        publicKeyX, 
        listIdx,
        exitInfo,
        exitInfoSig):

    staingPool = w3.eth.contract(address=contractAddress, abi=abi)

    # Manually build and sign a transaction:
    slashExit_tx = staingPool.functions.laggingTrigExit(
        publicKeyX, 
        listIdx,
        exitInfo,
        exitInfoSig,       
        ).build_transaction({
        "from": accts[listIdx].address,
        "nonce": w3.eth.get_transaction_count(accts[listIdx].address)
    })
    signed_tx = w3.eth.account.sign_transaction(slashExit_tx, private_key=accts[listIdx].key)

    # Send the raw transaction:
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    gas_used = receipt["gasUsed"]
    transactionHash = receipt["transactionHash"]
    blockNumber = receipt["blockNumber"]

    print(f'from : {accts[listIdx].address}')
    print(f"node0 正在进行 slashExit ，请稍后")  
    print(f"publicKeyX = {publicKeyX}, exitInfo = {exitInfo}, exitInfoSig ={exitInfoSig}")
    print(f'blockNumber = {blockNumber}')
    print(f'register gas_used = {gas_used}')
    print(f'transactionHash = {transactionHash.hex()}')


def getClusterAmount():
    StakingPool  = w3.eth.contract(address=contractAddress, abi=abi)

    cluster_amount = StakingPool.functions.clusterAmount().call()
    print(f'cluster_amount = {cluster_amount}')

def getCluster(clusterNumber):
    StakingPool  = w3.eth.contract(address=contractAddress, abi=abi)

    cluster = StakingPool.functions.clusters(clusterNumber).call()
    print(f'cluster = {cluster}')


def getNodeAmount():
    StakingPool  = w3.eth.contract(address=contractAddress, abi=abi)

    node_amount = StakingPool.functions.nodeAmount().call()
    print(f'node_amount = {node_amount}')

def getNode(nodePublicKeyX):
    StakingPool  = w3.eth.contract(address=contractAddress, abi=abi)

    node = StakingPool.functions.nodes(nodePublicKeyX).call()
    print(f'node = {node}')

def get_latest_block_number():
    return w3.eth.block_number

def is_block_finalized(block_number):
    # Get the latest finalized block
    latest_finalized_block = w3.eth.get_block("finalized")
    print(f"当前finalzed block number = {latest_finalized_block['number']}")
    return block_number > latest_finalized_block['number']

def log_loop(block_number, poll_interval):
    while is_block_finalized(block_number):
        
        time.sleep(poll_interval)
        print(f'当前时间为 : {time.time()}')


# getClusterAmount()
# getNodeAmount()

# getCluster(1)
# getNode(11857375388377339159917146126754708647444152272095756164728292003396664855507)
# getNode(12045861018111163016402813231563781346382350605582967587696925944172364694240)


