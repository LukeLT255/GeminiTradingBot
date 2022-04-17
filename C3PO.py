import logging
import config
import time
from gemini_python_api import account, coininfo, orders
from app import db
from app import Account

logging.basicConfig(level=logging.INFO,
                    format='{asctime} {levelname:<8} {message}',
                    style='{',
                    filename='%slog' % __file__[:-2],
                    filemode='a')

sandbox = False

symbols = ["ETHUSD"]


def make_dem_trades():
    availableBalances = account.account_detail.get_available_balances(config.gemini_api_key,
                                                                      config.gemini_api_secret,
                                                                      config.gemini_sandbox_api_key,
                                                                      config.gemini_sandbox_api_secret, sandbox)
    current_value = get_current_value_of_account(availableBalances)
    print(current_value)
    accountValue = Account(value=current_value)
    db.session.add(accountValue)
    db.session.commit()

    for symbol in symbols:
        time.sleep(1)
        currentPrice = get_current_price(symbol)
        time.sleep(1)
        lookBackAmount = 30
        lookBackInterval = '1day'
        resistanceLevel = get_high(symbol, lookBackAmount=lookBackAmount, lookBackInterval=lookBackInterval,
                                   average=True)
        supportLevel = get_low(symbol, lookBackAmount=lookBackAmount, lookBackInterval=lookBackInterval, average=True)
        availableBalances = account.account_detail.get_available_balances(config.gemini_api_key,
                                                                          config.gemini_api_secret,
                                                                          config.gemini_sandbox_api_key,
                                                                          config.gemini_sandbox_api_secret, sandbox)
        availableCash = get_current_cash_balance(availableBalances)
        currentCoinBalance = get_current_coins_owned(availableBalances, symbol)
        tickSize = get_tick_size(symbol)
        cashAmountToBuy = 50
        ordersToPlace = 10
        amountToBuy = round(cashAmountToBuy / currentPrice, tickSize)
        amountToSell = amountToBuy

        time.sleep(1)
        pastTrades = get_past_trades(symbol)

        EVEN_GRID = False  # starts grid with even # of buys and sells; otherwise, grid is started with buys below current price and sells above

        if currentPrice < supportLevel:  # If price below s level, it waits until price rises and does nothing
            RESET_GRID = True
        elif currentPrice > resistanceLevel:  # take profit if current price is higher than resistance level
            time.sleep(1)
            orders.new_order.sell_order(symbol, currentCoinBalance, round(currentPrice * 0.95, 2), 'exchange limit',
                                        sandbox, options='immediate-or-cancel')
            RESET_GRID = True
        else:
            RESET_GRID = False

        time.sleep(1)
        openSellOrders = get_open_sell_orders(symbol)

        time.sleep(1)
        openBuyOrders = get_open_buy_orders(symbol)

        if len(openSellOrders) == 0 and len(
                openBuyOrders) == 0 and supportLevel < currentPrice < resistanceLevel:  # sets up grid if there are no open orders
            logging.info('Grid Start-Up')
            set_up_grid(symbol, supportLevel, resistanceLevel, currentPrice, ordersToPlace, amountToBuy, amountToSell,
                        EVEN_GRID, tickSize)

        elif RESET_GRID and supportLevel < currentPrice < resistanceLevel:  # cancels all open orders and resets grid
            time.sleep(1)
            orderCancel = orders.cancel_order.cancel_all_active_orders(sandbox)
            logging.info(orderCancel)
            logging.info('Grid Reset')
            set_up_grid(symbol, supportLevel, resistanceLevel, currentPrice, ordersToPlace, amountToBuy, amountToSell,
                        EVEN_GRID, tickSize)

        elif len(openBuyOrders) + len(
                openSellOrders) > 0 and supportLevel < currentPrice < resistanceLevel:  # checks open orders and previous filled orders to place new orders on the grid
            check_and_replace(symbol, openSellOrders, openBuyOrders, pastTrades, currentPrice, EVEN_GRID, ordersToPlace)

        else:  # cancels open orders and does nothing until current price is back between s and r
            time.sleep(1)
            orderCancel = orders.cancel_order.cancel_all_active_orders(sandbox)
            logging.info(orderCancel)
            return


def get_high(symbol, lookBackAmount, lookBackInterval, average):
    candles = coininfo.public_info.get_candles(symbol, sandbox, timeInterval=lookBackInterval)
    highs = []
    timeFrame = lookBackAmount
    start = 0

    for m in range(start, timeFrame):
        highs.append(candles[m][2])

    highs.sort(reverse=True)

    if average:
        high = sum(highs[0:10]) / 10
    else:
        high = max(highs)

    # print(high)
    return round(high, 2)


def get_low(symbol, lookBackAmount, lookBackInterval, average):
    candles = coininfo.public_info.get_candles(symbol, sandbox, timeInterval=lookBackInterval)
    lows = []
    timeFrame = lookBackAmount
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
    time.sleep(1)
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

def get_current_value_of_account(balances):
    total = 0
    print(balances)
    for balance in balances:
        if balance['currency'] == 'USD':
            total += round(float(balance['amount']), 2)
        else:
            currentPrice = get_current_price(balance['currency'] + 'USD')
            total += round(float(balance['amount']), 2) * currentPrice
    return total



def set_up_grid(symbol, low, high, currentPrice, gridLevels, amountToBuy, amountToSell, EVEN_GRID, tickSize):
    gridRange = high - low
    distance_between_orders = gridRange / gridLevels
    grids = []
    totalSellOrders = 0

    logging.info('Current price: ' + f'{currentPrice}')
    logging.info('High: ' + f'{high}')
    logging.info('Low: ' + f'{low}')

    for i in range(gridLevels):  # creates a list of grid levels
        level = round(low + distance_between_orders * i, 2)
        grids.append(level)
        if level > currentPrice:  # keeps track of how many sell orders initially placed
            totalSellOrders += 1

    initialAmountToBuy = round(totalSellOrders * amountToBuy, tickSize)

    time.sleep(1)
    startUpBuy = orders.new_order.buy_order(symbol, initialAmountToBuy, round(currentPrice * 1.05, 2), 'exchange limit',
                                            sandbox, options='immediate-or-cancel')
    logging.info('Start Up Buy: ')
    logging.info(startUpBuy)

    if not EVEN_GRID:
        for level in grids:
            if currentPrice > level:
                time.sleep(1)
                buy_order = orders.new_order.buy_order(symbol, amountToBuy, level, 'exchange limit', sandbox)
                logging.info(buy_order)
            else:
                time.sleep(1)
                sell_order = orders.new_order.sell_order(symbol, amountToSell, level, 'exchange limit', sandbox)
                logging.info(sell_order)
    else:
        for i, level in enumerate(grids):
            if i < (gridLevels / 2):
                time.sleep(1)
                buy_order = orders.new_order.buy_order(symbol, amountToBuy, level, 'exchange limit', sandbox)
                logging.info(buy_order)
            else:
                time.sleep(1)
                sell_order = orders.new_order.sell_order(symbol, amountToSell, level, 'exchange limit', sandbox)
                logging.info(sell_order)

    logging.info('\n')
    return


def check_and_replace(symbol, openSellOrders, openBuyOrders, pastTrades, currentPrice, EVEN_GRID, ordersToPlace):
    if EVEN_GRID:  # check and replace for even grid
        pass

    else:  # check and replace for trailing grid
        totalOpenOrders = len(openSellOrders) + len(openBuyOrders)

        # print('All open buy orders: ')
        # for order in openBuyOrders:
        #     print(order)
        #     print('\n')

        # print('All open sell orders: ')
        # for order in openSellOrders:
        #     print(order)
        #     print('\n')

        totalOrdersToReplace = ordersToPlace - totalOpenOrders
        logging.info('Past trades: ')
        for i in range(totalOrdersToReplace):
            logging.info(pastTrades[i])
            logging.info('\n')

        if totalOrdersToReplace == 0:
            logging.info("Grid full")
            return
        elif totalOrdersToReplace == 1:
            logging.info('No grid levels ready to be replaced')
        else:
            for i in range(1, totalOrdersToReplace):
                try:
                    if currentPrice > float(pastTrades[i]['price']):
                        amountToBuy = float(pastTrades[i]['amount'])
                        price = float(pastTrades[i]['price'])
                        time.sleep(1)
                        buy_order = orders.new_order.buy_order(symbol, amountToBuy, price, 'exchange limit', sandbox)
                        logging.info(f'Buy order placed: {buy_order}')
                    else:
                        amountToSell = float(pastTrades[i]['amount'])
                        price = float(pastTrades[i]['price'])
                        time.sleep(1)
                        sell_order = orders.new_order.sell_order(symbol, amountToSell, price, 'exchange limit', sandbox)
                        logging.info(f'Sell order placed: {sell_order}')

                except KeyError:
                    logging.error('Key error exception')

    logging.info('\n')
    return
