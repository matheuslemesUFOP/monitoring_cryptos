from typing import List
import telegram
from binance.spot import Spot as Client
import pandas as pd
import plotly.graph_objects as go
import os


class CryptoTracking:
    def __init__(self, chat_id: str, coin_to_monitoring: List[str]):
        self.__TOKEN = 'BINANCE TOKEN'
        self.__CHAT_ID = chat_id
        self.__IMAGE_PATH = "images/fig1.jpeg"
        self.__coin_to_monitoring = coin_to_monitoring
        self.bot = telegram.Bot(token=self.__TOKEN)
        self.base_url = 'https://api.binance.com'
        self.base_url_test = 'https://testnet.binance.vision'
        self.chart_limit = 70
        self.crypto_tracking()

    @staticmethod
    def get_sma(prices, rate):
        return prices.rolling(rate).mean()

    def get_bollinger_bands(self, prices, rate=5):
        sma = self.get_sma(prices, rate)
        std = prices.rolling(rate).std()
        bollinger_up = sma + std * 2  # Calculate top band
        bollinger_down = sma - std * 2  # Calculate bottom band
        return bollinger_up, bollinger_down

    def send_message_in_telegram(self, message: str, send_image: bool):
        self.bot.send_message(chat_id=self.__CHAT_ID, text=message)
        if send_image:
            if not os.path.exists("images"):
                os.mkdir("images")
            self.bot.send_photo(chat_id=self.__CHAT_ID, photo=open(self.__IMAGE_PATH, 'rb'))
            os.remove(self.__IMAGE_PATH)

    def crypto_tracking(self):
        for coin in self.__coin_to_monitoring:
            historical_prices_df = self.get_coin_price_history(coin)

            fig = self.make_candle_graph_figure(historical_prices_df)

            bollinger_up, bollinger_down = self.get_bollinger_bands(historical_prices_df['close'])

            self.plot_bollinger_bands_in_figure(bollinger_down, bollinger_up, fig, historical_prices_df)

            # fig.show()

            close_price = float(historical_prices_df.iloc[-1, 4])

            up_bollinger = float(list(bollinger_up)[-2])
            down_bollinger = float(list(bollinger_down)[-2])

            coin_message = f'==================== {coin} ==================== \n'
            if down_bollinger >= close_price:
                if not os.path.exists("images"):
                    os.mkdir("images")
                fig.write_image(self.__IMAGE_PATH)
                message = f'Confira a possível oportunidade de COMPRA para a moeda: {coin}' \
                          f'\nPreço Atual: {round(float(close_price), 2)}$' \
                          f'\nBollinger Superior: {round(up_bollinger, 2)}' \
                          f'\nBollinger Inferior: {round(down_bollinger, 2)}'

            elif up_bollinger <= close_price:
                if not os.path.exists("images"):
                    os.mkdir("images")
                fig.write_image(self.__IMAGE_PATH)
                message = f'Confira a possível oportunidade de VENDA para a moeda: {coin}\n' \
                          f'\nPreço Atual: {round(close_price, 2)}$' \
                          f'\nBollinger Superior: {round(up_bollinger, 2)}' \
                          f'\nBollinger Inferior: {round(down_bollinger, 2)}'

            else:
                if not os.path.exists("images"):
                    os.mkdir("images")
                message = f'Nenhuma oportunidade para a moeda: {coin}' \
                          f'\nPreço Atual: {round(close_price, 2)}$' \
                          f'\nBollinger Superior: {round(up_bollinger, 2)}' \
                          f'\nBollinger Inferior: {round(down_bollinger, 2)}'

            self.send_message_in_telegram(message=coin_message + message, send_image=True)
    @staticmethod
    def plot_bollinger_bands_in_figure(bollinger_down, bollinger_up, fig, historical_prices_df):
        trace_down = go.Scatter(x=historical_prices_df['time'],
                                y=bollinger_down,
                                showlegend=False,
                                marker_color='rgba(255, 0, 170, 1.5)')
        trace_up = go.Scatter(x=historical_prices_df['time'],
                              y=bollinger_up,
                              showlegend=False,
                              marker_color='rgba(0, 251, 255, 1.5)')
        fig.add_trace(trace_up)
        fig.add_trace(trace_down)

    @staticmethod
    def make_candle_graph_figure(historical_prices_df):
        fig = go.Figure(data=[go.Candlestick(
            showlegend=False,
            x=historical_prices_df['time'],
            open=historical_prices_df['open'],
            high=historical_prices_df['high'],
            low=historical_prices_df['low'],
            close=historical_prices_df['close']
        )])
        fig["layout"]["uirevision"] = "The User is always right"
        fig["layout"]["margin"] = {"t": 50, "l": 50, "b": 50, "r": 25}
        fig["layout"]["autosize"] = True
        fig["layout"]["height"] = 400
        fig["layout"]["xaxis"]["rangeslider"]["visible"] = False
        fig["layout"]["xaxis"]["gridcolor"] = "#3E3F40"
        fig["layout"]["yaxis"]["showgrid"] = True
        fig["layout"]["yaxis"]["gridcolor"] = "#3E3F40"  # 3E3F40
        fig["layout"]["yaxis"]["gridwidth"] = 1
        fig["layout"].update(paper_bgcolor="#21252C", plot_bgcolor="#21252C")  # 21252C
        fig.update_xaxes(tickfont=dict(color="#e7e7e7"), tickangle=-45)  # e7e7e7
        fig.update_yaxes(tickfont=dict(color="#e7e7e7"))
        return fig

    def get_coin_price_history(self, coin):
        """

        Args:
            coin: desired crypto coin

        Returns:
            dataframe with prices by day

        """
        historical_prices = Client(self.base_url).klines(symbol=coin, interval='1d', limit=self.chart_limit)
        columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                   'number_of_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore']
        historical_prices_df = pd.DataFrame(historical_prices, columns=columns)
        historical_prices_df['time'] = pd.to_datetime(historical_prices_df['time'], utc=True, unit='ms')
        historical_prices_df = historical_prices_df.iloc[:, range(5)]
        return historical_prices_df


if __name__ == '__main__':
    chat_id = 'YOUR TELEGRAM ID'
    coin_to_monitoring = ['ETHUSDT', 'RVNUSDT', 'BTCUSDT']
    CryptoTracking(chat_id, coin_to_monitoring)
