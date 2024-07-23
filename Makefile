APP=docker-compose.yml
DEV=docker-compose.dev.yml

ENV_FILE = --env-file ./.env

APP_SERVICE=app


up-dev:
	docker compose -f ${APP} -f ${DEV} ${ENV_FILE} up --build -d

down:
	docker compose -f ${APP} -f ${DEV} down

shell:
	docker compose -f ${APP} exec ${APP_SERVICE} bash

