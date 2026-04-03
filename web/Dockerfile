FROM node:20-alpine

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build && npm install -g serve

EXPOSE 3000

CMD ["serve", "-s", "out", "-l", "3000"]
