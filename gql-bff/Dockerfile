FROM node:18-alpine

WORKDIR /app

# Copy everything
COPY . .

# Install dependencies
RUN yarn install

# Expose port
EXPOSE 5000

# Start the app
CMD ["yarn", "start"]