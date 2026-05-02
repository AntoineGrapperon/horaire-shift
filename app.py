import streamlit as st
import pandas as pd
from datetime import datetime, time
from models import Skill, Doctor, ActivityType, ActivityInstance, Room, Equipment
from solver import ShiftSolver

st.set_page_config(page_title="Doctor Shift Scheduler", layout="wide")

st.title("🏥 Doctor Shift Scheduler")

# Helper to parse comma separated strings
def parse_tags(text):
    if not text: return set()
    return {s.strip() for s in text.split(",") if s.strip()}

# Initialize Session State
if 'doctors' not in st.session_state:
    st.session_state.doctors = pd.DataFrame([
        {"id": "smith", "name": "Dr. Smith", "skills": "Surgery, General Medicine", "hist_burden": 20},
        {"id": "jones", "name": "Dr. Jones", "skills": "General Medicine, Emergency", "hist_burden": 5},
        {"id": "williams", "name": "Dr. Williams", "skills": "Surgery, Emergency", "hist_burden": 0}
    ])

if 'rooms' not in st.session_state:
    st.session_state.rooms = pd.DataFrame([
        {"id": "r1", "name": "Surgery Room A", "equipment": "MRI"},
        {"id": "r2", "name": "Consultation 1", "equipment": "X-Ray"},
        {"id": "r3", "name": "Emergency Bay", "equipment": "X-Ray, MRI"}
    ])

if 'activity_types' not in st.session_state:
    st.session_state.activity_types = pd.DataFrame([
        {"id": "app", "name": "Appendectomy", "skills": "Surgery", "equipment": "MRI", "burden": 10},
        {"id": "chk", "name": "Regular Checkup", "skills": "General Medicine", "equipment": "", "burden": 2},
        {"id": "er", "name": "ER Shift", "skills": "Emergency", "equipment": "X-Ray", "burden": 15}
    ])

if 'activities' not in st.session_state:
    st.session_state.activities = pd.DataFrame([
        {"id": "a1", "type_id": "app", "date": datetime(2024, 5, 1), "start": time(9, 0), "end": time(11, 0), "group": ""},
        {"id": "a2", "type_id": "chk", "date": datetime(2024, 5, 1), "start": time(9, 0), "end": time(10, 0), "group": ""},
        {"id": "a3", "type_id": "er", "date": datetime(2024, 5, 1), "start": time(13, 0), "end": time(17, 0), "group": ""},
    ])

# UI Tabs
tab1, tab2, tab3, tab4 = st.tabs(["👨‍⚕️ Doctors", "🏥 Rooms", "📋 Activity Types", "📅 Schedule"])

with tab1:
    st.header("Manage Doctors")
    st.session_state.doctors = st.data_editor(st.session_state.doctors, num_rows="dynamic", key="edit_docs")

with tab2:
    st.header("Manage Rooms")
    st.session_state.rooms = st.data_editor(st.session_state.rooms, num_rows="dynamic", key="edit_rooms")

with tab3:
    st.header("Activity Definitions")
    st.session_state.activity_types = st.data_editor(st.session_state.activity_types, num_rows="dynamic", key="edit_types")

with tab4:
    st.header("Shift Instances")
    view_mode = st.radio("View Mode", ["Table", "Calendar"], horizontal=True)

    if view_mode == "Table":
        st.session_state.activities = st.data_editor(st.session_state.activities, num_rows="dynamic", key="edit_acts")
    else:
        # Calendar View Logic
        # 1. Add Event Form
        with st.expander("➕ Add New Shift", expanded=False):
            with st.form("add_shift_form"):
                f_id = st.text_input("Shift ID", value=f"a{len(st.session_state.activities)+1}")
                f_type = st.selectbox("Type", options=st.session_state.activity_types['id'].tolist())
                f_date = st.date_input("Date", value=datetime.today())
                c1, c2 = st.columns(2)
                f_start = c1.time_input("Start Time", value=time(9, 0))
                f_end = c2.time_input("End Time", value=time(17, 0))
                f_group = st.text_input("Group ID (optional)")
                
                if st.form_submit_button("Add Shift"):
                    # Ensure date is a datetime object to match existing data if needed, 
                    # but actually keeping it as date is fine if we are consistent.
                    # We'll use datetime for consistency.
                    new_date = datetime.combine(f_date, time.min)
                    new_row = pd.DataFrame([{"id": f_id, "type_id": f_type, "date": new_date, "start": f_start, "end": f_end, "group": f_group}])
                    st.session_state.activities = pd.concat([st.session_state.activities, new_row], ignore_index=True)
                    st.rerun()

        # 2. Visual Calendar (Simple Grid)
        df = st.session_state.activities.copy()
        if not df.empty:
            # Ensure date is date type for grouping
            df['date_only'] = pd.to_datetime(df['date']).dt.date
            unique_dates = sorted(df['date_only'].unique())
            
            # Display in columns (max 5 per row for readability)
            for i in range(0, len(unique_dates), 5):
                batch = unique_dates[i:i+5]
                cols = st.columns(5)
                for j, d in enumerate(batch):
                    with cols[j]:
                        st.markdown(f"📅 **{d.strftime('%a, %b %d')}**")
                        day_shifts = df[df['date_only'] == d].sort_values("start")
                        for _, s in day_shifts.iterrows():
                            with st.container(border=True):
                                st.markdown(f"**{s['type_id']}**")
                                st.caption(f"🕒 {s['start'].strftime('%H:%M')} - {s['end'].strftime('%H:%M')}")
                                if s['group']:
                                    st.caption(f"🔗 {s['group']}")
                st.divider()
        else:
            st.info("No shifts defined yet.")

# Solver Logic
if st.sidebar.button("🚀 Run Solver", use_container_width=True):
    try:
        # Convert DataFrames to Objects
        skills_cache = {}
        def get_skill(name):
            if name not in skills_cache: skills_cache[name] = Skill(name)
            return skills_cache[name]
        
        equip_cache = {}
        def get_equip(name):
            if name not in equip_cache: equip_cache[name] = Equipment(name)
            return equip_cache[name]

        doctors = []
        for _, r in st.session_state.doctors.iterrows():
            doctors.append(Doctor(
                id=r['id'], name=r['name'],
                skills={get_skill(s) for s in parse_tags(r['skills'])},
                historical_burden=int(r['hist_burden'])
            ))
        
        rooms = []
        for _, r in st.session_state.rooms.iterrows():
            rooms.append(Room(
                id=r['id'], name=r['name'],
                equipment={get_equip(e) for e in parse_tags(r['equipment'])}
            ))
            
        types = {}
        for _, r in st.session_state.activity_types.iterrows():
            types[r['id']] = ActivityType(
                id=r['id'], name=r['name'],
                required_skills={get_skill(s) for s in parse_tags(r['skills'])},
                required_equipment={get_equip(e) for e in parse_tags(r['equipment'])},
                burden_weight=int(r['burden'])
            )
            
        activities = []
        for _, r in st.session_state.activities.iterrows():
            dt = r['date']
            start_dt = datetime.combine(dt, r['start'])
            end_dt = datetime.combine(dt, r['end'])
            activities.append(ActivityInstance(
                id=r['id'],
                activity_type=types[r['type_id']],
                start_time=start_dt,
                end_time=end_dt,
                group_id=r['group'] if r['group'] else None
            ))

        # Solve
        solver = ShiftSolver(doctors, activities, rooms)
        with st.spinner("Calculating optimal schedule..."):
            result = solver.solve()

        if result:
            st.success(f"Solution Found! (Objective Score: {result['equity_score']})")
            
            # Prepare Results Table
            doc_map = {d.id: d.name for d in doctors}
            act_map = {a.id: a for a in activities}
            room_map = {r.id: r.name for r in rooms}
            room_assigns = {a_id: r_id for r_id, a_id in result['room_assignments']}
            
            schedule_data = []
            assigned_burdens = {d.id: 0 for d in doctors}
            
            for d_id, a_id in result['doctor_assignments']:
                act = act_map[a_id]
                assigned_burdens[d_id] += act.activity_type.burden_weight
                schedule_data.append({
                    "Doctor": doc_map[d_id],
                    "Activity": act.activity_type.name,
                    "Room": room_map[room_assigns[a_id]],
                    "Start": act.start_time.strftime("%Y-%m-%d %H:%M"),
                    "End": act.end_time.strftime("%Y-%m-%d %H:%M")
                })
            
            st.subheader("📅 Final Schedule")
            st.dataframe(pd.DataFrame(schedule_data), use_container_width=True)
            
            st.subheader("📊 Equity Report")
            equity_data = []
            for d in doctors:
                curr = assigned_burdens[d.id]
                equity_data.append({
                    "Doctor": d.name,
                    "Historical": d.historical_burden,
                    "Current": curr,
                    "Total": d.historical_burden + curr
                })
            st.table(pd.DataFrame(equity_data))
            
        else:
            st.error("No feasible solution found with current constraints.")
            
    except Exception as e:
        st.error(f"Error during solving: {e}")

st.sidebar.info("Fill in the data in the tabs and click 'Run Solver' to generate the schedule.")
