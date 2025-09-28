FROM node:18-alpine
WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Copy everything
COPY . .
# Install dependencies
RUN yarn install
# Expose port
EXPOSE 5000
# Start the app
CMD ["yarn", "start"]
