"""
Skin Disease Classifier — FastAPI Endpoint
Accepts: image file (multipart/form-data)
Returns: predicted class, confidence scores, disease info
"""

import io
import json
from pathlib import Path
from typing import Optional

import torch
import numpy as np
from PIL import Image
from torchvision import transforms

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


# ─── Config ─────────────────────────────────────────────────────────────────

MODEL_PATH = Path("model_output/skin_classifier.pt")
META_PATH  = Path("model_output/model_meta.json")

DISEASE_INFO = {
    "nv":    {"name": "Melanocytic Nevi",                     "risk": "Low",    "color": "#22c55e"},
    "mel":   {"name": "Melanoma",                             "risk": "High",   "color": "#ef4444"},
    "bkl":   {"name": "Benign Keratosis-like Lesion",         "risk": "Low",    "color": "#22c55e"},
    "bcc":   {"name": "Basal Cell Carcinoma",                 "risk": "Medium", "color": "#f59e0b"},
    "akiec": {"name": "Actinic Keratosis / Intraepithelial",  "risk": "Medium", "color": "#f59e0b"},
    "vasc":  {"name": "Vascular Lesion",                      "risk": "Low",    "color": "#22c55e"},
    "df":    {"name": "Dermatofibroma",                       "risk": "Low",    "color": "#22c55e"},
}


# ─── Load model ─────────────────────────────────────────────────────────────

def load_model():
    if not META_PATH.exists():
        raise RuntimeError(f"Model metadata not found at {META_PATH}. Run train.py first.")

    with open(META_PATH) as f:
        meta = json.load(f)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Try to load TorchScript model first, fall back to standard checkpoint
    model = None
    if MODEL_PATH.exists():
        try:
            model = torch.jit.load(str(MODEL_PATH), map_location=device)
            print(f"✓ Loaded TorchScript model from {MODEL_PATH}")
        except Exception as e:
            print(f"⚠ TorchScript load failed: {e}. Trying .pth format...")
    
    # If TorchScript failed or doesn't exist, try .pth format
    if model is None:
        pth_path = MODEL_PATH.parent / "skin_classifier.pth"
        if pth_path.exists():
            # Load as standard checkpoint and rebuild model
            from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
            import torch.nn as nn
            
            model = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
            in_features = model.classifier[1].in_features
            model.classifier = nn.Sequential(
                nn.Dropout(p=0.4, inplace=True),
                nn.Linear(in_features, 512),
                nn.ReLU(inplace=True),
                nn.Dropout(p=0.3),
                nn.Linear(512, meta["num_classes"]),
            )
            
            checkpoint = torch.load(str(pth_path), map_location=device)
            model.load_state_dict(checkpoint["model_state_dict"])
            print(f"✓ Loaded standard checkpoint from {pth_path}")
        else:
            raise RuntimeError(
                f"Model not found. Expected either:\n"
                f"  - {MODEL_PATH}\n"
                f"  - {pth_path}\n"
                f"Run train.py first."
            )
    
    model.eval()

    transform = transforms.Compose([
        transforms.Resize((meta["img_size"], meta["img_size"])),
        transforms.ToTensor(),
        transforms.Normalize(mean=meta["mean"], std=meta["std"]),
    ])

    return model, transform, meta, device


# ─── App setup ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Skin Disease Classifier",
    description="EfficientNetB0-based classifier for HAM10000 skin lesion categories.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model at startup
model, transform, meta, device = None, None, None, None

@app.on_event("startup")
async def startup_event():
    global model, transform, meta, device
    try:
        model, transform, meta, device = load_model()
        print(f"✓ Model loaded on {device}")
        print(f"  Best validation accuracy: {meta.get('best_val_accuracy', 'N/A'):.4f}")
    except RuntimeError as e:
        print(f"⚠ Model not loaded: {e}")


# ─── Response schema ─────────────────────────────────────────────────────────

class PredictionResult(BaseModel):
    predicted_class: str
    predicted_label: str
    confidence: float
    risk_level: str
    all_scores: dict[str, float]
    disclaimer: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str
    model: Optional[str]
    num_classes: Optional[int]
    best_val_accuracy: Optional[float]


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok",
        model_loaded=model is not None,
        device=str(device) if device else "N/A",
        model=meta.get("model") if meta else None,
        num_classes=meta.get("num_classes") if meta else None,
        best_val_accuracy=meta.get("best_val_accuracy") if meta else None,
    )


@app.post("/predict", response_model=PredictionResult)
async def predict(file: UploadFile = File(...)):
    """
    Classify a skin lesion image.

    - **file**: JPG/PNG image of the skin lesion

    Returns the predicted disease class with confidence scores.
    """
    if model is None:
        raise HTTPException(503, detail="Model not loaded. Run train.py first.")

    # Validate file type
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(400, detail="Only JPEG/PNG images are accepted.")

    # Read and preprocess image
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(400, detail="Could not read image file.")

    try:
        tensor = transform(image).unsqueeze(0).to(device)   # (1, 3, H, W)
    except Exception as e:
        raise HTTPException(500, detail=f"Preprocessing error: {e}")

    # Inference
    with torch.no_grad():
        logits = model(tensor)                              # (1, num_classes)
        probs  = torch.softmax(logits, dim=1)[0]            # (num_classes,)

    probs_np = probs.cpu().numpy()
    pred_idx = int(np.argmax(probs_np))

    label_names: list[str] = meta["label_names"]
    pred_label = label_names[pred_idx]
    confidence = float(probs_np[pred_idx])

    # Build score dict
    all_scores = {
        label: round(float(probs_np[i]), 4)
        for i, label in enumerate(label_names)
    }

    disease = DISEASE_INFO.get(pred_label, {})

    return PredictionResult(
        predicted_class=pred_label,
        predicted_label=disease.get("name", pred_label),
        confidence=round(confidence, 4),
        risk_level=disease.get("risk", "Unknown"),
        all_scores=all_scores,
        disclaimer=(
            "This result is for research/educational purposes only. "
            "Consult a dermatologist for clinical diagnosis."
        ),
    )


@app.get("/classes")
async def list_classes():
    """Return all supported disease classes with descriptions."""
    return {
        "classes": [
            {
                "code": code,
                "name": info["name"],
                "risk": info["risk"],
            }
            for code, info in DISEASE_INFO.items()
        ]
    }


# ─── Dev server ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
