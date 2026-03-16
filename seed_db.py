import random
from datetime import datetime, timedelta
from sqlmodel import Session
from app.models.engine import engine
from app.models.database import Schedule

def generate_schedules():
    classes = ["Yoga", "Pilates", "HIIT", "Zumba", "Spinning", "CrossFit", "Boxing", "BodyPump"]
    instructors = ["Maya", "John", "Sarah", "Mike", "Emma", "David", "Lisa", "Tom"]
    
    with Session(engine) as session:
        # Check if we already have data
        existing = session.query(Schedule).first()
        if existing:
            print("Schedules already exist! Skipping generation.")
            return

        print("Generating 20 schedules...")
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        for i in range(20):
            # Randomize days ahead and time
            days_ahead = random.randint(0, 14)
            hour = random.randint(6, 20)  # Between 6 AM and 8 PM
            
            start_time = now + timedelta(days=days_ahead)
            start_time = start_time.replace(hour=hour)
            end_time = start_time + timedelta(hours=1)
            
            schedule = Schedule(
                class_name=random.choice(classes),
                instructor=random.choice(instructors),
                start_time=start_time,
                end_time=end_time
            )
            session.add(schedule)
            
        session.commit()
        print("Successfully added 20 schedules to the database!")

if __name__ == "__main__":
    generate_schedules()
