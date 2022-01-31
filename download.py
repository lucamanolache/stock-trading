import yfinance as yf
import pandas as pd

data = yf.download('msft', '2017-01-01', '2019-01-01')
data.to_csv('msft.csv')
