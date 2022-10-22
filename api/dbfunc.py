import psycopg

def fetch_tickers(exchange):
     with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute(f"SELECT * FROM TICKERS WHERE exchange='{exchange}'")

                data = cur.fetchall()
                if len(data) == 0:
                    return {"status": 404, "data":"Exchange does not Found"}
                return {"status":200, "data":data[0][1]}
                
def fetch_exchanges():
     with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute("SELECT exchange FROM TICKERS")
                return {"status":200, "data":[db[0].upper().replace('-','').replace('_','').replace('/','') for db in cur.fetchall()]}

def fetch_chartdata(exchange, symbol):
         with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute(f"SELECT * FROM cdata.{exchange.lower()}data WHERE ticker='{symbol}'")
                data = cur.fetchall()
                if len(data) == 0:
                    return {"status": 404, "data":"Ticker or Exchange does not Found"}
                return {"status":200, "data":[[dta[1],dta[2],dta[3],dta[4],dta[5],dta[6]] for dta in data ]}