import asyncio, aiohttp, psycopg, requests
from aioexec import Procs, Call


urls = [
    "https://api.bithumb.com/public/ticker/ALL_KRW",
    "https://api1.binance.com/api/v3/exchangeInfo",
    "https://ftx.com/api/markets",
    "https://api.mexc.com/api/v3/exchangeInfo",
    "https://api.kucoin.com/api/v1/symbols",
    "https://api.gateio.ws/api/v4/spot/currency_pairs",
    "https://api.huobi.pro/v2/settings/common/symbols",
]
exchange = [
    "BITHUMB",
    "BINANCE",
    "FTX",
    "MEXC",
    "KUCOIN",
    "GATEIO",
    "HUOBI",
]


async def fetchData(url):
    header = {"Accept": "application/json", "Content-Type": "application/json"}
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(url) as res:
            try:
                return await res.json()
            except:
                return await res.read()

async def fetchurls(exc):
    print(exc)
    await asyncio.gather(
        *[fetchData(url) for url in urls]
    )
    await asyncio.gather(
        *[fetchData(url) for url in urls]
    )
    await asyncio.gather(
        *[fetchData(url) for url in urls]
    )
    await asyncio.gather(
        *[fetchData(url) for url in urls]
    )
    await asyncio.gather(
        *[fetchData(url) for url in urls]
    )
    print(exc)


def initialize_data(exc):
    asyncio.new_event_loop().run_until_complete(fetchurls(exc))            
            


async def main():
    res = await asyncio.gather(*Procs(10).batch(Call(initialize_data, exc=exc) for exc in exchange))
    print(res)
    
    
    
    # for data in res["data"]:
    #    d = data["bc"]+data["qc"]
    #    print(d)
    # res = await fetchData("https://api.huobi.pro/market/history/kline?period=60min&size=2000&symbol=HIVE/USDT")
    # print(res)

    tickers = []
    # with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
    #    with post.cursor() as cur:
    # cur.execute("SELECT * FROM getTicker(%s)", ('MEXC',))
    #        tickers= cur.fetchall()[0][0]

    # for ticker in tickers:
    #    url = f"https://api.mexc.com/api/v3/klines?symbol={ticker}&interval=1h&limit=1000"
    #    res = await fetchData(url)
    #    print(res)


if __name__ == "__main__":
    asyncio.run(main())
