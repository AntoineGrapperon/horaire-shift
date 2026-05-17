# ShiftMed: Medical Shift Scheduling Platform

ShiftMed is a specialized web application designed to automate and optimize the complex task of creating medical staff schedules. It balances institutional requirements, labor laws, and staff well-being through intelligent automation.

## Core Mission
To eliminate the manual overhead of hospital rostering while ensuring 100% coverage safety and improving clinician work-life balance.

## Key Features
- **Constraint-Based Solver:** Automated shift generation respecting medical competencies and rest requirements.
- **Compliance Engine:** Real-time validation against labor laws and internal hospital policies.
- **Staff Portal:** Mobile-first interface for viewing shifts, requesting swaps, and managing availability.
- **Coverage Heatmaps:** Instant visual identification of staffing gaps or over-scheduling.

## Technical Vision
ShiftMed is built as a unified, lightweight Python application powered by **Streamlit**. It integrates the UI, database management (SQLite), and the mathematical optimization engine (Google OR-Tools) into a single, high-performance container. This architecture ensures rapid deployment on small VPS instances without the overhead of separate frontend/backend pipelines.

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Docker (optional)

### Local Setup
1. Clone the repository.
2. Run the setup and start script:
   ```bash
   ./start-local.sh
   ```
3. Access the application at `http://localhost:8501`.

### Docker Setup
1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```
2. Access the application at `http://localhost:8501`.
