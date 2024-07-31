# Universal Location Gateway

This Flask application serves as a gateway to fetch and return blockchain asset data by parsing universal location queries. It interacts with EVM-compatible blockchain nodes to retrieve token URIs and fetches associated metadata from IPFS.

## Features

- Parses URLs to extract blockchain-related parameters, following the [Universal Location Specification] (https://github.com/freeverseio/laos/issues/177)
- Retrieves blockchain asset data from EVM-compatible chains connecting to the corresponding RPC nodes.
- Fetches and returns IPFS-hosted metadata.
- It supports private IPFS providers. Create the file `./supportedIPFSGatewaysPrivate.json` with content such as:

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
- it only supports `tokenURI` that returns an ipfs address.
- it only supports ipfs addresses that return strings that can be parsed as a json object, explicitly, via the `jsonify` method.
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

The following command line test should return the json metadata of an NFT on **LAOS Sigma**:
```bash
$ curl "http://127.0.0.1:5000/GlobalConsensus(0:0x77afd6190f1554ad45fd0d31aee62aacc33c6db0ea801129acb813f913e0764f)/Parachain(4006)/PalletInstance(51)/AccountKey20(0xfffffffffffffffffffffffe0000000000000004)/GeneralKey(34560331594530882314307165352126634424401996839473067194454284012200635144743)"
```  
