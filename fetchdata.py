import aiohttp, ssl, psycopg, asyncio
from aioexec import Procs, Call

ssl._create_default_https_context = ssl._create_unverified_context


async def fetch_request(url: str):
    def set_header(url: str):
        if url.find("bithumb") != -1:
            return {"accept": "application/json"}
        elif url.find("gateio") != -1:
            return {"Accept": "application/json", "Content-Type": "application/json"}
        elif url.find('mexc') != -1:
            return {"Content-Type": "application/json"}
        else:
            return None

    header = set_header(url)
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(url) as res:
            try:
                return await res.json()
            except:
                return await res.read()


class GET_TICKERS:
    async def get_tickers(self, target: str):
        urls = {
            "BITHUMB": "https://api.bithumb.com/public/ticker/ALL_KRW",
            "BINANCE": "https://api1.binance.com/api/v3/exchangeInfo",
            "FTX": "https://ftx.com/api/markets",
            "MEXC": "https://api.mexc.com/api/v3/exchangeInfo",
            "KUCOIN": "https://api.kucoin.com/api/v1/symbols",
            "GATEIO": "https://api.gateio.ws/api/v4/spot/currency_pairs",
            "HUOBI": "https://api.huobi.pro/v2/settings/common/symbols",
        }
        res = await fetch_request(urls[target])
        self.update_tickers(target, res)

    def update_tickers(self, target: str, res):
        if target == "BITHUMB":
            market_list = [a for a in res["data"]][:-1]
        elif target == "BINANCE":
            market_list = [a["symbol"] for a in res["symbols"]]
            market_list = list(filter(lambda x: x.find("USDT") != -1, market_list))
        elif target == "FTX":
            market_list = [a["name"] for a in res["result"]]
            market_list = list(
                filter(
                    lambda x: x.find("USDT") != -1 or x.find("USD") != -1, market_list
                )
            )
        elif target == "MEXC":
            market_list = [a["symbol"] for a in res["symbols"]]
        elif target == "KUCOIN":
            market_list = [a["symbol"] for a in res["data"]]
            market_list = list(filter(lambda x: x.find("USDT") != -1, market_list))
        elif target == "GATEIO":
            market_list = [a["id"] for a in res]
            market_list = list(filter(lambda x: x.find("USDT") != -1, market_list))
        elif target == "HUOBI":
            market_list = [a["bc"]+a["qc"] for a in res["data"]]
            market_list = list(filter(lambda x: x.find("usdt") != -1, market_list))
        else:
            return
        with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute("CALL updTicker(%s, %s)", (market_list, target))
                post.commit()

    async def ticker_start(self):
        need_to_update = []
        with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute("SELECT * FROM TICKERS")
                for record in cur.fetchall():
                    a, _ = record
                    need_to_update.append(a)
        await asyncio.gather(*[self.get_tickers(update) for update in need_to_update])


def insert():
    db = []
    with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
        with post.cursor() as cur:
            cur.execute(
                "DELETE FROM CHARTDATA",
            )
            post.commit()
            for args in db:
                print(
                    args[0],
                    args[1],
                    args[2],
                    args[3],
                    args[4],
                    args[5],
                    args[6],
                    args[7],
                    args[8],
                )
                cur.execute(
                    "INSERT INTO CHARTDATA (exchange, ticker, tstamp, OPEN, CLOSE, low, high, vol, count) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        args[0],
                        args[1],
                        args[2],
                        args[3],
                        args[4],
                        args[5],
                        args[6],
                        args[7],
                        args[8],
                    ),
                )


class GET_CHART:
    def __init__(self, exchange):
        self.exchange = exchange["exchange"]
        self.baseurl = exchange["url"]
        self.urls = []
        self.tickers = []

    def get_tickers(self):
        with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute("SELECT * FROM getTicker(%s)", (self.exchange,))
                self.tickers = cur.fetchall()[0][0]

    def sumurls(self):
        if self.exchange == "BITHUMB":
            self.urls = [f"{self.baseurl}{ticker}_KRW/1h" for ticker in self.tickers]
        elif self.exchange == "BINANCE":
            self.urls = [
                f"{self.baseurl}{ticker}&interval=1h&limit=1000"
                for ticker in self.tickers
            ]
        elif self.exchange == 'HUOBI':
            self.urls = [
                f"{self.baseurl}{ticker}"
                for ticker in self.tickers
            ]
        elif self.exchange == 'GATEIO':
            self.urls = [
                f"{self.baseurl}{ticker}&interval=1h"
                for ticker in self.tickers
            ]
        elif self.exchange == 'KUCOIN':
            self.urls = [
                f"{self.baseurl}{ticker}"
                for ticker in self.tickers
            ]
        elif self.exchange == 'MEXC':
            self.urls = [
                f"{self.baseurl}{ticker}&interval=1h&limit=1000"
                for ticker in self.tickers
            ]
        elif self.exchange == 'FTX':
            self.urls = [
                f"{self.baseurl}{ticker}/candles?resolution=3600"
                for ticker in self.tickers
            ]

    async def fetchDataFromTheUrl(self):
        res = []
        """
        if self.exchange == "BITHUMB":
            for i in range(30, len(self.urls), 30):
                res.append(
                    await asyncio.gather(
                        *[fetch_request(url) for url in self.urls[i - 30 : i]]
                    )
                )
                await asyncio.sleep(1)
                if i + 30 > len(self.urls):
                    temp = len(self.urls)
                    res.append(
                        await asyncio.gather(
                            *[fetch_request(url) for url in self.urls[i:temp]]
                        )
                    )
        else:

        """
        res = await asyncio.gather(*[fetch_request(url) for url in self.urls])
        return res

    async def main(self):
        self.get_tickers()
        self.sumurls()
        res = await self.fetchDataFromTheUrl()
        with open("./result.txt", "a") as f:
            f.write(str(res))


loop = asyncio.get_event_loop()


def initiate_ticker():
    get_tickers = GET_TICKERS()
    future = asyncio.ensure_future(get_tickers.ticker_start())
    loop.run_until_complete(future)


async def initiate_chart():
    infos = [
        {
            "exchange": "BITHUMB",
            "url": "https://api.bithumb.com/public/candlestick/",
        },
        {
            "exchange": "BINANCE",
            "url": "https://api.binance.com/api/v3/uiKlines?symbol=",
        },
        {"exchange": "FTX", "url": "https://ftx.com/api/markets/"},
        {
            "exchange": "MEXC",
            "url": "https://api.mexc.com/api/v3/klines?symbol=",
        },
        {
            "exchange": "KUCOIN",
            "url": "https://api.kucoin.com/api/v1/market/candles?type=1hour&symbol=",
        },
        {
            "exchange": "GATEIO",
            "url": "https://api.gateio.ws/api/v4/spot/currency_pairs=",
        },
        {
            "exchange": "HUOBI",
            "url": "https://api.huobi.pro/v2/market/history/kline?period=60min&size=2000&symbol=",
        },
    ]
    classes = [GET_CHART(info) for info in infos]
    await asyncio.gather(
        *Procs(10).batch(*[Call(await clas.main()) for clas in classes])
    )


def start():
    initiate_ticker()
    asyncio.run(initiate_chart())


if __name__ == "__main__":
    start()
