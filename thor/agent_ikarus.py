import argparse
import cgi
import http.server
import ipaddress
import json
import os
import shutil
import socketserver
import stat
import subprocess
import sys
import tempfile
import traceback
from io import StringIO
from typing import Iterable
from zipfile import ZipFile
import shlex

try:
    import re2 as re
except ImportError:
    import re

if sys.version_info[:2] < (3, 6):
    sys.exit("You are running an incompatible version of Python, please use >= 3.6")

if sys.maxsize > 2**32 and sys.platform == "win32":
    sys.exit("You should install python3 x86! not x64")

AGENT_VERSION = "1.0"
AGENT_FEATURES = [
    "execpy",
    "execute",
]
STATUS_INIT = 0x0001
state = {"status": STATUS_INIT}

# To send output to stdin comment out this 2 lines
sys.stdout = StringIO()
sys.stderr = StringIO()

class MiniHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    server_version = "AVScan Agent"

    def do_GET(self):
        request.client_ip, request.client_port = self.client_address
        request.form = {}
        request.files = {}
        request.method = "GET"

        self.httpd.handle(self)

    def do_POST(self):
        environ = {
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE": self.headers.get("Content-Type"),
        }

        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ=environ)

        request.client_ip, request.client_port = self.client_address
        request.form = {}
        request.files = {}
        request.method = "POST"

        if form.list:
            for key in form.keys():
                value = form[key]
                if value.filename:
                    request.files[key] = value.file
                else:
                    request.form[key] = value.value
        self.httpd.handle(self)

class MiniHTTPServer:
    def __init__(self):
        self.handler = MiniHTTPRequestHandler

        # Reference back to the server.
        self.handler.httpd = self

        self.routes = {
            "GET": [],
            "POST": [],
        }

    def run(self, host: ipaddress.IPv4Address = "0.0.0.0", port: int = 8005):
        self.s = socketserver.TCPServer((host, port), self.handler)
        self.s.allow_reuse_address = True
        self.s.serve_forever()

    def route(self, path: str, methods: Iterable[str] = ["GET"]):
        def register(fn):
            for method in methods:
                self.routes[method].append((re.compile(f"{path}$"), fn))
            return fn

        return register
    def handle(self, obj):
        if "client_ip" in state and request.client_ip != state["client_ip"]:
            if request.client_ip != "127.0.0.1":
                return
            if obj.path != "/status" or request.method != "POST":
                return

        for route, fn in self.routes[obj.command]:
            if route.match(obj.path):
                ret = fn()
                break
        else:
            ret = json_error(404, message="Route not found")
        ret.init()
        obj.send_response(ret.status_code)
        ret.headers(obj)
        obj.end_headers()

        if isinstance(ret, jsonify):
            obj.wfile.write(ret.json().encode())
        elif isinstance(ret, send_file):
            ret.write(obj.wfile)

    def shutdown(self):
        # BaseServer also features a .shutdown() method, but you can't use
        # that from the same thread as that will deadlock the whole thing.
        self.s._BaseServer__shutdown_request = True
class jsonify:
    """Wrapper that represents Flask.jsonify functionality."""

    def __init__(self, **kwargs):
        self.status_code = 200
        self.values = kwargs

    def init(self):
        pass

    def json(self):
        return json.dumps(self.values)

    def headers(self, obj):
        pass
class send_file:
    """Wrapper that represents Flask.send_file functionality."""

    def __init__(self, path):
        self.path = path
        self.status_code = 200

    def init(self):
        if not os.path.isfile(self.path):
            self.status_code = 404
            self.length = 0
        else:
            self.length = os.path.getsize(self.path)

    def write(self, sock):
        if not self.length:
            return

        with open(self.path, "r") as f:
            buf = f.read(1024 * 1024)
            while buf:
                sock.write(buf)
                buf = f.read(1024 * 1024)

    def headers(self, obj):
        obj.send_header("Content-Length", self.length)

class request:
    form = {}
    files = {}
    client_ip = None
    client_port = None
    method = None
    environ = {
        "werkzeug.server.shutdown": lambda: app.shutdown(),
    }

app = MiniHTTPServer()

def json_error(error_code: int, message: str) -> jsonify:
    r = jsonify(message=message, error_code=error_code)
    r.status_code = error_code
    return r

def json_exception(message: str) -> jsonify:
    r = jsonify(message=message, error_code=500, traceback=traceback.format_exc())
    r.status_code = 500
    return r


def json_success(message: str, **kwargs) -> jsonify:
    return jsonify(message=message, **kwargs)

@app.route("/")
def get_index():
    return json_success("AVScan Agent!", version=AGENT_VERSION, features=AGENT_FEATURES)

@app.route("/mkdir", methods=["POST"])
def do_mkdir():
    if "dirpath" not in request.form:
        return json_error(400, "No dirpath has been provided")

    mode = int(request.form.get("mode", 0o777))

    try:
        os.makedirs(request.form["dirpath"], mode=mode)
    except Exception:
        return json_exception("Error creating directory")

    return json_success("Successfully created directory")

@app.route("/mktemp", methods=("GET", "POST"))
def do_mktemp():
    suffix = request.form.get("suffix", "")
    prefix = request.form.get("prefix", "tmp")
    dirpath = request.form.get("dirpath")

    try:
        fd, filepath = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dirpath)
    except Exception:
        return json_exception("Error creating temporary file")

    os.close(fd)

    return json_success("Successfully created temporary file", filepath=filepath)

@app.route("/mkdtemp", methods=("GET", "POST"))
def do_mkdtemp():
    suffix = request.form.get("suffix", "")
    prefix = request.form.get("prefix", "tmp")
    dirpath = request.form.get("dirpath")

    try:
        dirpath = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dirpath)
    except Exception:
        return json_exception("Error creating temporary directory")

    return json_success("Successfully created temporary directory", dirpath=dirpath)

@app.route("/retrieve", methods=["POST"])
def do_retrieve():
    if "filepath" not in request.form:
        return json_error(400, "No filepath has been provided")

    return send_file(request.form["filepath"])


@app.route("/extract", methods=["POST"])
def do_extract():
    if "dirpath" not in request.form:
        return json_error(400, "No dirpath has been provided")

    if "zipfile" not in request.files:
        return json_error(400, "No zip file has been provided")

    try:
        with ZipFile(request.files["zipfile"], "r") as archive:
            archive.extractall(request.form["dirpath"])
    except Exception:
        return json_exception("Error extracting zip file")

    return json_success("Successfully extracted zip file")


@app.route("/remove", methods=["POST"])
def do_remove():
    if "path" not in request.form:
        return json_error(400, "No path has been provided")

    try:
        if os.path.isdir(request.form["path"]):
            # Mark all files as readable so they can be deleted.
            for dirpath, _, filenames in os.walk(request.form["path"]):
                for filename in filenames:
                    os.chmod(os.path.join(dirpath, filename), stat.S_IWRITE)

            shutil.rmtree(request.form["path"])
            message = "Successfully deleted directory"
        elif os.path.isfile(request.form["path"]):
            os.chmod(request.form["path"], stat.S_IWRITE)
            os.remove(request.form["path"])
            message = "Successfully deleted file"
        else:
            return json_error(404, "Path provided does not exist")
    except Exception:
        return json_exception("Error removing file or directory")

    return json_success(message)
def parser1(log_file_path):
    try:
        print("go")
        def extract_text_between_patterns(file_path, start_pattern="All rights reserved.", end_pattern="Summary:"):
            with open(file_path, 'r', encoding='utf-16') as file:
                file_content = file.read()
            pattern = re.compile(f'{re.escape(start_pattern)}(.*?){re.escape(end_pattern)}', re.DOTALL)
            match = re.search(pattern, file_content)
            if match:
                result = match.group(1).strip()
                return result
            else:
                return ""
        def extract_string_before_found(log_text):
            pattern = re.compile(r"'(.*?)' found")
            match = re.search(pattern, log_text)
            if match:
                result = match.group(1)
                return result
            else:
                return ""
        result = extract_text_between_patterns(log_file_path)
        result = extract_string_before_found(result)
        print(result)
        if result:
            return result
        return ""
    except:
        return ""
@app.route("/scan", methods=["POST"])
def do_scan():
    def __kasper(file_path):
        import re
        db_path = r"C:\Users\Admin1\Desktop\t3sigs.vdb"
        log_path = tempfile.NamedTemporaryFile(delete=True).name
        cmd = f't3scan_w64 -vp {db_path} -l {log_path} {file_path}'
        subprocess.run(cmd, shell=True)
        return parser1(log_path)

    if not request.files['file']:
        return json_error(400, "No file has been provided")
    
    try:
        uploaded_file = request.files.get('file')
        file_path = tempfile.NamedTemporaryFile(delete=True).name 
        with open(file_path, 'wb') as destination_file:
            shutil.copyfileobj(uploaded_file, destination_file) 
        return json_success(__kasper(file_path))
    except Exception as e:
        return json_exception("", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", nargs="?", default="0.0.0.0")
    parser.add_argument("port", type=int, nargs="?", default=8006)
    args = parser.parse_args()
    app.run(host=args.host, port=args.port)
