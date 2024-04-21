up:
	docker compose -f docker/app-compose.yml -f docker/mongo-compose.yml -f docker/redis-compose.yml up -d --build

up-dev:
	docker compose -f docker/dev-compose.yml -f docker/mongo-compose.yml -f docker/redis-compose.yml up --build --abort-on-container-exit --attach dev-app --no-log-prefix

down:
	docker compose -f docker/dev-compose.yml -f docker/app-compose.yml -f docker/mongo-compose.yml -f docker/redis-compose.yml down