APP=docker/docker-compose.app.yml
MONGO=docker/docker-compose.mongo.yml
MONGO_EXPRESS=docker/docker-compose.mongo-express.yml
REDIS=docker/docker-compose.redis.yml
DEV=docker/docker-compose.dev.yml
PROXY=docker/docker-compose.proxy.yml
PROXY_TLS=docker/docker-compose.proxy-tls.yml
ENV_FILE = --env-file ./.env


up:
	docker compose -f ${APP} -f ${MONGO} -f ${REDIS} up -d --build

up-dev:
	docker compose -f ${APP} -f ${DEV} -f ${MONGO} -f ${MONGO_EXPRESS} -f ${REDIS} ${ENV_FILE} up --build --abort-on-container-exit --attach app --no-log-prefix

down:
	docker compose -f ${DEV} -f ${APP} -f ${MONGO} -f ${MONGO_EXPRESS} -f ${REDIS} down

up-proxy:
	docker compose -f ${APP} -f ${PROXY} -f ${MONGO} -f ${REDIS} ${ENV_FILE} up -d --build

down-proxy:
	docker compose -f ${APP} -f ${PROXY} -f ${MONGO} -f ${REDIS} down

up-proxy-tls:
	docker compose -f ${APP} -f ${PROXY_TLS} -f ${MONGO} -f ${REDIS} ${ENV_FILE} up -d --build

down-proxy-tls:
	docker compose -f ${APP} -f ${PROXY_TLS} -f ${MONGO} -f ${REDIS} down