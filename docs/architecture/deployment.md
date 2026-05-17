# VPS Deployment Strategy (Streamlit Proto)

## 1. Containerization (Docker)
*   A single `Dockerfile` or `docker-compose.yml` defining the main service:
    *   `app`: Streamlit Application + SQLite + Solver.
*   **Port:** Streamlit typically runs on port 8501.

## 2. Reverse Proxy & SSL
*   **Nginx (Optional for Proto):** Can still be used to handle SSL termination (via Let's Encrypt/Certbot) and map domain to port 8501.
*   **Direct Access:** For early prototyping, the app can be accessed directly via the VPS IP and port.

## 3. Database Backups
*   Since SQLite is a single file, backups are a simple `cp` command to a secure S3 bucket or external volume, triggered via a daily cron job.

## 4. Performance Tuning
*   **Memory Management:** Streamlit can be memory-intensive with large datasets; limit data caching to stay within VPS RAM limits.
*   **Solver Timeout:** Set to 30-60 seconds to prevent CPU spikes from hanging the server.
