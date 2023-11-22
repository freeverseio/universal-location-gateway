from flask import Flask, jsonify
import re
import json


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
def get_chain_rpc(global_consensus, parachain=""):
    """
    Get the RPC URL from the configuration based on the global consensus and parachain.

    :param global_consensus: The global consensus identifier.
    :param parachain: The parachain identifier.
    :return: The RPC URL if found, or None if not found.
    """
    config = load_config()  # Load the configuration
    consensus_config = config.get('GlobalConsensusMappings', {}).get(global_consensus, {})
    parachain_config = consensus_config.get('Parachains', {}).get(parachain, {})
    return parachain_config.get('rpc')  # Return the RPC URL or None if not found

@app.route('/<path:path>', methods=['GET'])
def handle_request(path):
    """
    Handle the incoming request and parse the URL for specific components.

    :param path: The full path from the request URL.
    :return: A JSON response with the parsed components.
    """
    global_consensus, parachain, account_key, general_key = get_ul_fields(path)
    rpc_url = get_chain_rpc(global_consensus, parachain)
    return jsonify({
        "GlobalConsensus": global_consensus,
        "Parachain": parachain,
        "AccountKey20": account_key,
        "GeneralKey": general_key,
        "rpc_url":rpc_url
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
