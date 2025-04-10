# Universal Location Gateway

This Flask application serves as a gateway to fetch and return blockchain asset data by parsing universal location queries. It interacts with EVM-compatible blockchain nodes to retrieve token URIs and fetches associated metadata from IPFS.

## Features

- It parses the provided URL to extract blockchain-related parameters, following the [Universal Location Specification] (https://github.com/freeverseio/laos/issues/177). In particular, it tries to parse:
  - the blockchain
  - the contract address inside that blockchain
  - the `tokenId` created within that contract

- It then queries `tokenURI(tokenId)` in the parsed contract, and:
  - if `tokenURI` points to `ipfs://` it returns the content of that IPFS address
  - else, if `tokenURI` points to a valid URL, it returns the response of the server at that URL,
  - else, it returns the raw string returned by `tokenURI(tokenId)`.  

- It supports private IPFS providers. To set up your own provider, create the file `./supportedIPFSGatewaysPrivate.json` with content such as:

```
[
  {
    "url": "https://ul-gateway.mypinata.cloud/ipfs/",
    "apiKeySuffix": "?pinataGatewayToken=2z....Nk"
  }
]
```

## Limitations

Currently:
- it only supports locations in Polkadot, i.e. it reverts if the `Parachain` and `PalletInstance` junctions are not provided.

## Requirements

To run this project, you'll need:

- Python 3.7+
- Pip for installing Python packages
- Access to an EVM-compatible blockchain node


## Configuration
The project requires a `supportedConsensus.json` file to define mappings for global consensus parameters, with the following structure:

```json
[
  {
    "Name": "LAOS Sigma",
    "GlobalConsensus": "0:0x77afd6190f1554ad45fd0d31aee62aacc33c6db0ea801129acb813f913e0764f",
    "Parachain": "4006",
    "PalletInstance": "51",
    "ChainId": "62850",
    "rpc": ["https://rpc.laossigma.laosfoundation.io"]
  },
  {
    "Name": "LAOS Mainnet",
    "GlobalConsensus": "2",
    "Parachain": "3370",
    "PalletInstance": "51",
    "ChainId": "6283",
    "rpc": ["https://rpc.laos.laosfoundation.io"]
  }
]
```

## Usage
Install:
```bash
$ pip install -r requirements.txt
```

To start the application, run:

```bash
$ flask run
```

Or directly with python:
```bash
$ python app.py
```

To run tests locally:
```bash
$ pytest
```

When the server initiates, it logs the local server's URL (e.g., http://127.0.0.1:5000), where GET requests can be directed.


## Endpoints
- `GET /<path>`: Parses the given path as a universal location and returns the asset data.

## Testing
The functionality can be tested by using curl or any API client like Postman.

Start the server locally. Then run the following command line tests, which should return the json metadata of existing NFTs:
```bash
$ curl "http://10.10.152.90:8080/GlobalConsensus(2)/Parachain(3370)/PalletInstance(51)/AccountKey20(0xFffFFFFFFfFfFFFFfFFfFFFe0000000000000000)/GeneralKey(4046614996555278700417118163670322946781784547715)"

# the following is stored in a private server:
$ curl "http://10.10.152.90:8080/GlobalConsensus(0:0x77afd6190f1554ad45fd0d31aee62aacc33c6db0ea801129acb813f913e0764f)/Parachain(4006)/PalletInstance(51)/AccountKey20(0xfffffffffffffffffffffffe000000000000007b)/GeneralKey(1816828245772543144481346997133324732024448676966294077)"

$ curl "http://10.10.152.90:8080/GlobalConsensus(0:0x77afd6190f1554ad45fd0d31aee62aacc33c6db0ea801129acb813f913e0764f)/Parachain(4006)/PalletInstance(51)/AccountKey20(0xfffffffffffffffffffffffe000000000000007b)/GeneralKey(1820218929571150839251579545945226508630050440465998397)"
```
Likewise, this is a query about a token that does not exist:
```bash
$ curl "http://10.10.152.90:8080/GlobalConsensus(0:0x77afd6190f1554ad45fd0d31aee62aacc33c6db0ea801129acb813f913e0764f)/Parachain(4006)/PalletInstance(51)/AccountKey20(0xfffffffffffffffffffffffe000000000000007b)/GeneralKey(14320218929571150839251579545945226508630050440465998397)"
```

