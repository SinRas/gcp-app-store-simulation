# 05) BI Dashboards 📊

The ultimate goal of a data pipeline is to make data accessible and useful for decision-making. This component focuses on visualizing the processed data from the BigQuery warehouse into live, interactive dashboards using **Metabase**, an open-source BI tool.

This demonstrates the final step in the data value chain: transforming aggregated data into actionable business insights.

## Dashboards Links

- [Metabse: User Statistics Dashboard](https://sinras-app-store-simulation.metabaseapp.com/public/dashboard/10d83b10-a81b-40d1-866f-83aa642293bf)


## From Raw Data to Live Forecasts

The dashboarding process was implemented in two distinct stages: first, visualizing the historical data, and second, enriching the dashboard with a predictive, forward-looking view using machine learning.

Here are the tables created in order:
|          Task           |                     SQL file                         |
|:------------------------|:-----------------------------------------------------|
| Prepare training data   |  `05-bi-dashboard/00_aggregate_per_hour_country.sql` |
| Train BigQuery ML model |  `05-bi-dashboard/01_train_arima_plus_model.sql`     |
| Create forecast result  |  `05-bi-dashboard/02_create_forecast_table.sql`      |
| Forecast and populate   |  `05-bi-dashboard/03_forecast_and_populate.sql`      |

## 5.1) Setup & Connectivity

- **Metabase: Local and Hosted:** I used **Metabase** both locally, in a Docker container for ease of setup, and on the **Metabase Cloud** account. With proper network infrastructure, running a Docker container is pretty straighforward. But I used the **Metabase Cloud** for ease of public sharing of the dashboards.

- **Secure Connection:** A secure connection to the Google BigQuery warehouse was established by creating a dedicated GCP Service Account. This account was granted limited, read-only permissions to adhere to the principle of least privilege. This avoids exposing primary user credentials and is a best practice for connecting third-party applications to cloud data warehouses.


## 5.2) Live Historical Dashboard

A live dashboard was created to monitor the real-time activity of the AppStore simulation.

- **Direct Querying:** Charts and graphs on the dashboard run live SQL queries directly against the user-interactions-table in BigQuery.

- **Key Metrics:** The dashboard visualizes metrics such as the total number of user interactions over time, breakdowns by country, and distribution of event types (e.g., installs vs. searches).



## 5.3) Forecasting with BigQuery ML

To demonstrate a proactive, data-driven approach, time-series models were used to forecast future user traffic. This entire ML workflow was implemented within BigQuery itself.

- **Automated Feature Engineering:** A BigQuery Scheduled Query runs periodically to aggregate the raw interaction data into hourly bucketed time-series, creating a clean, structured dataset suitable for model training.

- **In-Warehouse Model Training:** Using BigQuery ML, a time-series forecasting model (`ARIMA_PLUS`) is automatically re-trained on this aggregated data, with a determined schedule to ensure changes in user behavior are captured. This demonstrates a lightweight and efficient MLOps practice, as model training is part of a repeatable, scheduled SQL script.

- **Batch Predictions:** After training is done, the scheduled query uses the `ML.FORECAST` function to predict the number of user interactions for upcoming days.

- **Storing & Visualizing Forecasts:** The prediction results, including the forecast value and confidence intervals, are saved to a dedicated table, which is then used in **Metabase** to add trends to visualizations.
