1. pip install -r requirements.txt
2. make sendgrid.env file:
	paste the given content into it.
3. source ./sendgrid.env
4. create mysql db named as "api"
4. python manage.py makemigrations
5. python manage.py migrate
6. hit the api 127.0.0.1:8000/api/1/send-data-ingestion/ with POST and data(given or any)