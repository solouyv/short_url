-include Makefile.local

.PHONY: config
## Show current docker-compose config
config:
	docker-compose -f docker-compose.yml config

.PHONY: config-test
## Show docker-compose test config
config-test:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml config

.PHONY: poetry-lock
poetry-lock:
	docker-compose run --rm api poetry lock

.PHONY: poetry-add
poetry-add:
	# make poetry-add pkg=black
	docker-compose run --rm api poetry add $(pkg)

.PHONY: prereq
prereq:
	docker network create network || true

.PHONY: prereq-tests
prereq-tests: | prereq
	docker-compose -f docker-compose.yml -f docker-compose.test.yml down -v

.PHONY: run
## Run service
run: | prereq
	docker-compose up -d

.PHONY: logs
## Open service logs
logs:
	docker-compose logs -f

.PHONY: status
## Get running status information
status:
	docker-compose ps

.PHONY: stop
## Stop runned services
stop:
	docker-compose stop

.PHONY: down
down:
	docker-compose down
	docker-compose -f docker-compose.yml -f docker-compose.test.yml down

.PHONY: clean-volume
clean-volume:
	docker volume prune -f

.PHONY: build
## Build containers
build:
	docker-compose build

.PHONY: migrate
## Apply database migrations
migrate:
	docker-compose run --rm migrator update

.PHONY: recreate
recreate: | down clean-volume run migrate

.PHONY: shell-app
shell-app:
	docker-compose exec -u "$(CURRENT_UID)" api /bin/sh

.PHONY: shell-db
## Open db shell
shell-db:
	docker-compose exec -u "$(CURRENT_UID)" database psql -U postgres short_url

.PHONY: format
## Apply black & isort code formatting
format:
	docker-compose run --rm -u "$(CURRENT_UID)" api black --exclude 'vendors' -l 130 .
	docker-compose run --rm -u "$(CURRENT_UID)" api isort --settings-path /app/setup.cfg .

.PHONY: format-check
## Check for correct code format
format-check:
	docker-compose run --rm -u "$(CURRENT_UID)" api black --exclude 'vendors' -l 130 --check .
	docker-compose run --rm -u "$(CURRENT_UID)" api isort --settings-path /app/setup.cfg --check-only .

.PHONY: lint
## Check code using linters
lint:
	docker-compose run --rm api flake8 .

.PHONY: mypy
## Check code using mypy
mypy:
	docker-compose run --rm api mypy --config-file /app/setup.cfg .

.PHONY: tests-unit
## Run unit tests
tests-unit:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm api coverage run -a -m pytest --pdbcls=IPython.terminal.debugger:Pdb -s -vv -x --ff tests/unit

.PHONY: tests-integration
## Run integration tests
tests-integration:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml rm -f
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d test-database
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm migrator update
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm api coverage run -a -m pytest --pdbcls=IPython.terminal.debugger:Pdb -s -vv -x --ff tests/integration
	docker-compose -f docker-compose.yml -f docker-compose.test.yml rm -f

.PHONY: tests
## Run unit & integration tests
tests:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml rm -f
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d test-database
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm migrator update
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm api coverage run -a -m pytest --pdbcls=IPython.terminal.debugger:Pdb -s -vv -x tests
	docker-compose -f docker-compose.yml -f docker-compose.test.yml rm -f

.PHONY: coverage
## Get code coverage report
coverage:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm api coverage report -i --omit=/opt/venv/*,/vendors/*

.PHONY: ci
## Run CI checks
ci: | prereq-tests format-check lint mypy tests coverage prereq-tests

