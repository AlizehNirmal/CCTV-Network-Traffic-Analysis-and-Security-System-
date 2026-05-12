import time
import re
import threading
import os
from db import insert_alert

SNORT_LOG_PATH = '/var/log/snort/alert'
ALLOWED_SRC = '192.168.0.103'
ALLOWED_DST = '192.168.100.8'

def parse_snort_alert(block):
    src_ip, dst_ip, msg = None, None, 'Unknown Snort Alert'
    msg_match = re.search(r'\[\*\*\] \[.*?\] (.*?) \[\*\*\]', block)
    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+):\d+ -> (\d+\.\d+\.\d+\.\d+)', block)
    if msg_match:
        msg = msg_match.group(1).strip()
    if ip_match:
        src_ip = ip_match.group(1)
        dst_ip = ip_match.group(2)
    return src_ip, dst_ip, msg

def monitor_snort_log():
    print("[Snort Monitor] Starting...")
    while not os.path.exists(SNORT_LOG_PATH):
        time.sleep(5)
    with open(SNORT_LOG_PATH, 'r') as f:
        f.seek(0, 2)
        buffer = ''
        while True:
            line = f.readline()
            if line:
                buffer += line
                if line.strip() == '':
                    if buffer.strip():
                        src_ip, dst_ip, msg = parse_snort_alert(buffer)
                        severity = 'HIGH'
                        if src_ip == ALLOWED_SRC and dst_ip == ALLOWED_DST:
                            severity = 'LOW'
                        insert_alert('Snort', 'NETWORK', severity, src_ip, dst_ip, msg)
                    buffer = ''
            else:
                time.sleep(0.5)

def start_snort_monitor():
    t = threading.Thread(target=monitor_snort_log, daemon=True)
    t.start()
