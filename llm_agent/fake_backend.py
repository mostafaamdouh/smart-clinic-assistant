from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI()

# Data structures exactly as requested by user
DOCTORS = {
    "ahmed": "Dr. Ahmed Hassan - Cardiologist",
    "sara": "Dr. Sara Khaled - Dermatologist",
    "omar": "Dr. Omar Fathy - General Practitioner"
}

SLOTS = {
    "ahmed": {
        "thursday": ["10:00 AM", "2:00 PM", "4:00 PM"],
        "friday": ["11:00 AM", "3:00 PM"]
    },
    "sara": {
        "thursday": ["9:00 AM", "1:00 PM"],
        "friday": ["10:00 AM", "2:00 PM", "5:00 PM"]
    },
    "omar": {
        "thursday": ["8:00 AM", "12:00 PM", "3:00 PM"],
        "friday": ["9:00 AM", "11:00 AM"]
    }
}

RESERVATIONS = {}

PATIENTS = {
    "mahmoud": {
        "name": "Mahmoud Ahmed",
        "history": [
            {"date": "2025-12-01", "doctor": "Dr. Ahmed Hassan", "diagnosis": "High blood pressure", "prescription": "Amlodipine 5mg"},
            {"date": "2026-01-15", "doctor": "Dr. Sara Khaled", "diagnosis": "Skin rash", "prescription": "Hydrocortisone cream"}
        ]
    }
}

# Request body models
class ReserveRequest(BaseModel):
    patient_id: str
    slot_id: str

class ReleaseRequest(BaseModel):
    slot_id: str

@app.get("/slots")
def get_slots(doctor_id: str, date: str):
    """Check available appointment slots for a doctor on a given date."""
    if doctor_id not in SLOTS:
        return {"error": f"Doctor '{doctor_id}' not found."}
    if date not in SLOTS[doctor_id]:
        return {"error": f"No available slots for date '{date}'."}
    return {"doctor_id": doctor_id, "date": date, "available_slots": SLOTS[doctor_id][date]}

@app.post("/reserve")
def reserve(req: ReserveRequest):
    """Reserve an appointment slot for a patient."""
    # slot_id expected format: "doctor_id_date_time"
    # e.g. "ahmed_thursday_10:00 AM"
    parts = req.slot_id.split("_")
    if len(parts) < 3:
        return {"error": "Invalid slot_id format. Use 'doctor_id_date_time'."}
    
    doc_id = parts[0]
    date = parts[1]
    time = "_".join(parts[2:]) # handles any underscores in time
    
    if doc_id not in SLOTS or date not in SLOTS[doc_id] or time not in SLOTS[doc_id][date]:
        return {"error": "Slot is not available or already reserved."}
    
    # Process reservation
    SLOTS[doc_id][date].remove(time)
    RESERVATIONS[req.slot_id] = req.patient_id
    return {"message": f"Success: Slot '{req.slot_id}' reserved for patient '{req.patient_id}'."}

@app.post("/release")
def release(req: ReleaseRequest):
    """Release a previously reserved appointment slot."""
    if req.slot_id not in RESERVATIONS:
        return {"error": "Slot not found in current reservations."}
    
    # Restore slot to available list
    parts = req.slot_id.split("_")
    doc_id = parts[0]
    date = parts[1]
    time = "_".join(parts[2:])
    
    if doc_id in SLOTS and date in SLOTS[doc_id]:
        SLOTS[doc_id][date].append(time)
        SLOTS[doc_id][date].sort()
    
    del RESERVATIONS[req.slot_id]
    return {"message": f"Success: Slot '{req.slot_id}' has been released."}

@app.get("/patient/{patient_id}/history")
def get_history(patient_id: str):
    """Get the appointment and medical history for a patient."""
    if patient_id not in PATIENTS:
        return {"error": f"Patient '{patient_id}' not found."}
    return PATIENTS[patient_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)