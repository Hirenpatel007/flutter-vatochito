run:
	python manage.py runserver

worker:
	celery -A vatochito_backend worker -l info

beat:
	celery -A vatochito_backend beat -l info

migrate:
	python manage.py migrate

createsuperuser:
	python manage.py createsuperuser

lint:
	flake8
