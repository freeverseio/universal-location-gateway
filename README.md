# Universal Location Gateway

This Flask application serves as a gateway to fetch and return blockchain asset data by parsing universal location queries. It interacts with EVM-compatible blockchain nodes to retrieve token URIs and fetches associated metadata from IPFS.

## Features

- Parses URLs to extract blockchain-related parameters, following the [Universal Location Specification] (https://github.com/freeverseio/laos/issues/177)
- Retrieves blockchain asset data from EVM-compatible chains connecting to the corresponding RPC nodes.
- Fetches and returns IPFS-hosted metadata.

## Requirements

To run this project, you'll need:

- Python 3.7+
- Pip for installing Python packages
- Access to an EVM-compatible blockchain node


## Configuration
The project requires a `config.json`` file to define mappings for global consensus parameters, with the following structure:

```json
{
    "GlobalConsensusMappings": {
        "consensus_key": {
            "relayChainName": "Relay Chain Name",
            "Parachains": {
                "parachain_key": {
                    "name": "Parachain Name",
                    "rpc": "RPC URL",
                    "chainId": "Chain ID"
                }
            }
        }
    }
}
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

When the server initiates, it logs the local server's URL (e.g., http://localhost:4000), where GET requests can be directed.

## Endpoints
- `GET /<path>`: Parses the given path as a universal location and returns the asset data.

## Testing
The functionality can be tested by using curl or any API client like Postman.

Example request:
```bash
$ curl "http://localhost:4000/GlobalConsensus(your_global_consensus)/Parachain(your_parachain)/AccountKey20(your_account_key)/GeneralKey(your_general_key)"
```
