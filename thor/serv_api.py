from functools import wraps
import ssl
from flask import Flask, request, jsonify, g
from gevent.pywsgi import WSGIServer
import subprocess
import os
import concurrent.futures
import json
import requests
import zipfile
import tempfile
import argparse
import tarfile
import docker
import re
app = Flask(__name__)
URL_CLAMAV = "http://localhost:9000"
import libvirt
import timeit
import socket
import time
from logging import log
import sqlite3
import hashlib
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=os.cpu_count()+4)
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

def get_vm_status(vm_name):
    conn = libvirt.open('qemu:///system')  # Connect to the local QEMU/KVM hypervisor
    if conn is None:
        return "Failed to open connection to qemu:///system"
    
    try:
        vm = conn.lookupByName(vm_name)
        state, _ = vm.state()  # Get the state of the virtual machine
        return state
    except libvirt.libvirtError as e:
        return f"Error: {e}"
    finally:
        conn.close()
def power_on_vm(vm_name):
    conn = libvirt.open('qemu:///system')  # Connect to the local QEMU/KVM hypervisor
    if conn is None:
        return "Failed to open connection to qemu:///system"
    
    try:
        vm = conn.lookupByName(vm_name)
        vm.create()  # Power on the virtual machine
        return f"Powering on {vm_name}..."
    except libvirt.libvirtError as e:
        return f"Error: {e}"
    finally:
        conn.close()
def start_vm_from_snapshot(vm_name, snapshot_name):
    conn = libvirt.open('qemu:///system') 

    try:
        domain = conn.lookupByName(vm_name)
        snapshots = domain.listAllSnapshots()
        target_snapshot = None
        for snapshot in snapshots:
            if snapshot.getName() == snapshot_name:
                target_snapshot = snapshot
                break

        if target_snapshot is None:
            print("Snapshot not found.")
            return
        target_snapshot._dom.revertToSnapshot(target_snapshot, flags=0)
        print("Virtual machine '{}' started from snapshot '{}'.".format(vm_name, snapshot_name))
    except libvirt.libvirtError as e:
        print("Error: {}".format(e))
    finally:
        conn.close()
def wait_available(ipaddr, port):
    """Wait until the Virtual Machine is available for usage."""
    start = timeit.default_timer()
    while(1):
        try:
            socket.create_connection((ipaddr, port), 1).close()
            break
        except socket.timeout:
            log.debug("Timout")
        except socket.error:
            log.debug("Task is not ready yet")
            time.sleep(1)

        if timeit.default_timer() - start > 200:
            log.debug("error")
def post(method, *args, **kwargs):
    """Simple wrapper around requests.post()."""
    r = 0
    url = f"http://192.168.122.250:{8005}{method}"
    try:
        r = requests.post(url, *args, **kwargs)
    except Exception as e:
        print("error Connection",e)
    return r
def thor_av (amas_mod, file_path):
    try:
        output = subprocess.check_output(
                    ["python3", amas_mod, "-j", "-s", file_path],
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    cwd=os.path.dirname(amas_mod)
                )
    except Exception as e:
            print("errr", e)
    return output
def docker_kaspersky(file_path):
    try:
        import re
        resultt2 = subprocess.check_output(
            ["docker", "run", "-it", "--rm", "-v", f"{file_path}:/data:ro", "--network", "none", "tabledevil/kaspersky", "scan"],
            stderr=subprocess.STDOUT,
        )
        detect_name_match = re.search(r'DetectName=(.*?)\n', resultt2.decode())
        if detect_name_match:
            return detect_name_match.group(1)
        else:
             return ""
    except Exception as e:
        print("errr", e)
    return ""
def realVM_Eset(file_path):
    vm_name = "win8-AV"
    if get_vm_status(vm_name) == libvirt.VIR_DOMAIN_SHUTOFF:
        start_vm_from_snapshot(vm_name, "eset_latest")
    wait_available("192.168.122.250", 8005)
    return post("/scan", files={"file":open(file_path, "rb")}).json()["message"]

def realVM_Avast(file_path):
    vm_name = "win8-AV-VM1"
    if get_vm_status(vm_name) == libvirt.VIR_DOMAIN_SHUTOFF:
        start_vm_from_snapshot(vm_name, "agent_avast")
    wait_available("192.168.122.38", 8005)
    return requests.post(f"http://192.168.122.38:{8005}{'/scan'}", files={'file':open(file_path, 'rb')}).json()["message"]

client = docker.from_env()
def copy_to(src, dst):
    name, dst = dst.split(':')
    container = client.containers.get(name)

    os.chdir(os.path.dirname(src))
    srcname = os.path.basename(src)
    tar = tarfile.open(src + '.tar', mode='w')
    try:
        tar.add(srcname)
    finally:
        tar.close()

    data = open(src + '.tar', 'rb').read()
    container.put_archive(os.path.dirname(dst), data)

def av_avira(container_id,local_file_path):
    try:
        container_file_path = "/saferwall/"
        copy_to(local_file_path, f"{container_id}:{container_file_path}")

        container = client.containers.get(container_id)

        scan_command = f"/opt/avira/scancl --nombr --nostats --quarantine=/tmp {container_file_path + local_file_path.split('/')[-1]}"
        exec_response = container.exec_run(scan_command, stdout=True, stderr=True, tty=True)
        client.close()
        alert_pattern = r'ALERT: \[([^\]]+)\] (.+?)(?=\n|$)'
        # print(exec_response.output.decode())
        alert_matches = re.findall(alert_pattern, exec_response.output.decode())
        if alert_matches:
            for match in alert_matches:
                alert_type, file_path = match
            return alert_type
        else:
            return ""
    except: 
        return 0
    
def av_windefender(container_id,local_file_path):
    #"C:\Program Files\Windows Defender\MpCmdRun.exe"  -Scan -ScanType 3 -File "C:\Users\Admin\AppData\Local\Temp\MicrosoftEdgeDownloads\e146bf98-4b94-4230-8149-476d28cf3c39\2629b7c8c2e9b2357904b4a29c8d211bee5c45f0fa532941c41385e7fb58bfcf\2629b7c8c2e9b2357904b4a29c8d211bee5c45f0fa532941c41385e7fb58bfcf.pdf" -DisableRemediation -Trace -Level 0x10

    try:
        container_file_path = "/saferwall/"
        copy_to(local_file_path, f"{container_id}:{container_file_path}")
        container = client.containers.get(container_id)
        # container.exec_run("cd /opt/windows-defender")
        # print(container.exec_run("pwd", stdout=True, stderr=True, tty=True).output.decode())
        scan_command = f"wine mploader.exe  -f {container_file_path + local_file_path.split('/')[-1]} -u"
        exec_response = container.exec_run(scan_command, stdout=True, stderr=True, tty=True,workdir="/opt/windows-defender")
        # print(exec_response.output.decode())
        client.close()
        detection_pattern = r'Threat\s([^\n]+)\sidentified\.'
        detection_matches = re.findall(detection_pattern, exec_response.output.decode())
        if detection_matches:
            return detection_matches[0]
        else:
            return ""
    except:
        return ""
    
def av_comodo(container_id,local_file_path):
    try:
        container_file_path = "/saferwall/"
        copy_to(local_file_path, f"{container_id}:{container_file_path}")

        container = client.containers.get(container_id)
        scan_command = f"/opt/COMODO/cmdscan -v -s {container_file_path + local_file_path.split('/')[-1]}"
        exec_response = container.exec_run(scan_command, stdout=True, stderr=True, tty=True)
        # print(exec_response.output.decode())
        client.close()
        pattern = r'.*Found Virus, Malware Name is (.+?)\r\n.*'
        match = re.match(pattern, exec_response.output.decode(), re.DOTALL)

        if match:
            detection = match.group(1)
            return detection
        else:
            return ""
    except: 
        return ""
def get_id_by_name(name:str):
    containers = client.containers.list()

    # Loop through the containers and find the one with the specified name
    container_id =''
    for container in containers:
        if container.image.tags[0] == name:
            # Get container ID
            container_id = container.id
            break
    return container_id

def calculate_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(65536)  # 64k chunks
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def check_file_in_database(file_hash):
    conn = sqlite3.connect(f'{os.path.dirname(os.path.abspath(__file__))}/AVScan.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM AVScan WHERE hash=?", (file_hash,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[2]

def update_to_db(file_hash, data):
    conn = sqlite3.connect(f'{os.path.dirname(os.path.abspath(__file__))}/AVScan.db')

    # Tạo một đối tượng cursor để thao tác với cơ sở dữ liệu
    cursor = conn.cursor()

    # Tạo bảng AVScan nếu chưa tồn tại
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AVScan (
            hash TEXT PRIMARY KEY NOT NULL,
            positives INTEGER NOT NULL,
            scans TEXT NOT NULL,
            total INTEGER NOT NULL
        )
    ''')
    # Chuyển dữ liệu JSON thành chuỗi JSON
    json_data = json.dumps(data)

    # Thêm dữ liệu vào bảng
    cursor.execute("INSERT OR REPLACE INTO AVScan (hash, positives, scans, total) VALUES (?, ?, ?, ?)",
                (file_hash, data['positives'], json_data, data['total']))

    conn.commit()
    conn.close()

@app.route('/')
def hello_world():
    return jsonify("hello world")
method_scan = '/scan'  
@app.route('/scan', methods=['POST'])
@app.route('/rescan', methods=['POST'])
@require_api_token
def scan_file():
    global method_scan 
    global vt_demand
    try:
        vt_demand = request.form["vt_demand"]
    except:
        vt_demand = ''
    method_scan = request.path
    uploaded_file = request.files['file']
    file_name = uploaded_file.filename
    mode = request.form['mode']
    def _process_file(file_path):
            temp_dir = tempfile.mkdtemp()
            res_json = []
            if mode =="1":
                if zipfile.is_zipfile(file_path):
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                            extracted_file_paths = [os.path.join(
                                temp_dir, file) for file in zip_ref.namelist()]
                        future_to_file = {executor.submit(scan_one_file, file_path): file_path for file_path in extracted_file_paths}
                        for future in concurrent.futures.as_completed(future_to_file):
                            file_path = future_to_file[future]
                            try:
                                scan_result = future.result()
                                scan_result["file"] = os.path.basename(file_path)
                                res_json.append(scan_result)
                            except Exception as exc:
                                print(f"Error processing file {file_path}: {exc}")
                        return res_json
            scan_result = scan_one_file(file_path)
            scan_result["file"] = file_name
            res_json.append(scan_result)
            return res_json
    if uploaded_file:
        file_path = tempfile.NamedTemporaryFile(delete=True).name # You can choose any temporary path
        # print(file_path)
        uploaded_file.save(file_path)
        future = executor.submit(_process_file, file_path)
        result = future.result()
        return jsonify(result)
    
    

def scan_one_file(file_path):
    output = {}
    # amas_mod = os.path.join("/opt/CAPEv2", "data/thor-av-multiscanner/thor/thor.py")
    # if /scan
    # Check file has been exist on database
    hash_file = calculate_file_hash(file_path)
    ### VT query HASH ##
    try:
        res = vt_lookup(hash_file)
        if res:
            update_to_db(hash_file, res)
            return res
    except:
        res = ''
    global method_scan 
    if method_scan == '/scan':
        try:
            res = check_file_in_database(hash_file)
        except:
            res = ''
        if res:
            return json.loads(res)
    amas_mod =  f"{os.path.dirname(os.path.abspath(__file__))}/thor.py"
    future_subprocess = executor.submit(thor_av, amas_mod, file_path)
    future_docker_scan = executor.submit(docker_kaspersky, file_path)
    future_windefend = executor.submit(av_windefender,get_id_by_name("saferwall/gowindefender:latest"), file_path)
    future_avira = executor.submit(av_avira,get_id_by_name("saferwall/goavira:latest"), file_path)
    future_eset = executor.submit(realVM_Eset, file_path)
    future_avast = executor.submit(realVM_Avast, file_path)
    # Wait for both tasks to complete
    concurrent.futures.wait([future_subprocess, future_docker_scan, future_windefend,future_eset,future_avast])
    output = future_subprocess.result()
    try:
        resultt2 = future_docker_scan.result(timeout= 90)
    except:
        resultt2 = ''
    try:
        win_res = future_windefend.result(timeout= 90)
    except:
        win_res = ''
    try:
        avira_res = future_avira.result(timeout= 90)
    except:
        avira_res = ''
    try:
        eset_res = future_eset.result(timeout= 90)
    except:
        eset_res = ''
    try:
        avast_res = future_avast.result(timeout= 90)
    except:
        avast_res = ''
    try:
        ikarus_res = requests.post(f"http://192.168.122.38:{8006}{'/scan'}", files={'file':open(file_path, 'rb')}, timeout= 90).json()["message"]
    except:
        ikarus_res = ""
    output = json.loads(output.replace("'", "\"").strip().replace("False","false").replace("True","true"))
    try:
        res_clamav =json.loads(requests.post(f"{URL_CLAMAV}/scan", files={"file": open(file_path, "rb")}, timeout= 15).text)["Description"]
    except:
        res_clamav = ""
    try:
        headers = {"Authorization": f'Bearer {g.api_token}'}
        res_amasAI  = json.loads(requests.post("localhost:8050/scan",  files={"file": open(file_path, "rb")}, verify=False, headers=headers, timeout=90).text)
    except: 
        res_amasAI = ""
    clam_av= {"infected": (1 if res_clamav else 0), "result": res_clamav}
    kes_av ={"infected": (1 if resultt2 else 0), "result": resultt2}
    windf_av = {"infected": (1 if win_res else 0), "result": win_res}
    avira_av = {"infected": (1 if avira_res else 0), "result": avira_res}
    eset_av = {"infected": (1 if eset_res else 0), "result": eset_res}
    avast_av = {"infected": (1 if avast_res else 0), "result": avast_res}
    ikarus_av = {"infected": (1 if ikarus_res else 0), "result": ikarus_res}
    amas_AI = {"infected": (1 if res_amasAI else 0), "result": res_amasAI}
    output["detections"]["Kaspersky"] = kes_av
    output["detections"]["ClamAV"] = clam_av
    output["detections"]["Windows Defender"] = windf_av
    output["detections"]["Avira"] = avira_av
    output["detections"]["Eset"] = eset_av
    output["detections"]["Avast"] = avast_av
    output["detections"]["Ikarus"] = ikarus_av
    output["detections"]["AiTool"] = amas_AI

    amas_av = {
    "positives": sum(1 for antivirus in output['detections'].values() if antivirus.get('infected') == True),
    "total": len(output.get("detections").keys())
    }
    output = output.get("detections")
    transformed_data = {}
    for program, info in output.items():
        transformed_data[program] = {'infected': "True" if info['infected'] else "False", 'result': info['result'] if info["result"] else "Undetected"}
    amas_av["scans"] = transformed_data
    update_to_db(hash_file, amas_av)
    return amas_av

def vt_lookup(hash_file):
    global vt_demand
    headers = {"X-Apikey": vt_demand}
    VIRUSTOTAL_URL_URL = "https://www.virustotal.com/api/v3/files/{id}"
    url = VIRUSTOTAL_URL_URL.format(id=hash_file)
    r = requests.get(url, headers=headers, verify=True, timeout=60)
    if not r.ok:
        return {}
    vt_response = r.json()
    engines = vt_response.get("data", {}).get("attributes", {}).get("last_analysis_results", {})
    if not engines:
        return {}
    virustotal = {
        "names": vt_response.get("data", {}).get("attributes", {}).get("names"),
        "scan_id": vt_response.get("data", {}).get("id"),
        "md5": vt_response.get("data", {}).get("attributes", {}).get("md5"),
        "sha1": vt_response.get("data", {}).get("attributes", {}).get("sha1"),
        "sha256": vt_response.get("data", {}).get("attributes", {}).get("sha256"),
        "tlsh": vt_response.get("data", {}).get("attributes", {}).get("tlsh"),
        "positives": vt_response.get("data", {}).get("attributes", {}).get("last_analysis_stats", {}).get("malicious"),
        "total": len(engines.keys()),
        "permalink": vt_response.get("data", {}).get("links", {}).get("self"),
    }
    virustotal["scans"] = {engine.replace(".", "_"): block for engine, block in engines.items()}
    res = {vendor: {'infected': "True" if info['category'] == 'malicious' else "False", 'result': info['result']} for vendor, info in virustotal["scans"].items()}
    total = {"positives": virustotal["positives"], "total":virustotal["total"], "scans":res}
    return total

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=8023)
    parser = argparse.ArgumentParser(description='Run the Flask application with custom port')
    parser.add_argument('port', nargs='?', type=int, default=8025, help='Port number (default is 5000)')
    args = parser.parse_args()
    port = args.port
    # openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
    key_path, cert_path = [os.path.join(os.path.dirname(__file__), f) for f in ['key.pem', 'cert.pem']]
    https_server = WSGIServer(('', port), app, keyfile=key_path, certfile=cert_path, 
                             ssl_version=ssl.PROTOCOL_TLSv1_2)
    https_server.serve_forever()
