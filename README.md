# Setup
We have used 18.04.4 Bionic, Pandas, Python 3.6,Jupyter Notebook and Hyperledger AnonCreds 1.0 for generation and verification of Dynamic Identities(DID), Wallet address and Verifiable Credentials for the marketplace participants. 
But AnonCreds 1.0 basically works coordinating with Hyperledger Indy platform for generation of Indy System Pool for predefined verifiers for Aoncreds Issuers and verrifiers assisgning verifier roles -such as Trust Anchor (role ’101’)
or Trustee(role ’0’) respectively from the Indy system pool using Nym Transactions.

### Start Docker with the following command

docker-compose up-d

### to stop the docker after experiment 
docker-compose down

### Installation of Hyperledger Fabric platform 
cd fabric

./ install.sh

### Installation of Ethereum platform 
cd ethereum

sudo ./ install.sh
