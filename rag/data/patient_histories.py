"""
Fake patient history records for the Smart Clinic knowledge base.
"""

PATIENT_HISTORIES = [
    {
        "patient_id": "pat_001",
        "name": "Mohamed Ali",
        "age": 34,
        "gender": "Male",
        "visits": [
            {
                "date": "2024-11-10",
                "doctor": "Dr. Ahmed Hassan",
                "specialization": "Dermatology",
                "complaint": "Persistent acne on face and back",
                "diagnosis": "Moderate acne vulgaris",
                "prescription": "Benzoyl peroxide 5% gel, Doxycycline 100mg daily for 3 months",
                "notes": "Patient advised to avoid oily foods and use non-comedogenic sunscreen.",
                "follow_up": "2024-12-10",
            },
            {
                "date": "2024-12-10",
                "doctor": "Dr. Ahmed Hassan",
                "specialization": "Dermatology",
                "complaint": "Follow-up for acne treatment",
                "diagnosis": "Improving acne vulgaris",
                "prescription": "Continue Benzoyl peroxide 5% gel, Doxycycline reduced to 50mg daily",
                "notes": "Significant improvement noted. Patient to continue current regimen.",
                "follow_up": "2025-02-10",
            },
        ],
    },
    {
        "patient_id": "pat_002",
        "name": "Fatma Ibrahim",
        "age": 52,
        "gender": "Female",
        "visits": [
            {
                "date": "2024-10-05",
                "doctor": "Dr. Sara Mahmoud",
                "specialization": "General Practice",
                "complaint": "Frequent headaches and fatigue",
                "diagnosis": "Mild hypertension and iron deficiency anemia",
                "prescription": "Amlodipine 5mg daily, Iron supplement 325mg daily",
                "notes": "Patient advised to reduce salt intake and follow up in 6 weeks.",
                "follow_up": "2024-11-16",
            },
            {
                "date": "2024-11-16",
                "doctor": "Dr. Sara Mahmoud",
                "specialization": "General Practice",
                "complaint": "Follow-up hypertension and anemia",
                "diagnosis": "Controlled hypertension, improving anemia",
                "prescription": "Continue Amlodipine 5mg, Continue Iron supplement",
                "notes": "Blood pressure now within normal range. Hemoglobin improving.",
                "follow_up": "2025-01-16",
            },
            {
                "date": "2025-01-16",
                "doctor": "Dr. Khaled Nour",
                "specialization": "Cardiology",
                "complaint": "Referred by Dr. Sara for occasional chest tightness",
                "diagnosis": "Mild left ventricular hypertrophy secondary to hypertension",
                "prescription": "Add Losartan 50mg daily, Continue Amlodipine 5mg",
                "notes": "ECG performed, no acute changes. Echocardiogram scheduled.",
                "follow_up": "2025-03-01",
            },
        ],
    },
    {
        "patient_id": "pat_003",
        "name": "Omar Saeed",
        "age": 28,
        "gender": "Male",
        "visits": [
            {
                "date": "2025-01-20",
                "doctor": "Dr. Ahmed Hassan",
                "specialization": "Dermatology",
                "complaint": "Red itchy patches on elbows and knees",
                "diagnosis": "Plaque psoriasis",
                "prescription": "Betamethasone cream 0.05% twice daily, Calcipotriol ointment",
                "notes": "Patient educated about chronic nature of psoriasis. Stress management advised.",
                "follow_up": "2025-03-01",
            },
        ],
    },
]