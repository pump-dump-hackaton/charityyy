from collections import namedtuple
from web3 import Web3
import json

PROVIDER_RPC = 'https://westend-asset-hub-eth-rpc.polkadot.io'

def _load_abi(contract_name):
    try:
        with open(contract_name, 'r') as file:
            return json.load(file)
    except Exception as error:
        print(f"❌ Could not find ABI for contract {contract_name}: {error}")
        raise error

def _load_bytecode(contract_name):
    try:
        with open(contract_name, 'rb') as file:
            return '0x' + file.read().hex()
    except Exception as error:
        print(f"❌ Could not find bytecode for contract {contract_name}: {error}")
        raise error

def _connect_to_rpc():
    try:
        # Initialize Web3 with RPC URL
        return Web3(Web3.HTTPProvider(PROVIDER_RPC))
    except Exception as e:
        print("Couldn't connect to the PRC: " + e)
        raise Exception("Couldn't connect to RPC")

CONTRACT_ABI = _load_abi("contract/proposal.json")
CONTRACT_CODE = _load_bytecode("contract/proposal.polkavm")

Expense = namedtuple('Expense', 'address amount')

def deploy_proposal(expenses: list[Expense], public_key, private_key):
    web3 = _connect_to_rpc()

    # Prepare account
    account = web3.eth.account.from_key(private_key)
    print(f"address: {account.address}")

    # Create contract instance
    contract = web3.eth.contract(abi=CONTRACT_ABI, bytecode=CONTRACT_CODE)

    # Get current nonce
    nonce = web3.eth.get_transaction_count(account.address)

    # Prepare deployment transaction
    transaction = {
        'from': account.address,
        'nonce': nonce,
    }

    # Build and sign transaction
    addresses = [expense.address for expense in expenses]
    amounts = [expense.amount for expense in expenses]

    construct_txn = contract.constructor(addresses, amounts, public_key).build_transaction(transaction)
    signed_txn = web3.eth.account.sign_transaction(construct_txn, private_key=private_key)

    # Send transaction
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction hash: {tx_hash.hex()}")

    # Wait for transaction receipt
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress

    # Log and return contract details
    print(f"Contract deployed at: {contract_address}")
    return contract_address

def donate(amount, contract_address, private_key):
    # Initialize Web3 with RPC URL
    web3 = _connect_to_rpc()

    # Prepare account
    account = web3.eth.account.from_key(private_key)

    # Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=CONTRACT_ABI)

    # Get current nonce
    nonce = web3.eth.get_transaction_count(account.address)

    # Prepare transaction
    transaction = contract.functions.donate(amount).build_transaction({
        'from': account.address,
        'nonce': nonce
    })

    # Sign transaction
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)

    # Send transaction
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction hash: {tx_hash.hex()}")

    # Wait for receipt
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    return receipt

def get_info(contract_address):
    web3 = _connect_to_rpc()

    # Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=CONTRACT_ABI)
    expenses = contract.functions.expenses().call()
    funds_raised = contract.functions.funds_raised().call()

    return expenses, funds_raised
