# Deployment Guide

## Local Docker
1. `docker compose up --build`
2. Backend at `http://localhost:8000`, frontend at `http://localhost:5173`

## Render
1. Create Web Service for backend using `docker/backend.Dockerfile`
2. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --app-dir backend`
3. Add persistent disk for `/app/data`

## Railway
1. Import repo and deploy backend service
2. Configure environment variables from `.env.example`
3. Expose port `8000`

## HuggingFace Spaces (Docker)
1. Use Docker SDK space
2. Point to backend Dockerfile
3. Expose FastAPI app and optional static frontend build

## AWS EC2
1. Install Docker + Docker Compose
2. Clone project and run `docker compose up -d --build`
3. Configure Nginx reverse proxy and TLS (Let’s Encrypt)
4. Enable CloudWatch logs and restart policy

.\.venv\Scripts\Activate
uvicorn app.main:app --reload --app-dir backend
 npm run dev

