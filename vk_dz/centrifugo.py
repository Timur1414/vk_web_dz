import base64
import hmac
import json
import time
from vk_dz import settings


def generate_centrifugo_token(user_id, exp=None):
    """
    This function generates a Centrifugo token based on the given user_id and
    expiration time in seconds. If no expiration time is given, it defaults
    to 24 hours from the current time.

    The token is a JSON Web Token (JWT) with the following format:
    header.payload.signature

    The header is a JSON object containing the algorithm and type of the
    token. The payload is a JSON object containing the user_id and expiration
    time. The signature is a base64 encoded SHA256 hash of the message
    (header.payload) with the Centrifugo secret key.

    Args:
        user_id (int): The user_id to generate a token for.
        exp (int, optional): The expiration time in seconds. Defaults to None.

    Returns:
        str: The Centrifugo token.
    """
    if exp is None:
        exp = int(time.time()) + 24 * 3600
    header = {
        'alg': 'HS256',
        'typ': 'JWT'
    }
    payload = {
        'sub': str(user_id),
        'exp': exp
    }
    header_encoded = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).decode().rstrip('=')
    payload_encoded = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).decode().rstrip('=')

    message = f'{header_encoded}.{payload_encoded}'
    signature = hmac.new(
        settings.CENTRIFUGO_SECRET.encode(),
        message.encode(),
        digestmod='sha256'
    ).digest()
    signature_encoded = base64.urlsafe_b64encode(
        signature
    ).decode().rstrip('=')
    return f'{message}.{signature_encoded}'
