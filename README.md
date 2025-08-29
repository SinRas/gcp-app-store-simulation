# 🌐 GCP AppStore Data Pipeline Simulator
This project is an end-to-end simulation of a real-time data platform for a modern application marketplace, built entirely on the Google Cloud Platform.
It demonstrates a scalable architecture for generation, ingesting, processing, analyzing, and running machine learning models on high-throughput event data.

<p align="center"><strong><a href="https://sinras.github.io/static/project_gcp_appstore_simulator_7ee5">🚀 View the Live Project Showcase Page 🚀</a></strong></p>

## ✨ Key Skills & Technologies Showcased

| Category | Technologies & Concepts |
| :---------|:------------------------|
| Cloud Platform | `Google Cloud Platform (GCP)` `Identity and Access Management (IAM)`  |
| Data Generation | `Python` `Stochastic Processes (Poisson Process)` `Streaming Data` |
| Data Ingestion | `Cloud Pub/Sub` `Real-Time Streaming` `Avro Schemas` |
| Data Processing | `Cloud Dataflow` `Apache Beam` `ETL/ELT` `Parquet Data Lake` |
| Data Warehousing | `BigQuery` `SQL` `Data Analytics` |
| BI & Visualization | `Metabase` `Live Dashboards` `BigQuery ML` |
| Machine Learning | `Vertex AI` `PyTorch` `Time Series Forecasting` |
| MLOps & Infra | `Docker` `Google Kubernetes Engine (GKE)` `Serverless Architecture` |

## 🏛️ Architecture Overview
This project implements a complete data lifecycle, from event generation to ML-powered forecasting.

`[Real-world Data 📱]` -> `[GKE: Python Data Generators 🐍]` -> `[Pub/Sub 📨]` -> `[Dataflow 🌊]` -> `[BigQuery Data Warehouse 🗄️]` & `[GCS Data Lake (Parquet) 🏞️]`

From the warehouse, data is used for:

- `[Metabase 📊]` -> **Live BI Dashboards**
- `[Vertex AI & BQML 🤖]` -> **Time Series Forecasting**

## 🛠️ Project Components Deep Dive

This repository is structured to mirror the data pipeline stages.

### 1. 🌍 Data Generation (`/01-data-generation`)

- **Objective:** Simulate a realistic, high-volume stream of user interaction events from a global user base.
- **Implementation:**
    - A Python script generates events based on a Non-Homogeneous Poisson Process, creating dynamic and time-varying traffic.
    - Event rates are realistically weighted using a dataset of real-world country populations ([1]), internet penetration rates ([2]),time zone ([3]) and daily activity patterns.
    - The application is containerized with Docker and deployed as a scalable, replicated service on Google Kubernetes Engine (GKE).
    - The GCP Python SDK is used for efficient, batched message publishing to Pub/Sub.


[1]: https://www.worldometers.info/world-population/population-by-country
[2]: https://data.worldbank.org/indicator/IT.NET.USER.ZS
[3]: https://en.wikipedia.org/wiki/List_of_time_zones_by_country

### 2. 📨 Data Ingestion (`/02-data-ingestion`)

- **Objective:** Reliably capture the streaming data at scale and make it available to downstream consumers.
- **Implementation:**
    - Cloud Pub/Sub is used as a fully-managed, auto-scaling message bus to decouple producers from consumers.
    - A formal data contract is enforced using an Avro schema attached to the Pub/Sub topic, ensuring data quality and preventing bad data from entering the pipeline.

### 3. 🌊 Data Processing (`/03-data-processing`)

- **Objective:** Transform the raw, incoming JSON data into a clean, structured, and query-optimized format.
- **Implementation:**
    - A streaming ETL pipeline built with Apache Beam reads from the Pub/Sub subscription in real-time.
    - The pipeline is executed on Cloud Dataflow, which provides a serverless, auto-scaling environment to handle fluctuating data volumes without manual intervention.
    - Processed data is written in the columnar Parquet format to a Google Cloud Storage (GCS) bucket, creating a cost-effective and scalable data lake.

### 4. 📈 Data Warehousing & BI (`/04-05-data-warehouse-BI`)

- **Objective:** Make historical and real-time data available for high-speed analytics and visualization.
- **Implementation:**
    - Live, interactive dashboards are built with Metabase, which run real-time SQL queries directly against BigQuery tables
    - Using SQL-like BigQuery ML for timeseries forcasting and costumer behavior prediction.
    - Historical data and future forecasts combined to provide insight for business decisions.


### 5. 🤖 Machine Learning Tasks (`/06-ml-tasks`)

- **Objective:** Train, deploy, and serve time-series forecasting models to predict future user activity.
- **Implementation:** Production-Grade ML with Vertex AI:
    - A formal dataset is created in Vertex AI from the BigQuery table/GCS.
    - A custom PyTorch model is containerized and trained using a Vertex AI Custom Training Job, demonstrating a full MLOps workflow.
    - The trained model is deployed to a Vertex AI Endpoint with configurable GPU resources and autoscaling to serve live predictions.


## 💡 Conclusion & Key Learnings

This project demonstrates an end-to-end, production-ready data platform built entirely on Google Cloud Platform. It showcases the ability to handle **real-time data streams at scale**, process them efficiently with **serverless tools**, and derive value through both **business intelligence** and **machine learning**.

I also demostrated practical use of multiple concepts like **time-varying stochastic process simulation**, **containerize and scale with Kubernetes cluster**, **Pub/Sub communication with Python**, **stream processing with Apache Beam**, **BI forecasts with BigQueryML**, **live dashboards with Metabase**, and **training ML models on Vertex AI**.