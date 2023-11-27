import unittest
from app import *
from unittest.mock import patch
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
        mock_get_ul_fields.return_value = ('123', '456', '0xABC123', '789')
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

    def test_load_config(self):
        config = load_config()
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
        path = 'GlobalConsensus(123)/Parachain(456)/AccountKey20(0xABC123)/GeneralKey(789)'
        expected = ('123', '456', '0xABC123', '789')
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

    @patch('app.load_config')
    def test_get_chain_info(self, mock_load_config):
        mock_load_config.return_value = {
            'GlobalConsensusMappings': {
                '123': {
                    'Parachains': {
                        '456': {
                            'rpc': 'http://example.com',
                            'chainId': 1
                        }
                    }
                }
            }
        }

        rpc_url, chain_id = get_chain_info('123', '456')
        self.assertEqual(rpc_url, 'http://example.com')
        self.assertEqual(chain_id, 1)

        rpc_url, chain_id = get_chain_info('999', '888')
        self.assertIsNone(rpc_url)
        self.assertIsNone(chain_id)

if __name__ == '__main__':
    unittest.main()
