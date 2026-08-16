import re
import pandas as pd
from datetime import datetime

LOG_FILE = "/home/parth/hadoop/logs/hdfs-audit.log"

file_stats = {}

log_pattern = re.compile(
    r'(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) INFO.*cmd=(?P<cmd>\w+)\s+src=(?P<src>[^\s]+)'
)

print("=== Parsing HDFS Audit Log ===")

with open(LOG_FILE, 'r') as f:
    for line in f:
        match = log_pattern.search(line)
        if not match:
            continue
        
        timestamp_str, cmd, src = match.groups()
        
        # Only track files in our target directory AND exclude temporary upload files
        if not src.startswith("/tier_data/") or src.endswith("._COPYING_"):
            continue
            
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')

        if src not in file_stats:
            file_stats[src] = {
                'file_path': src,
                'create_time': timestamp,
                'last_access_time': timestamp,
                'access_count': 0
            }

        if cmd == 'create':
            file_stats[src]['create_time'] = timestamp
        elif cmd == 'open':
            file_stats[src]['access_count'] += 1
            file_stats[src]['last_access_time'] = timestamp

data = []
now = datetime.now()

for path, stats in file_stats.items():
    recency_seconds = (now - stats['last_access_time']).total_seconds()
    age_seconds = (now - stats['create_time']).total_seconds()
    
    data.append({
        'file_path': stats['file_path'],
        'access_count': stats['access_count'],
        'recency_seconds': round(recency_seconds, 2),
        'age_seconds': round(age_seconds, 2)
    })

df = pd.DataFrame(data)
print("\n=== Cleaned Features for ML Model ===")
print(df.to_string(index=False))

df.to_csv("hdfs_features.csv", index=False)
print("\nFeatures saved to 'hdfs_features.csv'")
