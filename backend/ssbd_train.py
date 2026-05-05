import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────
# 1. LOAD DATASET
# ─────────────────────────────────────────
df = pd.read_csv("ssbd_dataset.csv")

print("Dataset Shape:", df.shape)
print("\nClass Distribution:\n", df["category"].value_counts())
print("\nMissing Values:\n", df.isnull().sum())

# ─────────────────────────────────────────
# 2. ENCODE CATEGORICAL FEATURES
# ─────────────────────────────────────────
le_bodypart  = LabelEncoder()
le_intensity = LabelEncoder()
le_target    = LabelEncoder()

df["bodypart"]  = le_bodypart.fit_transform(df["bodypart"])
df["intensity"] = le_intensity.fit_transform(df["intensity"])
df["category"]  = le_target.fit_transform(df["category"])

print("\nEncoded Classes:", list(le_target.classes_))

# ─────────────────────────────────────────
# 3. FEATURE ENGINEERING
# ─────────────────────────────────────────
# Ratio features help the model generalize better
df["frames_per_duration"]    = df["frames"] / (df["duration"] + 1e-5)
df["behaviour_per_duration"] = df["behaviour_count"] / (df["duration"] + 1e-5)
df["intensity_x_behaviour"]  = df["intensity"] * df["behaviour_count"]

features = [
    "frames", "duration", "bodypart", "intensity", "behaviour_count",
    "frames_per_duration", "behaviour_per_duration", "intensity_x_behaviour"
]

X = df[features]
y = df["category"]

# ─────────────────────────────────────────
# 4. ADD NOISE AUGMENTATION (prevents memorization)
# ─────────────────────────────────────────
def augment_with_noise(X, y, noise_level=0.02, augment_factor=0.3):
    """Add slightly noisy copies of training samples"""
    n_augment = int(len(X) * augment_factor)
    idx = np.random.choice(len(X), n_augment, replace=True)

    X_aug = X.iloc[idx].copy().reset_index(drop=True)
    y_aug = y.iloc[idx].copy().reset_index(drop=True)

    # Add small noise only to numeric columns
    numeric_cols = ["frames", "duration", "behaviour_count",
                    "frames_per_duration", "behaviour_per_duration"]
    noise = np.random.normal(0, noise_level, X_aug[numeric_cols].shape)
    X_aug[numeric_cols] = X_aug[numeric_cols] + noise

    X_combined = pd.concat([X.reset_index(drop=True), X_aug], ignore_index=True)
    y_combined = pd.concat([y.reset_index(drop=True), y_aug], ignore_index=True)
    return X_combined, y_combined

# ─────────────────────────────────────────
# 5. TRAIN / TEST SPLIT
# ─────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y          # ensures equal class ratio in both splits
)

# Apply augmentation ONLY on training data
X_train_aug, y_train_aug = augment_with_noise(X_train, y_train,
                                               noise_level=0.02,
                                               augment_factor=0.3)

print(f"\nTrain size (after augment): {X_train_aug.shape[0]}")
print(f"Test size:                  {X_test.shape[0]}")

# ─────────────────────────────────────────
# 6. FEATURE SCALING
# ─────────────────────────────────────────
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_aug)   # fit only on train
X_test_scaled  = scaler.transform(X_test)             # transform test

# ─────────────────────────────────────────
# 7. FEATURE SELECTION (remove redundant features)
# ─────────────────────────────────────────
selector_model = RandomForestClassifier(
    n_estimators=50,
    max_depth=5,
    random_state=42
)
selector = SelectFromModel(selector_model, max_features=6)
selector.fit(X_train_scaled, y_train_aug)

X_train_sel = selector.transform(X_train_scaled)
X_test_sel  = selector.transform(X_test_scaled)

selected_features = [features[i] for i in selector.get_support(indices=True)]
print(f"\nSelected Features: {selected_features}")

# ─────────────────────────────────────────
# 8. REGULARIZED RANDOM FOREST MODEL
# ─────────────────────────────────────────
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=8,            # ← prevents deep overfitting trees
    min_samples_split=10,   # ← needs 10 samples to make a split
    min_samples_leaf=5,     # ← each leaf needs at least 5 samples
    max_features='sqrt',    # ← each tree sees sqrt(n_features)
    class_weight='balanced',# ← handles class imbalance
    random_state=42,
    n_jobs=-1
)

# ─────────────────────────────────────────
# 9. CROSS-VALIDATION (honest accuracy estimate)
# ─────────────────────────────────────────
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_acc = cross_val_score(model, X_train_sel, y_train_aug,
                          cv=skf, scoring='accuracy')
cv_f1  = cross_val_score(model, X_train_sel, y_train_aug,
                          cv=skf, scoring='f1_weighted')

print(f"\n── Cross-Validation Results ──")
print(f"CV Accuracy : {cv_acc.mean()*100:.2f}% ± {cv_acc.std()*100:.2f}%")
print(f"CV F1-Score : {cv_f1.mean():.3f}  ± {cv_f1.std():.3f}")

# ─────────────────────────────────────────
# 10. TRAIN FINAL MODEL
# ─────────────────────────────────────────
model.fit(X_train_sel, y_train_aug)

# ─────────────────────────────────────────
# 11. EVALUATE ON TEST SET
# ─────────────────────────────────────────
y_pred = model.predict(X_test_sel)

train_acc = model.score(X_train_sel, y_train_aug)
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
    print(f"Overfit Gap    : {gap*100:.2f}% ❌ Still overfitting")

print("\n── Classification Report ──")
print(classification_report(y_test, y_pred,
                             target_names=le_target.classes_))

# ─────────────────────────────────────────
# 12. CONFUSION MATRIX PLOT
# ─────────────────────────────────────────
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(7, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=le_target.classes_,
            yticklabels=le_target.classes_)
plt.title("Confusion Matrix — SSBD Classification")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
plt.show()

# ─────────────────────────────────────────
# 13. FEATURE IMPORTANCE PLOT
# ─────────────────────────────────────────
importances = model.feature_importances_
plt.figure(figsize=(8, 4))
plt.barh(selected_features, importances, color='steelblue')
plt.title("Feature Importance — Random Forest")
plt.xlabel("Importance Score")
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=150)
plt.show()

# ─────────────────────────────────────────
# 14. SAVE MODEL
# ─────────────────────────────────────────
import joblib
joblib.dump(model,    "ssbd_model.pkl")
joblib.dump(scaler,   "ssbd_scaler.pkl")
joblib.dump(selector, "ssbd_selector.pkl")
joblib.dump(le_target, "ssbd_label_encoder.pkl")
print("\n✅ Model saved successfully.")