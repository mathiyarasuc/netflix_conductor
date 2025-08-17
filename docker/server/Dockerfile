#
# conductor:ui - UI Only Build (Server uses working image)
#
FROM alpine:3.18 AS builder
LABEL maintainer="Netflix OSS <conductor@netflix.com>"

# Install dependencies for UI build only
RUN apk add --update nodejs npm yarn curl

# Build UI
COPY . /conductor
WORKDIR /conductor/ui

# Include monaco sources into bundle (instead of using CDN)
ENV REACT_APP_MONACO_EDITOR_USING_CDN=false
RUN yarn install && cp -r node_modules/monaco-editor public/ && yarn build

# ===========================================================================================================
# Final stage - nginx for UI
# ===========================================================================================================
FROM nginx:alpine
LABEL maintainer="Netflix OSS <conductor@netflix.com>"

# Copy compiled UI assets
COPY --from=builder /conductor/ui/build /usr/share/nginx/html
COPY --from=builder /conductor/docker/ui/nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=60s --timeout=30s --retries=10 \
    CMD curl -f http://localhost:5000 || exit 1

EXPOSE 5000
CMD ["nginx", "-g", "daemon off;"]
