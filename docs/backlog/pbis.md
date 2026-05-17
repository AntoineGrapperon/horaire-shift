# Product Backlog Items (PBIs) - ShiftMed (Streamlit Proto)

This backlog outlines the technical tasks required to move from design to a functional Streamlit prototype.

## Milestone 1: Foundation & Core Models (The Skeleton)
*   **PBI-1: Streamlit Scaffolding:** Set up the Streamlit application structure, project configuration, and initial SQLite database connection.
*   **PBI-2: User & Staff Management:** Implement interactive forms for managing `users` (staff profiles, contract hours, roles).
*   **PBI-3: Authentication:** Integrate `streamlit-authenticator` for role-based access control (Admin vs. Clinician).

## Milestone 2: Structural Planning (The "Typical Week")
*   **PBI-4: Shift Template Designer:** Build a Streamlit interface to define and manage `shift_templates` (The "Typical Week" baseline).
*   **PBI-5: Template Expander Service:** Develop the logic to take a `shift_template` and a date range to generate empty `shift_instances` in the database.
*   **PBI-6: Roster Dashboard:** Create the initial dashboard to visualize the generated empty roster.

## Milestone 3: The Intelligence Layer (The Solver)
*   **PBI-7: Constraint Modeling:** Map the data model to Google OR-Tools (Hard constraints: rest periods, roles; Soft constraints: preferences).
*   **PBI-8: Solver Integration:** Create the "Solve" button in the Streamlit UI that triggers the assignment process for a specific date range.
*   **PBI-9: Manual Override & Validation:** Interactive roster editing with real-time validation against hard constraints.

## Milestone 4: Clinician Experience & Portal
*   **PBI-10: Clinician Monthly View:** Build a mobile-friendly view for staff to see their assigned shifts.
*   **PBI-11: Preference Submission:** Interactive calendar for clinicians to mark "Preferred-Off" dates before a solver run.
*   **PBI-12: Shift Swap Workflow:** Implement a simple request-approval interface for staff trading shifts.

## Milestone 5: Deployment & Hardening
*   **PBI-13: Streamlit Dockerization:** Create a production-ready Docker image for the Streamlit app.
*   **PBI-14: Automated Backups:** Script for daily SQLite database snapshots.
*   **PBI-15: Final Compliance Audit:** Ensure all labor law constraints are strictly enforced by the solver and displayed in the UI.
