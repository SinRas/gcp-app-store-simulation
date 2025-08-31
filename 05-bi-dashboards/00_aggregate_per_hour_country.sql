-- Create a new table with 1-hour aggregated data
CREATE OR REPLACE TABLE `app-store-simulation.data.user-interactions-hourly-agg` AS
SELECT
  -- This column identifies each unique time series
  country_code,
  -- Truncate the timestamp to the nearest 1-hour bucket
  TIMESTAMP_TRUNC(event_timestamp, HOUR) AS time_bucket,
  -- Target and other features to improve the model
  COUNT(*) AS n_records,
  COUNT(DISTINCT user_id) AS unique_users,
  COUNTIF(event_type = 'search') AS search_events,
  COUNTIF(event_type = 'app_install') AS install_events,
  COUNTIF(event_type = 'in_app_purchase') AS purchase_events
FROM
  `app-store-simulation.data.user-interactions-table`
GROUP BY
  time_bucket,
  country_code
ORDER BY
  time_bucket,
  country_code
;