DROP DATABASE "API_SERVER";

CREATE DATABASE "API_SERVER" WITH OWNER = postgres ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C' IS_TEMPLATE = FALSE;

DROP TABLE IF EXISTS tickers;

CREATE TABLE IF NOT EXISTS tickers (
  exnum serial PRIMARY KEY NOT NULL,
  exchange text,
  tickers text[]
);

DROP TABLE IF EXISTS chartdata;

CREATE TABLE IF NOT EXISTS chartdata (
  exnum serial PRIMARY KEY NOT NULL,
  exchange text,
  chartdata text[]
);


/* INSERT VALUES*/
INSERT INTO tickers (exchange, tickers)
  VALUES ('UPBIT', NULL);

INSERT INTO tickers (exchange, tickers)
  VALUES ('BINANCE', NULL);

INSERT INTO tickers (exchange, tickers)
  VALUES ('FTX', NULL);

INSERT INTO tickers (exchange, tickers)
  VALUES ('BITFLY', NULL);

INSERT INTO tickers (exchange, tickers)
  VALUES ('KUCOIN', NULL);

INSERT INTO tickers (exchange, tickers)
  VALUES ('GATEIO', NULL);

INSERT INTO tickers (exchange, tickers)
  VALUES ('HUOBI', NULL);

DO $$
DECLARE
  ext text;
BEGIN
  FOR ext IN
  SELECT
    exchange
  FROM
    tickers LOOP
      EXECUTE FORMAT('INSERT INTO chartdata (exchange, chartdata) VALUES (''%s'', NULL)', ext);
    END LOOP;
END
$$;

DROP PROCEDURE IF EXISTS updTicker;

CREATE PROCEDURE updTicker (dta text[], exc text)
LANGUAGE SQL
AS $$
  UPDATE
    tickers
  SET
    tickers = dta
  WHERE
    exchange = exc;
$$;

DROP PROCEDURE IF EXISTS updChart;

CREATE PROCEDURE updChart (dta text[], exc text)
LANGUAGE SQL
AS $$
  UPDATE
    chartdata
  SET
    chartdata = dta
  WHERE
    exchange = exc;
$$;

SELECT
  *
FROM
  tickers;

SELECT
  *
FROM
  chartdata;

