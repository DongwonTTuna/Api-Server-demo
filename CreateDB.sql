DROP DATABASE "API_SERVER";

CREATE DATABASE "API_SERVER" WITH OWNER = postgres ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C' IS_TEMPLATE = FALSE;

DROP TABLE IF EXISTS TICKERS;

CREATE TABLE IF NOT EXISTS TICKERS (
  exnum serial PRIMARY KEY NOT NULL,
  exchange text,
  tickers text[]
);

DROP TABLE IF EXISTS CHARTDATA;

CREATE TABLE IF NOT EXISTS CHARTDATA (
  exnum serial PRIMARY KEY NOT NULL,
  exchange text,
  ticker text,
  chartdata text[][]
);

DROP TABLE IF EXISTS TSTAMP;

CREATE TABLE IF NOT EXISTS TSTAMP (
  exnum serial PRIMARY KEY NOT NULL,
  tstamp int
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

INSERT INTO TSTAMP (tstamp)
  VALUES (NULL);

INSERT INTO TSTAMP (tstamp)
  VALUES (NULL);

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

CREATE PROCEDURE updChart (dta text[][], exc text)
LANGUAGE SQL
AS $$
  UPDATE
    chartdata
  SET
    chartdata = dta
  WHERE
    exchange = exc;
$$;

DROP PROCEDURE IF EXISTS CreateTickersInChartData;

CREATE PROCEDURE CreateTickersInChartData (exc text)
LANGUAGE SQL
AS $$
  INSERT INTO
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
  RETURNS SETOF text[]
  LANGUAGE SQL
  AS $$
  SELECT
    *
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
  chartdata;

