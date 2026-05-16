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

## 4. Client Layer (The UI)
*   Fetches `ShiftInstances` via a `/shifts` endpoint.
*   Displays a monthly calendar view with color-coded assignments and conflict warnings.
