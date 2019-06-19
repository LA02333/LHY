"""
展示如何执行策略回测。
"""
from vnpy.trader.app.ctaStrategy import BacktestingEngine
import pandas as pd
from vnpy.trader.utils import htmlplot
import json
import os,sys
sys.path.append("/Users/apple/Desktop/celve/double")
from myIfStrategy import myStrategy

# 
if __name__ == '__main__':
    # 创建回测引擎
    engine = BacktestingEngine()
    engine.setDB_URI("mongodb://localhost:27017")
    # engine.setDB_URI("mongodb://192.168.4.132:27017")


    # Bar回测
    engine.setBacktestingMode(engine.BAR_MODE)
    engine.setDatabase('VnTrader_1Min_Db')

    # Tick回测
    # engine.setBacktestingMode(engine.TICK_MODE)
    # engine.setDatabase('VnTrader_1Min_Db', 'VnTrader_Tick_Db')

    # 设置回测用的数据起始日期，initHours 默认值为 0
    engine.setStartDate('20161130 10:00:00',initHours=10)
    engine.setEndDate('20170213 23:00:00')

    # 设置产品相关参数
    engine.setCapital(1000000)  # 设置起始资金，默认值是1,000,000
    contracts = [{
                    "symbol":"A88:CTP",
                    "size" : 1, # 每点价值
                    "priceTick" : 0.1, # 最小价格变动
                    "rate" : 5/10000, # 单边手续费
                    "slippage" : 0.002 # 滑价
                    },]

    engine.setContracts(contracts)
    engine.setLog(True, "./logA88")
    # 获取当前绝对路径
    path = os.path.split(os.path.realpath("/Users/apple/Desktop/celve/double/runBacktesting.py"))[0]
    with open(path+"/CTA_setting.json") as f:
        setting = json.load(f)[0]

    # Bar回测
    engine.initStrategy(myStrategy, setting)
    
    # 开始跑回测
    engine.runBacktesting()
    
    # 显示回测结果
    # engine.showBacktestingResult()
    engine.showDailyResult()
    
    # ## 画图分析
    # chartLog = pd.DataFrame(engine.strategy.chartLog).set_index('datetime')
    # mp = htmlplot.getXMultiPlot(engine, freq="15m")
    # mp.addLine(line=chartLog[['MI','bull','bear', 'fastMa', 'slowMa']].reset_index(), colors={"MI": "blue","bull": "red",'bear':'green', 'fastMa':'yellow', 'slowMa':'purple'}, pos=0)
    # mp.resample()
    # mp.show()