import json
import unittest

from lesson3.common.utils import send_message, get_message
from lesson3.common.variables import ENCODING, ACTION, TIME, USER, PRESENCE, ACCOUNT_NAME, RESPONSE, ERROR


class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_msg = None
        self.received_msg = None

    def send(self, msg_to_send):
        json_test_msg = json.dumps(self.test_dict)
        self.encoded_msg = json_test_msg.encode(ENCODING)
        self.received_msg = msg_to_send

    def recv(self, max_len):
        json_test_msg = json.dumps(self.test_dict)
        return json_test_msg.encode(ENCODING)


class TestUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dict_send = {
            ACTION: PRESENCE,
            TIME: 111111.111111,
            USER: {
                ACCOUNT_NAME: 'test_user'
            }
        }
        self.test_recv_ok = {RESPONSE: 200}
        self.test_recv_err = {
            RESPONSE: 400,
            ERROR: 'Bad request'
        }
        self.test_socket = TestSocket(self.test_dict_send)
        self.send_msg = send_message
        self.get_msg = get_message

    def test_send_msg(self):
        self.send_msg(self.test_socket, self.test_dict_send)
        self.assertEqual(self.test_socket.encoded_msg, self.test_socket.received_msg)

    def test_send_msg_raise(self):
        self.send_msg(self.test_socket, self.test_dict_send)
        self.assertRaises(TypeError, self.send_msg, self.test_socket, 'wrong_dictionary')

    def test_get_message_ok(self):
        self.test_socket.test_dict = self.test_recv_ok
        self.assertEqual(self.get_msg(self.test_socket), self.test_recv_ok)

    def test_get_message_err(self):
        self.test_socket.test_dict = self.test_recv_err
        self.assertEqual(self.get_msg(self.test_socket), self.test_recv_err)


if __name__ == '__main__':
    unittest.main()
