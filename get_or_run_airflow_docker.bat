@echo off

:: Step 0: Detect the drive where the batch file is located
%~d0
cd %~dp0
if %errorlevel% neq 0 (
    echo Failed to switch to the script's drive and directory. Please check the script location.
    exit /b
)

:: Check if the 'airflow' folder exists
if not exist airflow (
    :: Step 1: Create 'airflow' folder
    echo Creating airflow folder...
    mkdir airflow
    if %errorlevel% neq 0 (
        echo Failed to create airflow folder. Please check your permissions.
        exit /b
    )

    :: Step 2: Pull docker-compose.yaml for Airflow into the 'airflow' folder
    echo Downloading docker-compose.yaml into airflow folder...
    curl -LfO "https://airflow.apache.org/docs/apache-airflow/2.10.5/docker-compose.yaml"
    if %errorlevel% neq 0 (
        echo Failed to download docker-compose.yaml. Please check your internet connection.
        exit /b
    )
    move docker-compose.yaml airflow
    if %errorlevel% neq 0 (
        echo Failed to move docker-compose.yaml. Please check your permissions.
        exit /b
    )

    :: Step 3: Set up necessary folders inside 'airflow'
    echo Creating subfolders inside airflow: dags, logs, plugins...
    mkdir airflow\dags airflow\logs airflow\plugins
    if %errorlevel% neq 0 (
        echo Failed to create subfolders inside airflow. Please check your permissions.
        exit /b
    )

    :: Step 4: Initialize Airflow
    echo Initializing Airflow...
    cd airflow
    docker-compose up airflow-init
    if %errorlevel% neq 0 (
        echo Failed to initialize Airflow. Ensure Docker is running.
        exit /b
    )
) else (
    :: If the 'airflow' folder exists, run Airflow
    echo Airflow folder already exists. Starting Airflow services...
    cd airflow
    docker-compose up
    if %errorlevel% neq 0 (
        echo Failed to start Airflow. Ensure Docker is running.
        exit /b
    )
)

echo All tasks completed successfully!
pause
