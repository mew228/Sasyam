"""
model/train.py
══════════════════════════════════════════════════════════════
Sasyam — Crop Classification Model Training (All 14 Steps)
MobileNetV2 transfer learning + fine-tuning on 4 crop classes.
══════════════════════════════════════════════════════════════
"""

# ════════════════════════════════════════════════════════════
# STEP 1 — Imports & Reproducibility
# ════════════════════════════════════════════════════════════
import os
import json
import random
import datetime
import numpy as np
import matplotlib
matplotlib.use("Agg")          # Non-interactive backend (no GUI needed)
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import (
    GlobalAveragePooling2D, Dense, Dropout, BatchNormalization,
    RandomFlip, RandomRotation, RandomZoom, RandomBrightness, RandomContrast,
    Input
)
from tensorflow.keras import Model
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
)
from sklearn.metrics import classification_report, confusion_matrix

# ── Reproducibility seeds ────────────────────────────────── #
random.seed(42)
np.random.seed(42)
tf.random.set_seed(42)

print("=" * 60)
print("  Sasyam Crop Classifier — Training Pipeline")
print("=" * 60)
print(f"  TensorFlow version : {tf.__version__}")

gpus = tf.config.list_physical_devices("GPU")
if gpus:
    print(f"  GPU detected       : {[g.name for g in gpus]}")
    # Allow memory growth to avoid OOM on shared GPU
    for g in gpus:
        tf.config.experimental.set_memory_growth(g, True)
else:
    print("  Training on CPU — this will take longer")

print("=" * 60)


# ════════════════════════════════════════════════════════════
# STEP 2 — Constants
# ════════════════════════════════════════════════════════════
DATASET_DIR       = "../dataset"
MODEL_SAVE_PATH   = "sasyam_crop_model.keras"
BEST_MODEL_PATH   = "sasyam_best.keras"
CLASS_INDICES_PATH = "class_indices.json"
HISTORY_PATH      = "training_history.json"
MODEL_CARD_PATH   = "model_card.md"
CONFUSION_MATRIX_PATH = "confusion_matrix.png"
TRAINING_CURVES_PATH  = "training_curves.png"

IMG_SIZE         = (224, 224)
BATCH_SIZE       = 32
PHASE1_EPOCHS    = 15
PHASE2_EPOCHS    = 10
PHASE1_LR        = 1e-3
PHASE2_LR        = 1e-5
UNFREEZE_LAYERS  = 30
VALIDATION_SPLIT = 0.2
AUTOTUNE         = tf.data.AUTOTUNE
CLASS_NAMES      = ["Corn", "Other", "Sugarcane", "Wheat"]


# ════════════════════════════════════════════════════════════
# STEP 3 — Data Loading with Validation
# ════════════════════════════════════════════════════════════
print("\n=== Dataset Summary ===")

if not os.path.isdir(DATASET_DIR):
    raise FileNotFoundError(
        f"\nDataset directory not found: {os.path.abspath(DATASET_DIR)}\n"
        "Please place class sub-folders inside ../dataset/"
    )

missing = [c for c in CLASS_NAMES if not os.path.isdir(os.path.join(DATASET_DIR, c))]
if missing:
    raise FileNotFoundError(
        f"Missing class folder(s): {missing}\n"
        f"Expected inside: {os.path.abspath(DATASET_DIR)}"
    )

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def count_images(folder):
    return sum(
        1 for f in os.listdir(folder)
        if os.path.splitext(f)[1].lower() in IMG_EXTS
    )

total_images = 0
class_counts = {}
for cls in CLASS_NAMES:
    n = count_images(os.path.join(DATASET_DIR, cls))
    class_counts[cls] = n
    total_images += n
    print(f"  {cls:<12}: {n:>6} images")

print(f"  {'Total':<12}: {total_images:>6} images")
print()

# Load datasets
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split = VALIDATION_SPLIT,
    subset           = "training",
    seed             = 42,
    image_size       = IMG_SIZE,
    batch_size       = BATCH_SIZE,
    label_mode       = "int",
    shuffle          = True,
    class_names      = CLASS_NAMES
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split = VALIDATION_SPLIT,
    subset           = "validation",
    seed             = 42,
    image_size       = IMG_SIZE,
    batch_size       = BATCH_SIZE,
    label_mode       = "int",
    shuffle          = False,
    class_names      = CLASS_NAMES
)

print(f"  Training batches  : {len(train_ds)}")
print(f"  Validation batches: {len(val_ds)}")

# Save class indices
class_indices = {name: idx for idx, name in enumerate(train_ds.class_names)}
with open(CLASS_INDICES_PATH, "w") as f:
    json.dump(class_indices, f, indent=2)
print(f"\n  class_indices.json saved: {class_indices}")

# Performance optimisation
train_ds = train_ds.cache().shuffle(1000).prefetch(AUTOTUNE)
val_ds   = val_ds.cache().prefetch(AUTOTUNE)


# ════════════════════════════════════════════════════════════
# STEP 4 — Augmentation Layer (inside model, training-only)
# ════════════════════════════════════════════════════════════
augmentation_layer = tf.keras.Sequential([
    RandomFlip("horizontal_and_vertical"),
    RandomRotation(0.2),
    RandomZoom(0.15),
    RandomBrightness(0.2),
    RandomContrast(0.2),
], name="augmentation")


# ════════════════════════════════════════════════════════════
# STEP 5 — Build Model
# ════════════════════════════════════════════════════════════
def build_model(num_classes=4):
    base = MobileNetV2(
        include_top  = False,
        weights      = "imagenet",
        input_shape  = (*IMG_SIZE, 3)
    )
    base.trainable = False

    inputs = Input(shape=(*IMG_SIZE, 3), name="image_input")
    x = augmentation_layer(inputs)
    # preprocess_input via Lambda for Keras 3 functional API compatibility
    x = tf.keras.layers.Lambda(
        lambda img: tf.keras.applications.mobilenet_v2.preprocess_input(img),
        name="mobilenet_preprocess"
    )(x)
    x = base(x, training=False)
    x = GlobalAveragePooling2D(name="gap")(x)
    x = BatchNormalization(name="bn")(x)
    x = Dense(256, activation="relu", name="dense_256")(x)
    x = Dropout(0.4, name="drop_256")(x)
    x = Dense(128, activation="relu", name="dense_128")(x)
    x = Dropout(0.3, name="drop_128")(x)
    outputs = Dense(num_classes, activation="softmax", name="predictions")(x)

    model = Model(inputs, outputs, name="sasyam_crop_classifier")
    return model, base

model, base_model = build_model(num_classes=len(CLASS_NAMES))

print("\n")
model.summary()

total_params     = model.count_params()
trainable_params = sum(tf.size(w).numpy() for w in model.trainable_weights)
non_trainable    = total_params - trainable_params
print(f"\n  Total params      : {total_params:,}")
print(f"  Trainable params  : {trainable_params:,}")
print(f"  Non-trainable     : {non_trainable:,}")


# ════════════════════════════════════════════════════════════
# STEP 6 — Callbacks
# ════════════════════════════════════════════════════════════
class EpochLogger(tf.keras.callbacks.Callback):
    """Pretty per-epoch log line."""
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        total = self.params.get("epochs", "?")
        lr  = float(tf.keras.backend.get_value(self.model.optimizer.learning_rate))
        print(
            f"  [Epoch {epoch+1:02d}/{total:02d}] "
            f"loss: {logs.get('loss', 0):.4f} | "
            f"acc: {logs.get('accuracy', 0):.4f} | "
            f"val_loss: {logs.get('val_loss', 0):.4f} | "
            f"val_acc: {logs.get('val_accuracy', 0):.4f} | "
            f"lr: {lr:.6f}"
        )

def make_callbacks():
    return [
        EarlyStopping(
            monitor              = "val_accuracy",
            patience             = 4,
            restore_best_weights = True,
            verbose              = 1
        ),
        ReduceLROnPlateau(
            monitor  = "val_loss",
            factor   = 0.3,
            patience = 2,
            min_lr   = 1e-7,
            verbose  = 1
        ),
        ModelCheckpoint(
            filepath       = BEST_MODEL_PATH,
            monitor        = "val_accuracy",
            save_best_only = True,
            verbose        = 1
        ),
        EpochLogger()
    ]


# ════════════════════════════════════════════════════════════
# STEP 7 — Phase 1: Feature Extraction (base frozen)
# ════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("  PHASE 1: Feature Extraction (base layers frozen)")
print("  Training only the classification head")
print("=" * 60 + "\n")

model.compile(
    optimizer = tf.keras.optimizers.Adam(learning_rate=PHASE1_LR),
    loss      = "sparse_categorical_crossentropy",
    metrics   = ["accuracy"]
)

history1 = model.fit(
    train_ds,
    epochs          = PHASE1_EPOCHS,
    validation_data = val_ds,
    callbacks       = make_callbacks(),
    verbose         = 0    # Silenced — EpochLogger handles output
)

best_p1_acc = max(history1.history["val_accuracy"])
print(f"\n  ✓ Phase 1 best val_accuracy: {best_p1_acc * 100:.2f}%")


# ════════════════════════════════════════════════════════════
# STEP 8 — Phase 2: Fine-Tuning (last 30 layers unfrozen)
# ════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("  PHASE 2: Fine-Tuning (unfreezing last 30 layers)")
print("  Learning rate reduced to 1e-5")
print("=" * 60 + "\n")

# Unfreeze last UNFREEZE_LAYERS layers of MobileNetV2
base_model.trainable = True
for layer in base_model.layers[:-UNFREEZE_LAYERS]:
    layer.trainable = False

trainable_now = sum(1 for l in base_model.layers if l.trainable)
frozen_now    = sum(1 for l in base_model.layers if not l.trainable)
print(f"  MobileNetV2 — Trainable layers: {trainable_now} | Frozen: {frozen_now}")
print(f"  Total trainable variables: {len(model.trainable_variables)}")

model.compile(
    optimizer = tf.keras.optimizers.Adam(learning_rate=PHASE2_LR),
    loss      = "sparse_categorical_crossentropy",
    metrics   = ["accuracy"]
)

history2 = model.fit(
    train_ds,
    epochs          = PHASE1_EPOCHS + PHASE2_EPOCHS,
    initial_epoch   = len(history1.epoch),
    validation_data = val_ds,
    callbacks       = make_callbacks(),
    verbose         = 0
)

best_p2_acc = max(history2.history["val_accuracy"])
print(f"\n  ✓ Phase 2 best val_accuracy: {best_p2_acc * 100:.2f}%")


# ════════════════════════════════════════════════════════════
# STEP 9 — Save Model & History
# ════════════════════════════════════════════════════════════
model.save(MODEL_SAVE_PATH)
print(f"\n  ✓ Model saved → {MODEL_SAVE_PATH}")

final_val_acc  = max(best_p1_acc, best_p2_acc)
total_epochs   = len(history1.epoch) + len(history2.epoch)
training_date  = datetime.date.today().isoformat()

merged_history = {
    "phase1": {
        "accuracy":     history1.history["accuracy"],
        "val_accuracy": history1.history["val_accuracy"],
        "loss":         history1.history["loss"],
        "val_loss":     history1.history["val_loss"]
    },
    "phase2": {
        "accuracy":     history2.history["accuracy"],
        "val_accuracy": history2.history["val_accuracy"],
        "loss":         history2.history["loss"],
        "val_loss":     history2.history["val_loss"]
    },
    "final_val_accuracy": round(float(final_val_acc), 6),
    "total_epochs":       total_epochs,
    "training_date":      training_date,
    "class_names":        CLASS_NAMES
}

with open(HISTORY_PATH, "w") as f:
    json.dump(merged_history, f, indent=2)
print(f"  ✓ History saved → {HISTORY_PATH}")

# Verify saved model loads correctly
_check = tf.keras.models.load_model(MODEL_SAVE_PATH, compile=False)
print("  ✓ Model verified — loads correctly")
del _check


# ════════════════════════════════════════════════════════════
# STEP 10 — Evaluation & Confusion Matrix
# ════════════════════════════════════════════════════════════
print("\n=== Final Evaluation ===")
final_loss, final_acc = model.evaluate(val_ds, verbose=0)
print(f"  Val Loss     : {final_loss:.4f}")
print(f"  Val Accuracy : {final_acc * 100:.2f}%")

# Collect all true labels and predictions
all_true  = []
all_preds = []

for images, labels in val_ds:
    preds = model.predict(images, verbose=0)
    all_preds.extend(np.argmax(preds, axis=1))
    all_true.extend(labels.numpy())

all_true  = np.array(all_true)
all_preds = np.array(all_preds)

print("\n=== Classification Report ===")
report_str = classification_report(
    all_true, all_preds,
    target_names = CLASS_NAMES,
    digits       = 4
)
print(report_str)

# Parse report dict for model card
report_dict = classification_report(
    all_true, all_preds,
    target_names = CLASS_NAMES,
    output_dict  = True
)

# Confusion Matrix plot
cm = confusion_matrix(all_true, all_preds)

plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot        = True,
    fmt          = "d",
    cmap         = "Greens",
    xticklabels  = CLASS_NAMES,
    yticklabels  = CLASS_NAMES,
    linewidths   = 0.5,
    linecolor    = "white"
)
plt.title("Sasyam Model — Confusion Matrix", fontsize=14, fontweight="bold", pad=12)
plt.xlabel("Predicted Label", fontsize=11)
plt.ylabel("True Label",      fontsize=11)
plt.tight_layout()
plt.savefig(CONFUSION_MATRIX_PATH, dpi=150)
plt.close()
print(f"  ✓ Confusion matrix saved → {CONFUSION_MATRIX_PATH}")


# ════════════════════════════════════════════════════════════
# STEP 11 — Training Curves Plot
# ════════════════════════════════════════════════════════════
p1_epochs = len(history1.epoch)
p2_epochs_range = range(p1_epochs, p1_epochs + len(history2.epoch))

p1_x = range(1, p1_epochs + 1)
p2_x = range(p1_epochs + 1, p1_epochs + len(history2.epoch) + 1)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Sasyam Crop Classifier — Training History", fontsize=14, fontweight="bold", y=1.02)

# ── Left: Accuracy ──────────────────────────────────────────
ax = axes[0]
ax.plot(p1_x, history1.history["accuracy"],     "b-",  linewidth=1.8, label="P1 Train Acc")
ax.plot(p1_x, history1.history["val_accuracy"], "b--", linewidth=1.8, label="P1 Val Acc")
ax.plot(p2_x, history2.history["accuracy"],     "g-",  linewidth=1.8, label="P2 Train Acc")
ax.plot(p2_x, history2.history["val_accuracy"], "g--", linewidth=1.8, label="P2 Val Acc")
ax.axvline(x=p1_epochs + 0.5, color="red", linestyle="--", linewidth=1.2, label="Phase boundary")
ax.set_title("Model Accuracy", fontsize=12)
ax.set_xlabel("Epoch")
ax.set_ylabel("Accuracy")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_ylim([0, 1.05])

# ── Right: Loss ─────────────────────────────────────────────
ax = axes[1]
ax.plot(p1_x, history1.history["loss"],     "b-",  linewidth=1.8, label="P1 Train Loss")
ax.plot(p1_x, history1.history["val_loss"], "b--", linewidth=1.8, label="P1 Val Loss")
ax.plot(p2_x, history2.history["loss"],     "g-",  linewidth=1.8, label="P2 Train Loss")
ax.plot(p2_x, history2.history["val_loss"], "g--", linewidth=1.8, label="P2 Val Loss")
ax.axvline(x=p1_epochs + 0.5, color="red", linestyle="--", linewidth=1.2, label="Phase boundary")
ax.set_title("Model Loss", fontsize=12)
ax.set_xlabel("Epoch")
ax.set_ylabel("Loss")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(TRAINING_CURVES_PATH, dpi=150, bbox_inches="tight")
plt.close()
print(f"  ✓ Training curves saved → {TRAINING_CURVES_PATH}")


# ════════════════════════════════════════════════════════════
# STEP 12 — Per-Class Confidence Sanity Check
# ════════════════════════════════════════════════════════════
print("\n=== Sanity Check (3 images × 4 classes) ===")

IMG_EXTS_GLOB = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
sanity_correct = 0
sanity_total   = 0

for cls_name in CLASS_NAMES:
    cls_folder = os.path.join(DATASET_DIR, cls_name)
    files = [
        f for f in os.listdir(cls_folder)
        if f.lower().endswith(IMG_EXTS_GLOB)
    ]
    picks = random.sample(files, min(3, len(files)))

    for fname in picks:
        fpath = os.path.join(cls_folder, fname)
        try:
            img_raw = tf.keras.utils.load_img(fpath, target_size=IMG_SIZE)
            arr     = tf.keras.utils.img_to_array(img_raw)              # HWC float32
            arr_exp = np.expand_dims(arr, axis=0)                       # (1,224,224,3)

            probs   = model.predict(arr_exp, verbose=0)[0]
            pred_idx  = int(np.argmax(probs))
            pred_cls  = CLASS_NAMES[pred_idx]
            confidence = float(probs[pred_idx]) * 100
            correct   = pred_cls == cls_name

            sanity_correct += int(correct)
            sanity_total   += 1

            mark = "✓ CORRECT" if correct else f"✗ WRONG (true: {cls_name})"
            label = f"[{cls_name}/{fname}]"
            print(f"  {label:<40}  → Predicted: {pred_cls:<10} ({confidence:5.1f}%)  {mark}")
        except Exception as e:
            print(f"  [!] Could not process {fname}: {e}")

sanity_pct = (sanity_correct / sanity_total * 100) if sanity_total else 0
print(f"\n  Sanity Check: {sanity_correct}/{sanity_total} correct ({sanity_pct:.1f}%)")


# ════════════════════════════════════════════════════════════
# STEP 13 — Generate model_card.md
# ════════════════════════════════════════════════════════════
def fmt_metric(cls):
    d = report_dict.get(cls, {})
    return (
        f"| {cls:<12} | {d.get('precision',0):.4f}    | "
        f"{d.get('recall',0):.4f} | {d.get('f1-score',0):.4f}   | "
        f"{int(d.get('support',0)):>7} |"
    )

model_card_content = f"""# Sasyam Crop Classification Model

## Model Details
- **Architecture**: MobileNetV2 + Custom Classification Head
- **Input Size**: 224×224×3 (RGB)
- **Output Classes**: 4 ({', '.join(CLASS_NAMES)})
- **Framework**: TensorFlow / Keras {tf.__version__}
- **Training Date**: {training_date}
- **Final Validation Accuracy**: {final_val_acc * 100:.2f}%

## Training Data
- **Dataset**: Indian agricultural satellite/field imagery
- **Total Images**: {total_images:,}
- **Class Distribution**: {', '.join(f'{k}: {v:,}' for k, v in class_counts.items())}
- **Split**: 80% train / 20% validation
- **Augmentation**: RandomFlip, RandomRotation(0.2), RandomZoom(0.15), RandomBrightness(0.2), RandomContrast(0.2)

## Training Process
- **Phase 1** (Feature Extraction): {len(history1.epoch)} epochs, Adam lr=1e-3, MobileNetV2 base frozen
- **Phase 2** (Fine-Tuning): {len(history2.epoch)} epochs, Adam lr=1e-5, last {UNFREEZE_LAYERS} MobileNetV2 layers unfrozen
- **Total Epochs Trained**: {total_epochs}
- **Callbacks**: EarlyStopping (patience=4), ReduceLROnPlateau (factor=0.3), ModelCheckpoint

## Per-Class Performance

| Class        | Precision | Recall | F1-Score | Support |
|--------------|-----------|--------|----------|---------|
{chr(10).join(fmt_metric(c) for c in CLASS_NAMES)}
| **Macro Avg**   | {report_dict['macro avg']['precision']:.4f}    | {report_dict['macro avg']['recall']:.4f} | {report_dict['macro avg']['f1-score']:.4f}   | {int(report_dict['macro avg']['support']):>7} |
| **Weighted Avg**| {report_dict['weighted avg']['precision']:.4f}    | {report_dict['weighted avg']['recall']:.4f} | {report_dict['weighted avg']['f1-score']:.4f}   | {int(report_dict['weighted avg']['support']):>7} |

## Architecture Details

```
Input (224, 224, 3)
  → Augmentation (RandomFlip, Rotation, Zoom, Brightness, Contrast)
  → MobileNetV2 preprocess_input  [rescales to -1…1]
  → MobileNetV2 (ImageNet weights) [Phase 1: frozen | Phase 2: last 30 unfrozen]
  → GlobalAveragePooling2D
  → BatchNormalization
  → Dense(256, relu) → Dropout(0.4)
  → Dense(128, relu) → Dropout(0.3)
  → Dense(4, softmax)
```

## Usage

```python
import tensorflow as tf
import numpy as np
from PIL import Image

model = tf.keras.models.load_model('sasyam_crop_model.h5')
CLASS_NAMES = {CLASS_NAMES}

img  = Image.open("your_image.jpg").resize((224, 224))
arr  = np.expand_dims(np.array(img, dtype="float32"), axis=0)  # (1, 224, 224, 3)
pred = model.predict(arr)
print(CLASS_NAMES[np.argmax(pred)], f"{{np.max(pred)*100:.1f}}%")
```

## Files

| File | Description |
|------|-------------|
| `sasyam_crop_model.h5` | Full saved Keras model |
| `sasyam_best.h5` | Best checkpoint (highest val_accuracy) |
| `class_indices.json` | Class name → integer index mapping |
| `training_history.json` | Full per-epoch metrics for both phases |
| `confusion_matrix.png` | Validation set confusion matrix heatmap |
| `training_curves.png` | Accuracy & loss curves for both phases |

## Limitations & Intended Use
- **Intended for**: Crop type identification to feed Sasyam's yield prediction pipeline
- **Not intended for**: Medical, legal, financial, or critical safety decisions
- **Known limitations**: Performance may degrade on very small crops, extreme lighting, or partial/obscured images
- **Dataset bias**: Trained primarily on well-lit Indian field imagery
"""

with open(MODEL_CARD_PATH, "w", encoding="utf-8") as f:
    f.write(model_card_content)
print(f"\n  ✓ Model card saved → {MODEL_CARD_PATH}")


# ════════════════════════════════════════════════════════════
# STEP 14 — Final Summary Banner
# ════════════════════════════════════════════════════════════
print("\n")
print("╔══════════════════════════════════════════════════╗")
print("║           SASYAM MODEL TRAINING COMPLETE         ║")
print("╠══════════════════════════════════════════════════╣")
print(f"║  Final Val Accuracy : {final_val_acc*100:5.2f}%                    ║")
print(f"║  Total Epochs       : {total_epochs:<5}                      ║")
print("║  Model saved        : sasyam_crop_model.keras✓    ║")
print("║  Class indices      : class_indices.json    ✓    ║")
print("║  Training history   : training_history.json ✓    ║")
print("║  Confusion matrix   : confusion_matrix.png  ✓    ║")
print("║  Training curves    : training_curves.png   ✓    ║")
print("║  Model card         : model_card.md         ✓    ║")
print("╚══════════════════════════════════════════════════╝")
