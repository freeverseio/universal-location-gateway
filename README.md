# Universal Location Gateway

This Flask application serves as a gateway to fetch and return blockchain asset data by parsing universal location queries. It interacts with EVM-compatible blockchain nodes to retrieve token URIs and fetches associated metadata from IPFS.

## Features

- Parses URLs to extract blockchain-related parameters, following the [Universal Location Specification] (https://github.com/freeverseio/laos/issues/177)
- Retrieves blockchain asset data from EVM-compatible chains connecting to the corresponding RPC nodes.
- Fetches and returns IPFS-hosted metadata.

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
    "Name": "Caladan",
    "GlobalConsensus": "0:0x22c48a576c33970622a2b4686a8aa5e4b58350247d69fb5d8015f12a8c8e1e4c",
    "Parachain": "2900",
    "PalletInstance": "51",
    "ChainId": "667",
    "rpc": ["https://caladan.gorengine.com/own"]
  },
  {
    "Name": "KLAOS",
    "GlobalConsensus": "3",
    "Parachain": "3336",
    "PalletInstance": "51",
    "ChainId": "2718",
    "rpc": ["https://rpc.klaos.laosfoundation.io"]
  }
]
```

## Usage
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


When the server initiates, it logs the local server's URL (e.g., http://localhost:4000), where GET requests can be directed.

## Endpoints
- `GET /<path>`: Parses the given path as a universal location and returns the asset data.

## Testing
The functionality can be tested by using curl or any API client like Postman.

Example request:
```bash
$ curl "http://localhost:4000/GlobalConsensus(your_global_consensus)/Parachain(your_parachain)/AccountKey20(your_account_key)/GeneralKey(your_general_key)"
```
