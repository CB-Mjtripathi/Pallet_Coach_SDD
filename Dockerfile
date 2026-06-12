FROM node:18-alpine AS ui-build
WORKDIR /app/UI/pallet_coach_ui
COPY UI/pallet_coach_ui/package*.json ./
RUN npm ci
COPY UI/pallet_coach_ui/ ./
RUN npm run build

FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends nginx curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY scripts/ /app/scripts/
COPY --from=ui-build /app/UI/pallet_coach_ui/dist /app/static/
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN pip install --no-cache-dir -r scripts/requirements.txt

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
