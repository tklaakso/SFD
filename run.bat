@echo off
cd client
call npm run build
cd ../server
call activate server
start cmd /k python manage.py runserver
cd ../geographic_service
call activate simulator
python run.py osm