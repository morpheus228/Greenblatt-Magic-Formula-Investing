from magic_formula import MagicFormula
from openapi_client import openapi

client = openapi.api_client('t.Ma_LNZY0MGeWcykAahoL0s9M7aS5Z1QcfdkgXkfu3NuoBp2WbQT_TCRBOgoMlFQU3aGKIRpliakTFsi3urdMtQ')
stocks = client.market.market_stocks_get()

tickers = []
for i in list(stocks.payload.instruments):
    ticker = str(i).split("ticker': '")[1].split("',\n")[0]
    tickers.append(ticker)

print(f'Всего акций: {len(tickers)}', end='\n\n')

mf = MagicFormula()

mf.get_stocks_info(tickers, 100)

stocks = mf.ranking()

stocks.to_csv('ranked_stoсks.csv')