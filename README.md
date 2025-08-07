# VeighNa框架的AkShare数据服务接口

<p align="center">
  <img src ="https://vnpy.oss-cn-shanghai.aliyuncs.com/vnpy-logo.png"/>
</p>

<p align="center">
    <img src ="https://img.shields.io/badge/version-1.0.0-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-windows|linux|macos-yellow.svg"/>
    <img src ="https://img.shields.io/badge/python-3.10|3.11|3.12|3.13-blue.svg"/>
    <img src ="https://img.shields.io/github/license/vnpy/vnpy.svg?color=orange"/>
</p>

## 说明

基于akshare模块的1.17.25版本开发，支持以下中国金融市场的K线数据：

* 期货：
  * CFFEX：中国金融期货交易所
  * SHFE：上海期货交易所
  * DCE：大连商品交易所
  * CZCE：郑州商品交易所
  * INE：上海国际能源交易中心
  * GFEX：广州期货交易所
* 股票：
  * SSE：上海证券交易所
  * SZSE：深圳证券交易所
  * BSE：北京证券交易所

AkShare是一个开源的金融数据接口库，无需注册即可获取数据。

## 安装

安装环境推荐基于4.0.0版本以上的【[**VeighNa Studio**](https://www.vnpy.com)】。

直接使用pip命令：

```
pip install vnpy_akshare
```

或者下载源代码后，解压后在cmd中运行：

```
pip install .
```

## 使用

在VeighNa中使用AkShare时，需要在全局配置中填写以下字段信息：

|名称|含义|必填|举例|
|---------|----|---|---|
|datafeed.name|名称|是|akshare|

注意：AkShare无需用户名和密码。

### 示例代码

```python
from datetime import datetime
from vnpy_akshare import Datafeed
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import HistoryRequest

# 创建数据接口实例
datafeed = Datafeed()

# 初始化
if datafeed.init():
    # 创建历史数据请求
    req = HistoryRequest(
        symbol="000001",  # 平安银行
        exchange=Exchange.SZSE,
        start=datetime(2023, 1, 1),
        end=datetime(2023, 1, 10),
        interval=Interval.DAILY
    )
    
    # 查询历史数据
    bars = datafeed.query_bar_history(req)
    
    if bars:
        for bar in bars:
            print(f"时间: {bar.datetime}, 开盘: {bar.open_price}, 最高: {bar.high_price}, "
                  f"最低: {bar.low_price}, 收盘: {bar.close_price}, 成交量: {bar.volume}")
```

## 单元测试

单元测试代码目录为`./tests/test_*.py`
```sh
# 进入测试目录
cd tests

# 指定文件执行单元测试
python test_query_bar_history.py
```

