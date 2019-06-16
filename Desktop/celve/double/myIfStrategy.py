from __future__ import division
from vnpy.trader.vtConstant import *
from vnpy.trader.app.ctaStrategy import CtaTemplate
import talib as ta
import numpy as np
from datetime import datetime
import sys
sys.path.append("/Users/apple/Desktop/celve/double")
from mySignalClass import mySignal

########################################################################
# 策略继承CtaTemplate
class myStrategy(CtaTemplate):
    className = 'myStrategy'
    author = 'LHY'

    # 策略变量
    transactionPrice = {} # 记录成交价格
    
     # 参数列表
    paramList = [
                 'timeframeMap',
                 'symbolList', 'barPeriod', 'lot',
                 'envPeriod', 'longenvPeriod', 'MIfactor',
                 'bullperiod', 'bearperiod',
                 'fastPeriod','slowPeriod',
                 'maPeriod',
                 'stoplossPct',
                ]    
    
    # 变量列表
    varList = ['transactionPrice']  
    
    # 同步列表，保存了需要保存到数据库的变量名称
    syncList = ['posDict', 'eveningDict']

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        # 首先找到策略的父类（就是类CtaTemplate），然后把DoubleMaStrategy的对象转换为类CtaTemplate的对象
        super().__init__(ctaEngine, setting)
        self.paraDict = setting
        self.symbol = self.symbolList[0]
        self.transactionPrice = None # 生成成交价格的字典
        self.misignal = None

        self.chartLog = {
                'datetime':[],
                'MI':[],
                'bull':[],
                'bear':[],
                'fastMa':[],
                'slowMa':[]
                }

    def prepare_data(self):
        for timeframe in list(set(self.timeframeMap.values())):
            self.registerOnBar(self.symbol, timeframe, None)

    def arrayPrepared(self, period):
        am = self.getArrayManager(self.symbol, period)
        if not am.inited:
            return False, None
        else:
            return True, am

    #----------------------------------------------------------------------
    def onInit(self):
        """初始化策略"""
        self.setArrayManagerSize(self.barPeriod)
        self.prepare_data()
        self.putEvent()

    #----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'策略启动')
        self.putEvent()
    
    #----------------------------------------------------------------------
    def onStop(self):
        """停止策略"""
        self.writeCtaLog(u'策略停止')
        self.putEvent()
        
    #----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送"""
        pass
    
    def on5MinBar(self, bar):
        self.strategy(bar)
        
    def exitSignal(self, signalPeriod):
        arrayPrepared, amSignal = self.arrayPrepared(signalPeriod)
        algorithm = mySignal()
        misignal = 0
        exitSignal_long = 0
        exitSignal_short = 0
        if arrayPrepared:
            misignal = algorithm.miEnvironment(amSignal, self.paraDict)
            exitSinal_long, exitSignal_short = algorithm.maExit(amSignal, self.paraDict)
        return exitSignal_long, exitSignal_short, misignal

    def exitOrder(self, bar, misignal, exitSignal_long, exitSignal_short):
        exitStatus = 0
        if misignal!=0:
            if exitSignal_long and self.posDict[self.symbol+'_LONG']>0:
                self.sell(self.symbol, bar.close*0.99, self.posDict[self.symbol+'_LONG'])
                exitStatus = 1
            if exitSignal_short and self.posDict[self.symbol+'_SHORT']>0:
                self.cover(self.symbol, bar.close*1.01, self.posDict[self.symbol+'_SHORT'])
                exitStatus = 1
        else: #止损    
            if self.posDict[self.symbol+'_LONG']>0:
                if bar.low <(self.transactionPrice*(1-self.stoplossPct)):
                    self.cancelAll()
                    self.sell(self.symbol, bar.close*0.99, self.posDict[self.symbol+'_LONG'])
                    exitStatus = 1
            if self.posDict[self.symbol+'_SHORT']>0:
                if bar.high >(self.transactionPrice*(1+self.stoplossPct)):
                    self.cancelAll()
                    self.cover(self.symbol, bar.close*1.01, self.posDict[self.symbol+'_SHORT'])
                    exitStatus = 1
        return exitStatus

    def entrySignal(self, signalPeriod):
        arrayPrepared, amSignal = self.arrayPrepared(signalPeriod)
        algorithm = mySignal()

        misignal = 0
        MI = [0]
        bbsignal = [0]
        bull, bear = [0], [0]
        maCrossSignal = [0]
        sma, lma = [0], [0]

        if arrayPrepared:
            misignal, MI = algorithm.miEnvironment(amSignal, self.paraDict)
            if misignal == 0: #平稳
                maCrossSignal, sma, lma = algorithm.maCross(amSignal,self.paraDict)
            else: #波动
                bbsignal, bull, bear = algorithm.bullbearsignal(amSignal, self.paraDict)
            print(bull)
                # 画图记录数据
            self.chartLog['datetime'].append(datetime.strptime(amSignal.datetime[-1], "%Y%m%d %H:%M:%S"))
            self.chartLog['MI'].append(MI[-1])
            self.chartLog['bull'].append(bull[-1])
            self.chartLog['bear'].append(bear[-1])
            self.chartLog['fastMa'].append(fastMa[-1])
            self.chartLog['slowMa'].append(slowMa[-1])
            
        return misignal, bbsignal, bull, bear, maCrossSignal


    def entryOrder(self, bar, misignal, bbsignal, bull, bear, maCrossSignal):
        if misignal == 1: #波动看涨
            if (bbsignal == 1) and (self.posDict[self.symbol+'_SHORT']==0):
                if  self.posDict[self.symbol+'_LONG']==0:
                    self.buy(self.symbol, bar.close*1.01, self.lot)  # 成交价*1.01发送高价位的限价单，以最优市价买入进场
                # 如果有空头持仓，则先平空，再做多
                elif self.posDict[self.symbol+'_LONG'] > 0:
                    self.cancelAll() # 撤销挂单
                    self.cover(self.symbol, bar.close*1.01, self.posDict[self.symbol+'_LONG'])
                    self.buy(self.symbol, bar.close*1.01, self.lot)
            
        elif misignal == -1: #波动看跌
            if (bbsignal == 1) and (self.posDict[self.symbol+'_LONG']==0):
                if self.posDict[self.symbol+'_SHORT']==0:
                    self.short(self.symbol, bar.close*0.99, self.lot) # 成交价*0.99发送低价位的限价单，以最优市价卖出进场
                elif self.posDict[self.symbol+'_SHORT'] > 0:
                    self.cancelAll() # 撤销挂单
                    self.sell(self.symbol, bar.close*0.99, self.posDict[self.symbol+'_SHORT'])
                    self.short(self.symbol, bar.close*0.99, self.lot)
        else:#平稳金叉死叉
            if (maCrossSignal==1) and (self.posDict[self.symbol+'_SHORT']==0) and (bull[-1]>0):
                if  self.posDict[self.symbol+'_LONG']==0:
                    self.buy(self.symbol, bar.close*1.01, self.lot)  # 成交价*1.01发送高价位的限价单，以最优市价买入进场
                elif self.posDict[self.symbol+'_LONG'] > 0:
                    self.cancelAll() # 撤销挂单
                    self.cover(self.symbol, bar.close*1.01, self.posDict[self.symbol+'_LONG'])
                    self.buy(self.symbol, bar.close*1.01, self.lot)
            elif (maCrossSignal==-1) and (self.posDict[self.symbol+'_LONG']==0) and (bear[-1]<0):
                if self.posDict[self.symbol+'_SHORT']==0:
                    self.short(self.symbol, bar.close*0.99, self.lot) # 成交价*0.99发送低价位的限价单，以最优市价卖出进场
                elif self.posDict[self.symbol+'_SHORT'] > 0:
                    self.cancelAll() # 撤销挂单
                    self.sell(self.symbol, bar.close*0.99, self.posDict[self.symbol+'_SHORT'])
                    self.short(self.symbol, bar.close*0.99, self.lot)

    def strategy(self, bar):
        envPeriod= self.timeframeMap["envPeriod"]
        signalPeriod= self.timeframeMap["signalPeriod"]

        # 根据出场信号出场
        exitSignal_long, exitSignal_short, misignal = self.exitSignal(signalPeriod)
        exitStatus = self.exitOrder(bar, misignal, exitSignal_long, exitSignal_short)
        # 根据进场信号进场
        misignal, bbsignal, bull, bear, maCrossSignal = self.entrySignal(signalPeriod)
        if not exitStatus:
            self.entryOrder(bar, misignal, bbsignal, bull, bear, maCrossSignal)
        


    
    #----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送"""
        if order.offset == OFFSET_OPEN:  # 判断成交订单类型
            self.transactionPrice = order.price_avg # 记录成交价格
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass
    
    #----------------------------------------------------------------------
    def onTrade(self, trade):
        """收到成交推送"""
        pass
    #----------------------------------------------------------------------
    def onStopOrder(self, so):
        """停止单推送"""
        pass