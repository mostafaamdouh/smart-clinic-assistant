"""
Test and Validation Script
Verifies that the model, dataset, and API are working correctly
"""

import json
import sys
from pathlib import Path
from typing import Tuple

import torch
import numpy as np
from PIL import Image
from torchvision import transforms

# ─── Config ─────────────────────────────────────────────────────────────────

MODEL_PATH = Path("model_output/skin_classifier.pt")
PTH_PATH = Path("model_output/skin_classifier.pth")
META_PATH = Path("model_output/model_meta.json")
DATA_DIR = Path("data/ham10000")
IMAGES_DIR = DATA_DIR / "images"


def check_dataset():
    """Verify dataset is present and has expected structure."""
    print("\n" + "="*60)
    print("🔍 CHECKING DATASET")
    print("="*60)
    
    if not DATA_DIR.exists():
        print("✗ Dataset directory not found at:", DATA_DIR)
        return False
    
    metadata_csv = DATA_DIR / "HAM10000_metadata.csv"
    if not metadata_csv.exists():
        print("✗ Metadata CSV not found at:", metadata_csv)
        return False
    
    import pandas as pd
    df = pd.read_csv(metadata_csv)
    images = list(IMAGES_DIR.glob("*.jpg"))
    
    print(f"✓ Dataset directory found: {DATA_DIR}")
    print(f"✓ Metadata CSV found: {len(df)} records")
    print(f"✓ Images found: {len(images)}")
    print(f"\n  Class distribution:")
    for cls, count in df["dx"].value_counts().items():
        print(f"    {cls}: {count}")
    
    return True


def check_model():
    """Verify model files and metadata."""
    print("\n" + "="*60)
    print("🔍 CHECKING MODEL FILES")
    print("="*60)
    
    if not META_PATH.exists():
        print("✗ Model metadata not found at:", META_PATH)
        return False
    
    with open(META_PATH) as f:
        meta = json.load(f)
    
    print(f"✓ Model metadata found: {META_PATH}")
    print(f"  Model type: {meta.get('model')}")
    print(f"  Image size: {meta.get('img_size')}")
    print(f"  Classes: {meta.get('num_classes')}")
    print(f"  Best val accuracy: {meta.get('best_val_accuracy', 'N/A')}")
    
    # Check model file
    has_torchscript = MODEL_PATH.exists()
    has_checkpoint = PTH_PATH.exists()
    
    if has_torchscript:
        print(f"✓ TorchScript model found: {MODEL_PATH}")
    elif has_checkpoint:
        print(f"✓ Standard checkpoint found: {PTH_PATH}")
    else:
        print(f"✗ No model found. Expected either:")
        print(f"    - {MODEL_PATH}")
        print(f"    - {PTH_PATH}")
        return False
    
    return True


def test_model_inference():
    """Test model inference with a sample image."""
    print("\n" + "="*60)
    print("🔍 TESTING MODEL INFERENCE")
    print("="*60)
    
    if not META_PATH.exists():
        print("✗ Model metadata not found, skipping inference test")
        return False
    
    # Load metadata
    with open(META_PATH) as f:
        meta = json.load(f)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"✓ Using device: {device}")
    
    # Try to load model
    model = None
    if MODEL_PATH.exists():
        try:
            model = torch.jit.load(str(MODEL_PATH), map_location=device)
            print(f"✓ Loaded TorchScript model")
            is_torchscript = True
        except Exception as e:
            print(f"⚠ TorchScript load failed: {e}")
            is_torchscript = False
    
    if model is None and PTH_PATH.exists():
        try:
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
            
            checkpoint = torch.load(str(PTH_PATH), map_location=device)
            model.load_state_dict(checkpoint["model_state_dict"])
            print(f"✓ Loaded standard checkpoint model")
            is_torchscript = False
        except Exception as e:
            print(f"✗ Failed to load checkpoint: {e}")
            return False
    
    if model is None:
        print("✗ Could not load any model format")
        return False
    
    model.eval()
    
    # Create a dummy input
    dummy_input = torch.randn(1, 3, meta["img_size"], meta["img_size"]).to(device)
    
    # Run inference
    try:
        with torch.no_grad():
            if is_torchscript:
                output = model(dummy_input)
            else:
                output = model(dummy_input)
        
        probs = torch.softmax(output, dim=1)[0]
        pred_idx = torch.argmax(probs).item()
        confidence = float(probs[pred_idx])
        pred_label = meta["label_names"][pred_idx]
        
        print(f"✓ Inference successful")
        print(f"  Predicted class: {pred_label}")
        print(f"  Confidence: {confidence:.4f}")
        print(f"  Output shape: {output.shape}")
        
        return True
    except Exception as e:
        print(f"✗ Inference failed: {e}")
        return False


def test_api_endpoint():
    """Test API endpoint if server is running."""
    print("\n" + "="*60)
    print("🔍 TESTING API ENDPOINT")
    print("="*60)
    
    try:
        import requests
    except ImportError:
        print("⚠ requests library not installed, skipping API test")
        return None
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✓ API is running on localhost:8000")
            print(f"  Status: {health.get('status')}")
            print(f"  Model loaded: {health.get('model_loaded')}")
            print(f"  Device: {health.get('device')}")
            print(f"  Best accuracy: {health.get('best_val_accuracy')}")
            return True
        else:
            print(f"⚠ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠ Could not connect to API (not running?)")
        print("  Start with: python api.py")
        return None
    except Exception as e:
        print(f"⚠ API test error: {e}")
        return None


def main():
    """Run all checks."""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  SKIN CLASSIFIER - SYSTEM VERIFICATION".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    results = {
        "Dataset": check_dataset(),
        "Model": check_model(),
        "Inference": test_model_inference(),
        "API": test_api_endpoint(),
    }
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    for test, result in results.items():
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⚠ SKIP"
        print(f"{test:.<30} {status}")
    
    all_critical_pass = all(v for k, v in results.items() if k != "API")
    
    print("\n" + "="*60)
    if all_critical_pass:
        print("✓ System is ready to use!")
        if results["API"] is None:
            print("  To start the API server, run: python api.py")
        return 0
    else:
        print("✗ System has issues. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
