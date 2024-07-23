FROM node:18-alpine as BUILD_STAGE

WORKDIR /app

COPY . /app

RUN npm install \
    && npm run build

FROM nginx:stable-alpine3.19-slim

COPY --from=BUILD_STAGE /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf


CMD ["nginx", "-g", "daemon off;"]
