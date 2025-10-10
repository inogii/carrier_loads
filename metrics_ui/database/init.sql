-- Enums for standardized values
CREATE TYPE sentiment_enum AS ENUM ('happy', 'neutral', 'upset', 'n/a');
CREATE TYPE outcome_enum   AS ENUM ('successful', 'unsuccessful', 'n/a');

-- Calls table
CREATE TABLE calls (
  call_id         BIGSERIAL PRIMARY KEY,
  mc_number       TEXT NOT NULL,
  original_price  NUMERIC(12,2) NOT NULL CHECK (original_price >= 0),
  agreed_price    NUMERIC(12,2)      CHECK (agreed_price >= 0),
  had_discount    BOOLEAN NOT NULL DEFAULT FALSE,
  discount_rate   NUMERIC(5,2) NOT NULL DEFAULT 0
                  CHECK (discount_rate >= 0 AND discount_rate <= 100),
  sentiment       sentiment_enum NOT NULL DEFAULT 'n/a',
  outcome         outcome_enum   NOT NULL DEFAULT 'n/a',

  -- new fields
  duration        INTEGER NOT NULL CHECK (duration >= 0),  -- in seconds
  timestamp       TIMESTAMPTZ NOT NULL                    -- ISO format automatically handled
);

-- Helpful indexes
CREATE INDEX idx_calls_timestamp   ON calls (timestamp);
CREATE INDEX idx_calls_outcome     ON calls (outcome);
CREATE INDEX idx_calls_sentiment   ON calls (sentiment);
CREATE INDEX idx_calls_mc          ON calls (mc_number);
