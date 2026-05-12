import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'security.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            src_ip TEXT,
            dst_ip TEXT,
            message TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ip_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_ip TEXT NOT NULL,
            dst_ip TEXT NOT NULL,
            action TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO ip_rules (id, src_ip, dst_ip, action)
        VALUES (1, '192.168.0.103', '192.168.100.8', 'ALLOW')
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def insert_alert(source, alert_type, severity, src_ip, dst_ip, message):
    conn = get_db()
    conn.execute('''
        INSERT INTO alerts (source, alert_type, severity, src_ip, dst_ip, message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (source, alert_type, severity, src_ip, dst_ip, message))
    conn.commit()
    conn.close()

def get_alerts(limit=100):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_ip_rules():
    conn = get_db()
    rows = conn.execute('SELECT * FROM ip_rules').fetchall()
    conn.close()
    return [dict(r) for r in rows]
