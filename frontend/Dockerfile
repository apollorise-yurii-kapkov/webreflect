# 1. Install dependencies only when needed
FROM node:18-alpine AS deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package*.json ./
RUN npm ci --legacy-peer-deps

# 2. Rebuild the source code only when needed
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# This will create the folder .next/standalone
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

# 3. Production image, copy all the files and run next
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Copy standalone output first
COPY --from=builder /app/.next/standalone ./standalone

# Copy static assets into standalone directory structure
COPY --from=builder /app/public ./standalone/public
COPY --from=builder /app/.next/static ./standalone/.next/static

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Change directory to standalone folder where server.js and .next/static are
WORKDIR /app/standalone

CMD ["node", "server.js"]
