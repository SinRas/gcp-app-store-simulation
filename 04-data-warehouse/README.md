# 04) Data Warehouse

Google BigQuery serves as the central repository and analytical engine for the entire project. After raw data is processed, it's loaded into a structured, queryable format, making it available for high-speed analytics, business intelligence, and machine learning tasks.



## Why Google BigQuery?
For a project designed to handle large-scale, streaming data, BigQuery is the ideal choice over traditional transactional databases (like PostgreSQL/MySQL) for several key reasons:

- 🚀 Serverless Architecture: BigQuery is a fully-managed service that requires zero infrastructure management. It automatically scales compute resources to handle queries of any size, from megabytes to petabytes, without needing to provision or manage clusters.

- 🏛️ Columnar Storage: Unlike row-based databases, BigQuery stores data by column. This is massively efficient for analytical queries (OLAP workloads), as it only reads the specific columns needed to answer a question, dramatically reducing I/O and accelerating performance.

- 🧠 Integrated Machine Learning: With BigQuery ML, powerful machine learning models (like time-series forecasting) can be trained and deployed directly within the data warehouse using familiar SQL syntax, significantly simplifying the MLOps lifecycle.

- 🌐 Native GCP Integration: BigQuery seamlessly connects to other GCP services, including Pub/Sub for direct streaming ingestion, Dataflow for ETL, and Vertex AI for advanced ML, creating a cohesive and powerful data ecosystem.

## Implementation Details

The table for storing user interaction data is defined with the BigQuery SQL command in the file `04-data-warehouse/00_create_main_table.sql`, with date partitioning for performance optimization. The table definition is based on and compatible with the Avro schmea in the file `02-data-ingestion/user_interaction_v1_avro.json` to make sure consistensy, and part.

### Table Schema & Data Integrity
A robust table schema was designed to store the user interaction data. This acts as a "schema-on-write" enforcement layer, ensuring data quality and consistency.

- **Data Types:** Appropriate data types were selected for analytical efficiency. Notably, ISO 8601 strings for timestamps are automatically parsed into BigQuery's native TIMESTAMP type, and flexible JSON objects are stored in the native JSON type, allowing for direct querying of nested fields.

- **Constraints:** To ensure data integrity, ID fields like user_id and event_id are defined with a maximum length of 36 characters (e.g., STRING(36)), matching the UUID format.

The SQL script to create the main table can be found at create_user_interactions_table.sql.

### Performance Optimization: Partitioning
To optimize query performance and manage costs, the primary table is partitioned by the event_timestamp column on a daily basis. When a query includes a date filter (e.g., WHERE DATE(event_timestamp) = "2024-10-26"), BigQuery's query optimizer will only scan the data in the relevant partitions, avoiding a costly full-table scan. This is a critical best practice for managing large-scale time-series data.
