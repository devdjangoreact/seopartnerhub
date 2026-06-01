# syntax=docker/dockerfile:1
ARG NODE_VERSION=20-alpine
FROM node:${NODE_VERSION}

ARG FRONTEND_DIR=frontend/starter-kit
ENV FRONTEND_DIR=${FRONTEND_DIR}

RUN apk add --no-cache bash git python3 make g++ libc6-compat \
    && corepack enable \
    && corepack prepare pnpm@10.5.2 --activate

WORKDIR /app

COPY ./compose/local/frontend/start /usr/local/bin/start
RUN sed -i 's/\r$//g' /usr/local/bin/start \
    && chmod +x /usr/local/bin/start

EXPOSE 3000

ENTRYPOINT ["/usr/local/bin/start"]
