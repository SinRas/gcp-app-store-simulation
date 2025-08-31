-- Run this once to create the destination table for your forecasts
CREATE OR REPLACE TABLE `app-store-simulation.data.user-interactions-7days-forecast` (
  forecast_timestamp TIMESTAMP,
  prediction_value FLOAT64,
  prediction_lower_bound FLOAT64,
  prediction_upper_bound FLOAT64,
  -- This is the timestamp for when the forecast was generated
  generated_at TIMESTAMP
)
;