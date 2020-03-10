all:
	docker-compose up
detached:
	docker-compose up -d
stop:
	docker-compose stop rest
down:
	docker-compose down
serve:
	cd vue; npm run serve
attach:
	docker-compose exec rest bash
db:
	docker-compose exec postgres psql -U app -d argus
restart:
	docker-compose restart rest nginx
check:
	docker-compose exec rest python manage.py check
shell:
	docker-compose exec rest python manage.py shell
build:
	docker-compose build
rebuild:
	docker-compose build --no-cache rest
test:
	docker-compose exec rest python manage.py test
