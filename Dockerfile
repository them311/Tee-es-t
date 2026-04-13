FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci --omit=dev && npm install vite @vitejs/plugin-react

# Copy source
COPY . .

# Build frontend
RUN npx vite build

# Clean dev deps after build
RUN npm prune --production

# Data volume
RUN mkdir -p server/data
VOLUME /app/server/data

EXPOSE 3001

ENV NODE_ENV=production
ENV PORT=3001

CMD ["node", "server/index.js"]
