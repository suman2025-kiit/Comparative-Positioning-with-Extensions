import asyncio
import json
import time
#from brownie import Contract,accounts
# import brownie
from web3.auto import Web3
from eth_account.messages import encode_defunct
#from eth_abi.packed import encode_abi_packed
from eth_utils import keccak
from pycoin.ecdsa.secp256k1 import secp256k1_generator
#from pycoin.ecdsa import sign, verify
import hashlib, secrets
from hashlib import sha1
#import ecdsa, ellipticcurve
#editor.renderWhitespace: all
from indy import pool, wallet, did, ledger,anoncreds
from indy.error import ErrorCode, IndyError
from ecdsa import SigningKey,SECP256k1
from Crypto.Hash import keccak
from solcx import compile_standard, install_solc
import os
from web3 import Web3
import subprocess
import time
import re
from itertools import chain
from solcx import compile_standard, install_solc

#editor.renderWhitespace: all

async def create_wallet(identity):
    print("\"{}\" -> Create wallet".format(identity['name']))
    try:
        await wallet.create_wallet(identity['wallet_config'],
                                   identity['wallet_credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    identity['wallet'] = await wallet.open_wallet(identity['wallet_config'],
                                                   identity['wallet_credentials'])
async def getting_verinym(from_, to):
    await create_wallet(to)

    (to['did'], to['key']) = await did.create_and_store_my_did(to['wallet'], "{}")
    from_['info'] = {
        'did': to['did'],
        'verkey': to['key'],
        'role': to['role'] or None
        }

    await send_nym(from_['pool'], from_['wallet'], from_['did'], from_['info']['did'],
                   from_['info']['verkey'], from_['info']['role'])

async def get_cred_def(pool_handle, _did, cred_def_id):
    get_cred_def_request = await ledger.build_get_cred_def_request(_did, cred_def_id)
    get_cred_def_response = \
        await ensure_previous_request_applied(pool_handle, get_cred_def_request,
                                              lambda response: response['result']['data'] is not None)
    return await ledger.parse_get_cred_def_response(get_cred_def_response)

async def send_nym(pool_handle, wallet_handle, _did, new_did, new_key, role):
    nym_request = await ledger.build_nym_request(_did, new_did, new_key, None, role)
    print(nym_request)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, _did, nym_request)

async def ensure_previous_request_applied(pool_handle, checker_request, checker):
    for _ in range(3):
        response = json.loads(await ledger.submit_request(pool_handle, checker_request))
        try:
            if checker(response):
                return json.dumps(response)
        except TypeError:
            pass
        time.sleep(5)

    # Generation of Indy Pools of Valid users for AnonCreds
dev_sign=""
async def run():
    print ("Anoncreds Demo Program for Identity Management and communicates with Registration Contract and PIECHAIN")
    print ("Generating and Connecting with the generated pool of valid users")

    pool_ ={
    "name": "pool1"
    }
    print ("Open pool for AnonCreds ledger:{}".format(pool_['name']))
    pool_['genesis_txn_path'] = "pool1.txn"
    pool_['config'] = json.dumps({"genesis_txn": str(pool_['genesis_txn_path'])})
    
    print(pool_)

    # Set protocol version 2 to work with Indy Node 1.4
    await pool.set_protocol_version(2)

    try:
        await pool.create_pool_ledger_config(pool_['name'], pool_['config'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    pool_['handle'] = await pool.open_pool_ledger(pool_['name'], None)

    print(pool_['handle'])

    print("\n\n\n========================================================================")
    print("==  System Genetered nonce  to handle the pool ==")
    print("============================================================================")
    #    --------------------------------------------------------------------------
    #  Accessing a steward.
    steward = {
        'name': "AnonCreds Poll registration and setup",
        'wallet_config': json.dumps({'id': 'sovrin_steward_wallet'}),
        'wallet_credentials': json.dumps({'key': 'steward_wallet_key'}),
        'pool': pool_['handle'],
        'seed': '000000000000000000000000Steward1'
    }
    print(steward)

    await create_wallet(steward)

    print(steward["wallet"])

    steward["did_info"] = json.dumps({'seed':steward['seed']})
    print(steward["did_info"])

# did:generated for the demoindynetwork for the validators to participate in the validation process :Th7MpTaRZVRYnPiabds81Y
    steward['did'], steward['key'] = await did.create_and_store_my_did(steward['wallet'], steward['did_info']
)

# ----------------------------------------------------------------------
    # Generatred and register dids for Issuer and Verifier
    # 
    print("\n\n\n=======================================================================")
    print("==  Issuer registering DIDs and Verinym for verifier (ISSUER))only ==")
    print("============================================================================")

    issuer = {
        'name': 'issuer',
        'wallet_config': json.dumps({'id': 'Issuer_wallet'}),
        'wallet_credentials': json.dumps({'key': 'Issuer_wallet_key'}),
        'pool': pool_['handle'],
        'role': 'TRUST_ANCHOR'
    }
    #issuer1 = bytes(issuer, 'utf-8')
    #issuer = (issuer, 'utf-8')
    await getting_verinym(steward, issuer)

    print("============================================================================")
    print("== Issuer registering DIDs and Verinym for verifier (VERIFIER))only ==")  
    print("============================================================================")

    verifier = {
        'name': 'verifier',
        'wallet_config': json.dumps({'id': 'verifier'}),
        'wallet_dest': json.dumps({'dest': 'destination'}),
        'wallet_credentials': json.dumps({'key': 'verifier_wallet_key'}),
        'pool': pool_['handle'],
        'role': 'TRUSTEE'
    }

    await getting_verinym(steward, verifier)

    private_key = SigningKey.generate()
    dest_has = hashlib.sha1(verifier['wallet_dest'].encode('utf-8')).hexdigest()
    #print("==========================================================================")
    print("=== 160-bit Address of the Verifier wallet in hexadecimal format=")
    #print("==========================================================================")
    did_byts = bytes(dest_has.encode('utf-8'))
    print('0x'+dest_has)
    print("\n==========================================================================")

    print("\n\n==========================================================================")
    print("== Issuer creates transcript schema and sends to the AnonCreds ledger  ==")
    print("=============================================================================")
    # -----------------------------------------------------
    # Issuer creates transcript Schema and sends to the AnonCreds ledger

    print("\"Issuer\" -> Create \"Transcript\" Schema")
    transcript = {
        'name': 'Transcript',
        'version': '1.2',
        'attributes': ['first_name', 'last_name', 'credentials', 'country', 'year', 'date', 'ssn','nonce']
    }
    (issuer['transcript_schema_id'], issuer['transcript_schema']) = \
        await anoncreds.issuer_create_schema(issuer['did'], transcript['name'], transcript['version'],
                                             json.dumps(transcript['attributes'])) 
                                             
    print(issuer['transcript_schema'])
    transcript_schema_id = issuer['transcript_schema_id']

    print(issuer['transcript_schema_id'], issuer['transcript_schema'])

    print("\"Issuer\" -> Send \"Transcript\" Schema to Ledger")

    schema_request = await ledger.build_schema_request(issuer['did'], issuer['transcript_schema'])
    await ledger.sign_and_submit_request(issuer['pool'], issuer['wallet'], issuer['did'], schema_request)

    # ------------------------------------------------------------
    # The Issuer will create a credential definition for the Scheme
    
    print("\n\n==========================================================================")
    print("=== Issuer will perform Credential Definition Setup ==")
    print("==============================================================================")

    print("\"Issuer\" -> Get \"Transcript\" Schema from Ledger")

    # GET SCHEMA FROM LEDGER
    get_schema_request = await ledger.build_get_schema_request(issuer['did'], transcript_schema_id)
    get_schema_response = await ensure_previous_request_applied(
        issuer['pool'], get_schema_request, lambda response: response['result']['data'] is not None)
    (issuer['transcript_schema_id'], issuer['transcript_schema']) = await ledger.parse_get_schema_response(get_schema_response)

    # TRANSCRIPT CREDENTIAL DEFINITION
    print("\"Issuer\" -> Create and store in Wallet \"Issuer generated\" Credential Definition")
    transcript_cred_def = {
        'tag': 'TAG1',
        'type': 'CL',
        'config': {"support_revocation": True}
    }
    (issuer['transcript_cred_def_id'], issuer['transcript_cred_def']) = \
        await anoncreds.issuer_create_and_store_credential_def(issuer['wallet'], issuer['did'],
                                                               issuer['transcript_schema'], transcript_cred_def['tag'],
                                                               transcript_cred_def['type'],
                                                               json.dumps(transcript_cred_def['config']))

    print("\"Issuer\" -> Send  \"Issuer defination\" Credential Definition to Ledger")
    # print(issuer['transcript_cred_def'])
    cred_def_request = await ledger.build_cred_def_request(issuer['did'], issuer['transcript_cred_def'])
    # print(cred_def_request)
    await ledger.sign_and_submit_request(issuer['pool'], issuer['wallet'], issuer['did'], cred_def_request)
    print("\n\n>>>>> Cresential Defination and Scheme for the Holder is generated by issuer with the Identity: \n\n", issuer['transcript_cred_def_id'])

    print("\n\n============================================================================")
    print("== Holder1(Actioner/Bidders) setup for wallet and credential defination== ==")
    print("================================================================================")

    Holder1 = {
        'name': 'Holder1',
        'wallet_config': json.dumps({'id': 'Holder1_wallet'}),
        'wallet_dest': json.dumps({'dest': 'Destination'}),
        'wallet_credentials': json.dumps({'key': 'Holder1_wallet_key'}),
        'pool': pool_['handle'],
    }
    await create_wallet(Holder1)
    (Holder1['did'], Holder1['key']) = await did.create_and_store_my_did(Holder1['wallet'], "{}")

    private_key = SigningKey.generate()
    dest_hash = hashlib.sha1(Holder1['wallet_dest'].encode('utf-8')).hexdigest()
    #print("==========================================================================")
    print("=== 160-bit Address of the Holder1 wallet in hexadecimal format=")
    #print("==========================================================================")
    did_byts = bytes(dest_hash.encode('utf-8'))
    hold_address = ('0x'+dest_hash)
    print(hold_address)
    print("\n==========================================================================")
    #k = keccak.new(digest_bits=256)
    #k.update(Holder1['wallet_dest'].encode('utf-8'))
    #byts = bytes(k.encode('utf-8'))
    #print('0x'+k.hexdigest())
     # Issuer creates transcript credential offer

    print("\"Issuer\" -> Create \"Transcript\" Credential Offer for Holder1")
    issuer['transcript_cred_offer'] = \
        await anoncreds.issuer_create_credential_offer(issuer['wallet'], issuer['transcript_cred_def_id'])

    print("\"Issuer\" -> Send \"Credentials\" for Scheme Credential Defination Identity to Holder1")

    # Over Network 
    Holder1['transcript_cred_offer'] = issuer['transcript_cred_offer']

    #print(Holder1['transcript_cred_offer'])
    print (issuer['transcript_cred_def_id'])

    transcript_cred_offer_object = json.loads(Holder1['transcript_cred_offer'])

    Holder1['transcript_schema_id'] = transcript_cred_offer_object['schema_id']
    Holder1['transcript_cred_def_id'] = transcript_cred_offer_object['cred_def_id']

    transcript_cred_offer_object['cred_def_id'] = json.dumps({
    'requested_predicates': {
            'predicate1_referent': {
                'restrictions': [{'cred_def_id': Holder1['transcript_cred_def_id']}]
            }
        } 
    })
    #print("\"Holder1\" -> Create and store \"Holder\" Master Secret in Wallet")
    Holder1['master_secret_id'] = await anoncreds.prover_create_master_secret(Holder1['wallet'], None)

    print("\"Holder1\" -> request for credentials and get \"Issuer generated \" credentials from Ledger")
    (Holder1['issuer_transcript_cred_def_id'], Holder1['issuer_transcript_cred_def']) = \
        await get_cred_def(Holder1['pool'], Holder1['did'], Holder1['transcript_cred_def_id'])

    print("\n\n============================================================================")
    print("== Getting Holder1 Pool Number, Generated DID and Credential Defination== ==")
    print("================================================================================")
        
    print("Pool No:",Holder1['pool'], "DID:",Holder1['did'], "Transaction Credention Def ID:",Holder1['transcript_cred_def_id']) 
    
    #print(Holder['transcript_cred_offer'])
    print("\"Holder1\" -> request \"Transcript\" Credential Request to Verifier")
    (Holder1['transcript_cred_request'], Holder1['transcript_cred_request_metadata']) = \
        await anoncreds.prover_create_credential_req(Holder1['wallet'], Holder1['did'],
                                                     Holder1['transcript_cred_offer'],
                                                     Holder1['issuer_transcript_cred_def'],
                                                     Holder1['master_secret_id'])
        
        #await anoncreds.prover_search_credentials_for_proof_req(Holder['wallet'], Holder['did'])
                                                    
    transcript_cred_offer_object['did'] = json.dumps({
        'requested_predicates': {
            'predicate1_referent': {
                'restrictions': [{'did': Holder1['did']}]
            }
        }
    })
    #print("\"Holder\" -> Send \"Transcript\" Credential Request to Verifier with " issuer['transcript_cred_def_id'])                                                
    print("\n\n==========================================================================")
    print("=== Getting Verifiable credential details for the Holder1  ==")    
    print("\n\n==========================================================================")  
    print(Holder1['transcript_cred_offer'])


    # Signing the transaction with DID of the Holder and sending it to Registration Smart Contract
    private_key = SigningKey.generate()
    did_has = hashlib.sha256(Holder1['did'].encode('utf-8')).hexdigest()
    print("\n\n==========================================================================")
    print("=== Transaction hash send by verifier for Holder1 while sending the DID information to =Registration Smart Contract=")
    print("\n\n==========================================================================")
    did_byts = bytes(did_has.encode('utf-8'))
    print('0x'+did_has)
    print("\n\n==========================================================================")
    print("=== ECDSA based Signed DID for Holder1 as RAW data after signing by AnonCresa Verifier==")
    print("\n\n==========================================================================")
    did_sin = private_key.sign(did_byts)
    print(did_sin)
    did_sign= did_sin.hex()
    print("\n\n==========================================================================")
    print("=== ECDSA based Signed HEXADECIMAL hashed transaction for Holder1 generated by AnonCresa Verifier==")
    print("\n\n==========================================================================")
    f = open("demofile2.txt", "a")
    f.write("Now the file has more content!")
    f.close()
    print('0x'+did_sign)
    
    print("\n\n==========================================================================")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(run())

start_time = time.time()

# helpful: https://gist.github.com/BjornvdLaan/e41d292339bbdebb831d0b976e1804e8
# tether contract: https://etherscan.io/token/0xdac17f958d2ee523a2206206994597c13d831ec7#code

# see https://coinsbench.com/how-to-deploy-and-interact-with-solidity-contracts-with-python-and-ganache-be63334323e6

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

install_solc("0.8.18")

with open(os.path.join(__location__, "./Registrationcontract.sol"), "r", encoding="utf-8") as file:
    coin_contract_file = file.read()

compiled_coin_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Registrationcontract.sol": {"content": coin_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_coin_sol, file)


# get bytecode
bytecode = compiled_coin_sol["contracts"]["Registrationcontract.sol"]["RegistrarHolderWithDid"]["evm"]["bytecode"]["object"]

# get abi
abi_contract = compiled_coin_sol["contracts"]["Registrationcontract.sol"]["RegistrarHolderWithDid"]["abi"]

# for connecting to ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
node_address = w3.eth.accounts[0]
print ("Node connected address:" + node_address)
node_private_key = "0xc3d00e9a07ac344b52d0e3292ef608170804ae04d7d4c1272dcead2cdf624659"

#deployed_coin_contract = w3.eth.contract(node_address, abi=abi_contract)

# Create a contract in python
Registrationcontract = w3.eth.contract(abi=abi_contract, bytecode=bytecode)
# Get the latest transaction
nonce = w3.eth.getTransactionCount(node_address)
# 1. build a transaction
# 2. sign a transaction
# 3. send a transaction
transaction = Registrationcontract.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": node_address,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key = node_private_key)
# send this signed trnsaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Deploying contract...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Contract was deployed!")

# working with a contract, you need...
# Contract abi
# Contract address
simple_storage = w3.eth.contract(address = tx_receipt.contractAddress, abi=abi_contract)
#----------------------------------------------------------

#----------------------------------------------------------
# Call > Simulate making the call and getting return values
# Transact > Actually making a state change
#hold_address = json.loads(Holder1['wallet_dest'])
#simple_storage.functions.registerHolders(json.dumps({'dest': 'Destination'}),json.dumps({'id': 'Holder1_wallet'}),Holder1).call()
# simple_storage.functions.registerHolders(Web3.to_checksum_address("0x6457b27f7a486931d5d6d894d63fd3f8285d8069"),"DShjcTEbHi1QmrjXeaF4H7","Holder1").call()
store_transaction = simple_storage.functions.registerHolders(Web3.to_checksum_address("0x6457b27f7a486931d5d6d894d63fd3f8285d8069"),"DShjcTEbHi1QmrjXeaF4H7","Holder1").buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": node_address,
        "nonce": nonce +1,
    }
)
sign_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key = node_private_key
)

send_store_tx = w3.eth.send_raw_transaction(sign_store_txn.rawTransaction)
print("Updating contract...")
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Retrieving information from contract...")
print(simple_storage.functions.registerHolders(Web3.to_checksum_address("0x6457b27f7a486931d5d6d894d63fd3f8285d8069"),"DShjcTEbHi1QmrjXeaF4H7","Holder1").call())
print(simple_storage.functions.getHolderDetails(Web3.to_checksum_address("0x6457b27f7a486931d5d6d894d63fd3f8285d8069")).call())
#print (simple_storage.functions.getHolderDetails(validinvalid)).call()
#print("Registration successful for Holder1!")



#open and read the file after the appending:
f = open("demofile2.txt", "r")
sts=f.read()
f.close()


store_transaction = simple_storage.functions.isValid_Signature_Hash(sts,"0x15e614e7dd17599a2c0f824a7247dda0675c13787e2333fc6dc0b671625db7b69b44fac2a8af73202bae54293e0e46ad").buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": node_address,
        "nonce": nonce +2,
    }


)
sign_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key = node_private_key
)
send_store_tx = w3.eth.send_raw_transaction(sign_store_txn.rawTransaction)
print("Updating contract...")
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Retrieving information from contract...")
print(simple_storage.functions.isValid_Signature_Hash("0xf66cc514b24516dfecd9be35e3b3a2427ad7f5302ed9c0515fb5ed4b2c4e1363","0x15e614e7dd17599a2c0f824a7247dda0675c13787e2333fc6dc0b671625db7b69b44fac2a8af73202bae54293e0e46ad").call())
#print(simple_storage.functions.getHolderDetails(Web3.to_checksum_address("0x6457b27f7a486931d5d6d894d63fd3f8285d8069")).call())

#loop = asyncio.get_event_loop()
end_time = time.time()
print("time duration:", (end_time - start_time))