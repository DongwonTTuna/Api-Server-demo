import aiohttp, ssl, psycopg, asyncio, nest_asyncio, datetime
from aioexec import Procs, Call

nest_asyncio.apply()
semaphore = asyncio.Semaphore(200)
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
    async with semaphore:
        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(url) as res:
                try:
                    return await res.json()
                except:
                    return await res.read()


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
                    ),
                    market_list,
                )
            )
        elif target == "KUCOIN":
            market_list = [a["symbol"] for a in res["data"]]
            market_list = list(filter(lambda x: x.find("USDT") != -1, market_list))
        elif target == "GATEIO":
            market_list = [a["id"] for a in res]
            market_list = list(filter(lambda x: x.find("USDT") != -1, market_list))
        elif target == "HUOBI":
            market_list = [a["bc"] + a["qc"] for a in res["data"]]
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


class GET_CHART:
    def __init__(self, exchange):
        url = {
            "UPBIT": "https://api.upbit.com/v1/candles/minutes/60?market=",
            "BYBIT": "https://api.bybit.com/v2/public/kline/list?symbol=",
            "BINANCE": "https://api.binance.com/api/v3/uiKlines?symbol=",
            "FTX": "https://ftx.com/api/markets/",
            "MEXC": "https://api.mexc.com/api/v3/klines?symbol=",
            "KUCOIN": "https://api.kucoin.com/api/v1/market/candles?type=1hour&symbol=",
            "GATEIO": "https://api.gateio.ws/api/v4/spot/currency_pairs=",
            "HUOBI": "https://api.huobi.pro/v2/market/history/kline?period=60min&size=2000&symbol=",
        }

        self.exchange = exchange
        self.baseurl = url[exchange]
        self.basedata = []
        self.tickers = []
        self.targetdb = []

    def insert(self):
        with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                Flag = True
                CurrentTicker = ""
                for args in self.targetdb:
                    if CurrentTicker != args[1]:
                        Flag = True
                    if Flag == True and CurrentTicker != args[1]:
                        cur.execute(
                            "DELETE FROM CHARTDATA WHERE (exchange,ticker) = (%s,%s)",
                            (self.exchange, args[1]),
                        )
                        post.commit()
                        Flag = False
                        CurrentTicker = args[1]
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

    def get_tickers(self):
        with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute("SELECT * FROM getTicker(%s)", (self.exchange,))
                self.tickers = cur.fetchall()[0][0]

    def sumurls(self):
        if self.exchange == "BYBIT":
            self.basedata = [
                {
                    "url": f"{self.baseurl}{ticker}&interval=60&from={round(datetime.datetime.now().timestamp()) - 3600*200}",
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
                    "url": f"{self.baseurl}{ticker}&interval=1h&limit=200",
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
                {"url": f"{self.baseurl}{ticker}&interval=1h", "ticker": ticker}
                for ticker in self.tickers
            ]
        elif self.exchange == "KUCOIN":
            self.basedata = [
                {"url": f"{self.baseurl}{ticker}" , "ticker": ticker} for ticker in self.tickers
            ]
        elif self.exchange == "MEXC":
            self.basedata = [
                {
                    "url": f"{self.baseurl}{ticker}&interval=60m&limit=200",
                    "ticker": ticker,
                }
                for ticker in self.tickers
            ]
        elif self.exchange == "FTX":
            self.basedata = [
                {
                    "url": f"{self.baseurl}{ticker}/candles?resolution=3600&start_time={round(datetime.datetime.now().timestamp()) - 3600*200}",
                    "ticker": ticker,
                }
                for ticker in self.tickers
            ]

    async def RefetchData(self, lst):
        for num in lst:
            self.basedata[num]["data"] = ""
        print(len(lst))
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

        print("succes")

    def processing_Data(self):
        if self.exchange == "BYBIT":
            for db in self.basedata:
                print(db)
                for n, a in enumerate(db["data"]["result"]):
                    # (exchange, ticker, tstamp, OPEN, CLOSE, low, high, vol, count)]
                    self.targetdb.append(
                        [
                            self.exchange,
                            a["symbol"],
                            a["open_time"],
                            a["open"],
                            a["close"],
                            a["low"],
                            a["high"],
                            a["volume"],
                            n,
                        ]
                    )
            self.insert()
        elif self.exchange == "BINANCE":
            for db in self.basedata:
                for num, a in enumerate(db["data"]):
                    self.targetdb.append(
                        [
                            self.exchange,
                            db["ticker"],
                            a[0],
                            a[4],
                            a[3],
                            a[2],
                            a[4],
                            a[5],
                            num,
                        ]
                    )
            self.insert()
        elif self.exchange == "UPBIT":
            for db in self.basedata:
                for num, a in enumerate(db["data"]):
                    self.targetdb.append(
                        [
                            self.exchange,
                            a["market"],
                            a["timestamp"],
                            a["opening_price"],
                            a["trade_price"],
                            a["low_price"],
                            a["high_price"],
                            a["candle_acc_trade_volume"],
                            num,
                        ]
                    )
            self.insert()
        elif self.exchange == "FTX":
            for db in self.basedata:
                for num, each in enumerate(db["data"]["result"]):
                    self.targetdb.append(
                        [
                            self.exchange,
                            db["ticker"],
                            round(
                                datetime.datetime.fromisoformat(
                                    each["startTime"]
                                ).timestamp()
                            ),
                            each["open"],
                            each["close"],
                            each["low"],
                            each["high"],
                            each["volume"],
                            num,
                        ]
                    )
            self.insert()
        elif self.exchange == "MEXC":
            for db in self.basedata:
                for num, a in enumerate(db["data"]):
                    # (exchange, ticker, tstamp, OPEN, CLOSE, low, high, vol, count)]
                    self.targetdb.append(
                        [
                            self.exchange,
                            db["ticker"],
                            a[0],
                            a[1],
                            a[4],
                            a[3],
                            a[2],
                            a[5],
                            num,
                        ]
                    )
            self.insert()
        elif self.exchange == "KUCOIN":
            for db in self.basedata:
                for a in db["data"]:
                    self.targetdb.append(
                        [
                            self.exchange,
                            db["ticker"],
                            a[0],
                            a[1],
                            a[2],
                            a[4],
                            a[3],
                            a[5],
                            num,
                        ]
                    )
        elif self.exchange == "GATEIO":
            print("GATEIO")
            print(self.db[0])
        elif self.exchange == "HUOBI":
            print("HUOBI")
            print(self.db[0])

    async def main(self):
        print(self.exchange)
        self.get_tickers()
        self.sumurls()
        await self.fetchDataFromTheUrl()
        with open("./result.txt", "w") as f:
            for data in self.basedata:
                f.write(str(data) + "\n")
        self.processing_Data()
        print(self.exchange)


loop = asyncio.get_event_loop()


def startchart(exchange):
    asyncio.new_event_loop().run_until_complete(GET_CHART(exchange).main())


def initiate_ticker():
    get_tickers = GET_TICKERS()
    future = asyncio.ensure_future(get_tickers.ticker_start())
    loop.run_until_complete(future)


async def initiate_chart():
    doneexc = [
        "UPBIT",
        "MEXC",
        "FTX",
        "BINANCE",
    ]
    tempexc = [
        "BYBIT",
        "GATEIO",
        "HUOBI",
    ]
    exchange = ["KUCOIN",]
    await asyncio.gather(
        *Procs(10).batch(Call(startchart, exchange=exc) for exc in exchange)
    )


if __name__ == "__main__":
    initiate_ticker()
    asyncio.run(initiate_chart())
