# Technical Stack: Lightweight & Efficient

To ensure high performance on a small VPS while maintaining developer productivity, we will use the following stack:

## 1. Backend: Python + FastAPI
*   **Why:** Extremely fast execution, native asynchronous support, and excellent integration with mathematical solver libraries.
*   **API Style:** RESTful API with automated OpenAPI documentation.

## 2. Database: SQLite
*   **Why:** Zero-config, single-file database. On a small VPS, it eliminates the memory overhead of a separate PostgreSQL/MySQL process.
*   **Scalability:** More than sufficient for hospital departments (hundreds of staff, thousands of shifts).

## 3. The Solver: Google OR-Tools (CP-SAT)
*   **Why:** A world-class constraint programming solver. It is lightweight in terms of setup but powerful enough to handle complex medical scheduling constraints in seconds.

## 4. Frontend: React (Vite) + Tailwind CSS
*   **Why:** Vite provides a lightning-fast build process. Tailwind keeps CSS bundles small.
*   **Delivery:** Served as static files via the FastAPI backend or Nginx to save memory.

## 5. Authentication: JWT (JSON Web Tokens)
*   **Why:** Stateless authentication reduces the need for server-side session storage.
