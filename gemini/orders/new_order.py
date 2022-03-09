import requests
import json
import base64
import hmac
import hashlib
import config
import time
import datetime




def buy_order(symbol, amount, price, type, sandbox: bool, options='maker-or-cancel'): #places a new buy  order
    t = datetime.datetime.now()
    nonce = str(int(time.mktime(t.timetuple()) * 1000))

    base_url = "https://api.sandbox.gemini.com" if sandbox else "https://api.gemini.com"
    endpoint = "/v1/order/new"
    url = base_url + endpoint

    gemini_api_key = config.gemini_sandbox_api_key if sandbox else config.gemini_api_key
    gemini_api_secret = config.gemini_sandbox_api_secret if sandbox else config.gemini_api_secret

    payload_nonce = nonce

    payload = {
        "request": "/v1/order/new",
        "nonce": payload_nonce,
        "symbol": f"{symbol}",
        "amount": f"{amount}",
        "price": f"{price}",
        "side": "buy",
        "type": f"{type}",
        "options": [f"{options}"]
    }

    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

    request_headers = {'Content-Type': "text/plain",
                       'Content-Length': "0",
                       'X-GEMINI-APIKEY': gemini_api_key,
                       'X-GEMINI-PAYLOAD': b64,
                       'X-GEMINI-SIGNATURE': signature,
                       'Cache-Control': "no-cache"}

    response = requests.post(url,
                             data=None,
                             headers=request_headers)

    new_order = response.json()
    return new_order


def sell_order(symbol, amount, price, type, sandbox: bool, options='maker-or-cancel'): #places a new sell order
    t = datetime.datetime.now()
    nonce = str(int(time.mktime(t.timetuple()) * 1000))

    base_url = "https://api.sandbox.gemini.com" if sandbox else "https://api.gemini.com"
    endpoint = "/v1/order/new"
    url = base_url + endpoint

    gemini_api_key = config.gemini_sandbox_api_key if sandbox else config.gemini_api_key
    gemini_api_secret = config.gemini_sandbox_api_secret if sandbox else config.gemini_api_secret

    payload_nonce = nonce

    payload = {
        "request": "/v1/order/new",
        "nonce": payload_nonce,
        "symbol": f"{symbol}",
        "amount": f"{amount}",
        "price": f"{price}",
        "side": "sell",
        "type": f"{type}",
        "options": [f"{options}"]
    }

    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

    request_headers = {'Content-Type': "text/plain",
                       'Content-Length': "0",
                       'X-GEMINI-APIKEY': gemini_api_key,
                       'X-GEMINI-PAYLOAD': b64,
                       'X-GEMINI-SIGNATURE': signature,
                       'Cache-Control': "no-cache"}

    response = requests.post(url,
                             data=None,
                             headers=request_headers)

    new_order = response.json()
    return new_order
