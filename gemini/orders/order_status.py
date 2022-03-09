import requests
import json
import base64
import hmac
import hashlib
import config
import time
import datetime



def order_status(orderID, sandbox: bool): #cancels a current order
    t = datetime.datetime.now()
    nonce = str(int(time.mktime(t.timetuple()) * 1000))

    base_url = "https://api.sandbox.gemini.com" if sandbox else "https://api.gemini.com"
    endpoint = "/v1/order/status"
    url = base_url + endpoint

    gemini_api_key = config.gemini_sandbox_api_key if sandbox else config.gemini_api_key
    gemini_api_secret = config.gemini_sandbox_api_secret if sandbox else config.gemini_api_secret


    payload_nonce = nonce

    payload = {
        "request": "/v1/order/status",
        "nonce": payload_nonce,
        "order_id": orderID
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

    status = response.json()

    return status


def get_past_trades(sandbox: bool):
    t = datetime.datetime.now()
    nonce = str(int(time.mktime(t.timetuple()) * 1000))

    base_url = "https://api.sandbox.gemini.com" if sandbox else "https://api.gemini.com"
    endpoint = "/v1/mytrades"
    url = base_url + endpoint

    gemini_api_key = config.gemini_sandbox_api_key if sandbox else config.gemini_api_key
    gemini_api_secret = config.gemini_sandbox_api_secret if sandbox else config.gemini_api_secret

    payload_nonce = nonce

    payload = {
        "request": "/v1/mytrades",
        "nonce": payload_nonce,
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

    past_trades = response.json()

    return past_trades

def get_active_orders(sandbox: bool):
    t = datetime.datetime.now()
    nonce = str(int(time.mktime(t.timetuple()) * 1000))

    base_url = "https://api.sandbox.gemini.com" if sandbox else "https://api.gemini.com"
    endpoint = "/v1/orders"
    url = base_url + endpoint

    gemini_api_key = config.gemini_sandbox_api_key if sandbox else config.gemini_api_key
    gemini_api_secret = config.gemini_sandbox_api_secret if sandbox else config.gemini_api_secret

    payload_nonce = nonce

    payload = {
        "request": "/v1/orders",
        "nonce": payload_nonce
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
    active_orders = response.json()

    return active_orders

