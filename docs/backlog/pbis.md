# Product Backlog Items (PBIs) - ShiftMed

This backlog outlines the technical tasks required to move from design to a functional MVP.

## Milestone 1: Foundation & Core Models (The Skeleton)
*   **PBI-1: Project Scaffolding:** Set up FastAPI backend, Docker configuration, and initial SQLite database connection.
*   **PBI-2: User & Staff Management API:** Implement CRUD endpoints for `users` (staff profiles, contract hours, roles).
*   **PBI-3: Authentication System:** Implement JWT-based login and role-based access control (Admin vs. Clinician).

## Milestone 2: Structural Planning (The "Typical Week")
*   **PBI-4: Shift Template Engine:** Implement API endpoints to create and manage `shift_templates` (The "Typical Week" baseline).
*   **PBI-5: Template Expander Service:** Develop the logic to take a `shift_template` and a date range (e.g., 3 months) to generate empty `shift_instances`.
*   **PBI-6: Template Management UI:** Build the initial frontend view to define the weekly structural shifts.

## Milestone 3: The Intelligence Layer (The Solver)
*   **PBI-7: Constraint Modeling:** Map the data model to Google OR-Tools (Hard constraints: rest periods, roles; Soft constraints: preferences).
*   **PBI-8: Solver Integration:** Create the `/solver/run` endpoint that triggers the assignment process for a specific date range.
*   **PBI-9: Manual Override API:** Endpoints to manually change an `assigned_user_id` and validate against hard constraints.

## Milestone 4: Clinician Experience & Portal
*   **PBI-10: Mobile Calendar View:** Build the React frontend for staff to view their assigned shifts for the month.
*   **PBI-11: Preference Submission:** UI and API for clinicians to mark "Preferred-Off" dates before a solver run.
*   **PBI-12: Shift Swap Workflow:** Implement the request-approval logic for staff trading shifts.

## Milestone 5: Deployment & Hardening
*   **PBI-13: Production Dockerization:** Optimize Docker images and set up Nginx reverse proxy.
*   **PBI-14: Automated Backups:** Script for daily SQLite database snapshots.
*   **PBI-15: Final Compliance Audit:** Ensure all labor law constraints (e.g., maximum work hours) are strictly enforced by the solver and API.
