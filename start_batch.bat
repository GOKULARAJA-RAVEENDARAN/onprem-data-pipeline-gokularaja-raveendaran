@echo off
echo ================================
echo Cleaning old Kafka logs...
echo ================================
rmdir /s /q C:\tmp\kafka-logs
mkdir C:\tmp\kafka-logs

echo ================================
echo Starting Zookeeper...
echo ================================
start "Zookeeper" cmd /k "cd /d C:\kafka && .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties"

timeout /t 15 /nobreak

echo ================================
echo Starting Kafka Broker...
echo ================================
start "Kafka Broker" cmd /k "cd /d C:\kafka && .\bin\windows\kafka-server-start.bat .\config\server.properties"

timeout /t 10 /nobreak

echo ================================
echo Starting Docker Compose Stack (Airflow)...
echo ================================
start "Airflow Stack" cmd /k "cd /d F:\Guvi\Final_project\Final_project && docker-compose up -d --build"

echo ================================
echo All services launched in separate terminals.
echo ================================
pause
