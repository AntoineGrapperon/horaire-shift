# Technical Stack: Lightweight & Efficient

To ensure high performance on a small VPS while maintaining developer productivity, we will use the following stack:

## 1. Core Logic: Python
*   **Why:** Native integration with mathematical solver libraries and data processing tools.
*   **Structure:** Modular Python services for template expansion, constraint modeling, and database interactions.

## 2. Database: SQLite
*   **Why:** Zero-config, single-file database. On a small VPS, it eliminates the memory overhead of a separate PostgreSQL/MySQL process.
*   **Scalability:** More than sufficient for hospital departments (hundreds of staff, thousands of shifts).

## 3. The Solver: Google OR-Tools (CP-SAT)
*   **Why:** A world-class constraint programming solver. It is lightweight in terms of setup but powerful enough to handle complex medical scheduling constraints in seconds.

## 4. Unified Application: Streamlit
*   **Why:** Enables rapid development of data-rich dashboards and interactive shift management tools using pure Python. 
*   **Consolidation:** The frontend and backend logic are unified within the Streamlit application, eliminating the need for REST APIs or separate build pipelines for internal tooling.
*   **Delivery:** Served as a single containerized Python application, providing a seamless reactive interface.

## 5. Authentication: Streamlit Authenticator / JWT
*   **Why:** Provides secure access control for different personas (Managers vs. Clinicians) directly within the Streamlit app.
