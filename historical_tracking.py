from utils import read_json_file_as_dict
import pandas as pd

dict_coin = dict(ETHUSDT='Ethereum', BTCUSDT='Bitcoin', RVNUSDT='Ravencoin')


def get_crypto(message, ):
    for coin in dict_coin:
        if coin in message['text']:
            return dict_coin[coin]


def get_order(message):
    return 'COMPRA' if 'COMPRA' in message['text'] else 'VENDA'


def get_price(message):
    i = 0
    for j, ch in enumerate(message['text']):
        if ch == "$":
            i = j
    return message['text'][127:i]


if __name__ == '__main__':
    not_to_do_message = "Nenhuma oportunidade para a moeda"
    telegram_json_messages = read_json_file_as_dict("ChatExport_2022-12-22/result.json")["messages"]
    historical_df = pd.DataFrame(columns=['DATA', 'MOEDA', 'ORDEM', 'VALOR'])
    for message in telegram_json_messages:
        if (
                not_to_do_message in message["text"] or
                len(message["text_entities"]) == 0 or
                "finalizada" in message["text"]
        ):
            continue
        crypto = get_crypto(message)
        order = get_order(message)
        price = get_price(message)
        new_row = {'DATA': message['date'], 'MOEDA': crypto, 'ORDEM': order, 'VALOR': price}
        historical_df = historical_df.append(new_row, ignore_index=True)

    historical_df.to_excel(r'historical_track.xlsx', index=False)
