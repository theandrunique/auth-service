APP=docker/app-compose.yml
MONGO=docker/mongo-compose.yml
REDIS=docker/redis-compose.yml
DEV=docker/dev-compose.yml


up:
	docker compose -f ${APP} -f ${MONGO} -f ${REDIS} up -d --build

up-dev:
	docker compose -f ${DEV} -f ${MONGO} -f ${REDIS} up --build --abort-on-container-exit --attach dev-app --no-log-prefix

down:
	docker compose -f ${DEV} -f ${APP} -f ${MONGO} -f ${REDIS} down