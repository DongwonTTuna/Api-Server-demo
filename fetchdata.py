import urllib.request, ssl, psycopg, json

ssl._create_default_https_context = ssl._create_unverified_context


class Fetched_Data:
    def __init__(self):
        self.urls = [
            "https://api.upbit.com/v1/candles/minutes/",
        ]

    def fetch_data(self, url: str):
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
            if url.find("gateio") != -1:
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

    def get_tickers(self, target):
        urls = {
            "UPBIT": "https://api.upbit.com/v1/market/all",
            "BINANCE": "https://api1.binance.com/api/v3/exchangeInfo",
            "FTX": "https://ftx.com/api/markets",
            "BITFLY": "https://api.bitflyer.com/v1/markets",
            "KUCOIN": "https://api.kucoin.com/api/v1/symbols",
            "GATEIO": "https://api.gateio.ws/api/v4/spot/currency_pairs",
            "HUOBI": "https://api.huobi.pro/v2/settings/common/symbols",
        }
        res = self.fetch_data(urls[target])
        self.update_tickers(target, res)

    def update_tickers(self, target, res):
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

    def fetch_start(self):
        need_to_update = []
        with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute("SELECT * FROM tickers")
                for record in cur.fetchall():
                    _, b, c = record
                    if c == None:
                        need_to_update.append(b)
        for update in need_to_update:
            self.get_tickers(update)


if __name__ == "__main__":
    Fetch = Fetched_Data()
    Fetch.fetch_start()
