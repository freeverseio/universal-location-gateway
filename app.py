from flask import Flask, jsonify
import re
import json
from web3 import Web3
import requests

app = Flask(__name__)

# Load the configuration data from the JSON file into a dictionary
def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

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
    # Split the path into segments for easier parsing
    path_segments = path.split('/')

    # Call the extract_content function for each component
    global_consensus = extract_between_parentheses('GlobalConsensus', path_segments)
    parachain = extract_between_parentheses('Parachain', path_segments)
    account_key = extract_between_parentheses('AccountKey20', path_segments)
    general_key = extract_between_parentheses('GeneralKey', path_segments)

    # Construct the response with the parsed data
    response = {
        "GlobalConsensus": global_consensus,
        "Parachain": parachain,
        "AccountKey20": account_key,
        "GeneralKey": general_key
    }
    return(global_consensus, parachain, account_key, general_key)


# Define a function to get the RPC URL from the config given the global consensus and parachain
def get_chain_info(global_consensus, parachain=""):
    """
    Get the RPC URL from the configuration based on the global consensus and parachain.

    :param global_consensus: The global consensus identifier.
    :param parachain: The parachain identifier.
    :return: The RPC URL if found, or None if not found.
    """
    config = load_config()  # Load the configuration
    consensus_config = config.get('GlobalConsensusMappings', {}).get(global_consensus, {})
    parachain_config = consensus_config.get('Parachains', {}).get(parachain, {})
    return parachain_config.get('rpc'), parachain_config.get('chainId')  # Return the RPC URL or None if not found

# Function to get the tokenURI from a smart contract
def get_token_uri(rpc_url, contract_address, asset_id):
    """
    Call an EVM chain RPC node to get the tokenURI for a given contract address and assetId.

    :param rpc_url: The RPC URL of the EVM-compatible blockchain node.
    :param contract_address: The address of the smart contract.
    :param asset_id: The asset ID for which to retrieve the token URI.
    :return: The token URI if found, otherwise None.
    """
    # Initialize a web3 connection to the RPC
    web3 = Web3(Web3.HTTPProvider(rpc_url))

    # Define the contract ABI to include only the function we're interested in (tokenURI)
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

    # Create a contract object using the contract address and ABI
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    try:
        # Call the tokenURI function of the contract
        token_uri = contract.functions.tokenURI(int(asset_id)).call()
        return token_uri
    except Exception as e:
        app.logger.error(f"An error occurred when fetching token URI: {e}")
        return None

def fetch_ipfs_data(token_uri):
    #TODO Modify function in order to filder for ipfs:// when the tokenURI returns it
    # Check if the token URI already includes the IPFS gateway URL
    if not token_uri.startswith('https://ipfs.io/ipfs/'):
        token_uri = 'https://ipfs.io/ipfs/' + token_uri

    try:
        response = requests.get(token_uri)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Python 3.6
        return None
    except Exception as err:
        print(f"An error occurred: {err}")  # Python 3.6
        return None

@app.route('/<path:path>', methods=['GET'])
def handle_request(path):
    """
    Handle the incoming request and parse the URL to get the content of the tokenURI of that Universal Location.

    :param path: The full path from the request URL.
    :return: A JSON response with the parsed components.
    """
    global_consensus, parachain, account_key, general_key = get_ul_fields(path)
    rpcUrl, chainId = get_chain_info(global_consensus, parachain)
    tokenUri = get_token_uri(rpcUrl, account_key, general_key)
    tokenURIResult = fetch_ipfs_data(tokenUri)
    return jsonify(tokenURIResult)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
