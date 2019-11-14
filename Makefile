start:
	docker-compose up

rebuild:
	docker-compose build --no-cache

migrate:
	docker-compose exec -u root app python manage.py migrate

createsuperuser:
	docker-compose exec -u root app python manage.py createsuperuser

shell:
	docker-compose exec app /bin/sh

django_shell:
	docker-compose exec app python manage.py shell

test:
	docker-compose exec app python manage.py test

collectstatic:
	docker-compose exec app python manage.py collectstatic --noinput

stop:
	docker-compose stop app
