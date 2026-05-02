from datetime import datetime, timedelta
from models import Skill, Doctor, ActivityType, ActivityInstance, Room
from solver import ShiftSolver

def create_sample_data():
    # Skills
    surgery = Skill("Surgery")
    general = Skill("General Medicine")
    emergency = Skill("Emergency")

    # Doctors
    dr_smith = Doctor(id="smith", name="Dr. Smith", skills={surgery, general})
    dr_jones = Doctor(id="jones", name="Dr. Jones", skills={general, emergency})
    dr_williams = Doctor(id="williams", name="Dr. Williams", skills={surgery, emergency})
    
    # Adding some unavailability
    dr_smith.unavailabilities = [
        (datetime(2024, 5, 1, 8, 0), datetime(2024, 5, 1, 12, 0))
    ]

    doctors = [dr_smith, dr_jones, dr_williams]

    # Activity Types
    appendectomy = ActivityType(id="app", name="Appendectomy", required_skills={surgery}, burden_weight=10)
    checkup = ActivityType(id="chk", name="Regular Checkup", required_skills={general}, burden_weight=2)
    er_shift = ActivityType(id="er", name="ER Shift", required_skills={emergency}, burden_weight=15)

    # Activity Instances (Single Day Sample)
    activities = [
        ActivityInstance(id="a1", activity_type=appendectomy, 
                         start_time=datetime(2024, 5, 1, 9, 0), 
                         end_time=datetime(2024, 5, 1, 11, 0)),
        ActivityInstance(id="a2", activity_type=checkup, 
                         start_time=datetime(2024, 5, 1, 9, 0), 
                         end_time=datetime(2024, 5, 1, 10, 0)),
        ActivityInstance(id="a3", activity_type=er_shift, 
                         start_time=datetime(2024, 5, 1, 13, 0), 
                         end_time=datetime(2024, 5, 1, 17, 0)),
        ActivityInstance(id="a4", activity_type=checkup, 
                         start_time=datetime(2024, 5, 1, 14, 0), 
                         end_time=datetime(2024, 5, 1, 15, 0)),
    ]

    return doctors, activities

def main():
    doctors, activities = create_sample_data()
    solver = ShiftSolver(doctors, activities)
    
    print("Starting solver...")
    assignments, equity_score = solver.solve()

    if assignments:
        print(f"Solution found! Equity Score (spread): {equity_score}")
        # Sort by activity time for readability
        assignments.sort(key=lambda x: x[1]) # x[1] is activity_id
        
        # Create a map for easy lookup
        act_map = {a.id: a for a in activities}
        doc_map = {d.id: d for d in doctors}

        for doc_id, act_id in assignments:
            doc = doc_map[doc_id]
            act = act_map[act_id]
            print(f"  - {doc.name} assigned to {act.activity_type.name} "
                  f"({act.start_time.strftime('%H:%M')} - {act.end_time.strftime('%H:%M')}) "
                  f"Burden: {act.activity_type.burden_weight}")
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
