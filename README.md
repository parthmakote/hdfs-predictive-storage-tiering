# ML-Driven HDFS Dynamic Storage Tiering

An automated machine learning pipeline and Streamlit control dashboard that parses `hdfs-audit.log` telemetry to dynamically assign file storage policies (`HOT`, `WARM`, `COLD`) and execute HDFS block relocation.

## Core Features
* **Telemetry Extraction**: Parses access frequency, recency, and file age metrics from raw audit logs.
* **Random Forest Classifier**: Machine learning model trained to optimize file tier placement.
* **Batch Enforcement**: Multi-threaded and batched execution of `hdfs storagepolicies` and `hdfs mover`.
* **Interactive Web UI**: Real-time visualization dashboard built with Streamlit and Plotly.

## Quick Start
```bash
pip install -r requirements.txt
python3 -m streamlit run app.py

