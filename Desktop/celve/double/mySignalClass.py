import talib as ta
import numpy as np
import pandas as pd
import scipy as sp


"""
将kdj策略需要用到的信号生成器抽离出来
"""

class mySignal():

    def __init__(self):
        self.author = 'LHY'

#判断趋势
    def miEnvironment(self, am, paraDict):
        envPeriod = paraDict["envPeriod"]
        longenvPeriod = paraDict["longenvPeriod"]
        MIfactor = paraDict["MIfactor"]

        emaHL = ta.EMA(am.high-am.low,envPeriod)
        emaRatio = emaHL/ta.EMA(emaHL, envPeriod)
        MI = pd.DataFrame(emaRatio[-longenvPeriod:]).dropna().rolling(longenvPeriod).sum().dropna()
        misignal = 0
        dif_up = float(MI.iloc[-1]-longenvPeriod) > float(MIfactor*longenvPeriod)
        dif_down = float(-MI.iloc[-1]+longenvPeriod) > float(MIfactor*longenvPeriod)
        if dif_up:
            misignal = 1
        elif dif_down:
            misignal = -1
        else:
            misignal = 0
        return misignal, MI

#波动状况判断进场
    def bullbearsignal(self, am, paraDict):
        bullPeriod= paraDict["bullPeriod"]
        bearPeriod= paraDict["bearPeriod"]
        bull = am.high - ta.EMA(am.close, bullPeriod)
        bear = am.low - ta.EMA(am.close, bearPeriod)
        # envelder = (envbull - envbear)/am.close
        # global bbsignal
        bbsignal = 0
        bbsignal = 1 if (bear[-1] < 0) or (bull[-1] > 0) else -1
        return bbsignal, bull, bear

#平稳状况判断进场
    def maCross(self, am, paraDict):
        fastPeriod = paraDict["fastPeriod"]
        slowPeriod = paraDict["slowPeriod"]

        sma = ta.MA(am.close, fastPeriod)
        lma = ta.MA(am.close, slowPeriod)

        goldenCross = sma[-1]>lma[-1] and sma[-2]<=lma[-2]
        deathCross = sma[-1]<lma[-1] and sma[-2]>=lma[-2]
        
        global maCrossSignal
        maCrossSignal = 0
        if goldenCross:
            maCrossSignal = 1
        elif deathCross:
            maCrossSignal = -1
        else:
            maCrossSignal = 0
        return maCrossSignal, sma, lma

#判断出场        
    def maExit(self, am, paraDict):
        maPeriod = paraDict["maPeriod"]
        exitSignal_long = am.low[-1]<ta.MA(am.close, maPeriod)[-1]
        exitSignal_short = am.high[-1]>ta.MA(am.close, maPeriod)[-1]
        return exitSignal_long, exitSignal_short