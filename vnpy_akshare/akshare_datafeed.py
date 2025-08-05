import akshare as ak
from datetime import timedelta, datetime
from collections.abc import Callable
from copy import deepcopy
import re

import pandas as pd
from pandas import DataFrame

from vnpy.trader.setting import SETTINGS
from vnpy.trader.datafeed import BaseDatafeed
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData, HistoryRequest
from vnpy.trader.utility import round_to, ZoneInfo

# 数据频率映射
INTERVAL_VT2AK: dict[Interval, str] = {
    Interval.MINUTE: "1m",
    Interval.HOUR: "60m",
    Interval.DAILY: "daily",
}

# 股票支持列表
STOCK_LIST: list[Exchange] = [
    Exchange.SSE,
    Exchange.SZSE,
    Exchange.BSE,
]

# 期货支持列表
FUTURE_LIST: list[Exchange] = [
    Exchange.CFFEX,
    Exchange.SHFE,
    Exchange.CZCE,
    Exchange.DCE,
    Exchange.INE,
    Exchange.GFEX
]

# 交易所映射
EXCHANGE_VT2AK: dict[Exchange, str] = {
    Exchange.CFFEX: "cffex",
    Exchange.SHFE: "shfe",
    Exchange.CZCE: "czce",
    Exchange.DCE: "dce",
    Exchange.INE: "ine",
    Exchange.SSE: "sh",
    Exchange.SZSE: "sz",
    Exchange.BSE: "bj",
    Exchange.GFEX: "gfex"
}

# 时间调整映射
INTERVAL_ADJUSTMENT_MAP: dict[Interval, timedelta] = {
    Interval.MINUTE: timedelta(minutes=1),
    Interval.HOUR: timedelta(hours=1),
    Interval.DAILY: timedelta()
}

# 中国上海时区
CHINA_TZ = ZoneInfo("Asia/Shanghai")

# 中文列名映射
COLUMN_MAP = {
    "日期": "date",
    "开盘": "open",
    "收盘": "close",
    "最高": "high",
    "最低": "low",
    "成交量": "volume",
    "成交额": "amount"
}


def to_ak_symbol(symbol: str, exchange: Exchange) -> str | None:
    """将交易所代码转换为akshare代码"""
    # 股票
    if exchange in STOCK_LIST:
        ak_symbol: str = symbol  # akshare直接使用股票代码，不需要添加交易所后缀
    # 期货
    elif exchange in FUTURE_LIST:
        ak_symbol = symbol
    else:
        return None

    return ak_symbol


def to_ak_asset(symbol: str, exchange: Exchange) -> str | None:
    """生成akshare资产类别"""
    # 股票
    if exchange in STOCK_LIST:
        if exchange is Exchange.SSE and symbol[0] == "6":
            asset: str = "stock"
        elif exchange is Exchange.SSE and symbol[0] == "5":
            asset = "fund"  # 场内etf
        elif exchange is Exchange.SZSE and symbol[0] == "1":
            asset = "fund"  # 场内etf
        # 39开头是指数，比如399001
        elif exchange is Exchange.SZSE and re.search("^(0|3)", symbol) and not symbol.startswith('39'):
            asset = "stock"
        # 89开头是指数，比如899050
        elif exchange is Exchange.BSE and not symbol.startswith('89'):
            asset = "stock"
        else:
            asset = "index"
    # 期货
    elif exchange in FUTURE_LIST:
        asset = "futures"
    else:
        return None

    return asset


class AkshareDatafeed(BaseDatafeed):
    """AkShare数据服务接口"""

    def __init__(self) -> None:
        """初始化"""
        self.inited: bool = False

    def init(self, output: Callable = print) -> bool:
        """初始化"""
        if self.inited:
            return True

        # AkShare不需要用户名密码，直接初始化
        self.inited = True
        return True

    def query_bar_history(self, req: HistoryRequest, output: Callable = print) -> list[BarData] | None:
        """查询k线数据"""
        if not self.inited:
            self.init(output)

        symbol: str = req.symbol
        exchange: Exchange = req.exchange
        interval: Interval = req.interval
        start: datetime = req.start
        end: datetime = req.end

        ak_symbol: str | None = to_ak_symbol(symbol, exchange)
        if not ak_symbol:
            return None

        asset: str | None = to_ak_asset(symbol, exchange)
        if not asset:
            return None

        ak_interval: str | None = INTERVAL_VT2AK.get(interval)
        if not ak_interval:
            return None

        adjustment: timedelta = INTERVAL_ADJUSTMENT_MAP[interval]

        try:
            # 根据资产类型调用不同的AkShare接口
            if asset == "stock":
                df: DataFrame = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period=ak_interval,
                    start_date=start.strftime("%Y%m%d"),
                    end_date=end.strftime("%Y%m%d"),
                    adjust=""
                )
            elif asset == "index":
                df: DataFrame = ak.index_zh_a_hist(
                    symbol=symbol,
                    period=ak_interval,
                    start_date=start.strftime("%Y%m%d"),
                    end_date=end.strftime("%Y%m%d")
                )
            elif asset == "fund":
                df: DataFrame = ak.fund_etf_hist_em(
                    symbol=symbol,
                    period=ak_interval,
                    start_date=start.strftime("%Y%m%d"),
                    end_date=end.strftime("%Y%m%d"),
                    adjust=""
                )
            elif asset == "futures":
                # 期货数据接口
                df: DataFrame = ak.futures_zh_daily_sina(symbol=symbol)
                # 过滤时间范围
                if not df.empty and 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    start_date = pd.to_datetime(start.date())
                    end_date = pd.to_datetime(end.date())
                    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            else:
                return None
        except Exception as ex:
            output(f"发生错误：{ex}")
            return []

        bar_dict: dict[datetime, BarData] = {}
        data: list[BarData] = []

        # 处理原始数据中的NaN值
        if df is not None and not df.empty:
            df.fillna(0, inplace=True)
            
            # 重命名列以匹配英文名称
            df.rename(columns=COLUMN_MAP, inplace=True)
            
            # 确保必要的列存在
            required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                output(f"数据格式不正确，缺少必要列: {df.columns.tolist()}")
                return []

            for _ix, row in df.iterrows():
                # 处理日期格式
                if 'date' in row:
                    dt_str: str = str(row["date"])
                    try:
                        if len(dt_str) == 8 and dt_str.isdigit():  # YYYYMMDD
                            dt = datetime.strptime(dt_str, "%Y%m%d")
                        elif len(dt_str) == 10:  # YYYY-MM-DD
                            dt = datetime.strptime(dt_str[:10], "%Y-%m-%d")
                        else:  # 其他格式尝试直接转换
                            dt = pd.to_datetime(dt_str).to_pydatetime()
                    except ValueError:
                        output(f"无法解析日期格式: {dt_str}")
                        continue
                else:
                    continue

                dt = dt.replace(tzinfo=CHINA_TZ)

                turnover = row.get("amount", row.get("volume", 0) * row.get("close", 0))
                if turnover is None:
                    turnover = 0

                open_interest = row.get("open_interest", 0)
                if open_interest is None:
                    open_interest = 0

                # 确保所有价格字段都存在
                open_price = row.get("open", 0)
                high_price = row.get("high", 0)
                low_price = row.get("low", 0)
                close_price = row.get("close", 0)
                volume = row.get("volume", row.get("vol", 0))

                bar: BarData = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    datetime=dt,
                    open_price=round_to(open_price, 0.000001),
                    high_price=round_to(high_price, 0.000001),
                    low_price=round_to(low_price, 0.000001),
                    close_price=round_to(close_price, 0.000001),
                    volume=volume*100,  # 成交量单位转换为股
                    turnover=turnover,
                    open_interest=open_interest,
                    gateway_name="AK"
                )

                bar_dict[dt] = bar

        bar_keys = sorted(bar_dict.keys(), reverse=False)
        for i in bar_keys:
            data.append(bar_dict[i])

        return data