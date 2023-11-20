
from web3 import Web3
from threading import Thread
import time

# instantiate Web3 instance
w3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/ed685130fe964c39aca273439462b5ed"))

def is_block_finalized(block_number):
    # Get the latest finalized block
    latest_finalized_block = w3.eth.get_block("finalized")
    print(f"当前finalzed block number = {latest_finalized_block['number']}")
    return block_number > latest_finalized_block['number']

def log_loop(block_number, poll_interval):
    while is_block_finalized(block_number):
        
        time.sleep(poll_interval)
        print(f'当前时间为 : {time.time()}')



def main():
    time_start = time.time()
    print(f'开始时间为 : {time_start}')

    current_block_number =  w3.eth.block_number
    print(f'当前区块号是 : {current_block_number}')

    log_loop(current_block_number, 12)

    time_end = time.time()
    print(f'结束时间为 : {time_end}')

    print(f'持续时间为 : {time_end - time_start}')
    

if __name__ == '__main__':
    main()  