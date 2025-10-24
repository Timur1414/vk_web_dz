import base64
import hmac
import json
import time
from vk_dz import settings


def generate_centrifugo_token(user_id, exp=None):
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
