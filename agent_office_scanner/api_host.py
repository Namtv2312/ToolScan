import docker
from flask import Flask, request, Response
import requests
import libvirt
import timeit
import socket
import time
client = docker.from_env()
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
IMAGES_OFFICE = 'libreofficedocker/libreoffice-unoserver:3.10-26e21e0'
URL_CONVERTPDF = "http://192.168.122.139:5000/upload"

executor = ThreadPoolExecutor(max_workers=10)  # 

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
            print("Connected")
            break
        except socket.timeout:
            print("Timout")
        except socket.error:
            print("Task is not ready yet")
            time.sleep(1)

        if timeit.default_timer() - start > 200:
            print("error")

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

def run_container():
    try:

        existing_container = client.containers.get(get_id_by_name(IMAGES_OFFICE))
        existing_container.stop()
        existing_container.remove()
    except Exception:
        pass
    #CREATE NEW
    client.containers.run(IMAGES_OFFICE, detach=True, name='my_containeroff2pdf', ports={'2004/tcp': 9997})


def process_file_on_external_server(file):
    try:
        vm_name = "ubuntu20.04"
        if get_vm_status(vm_name) == libvirt.VIR_DOMAIN_SHUTOFF:
            start_vm_from_snapshot(vm_name, "convert_PDF")
        wait_available("192.168.122.139", 5000)
        
        print("(+) Receive File, processing")
        response = requests.post(URL_CONVERTPDF, files={'file': file})
        
        if response.status_code == 200:
            return response.content, 'application/pdf'
        else:
            return None, 'Failed to generate PDF on the external server', 500
    except Exception as e:
        return None, 'Failed to generate PDF on the external server', e

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'

        if file:
            future = executor.submit(process_file_on_external_server, file)
            pdf_content, content_type = future.result()

            if pdf_content:
                return Response(response=pdf_content, content_type=content_type)
            else:
                return 'Failed to generate PDF on the external server', 500
        else:
            return 'Invalid file format'
    except Exception as e:
        return 'Failed to generate PDF on the external server', e

if __name__ == '__main__':
    # run_container()
    app.run(debug=True, host='0.0.0.0', port= 9998)