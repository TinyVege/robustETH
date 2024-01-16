from web3 import Web3
from contractInfo import private_keys
import time


infura_url = 'https://goerli.infura.io/v3/ed685130fe964c39aca273439462b5ed'
w3 = Web3(Web3.HTTPProvider(infura_url))

private_keys = private_keys
accts = []
for key in private_keys:
    accts.append(w3.eth.account.from_key(key))


def transfer(sender_acct, recipient_acct):

    # Build the transaction
    transfer_tx = {
        "to": recipient_acct.address,
        "value": w3.to_wei(100000000000000000),  # Amount to transfer in wei (1 ether in this example)
        "nonce": w3.eth.get_transaction_count(sender_acct.address),
        "gas": 21000,
        "gasPrice": w3.eth.gas_price
    }
    signed_tx = w3.eth.account.sign_transaction(transfer_tx, private_key=sender_acct.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    gas_used = receipt["gasUsed"]
    transactionHash = receipt["transactionHash"]
    blockNumber = receipt["blockNumber"]
    print(f'blockNumber = {blockNumber}')
    print(f'deployment gas_used = {gas_used}')    
    print(f'transactionHash = {transactionHash.hex()}') 

def getBalance(acct):
    balance = w3.eth.get_balance(acct.address)
    balance = w3.from_wei(balance, 'ether')
    print(f'account: {acct.address}, balance : {balance}')

def is_block_finalized(block_number):
    # Get the latest finalized block
    latest_finalized_block = w3.eth.get_block("finalized")
    print(f"当前finalzed block number = {latest_finalized_block['number']}")
    return block_number > latest_finalized_block['number']

def log_loop(block_number, poll_interval):
    while is_block_finalized(block_number):
        
        time.sleep(poll_interval)
        print(f'当前时间为 : {time.time()}')

# for i in range(1, len(accts)):
#     transfer(accts[0], accts[i])

transfer(accts[0], )

# for i in range(len(accts)):
#     getBalance(accts[i])



 