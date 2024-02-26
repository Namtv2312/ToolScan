import os
import tarfile
import docker
import re
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
        return 0
    
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

local_file_path = "/home/troot/ei.e"
# print(av_avira(get_id_by_name("saferwall/goavira:latest"), local_file_path))
# print(av_windefender(get_id_by_name("saferwall/gowindefender:latest"), local_file_path))
print(av_comodo(get_id_by_name("saferwall/gocomodo:latest"), local_file_path))
