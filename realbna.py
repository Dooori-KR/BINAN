import sys
import ccxt
import pandas as pd
import time
import datetime
from PyQt5.QtCore import *
import requests

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization":"Bearer "+token},
        data={"channel":channel,"text":text}
    )
    print(response)

myToken = ""


tickers=['BTC/USDT']
binance=ccxt.binance()

def get_state(ticker):
    btc_ohlc=binance.fetch_ohlcv(ticker,'1m',limit=200)
    df=pd.DataFrame(btc_ohlc,columns=['datetime(UTC)','open','high','low','close','volume'])  
    df['datetime(UTC)']=pd.to_datetime(df['datetime(UTC)'],unit='ms')
    df.set_index('datetime(UTC)',inplace=True)
    ma5=df['close'].rolling(180).mean()
    last_ma5=round(ma5[-2],4)
    price=binance.fetch_ticker(ticker)['close']

    if price > last_ma5:
        state = "Bullish"
    else:
        state = "Bearish"
    return state

def get_impulse(ticker):
    btc_ohlc=binance.fetch_ohlcv(ticker,'1m',limit=200)
    df=pd.DataFrame(btc_ohlc,columns=['datetime(UTC)','open','high','low','close','volume'])  
    df['datetime(UTC)']=pd.to_datetime(df['datetime(UTC)'],unit='ms')
    df.set_index('datetime(UTC)',inplace=True)
    ma5=df['close'].rolling(180).mean()
    last_ma5=round(ma5[-2],4)
    price=binance.fetch_ticker(ticker)['close']

    last180=min(df['low'][-180:-1])*1.015 < max(df['high'][-180:-1])
    if last180:
        impulse = "Impulsive"
    else:
        impulse = "Not Impulsive"
    return impulse

def get_gg(ticker):
    btc_ohlc=binance.fetch_ohlcv(ticker,'1m',limit=200)
    df=pd.DataFrame(btc_ohlc,columns=['datetime(UTC)','open','high','low','close','volume'])  
    df['datetime(UTC)']=pd.to_datetime(df['datetime(UTC)'],unit='ms')
    df.set_index('datetime(UTC)',inplace=True)
    ma5=df['close'].rolling(180).mean()
    last_ma5=round(ma5[-2],4)
    price=binance.fetch_ticker(ticker)['close']    

    if df['close'][-2]*1.0004 < price:
        gdgr="JUMP"
    elif df['close'][-2] > price*1.0004:
        gdgr="DROP"
    else:
        gdgr="No Signal"
    return gdgr

turnimpulse=0
gg2=0

while True:
    data = {}
    now=datetime.datetime.now().time()
    now=str(now)[:8]
    isimpulse=get_impulse('BTC/USDT')
    isstate=get_state('BTC/USDT')
    price=binance.fetch_ticker('BTC/USDT')['close']
    gg=get_gg('BTC/USDT')

    if turnimpulse==0:
        post_message(myToken,'#stock',now+" start program")
    elif turnimpulse!=isimpulse:
        post_message(myToken,'#stock',"Time : "+now+"\nBTC 3hours (1.5%) : "+isimpulse+"\nBTC Price : "+str(price)+"\nBTC condition : "+str(isstate))
    turnimpulse=isimpulse
    if gg2==0:
        pass
    elif gg2!=gg:
        if gg=="JUMP":
            post_message(myToken,'#stock',now+gg)
        if gg=="DROP":
            post_message(myToken,'#stock',now+gg)
    gg2=gg
    
    if now[3:8]=="00:00":
        post_message(myToken,'#stock',"Time : "+now+"\nBTC 3hours (1.5%) : "+isimpulse+"\nBTC Price : "+str(price)+"\nBTC condition : "+str(isstate))
    time.sleep(0.5)
