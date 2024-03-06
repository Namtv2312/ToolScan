from AI_SCANNER import get_ai_scan_detection
from flask import Flask, request, jsonify, g
from gevent.pywsgi import WSGIServer
import argparse
from functools import wraps
app = Flask(__name__)
import tempfile
import ssl
import os
import configparser

CONFIG_FILE = os.path.join(os.path.dirname(__file__),"../config.ini")
def require_api_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        tokens = config.get('token', 'token')
        if token is None or token != f"Bearer {tokens}":
            return jsonify({"error": "Unauthorized"}), 401

        g.api_token = token

        return func(*args, **kwargs)

    return wrapper

@app.route('/')
def hello_world():
    return jsonify("hello world")
@app.route('/scan',methods=['POST'])
@require_api_token
def detect_ai():
    uploaded_file = request.files['file']
    file_path = tempfile.NamedTemporaryFile(delete=True).name
    uploaded_file.save(file_path)
    res = get_ai_scan_detection(file_path)
    return res
if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=8050, ssl_context= 'adhoc')
    parser = argparse.ArgumentParser(description='Run the Flask application with custom port')
    parser.add_argument('port', nargs='?', type=int, default=8050, help='Port number (default is 5000)')
    args = parser.parse_args()
    port = args.port
    http_server = WSGIServer(('', port), app, keyfile='keyfile.pem', certfile='certfile.pem', 
                             ssl_version=ssl.PROTOCOL_TLSv1_2)
    http_server.serve_forever()

