import asyncio, ssl
import aiohttp,datetime

semaphore = asyncio.Semaphore(200)
ssl._create_default_https_context = ssl._create_unverified_context
async def fetch_request(url: str):
    def set_header(url: str):
        if url.find("gateio") != -1:
            return {"Accept": "application/json", "Content-Type": "application/json"}
        elif url.find("mexc") != -1 or url.find('bybit') != -1:
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

tstamp = round(datetime.datetime.now().timestamp()) - 3600*200
async def bitmain():
    url = "https://api.bybit.com/v2/public/symbols"
    res = await fetch_request(url)
    print(res)
    for r in res["result"]:
        symbol = r["name"]
        #print(symbol)
        url = f"https://api.bybit.com/v2/public/kline/list?symbol={symbol}&interval=60&from={tstamp}"
        r = await fetch_request(url)
        for n,a in enumerate(r["result"]):
            print(n, a["close"])
async def main():
    url = "https://api.mexc.com/api/v3/exchangeInfo"
    res = await fetch_request(url)
    print(res)
asyncio.run(main())