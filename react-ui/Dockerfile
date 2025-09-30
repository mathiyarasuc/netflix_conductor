# Build stage
FROM node:18-alpine AS build
WORKDIR /app

# Accept build arguments
ARG REACT_APP_THEME
ARG REACT_APP_VERSION
ARG REACT_APP_GQL
ARG REACT_APP_GQL_HTTP_PROTOCOL
ARG REACT_APP_GQL_WS_PROTOCOL
ARG REACT_APP_USE_NBB_MESSAGE

# Set as environment variables for build
ENV REACT_APP_THEME=$REACT_APP_THEME
ENV REACT_APP_VERSION=$REACT_APP_VERSION
ENV REACT_APP_GQL=$REACT_APP_GQL
ENV REACT_APP_GQL_HTTP_PROTOCOL=$REACT_APP_GQL_HTTP_PROTOCOL
ENV REACT_APP_GQL_WS_PROTOCOL=$REACT_APP_GQL_WS_PROTOCOL
ENV REACT_APP_USE_NBB_MESSAGE=$REACT_APP_USE_NBB_MESSAGE

# Enable Corepack for Yarn 3.5.0
RUN corepack enable && corepack prepare yarn@3.5.0 --activate

# Copy Yarn 3 configuration
COPY .yarnrc.yml ./
COPY .yarn ./.yarn

COPY package*.json ./
COPY yarn.lock ./
RUN yarn install --immutable
COPY . .
RUN yarn build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]