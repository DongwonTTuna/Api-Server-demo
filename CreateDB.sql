DROP DATABASE "API_SERVER";

CREATE DATABASE "API_SERVER" WITH OWNER = postgres ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C' IS_TEMPLATE = FALSE;

DROP TABLE IF EXISTS TICKERS;

CREATE TABLE IF NOT EXISTS TICKERS (
  exchange text PRIMARY KEY NOT NULL,
  tickers text[]
);

DROP TABLE IF EXISTS CHARTDATA;

CREATE TABLE IF NOT EXISTS CHARTDATA (
  exchange text NOT NULL,
  ticker text NOT NULL,
  tstamp text NOT NULL,
  open float NOT NULL,
  close float NOT NULL,
  low float NOT NULL,
  high float NOT NULL,
  vol float NOT NULL,
  count int NOT NULL
);

DROP TABLE IF EXISTS TSTAMP;

CREATE TABLE IF NOT EXISTS TSTAMP (
  exnum serial PRIMARY KEY NOT NULL,
  tstamp text
);


/* INSERT VALUES*/
INSERT INTO tickers (exchange, tickers)
  VALUES ('UPBIT', NULL);

INSERT INTO tickers (exchange, tickers)
  VALUES ('BYBIT', NULL);

INSERT INTO tickers (exchange, tickers)
  VALUES ('BINANCE', NULL);

INSERT INTO tickers (exchange, tickers)
  VALUES ('FTX', NULL);

INSERT INTO tickers (exchange, tickers)
  VALUES ('MEXC', NULL);

INSERT INTO tickers (exchange, tickers)
  VALUES ('KUCOIN', NULL);

INSERT INTO tickers (exchange, tickers)
  VALUES ('GATEIO', NULL);

INSERT INTO tickers (exchange, tickers)
  VALUES ('HUOBI', NULL);

INSERT INTO TSTAMP (tstamp)
  VALUES (NULL);

INSERT INTO TSTAMP (tstamp)
  VALUES (NULL);

DO $$
DECLARE
  exc text;
BEGIN
  FOR exc IN
  SELECT
    exchange
  FROM
    TICKERS LOOP
      EXECUTE 'DROP TABLE IF EXISTS ' || exc;
      EXECUTE 'CREATE TABLE IF NOT EXISTS ' || exc || 'DATA( exchange text NOT NULL,  ticker text NOT NULL,  tstamp text NOT NULL,  open float NOT NULL,  close float NOT NULL,  low float NOT NULL,  high float NOT NULL,  vol float NOT NULL,  count int NOT NULL)';
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

DROP FUNCTION IF EXISTS getTicker;

CREATE FUNCTION getTicker (exc text)
  RETURNS SETOF text[]
  LANGUAGE SQL
  AS $$
  SELECT
    tickers
  FROM
    tickers
  WHERE
    exchange = exc;
$$;

DROP FUNCTION IF EXISTS getChart;

CREATE FUNCTION getChart (exc text)
  RETURNS TABLE (
    exchange text,
    ticker text,
    tstamp text,
    OPEN float,
    CLOSE float,
    low float,
    high float,
    vol float,
    count int)
  LANGUAGE SQL
  AS $$
  SELECT
    (exchange,
      ticker,
      tstamp,
      OPEN,
      CLOSE,
      low,
      high,
      vol,
      count)
  FROM
    chartdata
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
  CHARTDATA;
