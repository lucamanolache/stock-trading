from datetime import datetime
import backtrader as bt
import numpy as np
import torch
import yfinance as yf
from rich import print, inspect
from rich.console import Console
from rich.traceback import install
from model import LSTM
from sklearn.preprocessing import MinMaxScaler


install(show_locals=True)


class LSTMIndicator(bt.ind.PeriodN):
    """
    This generic indicator doesn't assume the data feed has the components
    ``high``, ``low`` and ``close``. It needs three data sources passed to it,
    which whill considered in that order. (following the OHLC standard naming)
    """
    lines = ('predict_line',)
    params = (('period', 21),)

    def __init__(self):
        super().__init__()
        input_dim = 1
        hidden_dim = 32
        num_layers = 2
        output_dim = 1

        self.model = LSTM(input_dim=input_dim,
                          hidden_dim=hidden_dim,
                          output_dim=output_dim,
                          num_layers=num_layers)

        self.model.load_state_dict(torch.load('model'))
        self.model.eval()
        self.model_input = np.ndarray((0, 20, 1))
        self.scaler = MinMaxScaler(feature_range=(-1, 1))

    def next(self):
        d = np.ndarray((20, 1), dtype=np.float32)
        for i in range(20):
            d[i] = self.data[-i]
        d = np.reshape(self.scaler.fit_transform(d), (1, 20, 1))

        self.model_input = np.append(self.model_input, d, axis=0)
        pred = self.model(torch.from_numpy(self.model_input).type(torch.Tensor))[-1]
        self.l.predict_line[0] = pred[0]


class SmaCross(bt.Strategy):
    def __init__(self):
        self.connor = LSTMIndicator()

    def next(self):
        if not self.position:  # not in the market
            if self.connor > 0:  # if fast crosses slow to the upside
                self.buy()  # enter long

        elif self.connor < 0:  # in the market & cross to the downside
            self.close()  # close long position


cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)

data = bt.feeds.YahooFinanceCSVData(dataname="msft.csv")

cerebro.adddata(data)
cerebro.broker.setcash(100000)
cerebro.run()
cerebro.plot()
