import time
import json
import threading
import os
from db import insert_alert

WAZUH_LOG_PATH = '/var/ossec/logs/alerts/alerts.json'

def parse_wazuh_alert(line):
    try:
        data = json.loads(line)
        src_ip = data.get('data', {}).get('srcip', 'N/A')
        dst_ip = data.get('data', {}).get('dstip', 'N/A')
        msg = data.get('rule', {}).get('description', 'Unknown Wazuh Alert')
        level = data.get('rule', {}).get('level', 0)
        severity = 'LOW' if level < 7 else 'HIGH' if level >= 12 else 'MEDIUM'
        return src_ip, dst_ip, msg, severity
    except Exception:
        return 'N/A', 'N/A', 'Malformed Wazuh alert', 'LOW'

def monitor_wazuh_log():
    print("[Wazuh Monitor] Starting...")
    while not os.path.exists(WAZUH_LOG_PATH):
        print("[Wazuh Monitor] Waiting for log file...")
        time.sleep(10)
    with open(WAZUH_LOG_PATH, 'r') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if line and line.strip():
                src_ip, dst_ip, msg, severity = parse_wazuh_alert(line)
                insert_alert('Wazuh', 'ENDPOINT', severity, src_ip, dst_ip, msg)
            else:
                time.sleep(1)

def start_wazuh_monitor():
    t = threading.Thread(target=monitor_wazuh_log, daemon=True)
    t.start()
