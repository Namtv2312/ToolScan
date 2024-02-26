from functools import wraps
import os
import subprocess
import tempfile
from flask import Flask, request, send_file, jsonify, g
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify,  render_template_string
import secrets
from datetime import datetime, timedelta
import configparser
executor = ThreadPoolExecutor(max_workers=10) 
app = Flask(__name__)

CONFIG_FILE = '/toolscan/config.ini'
def modify_tokens(token):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    config['token'] = {'token': token}
    with open(CONFIG_FILE, 'w') as configfile:
     config.write(configfile)

config = configparser.ConfigParser()
config.read(CONFIG_FILE)
users = dict(config['credentials'])
tokens = {}

def generate_token():
    token = secrets.token_urlsafe(16)
    expiration_time = datetime.now() + timedelta(weeks=1)
    tokens[token] = expiration_time
    return token

@app.route('/', methods=['GET'])
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
</head>
<body>
    <form action="/login" method="post">
        <label for="username">Username:</label><br>
        <input type="text" id="username" name="username"><br>
        <label for="password">Password:</label><br>
        <input type="password" id="password" name="password"><br><br>
        <button type="submit">Login</button>
    </form>
    <div id="token" style="display:none;">
        <p>Your token is: <span id="token_value"></span></p>
    </div>
    <script>
        document.querySelector('form').addEventListener('submit', function(event) {
            event.preventDefault();
            var username = document.getElementById('username').value;
            var password = document.getElementById('password').value;
            var data = {
                'username': username,
                'password': password
            };
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            }).then(function(response) {
                return response.json();
            }).then(function(data) {
                showToken(data.token);
            });
        });

        function showToken(token) {
            document.getElementById("token_value").innerText = token;
            document.getElementById("token").style.display = "block";
        }
    </script>
</body>
</html>
    """)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in users and users[username] == password:
        token = generate_token()
        modify_tokens(token)
        return jsonify({'token': token, 'expires_in': '1 week'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401


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

def convert_to_pdf(input_file_path):
    try:
        subprocess.run(['libreoffice', '--convert-to', 'pdf', '--outdir', os.path.dirname(input_file_path), input_file_path])
        return True
    except Exception as e:
        print(f"Error converting file to PDF: {e}")
        return False

def process_file(file_path):
    success = convert_to_pdf(file_path)
    if success:
        return file_path
    else:
        return None

@app.route('/upload', methods=['POST'])
@require_api_token
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    if file:
        file_path = tempfile.NamedTemporaryFile(delete=False).name  # Tạo một file tạm thời
        file.save(file_path)
        
        # Gửi nhiệm vụ xử lý file đến ThreadPoolExecutor
        future = executor.submit(process_file, file_path)

        # Trả về kết quả khi xử lý xong
        pdf_path = future.result()

        if pdf_path:
            # Serve the PDF file for download
            return send_file(pdf_path + ".pdf", as_attachment=True, mimetype='application/pdf')
        else:
            return 'Failed to process the file'
    else:
        return 'Invalid file format'

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,  ssl_context= 'adhoc')