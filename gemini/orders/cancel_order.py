import requests
import json
import base64
import hmac
import hashlib
import config
import time
import datetime



def cancel_order(orderID, sandbox: bool): #cancels a current order
    t = datetime.datetime.now()
    nonce = str(int(time.mktime(t.timetuple()) * 1000))

    base_url = "https://api.sandbox.gemini.com" if sandbox else "https://api.gemini.com"
    endpoint = "/v1/order/cancel"
    url = base_url + endpoint

    gemini_api_key = config.gemini_sandbox_api_key if sandbox else config.gemini_api_key
    gemini_api_secret = config.gemini_sandbox_api_secret if sandbox else config.gemini_api_secret


    payload_nonce = nonce

    payload = {
        "request": "/v1/order/cancel",
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

    cancel = response.json()

    return cancel

def cancel_all_active_orders(sandbox: bool): #cancels a current order
    t = datetime.datetime.now()
    nonce = str(int(time.mktime(t.timetuple()) * 1000))

    base_url = "https://api.sandbox.gemini.com" if sandbox else "https://api.gemini.com"
    endpoint = "/v1/order/cancel/all"
    url = base_url + endpoint

    gemini_api_key = config.gemini_sandbox_api_key if sandbox else config.gemini_api_key
    gemini_api_secret = config.gemini_sandbox_api_secret if sandbox else config.gemini_api_secret


    payload_nonce = nonce

    payload = {
        "request": "/v1/order/cancel/all",
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

    cancel_all = response.json()

    return cancel_all