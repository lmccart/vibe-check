import os
import time
from datetime import datetime

src_folder = "images"
log_file = "gdpr-log.txt"

current_time = time.time()
threshold = 30 * 24 * 60 * 60 # 30 days in seconds

with open(log_file, "a") as log:
    current_time_iso = datetime.utcfromtimestamp(current_time).isoformat()
    log.write(f"# {current_time_iso}\n")
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > threshold:
                file_size = os.path.getsize(file_path)
                creation_time = time.ctime(os.path.getctime(file_path))
                log.write(f"{file_path}\t{file_size}\t{creation_time}\n")
                os.remove(file_path)
