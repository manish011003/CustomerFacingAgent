# Passenger chat + operations dashboard + FastAPI, one origin.
FROM node:20-alpine AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
ENV EXPORT=1 NEXT_PUBLIC_OPS_URL=/ops
RUN npm run build

FROM node:20-alpine AS ops
WORKDIR /ops
COPY frontend-manager/package.json ./
RUN npm install
COPY frontend-manager/ .
ENV EXPORT=1
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
COPY --from=web /web/out ./static/web
COPY --from=ops /ops/out ./static/ops
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
