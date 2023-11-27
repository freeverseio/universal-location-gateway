import unittest
import app
from unittest.mock import patch

class TestApp(unittest.TestCase):

    def test_load_config(self):
        # Test if the configuration is loaded correctly
        config = app.load_config()
        self.assertIsNotNone(config)

    def test_extract_between_parentheses(self):
        # Test the extract_between_parentheses function
        path_segments = ['GlobalConsensus(123)', 'Parachain(456)']
        result = app.extract_between_parentheses('GlobalConsensus', path_segments)
        self.assertEqual(result, '123')

        result = app.extract_between_parentheses('Parachain', path_segments)
        self.assertEqual(result, '456')

        # Test with a non-existing keyword
        result = app.extract_between_parentheses('NonExisting', path_segments)
        self.assertIsNone(result)


    def test_get_ul_fields_correct(self):
        # Test with a valid path containing all fields
        path = 'GlobalConsensus(123)/Parachain(456)/AccountKey20(0xABC123)/GeneralKey(789)'
        global_consensus, parachain, account_key, general_key = app.get_ul_fields(path)
        self.assertEqual(global_consensus, '123')
        self.assertEqual(parachain, '456')
        self.assertEqual(account_key, '0xABC123')
        self.assertEqual(general_key, '789')

    def test_get_ul_fields_missing_fields(self):
        # Test with a path missing some fields
        path = 'GlobalConsensus(123)/AccountKey20(0xABC123)'
        global_consensus, parachain, account_key, general_key = app.get_ul_fields(path)
        self.assertEqual(global_consensus, '123')
        self.assertIsNone(parachain)
        self.assertEqual(account_key, '0xABC123')
        self.assertIsNone(general_key)

    def test_get_ul_fields_empty_path(self):
        # Test with an empty path
        path = ''
        global_consensus, parachain, account_key, general_key = app.get_ul_fields(path)
        self.assertIsNone(global_consensus)
        self.assertIsNone(parachain)
        self.assertIsNone(account_key)
        self.assertIsNone(general_key)

    def test_get_ul_fields_loose_to_permutations(self):
        # Test with a path missing some fields
        path1 = 'GlobalConsensus(123)/AccountKey20(0xABC123)'
        path2 = 'GlobalConsensus(123)/AccountKey20(0xABC123)'
        global_consensus1, _, account_key1, _ = app.get_ul_fields(path1)
        global_consensus2, _, account_key2, _ = app.get_ul_fields(path2)
        self.assertEqual(global_consensus1, '123')
        self.assertEqual(global_consensus2, '123')
        self.assertEqual(account_key1, '0xABC123')
        self.assertEqual(account_key2, '0xABC123')

    @patch('app.load_config')
    def test_get_chain_info(self, mock_load_config):
        # Mock the load_config function
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

        rpc_url, chain_id = app.get_chain_info('123', '456')
        self.assertEqual(rpc_url, 'http://example.com')
        self.assertEqual(chain_id, 1)

        # Test with non-existing global consensus or parachain
        rpc_url, chain_id = app.get_chain_info('999', '888')
        self.assertIsNone(rpc_url)
        self.assertIsNone(chain_id)

    # Additional tests for other functions like get_token_uri, determine_token_uri_standard, etc.

if __name__ == '__main__':
    unittest.main()
