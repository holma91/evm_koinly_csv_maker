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


def get_avax_to_erc20():
    pass


def is_erc20_to_erc20(erc20_transfers, tte):
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


def is_avax_to_erc20(transactions, tte):
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


def is_erc20_to_avax(transactions, tte):
    for tx in transactions:
        if tx['hash'] == tte['hash']:
            # we have found a erc20 to avax token swap
            correct_amount_tte = to_correct_unit(int(tte['value']), int(tte['tokenDecimal']))
            # correct_amount_tx = to_correct_unit(int(tx['value']), AVAX_DECIMALS)
            obj = {
                'type': 'avax in, erc20 out',
                'received amount': '',  # get this from coingecko?
                'received currency': 'AVAX',
                'sent amount': correct_amount_tte,
                'sent currency': tte['tokenSymbol'],
                'hash': tx['hash'],
                'timeStamp': tx['timeStamp'],
                'tokenDecimal': tte['tokenDecimal'],
            }
            return obj

    return False


def is_erc20_from_someone(transactions, tte):
    for tx in transactions:
        if tx['hash'] == tte['hash']:
            return False

    correct_amount_tte = to_correct_unit(int(tte['value']), int(tte['tokenDecimal']))

    obj = {
        'type': 'tte in',
        'received amount': correct_amount_tte,
        'received currency': tte['tokenSymbol'],
        'sent amount': '',
        'sent currency': '',
        'hash': tte['hash'],
        'timeStamp': tte['timeStamp'],
        'tokenDecimal': tte['tokenDecimal'],
    }

    return obj


def is_avax_from_someone(erc20_transfers, tx):
    for tte in erc20_transfers:
        if tte['hash'] == tx['hash']:
            return False

    correct_amount_tx = to_correct_unit(int(tx['value']), AVAX_DECIMALS)

    obj = {
        'type': 'avax in',
        'received amount': correct_amount_tx,
        'received currency': 'AVAX',
        'sent amount': '',
        'sent currency': '',
        'hash': tx['hash'],
        'timeStamp': tx['timeStamp'],
        'tokenDecimal': AVAX_DECIMALS,
    }

    return obj


def is_avax_to_someone(erc20_transfers, tx):
    for tte in erc20_transfers:
        if tte['hash'] == tx['hash']:
            return False

    correct_amount_tx = to_correct_unit(int(tx['value']), AVAX_DECIMALS)

    obj = {
        'type': 'avax out',
        'received amount': '',
        'received currency': '',
        'sent amount': correct_amount_tx,
        'sent currency': 'AVAX',
        'hash': tx['hash'],
        'timeStamp': tx['timeStamp'],
        'tokenDecimal': AVAX_DECIMALS,
    }

    return obj


def main(address):
    avax_to_erc20 = []  # avax to token swap
    erc20_to_avax = []  # erc20 swap for avax
    erc20_to_erc20 = []  # token swap
    erc20_to_someone = []  # a token transfer to another account
    erc20_from_someone = []  # tte in from another account
    avax_from_someone = []  # native avax transaction
    avax_to_someone = []  # native avax transaction
    avax_approval = []  # contract approvals

    transactions = requests.get(
        f'https://api.snowtrace.io/api?module=account&action=txlist&address={address}&startblock=1&endblock=99999999&sort=asc&apikey={APIKEY_SNOWTRACE}').json()['result']

    erc20_transfers = requests.get(
        f'https://api.snowtrace.io/api?module=account&action=tokentx&address={address}&sort=asc&apikey={APIKEY_SNOWTRACE}').json()['result']

    for tte in erc20_transfers:

        if tte['to'] == address:
            # we find all erc20_to_erc20 in this block
            res = is_erc20_to_erc20(erc20_transfers, tte)
            if res:
                erc20_to_erc20.append(res)
                continue

            # we find the ingoing part of the avax_to_erc20 in this block
            res = is_avax_to_erc20(transactions, tte)
            if res:
                if float(res['sent amount']) == 0.0:
                    erc20_to_someone.append(res)
                else:
                    avax_to_erc20.append(res)
                continue

            # we find the ingoing part of the erc20_from_someone in this block
            res = is_erc20_from_someone(transactions, tte)
            if res:
                erc20_from_someone.append(res)
        elif tte['from'] == address:
            # look for avax_to_erc20, erc20_to_someone, erc20_from_someone
            res = is_erc20_to_avax(transactions, tte)
            if res:
                erc20_to_avax.append(res)

    # Check for avax_from_someone and avax_to_someone
    for tx in transactions:
        if tx['to'] == address:

            res = is_avax_from_someone(erc20_transfers, tx)
            if res:
                avax_from_someone.append(res)
                continue

        elif tx['from'] == address:

            res = is_avax_to_someone(erc20_transfers, tx)
            if res:
                if float(res['sent amount']) == 0.0:
                    avax_approval.append(res)
                else:
                    avax_to_someone.append(res)
                continue

    print(json.dumps(avax_approval, indent=2))

    # sorted_all_txs = sorted(transactions + erc20_transfers, key=itemgetter('timeStamp'))

    # # print(json.dumps(sorted_all_txs, indent=2))
    # # headers taken from koinly specs
    # headers = ['Date', 'Sent Amount', 'Sent Currency', 'Received Amount',	'Received Currency', 'Fee Amount',
    #            'Fee Currency',	'Net Worth Amount',	'Net Worth Currency',	'Label',	'Description',	'TxHash']

    # f = open('txs2.csv', 'w')
    # writer = csv.writer(f)
    # writer.writerow(headers)


main(ACCOUNT1)
