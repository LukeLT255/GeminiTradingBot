import datetime
import os
import sys

import config
from gemini import account, coininfo, orders
import time

sandbox = True

symbols = ["ETHUSD", "BTCUSD"]



def make_dem_trades():
    for symbol in symbols:

        currentPrice = get_current_price(symbol)
        time.sleep(1)
        resistanceLevel = get_high(symbol, lookbackAmount=30, lookbackInterval='1day', average=True)
        supportLevel = get_low(symbol, lookbackAmount=30, lookbackInterval='1day', average=True)
        availableBalances = account.account_detail.get_available_balances(sandbox)
        availableCash = get_current_cash_balance(availableBalances)
        currentCoinBalance = get_current_coins_owned(availableBalances, symbol)
        tickSize = get_tick_size(symbol)
        cashAmountToBuy = 25
        ordersToPlace = 50
        amountToBuy = round(cashAmountToBuy / currentPrice, tickSize)
        amountToSell = round(currentCoinBalance / ordersToPlace, tickSize)
        time.sleep(1)
        pastBuyTrades = get_past_buy_trades(symbol)
        time.sleep(1)
        pastSellTrades = get_past_sell_trades(symbol)
        time.sleep(1)
        pastTrades = get_past_trades(symbol)
        hundredDayAverage = get_hundred_day_average(symbol)
        EVEN_GRID = False # starts grid with even # of buys and sells; otherwise, grid is started with buys below current price and sells above

        if currentPrice < supportLevel: # Sells all current positions, and resets grid if price is below resistance level
            orders.new_order.sell_order(symbol, currentCoinBalance, currentPrice, 'immediate-or-cancel', sandbox, options=[])
            RESET_GRID = True
        elif currentPrice > resistanceLevel: #take profit if current price is higher than resistance level
            orders.new_order.sell_order(symbol, currentCoinBalance, currentPrice, 'immediate-or-cancel', sandbox, options=[])
            RESET_GRID = True
        else:
            RESET_GRID = False

        time.sleep(1)
        openSellOrders = get_open_sell_orders(symbol)

        time.sleep(1)
        openBuyOrders = get_open_buy_orders(symbol)

        if len(openSellOrders) == 0 and len(openBuyOrders) == 0 and supportLevel < currentPrice < resistanceLevel:  # sets up grid if there are no open orders
            print('Grid Start-Up')
            set_up_grid(symbol, supportLevel, resistanceLevel, currentPrice, ordersToPlace, amountToBuy, amountToSell, EVEN_GRID)

        elif RESET_GRID: # cancels all open orders and resets grid
            orders.cancel_order.cancel_all_active_orders(sandbox)
            print('Grid Reset')
            set_up_grid(symbol, supportLevel, resistanceLevel, currentPrice, ordersToPlace, amountToBuy, amountToSell, EVEN_GRID)

        else: # checks open orders and previous filled orders to place new orders on the grid
            check_and_replace(symbol, openSellOrders, openBuyOrders, pastSellTrades, pastBuyTrades, pastTrades, currentPrice, EVEN_GRID, ordersToPlace)



def get_high(symbol, lookbackAmount, lookbackInterval, average):
    candles = coininfo.public_info.get_candles(symbol, sandbox, timeInterval=lookbackInterval)
    highs = []
    timeFrame = lookbackAmount
    start = 0

    for m in range(start, timeFrame):
        highs.append(candles[m][2])

    highs.sort(reverse=True)

    if average:
        high = sum(highs[0:20]) / 20
    else:
        high = max(highs)

    # print(high)
    return round(high, 2)


def get_low(symbol, lookbackAmount, lookbackInterval, average):
    candles = coininfo.public_info.get_candles(symbol, sandbox, timeInterval=lookbackInterval)
    lows = []
    timeFrame = lookbackAmount
    start = 0

    for m in range(start, timeFrame):
        lows.append(candles[m][3])

    lows.sort()

    if average:
        low = sum(lows[0:10]) / 10
    else:
        low = min(lows)


    # print(low)
    return round(low, 2)


def get_current_price(symbol):
    prices = coininfo.public_info.get_price_feed(sandbox)
    price = 0
    for coin in prices:
        if coin['pair'] == symbol:
            price = coin['price']

    # print(price)
    return float(price)


def get_current_cash_balance(accountInfo):
    cash = 0
    for currency in accountInfo:
        if currency['currency'] == 'USD':
            cash = currency['amount']

    # print(cash)
    return float(cash)


def get_current_coins_owned(balances, symbol):
    available = 0
    for coin in balances:
        if coin['currency'] == symbol[0:3]:
            available = coin['available']

    # print(available)
    return float(available)


def get_tick_size(symbol):
    symbolDetail = coininfo.public_info.get_symbol_details(symbol, sandbox)
    tickSize = str(symbolDetail['tick_size'])

    return int(tickSize[4])


def get_open_sell_orders(symbol):
    openSellOrders = orders.order_status.get_active_orders(sandbox)
    sellOrders = []
    for order in openSellOrders:
        if order['side'] == 'sell' and order['symbol'] == symbol.lower():
            sellOrders.append(order)

    return sellOrders


def get_open_buy_orders(symbol):
    openBuyOrders = orders.order_status.get_active_orders(sandbox)
    buyOrders = []
    for order in openBuyOrders:
        if order['side'] == 'buy' and order['symbol'] == symbol.lower():
            buyOrders.append(order)

    return buyOrders


def get_past_buy_trades(symbol):
    past_trades = orders.order_status.get_past_trades(sandbox)
    buy_trades = []
    for trade in past_trades:
        if trade['symbol'] == symbol and trade['type'] == 'Buy':
            buy_trades.append(trade)
    # print('Buys: ')
    # print(buy_trades)
    return buy_trades


def get_past_sell_trades(symbol):
    past_trades = orders.order_status.get_past_trades(sandbox)
    sell_trades = []
    for trade in past_trades:
        if trade['symbol'] == symbol and trade['type'] == 'Sell':
            sell_trades.append(trade)
    # print('Sells: ')
    # print(sell_trades)
    return sell_trades

def get_hundred_day_average(symbol):
    candles = coininfo.public_info.get_candles(symbol, sandbox, timeInterval="1day")
    closes = []
    timeFrame = 100
    start = 0

    for m in range(start, timeFrame):
        closes.append(candles[m][4])

    average = sum(closes) / timeFrame

    # print(average)
    return average

def get_past_trades(symbol):
    past_trades = orders.order_status.get_past_trades(sandbox)
    trades = []
    for trade in past_trades:
        if trade['symbol'] == symbol:
            trades.append(trade)

    # print(trades)
    return trades





def set_up_grid(symbol, low, high, currentPrice, gridLevels, amountToBuy, amountToSell, EVEN_GRID):
    gridRange = high - low
    distance_between_orders = gridRange / gridLevels
    grids = []

    print('Current price: ' + f'{currentPrice}')
    print('High: ' + f'{high}')
    print('Low: ' + f'{low}')

    for i in range(gridLevels):
        grids.append(round(low + distance_between_orders * i, 2))

    if not EVEN_GRID:
        for level in grids:
            if currentPrice > level:
                time.sleep(1)
                buy_order = orders.new_order.buy_order(symbol, amountToBuy, level, 'exchange limit', sandbox)
                print(buy_order)
            else:
                time.sleep(1)
                sell_order = orders.new_order.sell_order(symbol, amountToSell, level, 'exchange limit', sandbox)
                print(sell_order)
    else:
        for i, level in enumerate(grids):
            if i < (gridLevels / 2):
                time.sleep(1)
                buy_order = orders.new_order.buy_order(symbol, amountToBuy, level, 'exchange limit', sandbox)
                print(buy_order)
            else:
                time.sleep(1)
                sell_order = orders.new_order.sell_order(symbol, amountToSell, level, 'exchange limit', sandbox)
                print(sell_order)

    print('\n')
    return


def check_and_replace(symbol, openSellOrders, openBuyOrders, pastSellTrades, pastBuyTrades, pastTrades, currentPrice, EVEN_GRID, ordersToPlace ):
    if EVEN_GRID: # check and replace for even grid
        pass
    else: #check and replace for trailing grid
        totalOpenOrders = len(openSellOrders) + len(openBuyOrders)
        totalOrdersToReplace = ordersToPlace - totalOpenOrders
        if totalOrdersToReplace == 0:
            print("Grid full")
            return
        else:
            if totalOrdersToReplace <= 1:
                print('No grid levels ready to be replaced')
            else:
                for i in range(1, totalOrdersToReplace):
                    try:
                        if currentPrice > pastTrades[i]['price']:
                            amountToBuy = pastTrades[i]['amount']
                            price = pastTrades[i]['price']
                            buy_order = orders.new_order.buy_order(symbol, amountToBuy, price, 'exchange limit', sandbox)
                            print(buy_order)
                        else:
                            amountToSell = pastTrades[i]['amount']
                            price = pastTrades[i]['price']
                            sell_order = orders.new_order.sell_order(symbol, amountToSell, price, 'exchange limit', sandbox)
                            print(sell_order)

                    except KeyError:
                        print('Key error exception')

    print('\n')
    return




