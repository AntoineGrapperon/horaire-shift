# Data Model: ShiftMed Schema

We will use a relational structure in SQLite to manage the transition from structural templates to assigned schedules.

## 1. Staff & Configuration

### `users`
*   `id`: UUID (Primary Key)
*   `full_name`: String
*   `email`: String (Unique)
*   `role`: Enum (Nurse, Senior Nurse, Resident, Doctor)
*   `contract_hours_per_week`: Float
*   `competencies`: JSON/String (e.g., `["ICU", "ER"]`)
*   `is_active`: Boolean

## 2. Structural Layer (The Template)

### `shift_templates`
*   `id`: UUID (Primary Key)
*   `day_of_week`: Integer (0=Sunday, 6=Saturday)
*   `start_time`: Time (e.g., "08:00")
*   `end_time`: Time (e.g., "20:00")
*   `required_role`: Enum
*   `required_competency`: String (Optional)
*   `quantity`: Integer (How many staff needed for this specific slot)

## 3. Operational Layer (The Roster)

### `shift_instances`
*   `id`: UUID (Primary Key)
*   `template_id`: UUID (Foreign Key, Optional - allows tracking back to template)
*   `date`: Date
*   `start_time`: Time
*   `end_time`: Time
*   `required_role`: Enum
*   `assigned_user_id`: UUID (Foreign Key to `users`, Nullable)
*   `status`: Enum (Unassigned, Draft, Published)

## 4. Preferences & Constraints

### `user_preferences`
*   `id`: UUID (Primary Key)
*   `user_id`: UUID (Foreign Key)
*   `date`: Date
*   `preference_type`: Enum (Preferred-Off, Mandatory-Off, Available)
*   `reason`: String

## Relationships
- **Template -> Instances:** When a manager "expands" a template for a 3-month cycle, the system creates `N` rows in `shift_instances` for every week in that range, where `N = shift_template.quantity`.
- **User -> Instances:** A user is linked to a `shift_instance` via the solver or manual assignment.
- **Constraints:** The solver reads from `users` (contract hours) and `user_preferences` to decide who fills which `shift_instance`.
