import os
from django.http import response
import requests

# The API doesn't provide the full coin name in its response, so I created a dictionary where the full names can be accessed and passed to template.
coin_name_dict = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "XRP": "Ripple", "ADA": "Cardano", 
    "LTC": "Litecoin", "BCH": "Bitcoin Cash", "DOGE": "Dogecoin", "XLM": "Stellar",
    "BNB": "Binance Coin", "SXP": "Swipe", "LINK": "ChainLink", "DOT": "Polkadot",
    "YFI": "Yearn.finance", "GRT": "The Graph", "EOS": "Eos", "EGLD": "Elrond",
    "AVAX": "Avalanche", "UNI": "Uniswap", "CHZ": "Chiliz", "ENJ": "Enjin Coin",
    "MATIC": "Polygon", "LUNA": "Terra", "THETA": "Theta", "BTT": "BlockTrade Token",
    "WIN": "WinToken", "VET": "VeChain", "WRX": "WazirX", "TRX": "TRON", "SHIB": "Shiba Inu",
    "ETC": "Ethereum Classic", "SOL": "Solana", "ICP": "Internet Computer/Dfinity", "RUNE": "THORChain",
    "LAZIO": "Lazio Fan Token"
    }

# Retrieve API Keys from environment variables
IEX_key = os.environ.get('IEX_API_Key')
nomics_key = os.environ.get('nomics_API_key')

def get_coin_info(coin_id):
    """Takes a coin ID and returns a dictionary with price and other info for that coin (coin ID must be recognised by IEX API)"""

    response = requests.get(f"https://cloud.iexapis.com/stable/crypto/{coin_id}EUR/quote?token={IEX_key}")
    info = response.json()

    return(info)


def price_chart_data(coin_id):
    """Takes a coin ID and returns historic price data from Nomics API (timestamps and prices) from a specified date up to the present date. Used to provide data for chart.JS"""

    response = requests.get(f"https://api.nomics.com/v1/currencies/sparkline?key={nomics_key}&ids={coin_id}&start=2016-11-02T00%3A00%3A00Z&convert=EUR")
    info = response.json()

    # Timestamps must be cleaned before being passed to chart.js
    timestamp_list = info[0]['timestamps']
    cleaned_timestamp_list = [item.strip("T00:00:00Z") for item in timestamp_list]

    # Prices must be changed from strings to floats before being passed to chart.js
    price_list = info[0]['prices']
    cleaned_price_list = [float(item) for item in price_list]

    return(cleaned_price_list, cleaned_timestamp_list)


def portfolio_coin_prices(coin_ids):
    """Takes a string of comma separated coin ID's and returns data for each coin from Nomics API. This function is for use on the dashboard page
        where we need to get price information for all the User's holdings at once"""

    response = requests.get(f"https://api.nomics.com/v1/currencies/ticker?key={nomics_key}&ids={coin_ids}&interval=1d&convert=EUR")
    info = response.json()

    return(info)





                                ### SHELVED FOR NOW - MIGHT USE LATER ###
def comprehensive_coin_info(coin_id):
    """Takes a coin ID and returns a dictionary with comprehensive data for the coin (market cap, circulating supply etc)"""

    response = requests.get(f"https://api.nomics.com/v1/currencies/ticker?key={nomics_key}&ids={coin_id}&interval=1d&convert=EUR")
    info = response.json()

    info_dict = {
        'market_cap': info[0]['market_cap'],
        'circulating_supply': info[0]['circulating_supply'],
        'max_supply': info[0]['max_supply'],
        'rank': info[0]['rank'],
        'high': info[0]['high'],
        'high_timestamp': info[0]['high_timestamp']
        }

    return(info_dict)

