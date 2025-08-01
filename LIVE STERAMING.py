from flask import Flask, Response, render_template_string
from flask_httpauth import HTTPBasicAuth
import cv2, threading

app = Flask(__name__)
auth = HTTPBasicAuth()

# ইউজার ডেটা
users = {
    "admin": "mypassword123"
}

@auth.verify_password
def verify_password(username, password):
    return users.get(username) == password

# ক্যামেরা থ্রেড সেটআপ
camera = cv2.VideoCapture(0)
lock = threading.Lock()
frame = None

def camera_thread():
    global frame
    while True:
        with lock:
            success, img = camera.read()
            if success:
                _, buffer = cv2.imencode('.jpg', img)
                frame = buffer.tobytes()

# থ্রেড চালু করো
t = threading.Thread(target=camera_thread, daemon=True)
t.start()

# HTML টেমপ্লেট
html = """
<html>
<head><title>Secure Live Stream</title></head>
<body>
<h1>Live Camera Feed</h1>
<img src="{{ url_for('video_feed') }}">
</body>
</html>
"""

@app.route('/')
@auth.login_required
def index():
    return render_template_string(html)

@app.route('/video_feed')
@auth.login_required
def video_feed():
    def generate():
        while True:
            with lock:
                if frame is not None:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

