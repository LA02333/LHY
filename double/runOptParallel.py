from vnpy.trader.utils import optimize
import sys
sys.path.append("/Users/apple/Desktop/celve/double")
from myIfStrategy_3 import myStrategy
from datetime import datetime
import numpy as np
import os
import json

def setConfig(root=None):
    # 设置策略类
    optimize.strategyClass = myStrategy
    # 设置缓存路径，如果不设置则不会缓存优化结果。
    optimize.root = root
    # 设置引擎参数
    optimize.engineSetting = {
        "startDate": "20160703 10:00:00",
        "endDate": "20190101 23:59:00",
        "dbName": "VnTrader_1Min_Db",
        "contract":[{
                    "slippage": 0.002,
                    "rate": 5/10000,
                    }]
    }
    # 设置策略固定参数
    optimize.globalSetting = {
        "symbolList": ["A88:CTP"],
        "barPeriod": 150,
    }
    # 设置策略优化参数
    optimize.paramsSetting = {
            "envPeriod": range(10,25,5),
            "longenvPeriod": range(20,35,5),
            "MIfactor": np.arange(0.05, 0.2, 0.05),
            "bullPeriod": range(15,30,5),
            "bearPeriod": (10,15,5),

            "fastPeriod": range(5,15,5),
            "slowPeriod": range(20,35,5),

            "maPeriod": range(25,35,5)

    }
    path = os.path.split(os.path.realpath("runOptParallel.py"))[0]
    with open(path+"/CTA_setting.json") as f:
        globalSetting = json.load(f)[0]
    optimize.globalSetting = globalSetting
    optimize.initOpt()

# 并行优化 无缓存
def runSimpleParallel():
    start = datetime.now()
    print("run simple | start: %s -------------------------------------------" % start)
    setConfig()
    # optimize.runParallel() 并行优化，返回回测结果
    report = optimize.runParallel()
    print(report)
    report.sort_values(by = 'sharpeRatio', ascending=False, inplace=True)
    # 将结果保存成csv
    report.to_csv('opt_IF88.csv')    
    end = datetime.now()
    print("run simple | end: %s | expire: %s -----------------------------" % (end, end-start))

def main():
    runSimpleParallel()

if __name__ == '__main__':
    main()