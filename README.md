# Setup
We employed Bionic 18.04.4, Pandas, Python 3.6, Jupyter Notebook, and Hyperledger AnonCreds 1.0 to create and confirm Dynamic Identities (DID), Wallet addresses, and Verifiable Credentials (VC) for marketplace participants. AnonCreds 1.0 operates with the Hyperledger Indy platform to generate an Indy System Pool, assigning verifier roles like Trust Anchor (role '101') or Trustee (role '0') using Nym Transactions in our main21.py program.

 ### 1. Start Docker with the following command

docker-compose up-d

### to stop the docker after experiment 
docker-compose down

### 2. Installation 
AnonCreds 1.0 collaborates with the Hyperledger Indy platform, creating an Indy System Pool that assigns predefined verifiers, such as Trust Anchors (role '101') and Trustees (role '0'), through Nym Transactions in our main21.py program.

Please go inside path # cd fabric

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

### 3. Installation of Ethereum platform 
cd ethereum

sudo ./ install.sh

### 4. Installation of Hyperledger Indy platform for starting the system pool for AnonCreds and run the AnonCreds funcionality under Hyperledger platform

a.First clone Indy node repository for starting the repository using the commands- 

git clone https://github.com/hyperledger/indy-node.git 

Then go inside the directory using the command - cd indy-sdk

b. starting with a pre-configured docker image to build and run it for the pool:
   
docker build -f ci/indy-pool.dockerfile -t indy_pool.

docker run -itd -p 9701-9708: 9701-9708 ghoshbishakh/indy_pool

This creates an Indy container housing a pool of system-validated authenticators, each with a unique identity, pool number, and assigned port between 9701-9708.

c.Then run-  docker ps , to get the container identity forexample in our case it is 351k39691g56. 
Then go inside the indy pool docker container  using the command - docker exec -it 351k39691g56 bash

d. Now go inside the container 351k39691g56 and run the command - cat /var/lib/indy/sandbox/pool_transactions_genesis                                              
to get the details information of each validator nodes.

e. Now open a terminal and copy the information of all the information of validators nodes in to an text editotor that is opened using the command -'code.'.
and past all the information into the text editor and save it as 'pool1.txn' that is basically a type of JSON file for communication with the AnonCreds main code.

f. Import "main21.py" into the folder containing 'pool1.txn' to integrate Hyperledger AnonCreds for generating dynamic IDs, wallet addresses, and verifiable credentials for anonymous marketplace participant validation.

g. Now Import "main30.py" and "Registrationcontract.sol" into the editor's folder containing 'pool1.txn', then execute "main30.py" to validate dynamic identities and wallet addresses before registering marketplace participants.

All such coding related the aforesaid procedure is already uploaded under the path -  ### smajumder/did_wallet_management/indy-sdk/

### 5. Installation of python 3.6, Jupiter Note book and Pandas for running the graph generated from the dNFT Tokens 

a. Initially, install Python 3.6, Jupyter Notebook, and Pandas to efficiently generate reputation graphs using dNFT token data from wallet addresses.

b. The relevant information is uploaded in separate CSV files, detailing 'bidding and pricing,' linked to dynamically generated DID and Wallet Addresses, 'listing and current dNFT prices,' as well as 'dNFT owner, creator, and minting information,' to facilitate efficient data exchange (located at smajumder/Meritrank/NFT/data/).

c. Afterwards, a .JSON file is created from the .CSV files, shaping a multi-directed weighted graph (MDG) with nodes V linked to unique dynamic wallet addresses and edges E depicting token transfers from node Vi to Vj, using scripts like 'hitting_time.py', 'random_walks.py', located at smajumder/Meritrank/NFT/Trust/.

d. Create 'read_data.py' and the 'NFT_mail_file.ipynb' as found in the directory smajumder/Meritrank/NFT/, then execute 'NFT_mail_file.ipynb' to produce outputs depicted from Figures 2 to 10 in the manuscript.

### 6. Installation of Hyperledger Caliper platform, please follow the steps as mentioned in the detailed link

a.Please follow the installation procedure as mentioned in the link below:
https://hyperledger.github.io/caliper/v0.5.0/installing-caliper/

### 7. For running the Caliper sut configuration of thr benchmark and generate the report in tabular format using Prometheus, run the following command in Hyperledger caliper platform 

a. Please the upload the files as mentioned in the paths ### - smajumder/Caliper/caliper-benchmarks/ 
and smajumder/fabric/ .

b. Run the following command for generation of reports in 'Prometheus' as shown in Figures 11 and Figure 12 respectively in the manuscript.

npx caliper launch manager --caliper-bind-sut fabric:2.2 --caliper-workspace . --caliper-benchconfig benchmarks/scenario/simple/config.yaml --caliper-networkconfig networks/fabric/test-network.yaml
