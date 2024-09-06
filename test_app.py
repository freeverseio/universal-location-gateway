import unittest
from app import *
from unittest.mock import patch, MagicMock
from werkzeug.exceptions import HTTPException

class TestApp(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @patch('app.get_ul_fields')
    @patch('app.get_chain_info')
    @patch('app.get_token_uri')
    @patch('app.fetch_ipfs_data')
    def test_handle_request_success(self, mock_fetch_ipfs_data, mock_get_token_uri, mock_get_chain_info, mock_get_ul_fields):
        # Mock the functions to return expected values
        mock_get_ul_fields.return_value = ('3', '3336', '51', '0xABC123', '789')
        mock_get_chain_info.return_value = (['http://example.com'], 1)
        mock_get_token_uri.return_value = 'ipfs://tokenUri'
        mock_fetch_ipfs_data.return_value = {'data': 'some data'}

        response = self.client.get('/GlobalConsensus(123)/Parachain(456)/AccountKey20(0xABC123)/GeneralKey(789)')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'data': 'some data'})

    @patch('app.get_ul_fields')
    def test_handle_request_invalid_path(self, mock_get_ul_fields):
        # Mock get_ul_fields to return None values indicating an invalid path
        mock_get_ul_fields.return_value = (None, None, None, None)

        response = self.client.get('/invalid/path')
        self.assertEqual(response.status_code, 500)

    def test_load_supported_consensus(self):
        config = load_supported_consensus()
        self.assertIsNotNone(config)

    def test_load_supported_ipfs(self):
        config = load_supported_ipfs_gateways()
        self.assertIsNotNone(config)

    def test_extract_between_parentheses(self):
        path_segments = ['GlobalConsensus(123)', 'Parachain(456)']
        result = extract_between_parentheses('GlobalConsensus', path_segments)
        self.assertEqual(result, '123')

        result = extract_between_parentheses('Parachain', path_segments)
        self.assertEqual(result, '456')

        result = extract_between_parentheses('NonExisting', path_segments)
        self.assertIsNone(result)

    def test_get_ul_fields_correct_order(self):
        path = 'GlobalConsensus(123)/Parachain(456)/PalletInstance(52)/AccountKey20(0xABC123)/GeneralKey(789)'
        expected = ('123', '456', '52', '0xABC123', '789')
        self.assertEqual(get_ul_fields(path), expected)

    def test_get_ul_fields_incorrect_order(self):
        path = 'Parachain(456)/GlobalConsensus(123)/AccountKey20(0xABC123)/GeneralKey(789)'
        with self.assertRaises(HTTPException) as context:
            get_ul_fields(path)
        self.assertEqual(context.exception.code, 400)
    
    def test_get_ul_fields_missing_field(self):
        path = 'GlobalConsensus(123)/AccountKey20(0xABC123)/GeneralKey(789)'
        with self.assertRaises(HTTPException) as context:
            get_ul_fields(path)
        self.assertEqual(context.exception.code, 400)

    def test_get_ul_fields_empty_path(self):
        path = ''
        with self.assertRaises(HTTPException) as context:
            get_ul_fields(path)
        self.assertEqual(context.exception.code, 400)

    @patch('app.load_supported_consensus')
    def test_get_chain_info(self, mock_load_config):
        loaded_config = load_supported_consensus()
        mock_load_config.return_value = loaded_config

        rpc_urls, chain_id = get_chain_info('3', '3336', '51')
        self.assertEqual(rpc_urls, ['https://rpc.klaos.laosfoundation.io'])
        self.assertEqual(chain_id, '2718')

        rpc_url, chain_id = get_chain_info('999', '888', '52')
        self.assertIsNone(rpc_url)
        self.assertIsNone(chain_id)

    @patch('app.requests.get')
    @patch('app.load_supported_ipfs_gateways')
    def test_fetch_ipfs_data_success(self, mock_load_gateways, mock_requests_get):
        loaded_config = load_supported_ipfs_gateways()
        mock_load_gateways.return_value = loaded_config
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "some data"}
        mock_requests_get.return_value = mock_response

        result = fetch_ipfs_data('ipfs://someCID')
        self.assertEqual(result, {"data": "some data"})
        mock_requests_get.assert_called_with('https://ipfs.io/ipfs/someCID')

    @patch('app.requests.get')
    @patch('app.load_supported_ipfs_gateways')
    def test_fetch_ipfs_data_http_error(self, mock_load_gateways, mock_requests_get):
        loaded_config = load_supported_ipfs_gateways()
        mock_load_gateways.return_value = loaded_config
        mock_requests_get.side_effect = requests.exceptions.HTTPError("Error")

        result = fetch_ipfs_data('ipfs://someCID')
        self.assertIsNone(result)

    @patch('app.get_ul_fields')
    @patch('app.get_chain_info')
    @patch('app.get_token_uri')
    def test_handle_request_unsupported_https_token_uri(self, mock_get_token_uri, mock_get_chain_info, mock_get_ul_fields):
        # Mock the functions to return expected values
        mock_get_ul_fields.return_value = ('3', '3336', '51', '0xABC123', '789')
        mock_get_chain_info.return_value = (['http://example.com'], 1)
        mock_get_token_uri.return_value = 'https://tokenUri'

        # Perform the GET request to the endpoint
        response = self.client.get('/GlobalConsensus(123)/Parachain(456)/AccountKey20(0xABC123)/GeneralKey(789)')

        # Check that the response status code is 400
        self.assertEqual(response.status_code, 400)

        # Assert the response contains the expected error message
        self.assertIn(b"Invalid token URI standard.", response.data)

        # Assert the content type is application/json
        self.assertEqual(response.content_type, "application/json")

    @patch('app.get_ul_fields')
    @patch('app.get_chain_info')
    @patch('app.get_token_uri')
    def test_handle_request_unsupported_https_token_uri(self, mock_get_token_uri, mock_get_chain_info, mock_get_ul_fields):
        # Mock the functions to return expected values
        mock_get_ul_fields.return_value = ('3', '3336', '51', '0xABC123', '789')
        mock_get_chain_info.return_value = (['http://example.com'], 1)
        mock_get_token_uri.return_value = 'http://tokenUri'

        # Perform the GET request to the endpoint
        response = self.client.get('/GlobalConsensus(123)/Parachain(456)/AccountKey20(0xABC123)/GeneralKey(789)')

        # Check that the response status code is 400
        self.assertEqual(response.status_code, 400)

        # Assert the response contains the expected error message
        self.assertIn(b"Invalid token URI standard.", response.data)

        # Assert the content type is application/json
        self.assertEqual(response.content_type, "application/json")



if __name__ == '__main__':
    unittest.main()
