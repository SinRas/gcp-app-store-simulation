-- Train the time series model
CREATE OR REPLACE MODEL `app-store-simulation.data.model_dashboard_interaction_forecaster`
OPTIONS(
  MODEL_TYPE='ARIMA_PLUS',
  TIME_SERIES_TIMESTAMP_COL='time_bucket',
  TIME_SERIES_DATA_COL='n_records',
  HORIZON = 168, -- Tell the model you want to predict next 7 days
  AUTO_ARIMA = TRUE
) AS
SELECT
  time_bucket,
  SUM(n_records) AS n_records
FROM
  `app-store-simulation.data.user-interactions-hourly-agg`
GROUP BY
  time_bucket
;