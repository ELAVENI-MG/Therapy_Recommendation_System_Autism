import os
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────
# 1. LOAD ALL SAVED MODELS
# ─────────────────────────────────────────

print("Loading models...")

ssbd_model    = joblib.load("ssbd_model.pkl")
ssbd_scaler   = joblib.load("ssbd_scaler.pkl")
ssbd_selector = joblib.load("ssbd_selector.pkl")
ssbd_le       = joblib.load("ssbd_label_encoder.pkl")

eye_model     = joblib.load("eye_model.pkl")
eye_scaler    = joblib.load("eye_scaler.pkl")

print("✅ All models loaded")

# ─────────────────────────────────────────
# 2. HELPER — extract scanpath features
#    (same function as train_eye_model.py)
# ─────────────────────────────────────────

def extract_eye_features(txt_path):
    try:
        df = pd.read_csv(txt_path, sep=",", header=0)
        df.columns = [c.strip().lower() for c in df.columns]

        if 'x' not in df.columns or 'y' not in df.columns or 'duration' not in df.columns:
            return None

        df = df[['x', 'y', 'duration']].dropna()
        if len(df) < 2:
            return None

        x        = df['x'].values.astype(float)
        y        = df['y'].values.astype(float)
        duration = df['duration'].values.astype(float)
        points   = np.column_stack([x, y])

        fixation_count    = len(df)
        avg_duration      = duration.mean()
        std_duration      = duration.std()
        min_duration      = duration.min()
        max_duration      = duration.max()
        total_duration    = duration.sum()

        diffs             = np.diff(points, axis=0)
        step_distances    = np.linalg.norm(diffs, axis=1)
        total_path_length = step_distances.sum()
        avg_step_distance = step_distances.mean()
        std_step_distance = step_distances.std()

        spread_x          = x.std()
        spread_y          = y.std()
        center_x          = x.mean()
        center_y          = y.mean()
        img_cx            = np.median(x)
        img_cy            = np.median(y)
        center_distance   = np.sqrt((center_x - img_cx)**2 + (center_y - img_cy)**2)

        try:
            hull_area = float(ConvexHull(points).volume) if len(points) >= 3 else 0.0
        except Exception:
            hull_area = 0.0

        q_cx         = x.mean()
        q_cy         = y.mean()
        q1           = np.sum((x <= q_cx) & (y <= q_cy))
        q2           = np.sum((x >  q_cx) & (y <= q_cy))
        q3           = np.sum((x <= q_cx) & (y >  q_cy))
        q4           = np.sum((x >  q_cx) & (y >  q_cy))
        quadrant_std = float(np.std([q1, q2, q3, q4]))

        revisit_count = 0
        for i in range(len(points)):
            for j in range(i + 2, min(i + 10, len(points))):
                if np.linalg.norm(points[i] - points[j]) < 50:
                    revisit_count += 1
        revisit_rate = revisit_count / max(len(points), 1)

        avg_saccade = float(step_distances.mean()) if len(step_distances) > 0 else 0.0
        max_saccade = float(step_distances.max())  if len(step_distances) > 0 else 0.0

        x_min, x_max = x.min(), x.max()
        y_min, y_max = y.min(), y.max()
        x_lo = x_min + (x_max - x_min) * 0.25
        x_hi = x_min + (x_max - x_min) * 0.75
        y_lo = y_min + (y_max - y_min) * 0.25
        y_hi = y_min + (y_max - y_min) * 0.75
        center_fix_ratio = float(
            np.sum((x >= x_lo) & (x <= x_hi) & (y >= y_lo) & (y <= y_hi))
            / max(fixation_count, 1)
        )

        return [
            fixation_count, avg_duration, std_duration, min_duration,
            max_duration, total_duration, total_path_length, avg_step_distance,
            std_step_distance, spread_x, spread_y, center_x, center_y,
            center_distance, hull_area, quadrant_std, revisit_rate,
            avg_saccade, max_saccade, center_fix_ratio
        ]

    except Exception as e:
        print(f"  Error: {e}")
        return None

# ─────────────────────────────────────────
# 3. LOAD EYE TRACKING SCANPATH DATA
#    and get eye model probability outputs
# ─────────────────────────────────────────

# ⚠️ UPDATE THESE to your actual scanpath folder paths
ASD_PATH = os.path.join(os.path.dirname(__file__), "ASD")
TD_PATH  = os.path.join(os.path.dirname(__file__), "TD")

eye_probs_list  = []
eye_labels_list = []

print("\nLoading ASD scanpaths for fusion...")
for file in sorted(os.listdir(ASD_PATH)):
    if not file.endswith(".txt"):
        continue
    features = extract_eye_features(os.path.join(ASD_PATH, file))
    if features is None:
        continue
    features_scaled = eye_scaler.transform(np.array(features).reshape(1, -1))
    probs           = eye_model.predict_proba(features_scaled)[0]
    eye_probs_list.append(probs)
    eye_labels_list.append(1)   # ASD = 1

print(f"  ✅ ASD eye samples: {np.sum(np.array(eye_labels_list)==1)}")

print("Loading TD scanpaths for fusion...")
for file in sorted(os.listdir(TD_PATH)):
    if not file.endswith(".txt"):
        continue
    features = extract_eye_features(os.path.join(TD_PATH, file))
    if features is None:
        continue
    features_scaled = eye_scaler.transform(np.array(features).reshape(1, -1))
    probs           = eye_model.predict_proba(features_scaled)[0]
    eye_probs_list.append(probs)
    eye_labels_list.append(0)   # TD = 0

print(f"  ✅ TD eye samples: {np.sum(np.array(eye_labels_list)==0)}")

eye_probs_arr  = np.array(eye_probs_list)    # shape: (n_eye, 2)
eye_labels_arr = np.array(eye_labels_list)

print(f"\nEye probs shape  : {eye_probs_arr.shape}")
print(f"Eye labels shape : {eye_labels_arr.shape}")

if len(eye_probs_arr) == 0:
    print("❌ No eye data loaded. Check ASD_PATH and TD_PATH.")
    import sys
    sys.exit()

# ─────────────────────────────────────────
# 4. LOAD SSBD DATASET
#    and get ssbd model probability outputs
# ─────────────────────────────────────────

print("\nLoading SSBD dataset for fusion...")

df_ssbd = pd.read_csv("ssbd_dataset.csv")

from sklearn.preprocessing import LabelEncoder
le_bodypart  = LabelEncoder()
le_intensity = LabelEncoder()

df_ssbd["bodypart"]  = le_bodypart.fit_transform(df_ssbd["bodypart"])
df_ssbd["intensity"] = le_intensity.fit_transform(df_ssbd["intensity"])
df_ssbd["category"]  = ssbd_le.transform(df_ssbd["category"])

df_ssbd["frames_per_duration"]    = df_ssbd["frames"] / (df_ssbd["duration"] + 1e-5)
df_ssbd["behaviour_per_duration"] = df_ssbd["behaviour_count"] / (df_ssbd["duration"] + 1e-5)
df_ssbd["intensity_x_behaviour"]  = df_ssbd["intensity"] * df_ssbd["behaviour_count"]

ssbd_features_cols = [
    "frames", "duration", "bodypart", "intensity", "behaviour_count",
    "frames_per_duration", "behaviour_per_duration", "intensity_x_behaviour"
]

X_ssbd = df_ssbd[ssbd_features_cols].values
y_ssbd = df_ssbd["category"].values

# Scale and select exactly like training
X_ssbd_scaled   = ssbd_scaler.transform(X_ssbd)
X_ssbd_selected = ssbd_selector.transform(X_ssbd_scaled)

# Get probability outputs — shape: (n_ssbd, n_classes)
ssbd_probs_all = ssbd_model.predict_proba(X_ssbd_selected)

print(f"SSBD probs shape : {ssbd_probs_all.shape}")
print(f"SSBD classes     : {ssbd_model.classes_}")

# ─────────────────────────────────────────
# 5. ALIGN BOTH DATASETS
#    Eye dataset is base — sample SSBD to match
# ─────────────────────────────────────────

n_eye  = len(eye_labels_arr)
n_ssbd = len(y_ssbd)

print(f"\nEye samples  : {n_eye}")
print(f"SSBD samples : {n_ssbd}")

np.random.seed(42)
ssbd_idx            = np.random.choice(n_ssbd, size=n_eye, replace=(n_ssbd < n_eye))
ssbd_probs_aligned  = ssbd_probs_all[ssbd_idx]   # shape: (n_eye, n_ssbd_classes)

print(f"Aligned SSBD probs shape : {ssbd_probs_aligned.shape}")
print(f"Eye probs shape          : {eye_probs_arr.shape}")

# ─────────────────────────────────────────
# 6. BUILD FUSION FEATURE VECTOR
#    Concatenate ssbd_probs + eye_probs
# ─────────────────────────────────────────

fusion_X = np.hstack([ssbd_probs_aligned, eye_probs_arr])
fusion_y = eye_labels_arr

print(f"\nFusion input shape : {fusion_X.shape}")
print(f"Fusion labels      : TD={np.sum(fusion_y==0)}, ASD={np.sum(fusion_y==1)}")

# Validate no empty rows
assert fusion_X.ndim == 2, f"❌ fusion_X must be 2D, got shape {fusion_X.shape}"
assert len(fusion_X) == len(fusion_y), "❌ X and y length mismatch"

# ─────────────────────────────────────────
# 7. SCALE FUSION FEATURES
# ─────────────────────────────────────────

fusion_scaler  = StandardScaler()
fusion_X_scaled = fusion_scaler.fit_transform(fusion_X)

# ─────────────────────────────────────────
# 8. TRAIN / TEST SPLIT
# ─────────────────────────────────────────

X_train, X_test, y_train, y_test = train_test_split(
    fusion_X_scaled, fusion_y,
    test_size=0.2,
    random_state=42,
    stratify=fusion_y
)

print(f"\nTrain size : {X_train.shape[0]}")
print(f"Test size  : {X_test.shape[0]}")

# ─────────────────────────────────────────
# 9. CROSS VALIDATION
# ─────────────────────────────────────────

fusion_model = LogisticRegression(
    C=1.0,
    class_weight='balanced',
    max_iter=1000,
    random_state=42
)

skf    = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_acc = cross_val_score(fusion_model, X_train, y_train, cv=skf, scoring='accuracy')
cv_f1  = cross_val_score(fusion_model, X_train, y_train, cv=skf, scoring='f1_weighted')

print(f"\n── Cross-Validation ──")
print(f"CV Accuracy : {cv_acc.mean()*100:.2f}% ± {cv_acc.std()*100:.2f}%")
print(f"CV F1-Score : {cv_f1.mean():.3f} ± {cv_f1.std():.3f}")

# ─────────────────────────────────────────
# 10. TRAIN FINAL MODEL
# ─────────────────────────────────────────

fusion_model.fit(X_train, y_train)

# ─────────────────────────────────────────
# 11. EVALUATE
# ─────────────────────────────────────────

y_pred    = fusion_model.predict(X_test)
train_acc = fusion_model.score(X_train, y_train)
test_acc  = accuracy_score(y_test, y_pred)

print(f"\n── Final Results ──")
print(f"Train Accuracy : {train_acc*100:.2f}%")
print(f"Test  Accuracy : {test_acc*100:.2f}%")

gap = train_acc - test_acc
if gap < 0.05:
    print(f"Overfit Gap    : {gap*100:.2f}% ✅ Good generalization")
elif gap < 0.10:
    print(f"Overfit Gap    : {gap*100:.2f}% ⚠️  Mild overfitting")
else:
    print(f"Overfit Gap    : {gap*100:.2f}% ❌ Overfitting")

print("\n── Classification Report ──")
print(classification_report(y_test, y_pred, target_names=["TD", "ASD"]))

# ─────────────────────────────────────────
# 12. CONFUSION MATRIX
# ─────────────────────────────────────────

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=["TD", "ASD"],
            yticklabels=["TD", "ASD"])
plt.title("Confusion Matrix — Fusion Model")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.savefig("fusion_confusion_matrix.png", dpi=150)
plt.show()

# ─────────────────────────────────────────
# 13. MODEL COMPARISON
# ─────────────────────────────────────────

print("\n── Model Comparison ──")
ssbd_binary   = (ssbd_probs_aligned[:, 1] > 0.5).astype(int) if ssbd_probs_aligned.shape[1] > 1 else ssbd_probs_aligned[:, 0]
eye_binary    = (eye_probs_arr[:, 1] > 0.5).astype(int)
fusion_binary = fusion_model.predict(fusion_X_scaled)

ssbd_acc   = accuracy_score(fusion_y, ssbd_binary)
eye_acc    = accuracy_score(fusion_y, eye_binary)
fusion_acc = accuracy_score(fusion_y, fusion_binary)

print(f"SSBD Model alone  : {ssbd_acc*100:.2f}%")
print(f"Eye Model alone   : {eye_acc*100:.2f}%")
print(f"Fusion Model      : {fusion_acc*100:.2f}%")

plt.figure(figsize=(7, 4))
models  = ["SSBD Model", "Eye Model", "Fusion Model"]
scores  = [ssbd_acc*100, eye_acc*100, fusion_acc*100]
colors  = ["#60a5fa", "#34d399", "#f97316"]
bars    = plt.bar(models, scores, color=colors, width=0.5)
plt.ylim(0, 110)
plt.ylabel("Accuracy (%)")
plt.title("Model Comparison")
for bar, score in zip(bars, scores):
    plt.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 1,
             f"{score:.1f}%", ha='center', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig("model_comparison.png", dpi=150)
plt.show()

# ─────────────────────────────────────────
# 14. SAVE
# ─────────────────────────────────────────

joblib.dump(fusion_model,  "fusion_model.pkl")
joblib.dump(fusion_scaler, "fusion_scaler.pkl")

print("\n✅ fusion_model.pkl saved")
print("✅ fusion_scaler.pkl saved")
print(f"\nFusion input size : {fusion_X.shape[1]} features")
print(f"  SSBD probs      : {ssbd_probs_aligned.shape[1]} features")
print(f"  Eye probs       : {eye_probs_arr.shape[1]} features")