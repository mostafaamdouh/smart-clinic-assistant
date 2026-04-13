"""
Basic medical articles for the Smart Clinic knowledge base.
Simplified versions based on general medical knowledge.
"""

MEDICAL_ARTICLES = [
    {
        "id": "art_001",
        "title": "Acne Vulgaris: Overview and Treatment",
        "content": """Acne vulgaris is a chronic skin condition that occurs when hair follicles become plugged 
        with oil and dead skin cells. It causes whiteheads, blackheads, and pimples, and usually appears on 
        the face, forehead, chest, upper back, and shoulders. Acne is most common among teenagers, though 
        it affects people of all ages. Effective treatments include topical retinoids, benzoyl peroxide, 
        antibiotics like doxycycline, and in severe cases, isotretinoin. Patients should avoid picking or 
        squeezing pimples, use gentle cleansers, and apply non-comedogenic moisturizers. Diet low in 
        refined sugars may also help reduce breakouts.""",
        "specialization": "Dermatology",
        "keywords": ["acne", "pimples", "skin", "benzoyl peroxide", "doxycycline", "retinoids"],
    },
    {
        "id": "art_002",
        "title": "Eczema (Atopic Dermatitis): Causes and Management",
        "content": """Eczema, or atopic dermatitis, is a condition that makes skin red, inflamed, and itchy. 
        It is common in children but can occur at any age. Eczema is chronic and tends to flare periodically. 
        It may be accompanied by asthma or hay fever. There is no cure for eczema, but treatments and 
        self-care measures can relieve itching and prevent new outbreaks. Moisturizing regularly, avoiding 
        harsh soaps and detergents, and applying corticosteroid creams during flares are the main management 
        strategies. Antihistamines can help with itching. Identifying and avoiding triggers is essential.""",
        "specialization": "Dermatology",
        "keywords": ["eczema", "atopic dermatitis", "itchy skin", "rash", "corticosteroids", "moisturizer"],
    },
    {
        "id": "art_003",
        "title": "Psoriasis: Understanding the Chronic Skin Condition",
        "content": """Psoriasis is a chronic autoimmune skin condition that speeds up the life cycle of skin 
        cells. Cells build up rapidly on the skin surface, forming scales and red patches that can be itchy 
        and sometimes painful. Psoriasis tends to go through cycles, flaring for a few weeks or months, 
        then subsiding. Common triggers include stress, infections, and certain medications. Treatments 
        include topical therapies like corticosteroids and calcipotriol, phototherapy, and systemic 
        medications for severe cases. There is no cure, but proper management can significantly improve 
        quality of life.""",
        "specialization": "Dermatology",
        "keywords": ["psoriasis", "skin scales", "autoimmune", "betamethasone", "calcipotriol", "plaques"],
    },
    {
        "id": "art_004",
        "title": "Hypertension: High Blood Pressure Management",
        "content": """Hypertension, or high blood pressure, is a condition where the force of blood against 
        artery walls is consistently too high. Blood pressure is measured in millimeters of mercury (mmHg) 
        and recorded as systolic over diastolic. Normal blood pressure is below 120/80 mmHg. Hypertension 
        is defined as 130/80 mmHg or higher. It is a major risk factor for heart disease and stroke. 
        Lifestyle changes include reducing salt intake, regular exercise, maintaining healthy weight, and 
        limiting alcohol. Medications include ACE inhibitors, calcium channel blockers like amlodipine, 
        and ARBs like losartan. Regular monitoring is essential.""",
        "specialization": "Cardiology / General Practice",
        "keywords": ["hypertension", "high blood pressure", "amlodipine", "losartan", "heart", "stroke"],
    },
    {
        "id": "art_005",
        "title": "Iron Deficiency Anemia: Diagnosis and Treatment",
        "content": """Iron deficiency anemia occurs when the body lacks enough iron to produce hemoglobin, 
        the substance in red blood cells that enables them to carry oxygen. Symptoms include fatigue, 
        weakness, pale skin, shortness of breath, headache, and cold hands and feet. It is diagnosed 
        through blood tests including complete blood count and serum ferritin levels. Treatment involves 
        iron supplements, typically ferrous sulfate 325mg daily, and identifying the underlying cause. 
        Dietary sources of iron include red meat, leafy vegetables, and fortified cereals. Vitamin C 
        enhances iron absorption.""",
        "specialization": "General Practice",
        "keywords": ["anemia", "iron deficiency", "fatigue", "hemoglobin", "iron supplement", "ferritin"],
    },
    {
        "id": "art_006",
        "title": "Cardiac Hypertrophy: Causes and Clinical Significance",
        "content": """Left ventricular hypertrophy (LVH) is a thickening of the heart muscle in the left 
        ventricle. It is most commonly caused by chronic high blood pressure, which forces the heart to 
        work harder. Over time, this extra workload causes the heart muscle to thicken. LVH increases 
        the risk of heart attack, heart failure, and sudden cardiac death. Diagnosis is made through 
        ECG and echocardiogram. Treatment focuses on controlling the underlying cause, particularly 
        managing blood pressure with medications like ACE inhibitors, ARBs, and calcium channel blockers. 
        Regular cardiac follow-up is essential.""",
        "specialization": "Cardiology",
        "keywords": ["LVH", "left ventricular hypertrophy", "heart", "hypertension", "echocardiogram", "ECG"],
    },
]