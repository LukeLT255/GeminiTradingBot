import requests, json


def get_symbols(sandbox: bool):  # returns all valid symbols
    base_url = "https://api.sandbox.gemini.com/v1" if sandbox else "https://api.gemini.com/v1"
    response = requests.get(base_url + "/symbols")
    symbols = response.json()

    return symbols


def get_symbol_details(symbol, sandbox: bool):  # returns extra detail for symbol trading pair
    base_url = "https://api.sandbox.gemini.com/v1" if sandbox else "https://api.gemini.com/v1"
    response = requests.get(base_url + f"/symbols/details/{symbol}")
    symbols = response.json()

    return symbols


def get_ticker(symbol, sandbox: bool):  # returns info about recent trading activity for symbol

    base_url = "https://api.sandbox.gemini.com/v1" if sandbox else "https://api.gemini.com/v1"
    response = requests.get(base_url + f"/pubticker/{symbol}")
    ticker_data = response.json()

    return ticker_data


def get_ticker_v2(symbol, sandbox: bool):  # returns information about recent trading activity for the provided symbol

    base_url = "https://api.sandbox.gemini.com/v2" if sandbox else "https://api.gemini.com/v2"
    response = requests.get(base_url + f"/ticker/{symbol}")
    ticker_v2_data = response.json()

    return ticker_v2_data


def get_candles(symbol, sandbox: bool, timeInterval="1hr"):  # returns time-intervaled data for the provided symbol

    base_url = "https://api.sandbox.gemini.com/v2" if sandbox else "https://api.gemini.com/v2"
    response = requests.get(base_url + f"/candles/{symbol}/{timeInterval}")
    symbol_candle_data = response.json()

    return symbol_candle_data


def get_current_order_book(symbol, sandbox: bool):  # return the current order book as two arrays (bids / asks)

    base_url = "https://api.sandbox.gemini.com/v1" if sandbox else "https://api.gemini.com/v1"
    response = requests.get(base_url + f"/book/{symbol}")
    symbol_book = response.json()

    return symbol_book


def get_trade_history(symbol, sandbox: bool):  # will return the trades that have executed since the specified timestamp

    base_url = "https://api.sandbox.gemini.com/v1" if sandbox else "https://api.gemini.com/v1"
    response = requests.get(base_url + f"/trades/{symbol}")
    symbol_trades = response.json()

    return symbol_trades


def get_current_action(symbol, sandbox: bool):  # returns auction info for symbol

    base_url = "https://api.sandbox.gemini.com/v1" if sandbox else "https://api.gemini.com/v1"
    response = requests.get(base_url + f"/auction/{symbol}")
    symbol_auction = response.json()

    return symbol_auction


def get_auction_history(symbol, sandbox: bool):  # will return the auction events, optionally including publications of indicative prices, since the specific timestamp

    base_url = "https://api.sandbox.gemini.com/v1" if sandbox else "https://api.gemini.com/v1"
    response = requests.get(base_url + f"/auction/{symbol}/history")
    symbol_auction_history = response.json()

    return symbol_auction_history


def get_price_feed(sandbox: bool):  # returns all trading pair prices and percent changes
    base_url = "https://api.sandbox.gemini.com/v1" if sandbox else "https://api.gemini.com/v1"
    response = requests.get(base_url + "/pricefeed")
    prices = response.json()

    return prices


