import aiohttp, ssl, asyncio, nest_asyncio, datetime, time, io, csv
from aioexec import Procs, Call
import psycopg2 as psycopg

nest_asyncio.apply()
ssl._create_default_https_context = ssl._create_unverified_context


async def fetch_request(url: str):
    def set_header(url: str):
        if url.find("gateio") != -1:
            return {"Accept": "application/json", "Content-Type": "application/json"}
        elif (
            url.find("mexc") != -1 or url.find("bybit") != -1 or url.find("upbit") != -1
        ):
            return {"Content-Type": "application/json"}
        else:
            return None

    header = set_header(url)
    while True:
        try:
            async with aiohttp.ClientSession(headers=header) as session:
                async with session.get(url) as res:
                    try:
                        return await res.json()
                    except:
                        return await res.read()
        except:
            continue


class GET_TICKERS:
    async def get_tickers(self, target: str):
        urls = {
            "UPBIT": "https://api.upbit.com/v1/market/all",
            "BYBIT": "https://api.bybit.com/v2/public/symbols",
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
        if target == "BYBIT":
            market_list = [a["name"] for a in res["result"]]
        elif target == "UPBIT":
            market_list = [a["market"] for a in res]
            market_list = list(filter(lambda x: x.find("KRW") != -1, market_list))
        elif target == "BINANCE":
            market_list = [a["symbol"] for a in res["symbols"]]
            market_list = list(
                filter(
                    lambda x: x.find("USDT") != -1 and x.find("USD") > 1, market_list
                )
            )
        elif target == "FTX":
            market_list = [a["name"] for a in res["result"]]
            market_list = list(
                filter(
                    lambda x: (x.find("USDT") != -1 or x.find("USD") != -1)
                    and x.find("USD") > 1,
                    market_list,
                )
            )
        elif target == "MEXC":
            market_list = [a["symbol"] for a in res["symbols"]]
            market_list = list(
                filter(
                    lambda x: x.find("USDT") != -1
                    and (
                        x.find("2S") == -1
                        and x.find("2L") == -1
                        and x.find("3L") == -1
                        and x.find("3S") == -1
                        and x.find("4S") == -1
                        and x.find("4L") == -1
                        and x.find("5S") == -1
                        and x.find("5L") == -1
                        and x.find("USD") > 1
                    ),
                    market_list,
                )
            )
        elif target == "KUCOIN":
            market_list = [a["symbol"] for a in res["data"]]
            market_list = list(
                filter(
                    lambda x: x.find("USDT") != -1 and x.find("USD") > 1, market_list
                )
            )
        elif target == "GATEIO":
            market_list = [a["id"] for a in res]
            market_list = list(
                filter(
                    lambda x: x.find("USDT") != -1 and x.find("USD") > 1, market_list
                )
            )
        elif target == "HUOBI":
            market_list = [a["bc"] + a["qc"] for a in res["data"]]
            market_list = list(
                filter(
                    lambda x: x.find("usdt") != -1 and x.find("usd") > 1, market_list
                )
            )
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


class GET_CHART:
    def __init__(self, exchange):
        url = {
            "UPBIT": "https://api.upbit.com/v1/candles/minutes/60?market=",
            "BYBIT": "https://api.bybit.com/v2/public/kline/list?symbol=",
            "BINANCE": "https://api.binance.com/api/v3/uiKlines?symbol=",
            "FTX": "https://ftx.com/api/markets/",
            "MEXC": "https://api.mexc.com/api/v3/klines?symbol=",
            "KUCOIN": "https://api.kucoin.com/api/v1/market/candles?type=1hour&symbol=",
            "GATEIO": "https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair=",
            "HUOBI": "https://api.huobi.pro/market/history/kline?period=60min&size=1000&symbol=",
        }
        self.exchange = exchange
        self.baseurl = url[exchange]
        self.basedata = []
        self.tickers = []
        self.targetdb = []

    def insert(self):
        with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute(
                    f"DELETE FROM cdata.{self.exchange.lower()}data",
                )
                post.commit()
                buf = io.StringIO()
                writer = csv.writer(buf)
                writer.writerows(self.targetdb)
                buf.seek(0)
                cur.copy_expert(
                    f"COPY cdata.{self.exchange.lower()}data FROM stdin DELIMITER ',' CSV",
                    file=buf,
                )
                post.commit()

    def get_tickers(self):
        with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute("SELECT * FROM getTicker(%s)", (self.exchange,))
                self.tickers = cur.fetchall()[0][0]

    def sumurls(self):
        if self.exchange == "BYBIT":
            self.basedata = [
                {
                    "url": f"{self.baseurl}{ticker}&interval=60&from={int(datetime.datetime.now().timestamp()) - 3600*1000}",
                    "ticker": ticker,
                }
                for ticker in self.tickers
            ]
        elif self.exchange == "UPBIT":
            self.basedata = [
                {
                    "url": f"{self.baseurl}{ticker}&count=200",
                }
                for ticker in self.tickers
            ]
        elif self.exchange == "BINANCE":
            self.basedata = [
                {
                    "url": f"{self.baseurl}{ticker}&interval=1h&limit=1000",
                    "ticker": ticker,
                }
                for ticker in self.tickers
            ]
        elif self.exchange == "HUOBI":
            self.basedata = [
                {"url": f"{self.baseurl}{ticker}", "ticker": ticker}
                for ticker in self.tickers
            ]
        elif self.exchange == "GATEIO":
            self.basedata = [
                {
                    "url": f"{self.baseurl}{ticker}&limit=1000&interval=1h",
                    "ticker": ticker,
                }
                for ticker in self.tickers
            ]
        elif self.exchange == "KUCOIN":
            self.basedata = [
                {
                    "url": f"{self.baseurl}{ticker}&startAt={int(datetime.datetime.now().timestamp()) - 3600*1000}&endAt{int(datetime.datetime.now().timestamp())}",
                    "ticker": ticker,
                }
                for ticker in self.tickers
            ]
        elif self.exchange == "MEXC":
            self.basedata = [
                {
                    "url": f"{self.baseurl}{ticker}&interval=60m&limit=1000",
                    "ticker": ticker,
                }
                for ticker in self.tickers
            ]
        elif self.exchange == "FTX":
            self.basedata = [
                {
                    "url": f"{self.baseurl}{ticker}/candles?resolution=3600&start_time={int(datetime.datetime.now().timestamp()) - 3600*1000}&end_time={int(datetime.datetime.now().timestamp())}",
                    "ticker": ticker,
                }
                for ticker in self.tickers
            ]

    async def RefetchData(self, lst):
        for num in lst:
            self.basedata[num]["data"] = ""
        res = await asyncio.gather(
            *[fetch_request(self.basedata[num]["url"]) for num in lst]
        )
        for n, num in enumerate(lst):
            self.basedata[num]["data"] = res[n]

    async def fetchDataFromTheUrl(self):
        res = await asyncio.gather(
            *[fetch_request(url["url"]) for url in self.basedata]
        )
        for n, dta in enumerate(res):
            self.basedata[n]["data"] = dta

        if self.exchange == "MEXC":
            while True:
                lst = []
                for num, data in enumerate(self.basedata):
                    if type(data["data"]) == dict:
                        lst.append(num)
                if lst == []:
                    break
                await asyncio.sleep(2)
                await self.RefetchData(lst)
        elif self.exchange == "KUCOIN":
            while True:
                lst = []
                for num, data in enumerate(self.basedata):
                    try:
                        if type(data["data"]) != bytes and data["data"]["data"] == []:
                            del self.basedata[num]
                            continue
                    except:
                        pass
                    if type(data["data"]) == bytes or data["data"]["code"] == "429000":
                        lst.append(num)
                if lst == []:
                    break
                await asyncio.sleep(2)
                await self.RefetchData(lst)
        elif self.exchange == "UPBIT":
            while True:
                lst = []
                for num, data in enumerate(self.basedata):
                    if type(data["data"]) == bytes:
                        lst.append(num)
                if lst == []:
                    break
                await asyncio.sleep(1)
                await self.RefetchData(lst)
        elif self.exchange == "BYBIT":
            while True:
                lst = []
                for num, data in enumerate(self.basedata):
                    if data["data"]["ret_code"] != 0:
                        lst.append(num)
                    if lst == []:
                        break
                    await asyncio.sleep(1)
                    await self.RefetchData(lst)

    def processing_Data(self):
        if self.exchange == "BYBIT":
            for db in self.basedata:
                for a in db["data"]["result"]:
                    self.targetdb.append(
                        [
                            a["symbol"]
                            .upper()
                            .replace("-", "")
                            .replace("_", "")
                            .replace("/", ""),
                            a["open_time"],
                            a["open"],
                            a["close"],
                            a["low"],
                            a["high"],
                            a["volume"],
                        ]
                    )
            self.insert()
        elif self.exchange == "BINANCE":
            for db in self.basedata:
                for a in db["data"]:
                    self.targetdb.append(
                        # oclh
                        [
                            db["ticker"]
                            .upper()
                            .replace("-", "")
                            .replace("_", "")
                            .replace("/", ""),
                            int("".join([*str(a[0])][0:10])),
                            float(a[1]),
                            float(a[4]),
                            float(a[3]),
                            float(a[2]),
                            float(a[5]) * float(a[4]),
                        ]
                    )
            self.insert()
        elif self.exchange == "UPBIT":
            for db in self.basedata:
                for a in db["data"]:
                    self.targetdb.append(
                        [
                            a["market"]
                            .upper()
                            .replace("-", "")
                            .replace("_", "")
                            .replace("/", ""),
                            int("".join([*str(a["timestamp"])][0:10])),
                            a["opening_price"],
                            a["trade_price"],
                            a["low_price"],
                            a["high_price"],
                            a["candle_acc_trade_price"],
                        ]
                    )
            self.insert()
        elif self.exchange == "FTX":
            for db in self.basedata:
                for each in db["data"]["result"]:
                    self.targetdb.append(
                        [
                            db["ticker"]
                            .upper()
                            .replace("-", "")
                            .replace("_", "")
                            .replace("/", ""),
                            "".join(
                                [
                                    *str(
                                        datetime.datetime.fromisoformat(
                                            each["startTime"]
                                        ).timestamp()
                                    )
                                ][0:10]
                            ),
                            float(each["open"]),
                            float(each["close"]),
                            float(each["low"]),
                            float(each["high"]),
                            float(each["volume"]),
                        ]
                    )
            self.insert()
        elif self.exchange == "MEXC":
            for db in self.basedata:
                for a in db["data"]:
                    self.targetdb.append(
                        [
                            db["ticker"]
                            .upper()
                            .replace("-", "")
                            .replace("_", "")
                            .replace("/", ""),
                            "".join([*str(a[0])][0:10]),
                            float(a[1]),
                            float(a[4]),
                            float(a[3]),
                            float(a[2]),
                            float(a[5]) * float(a[4]),
                        ]
                    )
            self.insert()
        elif self.exchange == "KUCOIN":
            for db in self.basedata:
                for a in db["data"]["data"]:
                    self.targetdb.append(
                        [
                            db["ticker"]
                            .upper()
                            .replace("-", "")
                            .replace("_", "")
                            .replace("/", ""),
                            "".join([*str(a[0])][0:10]),
                            float(a[1]),
                            float(a[2]),
                            float(a[4]),
                            float(a[3]),
                            float(a[5]) * float(a[2]),
                        ]
                    )
            self.insert()
        elif self.exchange == "GATEIO":
            for db in self.basedata:
                for a in db["data"]:
                    self.targetdb.append(
                        [
                            db["ticker"]
                            .upper()
                            .replace("-", "")
                            .replace("_", "")
                            .replace("/", ""),
                            "".join([*str(a[0])][0:10]),
                            float(a[5]),
                            float(a[2]),
                            float(a[4]),
                            float(a[3]),
                            float(a[1]),
                        ]
                    )
            self.insert()
        elif self.exchange == "HUOBI":
            for db in self.basedata:
                try:
                    for a in db["data"]["data"]:
                        self.targetdb.append(
                            [
                                db["ticker"]
                                .upper()
                                .replace("-", "")
                                .replace("_", "")
                                .replace("/", ""),
                                "".join([*str(a["id"])][0:10]),
                                float(a["open"]),
                                float(a["close"]),
                                float(a["low"]),
                                float(a["high"]),
                                float(a["vol"]),
                            ]
                        )
                except:
                    continue
            self.insert()

    async def main(self):
        print(self.exchange)
        while True:
            try:
                self.get_tickers()
                self.sumurls()
                await self.fetchDataFromTheUrl()
                self.processing_Data()
                break
            except:
                self.basedata = []
                self.tickers = []
                self.targetdb = []
                continue
        print(self.exchange)


loop = asyncio.get_event_loop()


def startchart(exchange):
    asyncio.new_event_loop().run_until_complete(GET_CHART(exchange).main())


def initiate_ticker():
    get_tickers = GET_TICKERS()
    future = asyncio.ensure_future(get_tickers.ticker_start())
    loop.run_until_complete(future)


async def initiate_chart():
    tempexc = [
        "BYBIT",
        "MEXC",
        "UPBIT",
        "KUCOIN",
        "HUOBI",
        
        "BINANCE",
        "FTX",
    ]
    exchange = [
        "GATEIO",
    ]
    await asyncio.gather(
        *Procs(10).batch(Call(startchart, exchange=exc) for exc in exchange)
    )


if __name__ == "__main__":
    while True:
        start = time.time()
        with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute("SELECT tstamp FROM TSTAMP WHERE exnum = 1")
                a = cur.fetchall()[0][0]
                cur.execute("SELECT tstamp FROM TSTAMP WHERE exnum = 2")
                b = cur.fetchall()[0][0]
                if a == None or int(a) <= (
                    int(datetime.datetime.now().timestamp()) - 10800
                ):
                    initiate_ticker()
                    cur.execute(
                        "UPDATE TSTAMP SET tstamp = %s WHERE exnum = 1",
                        (int(datetime.datetime.now().timestamp()),),
                    )
                    post.commit()
                if b == None or int(b) <= (
                    int(datetime.datetime.now().timestamp()) - 600
                ):
                    asyncio.run(initiate_chart())
                    cur.execute(
                        "UPDATE TSTAMP SET tstamp = %s WHERE exnum = 2",
                        (int(datetime.datetime.now().timestamp()),),
                    )
                    post.commit()
        print("Done!" + "\n\nTotal runtime: ", time.time() - start)
        time.sleep(5)
