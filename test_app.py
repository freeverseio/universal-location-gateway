import unittest
from app import *
from unittest.mock import patch
from werkzeug.exceptions import HTTPException

class TestApp(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

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

    def test_get_ul_fields_correct(self):
        path = 'GlobalConsensus(123)/Parachain(456)/AccountKey20(0xABC123)/GeneralKey(789)'
        global_consensus, parachain, account_key, general_key = get_ul_fields(path)
        self.assertEqual(global_consensus, '123')
        self.assertEqual(parachain, '456')
        self.assertEqual(account_key, '0xABC123')
        self.assertEqual(general_key, '789')

    def test_get_ul_fields_missing_fields(self):
        path = 'GlobalConsensus(123)/AccountKey20(0xABC123)'
        global_consensus, parachain, account_key, general_key = get_ul_fields(path)
        self.assertEqual(global_consensus, '123')
        self.assertIsNone(parachain)
        self.assertEqual(account_key, '0xABC123')
        self.assertIsNone(general_key)

    def test_get_ul_fields_empty_path(self):
        path = ''
        global_consensus, parachain, account_key, general_key = get_ul_fields(path)
        self.assertIsNone(global_consensus)
        self.assertIsNone(parachain)
        self.assertIsNone(account_key)
        self.assertIsNone(general_key)

    def test_process_url_prefix(self):
        self.assertEqual(process_url_prefix('uloc://example.com'), 'example.com')
        self.assertEqual(process_url_prefix('https://uloc.io/path'), 'path')
        # Test with an invalid prefix
        with self.assertRaises(HTTPException) as context:
            process_url_prefix('invalid://example.com')
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
