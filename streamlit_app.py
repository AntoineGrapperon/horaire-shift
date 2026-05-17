import streamlit as st
from app.database import engine, Base, SessionLocal
from app.models import User, UserRole
from sqlalchemy.orm import Session
import bcrypt

# Page configuration
st.set_page_config(
    page_title="ShiftMed | Medical Shift Scheduler",
    page_icon="🏥",
    layout="wide"
)

# Initialize database
Base.metadata.create_all(bind=engine)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass # Streamlit handles session differently

def create_admin_if_not_exists():
    db = SessionLocal()
    admin = db.query(User).filter(User.email == "admin@shiftmed.com").first()
    if not admin:
        hashed_password = hash_password("admin123")
        admin = User(
            full_name="System Admin",
            email="admin@shiftmed.com",
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.commit()
    db.close()

create_admin_if_not_exists()

def login():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        db.close()
        if user and verify_password(password, user.hashed_password):
            st.session_state["authenticated"] = True
            st.session_state["user_email"] = user.email
            st.session_state["user_role"] = user.role
            st.success(f"Welcome {user.full_name}")
            st.rerun()
        else:
            st.error("Invalid email or password")

def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        login()
        return

    st.title("🏥 ShiftMed Scheduler")
    st.sidebar.title(f"Welcome, {st.session_state['user_email']}")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    menu = ["Dashboard", "Staff Management", "Shift Templates", "Roster Solver"]
    
    # Restrict menu based on role
    if st.session_state["user_role"] != UserRole.ADMIN:
        menu = ["Dashboard"]
        st.sidebar.warning("Restricted Access: Clinician View")

    choice = st.sidebar.selectbox("Go to", menu)

    if choice == "Dashboard":
        st.subheader("Overview")
        st.write("Welcome to ShiftMed. Use the sidebar to navigate.")
        
    elif choice == "Staff Management":
        st.subheader("User & Staff Management")
        
        db = SessionLocal()
        
        # Form to add new user
        with st.expander("Add New Staff Member"):
            with st.form("add_user_form"):
                full_name = st.text_input("Full Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                role = st.selectbox("Role", [r.value for r in UserRole])
                contract_hours = st.number_input("Contract Hours per Week", min_value=0.0, max_value=168.0, value=35.0)
                submit_button = st.form_submit_button("Add Staff")
                
                if submit_button:
                    if not full_name or not email or not password:
                        st.error("Please fill in all required fields.")
                    else:
                        existing_user = db.query(User).filter(User.email == email).first()
                        if existing_user:
                            st.error("User with this email already exists.")
                        else:
                            new_user = User(
                                full_name=full_name,
                                email=email,
                                hashed_password=pwd_context.hash(password),
                                role=role,
                                contract_hours_per_week=contract_hours
                            )
                            db.add(new_user)
                            db.commit()
                            st.success(f"Added {full_name} as {role}")
                            st.rerun()

        # List existing users
        users = db.query(User).all()
        if users:
            import pandas as pd
            user_data = []
            for u in users:
                user_data.append({
                    "Name": u.full_name,
                    "Email": u.email,
                    "Role": u.role,
                    "Hours": u.contract_hours_per_week,
                    "Active": u.is_active
                })
            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.write("No staff members found.")
            
        db.close()

    elif choice == "Shift Templates":
        st.subheader("Weekly Shift Templates")
        st.write("Define the recurring shifts that happen every week.")
        
        db = SessionLocal()
        from app.models import ShiftTemplate
        
        with st.expander("Add New Template"):
            with st.form("add_template_form"):
                day = st.selectbox("Day of Week", 
                                   options=range(7), 
                                   format_func=lambda x: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][x])
                start_time = st.time_input("Start Time")
                end_time = st.time_input("End Time")
                role_req = st.selectbox("Required Role", [r.value for r in UserRole])
                quantity = st.number_input("Quantity", min_value=1, value=1)
                
                submit_template = st.form_submit_button("Save Template")
                if submit_template:
                    new_template = ShiftTemplate(
                        day_of_week=day,
                        start_time=start_time.strftime("%H:%M"),
                        end_time=end_time.strftime("%H:%M"),
                        required_role=role_req,
                        quantity=quantity
                    )
                    db.add(new_template)
                    db.commit()
                    st.success("Template added!")
                    st.rerun()

        templates = db.query(ShiftTemplate).all()
        if templates:
            template_data = []
            for t in templates:
                template_data.append({
                    "Day": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][t.day_of_week],
                    "Start": t.start_time,
                    "End": t.end_time,
                    "Role": t.required_role,
                    "Qty": t.quantity
                })
            st.table(template_data)
        else:
            st.info("No templates defined yet.")
        db.close()

    elif choice == "Roster Solver":
        st.subheader("Roster Management & Intelligence")
        
        db = SessionLocal()
        from app.services import expand_templates
        from app.models import ShiftInstance
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### 1. Generate Empty Roster")
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            if st.button("Generate Shifts from Templates"):
                count = expand_templates(db, start_date, end_date)
                st.success(f"Generated {count} empty shift instances.")
                st.rerun()
            
            if st.button("🗑️ Clear All Shifts", type="secondary"):
                db.query(ShiftInstance).delete()
                db.commit()
                st.warning("All shifts cleared.")
                st.rerun()

        with col2:
            st.write("### 2. Run Auto-Assignment")
            from app.solver import run_solver
            if st.button("Run OR-Tools Solver"):
                with st.spinner("Optimizing schedule..."):
                    count, msg = run_solver(db)
                    if count > 0:
                        st.success(f"Success! {count} shifts assigned.")
                    else:
                        st.warning(f"Solver result: {msg}")
                st.rerun()

        st.divider()
        st.write("### Current Roster View")
        shifts = db.query(ShiftInstance).order_by(ShiftInstance.date).all()
        if shifts:
            shift_data = []
            for s in shifts:
                shift_data.append({
                    "Date": s.date,
                    "Start": s.start_time,
                    "End": s.end_time,
                    "Role": s.required_role,
                    "Assigned": s.assigned_user.full_name if s.assigned_user else "UNASSIGNED",
                    "Status": s.status
                })
            st.dataframe(pd.DataFrame(shift_data), use_container_width=True)
        else:
            st.info("No shifts generated for this period.")
        db.close()

if __name__ == "__main__":
    main()
