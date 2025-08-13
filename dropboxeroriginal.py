import os
import socket
import webbrowser
import threading
import time
from flask import Flask, request, send_from_directory, render_template_string

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

HOST = "0.0.0.0"
PORT = 8000
local_ip = get_local_ip()

app = Flask(__name__)

HTML_PAGE = """
<!doctype html>
<title>File Transfer</title>
<h1>Upload new File</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
<h2>Files:</h2>
<ul>
{% for filename in files %}
  <li><a href="/uploads/{{ filename }}">{{ filename }}</a></li>
{% endfor %}
</ul>
"""

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files.get("file")
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(HTML_PAGE, files=files)

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def run_server():
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False, threaded=True)

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# Wait until the port is open
def wait_for_server(ip, port, timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((ip, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.1)
    return False

if wait_for_server(local_ip, PORT):
    url = f"http://{local_ip}:{PORT}"
    print(f"Server running at: {url}")
    webbrowser.open(url)
else:
    print("Error: Couldn't connect to server.")

input("Press Enter to stop server...")
