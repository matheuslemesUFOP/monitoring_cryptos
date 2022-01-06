import telegram
from binance.spot import Spot as Client
import pandas as pd
import plotly.graph_objects as go
import telegram_send
import os


def get_sma(prices, rate):
    return prices.rolling(rate).mean()


def get_bollinger_bands(prices, rate=20):
    sma = get_sma(prices, rate)
    std = prices.rolling(rate).std()
    bollinger_up = sma + std * 2  # Calculate top band
    bollinger_down = sma - std * 2  # Calculate bottom band
    return bollinger_up, bollinger_down


def send_message_in_telegram(message):
    telegram_send.send(messages=[message])
    telegram_send.send_photo


TOKEN = '5076624416:AAF_W7R4Ag_PgE73oUTfmP-6CqynL9fnaDo'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'
CHAT_ID = '718286932'

bot = telegram.Bot(token=TOKEN)

base_url = 'https://api.binance.com'

base_url_test = 'https://testnet.binance.vision'

spot_client = Client(base_url)

historical_prices = spot_client.klines(symbol='ETHUSDT', interval='1d', limit=200)
columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades',
           'taker_buy_base', 'taker_buy_quote', 'ignore']
historical_prices_df = pd.DataFrame(historical_prices, columns=columns)
historical_prices_df['time'] = pd.to_datetime(historical_prices_df['time'], utc=True, unit='ms')
historical_prices_df = historical_prices_df.iloc[:, range(5)]

fig = go.Figure(data=[go.Candlestick(
    x=historical_prices_df['time'],
    open=historical_prices_df['open'],
    high=historical_prices_df['high'],
    low=historical_prices_df['low'],
    close=historical_prices_df['close']
)])

bollinger_up, bollinger_down = get_bollinger_bands(historical_prices_df['close'])
trace_down = go.Scatter(
    x=historical_prices_df['time'],
    y=bollinger_down,
    marker_color='rgba(255, 0, 170, 1.5)'
)
trace_up = go.Scatter(
    x=historical_prices_df['time'],
    y=bollinger_up,
    marker_color='rgba(0, 251, 255, 1.5)'
)
fig.add_trace(trace_up)
fig.add_trace(trace_down)

fig.show()

open_today = historical_prices_df.iloc[-1, 1]
high_today = historical_prices_df.iloc[-1, 2]
low_today = historical_prices_df.iloc[-1, 3]
close_today = historical_prices_df.iloc[-1, 4]

higher = max(open_today, high_today, low_today, close_today)
lower = min(open_today, high_today, low_today, close_today)

if float(list(bollinger_up)[-1]) * 0.9 <= float(higher):
    print('VENDE')

if float(list(bollinger_down)[-1]) <= float(lower) * 1.1:
    print('COMPRA')
if not os.path.exists("images"):
    os.mkdir("images")
fig.write_image("images/fig1.jpeg")
bot.send_photo(chat_id=CHAT_ID, photo=open("images/fig1.jpeg", 'rb'))
bot.send_message(chat_id=CHAT_ID, text="From Telegram Bot")
os.remove("images/fig1.jpeg")
