# Universal Location Gateway

This Flask application serves as a gateway to fetch and return blockchain asset data by parsing universal location queries. It interacts with EVM-compatible blockchain nodes to retrieve token URIs and fetches associated metadata from IPFS.

## Features

- Parses URLs to extract blockchain-related parameters.
- Retrieves blockchain asset data from EVM-compatible chains using RPC.
- Fetches and returns IPFS-hosted metadata.

## Requirements

To run this project, you'll need:

- Python 3.7+
- Pip for installing Python packages
- Access to an EVM-compatible blockchain node

## Installation

First, clone the repository to your local machine:

```bash
git clone https://your-repository-url.git
cd universal-location-gateway
```

Then, set up a virtual environment and install the dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## Configuration
The project requires a config.json file to define mappings for global consensus parameters. The structure of the config.json file is as follows:

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
flask run
```

Or directly with python:
```bash
python app.py
```

The server will start, and you can send GET requests to http://localhost:4000/ with the appropriate path to receive asset data.

## Endpoints
- GET /<path>: Parses the given path as a universal location and returns the asset data.

## Testing
You can test the functionality by using curl or any API client like Postman.

Example request:
```bash
curl http://localhost:4000/GlobalConsensus(your_global_consensus)/Parachain(your_parachain)/AccountKey20(your_account_key)/GeneralKey(your_general_key)
```
