import psycopg2
from typing import Iterator, Optional
import io

db = [['KRWBTC', 166227135,27639000,27449000,2740000,27677000,290.955] for _ in range(0,10)]






with psycopg2.connect("dbname=API_SERVER user=postgres password=0790") as post:
    with post.cursor() as cur:
        cur.execute_value()
        cur.mogrify
    copy_string_iterator(post)