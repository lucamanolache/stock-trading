import yfinance as yf
import pandas as pd

data = yf.download('msft', '2000-01-01', '2021-01-01')
data.to_csv('msft.csv')
