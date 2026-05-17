# System Components & Data Flow

## 1. Structural Layer (The Template)
*   Managers define `ShiftTemplates` (Time, Role, DayOfWeek).
*   Data is stored in the `Template` table.

## 2. Operational Layer (The Roster)
*   A "Template Expander" script takes a date range and creates `ShiftInstance` records in the database.
*   Initially, these instances have `assigned_user_id = NULL`.

## 3. Intelligence Layer (The Solver)
*   **Input:** Staff availability, contract hours, and empty `ShiftInstances`.
*   **Processing:** The Python backend builds a mathematical model and sends it to OR-Tools.
*   **Output:** A list of `(ShiftID, UserID)` pairs written back to the database.

## 4. Client Layer (The Streamlit UI)
*   Interacts directly with the Intelligence Layer via internal Python function calls or a shared database.
*   Displays a monthly calendar view with color-coded assignments and conflict warnings.
*   Provides interactive widgets for managers to trigger the Solver and for clinicians to view their shifts.
