# Multi-stage build for production optimization
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies only
# --omit=dev is the modern equivalent of --only=production
RUN npm ci --omit=dev && npm cache clean --force
RUN npm audit fix --audit-level=none && npm cache clean --force

# Production stage
FROM node:20-alpine
 
# Install curl for healthchecks
RUN apk upgrade --no-cache && apk add --no-cache curl

# Set working directory
WORKDIR /app

# Copy dependencies from builder stage
COPY --from=builder /app/node_modules ./node_modules

# Copy application source code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY package*.json ./

# Create logs directory for winston
RUN mkdir -p logs && chmod 775 logs

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001 -G nodejs
RUN chown -R nodejs:nodejs /app

USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:3000/health/ || exit 1

# Start application
CMD ["node", "src/app.js"]
