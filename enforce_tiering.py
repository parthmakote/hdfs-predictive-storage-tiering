import pandas as pd
import joblib
import subprocess

print("=== 1. Loading Trained Random Forest Model ===")
model = joblib.load('hdfs_tiering_model.pkl')

print("=== 2. Reading Extracted Features ===")
df = pd.read_csv('hdfs_features.csv').dropna()

feature_cols = ['access_count', 'recency_seconds', 'age_seconds']
X = df[feature_cols]

print(f"Loaded {len(df)} files for policy evaluation.")

print("\n=== 3. Predicting Optimal Storage Tiers ===")
df['predicted_tier'] = model.predict(X)

print("\nPredicted Tier Distribution:")
print(df['predicted_tier'].value_counts())

print("\n=== 4. Applying Storage Policies to HDFS ===")
policy_map = {'HOT': 'HOT', 'WARM': 'WARM', 'COLD': 'COLD'}

applied_count = 0
for idx, row in df.iterrows():
    file_path = row['file_path']
    predicted = row['predicted_tier']
    hdfs_policy = policy_map.get(predicted, 'HOT')
    
    cmd = f"hdfs storagepolicies -setStoragePolicy -path {file_path} -policy {hdfs_policy}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        applied_count += 1

print(f"\nSuccessfully set policies for {applied_count}/{len(df)} files!")

print("\n=== 5. Running HDFS Mover ===")
print("Executing 'hdfs mover -p /tier_data' to physically relocate blocks...")
mover_result = subprocess.run("hdfs mover -p /tier_data", shell=True, capture_output=True, text=True)
print(mover_result.stdout)

print("=== Tiering Enforcement Complete! ===")
