import ccxt



# Initialize exchange (example: Binance)
exchange = ccxt.binance()

# Load available markets
exchange.load_markets()

# Fetch real-time price for BTC/USDT
btc_usdt_ticker = exchange.fetch_ticker('BTC/USDT')
btc_usdt_price = btc_usdt_ticker['last']

# Fetch real-time price for BTC/ETH
btc_eth_ticker = exchange.fetch_ticker('XRP/USDT')
btc_eth_price = btc_eth_ticker['last']

# Print results
print(f"BTC/USDT price: {btc_usdt_price}")
print(f"BTC/ETH price: {btc_eth_price}")
