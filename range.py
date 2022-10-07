import asyncio, aiohttp, psycopg



gateiourl = "https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair={targetCurrency}&interval=1h"
kucoin = ""
bitfly = ""
ftx = "https://ftx.com/api/markets"
mexc = "https://api.mexc.com/api/v3/klines?symbol={ticker}&interval=1h&limit=1000"
async def fetchData(url):
    header = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            return await res.json()
    
async def main():
    
    
    
    res = await fetchData("https://ftx.com/api/markets/BTC/USD/candles?resolution=3600")
    print(res)
    #for data in res["data"]:
    #    d = data["bc"]+data["qc"]
    #    print(d)
    #res = await fetchData("https://api.huobi.pro/market/history/kline?period=60min&size=2000&symbol=HIVE/USDT")
    #print(res)
    
    
    tickers = []
    #with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
    #    with post.cursor() as cur:
    #cur.execute("SELECT * FROM getTicker(%s)", ('MEXC',))
    #        tickers= cur.fetchall()[0][0]
   
    #for ticker in tickers:
    #    url = f"https://api.mexc.com/api/v3/klines?symbol={ticker}&interval=1h&limit=1000"
    #    res = await fetchData(url)
    #    print(res)
    
    
    
asyncio.run(main())
    
    
    
    