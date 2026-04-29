# note: this Dockerfile expects to be built from the project root, not from
# api/, because it pulls in the frontend source for the SPA build stage.
# docker-compose.yaml sets `context: .` and `dockerfile: api/Dockerfile`.

# build the SPA into /frontend/dist so the runtime stage can copy it next to
# the python app. the api then serves index.html + /assets/* itself, which
# kills CORS (same origin) and means one container is the whole user-facing
# surface. requires node 20+ for vite 5.
FROM node:20-alpine AS frontend-build

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund

# vite bakes VITE_* into the bundle at build time. relative /v1 keeps the
# SPA same-origin both in this image and in `npm run dev` (vite proxy).
ARG VITE_API_BASE_URL=/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY frontend/ ./
RUN npm run build


# runtime stage. python image, uv-managed venv, dist/ baked in at /app/static.
FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY api/pyproject.toml api/uv.lock* ./
RUN uv sync --frozen --no-cache

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

COPY api/ .
COPY --from=frontend-build /frontend/dist ./static

CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8080", "--timeout", "120"]
