from ortools.sat.python import cp_model
from models import Doctor, ActivityInstance, Room
from typing import List, Dict

class ShiftSolver:
    def __init__(self, doctors: List[Doctor], activities: List[ActivityInstance]):
        self.doctors = doctors
        self.activities = activities
        self.model = cp_model.CpModel()
        self.assignments = {} # (doctor_id, activity_id) -> bool var

    def _setup_variables(self):
        for doctor in self.doctors:
            for activity in self.activities:
                self.assignments[(doctor.id, activity.id)] = self.model.NewBoolVar(
                    f'assign_{doctor.id}_{activity.id}'
                )

    def _setup_constraints(self):
        # 1. Each activity must have the required number of doctors
        for activity in self.activities:
            self.model.Add(
                sum(self.assignments[(doctor.id, activity.id)] for doctor in self.doctors) == activity.required_doctors
            )

        # 2. Doctor must have required skills
        for doctor in self.doctors:
            for activity in self.activities:
                required_skills = activity.activity_type.required_skills
                if not required_skills.issubset(doctor.skills):
                    self.model.Add(self.assignments[(doctor.id, activity.id)] == 0)

        # 3. No overlapping activities for a doctor
        for doctor in self.doctors:
            for i, act1 in enumerate(self.activities):
                for j, act2 in enumerate(self.activities):
                    if i >= j:
                        continue
                    # Simple overlap check: (start1 < end2) and (start2 < end1)
                    if act1.start_time < act2.end_time and act2.start_time < act1.end_time:
                        self.model.Add(
                            self.assignments[(doctor.id, act1.id)] + 
                            self.assignments[(doctor.id, act2.id)] <= 1
                        )

        # 4. Respect unavailabilities
        for doctor in self.doctors:
            for activity in self.activities:
                for unavail_start, unavail_end in doctor.unavailabilities:
                    if activity.start_time < unavail_end and unavail_start < activity.end_time:
                        self.model.Add(self.assignments[(doctor.id, activity.id)] == 0)

    def _setup_equity_objective(self):
        # Calculate burden for each doctor
        doctor_burdens = []
        for doctor in self.doctors:
            burden = sum(
                self.assignments[(doctor.id, activity.id)] * activity.activity_type.burden_weight
                for activity in self.activities
            )
            doctor_burdens.append(burden)

        # Define min/max burden variables to minimize the spread (equity)
        # We need to find the range of possible burden values. 
        # For simplicity, let's assume max weight sum is 1000 for now.
        max_possible_burden = sum(a.activity_type.burden_weight for a in self.activities)
        
        min_burden = self.model.NewIntVar(0, max_possible_burden, 'min_burden')
        max_burden = self.model.NewIntVar(0, max_possible_burden, 'max_burden')

        for burden in doctor_burdens:
            self.model.Add(burden >= min_burden)
            self.model.Add(burden <= max_burden)

        # Objective: minimize the difference between max and min burden
        self.model.Minimize(max_burden - min_burden)

    def solve(self):
        self._setup_variables()
        self._setup_constraints()
        self._setup_equity_objective()

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            results = []
            for (d_id, a_id), var in self.assignments.items():
                if solver.Value(var):
                    results.append((d_id, a_id))
            return results, solver.ObjectiveValue()
        else:
            return None, None
