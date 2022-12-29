cd client
call npm run build
cd ../server
call activate server
python manage.py runserver