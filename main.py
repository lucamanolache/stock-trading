from datetime import datetime
import backtrader as bt
import yfinance as yf


class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=50,  # period for the fast moving average
        pslow=200   # period for the slow moving average
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal

    def next(self):
        print(self.position)
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.buy(size=100)  # enter long

        elif self.crossover < 0:  # in the market & cross to the downside
            self.close(size=100)  # close long position


cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)

data = bt.feeds.YahooFinanceCSVData(dataname="msft.csv")

cerebro.adddata(data)
cerebro.broker.setcash(100000)
cerebro.run()
cerebro.plot()
