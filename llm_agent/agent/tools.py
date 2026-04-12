import requests
from langchain.tools import tool

BACKEND_URL = "http://localhost:8000"

@tool
def check_available_slots(doctor_id: str, date: str) -> str:
    """Check available appointment slots for a doctor on a given date."""
    try:
        response = requests.get(f"{BACKEND_URL}/slots", params={"doctor_id": doctor_id, "date": date})
        return response.text
    except Exception as e:
        return f"Backend not available: {e}"

@tool
def reserve_slot(patient_id: str, slot_id: str) -> str:
    """Reserve an appointment slot for a patient."""
    try:
        response = requests.post(f"{BACKEND_URL}/reserve", json={"patient_id": patient_id, "slot_id": slot_id})
        return response.text
    except Exception as e:
        return f"Backend not available: {e}"

@tool
def release_slot(slot_id: str) -> str:
    """Release a previously reserved appointment slot."""
    try:
        response = requests.post(f"{BACKEND_URL}/release", json={"slot_id": slot_id})
        return response.text
    except Exception as e:
        return f"Backend not available: {e}"

@tool
def get_patient_history(patient_id: str) -> str:
    """Get the appointment and medical history for a patient."""
    try:
        response = requests.get(f"{BACKEND_URL}/patient/{patient_id}/history")
        return response.text
    except Exception as e:
        return f"Backend not available: {e}"