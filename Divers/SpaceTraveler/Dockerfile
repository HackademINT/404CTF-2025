FROM node:22-alpine AS base

# Install dependencies in order to build the app
RUN apk add --no-cache g++ make py3-pip libc6-compat
WORKDIR /app

# Don't send data to Vercel
# https://vercel.com/docs/concepts/next.js/telemetry
ENV NEXT_TELEMETRY_DISABLED=1

# Install dependencies
FROM base AS deps
COPY package*.json ./
RUN ["npm", "ci"]

# Build for production
FROM base AS build
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build


# Production image
FROM base AS production
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
RUN mkdir .next
RUN chown nextjs:nodejs .next

COPY --from=build /app/public ./public
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./package.json
COPY --from=build --chown=nextjs:nodejs /app/.next ./.next

USER nextjs

EXPOSE 3000

RUN ["ls", "-liar"]
RUN ["pwd"]
CMD ["npm", "start"]
