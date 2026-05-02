from datetime import datetime, timedelta
from models import Skill, Doctor, ActivityType, ActivityInstance, Room, Equipment
from solver import ShiftSolver

def create_sample_data():
    # Skills & Equipment
    surgery = Skill("Surgery")
    general = Skill("General Medicine")
    emergency = Skill("Emergency")
    
    xray = Equipment("X-Ray")
    mri = Equipment("MRI")

    # Doctors
    dr_smith = Doctor(id="smith", name="Dr. Smith", skills={surgery, general})
    dr_jones = Doctor(id="jones", name="Dr. Jones", skills={general, emergency})
    dr_williams = Doctor(id="williams", name="Dr. Williams", skills={surgery, emergency})
    
    dr_smith.unavailabilities = [(datetime(2024, 5, 1, 8, 0), datetime(2024, 5, 1, 12, 0))]
    doctors = [dr_smith, dr_jones, dr_williams]

    # Rooms
    room1 = Room(id="r1", name="Surgery Room A", equipment={mri})
    room2 = Room(id="r2", name="Consultation 1", equipment={xray})
    room3 = Room(id="r3", name="Emergency Bay", equipment={xray, mri})
    rooms = [room1, room2, room3]

    # Activity Types
    appendectomy = ActivityType(id="app", name="Appendectomy", required_skills={surgery}, required_equipment={mri}, burden_weight=10)
    checkup = ActivityType(id="chk", name="Regular Checkup", required_skills={general}, burden_weight=2)
    er_shift = ActivityType(id="er", name="ER Shift", required_skills={emergency}, required_equipment={xray}, burden_weight=15)

    # Activity Instances
    activities = [
        ActivityInstance(id="a1", activity_type=appendectomy, start_time=datetime(2024, 5, 1, 9, 0), end_time=datetime(2024, 5, 1, 11, 0)),
        ActivityInstance(id="a2", activity_type=checkup, start_time=datetime(2024, 5, 1, 9, 0), end_time=datetime(2024, 5, 1, 10, 0)),
        ActivityInstance(id="a3", activity_type=er_shift, start_time=datetime(2024, 5, 1, 13, 0), end_time=datetime(2024, 5, 1, 17, 0)),
        ActivityInstance(id="a4", activity_type=checkup, start_time=datetime(2024, 5, 1, 14, 0), end_time=datetime(2024, 5, 1, 15, 0)),
    ]

    return doctors, activities, rooms

def main():
    doctors, activities, rooms = create_sample_data()
    solver = ShiftSolver(doctors, activities, rooms)
    
    print("Starting solver...")
    result = solver.solve()

    if result:
        print(f"Solution found! Equity Score (spread): {result['equity_score']}")
        
        doc_assigns = result['doctor_assignments']
        room_assigns = {a_id: r_id for r_id, a_id in result['room_assignments']}
        
        act_map = {a.id: a for a in activities}
        doc_map = {d.id: d for d in doctors}
        room_map = {r.id: r for r in rooms}

        doc_assigns.sort(key=lambda x: act_map[x[1]].start_time)

        for doc_id, act_id in doc_assigns:
            doc = doc_map[doc_id]
            act = act_map[act_id]
            room = room_map[room_assigns[act_id]]
            print(f"  - {doc.name} assigned to {act.activity_type.name} "
                  f"in {room.name} ({act.start_time.strftime('%H:%M')} - {act.end_time.strftime('%H:%M')})")
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
