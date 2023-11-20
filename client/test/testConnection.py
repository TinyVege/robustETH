from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
import os


# 或者连接到Infura提供的节点
infura_url = 'https://goerli.infura.io/v3/ed685130fe964c39aca273439462b5ed'
w3 = Web3(Web3.HTTPProvider(infura_url))


contract_address = '0x818F3d56b1282e4D23E01ABF14B813691025324f'
contract_abi = [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": 'false',
		"inputs": [
			{
				"indexed": 'false',
				"internalType": "address",
				"name": "withdrawalCredential",
				"type": "address"
			}
		],
		"name": "CreateWithdrawalCredential",
		"type": "event"
	},
	{
		"anonymous": 'false',
		"inputs": [
			{
				"indexed": 'false',
				"internalType": "uint256",
				"name": "groupIndex",
				"type": "uint256"
			},
			{
				"indexed": 'false',
				"internalType": "bytes",
				"name": "withdrawalCredential",
				"type": "bytes"
			}
		],
		"name": "Deposit",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "publicKeyX",
				"type": "uint256"
			},
			{
				"internalType": "uint256[2]",
				"name": "signature",
				"type": "uint256[2]"
			},
			{
				"internalType": "uint256[2]",
				"name": "depositMessage",
				"type": "uint256[2]"
			}
		],
		"name": "depositToGoerli",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": 'false',
		"inputs": [
			{
				"indexed": 'false',
				"internalType": "uint256",
				"name": "issuer",
				"type": "uint256"
			},
			{
				"indexed": 'false',
				"internalType": "uint256[2]",
				"name": "sharedKey",
				"type": "uint256[2]"
			},
			{
				"indexed": 'false',
				"internalType": "uint256[2]",
				"name": "sharedKeyCorrectnessProof",
				"type": "uint256[2]"
			}
		],
		"name": "Dispute",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint8",
				"name": "listIdx",
				"type": "uint8"
			},
			{
				"internalType": "uint256",
				"name": "publicKeyX",
				"type": "uint256"
			},
			{
				"internalType": "uint256[]",
				"name": "encryptedShares",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256[2][]",
				"name": "commitments",
				"type": "uint256[2][]"
			}
		],
		"name": "distributeShares",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": 'false',
		"inputs": [
			{
				"indexed": 'false',
				"internalType": "uint256[4]",
				"name": "gpkj",
				"type": "uint256[4]"
			}
		],
		"name": "Gpkj",
		"type": "event"
	},
	{
		"anonymous": 'false',
		"inputs": [
			{
				"indexed": 'false',
				"internalType": "address",
				"name": "issuer",
				"type": "address"
			},
			{
				"indexed": 'false',
				"internalType": "uint256[2]",
				"name": "keyShareG1",
				"type": "uint256[2]"
			},
			{
				"indexed": 'false',
				"internalType": "uint256[2]",
				"name": "keyShareG1CorrectnessProof",
				"type": "uint256[2]"
			},
			{
				"indexed": 'false',
				"internalType": "uint256[4]",
				"name": "keyShareG2",
				"type": "uint256[4]"
			}
		],
		"name": "KeyShareSubmission",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "publicKeyX",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "listIdx",
				"type": "uint256"
			},
			{
				"internalType": "uint256[]",
				"name": "exitInfo",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256[]",
				"name": "exitInfoSig",
				"type": "uint256[]"
			}
		],
		"name": "laggingTrigExit",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "publicKeyX",
				"type": "uint256"
			},
			{
				"internalType": "uint256[]",
				"name": "balanceInfo",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256[2]",
				"name": "signature",
				"type": "uint256[2]"
			}
		],
		"name": "normalExit",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "clusterSize",
				"type": "uint256"
			},
			{
				"internalType": "uint256[2]",
				"name": "nodePublicKey",
				"type": "uint256[2]"
			}
		],
		"name": "register",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"anonymous": 'false',
		"inputs": [
			{
				"indexed": 'false',
				"internalType": "uint256",
				"name": "nodeIndex",
				"type": "uint256"
			},
			{
				"indexed": 'false',
				"internalType": "address",
				"name": "nodeAddress",
				"type": "address"
			},
			{
				"indexed": 'false',
				"internalType": "uint256",
				"name": "clusterIndex",
				"type": "uint256"
			},
			{
				"indexed": 'false',
				"internalType": "uint256",
				"name": "clusderSize",
				"type": "uint256"
			}
		],
		"name": "Register",
		"type": "event"
	},
	{
		"anonymous": 'false',
		"inputs": [
			{
				"indexed": 'false',
				"internalType": "address",
				"name": "issuer",
				"type": "address"
			},
			{
				"indexed": 'false',
				"internalType": "uint256[]",
				"name": "encryptedShares",
				"type": "uint256[]"
			},
			{
				"indexed": 'false',
				"internalType": "uint256[2][]",
				"name": "commitments",
				"type": "uint256[2][]"
			}
		],
		"name": "ShareDistribution",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "publicKeyX",
				"type": "uint256"
			},
			{
				"internalType": "uint256[][2]",
				"name": "slashContents",
				"type": "uint256[][2]"
			},
			{
				"internalType": "uint256[2][2]",
				"name": "slashProof",
				"type": "uint256[2][2]"
			},
			{
				"internalType": "uint256[]",
				"name": "faultyPublicKeyX",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256[4]",
				"name": "mutiBlsPK",
				"type": "uint256[4]"
			},
			{
				"internalType": "uint256[2][2]",
				"name": "slashContentsSignature",
				"type": "uint256[2][2]"
			},
			{
				"internalType": "uint256[]",
				"name": "balanceInfo",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256[2]",
				"name": "balanceInfoSignature",
				"type": "uint256[2]"
			}
		],
		"name": "slashExit",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "issuerPublicKeyX",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "disputerPublicKeyX",
				"type": "uint256"
			},
			{
				"internalType": "uint8",
				"name": "issuerListIdx",
				"type": "uint8"
			},
			{
				"internalType": "uint8",
				"name": "disputerListIdx",
				"type": "uint8"
			},
			{
				"internalType": "uint256[]",
				"name": "encrypted_shares",
				"type": "uint256[]"
			},
			{
				"internalType": "uint256[2][]",
				"name": "commitments",
				"type": "uint256[2][]"
			},
			{
				"internalType": "uint256[2]",
				"name": "sharedKey",
				"type": "uint256[2]"
			},
			{
				"internalType": "uint256[2]",
				"name": "sharedKeyCorrectnessProof",
				"type": "uint256[2]"
			}
		],
		"name": "submitDispute",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "publicKeyX",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "listIdx",
				"type": "uint256"
			},
			{
				"internalType": "uint256[2]",
				"name": "ggskj",
				"type": "uint256[2]"
			},
			{
				"internalType": "uint256[][]",
				"name": "encrypted_sharesQ",
				"type": "uint256[][]"
			},
			{
				"internalType": "uint256[2][][]",
				"name": "commitmentsQ",
				"type": "uint256[2][][]"
			},
			{
				"internalType": "uint256[2]",
				"name": "h1gpkj",
				"type": "uint256[2]"
			},
			{
				"internalType": "uint256[2]",
				"name": "h1gpkjCorrectnessProof",
				"type": "uint256[2]"
			},
			{
				"internalType": "uint256[4]",
				"name": "h2gpkj",
				"type": "uint256[4]"
			}
		],
		"name": "submitGpkj",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint8",
				"name": "listIdx",
				"type": "uint8"
			},
			{
				"internalType": "uint256",
				"name": "publicKeyX",
				"type": "uint256"
			},
			{
				"internalType": "uint256[2]",
				"name": "keyShareG1",
				"type": "uint256[2]"
			},
			{
				"internalType": "uint256[2]",
				"name": "keyShareG1CorrectnessProof",
				"type": "uint256[2]"
			},
			{
				"internalType": "uint256[4]",
				"name": "keyShareG2",
				"type": "uint256[4]"
			}
		],
		"name": "submitKeyShare",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "publicKeyX",
				"type": "uint256"
			},
			{
				"internalType": "uint256[4]",
				"name": "masterPublicKey",
				"type": "uint256[4]"
			}
		],
		"name": "submitMasterPublicKey",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"stateMutability": "payable",
		"type": "receive"
	},
	{
		"inputs": [],
		"name": "clusterAmount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "clusters",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "clusterIndex",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "clusterSize",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "withdrawalCredential",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "laggingTrigExit",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getBalance",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "nodeAmount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "nodes",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "nodeIndex",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "nodeAddress",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "clusterIndex",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "clusterSize",
				"type": "uint256"
			},
			{
				"internalType": "bytes32",
				"name": "shareDistributionHash",
				"type": "bytes32"
			},
			{
				"internalType": "bytes",
				"name": "validatorPublicKey",
				"type": "bytes"
			},
			{
				"internalType": "bytes",
				"name": "signature",
				"type": "bytes"
			},
			{
				"internalType": "bytes32",
				"name": "depositDataRoot",
				"type": "bytes32"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

testConnection = w3.eth.contract(address=contract_address, abi=contract_abi)

pk = '0x4b35be94ffa17994df598a8b555d50e0971b25f94fea76c5e7b2714f3c403ffc'
acct = w3.eth.account.from_key(pk)


# Manually build and sign a transaction:
unsent_testConnection_tx = testConnection.functions.register(4, 
    [11857375388377339159917146126754708647444152272095756164728292003396664855507, 11576282137752257579123107959164751060099665303122339147293900962084264876601]
    ).build_transaction({
    "from": acct.address,
    "nonce": w3.eth.get_transaction_count(acct.address),
})
signed_tx = w3.eth.account.sign_transaction(unsent_testConnection_tx, private_key=acct.key)

# Send the raw transaction:
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
info = w3.eth.wait_for_transaction_receipt(tx_hash)
print(info)