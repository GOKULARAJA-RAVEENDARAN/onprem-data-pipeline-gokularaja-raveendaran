from pyspark.sql import SparkSession
from pyspark.sql.functions import expr
from dotenv import load_dotenv
import os
import boto3
from datetime import datetime
import pandas as pd
import time

load_dotenv("F:\\Guvi\\Final_project\\Final_project\\batch\\.env")
sf_url = os.getenv("SFURL")
sf_user = os.getenv("SFUSER")
sf_password = os.getenv("SFPASSWORD")
sf_database = os.getenv("SFDATABASE")
sf_schema = os.getenv("SFSCHEMA")
sf_warehouse = os.getenv("SFWAREHOUSE")
sf_role = os.getenv("SFROLE")
my_pass = os.getenv("PASSWORD")
from pyspark.sql import SparkSession

def spark_create():
    spark = SparkSession.builder \
        .appName("BatchETL") \
        .config("spark.jars",
            "jars/spark-snowflake_2.12-2.16.0-spark_3.3.jar,"
            "jars/snowflake-jdbc-3.16.1.jar,"
            "file:///F:/Guvi/Final_project/Final_project/mysql-connector-j-9.3.0/mysql-connector-j-9.3.0.jar") \
        .getOrCreate()
    return spark

# Spark-MySQL connection
def spark_mysql_connection(spark):
    jdbc_url =     jdbc_url = (
        "jdbc:mysql://localhost:3306/mini_project"
        "?allowPublicKeyRetrieval=true"
        "&useSSL=false")
    connection_properties = {
        "user": "root",
        "password": my_pass,
        "driver": "com.mysql.cj.jdbc.Driver",
        "timestampTimezone": "Asia/Kolkata"
    }
    return jdbc_url, connection_properties

# Load weather data from MySQL
def weather_data_mysql(spark, jdbc_url, connection_properties):
    last_load_df = spark.read.jdbc(
        url=jdbc_url,
        table="load_time_tracker",
        properties=connection_properties)

    last_load_df = last_load_df.withColumn("loaded_time_corrected", expr("last_loaded_time - INTERVAL 5 HOURS 30 MINUTES"))
    row = last_load_df.select("loaded_time_corrected").first()

    # 💡 Default time if tracker is empty
    if row is None or row[0] is None:
        corrected_time = "1970-01-01 00:00:00"
    else:
        corrected_time = row[0]

    query = f"(SELECT * FROM station_data WHERE loaded_time > '{corrected_time}') AS filtered_data"

    df = spark.read.jdbc(
        url=jdbc_url,
        table=query,
        properties=connection_properties
    )
    final_df = df.withColumn("loaded_time", expr("loaded_time - INTERVAL 5 HOURS 30 MINUTES"))
    return final_df

# Load sensor CSV data
def read_sensor_csv(spark):
    folder_path = "F:/Guvi/Final_project/Final_project/faker_output"
    files = [f"file:///{folder_path}/{f}" for f in os.listdir(folder_path) if f.endswith(".csv")]

    if not files:
        raise FileNotFoundError("No CSV files found in faker_output folder")

    return spark.read.option("header", True).option("inferSchema", True).csv(files)

# Load final data to MySQL
def spark_to_mysql(df, spark, jdbc_url, tablename, connection_props):
    df.write.jdbc(
        url=jdbc_url,
        table=tablename,
        mode="append",
        properties=connection_props)

# Snowflake loading function
def snowflake_loading(df, spark, tablename):
    sfOptions = {
        "sfURL": os.getenv("SFURL"),
        "sfUser": os.getenv("SFUSER"),
        "sfPassword": os.getenv("SFPASSWORD"),
        "sfDatabase": os.getenv("SFDATABASE"),
        "sfSchema": os.getenv("SFSCHEMA"),
        "sfWarehouse": os.getenv("SFWAREHOUSE"),
        "sfRole": os.getenv("SFROLE")
    }

    df.write \
        .format("snowflake") \
        .options(**sfOptions) \
        .option("dbtable", tablename) \
        .mode("append") \
        .save()

# Upload CSVs to S3 and clean up locally
def upload_to_s3():
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    bucket_name = 'weatherdatacsvbackup'
    s3_folder = 'sensor_backup/'
    local_folder = r"F:\\Guvi\\Final_project\\Final_project\\faker_output"

    s3_client = boto3.client(
        's3',
        region_name='ap-south-1',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )

    for filename in os.listdir(local_folder):
        if filename.endswith('.csv'):
            print(filename)
            local_path = os.path.join(local_folder, filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            s3_key = s3_folder + f"{timestamp}_{filename}"
            try:
                s3_client.upload_file(local_path, bucket_name, s3_key)
                print(f"Uploaded: {filename} -> s3://{bucket_name}/{s3_key}")
                time.sleep(1)
                os.remove(local_path)
                print(f"🗑️ Deleted local file: {filename}")
            except Exception as e:
                print(f"Failed to upload {filename}: {e}")
