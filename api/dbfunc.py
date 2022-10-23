import psycopg

def fetch_tickers(exchange):
     with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                try:
                    cur.execute(f"SELECT * FROM TICKERS WHERE exchange='{exchange}'")
                    data = cur.fetchall()
                    if len(data) == 0:
                        return {"status": 404, "data":"Exchange does not Found"}
                    return {"status":200, "data":data[0][1]}
                except:
                    return {"status": 400, "data": "Error Occured"}
                
def fetch_exchanges():
     with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                try:
                    cur.execute("SELECT exchange FROM TICKERS")
                    return {"status":200, "data":[db[0].upper().replace('-','').replace('_','').replace('/','') for db in cur.fetchall()]}
                except:
                    return {"status": 400, "data": "Error Occured"}
def fetch_chartdata(exchange, symbol):
    with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
        with post.cursor() as cur:
            try:
                cur.execute(f"SELECT * FROM cdata.{exchange.lower()}data WHERE ticker='{symbol}' order by tstamp asc")
                data = cur.fetchall()
                if len(data) == 0:
                    return {"status": 404, "data":"Ticker or Exchange does not Found"}
                return {"status":200, "data":[[dta[1],dta[2],dta[3],dta[4],dta[5],dta[6]] for dta in data ]}
            except:
                return {"status": 400, "data": "Error Occured"}

def fetch_highest_volume(exchange):
    with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
        with post.cursor() as cur:
            try:
                cur.execute(f"SELECT tstamp FROM cdata.{exchange.lower()}data ORDER BY tstamp DESC LIMIT 1")
                tstamp = cur.fetchone()[0]
                cur.execute(f"SELECT ticker FROM cdata.{exchange.lower()}data where tstamp = '{tstamp}' ORDER BY vol desc")
                data = cur.fetchall()
                if len(data) == 0:
                        return {"status": 404, "data":"Exchange does not Found"}
                data = [p[0] for p in data]
                return {"status":200, "data":data[:30]}
            except:
                return {"status": 400, "data": "Error Occured"}
    