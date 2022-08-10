import pandas as pd, pandas_ta as ta

def genBaseIndicator(df: pd.DataFrame, cols_for_new: list = []):
    if len(cols_for_new) > 0:
        df_result = df[cols_for_new]
    else:
        df_result = df
    
    # moving average
    for ma in [5, 10, 20, 60, 120]:
        df_result[f"ma{ma}"] = ta.sma(df.close, ma)
    df_result["mavolu"] = ta.sma(df.volume, 10)
    
    # disparity
    for ma in [10, 20, 60, 120]:
        df_result[f"dsp{ma}"] = (df.ma5 - df[f"ma{ma}"]) / df.ma5
        
    # bolinger, macd, rsi
    df_result[["bbl", "bbm", "bbu", "bbb", "bbp"]] = ta.bbands(df.close, length=20, std=2)
    df_result[["macd", "macdh", "macds"]] = ta.macd(df.close, fast=12, slow=26, signal=9)
    df_result["rsi"] = ta.rsi(df.close, 15)
    df_result[["adx", "dmp", "dmn"]] = ta.adx(df.high, df.low, df.close, 11)
    df_result["dmp"] = ta.sma(df.dmp, 5)
    df_result["dmn"] = ta.sma(df.dmn, 5)
    df_result["adxpn"] = df_result.dmp - df_result.dmn
    df_result["obv"] = ta.obv(df.close, df.volume)

    if len(cols_for_new) > 0:
        return df_result
