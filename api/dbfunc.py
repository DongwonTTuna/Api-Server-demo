import psycopg

def fetch_tickers(exchange):
     with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute(f"SELECT * FROM TICKERS WHERE exchange='{exchange}'")

                data = cur.fetchall()
                if len(data) == 0:
                    return {"status": 404, "data":"Exchange does not Found"}
                return {"status":200, "data":{"exc": data[0][0],"tickers":data[0][1]}}
                
def fetch_exchanges():
     with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute("SELECT exchange FROM TICKERS")
                return {"status":200, "data":{"excs":[db[0] for db in cur.fetchall()]}}

def fetch_chartdata(exchange, symbol):
         with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute(f"SELECT * FROM {exchange}DATA WHERE ticker='{symbol}'")
                data = cur.fetchall()
                if len(data) == 0:
                    return {"status": 404, "data":"Ticker or Exchange does not Found"}
                return {"status":200, "data":{"chartdata":[[dta[1],dta[2],dta[3],dta[4],dta[5],dta[6],dta[7]] for dta in data ]}}
                
if __name__ == "__main__":
    fetch_chartdata('BINANCE', 'BTCUSDT')