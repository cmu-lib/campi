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
	docker-compose exec postgres psql -U app -d pp
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
blank: stop
	docker-compose exec postgres psql -U app -d postgres -c 'DROP DATABASE pp;'
wipe: blank
	docker-compose exec postgres psql -U app -d postgres -c 'CREATE DATABASE pp;'
	$(MAKE) restart
dumpusers:
	docker-compose exec web python manage.py dumpdata --indent 2 auth authtoken -e auth.permission -o users.json
restoreusers:
	docker-compose exec web python manage.py loaddata users.json
backup:
	docker-compose exec postgres pg_dump -U app -d pp > data/bkp/bk.sql
