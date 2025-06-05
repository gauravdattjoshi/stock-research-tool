#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 11:23:51 2023

@author: adityajoshi
"""


import yfinance as yf
import pandas as pd
import vectorbt as vbt
from ta.volatility import DonchianChannel
from datetime import datetime, timedelta
import numpy as np
import requests
import os


def enter_position(symbol):
    """Run breakout backtest for a symbol and send Telegram alerts."""
    # Fetch stock data using yfinance
    stock_data = vbt.YFData.download(
        symbol, start=datetime.now() - timedelta(200), end=datetime.now()
    ).get(["Close", "Low", "High"])

    stock_data["20day_max"] = stock_data.Close.vbt.rolling_max(window=20)
    dc = DonchianChannel(stock_data.High, stock_data.Low, stock_data.Close)
    stock_data["mband"] = dc.donchian_channel_mband()

    # Define a signal when price exceeds the 20-period high
    entry = np.where(stock_data.Close >= stock_data["20day_max"], True, False)
    stock_data["Exit"] = np.where(stock_data.Close <= stock_data["mband"], True, False)
    stock_data[symbol] = symbol

    print(stock_data)

    pf = vbt.Portfolio.from_signals(
        stock_data["Close"],
        entries=entry,
        # exits=stock_data['Exit'],
        sl_stop=0.025,
        tp_stop=0.05,
        fixed_fees=1300,
        slippage=0.001,
        init_cash=500000,
    )
    print(pf.stats())

    df_func = pd.DataFrame(pf.stats())
    df_func.drop(index=df_func.index[:2], axis=0, inplace=True)
    df_func.columns = [symbol]
    winrate = (df_func[df_func.index == "Win Rate [%]"].values[0])[0]
    openpnl = (df_func[df_func.index == "Open Trade PnL"].values[0])[0]
    # print(type(winrate), winrate,np.isnan(winrate), type(openpnl), openpnl, openpnl>2000)
    try:
        send_message(
            symbol,
            entry[-1],
            stock_data["Close"].iloc[-1],
            entry[-5:],
            winrate,
            openpnl,
        )
    except:
        send_message(
            symbol, entry[-1], stock_data["Close"].iloc[-1], entry[-1], winrate, openpnl
        )

    return df_func


def final():
    """Run the strategy across multiple symbols and merge results."""
    nifty50 = "%5ENSEI"
    stocks = [
        "ABB.NS",
        "ACC.NS",
        "AUBANK.NS",
        "ABBOTINDIA.NS",
        "ADANIENT.NS",
        "ADANIGREEN.NS",
        "ADANIPORTS.NS",
        "ADANIPOWER.NS",
        "ATGL.NS",
        "AWL.NS",
        "ABCAPITAL.NS",
        "ABFRL.NS",
        "ALKEM.NS",
        "AMBUJACEM.NS",
        "APOLLOHOSP.NS",
        "APOLLOTYRE.NS",
        "ASHOKLEY.NS",
        "ASIANPAINT.NS",
        "ASTRAL.NS",
        "AUROPHARMA.NS",
        "DMART.NS",
        "AXISBANK.NS",
        "BAJAJ-AUTO.NS",
        "BAJFINANCE.NS",
        "BAJAJFINSV.NS",
        "BAJAJHLDNG.NS",
        "BALKRISIND.NS",
        "BANDHANBNK.NS",
        "BANKBARODA.NS",
        "BANKINDIA.NS",
        "BATAINDIA.NS",
        "BERGEPAINT.NS",
        "BEL.NS",
        "BHARATFORG.NS",
        "BHEL.NS",
        "BPCL.NS",
        "BHARTIARTL.NS",
        "BIOCON.NS",
        "BOSCHLTD.NS",
        "BRITANNIA.NS",
        "CGPOWER.NS",
        "CANBK.NS",
        "CHOLAFIN.NS",
        "CIPLA.NS",
        "COALINDIA.NS",
        "COFORGE.NS",
        "COLPAL.NS",
        "CONCOR.NS",
        "COROMANDEL.NS",
        "CROMPTON.NS",
        "CUMMINSIND.NS",
        "DLF.NS",
        "DABUR.NS",
        "DALBHARAT.NS",
        "DEEPAKNTR.NS",
        "DELHIVERY.NS",
        "DEVYANI.NS",
        "DIVISLAB.NS",
        "DIXON.NS",
        "LALPATHLAB.NS",
        "DRREDDY.NS",
        "EICHERMOT.NS",
        "ESCORTS.NS",
        "NYKAA.NS",
        "FEDERALBNK.NS",
        "FORTIS.NS",
        "GAIL.NS",
        "GLAND.NS",
        "GODREJCP.NS",
        "GODREJPROP.NS",
        "GRASIM.NS",
        "FLUOROCHEM.NS",
        "GUJGASLTD.NS",
        "HCLTECH.NS",
        "HDFCAMC.NS",
        "HDFCBANK.NS",
        "HDFCLIFE.NS",
        "HAVELLS.NS",
        "HEROMOTOCO.NS",
        "HINDALCO.NS",
        "HAL.NS",
        "HINDPETRO.NS",
        "HINDUNILVR.NS",
        "HINDZINC.NS",
        "HONAUT.NS",
        "ICICIBANK.NS",
        "ICICIGI.NS",
        "ICICIPRULI.NS",
        "IDFCFIRSTB.NS",
        "ITC.NS",
        "INDIANB.NS",
        "INDHOTEL.NS",
        "IOC.NS",
        "IRCTC.NS",
        "IRFC.NS",
        "IGL.NS",
        "INDUSTOWER.NS",
        "INDUSINDBK.NS",
        "NAUKRI.NS",
        "INFY.NS",
        "INDIGO.NS",
        "IPCALAB.NS",
        "JSWENERGY.NS",
        "JSWSTEEL.NS",
        "JINDALSTEL.NS",
        "JUBLFOOD.NS",
        "KOTAKBANK.NS",
        "L&TFH.NS",
        "LTTS.NS",
        "LICHSGFIN.NS",
        "LTIM.NS",
        "LT.NS",
        "LAURUSLABS.NS",
        "LICI.NS",
        "LUPIN.NS",
        "MRF.NS",
        "M&MFIN.NS",
        "M&M.NS",
        "MARICO.NS",
        "MARUTI.NS",
        "MFSL.NS",
        "MAXHEALTH.NS",
        "MSUMI.NS",
        "MPHASIS.NS",
        "MUTHOOTFIN.NS",
        "NHPC.NS",
        "NMDC.NS",
        "NTPC.NS",
        "NAVINFLUOR.NS",
        "NESTLEIND.NS",
        "OBEROIRLTY.NS",
        "ONGC.NS",
        "OIL.NS",
        "PAYTM.NS",
        "OFSS.NS",
        "POLICYBZR.NS",
        "PIIND.NS",
        "PAGEIND.NS",
        "PATANJALI.NS",
        "PERSISTENT.NS",
        "PETRONET.NS",
        "PIDILITIND.NS",
        "PEL.NS",
        "POLYCAB.NS",
        "POONAWALLA.NS",
        "PFC.NS",
        "POWERGRID.NS",
        "PRESTIGE.NS",
        "PGHH.NS",
        "PNB.NS",
        "RECLTD.NS",
        "RELIANCE.NS",
        "SBICARD.NS",
        "SBILIFE.NS",
        "SRF.NS",
        "MOTHERSON.NS",
        "SHREECEM.NS",
        "SHRIRAMFIN.NS",
        "SIEMENS.NS",
        "SONACOMS.NS",
        "SBIN.NS",
        "SAIL.NS",
        "SUNPHARMA.NS",
        "SUNTV.NS",
        "SYNGENE.NS",
        "TVSMOTOR.NS",
        "TATACHEM.NS",
        "TATACOMM.NS",
        "TCS.NS",
        "TATACONSUM.NS",
        "TATAELXSI.NS",
        "TATAMOTORS.NS",
        "TATAPOWER.NS",
        "TATASTEEL.NS",
        "TTML.NS",
        "TECHM.NS",
        "RAMCOCEM.NS",
        "TITAN.NS",
        "TORNTPHARM.NS",
        "TORNTPOWER.NS",
        "TRENT.NS",
        "TRIDENT.NS",
        "TIINDIA.NS",
        "UPL.NS",
        "ULTRACEMCO.NS",
        "UNIONBANK.NS",
        "UBL.NS",
        "MCDOWELL-N.NS",
        "VBL.NS",
        "VEDL.NS",
        "IDEA.NS",
        "VOLTAS.NS",
        "WHIRLPOOL.NS",
        "WIPRO.NS",
        "YESBANK.NS",
        "ZEEL.NS",
        "ZOMATO.NS",
        "ZYDUSLIFE.NS",
    ]

    df_base = enter_position(nifty50)
    for stock in stocks:
        print(stock)
        df_new = enter_position(stock)
        df_final = pd.merge(
            df_base,
            df_new,
            how="inner",
            left_index=True,
            right_index=True,
        )
        df_base = df_final

    return df_base


def send_message(stock, entry_signal, price, last_10, winrate, openpnl):
    """Send a Telegram alert when entry conditions are met."""
    # Set up Telegram bot

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        raise ValueError("Telegram credentials not provided")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}"
    print(
        "run_bbbb",
        type(winrate),
    )
    textdata = {
        "text": f"BREAKOUT 20 DAY HIGH STRATEGY HAS HAPPENED IN {stock}.\
            \nThe winrate of this stock  is {winrate}.\nPlease buy a fut of this stock .\
                \nThe curent PnL is {openpnl}.\n Close price:{price}. \
                \nLast 10 entry conditions:{last_10}"
    }
    if (
        len(last_10) > 1
        and last_10[-2] == False
        and entry_signal == True
        and winrate > 35
        and 1 <= openpnl <= 10000
    ):
        requests.request("POST", url, params=textdata)
    elif (
        len(last_10) == 1
        and entry_signal == True
        and winrate > 35
        and 1 <= openpnl <= 10000
    ):
        requests.request("POST", url, params=textdata)
    if (
        (25 <= winrate <= 100)
        and (1 <= openpnl <= 2000)
        and (np.isnan(winrate) != True)
    ):
        requests.request("POST", url, params=textdata)


if __name__ == "__main__":
    df = final()
    df = df.T
    df.apply(pd.to_numeric)
