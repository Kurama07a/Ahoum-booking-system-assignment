@echo off
echo Starting Backend Services...
echo.
echo This will start:
echo - Backend Service (Port 5000)
echo - CRM Service (Port 5001) 
echo - Notification Service (Port 5002)
echo.

docker-compose -f docker-compose.backend.yml down
docker-compose -f docker-compose.backend.yml up --build

pause
