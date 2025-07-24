# 🌦️ On-Premise Data Pipeline for IoT & Weather Analytics

**Author**: Gokularaja R    
**Goal**: Real-time & Batch analytics pipeline using live weather API and synthetic IoT data.

---

## 🚀 Project Overview

This project implements a **modular on-premise data pipeline** that handles:

- 📡 **Real-time streaming** from weather APIs using Kafka and Spark Streaming
- 📊 **Batch processing** of synthetic IoT sensor data using Spark Batch ETL
- 🗃️ **Storage** into MySQL, Parquet, and Snowflake
- 🔁 **Orchestration** using Apache Airflow
- 📈 **Monitoring** via Prometheus + Grafana
- 🌐 **Interactive UI** with Streamlit dashboard

---

## 🧱 Architecture Components

| Layer              | Tool/Tech                                   |
|--------------------|---------------------------------------------|
| Ingestion          | Python (Faker), Weather API                 |
| Messaging          | Apache Kafka                                |
| Stream Processing  | Apache Spark Structured Streaming           |
| Batch ETL          | Apache Spark Batch                          |
| Storage            | MySQL, Parquet, S3, Snowflake               |
| Orchestration      | Apache Airflow (Dockerized)                 |
| Monitoring         | Prometheus + Grafana                        |
| UI Dashboard       | Streamlit                                   |

---

## 🔄 Data Flow

### 🌩️ **Stream Pipeline**
1. Airflow DAG fetches weather data every minute from API
2. Data is pushed to Kafka topic
3. Spark Structured Streaming reads from Kafka
4. Data is stored in **Parquet** files
5. Streamlit shows real-time weather visualizations

### 🧪 **Batch Pipeline**
1. IoT sensor data is generated every minute (Python + Faker)
2. Stored as CSV and inserted into a MySQL table
3. Spark Batch reads CSV & MySQL, performs transformation
4. Writes cleaned/aggregated data to:
   - Final MySQL table
   - Snowflake (cloud)
   - CSV backup to S3

---

## 📸 Dashboards & Monitoring

- 📊 **Grafana**: System metrics
- 🧪 **Streamlit**: Real-time weather visualization
- 📂 **Parquet Viewer**: Pandas + Streamlit integration

---

## 🛠️ Challenges & Solutions

- Kafka permission & log dir issues on Windows → Fixed via config & ACL changes
- Hive instability locally → Switched to **Snowflake**
- Docker file permissions & mount issues → Resolved via persistent volumes
- DAG scheduling problems → Solved with proper Airflow setup in Docker

---

## ✅ Achievements

- Built **fully modular pipeline** from scratch
- Combined both **real-time** and **batch processing**
- Integrated **cloud-ready systems** (Snowflake, S3)
- Automated everything using **Airflow**
- Visualized live data using **Streamlit**
- Monitored health using **Prometheus + Grafana**

---

## 💡 Real-World Applications

- 🚕 Cab surge pricing (based on weather)
- 🍔 Food delivery predictions
- 🛰️ Weather forecasting & disaster alert systems
- 🏭 Industrial sensor monitoring

---

## 📂 Project Structure

```bash
project/
├── airflow/               # DAGs, configs, logs
├── kafka/                 # Local Kafka setup
├── spark/                 # Batch & stream processing scripts
├── streamlit/             # UI code
├── monitoring/            # Prometheus + Grafana config
├── docker-compose.yaml    # Main orchestrator
├── .env                   # Env variables
├── jars/                  # JDBC connectors
└── README.md
