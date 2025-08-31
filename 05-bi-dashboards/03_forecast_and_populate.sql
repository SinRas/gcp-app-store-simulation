-- Step A: Delete the previous forecast results
DELETE FROM `app-store-simulation.data.user-interactions-7days-forecast` WHERE TRUE;

-- Step B: Generate a new forecast and insert it into the results table
INSERT INTO `app-store-simulation.data.user-interactions-7days-forecast` (
    forecast_timestamp,
    prediction_value,
    prediction_lower_bound,
    prediction_upper_bound,
    generated_at
)
SELECT
  forecast_timestamp,
  forecast_value AS prediction_value,
  prediction_lower_bound,
  prediction_upper_bound,
  -- Add the current timestamp to know when the forecast was made
  CURRENT_TIMESTAMP() AS generated_at
FROM
  ML.FORECAST(
    MODEL `app-store-simulation.data.model_dashboard_interaction_forecaster`,
    STRUCT(168 AS horizon)
  )
;