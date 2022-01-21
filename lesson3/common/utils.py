import json

from lesson3.common.variables import MAX_PACKAGE_LENGTH, ENCODING
from lesson3.decorators import log


@log
def get_message(client):
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError

@log
def send_message(sock, message):
    js_msg = json.dumps(message)
    encoded_msg = js_msg.encode(ENCODING)
    sock.send(encoded_msg)
