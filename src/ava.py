from operator import itemgetter
import json
import csv
import datetime


import requests
import pandas as pd

from env_vars import APIKEY_SNOWTRACE, ACCOUNT1


AVAX_DECIMALS = 18


def to_correct_unit(value, token_decimals):
    return str(value * 10 ** -token_decimals)

#  tte with tx, avax swap with token
#  tte without tx, weird stuff do manually
#  tte with tte, erc20 token swap
#  tx without tte, avax tx


def get_tte_with_tx():
    pass


def is_token_swap(erc20_transfers, tte):
    for tte2 in erc20_transfers:
        if tte2['hash'] == tte['hash'] and tte2['from'] != tte['from']:
            # we found a erc20 token swap
            correct_amount_tte = to_correct_unit(int(tte['value']), int(tte['tokenDecimal']))
            correct_amount_tte2 = to_correct_unit(int(tte2['value']), int(tte2['tokenDecimal']))
            obj = {
                'type': 'tte out, tte in',
                'received amount': correct_amount_tte,
                'received currency': tte['tokenSymbol'],
                'sent amount': correct_amount_tte2,
                'sent currency': tte2['tokenSymbol'],
                'hash': tte['hash'],
                'timeStamp': tte['timeStamp'],
                'tokenDecimal1': tte['tokenDecimal'],
                'tokenDecimal2': tte2['tokenDecimal']
            }
            return obj

    return False


def is_avax_to_token(transactions, tte):
    for tx in transactions:
        if tx['hash'] == tte['hash']:
            # we have found a avax to erc20 token swap
            correct_amount_tte = to_correct_unit(int(tte['value']), int(tte['tokenDecimal']))
            correct_amount_tx = to_correct_unit(int(tx['value']), AVAX_DECIMALS)
            obj = {
                'type': 'tx out, tte in',
                'received amount': correct_amount_tte,
                'received currency': tte['tokenSymbol'],
                'sent amount': correct_amount_tx,
                'sent currency': 'AVAX',
                'hash': tx['hash'],
                'timeStamp': tx['timeStamp'],
                'tokenDecimal': tte['tokenDecimal'],
            }
            return obj

    return False


def main(address):
    tte_with_tx = []  # if tx value is 0, then it is a send to another account. otherwise avax to token swap.
    tte_with_0tx = []
    tte_with_tte = []  # token swap
    tte_without_tx = []
    tx_without_tte = []

    objs = []
    transactions = requests.get(
        f'https://api.snowtrace.io/api?module=account&action=txlist&address={address}&startblock=1&endblock=99999999&sort=asc&apikey={APIKEY_SNOWTRACE}').json()['result']

    erc20_transfers = requests.get(
        f'https://api.snowtrace.io/api?module=account&action=tokentx&address={address}&sort=asc&apikey={APIKEY_SNOWTRACE}').json()['result']

    for tte in erc20_transfers:

        if tte['to'] == address:
            res = is_token_swap(erc20_transfers, tte)
            if res != False:
                tte_with_tte.append(res)
                continue

            res = is_avax_to_token(transactions, tte)
            if res != False:
                # print(float(res['sent amount']) == 0.0)
                if float(res['sent amount']) == 0.0:
                    tte_with_0tx.append(res)
                else:
                    tte_with_tx.append(res)

    print(json.dumps(tte_with_0tx, indent=2))

    # sorted_all_txs = sorted(transactions + erc20_transfers, key=itemgetter('timeStamp'))

    # # print(json.dumps(sorted_all_txs, indent=2))
    # # headers taken from koinly specs
    # headers = ['Date', 'Sent Amount', 'Sent Currency', 'Received Amount',	'Received Currency', 'Fee Amount',
    #            'Fee Currency',	'Net Worth Amount',	'Net Worth Currency',	'Label',	'Description',	'TxHash']

    # f = open('txs2.csv', 'w')
    # writer = csv.writer(f)
    # writer.writerow(headers)


main(ACCOUNT1)
