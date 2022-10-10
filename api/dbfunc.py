import psycopg

def fetch_tickers(exchange):
     with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute(f"SELECT * FROM TICKERS WHERE exchange='{exchange}'")
                data = cur.fetchall()[0]
                return {"exc": data[0],"tickers":data[1]}
                
def fetch_exchanges():
     with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute("SELECT exchange FROM TICKERS")
                return {"excs":[db[0] for db in cur.fetchall()]}

def fetch_chartdata(exchange, symbol):
         with psycopg.connect("dbname=API_SERVER user=postgres password=0790") as post:
            with post.cursor() as cur:
                cur.execute(f"SELECT * FROM {exchange} WHERE ticker")
    
if __name__ == "__main__":
    fetch_exchanges()