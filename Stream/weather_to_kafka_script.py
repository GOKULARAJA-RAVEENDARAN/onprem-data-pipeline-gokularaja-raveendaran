# scripts/weather_to_kafka_script.py

import requests
import json
from datetime import datetime
from kafka import KafkaProducer
import os

# Config
CITY_NAME = "OOTY"
API_KEY = os.getenv("WEATHER_API_KEY") 
KAFKA_BOOTSTRAP_SERVERS = "192.168.1.38:9092"
KAFKA_TOPIC = "my-first-topic55"

def get_weather_data():
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={API_KEY}"
    )
    if response.status_code == 200:
        data = response.json()
        data["ingestion_time"] = datetime.utcnow().isoformat() + "Z"
        return {
            "location_timestamp": data["ingestion_time"],
            "city": data["name"],
            "latitude": data["coord"]["lat"],
            "longitude": data["coord"]["lon"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "weather_description": data["weather"][0]["description"],
        }
    else:
        print("API error:", response.status_code)
        return None

def send_to_kafka(data):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    producer.send(KAFKA_TOPIC, value=data)
    producer.flush()
    producer.close()

def main():
    data = get_weather_data()
    if data:
        send_to_kafka(data)

if __name__ == "__main__":
    main()
