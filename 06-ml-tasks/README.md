# 06) Machine Learning Tasks 🤖

This part of the project demonstrates a full **MLOps lifecycle** on **Google Cloud Platform**, showcasing two distinct approaches to solve a time-series forecasting problem:

> Predicting number of user interactions for each country in hourly intervals.

I've taken two different approaches to demonstrate familiarity with both **GCP's built-in AutoML tools** and containerizing a **custom PyTorch Model** training and inference. Hope this demonstrates my skills in integrating existing AutoML tools and possibility of switching to fully customizable ML models written in Python.



## Approach 1: Vertex AI Forecast (AutoML)

This workflow leverages GCP's managed services to quickly build a high-performance baseline model without extensive custom code.

- **Data Preparation:** A *BigQuery Scheduled Query* aggregates raw data into a clean time-series format with *time series identifier* (`country_code`), `timestamp`, and `target` columns.

- **Training & Prediction:**
    - A **Vertex AI Dataset** is created from the BigQuery source.
    - An **AutoML Forecast model** is trained for time-series forecasting. Automatically handling time-series cross-validations and feature engineering and hyperparameter tuning.
    - A **Batch Prediction Job** generates forecasts and writes the results, including *confidence intervals*, directly back to a **BigQuery table** for visualization.


