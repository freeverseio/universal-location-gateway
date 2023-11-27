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
