# Stage 1: Build the app
FROM node:20-alpine AS build

WORKDIR /app

RUN apk update
RUN apk add zip --no-cache
RUN apk add wget --no-cache

RUN wget 'https://github.com/drawdb-io/drawdb/archive/refs/heads/main.zip'
RUN unzip main.zip

WORKDIR /app/drawdb-main
RUN npm ci

ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN npm run build

# Stage 2: Setup the Nginx Server to serve the app
FROM docker.io/library/nginx:stable-alpine3.17 AS production
COPY --from=build /app/drawdb-main/dist /usr/share/nginx/html
RUN echo 'server { listen 80; server_name _; root /usr/share/nginx/html;  location / { try_files $uri /index.html; } }' > /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]