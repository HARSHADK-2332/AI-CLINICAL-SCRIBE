"""
Seed script for ScribeCare database.
Populates 3 demo patients for clinical consultations.
"""
from backend.database import SessionLocal, init_db
from backend.models import Patient


DEMO_PATIENTS = [
    {
        "name": "Sarah Jenkins",
        "age": 42,
        "gender": "Female",
        "medical_record_number": "MRN-10492"
    },
    {
        "name": "David Miller",
        "age": 58,
        "gender": "Male",
        "medical_record_number": "MRN-20984"
    },
    {
        "name": "Priya Sharma",
        "age": 29,
        "gender": "Female",
        "medical_record_number": "MRN-39481"
    }
]


def seed_database():
    init_db()
    db = SessionLocal()
    try:
        count = db.query(Patient).count()
        if count == 0:
            for p_data in DEMO_PATIENTS:
                patient = Patient(**p_data)
                db.add(patient)
            db.commit()
            print(f"Successfully seeded {len(DEMO_PATIENTS)} demo patients.")
        else:
            print(f"Database already contains {count} patients. Skipping seed.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
