import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────
# 1. PATHS
# ─────────────────────────────────────────

ASD_PATH = os.path.join(os.path.dirname(__file__), "ASD")
TD_PATH  = os.path.join(os.path.dirname(__file__), "TD")

# ─────────────────────────────────────────
# 2. FEATURE EXTRACTION FROM TXT SCANPATH
# ─────────────────────────────────────────

def extract_features(txt_path):
    try:
        df = pd.read_csv(txt_path, sep=",", header=0)

        # Lowercase all column names
        df.columns = [c.strip().lower() for c in df.columns]

        # Verify required columns exist
        if 'x' not in df.columns or 'y' not in df.columns or 'duration' not in df.columns:
            print(f"  Missing columns in {txt_path}: {list(df.columns)}")
            return None

        df = df[['x', 'y', 'duration']].dropna()

        if len(df) < 2:
            return None

        x        = df['x'].values.astype(float)
        y        = df['y'].values.astype(float)
        duration = df['duration'].values.astype(float)
        points   = np.column_stack([x, y])

        # ── Feature 1: Fixation count ──
        fixation_count = len(df)

        # ── Feature 2: Duration features ──
        avg_duration   = duration.mean()
        std_duration   = duration.std()
        min_duration   = duration.min()
        max_duration   = duration.max()
        total_duration = duration.sum()

        # ── Feature 3: Scanpath length ──
        diffs             = np.diff(points, axis=0)
        step_distances    = np.linalg.norm(diffs, axis=1)
        total_path_length = step_distances.sum()
        avg_step_distance = step_distances.mean()
        std_step_distance = step_distances.std()

        # ── Feature 4: Gaze spread ──
        spread_x = x.std()
        spread_y = y.std()

        # ── Feature 5: Center of gaze ──
        center_x = x.mean()
        center_y = y.mean()

        # ── Feature 6: Distance from image center ──
        img_cx          = np.median(x)
        img_cy          = np.median(y)
        center_distance = np.sqrt((center_x - img_cx)**2 + (center_y - img_cy)**2)

        # ── Feature 7: Convex hull area ──
        try:
            if len(points) >= 3:
                hull      = ConvexHull(points)
                hull_area = float(hull.volume)
            else:
                hull_area = 0.0
        except Exception:
            hull_area = 0.0

        # ── Feature 8: Quadrant distribution ──
        q_cx         = x.mean()
        q_cy         = y.mean()
        q1           = np.sum((x <= q_cx) & (y <= q_cy))
        q2           = np.sum((x >  q_cx) & (y <= q_cy))
        q3           = np.sum((x <= q_cx) & (y >  q_cy))
        q4           = np.sum((x >  q_cx) & (y >  q_cy))
        quadrant_std = float(np.std([q1, q2, q3, q4]))

        # ── Feature 9: Revisit rate ──
        revisit_count = 0
        for i in range(len(points)):
            for j in range(i + 2, min(i + 10, len(points))):
                if np.linalg.norm(points[i] - points[j]) < 50:
                    revisit_count += 1
        revisit_rate = revisit_count / max(len(points), 1)

        # ── Feature 10: Saccade amplitude ──
        avg_saccade = float(step_distances.mean()) if len(step_distances) > 0 else 0.0
        max_saccade = float(step_distances.max())  if len(step_distances) > 0 else 0.0

        # ── Feature 11: Center fixation ratio ──
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
            fixation_count,       # 1
            avg_duration,         # 2
            std_duration,         # 3
            min_duration,         # 4
            max_duration,         # 5
            total_duration,       # 6
            total_path_length,    # 7
            avg_step_distance,    # 8
            std_step_distance,    # 9
            spread_x,             # 10
            spread_y,             # 11
            center_x,             # 12
            center_y,             # 13
            center_distance,      # 14
            hull_area,            # 15
            quadrant_std,         # 16
            revisit_rate,         # 17
            avg_saccade,          # 18
            max_saccade,          # 19
            center_fix_ratio      # 20
        ]

    except Exception as e:
        print(f"  Error reading {txt_path}: {e}")
        return None

# ─────────────────────────────────────────
# 3. LOAD ALL TXT FILES
# ─────────────────────────────────────────

data   = []
labels = []
files  = []

print("Loading ASD scanpaths...")
if not os.path.exists(ASD_PATH):
    print(f"  ❌ ASD folder not found at: {ASD_PATH}")
else:
    for file in sorted(os.listdir(ASD_PATH)):
        if not file.endswith(".txt"):
            continue
        path     = os.path.join(ASD_PATH, file)
        features = extract_features(path)
        if features is not None:
            data.append(features)
            labels.append(1)
            files.append(file)
    print(f"  ✅ Loaded {np.sum(np.array(labels) == 1)} ASD samples")

print("\nLoading TD scanpaths...")
td_start = len(data)
if not os.path.exists(TD_PATH):
    print(f"  ❌ TD folder not found at: {TD_PATH}")
else:
    for file in sorted(os.listdir(TD_PATH)):
        if not file.endswith(".txt"):
            continue
        path     = os.path.join(TD_PATH, file)
        features = extract_features(path)
        if features is not None:
            data.append(features)
            labels.append(0)
            files.append(file)
    print(f"  ✅ Loaded {len(data) - td_start} TD samples")

# ─────────────────────────────────────────
# 4. VALIDATE
# ─────────────────────────────────────────

if len(data) == 0:
    print("\n❌ No data loaded. Check folder paths.")
    import sys
    sys.exit()

data   = np.array(data)
labels = np.array(labels)

print(f"\n── Dataset Summary ──")
print(f"Total samples : {len(data)}")
print(f"Feature count : {data.shape[1]}")
print(f"ASD count     : {np.sum(labels == 1)}")
print(f"TD  count     : {np.sum(labels == 0)}")

# ─────────────────────────────────────────
# 5. FEATURE NAMES
# ─────────────────────────────────────────

feature_names = [
    "Fixation count",
    "Avg duration",
    "Std duration",
    "Min duration",
    "Max duration",
    "Total duration",
    "Total path length",
    "Avg step distance",
    "Std step distance",
    "Spread X",
    "Spread Y",
    "Center X",
    "Center Y",
    "Center distance",
    "Hull area",
    "Quadrant std",
    "Revisit rate",
    "Avg saccade",
    "Max saccade",
    "Center fixation ratio"
]

# ─────────────────────────────────────────
# 6. SCALE AND SAVE SCALER
# ─────────────────────────────────────────

scaler      = StandardScaler()
data_scaled = scaler.fit_transform(data)

# Save scaler immediately so app.py can use it
joblib.dump(scaler, "eye_scaler.pkl")
print("\n✅ eye_scaler.pkl saved")

# ─────────────────────────────────────────
# 7. TRAIN / TEST SPLIT
# ─────────────────────────────────────────

X_train, X_test, y_train, y_test = train_test_split(
    data_scaled, labels,
    test_size=0.2,
    random_state=42,
    stratify=labels
)

print(f"\nTrain size : {X_train.shape[0]}")
print(f"Test size  : {X_test.shape[0]}")

# ─────────────────────────────────────────
# 8. CROSS VALIDATION
# ─────────────────────────────────────────

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    min_samples_split=5,
    min_samples_leaf=3,
    max_features='sqrt',
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

skf    = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_acc = cross_val_score(model, X_train, y_train, cv=skf, scoring='accuracy')
cv_f1  = cross_val_score(model, X_train, y_train, cv=skf, scoring='f1_weighted')

print(f"\n── Cross-Validation ──")
print(f"CV Accuracy : {cv_acc.mean()*100:.2f}% ± {cv_acc.std()*100:.2f}%")
print(f"CV F1-Score : {cv_f1.mean():.3f} ± {cv_f1.std():.3f}")

# ─────────────────────────────────────────
# 9. TRAIN FINAL MODEL
# ─────────────────────────────────────────

model.fit(X_train, y_train)

# ─────────────────────────────────────────
# 10. EVALUATE
# ─────────────────────────────────────────

y_pred    = model.predict(X_test)
train_acc = model.score(X_train, y_train)
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
    print(f"Overfit Gap    : {gap*100:.2f}% ❌ Overfitting — reduce max_depth")

print("\n── Classification Report ──")
print(classification_report(y_test, y_pred, target_names=["TD", "ASD"]))

# ─────────────────────────────────────────
# 11. CONFUSION MATRIX
# ─────────────────────────────────────────

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=["TD", "ASD"],
            yticklabels=["TD", "ASD"])
plt.title("Confusion Matrix — Scanpath Eye Model")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.savefig("eye_confusion_matrix.png", dpi=150)
plt.show()

# ─────────────────────────────────────────
# 12. FEATURE IMPORTANCE
# ─────────────────────────────────────────

importances = model.feature_importances_
indices     = np.argsort(importances)[::-1]

plt.figure(figsize=(10, 6))
plt.barh(
    [feature_names[i] for i in indices],
    importances[indices],
    color='steelblue'
)
plt.title("Feature Importance — Scanpath Eye Model")
plt.xlabel("Importance Score")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("eye_feature_importance.png", dpi=150)
plt.show()

print("\n── Top 5 Most Important Features ──")
for i in range(5):
    print(f"  {i+1}. {feature_names[indices[i]]:30s} {importances[indices[i]]:.4f}")

# ─────────────────────────────────────────
# 13. SAVE MODEL AND SCALER
# ─────────────────────────────────────────

joblib.dump(model, "eye_model.pkl")

print("\n✅ eye_model.pkl saved")
print("✅ eye_scaler.pkl saved")
print("\n── Files saved ──")
print("  eye_model.pkl  — 20 scanpath features")
print("  eye_scaler.pkl — StandardScaler fitted on same features")
print("\nRun train_fusion_model.py next to rebuild fusion_model.pkl")