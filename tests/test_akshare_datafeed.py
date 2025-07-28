import unittest

from vnpy_akshare.akshare_datafeed import to_ak_asset
from vnpy.trader.constant import Exchange


class TestToAkAsset(unittest.TestCase):
    # 股票
    def test_stock(self) -> None:
        self.assertEqual(to_ak_asset('600009', Exchange.SSE), "stock")  # 沪市
        self.assertEqual(to_ak_asset('688981', Exchange.SSE), "stock")  # 科创版
        self.assertEqual(to_ak_asset('000001', Exchange.SZSE), "stock")  # 深市
        self.assertEqual(to_ak_asset('300308', Exchange.SZSE), "stock")  # 创业板
        self.assertEqual(to_ak_asset('430418', Exchange.BSE), "stock")  # 北交所
        self.assertEqual(to_ak_asset('835305', Exchange.BSE), "stock")  # 北交所

    # 指数
    def test_index(self) -> None:
        self.assertEqual(to_ak_asset('000001', Exchange.SSE), "index")  # 上证指数
        self.assertEqual(to_ak_asset('000688', Exchange.SSE), "index")  # 科创版指
        self.assertEqual(to_ak_asset('399001', Exchange.SZSE), "index")  # 深证指数
        self.assertEqual(to_ak_asset('399006', Exchange.SZSE), "index")  # 创业板指
        self.assertEqual(to_ak_asset('899050', Exchange.BSE), "index")  # 北交所50

    # 基金
    def test_fund(self) -> None:
        self.assertEqual(to_ak_asset('159934', Exchange.SZSE), "fund")  # 深市etf
        self.assertEqual(to_ak_asset('518880', Exchange.SSE), "fund")  # 沪市etf

    # 期货
    def test_future(self) -> None:
        self.assertEqual(to_ak_asset('i2409', Exchange.CFFEX), "futures")


if __name__ == '__main__':
    unittest.main()