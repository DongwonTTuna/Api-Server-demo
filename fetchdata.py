import urllib.request, ssl, psycopg, json, time

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_request(url: str):
    def create_request(url, header):
        req = urllib.request.Request(url)
        if header == None:
            return req
        for head in header:
            for head_h in head:
                req.add_header(head_h, head[head_h])
        return req

    def set_header(url: str):
        if url.find("upbit") != -1:
            return [{"accept": "application/json"}]
        elif url.find("gateio") != -1:
            return [
                {"Accept": "application/json"},
                {"Content-Type": "application/json"},
            ]
        else:
            return None

    header = set_header(url)
    req = create_request(url, header)
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        return data


class GET_TICKERS:
    def get_tickers(self, target: str):
        urls = {
            "UPBIT": "https://api.upbit.com/v1/market/all",
            "BINANCE": "https://api1.binance.com/api/v3/exchangeInfo",
            "FTX": "https://ftx.com/api/markets",
            "BITFLY": "https://api.bitflyer.com/v1/markets",
            "KUCOIN": "https://api.kucoin.com/api/v1/symbols",
            "GATEIO": "https://api.gateio.ws/api/v4/spot/currency_pairs",
            "HUOBI": "https://api.huobi.pro/v2/settings/common/symbols",
        }
        res = fetch_request(urls[target])
        self.update_tickers(target, res)

    def update_tickers(self, target: str, res):
        market_list = []
        if target == "UPBIT":
            for market in res:
                market_list.append(market["market"])
        elif target == "BINANCE":
            for market in res["symbols"]:
                market_list.append(market["symbol"])
        elif target == "FTX":
            for market in res["result"]:
                market_list.append(market["name"])
        elif target == "BITFLY":
            for market in res:
                market_list.append(market["product_code"])
        elif target == "KUCOIN":
            for market in res["data"]:
                market_list.append(market["symbol"])
        elif target == "GATEIO":
            for market in res:
                market_list.append(market["id"])
        elif target == "HUOBI":
            for market in res["data"]:
                market_list.append(market["dn"])
        if market_list == []:
            market_list = None
        with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute("CALL updTicker(%s, %s)", (market_list, target))
                post.commit()

    def ticker_start(self):
        need_to_update = []
        with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute("SELECT * FROM TICKERS")
                for record in cur.fetchall():
                    _, b, c = record
                    if c == None:
                        need_to_update.append(b)
        for update in need_to_update:
            self.get_tickers(update)


class GET_CHART:
    def __init__(self):
        self.tickers = []

    def initialize_variables(self):
        self.tickers = []

    def getChart(self, target: str, tickers: list):
        urls = {
            "UPBIT": "https://api.upbit.com/v1/candles/minutes/15?market=",
            "BINANCE": "https://api1.binance.com/api/v3/exchangeInfo",
            "FTX": "https://ftx.com/api/markets",
            "BITFLY": "https://api.bitflyer.com/v1/markets",
            "KUCOIN": "https://api.kucoin.com/api/v1/symbols",
            "GATEIO": "https://api.gateio.ws/api/v4/spot/currency_pairs",
            "HUOBI": "https://api.huobi.pro/v2/settings/common/symbols",
        }
        if target == "UPBIT":
            with psycopg.connect(
                "dbname=API_SERVER user=postgres password=0790"
            ) as post:
                with post.cursor() as cur:
                    for market in tickers:
                        data.append(
                            json.dumps(
                                fetch_request(urls[target] + market + "&count=200")
                            )
                        )
                    cur.execute("CALL updChart(%s,%s)", (data, target))

    def start_get(self):
        with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute("SELECT exchange FROM TICKERS")
                for exc in cur.fetchall():
                    cur.execute("SELECT * FROM getTicker(%s)", (exc[0],))
                    self.getChart(exc[0], cur.fetchall()[0][0])


class Fetch_Data:
    def start(self):
        get_tickers = GET_TICKERS()
        get_chart = GET_CHART()
        get_tickers.ticker_start()
        get_chart.start_get()


if __name__ == "__main__":
    Fetch = Fetch_Data()
    Fetch.start()
