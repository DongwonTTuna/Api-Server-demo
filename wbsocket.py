import asyncio, concurrent.futures, aiohttp,json, psycopg
from aioexec import Procs, Call


async def fetch_data(param):
     async with aiohttp.ClientSession() as session:
        async with session.ws_connect(f'wss://fstream.binance.com/stream?streams={param[2]}') as res:
            async for msg in res:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print(msg.json())
                    """with open('result.txt','a') as f:
                        f.write(json.dumps(msg.json()))"""

                        
            

'btcusdt@kline_1h'

async def main():
    exchange = ['UPBIT','BINANCE','FTX','BITFLY','KUCOIN','GATEIO','HUOBI']
    with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
        with post.cursor() as cur:
            param = [[]]
            cur.execute("SELECT * FROM getTicker(%s)", ('BINANCE',))
            data = cur.fetchall()[0][0]
            num = 0
            array_num = 0
            print(param[0])
            for dta in data:
                if num < 200:
                    if param[array_num] == []:
                        param[array_num] =  f'{dta.lower()}@kline_1h/'
                    else:
                        param[array_num] = param[array_num] + f'{dta.lower()}@kline_1h/'
                    num+=1
                if num == 200:
                    num = 0
                    param.append([])
                    array_num += 1
            await fetch_data(param)
    
        
asyncio.run(main())