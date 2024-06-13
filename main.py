import requests
from hashlib import sha256
import hmac
import time

API_KEY = "GyQBzygsWyTJhHKZ8FHsnSKneOYycqsz91mmQBtL24dTaFhG8yj1P8iZjKqZlmMUACVtr3sXpqK9YcXnwXYKQ"
SECRET_KEY = "dnsdD63a07Or1i93ad7WeQaD7QqdywzEYD29i8crCdSFyhj23Tzf1TrrMR8XLJmqzoKJEvzHzMUTCPPj5Xfw"

API_URL = "https://open-api.bingx.com"


def demo():
    payload = {}
    # path = '/openApi/swap/v2/quote/contracts'
    # path = '/openApi/swap/v2/user/balance'
    path = '/openApi/swap/v2/trade/allOrders'
    method = "GET"
    params_dict = {"symbol": "OCEAN-USDT", 'timestamp': f'{int(time.time() * 1000)}', 'limit': '500',
                   'startTime': '1716422400000', 'endTime': '1716681600000'}
    params_str = parse_param(params_dict)
    return send_request(method, path, params_str, payload)


def get_sign(api_secret, payload):
    signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    return signature


def send_request(method, path, params, payload):
    url = f"{API_URL}{path}?{params}&signature={get_sign(SECRET_KEY, params)}"
    headers = {'X-BX-APIKEY': API_KEY}
    response = requests.request(method, url, headers=headers, data=payload)
    return response.text


def parse_param(params_map):
    sorted_keys = sorted(params_map)
    params_str = "&".join([f"{x}={params_map[x]}" for x in sorted_keys])

    if params_str != "":
        timestamp_str = "&timestamp="
    else:
        timestamp_str = "timestamp="

    return params_str + timestamp_str + str(int(time.time() * 1000))


if __name__ == '__main__':
    print("demo:", demo())
