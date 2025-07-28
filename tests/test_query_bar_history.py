import datetime
from vnpy_akshare.akshare_datafeed import AkshareDatafeed
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import HistoryRequest

def test_query_bar_history():
    """测试 query_bar_history 方法"""
    # 创建数据接口实例
    datafeed = AkshareDatafeed()
    
    # 初始化
    if not datafeed.init():
        print("AkShare数据接口初始化失败")
        return
    
    print("AkShare数据接口初始化成功")
    
    # 测试1: 股票数据获取 (平安银行)
    print("\n=== 测试1: 股票数据获取 ===")
    req1 = HistoryRequest(
        symbol="000001",
        exchange=Exchange.SZSE,
        start=datetime.datetime(2023, 1, 1),
        end=datetime.datetime(2023, 1, 10),
        interval=Interval.DAILY
    )
    
    bars1 = datafeed.query_bar_history(req1)
    if bars1:
        print(f"成功获取到{len(bars1)}条股票K线数据")
        for bar in bars1[:3]:  # 显示前3条数据
            print(f"  时间: {bar.datetime}, 开盘: {bar.open_price}, 最高: {bar.high_price}, "
                  f"最低: {bar.low_price}, 收盘: {bar.close_price}, 成交量: {bar.volume}")
    else:
        print("未能获取到股票数据")
    
    # 测试2: 基金数据获取 (以某个ETF为例，如510050)
    print("\n=== 测试2: 基金数据获取 ===")
    req2 = HistoryRequest(
        symbol="510050",
        exchange=Exchange.SSE,
        start=datetime.datetime(2023, 1, 1),
        end=datetime.datetime(2023, 1, 10),
        interval=Interval.DAILY
    )
    
    bars2 = datafeed.query_bar_history(req2)
    if bars2:
        print(f"成功获取到{len(bars2)}条基金K线数据")
        for bar in bars2[:3]:  # 显示前3条数据
            print(f"  时间: {bar.datetime}, 开盘: {bar.open_price}, 最高: {bar.high_price}, "
                  f"最低: {bar.low_price}, 收盘: {bar.close_price}, 成交量: {bar.volume}")
    else:
        print("未能获取到基金数据")
    
    # 测试3: 指数数据获取 (以上证指数为例)
    print("\n=== 测试3: 指数数据获取 ===")
    req3 = HistoryRequest(
        symbol="000001",
        exchange=Exchange.SSE,
        start=datetime.datetime(2023, 1, 1),
        end=datetime.datetime(2023, 1, 10),
        interval=Interval.DAILY
    )
    
    bars3 = datafeed.query_bar_history(req3)
    if bars3:
        print(f"成功获取到{len(bars3)}条指数K线数据")
        for bar in bars3[:3]:  # 显示前3条数据
            print(f"  时间: {bar.datetime}, 开盘: {bar.open_price}, 最高: {bar.high_price}, "
                  f"最低: {bar.low_price}, 收盘: {bar.close_price}, 成交量: {bar.volume}")
    else:
        print("未能获取到指数数据")

    # 测试4: 错误处理 - 无效的交易所
    print("\n=== 测试4: 错误处理 ===")
    req4 = HistoryRequest(
        symbol="000001",
        exchange=Exchange.SMART,  # SMART不是一个支持的交易所
        start=datetime.datetime(2023, 1, 1),
        end=datetime.datetime(2023, 1, 10),
        interval=Interval.DAILY
    )
    
    bars4 = datafeed.query_bar_history(req4)
    if bars4 is None:
        print("正确处理了不支持的交易所，返回None")
    else:
        print("错误：应该返回None但没有")

if __name__ == "__main__":
    test_query_bar_history()