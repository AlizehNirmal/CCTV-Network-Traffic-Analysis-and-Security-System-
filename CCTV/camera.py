import cv2
import threading
import time
import urllib.request
import numpy as np

PHONE_STREAM_URL = 'http://192.168.0.103:8080/video'

class Camera:
    def __init__(self):
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        while self.running:
            try:
                cap = cv2.VideoCapture(PHONE_STREAM_URL)
                while self.running and cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        with self.lock:
                            self.frame = frame
                    else:
                        break
                cap.release()
            except Exception as e:
                print(f"[Camera] Connection error: {e}")
            time.sleep(2)

    def get_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            ret, buffer = cv2.imencode('.jpg', self.frame)
            return buffer.tobytes() if ret else None

    def stop(self):
        self.running = False

camera = Camera()
