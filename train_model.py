import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

print("=== 1. Loading Extracted Feature Dataset ===")
df = pd.read_csv("hdfs_features_labeled.csv")

# Filter out UNKNOWN labels or corrupt records
df = df[df['label'] != 'UNKNOWN'].dropna()

print(f"Cleaned Dataset Shape: {df.shape}")
print("\nTarget Class Distribution:")
print(df['label'].value_counts())

# Prepare Features (X) and Target (y)
feature_cols = ['access_count', 'recency_seconds', 'age_seconds']
X = df[feature_cols]
y = df['label']

# Split Data (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("\n=== 2. Training Random Forest Classifier ===")
rf_clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
rf_clf.fit(X_train, y_train)

print("\n=== 3. Model Evaluation ===")
y_pred = rf_clf.predict(X_test)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\n=== 4. Feature Importance ===")
importances = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': rf_clf.feature_importances_
}).sort_values(by='Importance', ascending=False)
print(importances.to_string(index=False))

# Save trained model
joblib.dump(rf_clf, 'hdfs_tiering_model.pkl')
print("\n=== Model saved successfully as 'hdfs_tiering_model.pkl'! ===")
