# VPS Deployment Strategy

## 1. Containerization (Docker)
*   A single `docker-compose.yml` defining two services:
    *   `api`: FastAPI + SQLite + Solver.
    *   `gateway`: Nginx (to serve the React frontend and proxy API requests).

## 2. Reverse Proxy & SSL
*   **Nginx:** Handles SSL termination (via Let's Encrypt/Certbot).
*   **Security:** Only ports 80 and 443 are exposed to the internet.

## 3. Database Backups
*   Since SQLite is a single file, backups are a simple `cp` command to a secure S3 bucket or external volume, triggered via a daily cron job.

## 4. Performance Tuning
*   **Worker Count:** Limited to 2-4 Uvicorn workers to stay within small VPS RAM limits (e.g., 1GB - 2GB RAM).
*   **Solver Timeout:** Set to 30-60 seconds to prevent CPU spikes from hanging the server.
