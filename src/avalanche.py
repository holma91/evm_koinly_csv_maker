from operator import itemgetter
import json
import csv
import datetime


import requests
import pandas as pd

from env_vars import APIKEY_SNOWTRACE, ACCOUNT1


AVAX_DECIMALS = 18

#  tte with tx
#  tte without tx
#  tte with tte
#  tx without tte


def main(address):
    tte_with_tx = []
    tte2_with_tx = []  # token swap
    tte_without_tx = []
    tx_without_tte = []

    objs = []
    transactions = requests.get(
        f'https://api.snowtrace.io/api?module=account&action=txlist&address={address}&startblock=1&endblock=99999999&sort=asc&apikey={APIKEY_SNOWTRACE}').json()['result']

    erc20_transfers = requests.get(
        f'https://api.snowtrace.io/api?module=account&action=tokentx&address={address}&sort=asc&apikey={APIKEY_SNOWTRACE}').json()['result']

    for tte in erc20_transfers:

        if tte['to'] == address:
            searched_tx = {}
            for tx in transactions:
                if tx['hash'] == tte['hash']:
                    searched_tx = tx
                    break

            searched_tte = {}

            for tte2 in erc20_transfers:
                if tte2['hash'] == tte['hash'] and tte2['from'] != tte['from']:
                    # we found a erc20 swap
                    searched_tte = tte2

            if searched_tx == {}:
                # TTE WITHOUT TX
                # bridge, airdrop, joe from other wallet, insert these manually
                # print(json.dumps(tte, indent=2))
                tte_without_tx.append(tte)
                continue

            if searched_tte != {}:
                # TTE WITH ANOTHER TTE AND TX
                tte2_with_tx.append()

            # SINGLE TTE WITH TX
            fee = int(tx['gasPrice']) * int(tx['gasUsed'])
            correct_fee = to_correct_unit(fee, AVAX_DECIMALS)

            correct_amount_tte = to_correct_unit(int(tte['value']), int(tte['tokenDecimal']))
            correct_amount_tx = to_correct_unit(int(searched_tx['value']), AVAX_DECIMALS)

            obj = {
                'type': 'tx out, tte in',
                'received amount': correct_amount_tte,
                'received currency': tte['tokenSymbol'],
                'sent amount': correct_amount_tx,
                'sent currency': 'AVAX',
                'fee amount': correct_fee,
                'fee currency': 'AVAX',
                'hash': tx['hash'],
                'timeStamp': tx['timeStamp'],
                'tokenDecimal': tte['tokenDecimal'],
            }
            tte_with_tx.append(obj)
        elif tte['from'] == address:
            pass

    #print(json.dumps(objs, indent=2))
    # sorted_all_txs = sorted(transactions + erc20_transfers, key=itemgetter('timeStamp'))

    # # print(json.dumps(sorted_all_txs, indent=2))
    # # headers taken from koinly specs
    headers = ['Date', 'Sent Amount', 'Sent Currency', 'Received Amount',	'Received Currency', 'Fee Amount',
               'Fee Currency',	'Net Worth Amount',	'Net Worth Currency',	'Label',	'Description',	'TxHash']

    f = open('txs2.csv', 'w')
    writer = csv.writer(f)
    writer.writerow(headers)
    for obj in objs:
        if obj['type'] == 'tx out, tte in':
            row = []
            row.append(str(datetime.datetime.utcfromtimestamp(int(obj['timeStamp']))) + ' UTC')
            row.append(obj['sent amount'][:14])  # Sent Amount
            row.append('AVAX')  # Sent Currency
            row.append(obj['received amount'][:14])  # Received Amount
            row.append(obj['received currency'])  # Received Currency
            row.append(obj['fee amount'][:14])  # Fee Amount
            row.append('AVAX')  # Fee Currency
            row.append('')  # Net Worth Amount
            row.append('')  # Net Worth Currency
            row.append('')  # Label
            row.append('')  # Description
            row.append(obj['hash'])  # TxHash

        writer.writerow(row)

    f.close()

    # for tx in sorted_all_txs:
    #     if tx['value'] == '0':
    #         continue
    #     if 'tokenName' in tx.keys():
    #         if tx['from'] == address:
    #             row = create_row(tx, 'TTE_FROM_ME')
    #         else:
    #             row = create_row(tx, 'TTE_TO_ME')

    #         writer.writerow(row)
    #     else:
    #         if tx['from'] == address:
    #             row = create_row(tx, 'TX_FROM_ME')
    #         else:
    #             row = create_row(tx, 'TX_TO_ME')

    #         writer.writerow(row)

    # f.close()


def create_row(tx, tx_type):
    if tx_type == 'TTE_FROM_ME':
        row = []
        row.append(str(datetime.datetime.utcfromtimestamp(int(tx['timeStamp']))) + ' UTC')
        correct_amount = to_correct_unit(int(tx['value']), int(tx['tokenDecimal']))
        row.append(correct_amount[:14])  # Sent Amount
        if tx['tokenSymbol'] in mapping.keys():
            tx['tokenSymbol'] = mapping[tx['tokenSymbol']]
        row.append(tx['tokenSymbol'])  # Sent Currency
        row.append('')  # Received Amount
        row.append('')  # Received Currency
        fee = int(tx['gasPrice']) * int(tx['gasUsed'])
        correct_fee = to_correct_unit(fee, 18)
        row.append(str(correct_fee)[:14])  # Fee Amount
        row.append('AVAX')  # Fee Currency
        row.append('')  # Net Worth Amount
        row.append('')  # Net Worth Currency
        row.append('')  # Label
        row.append('')  # Description
        row.append(tx['hash'])  # TxHash
        return row
    elif tx_type == 'TTE_TO_ME':
        row = []
        row.append(str(datetime.datetime.utcfromtimestamp(int(tx['timeStamp']))) + ' UTC')
        row.append('')  # Sent Amount
        row.append('')  # Sent Currency
        correct_amount = to_correct_unit(int(tx['value']), int(tx['tokenDecimal']))
        row.append(correct_amount[:14])  # Received Amount
        if tx['tokenSymbol'] in mapping.keys():
            tx['tokenSymbol'] = mapping[tx['tokenSymbol']]
        row.append(tx['tokenSymbol'])  # Received Currency
        row.append('')  # Fee Amount
        row.append('AVAX')  # Fee Currency
        row.append('')  # Net Worth Amount
        row.append('')  # Net Worth Currency
        row.append('')  # Label
        row.append('')  # Description
        row.append(tx['hash'])  # TxHash
        return row
    elif tx_type == 'TX_FROM_ME':
        row = []
        row.append(str(datetime.datetime.utcfromtimestamp(int(tx['timeStamp']))) + ' UTC')
        correct_amount = to_correct_unit(int(tx['value']), 18)  # 18 because avax
        row.append(correct_amount[:14])  # Sent Amount
        row.append('AVAX')  # Sent Currency
        row.append('')  # Received Amount
        row.append('')  # Received Currency
        fee = int(tx['gasPrice']) * int(tx['gasUsed'])
        correct_fee = to_correct_unit(fee, 18)  # 18 because avax
        row.append(str(correct_fee)[:14])  # Fee Amount
        row.append('AVAX')  # Fee Currency
        row.append('')  # Net Worth Amount
        row.append('')  # Net Worth Currency
        row.append('')  # Label
        row.append('')  # Description
        row.append(tx['hash'])  # TxHash
        return row
    elif tx_type == 'TX_TO_ME':
        row = []
        row.append(str(datetime.datetime.utcfromtimestamp(int(tx['timeStamp']))) + ' UTC')
        row.append('')  # Sent Amount
        row.append('')  # Sent Currency
        correct_amount = to_correct_unit(int(tx['value']), 18)
        row.append(correct_amount[:14])  # Received Amount
        row.append('AVAX')  # Received Currency
        row.append('')  # Fee Amount
        row.append('AVAX')  # Fee Currency
        row.append('')  # Net Worth Amount
        row.append('')  # Net Worth Currency
        row.append('')  # Label
        row.append('')  # Description
        row.append(tx['hash'])  # TxHash
        return row


def to_correct_unit(value, token_decimals):
    return str(value * 10 ** -token_decimals)


mapping = {
    'xJOE': 'JOE',
    'jUSDC': 'USDC',
    'variableDebtvWAVAX': 'AVAX',
    'avWAVAX': 'AVAX',
    'USDC.e': 'USDC',
    'WETH.e': 'WETH'
}

main(ACCOUNT1)
