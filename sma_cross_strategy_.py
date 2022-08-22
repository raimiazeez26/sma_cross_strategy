#!/usr/bin/env python
# coding: utf-8

# In[1]:


#import libraries
import time
import pandas as pd
import numpy
import MetaTrader5 as mt5
from datetime import datetime as dt
import ta
from MT5pytrader import Trader

#instantiate trader agent
trader = Trader()

#for visualization
import plotly.graph_objects as go

# Calculate SMA indicators
from ta.trend import sma_indicator


#get data from mt5 api - last 1000 data points on M5
def get_data(symbol, ema_slow, ema_fast):

    df = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 500)

    # create DataFrame out of the obtained data
    df = pd.DataFrame(df)
    
    # convert time in seconds into the datetime format
    df['time']=pd.to_datetime(df['time'], unit='s')
    df.index = df.time.values
    df = df.drop(["time", "spread", "real_volume"], axis = 1)
    df.columns = ["Open", "High", "Low", "Close", "Volume"]

    #sma_slow
    sma_slow = sma_indicator(close = df.Close, window = ema_slow)
    df["sma_slow"] = round(sma_slow, 5)
    
    #sma_fast
    sma_fast = sma_indicator(close = df.Close, window = ema_fast)
    df["sma_fast"] = round(sma_fast, 5)


    df = df.dropna()
    return df

#signal function 
def signal_check(df):
    last_close = round(float(df.Close[-2:-1]), 6) 
    sma_fast = df.sma_fast[-1]
    sma_slow = df.sma_slow[-1]
    
    if last_close > sma_fast > sma_slow:
        signal = "buy"
        
    elif last_close < sma_fast < sma_slow:
        signal = "sell"
        
    else:
        signal = "neutral"
        
    return signal 

def strategy(symbols, sma_slow, sma_fast):
    
    # Get number of Open positions
    positions_total=mt5.positions_total()
    print(f"{positions_total} open positions")
    
    for symbol in symbols:
        #get data for symbol
        df = get_data(symbol, sma_slow, sma_fast)
        signal = signal_check(df)
        
        # check the presence of open positions
        positions=mt5.positions_get(symbol=symbol)
        point = mt5.symbol_info(symbol).point
        
       
        
        if len(positions) == 0:  #if no open position on symbol
            print("No positions on {}".format(symbol))
            if signal == "buy":
                trader.open_buy(symbol, lot = 0.50, comment = "sma_cross")
                
            elif signal == "sell":
                trader.open_sell(symbol, lot = 0.50, comment = "sma_cross")
                
            else:
                print("Ranging Market!")
                
        elif len(positions)>0:  #if position open on symbol 
            print(f"Position already open on {symbol} =",len(positions))
            
            for position in positions:
                
                if position.type == 0 and signal != "buy": #if in a buy position and signal changes 
                    trader.close_buy(symbol)
                    print(f"Closing buy position")
                    
                elif position.type == 1 and signal != "sell": #if in a sell position and signal changes 
                    trader.close_sell(symbol)
                    print(f"Closing sell position")
        
    
    
symbols = ["AUDUSD", "EURUSD", "GBPUSD", "NZDUSD", "USDCAD"] 

while True:
    strategy(symbols, 200, 55) #trade sma200 & sma55 combination
    
    time.sleep(60)


# In[ ]:




