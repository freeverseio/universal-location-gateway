from flask import Flask, jsonify, abort
import re
import json
from web3 import Web3
import requests
import time
import logging
import os

app = Flask(__name__)

def load_supported_consensus():
    with open('supportedConsensus.json', 'r') as config_file:
        return json.load(config_file)

def load_supported_ipfs_gateways():
    with open('supportedIPFSGateways.json', 'r') as config_file:
        ipfs_gateways = json.load(config_file)

    private_file_path = 'supportedIPFSGatewaysPrivate.json'
    if not os.path.exists(private_file_path):
        return ipfs_gateways
    
    with open(private_file_path, 'r') as config_file:
        ipfs_gateways_private = json.load(config_file)

    return ipfs_gateways + ipfs_gateways_private

# General function to extract content within parentheses after a specific keyword
def extract_between_parentheses(keyword, path_segments):
    """
    Extract content within parentheses that comes immediately after a specific keyword.

    :param keyword: The keyword to search for.
    :param path_segments: List of path segments from the URL.
    :return: Content within parentheses after the keyword if found, else None.
    """
    # Create a regular expression pattern that looks for the keyword followed by content within parentheses
    pattern = rf"{keyword}\((.*?)\)"
    for segment in path_segments:
        match = re.search(pattern, segment)
        if match:
            return match.group(1)  # Return the content within parentheses
    return None

def get_ul_fields(path):
    """
    Extracts and returns fields from the URL path, ensuring they are in the correct order:
    GlobalConsensus, Parachain, AccountKey20, GeneralKey.
    """
    # Split the path into segments for easier parsing
    path_segments = path.split('/')

    # Define the expected order of parameters
    expected_order = ['GlobalConsensus', 'Parachain', 'PalletInstance', 'AccountKey20', 'GeneralKey']

    # Initialize a dictionary to store extracted values
    values = {key: None for key in expected_order}

    # Iterate through the expected fields and extract values
    for expected in expected_order:
        value = extract_between_parentheses(expected, path_segments)
        if value is None:
            # If a parameter is missing or out of order, abort the request
            abort(400, description=f"URL parameter '{expected}' is missing or not in the expected order.")

        values[expected] = value
        path_segments.pop(0)  # Remove the processed segment

    # Return the extracted values in the expected order
    return tuple(values[key] for key in expected_order)

def get_chain_info(global_consensus, parachain, pallet_instance):
    """
    Get the RPC URL and chain ID from the configuration based on the global consensus and parachain.

    :param global_consensus: The global consensus identifier.
    :param parachain: The parachain identifier.
    :return: A tuple containing the RPC URL and chain ID if found, or aborts with a 400 error if not found.
    """
    supported_consensus = load_supported_consensus()  # Load the configuration
    for entry in supported_consensus:
        if (entry.get("GlobalConsensus") == global_consensus and
                entry.get("Parachain") == parachain and
                entry.get("PalletInstance") == pallet_instance):
            return entry.get('rpc'), entry.get('ChainId')

    return None, None



# Function to get the token_uri from a smart contract
def get_token_uri(rpc_urls, contract_address, asset_id):
    """
    Call an EVM chain RPC nodes provided in round-robin fashion to get the token_uri for a given 
    contract address and assetId. Retries up to the number of RPC URLs provided with a 1-second 
    delay between retries if an error occurs.

    :param rpc_urls: A list of RPC URLs of the EVM-compatible blockchain nodes.
    :param contract_address: The address of the smart contract.
    :param asset_id: The asset ID for which to retrieve the token URI.
    :return: The token URI if found, otherwise None.
    """
    contract_abi = [
        {
            "constant": True,
            "inputs": [{"name": "_tokenId", "type": "uint256"}],
            "name": "tokenURI",
            "outputs": [{"name": "", "type": "string"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function",
        },
    ]
    
    # Initialize the counter and number of RPC URLs
    attempts = 0
    num_rpc_urls = len(rpc_urls)

    while attempts < num_rpc_urls:
        rpc_url = rpc_urls[attempts % num_rpc_urls]  # Round-robin selection
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        checksum_address = web3.toChecksumAddress(contract_address)
        contract = web3.eth.contract(address=checksum_address, abi=contract_abi)
        
        try:
            token_uri = contract.functions.tokenURI(int(asset_id)).call()
            return token_uri
        except Exception as e:
            logging.error(f"Attempt {attempts+1}: Error occurred with RPC URL {rpc_url}: {e}")
            time.sleep(1)  # Delay for 1 second before the next attempt
            attempts += 1
    
    logging.error("Failed to fetch token URI after trying all RPC URLs.")
    return None

def determine_token_uri_standard(token_uri):
    if token_uri.startswith('ipfs://'):
        return "ipfs"
    elif token_uri.startswith('https://'):
        return "https"
    elif token_uri.startswith('http://'):
        return "http"
    else:
        return "unknown"

def fetch_ipfs_data(token_uri):
    # token_uri if forced to start with ipfs:// outside this method
    # Extract the CID and construct the URL with the IPFS gateway
    cid = token_uri.split('ipfs://')[1]

    ipfs_gateways = load_supported_ipfs_gateways()  # Load the configuration data
    for gateway in ipfs_gateways:
        ipfs_gateway_url = gateway.get("url")
        # example of suffix = "?pinataGatewayToken=2z....Nk" 
        apyKeySuffix = gateway.get("apiKeySuffix")
        full_uri = f'{ipfs_gateway_url}{cid}{apyKeySuffix}'
        try:
            response = requests.get(full_uri)
            response.raise_for_status()  # Raises HTTPError for unsuccessful status codes
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred with {ipfs_gateway_url}: {http_err}")
            # Continue to the next gateway if this one fails
        except Exception as err:
            logging.error(f"An error occurred with {ipfs_gateway_url}: {err}")
            # Continue to the next gateway if this one fails

    logging.error("Failed to fetch data from all IPFS gateways.")
    return None


@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@app.route('/<path:path>', methods=['GET'])
def handle_request(path):
    try:
        global_consensus, parachain, pallet_instance, account_key, general_key = get_ul_fields(path)
        if not all([global_consensus, parachain, pallet_instance, account_key, general_key]):
            abort(400, description="Invalid URL format.")

        rpc_urls, chain_id = get_chain_info(global_consensus, parachain, pallet_instance)

        if not rpc_urls:
            abort(404, description="RPC URLs not found.")

        tokenUri = get_token_uri(rpc_urls, account_key, general_key)
        if not tokenUri:
            abort(404, description="Token URI not found.")

        token_uri_standard = determine_token_uri_standard(tokenUri)
        if token_uri_standard in ["ipfs"]:
            token_uri_result = fetch_ipfs_data(tokenUri)
            if not token_uri_result:
                abort(502, description="Failed to fetch data from IPFS.")
        else:
            abort(400, description="Invalid token URI standard.")

        return jsonify(token_uri_result)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        abort(500, description="Internal Server Error")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
