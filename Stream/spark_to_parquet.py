# spark_to_parquet.py
import os
import glob
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp
from pyspark.sql.types import StructType, StringType, DoubleType, IntegerType
from dotenv import load_dotenv

# point Spark at the Hadoop bin folder
os.environ["HADOOP_HOME"] = r"C:\spark\hadoop"
os.environ["PATH"] += os.pathsep + os.path.join(os.environ["HADOOP_HOME"], "bin")

# Load your .env file
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

# Read config with fallbacks
topic_name     = os.getenv("TOPIC_NAME",     "my-first-topic55")
output_path    = os.getenv("OUTPUT_PATH",    "F:/Guvi/Final_project/Final_project/output_parquet")
checkpoint     = os.getenv("CHECKPOINT_PATH", "F:/Guvi/Final_project/Final_project/spark_checkpoints")
bootstrap_svr  = os.getenv("BOOTSTRAP_SERVERS","localhost:9092")

# Make sure folders exist
os.makedirs(output_path, exist_ok=True)
os.makedirs(checkpoint, exist_ok=True)

# Gather all JARs from local jars/ directory
jars_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "jars"))
jar_files = glob.glob(os.path.join(jars_dir, "*.jar"))
if not jar_files:
    raise FileNotFoundError(f"❌ No JARs found in {jars_dir}")
jars_list = ",".join(jar_files)

# Initialize Spark
spark = (
    SparkSession.builder
    .appName("KafkaToParquet")
    .master("local[*]")
    .config("spark.jars", jars_list)
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# Define Kafka source
kafka_df = (
    spark.readStream
         .format("kafka")
         .option("kafka.bootstrap.servers", bootstrap_svr)
         .option("subscribe", topic_name)
         .option("startingOffsets", "earliest")  # ← important for debug!
         .option("failOnDataLoss", "false")
         .load()
)

# Define correct JSON schema
schema = (
    StructType()
    .add("location_timestamp", StringType())
    .add("city", StringType())
    .add("latitude", DoubleType())
    .add("longitude", DoubleType())
    .add("temperature", DoubleType())
    .add("humidity", IntegerType())
    .add("pressure", IntegerType())
    .add("wind_speed", DoubleType())
    .add("weather_description", StringType())
)

# Parse the JSON
json_df = (
    kafka_df
    .selectExpr("CAST(value AS STRING)")
    .select(from_json(col("value"), schema).alias("data"))
    .select("data.*")
)

# Add loaded_time column
stream_df = json_df.withColumn("loaded_time", to_timestamp("location_timestamp"))

# DEBUG: Show schema and write to console
stream_df.printSchema()

# Toggle this flag to switch between debug and parquet mode
DEBUG_MODE = False

if DEBUG_MODE:
    # Write to console for debugging
    query = (
        stream_df.writeStream
                 .format("console")
                 .outputMode("append")
                 .option("truncate", False)
                 .start()
    )
    print("🔎 Debug mode: writing stream to console…")
else:
    # Write to Parquet normally
    query = (
        stream_df.writeStream
                 .format("parquet")
                 .option("path", output_path)
                 .option("checkpointLocation", checkpoint)
                 .trigger(processingTime="2 minutes")
                 .start()
    )
    print(f"🚀 Streaming to parquet every 2m in `{output_path}` (checkpoint at `{checkpoint}`)…")

query.awaitTermination()
