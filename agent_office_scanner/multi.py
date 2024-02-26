import os
import queue
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import requests
import json
import shutil
import configparser
import datetime
import hashlib
from concurrent.futures import ThreadPoolExecutor
import mimetypes
from ast import literal_eval
import paramiko
import os
import time
import stat

current_time = datetime.datetime.now().strftime("_%Y_%m_%d_%H.%M%S")
global_priority_queue = queue.PriorityQueue()

def download_files_from_sftp(
    hostname, port, username, password, remote_folder, local_folder
):
    while True:
        try:
            transport = paramiko.Transport((hostname, port))
            transport.connect(username=username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            downloaded_files = set(os.listdir(local_folder))
            try:
                while True:
                    remote_files = sftp.listdir(remote_folder)
                    new_files = set(remote_files) - downloaded_files
                    for file_name in new_files:
                        remote_path = os.path.join(remote_folder, file_name)
                        local_path = os.path.join(local_folder, file_name)
                        try:
                            if stat.S_ISREG(sftp.stat(remote_path).st_mode):
                                sftp.get(remote_path, local_path)
                            downloaded_files.add(file_name)
                        except Exception as e:
                            print("Error: ", e)
                    time.sleep(10)
            except KeyboardInterrupt as e:
                print("Quitting...")
                break
            finally:
                sftp.close()
        except Exception as e:
            print(e)


class AgentScanner(FileSystemEventHandler):
    def __init__(self, path, worker_count, queue_priority, priority, config):
        super().__init__()
        self.path = path
        # self.file_queue = queue.Queue()
        self.worker_count = worker_count
        # self.processed_files = set()
        # self.lock = threading.Lock()
        self.last_event_time = time.time()
        self.executor = ThreadPoolExecutor(worker_count)
        self.queue_priority = queue_priority
        self.priority = priority
        self.folder_clean = os.path.join(self.path, "Clean")
        self.folder_malware = os.path.join(self.path, "Malware")
        self.config = config
        self.make_folders()

    def process_existing_files(self):
        for filename in os.listdir(self.path):
            file_path = os.path.join(self.path, filename)
            if os.path.isfile(file_path):
                # self.file_queue.put(file_path)
                self.queue_priority.put((self.priority, file_path))

    def on_modified(self, event):
        self.last_event_time = time.time()
        if event.is_directory:
            return
        file_path = event.src_path
        # self.file_queue.put(file_path)
        self.queue_priority.put((self.priority, file_path))

    def worker(self):
        while True:
            try:
                # file_path = self.file_queue.get(timeout=60)
                file_path = self.queue_priority.get(timeout=60)[1]
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    self.executor.submit(self.process_file, file_path)
            except queue.Empty:
                print(
                    "--------------------------Wating. No more files in the past 1 minute---------------------------"
                )
                continue
            except Exception:
                pass
            finally:
                try:
                    self.file_queue.task_done()
                except Exception:
                    pass

    def check_file_signature(self, file_path):
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                mime_type = mime_type.lower()

            office_formats = [
                "application/msword",
                "application/vnd.ms-excel",
                "application/vnd.ms-powerpoint",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "application/rtf",
                "application/pdf",
            ]

            if any(format in mime_type.lower() for format in office_formats):
                return 1
            else:
                return 0
        except:
            return 0

    def make_folders(self):

        for folder in [
            self.folder_clean,
            self.folder_malware,
            self.folder_clean + "//PDF",
            self.folder_malware + "//PDF",
        ]:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def generate_pdf_filename(self, file_path):
        folder_path, file_name = os.path.split(file_path)
        file_name_without_extension, file_extension = os.path.splitext(file_name)
        if (
            len(
                os.path.join(
                    self.folder_clean,
                    "PDF",
                    f"{file_name_without_extension}{current_time}.pdf",
                )
            )
            > 260
        ):
            file_name_without_extension = file_name_without_extension[
                : -(
                    len(
                        os.path.join(
                            self.folder_clean,
                            "PDF",
                            f"{file_name_without_extension}{current_time}.pdf",
                        )
                    )
                    - 290
                )
            ]
        new_pdf_filename = f"{file_name_without_extension}{current_time}.pdf"
        new_pdf_file_path = os.path.join(self.folder_clean, "PDF", new_pdf_filename)
        return new_pdf_file_path

    def generate_pdf_filename_Mal(self, file_path):
        folder_path, file_name = os.path.split(file_path)
        file_name_without_extension, file_extension = os.path.splitext(file_name)
        if (
            len(
                os.path.join(
                    self.folder_malware,
                    "PDF",
                    f"MAL_{file_name_without_extension}{current_time}.pdf",
                )
            )
            > 260
        ):
            file_name_without_extension = file_name_without_extension[
                : -(
                    len(
                        os.path.join(
                            self.folder_malware,
                            "PDF",
                            f"MAL_{file_name_without_extension}{current_time}.pdf",
                        )
                    )
                    - 290
                )
            ]
        new_pdf_filename = f"MAL_{file_name_without_extension}{current_time}.pdf"
        new_pdf_file_path = os.path.join(self.folder_malware, "PDF", new_pdf_filename)
        return new_pdf_file_path

    def calculate_file_hash(self, file_path):
        hasher = hashlib.sha256()
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(65536)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()

    def process_file(self, file_path):
        try:
            if os.path.getsize(file_path) / (1024 * 1024) <= self.config.getint(
                "Settings", "Max_file_size"
            ):
                print("(+) Processing file ", file_path)
                with open(file_path, "rb") as file:
                    if self.config.getint("ai_detect","on_demand"):
                        headers = {"Authorization": f'Bearer {self.config.get("ai_detect","token")}'}
                        res = json.loads(requests.post(self.config.get("ai_detect","URL_ai_detect"),  files={"file": file}, verify=False, headers=headers).text)
                    else:
                        headers = {"Authorization": f'Bearer {self.config.get("Settings","token")}'}
                        res = json.loads(
                            requests.post(
                                self.config.get("Settings", "URL_avscan"),
                                files={"file": file, "mode": (None, 0)},
                                data={
                                    "vt_demand": self.config.get("virustotal", "key")
                                    if self.config.get("virustotal", "on_demand")
                                    else ""
                                },
                                headers=headers,
                                verify=False
                            ).text
                        )
                    if self.check_file_signature(file_path):
                        if res[0]["positives"] == 0:
                            converted_file_path = self.generate_pdf_filename(file_path)
                            # pythoncom.CoInitialize()
                            # convert(file_path, converted_file_path)
                            url = self.config.get("Settings", "URL_off2pdf")
                            # with open(file_path, 'rb') as docx_file:
                            #     # files = {
                            #     #     'document': (file_path, docx_file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                            #     # }
                            #     files = {
                            #         'file': (file_path, docx_file)
                            #     }
                            #     response = requests.post(url, files=files)
                            with open(file_path, "rb") as docx_file:
                                files = {"file": (file_path, docx_file)}
                                headers = {"Authorization": f'Bearer {self.config.get("Settings","token")}'}
                                # data = {'convert-to': 'pdf'}
                                response = requests.post(
                                    url, files=files, verify=False, headers= headers
                                )  # , data=data)
                            if (
                                response.status_code == 200
                                and response.headers["Content-Type"]
                                == "application/pdf"
                            ):
                                with open(converted_file_path, "wb") as pdf_file:
                                    pdf_file.write(response.content)
                                print(
                                    f"PDF file has been saved to: {converted_file_path}"
                                )
                            else:
                                print(
                                    "Conversion failed. Status code:",
                                    response.status_code,
                                )
                                print("Response:", response.text)
                        else:
                            with open(
                                rf"{self.folder_malware}\aResult.txt", "a"
                            ) as result_file:
                                result_file.write(f"File: {file_path}, Result: {res}\n")
                            converted_file_path = self.generate_pdf_filename_Mal(
                                file_path
                            )
                            with open(file_path, "rb") as docx_file:
                                response = requests.post(
                                    self.config.get("Settings", "URL_off2pdf"),
                                    files={"file": (file_path, docx_file)},
                                    data={"convert-to": "pdf"},
                                )
                            if (
                                response.status_code == 200
                                and response.headers["Content-Type"]
                                == "application/pdf"
                            ):
                                with open(converted_file_path, "wb") as pdf_file:
                                    pdf_file.write(response.content)
                                print(
                                    f"PDF file has been saved to: {converted_file_path}"
                                )
                            else:
                                print(
                                    "Conversion failed. Status code:",
                                    response.status_code,
                                )
                                print("Response:", response.text)
                destination_folder = (
                    self.folder_malware if res[0]["positives"] else self.folder_clean
                )
                file_name, file_extension = os.path.splitext(
                    os.path.basename(file_path)
                )
                if (
                    len(
                        os.path.join(
                            destination_folder,
                            f'{file_name}{current_time}{file_extension if file_extension else ""}',
                        )
                    )
                    > 260
                ):
                    file_name = file_name[
                        : -(
                            len(
                                os.path.join(
                                    destination_folder,
                                    f'{file_name}{current_time}{file_extension if file_extension else ""}',
                                )
                            )
                            - 290
                        )
                    ]
                shutil.move(
                    file_path,
                    os.path.join(
                        destination_folder,
                        f'{file_name}{current_time}{file_extension if file_extension else ""}',
                    ),
                )
        except Exception as e:
            print(f"Error {file_path}: {e}")
            self.queue_priority.put((self.priority, file_path))

def main(config_path: str):
    worker_count = 3
    threads = []
    config = configparser.ConfigParser()
    config.read(config_path)
    if not config.getint("sftp", "on_demand"):
        folder_priorities = literal_eval(config.get("Settings", "Folder_path"))
    else:
        folder_priorities = []
        remote_folder = literal_eval(config.get("sftp", "sftp_folder_path"))
        root_local_folder = config.get("sftp", "root_local_folder")
        for folder_path, priority in remote_folder:
            des_folder = os.path.join(root_local_folder, os.path.basename(folder_path))
            if not os.path.exists(des_folder):
                os.makedirs(des_folder)
            sftp_thread = threading.Thread(
                target=download_files_from_sftp,
                args=(
                    config.get("sftp", "hostname"),
                    config.getint("sftp", "port"),
                    config.get("sftp", "username"),
                    config.get("sftp", "password"),
                    folder_path,
                    des_folder,
                ),
            )
            threads.append(sftp_thread)
            sftp_thread.start()
            folder_priorities.append((des_folder, priority))

    observer = Observer()
    handlers = []

    for folder_path, priority in folder_priorities:
        event_handler = AgentScanner(
            folder_path, worker_count, global_priority_queue, priority, config
        )
        handlers.append(event_handler)
        event_handler.process_existing_files()
        observer.schedule(event_handler, folder_path, recursive=False)

    for handler in handlers:
        thread1 = threading.Thread(target=handler.worker)
        thread1.start()
        threads.append(thread1)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    for handler in handlers:
        handler.queue_priority.join()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main("config.ini")