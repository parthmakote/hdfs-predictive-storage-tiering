import streamlit as st
import pandas as pd
import joblib
import subprocess
import os
import plotly.express as px

st.set_page_config(page_title="HDFS Dynamic Storage Tiering", page_icon="⚡", layout="wide")

st.title("⚡ ML-Driven HDFS Dynamic Storage Tiering Dashboard")
st.markdown("Monitor file telemetry, analyze model predictions, and enforce automated storage policies in real time.")

def run_script(command):
    with st.spinner(f"Executing: `{command}`..."):
        res = subprocess.run(command, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            st.success(f"Successfully executed `{command}`!")
            if res.stdout:
                st.code(res.stdout, language="text")
        else:
            st.error(f"Error running `{command}`:")
            st.code(res.stderr, language="text")

# Sidebar - Controls
st.sidebar.header("🛠️ Pipeline Control Panel")
if st.sidebar.button("1. 🎲 Generate 1,000 Files & Logs"):
    run_script("python3 generate_1000_instant.py")
if st.sidebar.button("2. 📊 Extract Features from Audit Log"):
    run_script("python3 extract_features.py")
if st.sidebar.button("3. 🧠 Retrain Random Forest Model"):
    run_script("python3 train_model.py")

# Main Dashboard
MODEL_PATH = "hdfs_tiering_model.pkl"
DATA_PATH = "hdfs_features.csv"

if os.path.exists(DATA_PATH) and os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    df = pd.read_csv(DATA_PATH).dropna()

    df['predicted_tier'] = model.predict(df[['access_count', 'recency_seconds', 'age_seconds']])

    # Metrics Overview
    st.subheader("📌 Cluster Storage Overview")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Files", f"{len(df):,}")
    m2.metric("🔥 HOT Tier Files", f"{len(df[df['predicted_tier'] == 'HOT']):,}")
    m3.metric("🌤️ WARM Tier Files", f"{len(df[df['predicted_tier'] == 'WARM']):,}")
    m4.metric("❄️ COLD Tier Files", f"{len(df[df['predicted_tier'] == 'COLD']):,}")

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(df, names='predicted_tier', title="Tier Breakdown",
                         color='predicted_tier', color_discrete_map={'HOT':'#FF4B4B','WARM':'#FFAA00','COLD':'#1C83E1'})
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        fig_scatter = px.scatter(df, x='recency_seconds', y='access_count', color='predicted_tier',
                                 title="Access Frequency vs. Recency",
                                 color_discrete_map={'HOT':'#FF4B4B','WARM':'#FFAA00','COLD':'#1C83E1'})
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Fast Batch Enforcement
    st.subheader("🚀 Automated Enforcement Center")
    if st.button("⚡ Enforce Storage Policies Live", type="primary"):
        with st.spinner("Batch enforcing policies and executing HDFS Mover..."):
            # 1. Generate batch shell commands in memory
            commands = []
            for _, row in df.iterrows():
                commands.append(f"hdfs storagepolicies -setStoragePolicy -path {row['file_path']} -policy {row['predicted_tier']}")
            
            # Write batch script to temporary shell file
            with open("batch_enforce.sh", "w") as f:
                f.write("\n".join(commands))
            
            # Execute batch script in a single shell call
            res = subprocess.run("bash batch_enforce.sh", shell=True, capture_output=True, text=True)
            
            # Run mover
            mover_res = subprocess.run("hdfs mover -p /tier_data", shell=True, capture_output=True, text=True)
            
            st.success(f"Successfully applied storage policies across all {len(df)} files!")
            if mover_res.stdout:
                st.code(mover_res.stdout)
            elif mover_res.stderr:
                st.code(mover_res.stderr)

    # Telemetry Explorer Table
    st.subheader("🔍 HDFS File Telemetry Explorer")
    search_term = st.text_input("Filter by filename path:", "")
    filtered_df = df if not search_term else df[df['file_path'].str.contains(search_term, case=False)]
    st.dataframe(filtered_df, use_container_width=True)
