from ortools.sat.python import cp_model
from models import Doctor, ActivityInstance, Room
from typing import List, Dict

class ShiftSolver:
    def __init__(self, doctors: List[Doctor], activities: List[ActivityInstance], rooms: List[Room]):
        self.doctors = doctors
        self.activities = activities
        self.rooms = rooms
        self.model = cp_model.CpModel()
        self.assignments = {} # (doctor_id, activity_id) -> bool var
        self.room_assignments = {} # (room_id, activity_id) -> bool var

    def _setup_variables(self):
        # Doctor assignments
        for doctor in self.doctors:
            for activity in self.activities:
                self.assignments[(doctor.id, activity.id)] = self.model.NewBoolVar(
                    f'assign_doc_{doctor.id}_{activity.id}'
                )
        
        # Room assignments
        for room in self.rooms:
            for activity in self.activities:
                self.room_assignments[(room.id, activity.id)] = self.model.NewBoolVar(
                    f'assign_room_{room.id}_{activity.id}'
                )

    def _setup_constraints(self):
        # --- DOCTOR CONSTRAINTS ---
        for activity in self.activities:
            self.model.Add(
                sum(self.assignments[(doctor.id, activity.id)] for doctor in self.doctors) == activity.required_doctors
            )

        for doctor in self.doctors:
            for activity in self.activities:
                if not activity.activity_type.required_skills.issubset(doctor.skills):
                    self.model.Add(self.assignments[(doctor.id, activity.id)] == 0)

        for doctor in self.doctors:
            for i, act1 in enumerate(self.activities):
                for j, act2 in enumerate(self.activities):
                    if i >= j: continue
                    if act1.start_time < act2.end_time and act2.start_time < act1.end_time:
                        self.model.Add(self.assignments[(doctor.id, act1.id)] + self.assignments[(doctor.id, act2.id)] <= 1)

        for doctor in self.doctors:
            for activity in self.activities:
                for unavail_start, unavail_end in doctor.unavailabilities:
                    if activity.start_time < unavail_end and unavail_start < activity.end_time:
                        self.model.Add(self.assignments[(doctor.id, activity.id)] == 0)

        # --- ROOM CONSTRAINTS ---
        for activity in self.activities:
            # Each activity must have exactly one room
            self.model.Add(
                sum(self.room_assignments[(room.id, activity.id)] for room in self.rooms) == 1
            )

            # Room must have required equipment
            for room in self.rooms:
                if not activity.activity_type.required_equipment.issubset(room.equipment):
                    self.model.Add(self.room_assignments[(room.id, activity.id)] == 0)
            
            # If a room is fixed in the activity instance, enforce it
            if activity.fixed_room:
                for room in self.rooms:
                    if room.id != activity.fixed_room.id:
                        self.model.Add(self.room_assignments[(room.id, activity.id)] == 0)

        # No overlapping activities in the same room
        for room in self.rooms:
            for i, act1 in enumerate(self.activities):
                for j, act2 in enumerate(self.activities):
                    if i >= j: continue
                    if act1.start_time < act2.end_time and act2.start_time < act1.end_time:
                        self.model.Add(self.room_assignments[(room.id, act1.id)] + self.room_assignments[(room.id, act2.id)] <= 1)

        # --- GROUP CONSTRAINTS ---
        activity_groups = {}
        for activity in self.activities:
            if activity.group_id:
                if activity.group_id not in activity_groups:
                    activity_groups[activity.group_id] = []
                activity_groups[activity.group_id].append(activity)
        
        for group_id, group_activities in activity_groups.items():
            if len(group_activities) > 1:
                first_act = group_activities[0]
                for other_act in group_activities[1:]:
                    for doctor in self.doctors:
                        self.model.Add(
                            self.assignments[(doctor.id, first_act.id)] == self.assignments[(doctor.id, other_act.id)]
                        )

    def _setup_equity_objective(self):
        # 1. Weighted Burden Points for Doctors (Harder Equity)
        doctor_burdens = []
        for doctor in self.doctors:
            burden = doctor.historical_burden + sum(
                self.assignments[(doctor.id, activity.id)] * activity.activity_type.burden_weight
                for activity in self.activities
            )
            doctor_burdens.append(burden)

        max_possible_burden = sum(a.activity_type.burden_weight for a in self.activities) + max((d.historical_burden for d in self.doctors), default=0)
        min_burden = self.model.NewIntVar(0, max_possible_burden, 'min_burden')
        max_burden = self.model.NewIntVar(0, max_possible_burden, 'max_burden')

        for burden in doctor_burdens:
            self.model.Add(burden >= min_burden)
            self.model.Add(burden <= max_burden)

        # 2. Preference Penalties (Soft Constraints)
        preference_penalties = []
        from models import PreferenceType
        for doctor in self.doctors:
            for pref in doctor.preferences:
                for activity in self.activities:
                    is_conflict = False
                    
                    if pref.type == PreferenceType.AVOID_DAY:
                        if activity.start_time.weekday() == pref.day_of_week:
                            is_conflict = True
                    
                    elif pref.type == PreferenceType.AVOID_TIME_RANGE:
                        # Check time overlap within the same day
                        p_start = pref.start_time.time()
                        p_end = pref.end_time.time()
                        a_start = activity.start_time.time()
                        a_end = activity.end_time.time()
                        
                        if a_start < p_end and p_start < a_end:
                            is_conflict = True
                    
                    if is_conflict:
                        # penalty = assignment * weight
                        penalty = self.model.NewIntVar(0, pref.weight, f'pref_penalty_{doctor.id}_{activity.id}')
                        self.model.Add(penalty == self.assignments[(doctor.id, activity.id)] * pref.weight)
                        preference_penalties.append(penalty)

        # Main Objective: 
        # Minimize (Spread of Burden * 10) + Total Preference Penalties
        # We multiply equity by 10 to give it higher priority than a single small preference.
        equity_weight = 10
        total_penalties = sum(preference_penalties)
        self.model.Minimize(equity_weight * (max_burden - min_burden) + total_penalties)

    def solve(self):
        self._setup_variables()
        self._setup_constraints()
        self._setup_equity_objective()

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            doc_results = []
            for (d_id, a_id), var in self.assignments.items():
                if solver.Value(var): doc_results.append((d_id, a_id))
            
            room_results = []
            for (r_id, a_id), var in self.room_assignments.items():
                if solver.Value(var): room_results.append((r_id, a_id))
                
            return {
                "doctor_assignments": doc_results,
                "room_assignments": room_results,
                "equity_score": solver.ObjectiveValue()
            }
        return None
