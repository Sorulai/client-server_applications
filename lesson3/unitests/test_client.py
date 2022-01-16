import sys
import unittest
from unittest.mock import patch

from lesson3.client import ChatClient
from lesson3.common.variables import TIME, ACTION, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, ERROR


class TestClient(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ChatClient()
        self.test = self.client.create_presence()
        self.request_ans = self.client.process_ans
        self.address = self.client.get_server_address
        self.err = {
            RESPONSE: 400,
            ERROR: 'Bad request'
        }
        self.ok = {
            RESPONSE: 200
        }

    def test_presense(self):
        self.test[TIME] = 1.1
        self.assertEqual(self.test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_200(self):
        self.assertEqual(self.request_ans(self.ok), '200: ok')

    def test_400(self):
        self.assertEqual(self.request_ans(self.err), '400: Bad request')

    def test_no_response(self):
        self.assertRaises(ValueError, self.request_ans, {ERROR: 'Bad request'})


if __name__ == '__main__':
    unittest.main()
