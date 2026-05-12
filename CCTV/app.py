from flask import Flask, Response, jsonify, render_template, request
from camera import camera
from db import init_db, get_alerts, get_ip_rules, insert_alert
from snort_monitor import start_snort_monitor
from wazuh_monitor import start_wazuh_monitor
import time

app = Flask(__name__)

ALLOWED_SRC = '192.168.0.103'

def generate_frames():
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.033)

@app.before_request
def enforce_ip_policy():
    client_ip = request.remote_addr
    if request.path == '/video_feed' and client_ip != ALLOWED_SRC:
        insert_alert(
            'Flask', 'UNAUTHORIZED_ACCESS', 'HIGH',
            client_ip, '127.0.0.1',
            f'Unauthorized IP {client_ip} attempted to access video stream'
        )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/alerts')
def api_alerts():
    return jsonify(get_alerts(100))

@app.route('/api/rules')
def api_rules():
    return jsonify(get_ip_rules())

@app.route('/api/stats')
def api_stats():
    alerts = get_alerts(1000)
    return jsonify({
        'total': len(alerts),
        'high': sum(1 for a in alerts if a['severity'] == 'HIGH'),
        'medium': sum(1 for a in alerts if a['severity'] == 'MEDIUM'),
        'low': sum(1 for a in alerts if a['severity'] == 'LOW'),
        'snort': sum(1 for a in alerts if a['source'] == 'Snort'),
        'wazuh': sum(1 for a in alerts if a['source'] == 'Wazuh'),
    })

if __name__ == '__main__':
    init_db()
    camera.start()
    start_snort_monitor()
    start_wazuh_monitor()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
