import json
import requests

from env_vars import ACCOUNT1, APIKEY_SNOWTRACE
# with open('tte_with_tte.json', 'r') as tte_with_tte_file:
#     data = tte_with_tte_file.read()
# with open('tte_with_tx.json', 'r') as tte_with_tx_file:
#     data2 = tte_with_tx_file.read()
# with open('tte_with_0tx.json', 'r') as tte_with_0tx_file:
#     data3 = tte_with_0tx_file.read()
# with open('tte_with_tte.json', 'r') as tte_with_tte_file:
#     data3 = tte_with_tte_file.read()
# with open('tte_without_tx.json', 'r') as tte_without_tx_file:
#     data4 = tte_without_tx_file.read()

# tte_with_ttes = json.loads(data)
# tte_with_txs = json.loads(data2)
# tte_with_0txs = json.loads(data3)
# tte_without_txs = json.loads(data4)

# tot = tte_with_ttes + tte_with_txs + tte_with_0txs + tte_without_txs
# print(len(tot))

with open('avax_to_someone.json', 'r') as tte_without_tx_file:
    data4 = tte_without_tx_file.read()

tte_with_ttes = json.loads(data4)

print(len(tte_with_ttes))
# erc20_transfers = requests.get(
#     f'https://api.snowtrace.io/api?module=account&action=tokentx&address={ACCOUNT1}&sort=asc&apikey={APIKEY_SNOWTRACE}').json()['result']
# print(json.dumps(erc20_transfers, indent=2))
