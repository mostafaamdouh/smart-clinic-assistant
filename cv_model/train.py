"""
HAM10000 Skin Disease Classifier - Training Pipeline (Improved)
Model: EfficientNetB0 (frozen backbone → fine-tuned)
Classes: 7 skin disease categories
Improvements:
  - Oversampling for minority classes
  - Two-phase training: frozen backbone then full fine-tuning
  - More epochs (30 total)
  - Lower LR for fine-tuning phase
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path
import json

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torchvision import transforms, models
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
from tqdm import tqdm


# ─── Config ─────────────────────────────────────────────────────────────────

DATA_DIR       = Path("data/ham10000")
IMAGES_DIR     = DATA_DIR / "images"
METADATA_CSV   = DATA_DIR / "HAM10000_metadata.csv"
OUTPUT_DIR     = Path("model_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IMG_SIZE         = 224
BATCH_SIZE       = 32
NUM_EPOCHS       = 30          
FINETUNE_EPOCH   = 15          
LR               = 1e-3
LR_FINETUNE      = 1e-4        
WEIGHT_DECAY     = 1e-4
NUM_WORKERS      = 4
SEED             = 42

LABEL_MAP = {
    "nv":   0,   # Melanocytic nevi
    "mel":  1,   # Melanoma
    "bkl":  2,   # Benign keratosis-like lesions
    "bcc":  3,   # Basal cell carcinoma
    "akiec":4,   # Actinic keratoses / intraepithelial carcinoma
    "vasc": 5,   # Vascular lesions
    "df":   6,   # Dermatofibroma
}

LABEL_NAMES = {v: k for k, v in LABEL_MAP.items()}

torch.manual_seed(SEED)
np.random.seed(SEED)


# ─── Dataset ─────────────────────────────────────────────────────────────────

class HAM10000Dataset(Dataset):
    def __init__(self, df: pd.DataFrame, images_dir: Path, transform=None):
        self.df = df.reset_index(drop=True)
        self.images_dir = images_dir
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = self.images_dir / f"{row['image_id']}.jpg"
        image = Image.open(img_path).convert("RGB")
        label = LABEL_MAP[row["dx"]]

        if self.transform:
            image = self.transform(image)
        return image, label


# ─── Transforms ─────────────────────────────────────────────────────────────

train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(20),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

val_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


# ─── Oversampling ────────────────────────────────────────────────────────────

def make_weighted_sampler(df: pd.DataFrame) -> WeightedRandomSampler:
    """WeightedRandomSampler to oversample minority classes."""
    class_counts = df["dx"].value_counts().to_dict()
    sample_weights = [1.0 / class_counts[row["dx"]] for _, row in df.iterrows()]
    sample_weights = torch.tensor(sample_weights, dtype=torch.float)
    return WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True
    )


# ─── Model ───────────────────────────────────────────────────────────────────

def build_model(num_classes: int = 7, freeze_backbone: bool = True) -> nn.Module:
    """EfficientNetB0 with frozen backbone and custom classification head."""
    model = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=True),
        nn.Linear(in_features, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.3),
        nn.Linear(512, num_classes),
    )

    for param in model.classifier.parameters():
        param.requires_grad = True

    return model


def unfreeze_backbone(model, optimizer, device):
    """Unfreeze all layers for fine-tuning with smaller LR."""
    print("\n  Unfreezing backbone for fine-tuning...")
    for param in model.parameters():
        param.requires_grad = True

    # Reset optimizer with lower LR
    optimizer.param_groups.clear()
    optimizer.add_param_group({
        'params': model.parameters(),
        'lr': LR_FINETUNE,
        'weight_decay': WEIGHT_DECAY
    })
    return optimizer


# ─── Training ────────────────────────────────────────────────────────────────

def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0, 0, 0

    for images, labels in tqdm(loader, desc="  Train", leave=False):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        preds = outputs.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += images.size(0)

    return total_loss / total, correct / total


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0, 0, 0
    all_preds, all_labels = [], []

    for images, labels in tqdm(loader, desc="  Val  ", leave=False):
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)

        total_loss += loss.item() * images.size(0)
        preds = outputs.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += images.size(0)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    return total_loss / total, correct / total, all_preds, all_labels


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # ── Load metadata ─────────────────────────────────────────────────────
    print("\nLoading metadata...")
    df = pd.read_csv(METADATA_CSV)
    print(f"Total samples: {len(df)}")
    print(f"Class distribution:\n{df['dx'].value_counts()}")

    df = df.drop_duplicates(subset=["lesion_id"]).reset_index(drop=True)
    print(f"After dedup: {len(df)} unique lesions")

    # ── Train / Val split ─────────────────────────────────────────────────
    train_df, val_df = train_test_split(
        df, test_size=0.2, stratify=df["dx"], random_state=SEED
    )
    print(f"Train: {len(train_df)} | Val: {len(val_df)}")

    # ── Datasets & Loaders ────────────────────────────────────────────────
    train_dataset = HAM10000Dataset(train_df, IMAGES_DIR, train_transform)
    val_dataset   = HAM10000Dataset(val_df,   IMAGES_DIR, val_transform)

    # Oversampling للـ training
    sampler = make_weighted_sampler(train_df)
    print("✓ Using WeightedRandomSampler for oversampling minority classes")

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE,
                              sampler=sampler, num_workers=NUM_WORKERS, pin_memory=True)
    val_loader   = DataLoader(val_dataset,   batch_size=BATCH_SIZE,
                              shuffle=False, num_workers=NUM_WORKERS, pin_memory=True)

    # ── Class weights (handle imbalance) ─────────────────────────────────
    class_counts = train_df["dx"].value_counts().to_dict()
    weights = [1.0 / class_counts.get(LABEL_NAMES[i], 1) for i in range(len(LABEL_MAP))]
    weights = torch.tensor(weights, dtype=torch.float).to(device)
    weights = weights / weights.sum() * len(LABEL_MAP)

    # ── Model, Loss, Optimizer ────────────────────────────────────────────
    model = build_model(num_classes=len(LABEL_MAP), freeze_backbone=True).to(device)
    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=LR, weight_decay=WEIGHT_DECAY
    )
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS)

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total     = sum(p.numel() for p in model.parameters())
    print(f"\nTrainable params: {trainable:,} / {total:,} ({100*trainable/total:.1f}%)")

    # ── Training loop ─────────────────────────────────────────────────────
    best_val_acc = 0.0
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    finetuning = False

    print("\nStarting training...\n")
    for epoch in range(1, NUM_EPOCHS + 1):

        # Unfreeze backbone at FINETUNE_EPOCH
        if epoch == FINETUNE_EPOCH and not finetuning:
            optimizer = unfreeze_backbone(model, optimizer, device)
            scheduler = optim.lr_scheduler.CosineAnnealingLR(
                optimizer, T_max=(NUM_EPOCHS - FINETUNE_EPOCH)
            )
            finetuning = True

        print(f"Epoch [{epoch}/{NUM_EPOCHS}]{'  [Fine-tuning]' if finetuning else ''}")
        tr_loss, tr_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        vl_loss, vl_acc, preds, labels = evaluate(model, val_loader, criterion, device)
        scheduler.step()

        history["train_loss"].append(tr_loss)
        history["val_loss"].append(vl_loss)
        history["train_acc"].append(tr_acc)
        history["val_acc"].append(vl_acc)

        print(f"  Train Loss: {tr_loss:.4f} | Acc: {tr_acc:.4f}")
        print(f"  Val   Loss: {vl_loss:.4f} | Acc: {vl_acc:.4f}")

        if vl_acc > best_val_acc:
            best_val_acc = vl_acc
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "val_acc": vl_acc,
                "label_map": LABEL_MAP,
            }, OUTPUT_DIR / "best_model.pth")
            print(f"  ✓ Saved best model (val_acc={vl_acc:.4f})")

    # ── Final evaluation ──────────────────────────────────────────────────
    print("\n── Final Evaluation ──────────────────────────────────────────")
    checkpoint = torch.load(OUTPUT_DIR / "best_model.pth", map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])

    _, final_acc, preds, labels = evaluate(model, val_loader, criterion, device)
    label_names = [LABEL_NAMES[i] for i in range(len(LABEL_MAP))]
    print(f"\nBest Val Accuracy: {final_acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(labels, preds, target_names=label_names))

    # ── Lock & Export ─────────────────────────────────────────────────────
    for param in model.parameters():
        param.requires_grad = False
    model.eval()

    try:
        dummy = torch.zeros(1, 3, IMG_SIZE, IMG_SIZE).to(device)
        traced = torch.jit.trace(model, dummy)
        traced.save(str(OUTPUT_DIR / "skin_classifier.pt"))
        print("\n✓ Model locked and exported to skin_classifier.pt")
    except Exception as e:
        print(f"\n⚠ Warning: TorchScript export failed ({e})")
        torch.save({
            "model_state_dict": model.state_dict(),
            "label_map": LABEL_MAP,
        }, OUTPUT_DIR / "skin_classifier.pth")
        print("✓ Model saved as skin_classifier.pth")

    meta = {
        "model": "EfficientNetB0",
        "img_size": IMG_SIZE,
        "num_classes": len(LABEL_MAP),
        "label_map": LABEL_MAP,
        "label_names": label_names,
        "best_val_accuracy": best_val_acc,
        "mean": [0.485, 0.456, 0.406],
        "std":  [0.229, 0.224, 0.225],
    }
    with open(OUTPUT_DIR / "model_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax1.plot(history["train_loss"], label="Train"); ax1.plot(history["val_loss"], label="Val")
    ax1.axvline(x=FINETUNE_EPOCH-1, color='r', linestyle='--', label='Fine-tune start')
    ax1.set(title="Loss", xlabel="Epoch"); ax1.legend()
    ax2.plot(history["train_acc"], label="Train"); ax2.plot(history["val_acc"], label="Val")
    ax2.axvline(x=FINETUNE_EPOCH-1, color='r', linestyle='--', label='Fine-tune start')
    ax2.set(title="Accuracy", xlabel="Epoch"); ax2.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "training_curves.png", dpi=120)
    print("✓ Training curves saved.")


if __name__ == "__main__":
    main()