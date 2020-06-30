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
	docker-compose exec postgres psql -U app -d campi
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
	docker-compose exec postgres psql -U app -d postgres -c 'DROP DATABASE campi;'
wipe: blank
	docker-compose exec postgres psql -U app -d postgres -c 'CREATE DATABASE campi;'
	$(MAKE) restart
dumpusers:
	docker-compose exec rest python manage.py dumpdata --indent 2 auth authtoken -e auth.permission -o /vol/data/users.json
restoreusers:
	docker-compose exec rest python manage.py loaddata /vol/data/users.json
backup:
	docker-compose exec postgres pg_dump -U app -d campi > data/bkp/bk.sql
restore: wipe
	docker-compose exec -T postgres psql -U app -d campi < data/bkp/bk.sql
resetmigrations:
	find rest -type f -regex ".*/migrations/[0-9].*" -exec rm {} \;
dumptest:
	docker-compose exec rest python manage.py dumpdata --indent 2 -e silk -e sessions -e contenttypes -e auth.permission -e auth.group -o campi/fixtures/test.json