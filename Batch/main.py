from functions import (
    spark_create,
    spark_mysql_connection,
    read_sensor_csv,
    weather_data_mysql,
    spark_to_mysql,
    snowflake_loading,
    upload_to_s3
)
from pyspark.sql.functions import col, expr, to_date
print("######## Starting Batch ETL Process... #######")

# Step 1: Spark session
spark = spark_create()

# Step 2: MySQL connection
jdbc_url, connection_props = spark_mysql_connection(spark)

# Step 3: Read and process station data from MySQL
print("####### Reading weather station data from MySQL #######")
station_df = weather_data_mysql(spark, jdbc_url, connection_props) \
    .withColumn("DATE", to_date("loaded_time"))

# Optional timezone shift if needed
station_df = station_df.withColumn("loaded_time", expr("loaded_time + INTERVAL 5 HOURS 30 MINUTES"))

# Step 4: Read and process sensor data from CSV
print("####### Reading sensor data from CSV #######")

sensor_df = read_sensor_csv(spark).selectExpr(
    "Sensor_id AS SENSOR_ID",
    "location AS LOCATION",
    "timestamp AS TIMESTAMP",
    "temp_celsius AS TEMP_CELSIUS",
    "humidity_percent AS HUMIDITY_PERCENT",
    "rain_mm AS RAIN_MM"
).withColumn("DATE", to_date("TIMESTAMP"))

# Step 5: Write both to MySQL
print("####### Writing to MySQL#######")
spark_to_mysql(station_df, spark, jdbc_url, "final_station", connection_props)
spark_to_mysql(sensor_df, spark, jdbc_url, "final_sensor", connection_props)

# Step 6: Write both to Snowflake
print("####### Writing to Snowflake#######")
snowflake_loading(station_df, spark, "weather_station_data")
snowflake_loading(sensor_df, spark, "sensor_data")

# Step 7: Upload both CSVs to S3
print("######## Uploading to S3##########")
upload_to_s3()

spark.stop()
print("########## ETL Complete.#########")
