from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

DOCTORS = {
    "ahmed": "Dr. Ahmed Hassan - Cardiologist",
    "sara": "Dr. Sara Khaled - Dermatologist",
    "omar": "Dr. Omar Fathy - General Practitioner",
}

SLOTS = {
    "ahmed": {
        "thursday": ["10:00 AM", "2:00 PM", "4:00 PM"],
        "friday": ["11:00 AM", "3:00 PM"],
    },
    "sara": {
        "thursday": ["9:00 AM", "1:00 PM"],
        "friday": ["10:00 AM", "2:00 PM", "5:00 PM"],
    },
    "omar": {
        "thursday": ["8:00 AM", "12:00 PM", "3:00 PM"],
        "friday": ["9:00 AM", "11:00 AM"],
    },
}

# شكل الحجز بعد التعديل:
# {
#   "ahmed_thursday_10:00 AM": {
#       "patient_id": "mahmoud",
#       "doctor_id": "ahmed",
#       "date": "thursday",
#       "time": "10:00 AM",
#       "status": "locked"
#   }
# }
RESERVATIONS = {}

PATIENTS = {
    "mahmoud": {
        "name": "Mahmoud Ahmed",
        "history": [
            {
                "date": "2025-12-01",
                "doctor": "Dr. Ahmed Hassan",
                "diagnosis": "High blood pressure",
                "prescription": "Amlodipine 5mg",
            },
            {
                "date": "2026-01-15",
                "doctor": "Dr. Sara Khaled",
                "diagnosis": "Skin rash",
                "prescription": "Hydrocortisone cream",
            },
        ],
    }
}


class ReserveRequest(BaseModel):
    patient_id: str
    slot_id: str


class ReleaseRequest(BaseModel):
    slot_id: str


class CompleteRequest(BaseModel):
    slot_id: str


def parse_slot_id(slot_id: str):
    parts = slot_id.split("_")
    if len(parts) < 3:
        return None, None, None
    doctor_id = parts[0]
    date = parts[1]
    time = "_".join(parts[2:])
    return doctor_id, date, time


@app.get("/")
def root():
    return {"message": "Fake backend is running"}


@app.get("/slots")
def get_slots(doctor_id: str, date: str):
    """Check available appointment slots for a doctor on a given date."""
    if doctor_id not in SLOTS:
        return {"error": f"Doctor '{doctor_id}' not found."}

    if date not in SLOTS[doctor_id]:
        return {"error": f"No available slots for date '{date}'."}

    return {
        "doctor_id": doctor_id,
        "date": date,
        "available_slots": SLOTS[doctor_id][date],
    }


@app.post("/reserve")
def reserve(req: ReserveRequest):
    """Reserve an appointment slot for a patient."""
    doctor_id, date, time = parse_slot_id(req.slot_id)

    if not doctor_id or not date or not time:
        return {"error": "Invalid slot_id format. Use 'doctor_id_date_time'."}

    if (
        doctor_id not in SLOTS
        or date not in SLOTS[doctor_id]
        or time not in SLOTS[doctor_id][date]
    ):
        return {"error": "Slot is not available or already reserved."}

    # شيل الموعد من المتاح
    SLOTS[doctor_id][date].remove(time)

    # خزّن الحجز
    RESERVATIONS[req.slot_id] = {
        "patient_id": req.patient_id,
        "doctor_id": doctor_id,
        "date": date,
        "time": time,
        "status": "locked",
    }

    return {
        "success": True,
        "message": f"Success: Slot '{req.slot_id}' reserved for patient '{req.patient_id}'.",
        "appointment": {
            "id": req.slot_id,
            "patient_id": req.patient_id,
            "doctor_id": doctor_id,
            "date": date,
            "time": time,
            "status": "locked",
        },
    }


@app.post("/release")
def release(req: ReleaseRequest):
    """Release a previously reserved appointment slot."""
    if req.slot_id not in RESERVATIONS:
        return {"error": "Slot not found in current reservations."}

    reservation = RESERVATIONS[req.slot_id]
    doctor_id = reservation["doctor_id"]
    date = reservation["date"]
    time = reservation["time"]

    if doctor_id in SLOTS and date in SLOTS[doctor_id]:
        if time not in SLOTS[doctor_id][date]:
            SLOTS[doctor_id][date].append(time)
            SLOTS[doctor_id][date].sort()

    del RESERVATIONS[req.slot_id]

    return {
        "success": True,
        "message": f"Success: Slot '{req.slot_id}' has been released."
    }


@app.post("/complete")
def complete(req: CompleteRequest):
    """Mark a reserved appointment as completed."""
    if req.slot_id not in RESERVATIONS:
        return {"error": "Slot not found in current reservations."}

    RESERVATIONS[req.slot_id]["status"] = "completed"

    return {
        "success": True,
        "message": f"Appointment '{req.slot_id}' marked as completed."
    }


@app.get("/appointments/{patient_id}")
def get_patient_appointments(patient_id: str):
    """Get all appointments for a patient."""
    patient_appointments = []

    for slot_id, reservation in RESERVATIONS.items():
        if reservation["patient_id"] == patient_id:
            patient_appointments.append({
                "id": slot_id,
                "doctor_id": reservation["doctor_id"],
                "patient_id": reservation["patient_id"],
                "date": reservation["date"],
                "time": reservation["time"],
                "status": reservation["status"],
            })

    return {
        "patient_id": patient_id,
        "appointments": patient_appointments
    }


@app.get("/doctor/{doctor_id}/appointments")
def get_doctor_appointments(doctor_id: str):
    """Get all appointments for a doctor."""
    doctor_appointments = []

    for slot_id, reservation in RESERVATIONS.items():
        if reservation["doctor_id"] == doctor_id:
            doctor_appointments.append({
                "id": slot_id,
                "doctor_id": reservation["doctor_id"],
                "patient_id": reservation["patient_id"],
                "date": reservation["date"],
                "time": reservation["time"],
                "status": reservation["status"],
            })

    return {
        "doctor_id": doctor_id,
        "appointments": doctor_appointments
    }


@app.get("/patient/{patient_id}/history")
def get_history(patient_id: str):
    """Get the appointment and medical history for a patient."""
    if patient_id not in PATIENTS:
        return {"error": f"Patient '{patient_id}' not found."}
    return PATIENTS[patient_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)