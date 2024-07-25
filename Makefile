APP=docker-compose.yml
DEV=docker-compose.dev.yml
DEPLOY=docker-compose.deploy.yml

ENV_FILE = --env-file ./.env

APP_SERVICE=app


up-dev:
	docker compose -f ${APP} -f ${DEV} ${ENV_FILE} up --build -d

down:
	docker compose -f ${APP} -f ${DEV} down

shell:
	docker compose -f ${APP} exec ${APP_SERVICE} bash


docker-deploy:
	docker compose -f ${APP} -f ${DEPLOY} ${ENV_FILE} up --build -d


create-env-secrets:
	kubectl create secret generic auth-server-env-secret --from-env-file=.env.deploy

deploy:
	kubectl apply -f ./kubernetes/config-map-env.yaml
	kubectl apply -f ./kubernetes/config-map.yaml
	kubectl apply -f ./kubernetes/secret.yaml
	kubectl apply -f ./kubernetes/deployment.yaml
