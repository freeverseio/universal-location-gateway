from flask import Flask, jsonify
import re

app = Flask(__name__)

# General function to extract content within parentheses after a specific keyword
def extract_content(keyword, path_segments):
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

@app.route('/<path:path>', methods=['GET'])
def handle_request(path):
    """
    Handle the incoming request and parse the URL for specific components.

    :param path: The full path from the request URL.
    :return: A JSON response with the parsed components.
    """
    # Split the path into segments for easier parsing
    path_segments = path.split('/')

    # Call the extract_content function for each component
    global_consensus = extract_content('GlobalConsensus', path_segments)
    account_key = extract_content('AccountKey20', path_segments)
    general_key = extract_content('GeneralKey', path_segments)

    # Construct the response with the parsed data
    response = {
        "GlobalConsensus": global_consensus,
        "AccountKey20": account_key,
        "GeneralKey": general_key
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
