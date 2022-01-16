import unittest

from lesson3.common.variables import RESPONSE, ERROR, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONDEFAULT_IP_ADDRESS
from lesson3.server import ChatServer


class TestServer(unittest.TestCase):
    def setUp(self) -> None:
        self.err = {
            RESPONDEFAULT_IP_ADDRESS: 400,
            ERROR: 'Bad Request'
        }
        self.ok = {
            RESPONSE: 200
        }

        self.server = ChatServer()
        self.client_msg = self.server.process_client_message

    def test_ok(self):
        self.assertEqual(self.client_msg({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.ok)

    def test_no_action(self):
        self.assertEqual(self.client_msg({TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.err)

    def test_wrong_action(self):
        self.assertEqual(self.client_msg({ACTION: 'wrong', TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.err)

    def test_no_time(self):
        self.assertEqual({ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}},
                         {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_no_user(self):
        self.assertEqual(self.client_msg({ACTION: PRESENCE, TIME: 1.1}), self.err)

    def test_unknown_user(self):
        self.assertEqual(self.client_msg({ACTION: 'wrong', TIME: 1.1, USER: {ACCOUNT_NAME: 'anonim'}}), self.err)


if __name__ == '__main__':
    unittest.main()
