from agent.tools import (
    check_available_slots,
    reserve_slot,
    release_slot,
    get_patient_history,
)

print("Checking slots...")
print(check_available_slots.invoke({"doctor_id": "ahmed", "date": "thursday"}))

print("\nGetting patient history...")
print(get_patient_history.invoke({"patient_id": "mahmoud"}))

print("\nReserving slot...")
print(
    reserve_slot.invoke(
        {
            "patient_id": "mahmoud",
            "slot_id": "ahmed_thursday_10:00 AM",
        }
    )
)

print("\nChecking slots again...")
print(check_available_slots.invoke({"doctor_id": "ahmed", "date": "thursday"}))

print("\nReleasing slot...")
print(release_slot.invoke({"slot_id": "ahmed_thursday_10:00 AM"}))

print("\nChecking slots after release...")
print(check_available_slots.invoke({"doctor_id": "ahmed", "date": "thursday"}))