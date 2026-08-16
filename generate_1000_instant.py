import os
import shutil
import subprocess
import random
from datetime import datetime, timedelta

TEMP_DIR = "temp_hdfs_staging"
HDFS_TARGET = "/tier_data"
LOG_FILE = os.path.expanduser("~/hadoop/logs/hdfs-audit.log")

print("=== 1. Creating 1,000 files locally ===")
if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)
os.makedirs(TEMP_DIR)

files_metadata = []

for i in range(1, 1001):
    file_type = "hot" if i <= 200 else ("warm" if i <= 600 else "cold")
    filename = f"{file_type}_file_{i}.txt"
    filepath = os.path.join(TEMP_DIR, filename)
    
    with open(filepath, "w") as f:
        f.write(f"Sample content for {file_type} file {i}\n")
        
    if file_type == "hot":
        reads = random.randint(15, 30)
    elif file_type == "warm":
        reads = random.randint(3, 10)
    else:
        reads = 0
        
    files_metadata.append((f"{HDFS_TARGET}/{filename}", reads))

print("=== 2. Bulk Uploading to HDFS (Single Command) ===")
subprocess.run(f"hdfs dfs -rm -r -f {HDFS_TARGET}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(f"hdfs dfs -mkdir -p {HDFS_TARGET}", shell=True)
subprocess.run(f"hdfs dfs -put {TEMP_DIR}/* {HDFS_TARGET}/", shell=True)
shutil.rmtree(TEMP_DIR)

print("=== 3. Injecting Access Telemetry into hdfs-audit.log ===")
now = datetime.now()

with open(LOG_FILE, "a") as log:
    for hdfs_path, read_count in files_metadata:
        # Log creation
        create_time = (now - timedelta(minutes=random.randint(60, 300))).strftime("%Y-%m-%d %H:%M:%S,000")
        log.write(f"{create_time} INFO FSNamesystem.audit: allowed=true\tugi=parth (auth:SIMPLE)\tip=/127.0.0.1\tcmd=create\tsrc={hdfs_path}\tdst=null\tperm=parth:supergroup:rwxr-xr-x\tproto=rpc\n")
        
        # Log simulated reads
        for _ in range(read_count):
            access_time = (now - timedelta(minutes=random.randint(1, 50))).strftime("%Y-%m-%d %H:%M:%S,000")
            log.write(f"{access_time} INFO FSNamesystem.audit: allowed=true\tugi=parth (auth:SIMPLE)\tip=/127.0.0.1\tcmd=open\tsrc={hdfs_path}\tdst=null\tperm=null\tproto=rpc\n")

print("=== Done! 1,000 files in HDFS and audit log populated instantly. ===")
