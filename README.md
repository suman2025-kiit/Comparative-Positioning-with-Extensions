# Setup
We have used 18.04.4 Bionic, Pandas, Python 3.6,Jupyter Notebook and Hyperledger AnonCreds 1.0 for generation and verification of Dynamic Identities(DID), Wallet address and Verifiable Credentials (VC) for the marketplace participants. 
But AnonCreds 1.0 basically works coordinating with Hyperledger Indy platform for generation of Indy System Pool for predefined verifiers for Aoncreds Issuers and verrifiers assisgning verifier roles -such as Trust Anchor (role ’101’)
or Trustee(role ’0’) respectively from the Indy system pool using Nym Transactions as implemented in the coding (main21.py program (attached herewith ) for generation of DID, Wallet address and VC).

### Start Docker with the following command

docker-compose up-d

### to stop the docker after experiment 
docker-compose down

### Installation of Hyperledger Fabric platform 
cd fabric

./ install.sh

####  during Installation of Fabric, also please confirm that the following commands will run successfully
/network down

./network up

Add mychannel:

./network.sh createChannel -c mychannel

Add simple chaincode to channel:

./network.sh deployCC -ccn simple -ccp /home/suman/Downloads/caliper-benchmarks/src/fabric/samples/marbles/go -ccl go

Invoke chain code:

peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile
${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n simple --peerAddresses localhost:7051 --tlsRootCertFiles 

${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt --peerAddresses localhost:9051 --tlsRootCertFiles 

${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt -c '{"function":"InitLedger","Args":[]}'

 
in test-networkfolder (onetime thing): 

export FABRIC_CFG_PATH=$PWD/../config/

export CORE_PEER_TLS_ENABLED=true

export CORE_PEER_LOCALMSPID="Org1MSP"

export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt

export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp

export CORE_PEER_ADDRESS=localhost:7051

### Installation of Ethereum platform 
cd ethereum

sudo ./ install.sh

### Installation of Hyperledger Indy platform for starting the system pool for AnonCreds

1.First clone Indy node repository for starting the repository using the commands- 

git clone https://github.com/hyperledger/indy-node.git 

Then go inside the directory using the command - cd indy-sdk

2. starting with a pre-configured docker image to build and run it for the pool:
   
docker build -f ci/indy-pool.dockerfile -t indy_pool.

docker run -itd -p 9701-9708: 9701-9708 ghoshbishakh/indy_pool

This will make an indy container for the poll of system generated validators in which all the pre-defined authenticated validators with proper identity and pool number ans assigned the specific port number within the range 9701-9708.

Then run docker ps , to get the container identity forexample in our case it is 351k39691g56. 
Then go inside the indy pool docker container  using the command - docker exec -it 351k39691g56 bash

Now go inside the container 351k39691g56 and run the command - cat /var/lib/indy/sandbox/pool_transactions_genesis                                              
to get the details information of each validator nodes.

Now open a terminal and copy the information of all the information of validators nodes in to an text editotor that is opened using the command -'code.'.
and past all the information into the text editor and save it as pool1.txn that is basically a type of JSON file for communication with the AnonCreds main code.





### Installation of Hyperledger Caliper platform, please follow the steps as mentioned in the detailed link
https://hyperledger.github.io/caliper/v0.5.0/installing-caliper/

### For running the Caliper sut configuration of thr benchmark and generate the report in tabular format using Prometheus, run the following command after Hyperledger caliper installation
npx caliper launch manager --caliper-bind-sut fabric:2.2 --caliper-workspace . --caliper-benchconfig benchmarks/scenario/simple/config.yaml --caliper-networkconfig networks/fabric/test-network.yaml
