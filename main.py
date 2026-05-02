from datetime import datetime, timedelta
from models import Skill, Doctor, ActivityType, ActivityInstance, Room, Equipment, Preference, PreferenceType
from solver import ShiftSolver

def create_sample_data():
    # Skills & Equipment
    surgery = Skill("Surgery")
    general = Skill("General Medicine")
    emergency = Skill("Emergency")
    
    xray = Equipment("X-Ray")
    mri = Equipment("MRI")

    # Doctors
    dr_smith = Doctor(id="smith", name="Dr. Smith", skills={surgery, general}, historical_burden=20)
    dr_jones = Doctor(id="jones", name="Dr. Jones", skills={general, emergency}, historical_burden=5)
    dr_williams = Doctor(id="williams", name="Dr. Williams", skills={surgery, emergency}, historical_burden=0)
    
    # Preference: Dr. Jones wants to avoid working on Wednesday (2)
    # 2024-05-01 is a Wednesday
    dr_jones.preferences = [
        Preference(type=PreferenceType.AVOID_DAY, weight=100, day_of_week=2)
    ]
    
    # Preference: Dr. Williams wants to avoid morning shifts (8:00 - 12:00)
    morning_start = datetime(2024, 1, 1, 8, 0)
    morning_end = datetime(2024, 1, 1, 12, 0)
    dr_williams.preferences = [
        Preference(type=PreferenceType.AVOID_TIME_RANGE, weight=50, start_time=morning_start, end_time=morning_end)
    ]

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
    on_call = ActivityType(id="on_call", name="On-Call", required_skills={general}, burden_weight=5)

    # Activity Instances (2024-05-01 is a Wednesday)
    activities = [
        ActivityInstance(id="a1", activity_type=appendectomy, start_time=datetime(2024, 5, 1, 9, 0), end_time=datetime(2024, 5, 1, 11, 0)),
        ActivityInstance(id="a2", activity_type=checkup, start_time=datetime(2024, 5, 1, 9, 0), end_time=datetime(2024, 5, 1, 10, 0)),
        ActivityInstance(id="a3", activity_type=er_shift, start_time=datetime(2024, 5, 1, 13, 0), end_time=datetime(2024, 5, 1, 17, 0)),
        ActivityInstance(id="a4", activity_type=checkup, start_time=datetime(2024, 5, 1, 14, 0), end_time=datetime(2024, 5, 1, 15, 0)),
        
        # Multi-day activity (On-Call grouped)
        ActivityInstance(id="call_night1", activity_type=on_call, 
                         start_time=datetime(2024, 5, 1, 20, 0), end_time=datetime(2024, 5, 2, 8, 0), 
                         group_id="weekend_call_1"),
        ActivityInstance(id="call_night2", activity_type=on_call, 
                         start_time=datetime(2024, 5, 2, 20, 0), end_time=datetime(2024, 5, 3, 8, 0), 
                         group_id="weekend_call_1"),
    ]

    return doctors, activities, rooms

def main():
    doctors, activities, rooms = create_sample_data()
    solver = ShiftSolver(doctors, activities, rooms)
    
    print("Starting solver...")
    result = solver.solve()

    if result:
        print(f"Solution found! Objective Score: {result['equity_score']}")
        
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
        
        print("\n--- Equity Report ---")
        assigned_burdens = {d.id: 0 for d in doctors}
        for d_id, a_id in doc_assigns:
            assigned_burdens[d_id] += act_map[a_id].activity_type.burden_weight
        
        totals = []
        for d in doctors:
            curr = assigned_burdens[d.id]
            total = d.historical_burden + curr
            totals.append(total)
            print(f"  {d.name:<12}: Hist={d.historical_burden:>3}, Curr={curr:>3}, Total={total:>3}")
        
        print(f"  Overall Spread (Max-Min Total): {max(totals) - min(totals)}")
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
