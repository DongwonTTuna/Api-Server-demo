DROP DATABASE "API_SERVER";

CREATE DATABASE "API_SERVER" WITH OWNER = postgres ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C' IS_TEMPLATE = FALSE;

DROP TABLE IF EXISTS TICKERS;

CREATE TABLE IF NOT EXISTS TICKERS (
  exchange text PRIMARY KEY NOT NULL,
  tickers text[]
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

DROP SCHEMA IF EXISTS CDATA CASCADE;

CREATE SCHEMA CDATA;

DO $$
DECLARE
  exc text;
BEGIN
  FOR exc IN
  SELECT
    exchange
  FROM
    TICKERS LOOP
      EXECUTE 'CREATE TABLE IF NOT EXISTS CDATA.' || exc || 'DATA(ticker text NOT NULL,  tstamp bigint NOT NULL,  open float NOT NULL,  close float NOT NULL,  low float NOT NULL,  high float NOT NULL,  vol float NOT NULL)';
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

