export DATABASE_HOST=127.0.0.1
export DATABASE_PORT=3306
export DATABASE_USER=root
export DATABASE_PASSWORD=testDB
export DATABASE_NAME=test
python manage.py makemigrations
python manage.py migrate