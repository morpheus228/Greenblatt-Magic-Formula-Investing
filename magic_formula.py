import pandas as pd
import numpy as np
import yfinance as yf
from openapi_client import openapi
import warnings
import time

warnings.filterwarnings("ignore")


class MagicFormula:
    def __init__(self):
        self.ready_stocks = pd.DataFrame({'ticker': [],
                                          'ep': [],
                                          'roa': [],
                                          'sector': [],
                                          'price': [],
                                          'currency': []})

        self.error_stocks = pd.DataFrame({'ticker': [],
                                          'status': []})
        self.last_time = time.time()
        self.time_cur = time.time()
        self.sum_time = 0

    def preproccesing(self, ticker):
        ticker = ticker.replace('_old', '')
        ticker = ticker.replace('old', '')
        return ticker

    def save_files(self):
        self.ready_stocks.to_csv('stocks1.csv')
        self.error_stocks.to_csv('errors1.csv')

    def time(self):
        self.last_time = time.time() - self.time_cur
        self.time_cur = time.time()
        self.sum_time += self.last_time

    def print_info(self, ):
        print(f'{round(((self.i+1) / self.arr_size) * 100, 2)}% ВЫПОЛНЕНО')
        print(f'{(self.i+1)} АКЦИЙ СДЕЛАНО')
        print(f'ПРОШЛО {round(self.sum_time,1)} СЕКУНД')
        print(f'ПОСЛЕДНЯЯ ОПЕРАЦИЯ ДЛИЛАСЬ {round(self.last_time, 1)} СЕКУНД')
        print(f'ПРИМЕРНО ОСТАЛОСЬ {round(self.last_time * (self.arr_size - self.i), 1)} СЕКУНД')
        print()

    def check_error(self, stock):
        try:
            info = stock.info

            if len(info) <= 2:
                return 'ТАКОЙ АКЦИИ НЕТ НА YFINANCE'

            if (not 'sharesOutstanding' in info.keys()) or (info['sharesOutstanding'] == None):
                return 'НЕТ КОЛ-ВА АКЦИЙ'

            financials = stock.quarterly_financials

            if len(financials) == 0:
                return 'ОТСУТСТВУЮТ ФИНАНСЫ'

            balance = stock.quarterly_balance_sheet

            if len(balance) == 0:
                'ОТСУТСТВУЕТ БАЛАНС'

            return 'НЕИЗВЕСТНАЯ ОШИБКА'

        except:
            return 'НЕИЗВЕСТНАЯ ОШИБКА'

    def get_other_variants_for_name(self, ticker):
        variants = []
        variants.append(ticker + '.ME')
        variants.append(ticker.replace('@', '.'))

        return variants

    def get_stock_score(self, ticker):
        stock = yf.Ticker(ticker)

        try:
            info = stock.info
            financials = stock.quarterly_financials
            balance = stock.quarterly_balance_sheet

            roa = financials.loc['Ebit', :].sum() / (balance.loc['Net Tangible Assets', :][0] + (
                        balance.loc['Total Current Assets', :][0] - balance.loc['Total Current Liabilities', :][
                    0])) * 100
            ep = financials.loc['Ebit', :].sum() / (
                        (info['currentPrice'] * info['sharesOutstanding']) + balance.loc['Total Liab'][0] -
                        balance.loc['Cash'][0]) * 100

            sector = info['sector']
            price = info['currentPrice']
            currency = info['currency']

            new_row = {'ticker': ticker,
                       'ep': ep,
                       'roa': roa,
                       'sector': sector,
                       'price': price,
                       'currency': currency,
                       }
            return (1, new_row)

        except:
            error_name = self.check_error(stock)

            new_row = {'ticker': ticker,
                       'status': error_name}

            return (0, new_row)

    def get_stocks_info(self, tickers, when_save):

        self.arr_size = len(tickers)

        for self.i in range(self.arr_size):

            if self.i % when_save == 0:
                self.save_files()

            ticker = tickers[self.i]
            ticker = self.preproccesing(ticker)
            status, ans = self.get_stock_score(ticker)

            if status == 1:
                self.ready_stocks = self.ready_stocks.append(ans, ignore_index=True)
                print(f'{ticker} - УСПЕШНО')

            else:
                other_variants_for_name = self.get_other_variants_for_name(ticker)
                do = True

                for another_ticker in other_variants_for_name:
                    status_, ans_ = self.get_stock_score(another_ticker)

                    if status_ == 1:
                        self.ready_stocks = self.ready_stocks.append(ans_, ignore_index=True)
                        print(f'{ticker} - УСПЕШНО')
                        do = False
                        break

                if do:
                    self.error_stocks = self.error_stocks.append(ans, ignore_index=True)
                    print(f"{ticker} - { ans['status'] }")

            self.time()
            self.print_info()

        return self.ready_stocks, self.error_stocks

    def ranking(self):
        self.ready_stocks = self.ready_stocks[(self.ready_stocks['roa']) > 0 & (self.ready_stocks['ep'] > 0)]

        add_df = self.ready_stocks.sort_values('roa', ascending=False)
        add_df['roa_place'] = np.arange(self.ready_stocks.shape[0])
        self.ready_stocks = self.ready_stocks.merge(add_df.loc[:, ['ticker', 'roa_place']], on=['ticker'])

        add_df = self.ready_stocks.sort_values('ep', ascending=False)
        add_df['ep_place'] = np.arange(self.ready_stocks.shape[0])
        self.ready_stocks = self.ready_stocks.merge(add_df.loc[:, ['ticker', 'ep_place']], on=['ticker'])

        self.ready_stocks['total_place'] = self.ready_stocks.ep_place + self.ready_stocks.roa_place
        self.ready_stocks = self.ready_stocks.sort_values('total_place')

        return self.ready_stocks
