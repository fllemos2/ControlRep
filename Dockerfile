# ─── Stage 1: Build do frontend (Vue + Vite) ─────────────────────────────────
FROM node:20-alpine AS frontend

WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


# ─── Stage 2: Backend Python (produção) ──────────────────────────────────────
FROM python:3.12-slim AS production

WORKDIR /app

# Dependências do sistema para psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Dependências Python
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Código do backend
COPY backend/ ./backend/

# Frontend buildado (o main.py espera ../../frontend/dist relativo a app/main.py)
COPY --from=frontend /build/dist ./frontend/dist

WORKDIR /app/backend

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
