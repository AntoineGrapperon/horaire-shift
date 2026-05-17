from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from .models import ShiftTemplate, ShiftInstance, ShiftStatus

def expand_templates(db: Session, start_date: date, end_date: date):
    """
    Expands weekly templates into concrete shift instances for a date range.
    """
    templates = db.query(ShiftTemplate).all()
    
    current_date = start_date
    instances_created = 0
    
    while current_date <= end_date:
        # 0 is Monday in python's weekday(), but in our model 0 is Sunday
        # python: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
        # our model: Sun=0, Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6
        py_weekday = current_date.weekday()
        model_weekday = (py_weekday + 1) % 7
        
        day_templates = [t for t in templates if t.day_of_week == model_weekday]
        
        for t in day_templates:
            # Create 'quantity' instances for each template
            for _ in range(t.quantity):
                instance = ShiftInstance(
                    template_id=t.id,
                    date=current_date,
                    start_time=t.start_time,
                    end_time=t.end_time,
                    required_role=t.required_role,
                    status=ShiftStatus.UNASSIGNED
                )
                db.add(instance)
                instances_created += 1
        
        current_date += timedelta(days=1)
    
    db.commit()
    return instances_created
