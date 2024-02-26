import os
import time
import concurrent.futures
import requests
import json
import shutil
import configparser
from threading import Lock
import datetime
# from docx2pdf import convert
# import pythoncom
config = configparser.ConfigParser()
config.read('config.ini')

folder_path = config.get('Settings', 'Folder_path')
folder_clean = os.path.join(folder_path, "Clean")
folder_malware = os.path.join(folder_path, "Malware")
processed_files = []
processed_files_lock = Lock()
current_time = datetime.datetime.now().strftime("_%Y_%m_%d_%H.%M%S")
def make_folders():

    for folder in [folder_clean, folder_malware, folder_clean + "//PDF", folder_malware + "//PDF"]:
        if not os.path.exists(folder):
            os.makedirs(folder)

def generate_pdf_filename(file_path):

    folder_path, file_name = os.path.split(file_path)
    file_name_without_extension, file_extension = os.path.splitext(file_name)
    new_pdf_filename = f"{file_name_without_extension}{current_time}.pdf"
    new_pdf_file_path = os.path.join(folder_clean, "PDF", new_pdf_filename)
    return new_pdf_file_path

def generate_pdf_filename_Mal(file_path):

    folder_path, file_name = os.path.split(file_path)
    file_name_without_extension, file_extension = os.path.splitext(file_name)
    new_pdf_filename = f"MAL_{file_name_without_extension}{current_time}.pdf"
    new_pdf_file_path = os.path.join(folder_malware, "PDF", new_pdf_filename)
    return new_pdf_file_path

def process_file(file_path):
    try:
        if os.path.getsize(file_path) / (1024 * 1024) <= config.getint('Settings', 'Max_file_size'):
            print("(+) Processing file ", file_path)
            with open(file_path, 'rb') as file:
                res = json.loads(requests.post(config.get('Settings', 'URL_avscan'), files={"file": file, "mode":(None,0)}).text)
                if res[0]['positives'] == 0:
                    destination_folder = folder_clean
                    converted_file_path = generate_pdf_filename(file_path)
                    # pythoncom.CoInitialize()
                    # convert(file_path, converted_file_path)
                    url = config.get('Settings', 'URL_off2pdf')
                    # with open(file_path, 'rb') as docx_file:
                    #     # files = {
                    #     #     'document': (file_path, docx_file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    #     # }
                    #     files = {
                    #         'file': (file_path, docx_file)
                    #     }
                    #     response = requests.post(url, files=files)
                    with open(file_path, 'rb') as docx_file:
                        files = {
                            'file': (file_path, docx_file)
                        }
                        # data = {'convert-to': 'pdf'}
                        response = requests.post(url, files=files)#, data=data)
                    if response.status_code == 200 and response.headers['Content-Type'] == 'application/pdf':
                        with open(converted_file_path, 'wb') as pdf_file:
                            pdf_file.write(response.content)
                        print(f'PDF file has been saved to: {converted_file_path}')
                    else:
                        print('Conversion failed. Status code:', response.status_code)
                        print('Response:', response.text)
                else:
                    with open(rf'{folder_malware}\aResult.txt', 'a') as result_file:
                        result_file.write(f"File: {file_path}, Result: {res}\n")
                    destination_folder = folder_malware
                    converted_file_path = generate_pdf_filename_Mal(file_path)
                    with open(file_path, 'rb') as docx_file:
                        response = requests.post(config.get('Settings', 'URL_off2pdf'), files={'file':(file_path, docx_file)}, data={'convert-to': 'pdf'})
                    if response.status_code == 200 and response.headers['Content-Type'] == 'application/pdf':
                        with open(converted_file_path, 'wb') as pdf_file:
                            pdf_file.write(response.content)
                        print(f'PDF file has been saved to: {converted_file_path}')
                    else:
                        print('Conversion failed. Status code:', response.status_code)
                        print('Response:', response.text)
                
            with processed_files_lock:
                processed_files.append(file_path)
            file_name, file_extension = os.path.splitext(os.path.basename(file_path))
            shutil.move(file_path, os.path.join(destination_folder, f'{file_name}{current_time}{file_extension if file_extension else ""}'))
    except Exception as e:
        print(f"Error {file_path}: {e}")

def process_all_files(folder_path):
    files_and_folders = os.listdir(folder_path)
    files = [file_name for file_name in files_and_folders if os.path.isfile(os.path.join(folder_path, file_name))]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_file, [os.path.join(folder_path, file) for file in files])

def track_folder(folder_path):
    make_folders()
    process_all_files(folder_path)
    
    while True:
        time.sleep(2)
        current_files = [file_name for file_name in  os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file_name))]

        new_files = list(set(current_files) - set(processed_files))
        
        if not new_files:
            print("(+) -----------------------------------Waiting file --------------------------------------------")

        with concurrent.futures.ThreadPoolExecutor() as executor:
           executor.map(process_file, [os.path.join(folder_path, file) for file in new_files])
            
        with processed_files_lock:
            processed_files.extend(new_files)

if __name__ == '__main__':
    track_folder(folder_path)