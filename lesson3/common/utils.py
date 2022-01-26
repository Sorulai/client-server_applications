import json

from lesson3.common.variables import MAX_PACKAGE_LENGTH, ENCODING
from lesson3.decorators import log
from lesson3.errors import IncorrectDataReceivedError, NonDictInputError


@log
def get_message(client):
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise IncorrectDataReceivedError
    raise IncorrectDataReceivedError


@log
def send_message(sock, message):
    if not isinstance(message, dict):
        raise NonDictInputError
    js_msg = json.dumps(message)
    encoded_msg = js_msg.encode(ENCODING)
    sock.send(encoded_msg)
