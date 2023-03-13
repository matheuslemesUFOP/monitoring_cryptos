import dash
from dash import Output, Input, html, dcc
import plotly.graph_objects as go
import pandas as pd
from binance.client import Client
import colorlover as cl

# Coloque sua API Key e Secret Key da Binance aqui
api_key = 'sua_api_key'
api_secret = 'sua_secret_key'

# Cria uma instância do cliente da Binance
client = Client(api_key, api_secret)

# Define o par de moedas e o intervalo de tempo para coletar os dados
symbol = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_1DAY

# Cria o layout do dashboard
app = dash.Dash(__name__)

app.layout = html.Div(
    className="row",
    style={},
    children=[
    html.H1('Gráfico de velas do Bitcoin em tempo real',
            style={}),

        html.Div(
            id="charts",
            className="row",
            children=[
                html.Div(
                    id='rightpainel_BBCE',
                    className='graph_div',
                    children=[]
                ),
            ]

        ),

    dcc.Interval(
        id='graph-update',
        interval=1000*10
    )
])

@app.callback(
    Output('rightpainel_BBCE', 'children'),
    [Input('graph-update', 'n_intervals')]
)
def update_graph(n_intervals):
    # Coleta os dados de mercado do Bitcoin em tempo real da Binance
    klines = client.futures_klines(symbol=symbol, interval=interval)

    # Cria um dataframe Pandas com os dados coletados
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                       'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                       'taker_buy_quote_asset_volume', 'ignore'])

    # Converte os valores de string para float
    df = df.astype(float)

    # Converte o timestamp para datetime e ajusta o timezone para 'America/Sao_Paulo'
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('America/Sao_Paulo')

    # Seleciona somente as velas do último mês
    one_month_ago = pd.Timestamp.now(tz='America/Sao_Paulo') - pd.Timedelta(days=90)
    df = df[df['timestamp'] > one_month_ago]

    # Obtém o preço atual do Bitcoin usando a API da Binance
    ticker = client.futures_ticker(symbol='BTCUSDT')
    price = float(ticker['lastPrice'])

    df.loc[df.index[-1], 'close'] = price
    print(df.loc[df.index[-1], 'close'])
    # Cria o gráfico de velas usando o Plotly
    fig = go.Figure()
    fig["layout"]["uirevision"] = "The User is always right"
    fig["layout"]["margin"] = {"t": 50, "l": 50, "b": 50, "r": 25}
    fig["layout"]["autosize"] = True
    fig["layout"]["height"] = 400
    fig["layout"]["xaxis"]["rangeslider"]["visible"] = True
    fig["layout"]["xaxis"]["gridcolor"] = "#3E3F40"
    fig["layout"]["yaxis"]["showgrid"] = True
    fig["layout"]["yaxis"]["gridcolor"] = "#3E3F40"  # 3E3F40
    fig["layout"]["yaxis"]["gridwidth"] = 1

    candle_chart = go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                showlegend=False,
                decreasing_fillcolor='indianred'
                )
    fig.add_trace(candle_chart)
    # Define a posição vertical da linha como o preço atual
    line_position = price

    # Obter a cor do último candle
    last_candle_color = 'darkgreen' if df['close'].iloc[-1] >= df['open'].iloc[-1] else 'indianred'

    # gera uma paleta de 3 cores a partir da cor do candle
    bgcolor = "rgba(96, 171, 91, 0.2)" if last_candle_color == 'darkgreen' else "rgba(171, 91, 91, 0.2)"

    # Adiciona a linha vertical no gráfico de velas

    vertical_line = go.Scatter(
        x=df['timestamp'],
        y=[line_position for _ in range(len(df['timestamp']))],
        mode="lines",
        showlegend=False,
        line=go.scatter.Line(color=last_candle_color, dash='dot')
    )
    fig.add_trace(vertical_line)


    # Adicionar a anotação com a cor do texto igual à cor do último candle
    fig.add_annotation(
        x=df['timestamp'].iloc[-1],
        y=line_position,
        text=str(line_position),
        font=dict(
            family='Arial',
            size=12,
            color=last_candle_color
        ),
        showarrow=False,
        xanchor='left',
        yanchor='bottom',
        xshift=5,
        bordercolor=last_candle_color,
        borderwidth=1,
        bgcolor=bgcolor,
        align='left',
        borderpad=4
    )

    # Configura o layout do gráfico
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        yaxis=dict(title='Preço (USDT)', side='right'))

    fig.update_layout(
        xaxis_gridcolor='#5d5d6b',
        yaxis_gridcolor='#5d5d6b',
        plot_bgcolor='#15142b',  # Define a cor de fundo do plot
        paper_bgcolor='#15142b',  # Define a cor de fundo do papel
        font_color='#ffffff'  # Define a cor da fonte
    )


    return dcc.Graph(
            id='graph_BBCE',
            className="chart-graph",
            config={"scrollZoom": True},
            figure=fig,
        # animate=True,
        #animation_options={ "frame": { "redraw": True, }, "transition": { "duration": 1, "ease": 'cubic-in-out', },}
    )

if __name__ == '__main__':
    app.run_server(port = 8069, host='0.0.0.0')
