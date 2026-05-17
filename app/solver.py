from ortools.sat.python import cp_model
from sqlalchemy.orm import Session
from .models import User, ShiftInstance, ShiftStatus

def run_solver(db: Session):
    """
    Simple OR-Tools solver to assign users to shifts.
    """
    # 1. Get data
    users = db.query(User).filter(User.is_active == True).all()
    # Only try to assign unassigned shifts
    shifts = db.query(ShiftInstance).filter(ShiftInstance.assigned_user_id == None).all()
    
    if not users or not shifts:
        return 0, "No users or unassigned shifts found."

    model = cp_model.CpModel()
    
    # 2. Variables
    # x[s, u] is true if shift s is assigned to user u
    x = {}
    for s in shifts:
        for u in users:
            x[s.id, u.id] = model.NewBoolVar(f'shift_{s.id}_user_{u.id}')

    # 3. Constraints
    
    # Each shift must be assigned to exactly one user (if possible)
    # Note: If we want to allow unassigned shifts, we'd use <= 1
    for s in shifts:
        model.Add(sum(x[s.id, u.id] for u in users) <= 1)

    # Role matching (Hard constraint)
    for s in shifts:
        for u in users:
            if u.role != s.required_role:
                model.Add(x[s.id, u.id] == 0)

    # Max 1 shift per day per person (Hard constraint)
    # Group shifts by date
    shifts_by_date = {}
    for s in shifts:
        if s.date not in shifts_by_date:
            shifts_by_date[s.date] = []
        shifts_by_date[s.date].append(s)
        
    for d, daily_shifts in shifts_by_date.items():
        for u in users:
            model.Add(sum(x[s.id, u.id] for s in daily_shifts) <= 1)

    # 4. Objective: Maximize assignments
    model.Maximize(sum(x[s.id, u.id] for s in shifts for u in users))

    # 5. Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        assignments_made = 0
        for s in shifts:
            for u in users:
                if solver.Value(x[s.id, u.id]):
                    s.assigned_user_id = u.id
                    s.status = ShiftStatus.PUBLISHED
                    assignments_made += 1
        db.commit()
        return assignments_made, "Success"
    else:
        return 0, "No feasible solution found."
