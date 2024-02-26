import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import simpledialog, filedialog
from tkinter.ttk import Combobox, Progressbar
from multi import AgentScanner
import multi
import os
import threading
import re

import configparser

config = configparser.ConfigParser()


class FileChooserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Office Scanner")

        self.priority_var = tk.IntVar()
        self.priority_var.set(0)

        self.automate_var = tk.IntVar()
        self.automate_var.set(0)

        self.config_path = tk.StringVar()
        self.config_path.set(f"{os.path.dirname(os.path.abspath(__file__))}\config.ini")
        self.selected_paths = []

        self.scan_statuses = {}

        self.lb_file_cf = tk.Label(
            root,
            text=f"Đường dẫn file config: (Default is: {os.path.dirname(os.path.abspath(__file__))}\config.ini)",
        )
        self.lb_file_cf.pack(pady=10)

        self.btn_choose_cf = tk.Button(
            root, text="Chọn config", command=self.cmd_choose_cf
        )
        self.btn_choose_cf.pack(pady=10)

        self.file_label = tk.Label(root, text="Chọn file muốn quét:")
        self.file_label.pack(pady=10)

        self.choose_file_button = tk.Button(
            root, text="Chọn file", command=self.choose_file
        )
        self.choose_file_button.pack(pady=10)

        self.folder_label = tk.Label(root, text="Danh sách folder:")
        self.folder_label.pack(pady=10)

        self.choose_folder_button = tk.Button(
            root, text="Chọn folder", command=self.choose_folder
        )
        self.choose_folder_button.pack(pady=10)

        self.priority_checkbox = tk.Checkbutton(
            root, text="Priority", variable=self.priority_var
        )
        self.priority_checkbox.pack(pady=10)

        self.automate_checkbox = tk.Checkbutton(
            root, text="Automate Scan", variable=self.automate_var
        )
        self.automate_checkbox.pack(pady=10)

        self.path_combobox = Combobox(
            root, values=self.selected_paths, state="readonly"
        )
        self.path_combobox.pack(pady=10)

        self.scan_button = tk.Button(root, text="SCAN", command=self.scan_files)
        self.scan_button.pack(pady=10)

        self.drop_text = tk.Text(root, wrap="word", height=5, width=40)
        self.drop_text.pack(pady=20)

        self.drop_text.drop_target_register(DND_FILES)
        self.drop_text.dnd_bind("<<Drop>>", self.handle_drop)

        self.progress_bars = []

        self.bottom_progress = Progressbar(
            root, orient="horizontal", length=600, mode="determinate"
        )
        self.bottom_progress.pack(pady=10)

    def cmd_choose_cf(self):
        file_path = filedialog.askopenfilename()
        self.lb_file_cf.config(text=f"Config path: {file_path}")
        self.config_path.set(file_path)

    def choose_file(self):
        file_path = filedialog.askopenfilename()
        self.file_label.config(text=f"Đường dẫn file: {file_path}")
        self.update_selected_paths(file_path)

    def choose_folder(self):
        folder_paths = self.askdirectory_multiple()
        self.folder_label.config(text="Danh sách folder:")
        for folder_path in folder_paths:
            self.folder_label.config(
                text=self.folder_label.cget("text") + f"\n{folder_path}"
            )
            self.update_selected_paths(folder_path)

    def askdirectory_multiple(self):
        root = tk.Tk()
        root.withdraw()

        folder_paths = simpledialog.askstring(
            "Chọn folder", "Nhập đường dẫn các thư mục cách nhau bằng dấu phẩy:"
        )

        root.destroy()

        if folder_paths:
            folder_paths = folder_paths.split(",")
            folder_paths = [folder.strip() for folder in folder_paths]

        return folder_paths

    def handle_drop(self, event):
        file_paths = re.findall(r"\{(.*?)\}", event.data)
        for file_path in file_paths:
            self.drop_text.insert(tk.END, f"{file_path}\n")
            self.update_selected_paths(file_path)

    def update_selected_paths(self, path):
        self.selected_paths.append(path)
        self.path_combobox["values"] = self.selected_paths
        self.path_combobox.current(len(self.selected_paths) - 1)

    def scan_files(self):
        threads = []
        if self.automate_var.get():
            auto_t = threading.Thread(target=multi.main, args=(self.config_path.get(),))
            auto_t.start()
            threads.append(auto_t)
        else:
            thread = threading.Thread(target=self.scan_selected_files)
            thread.start()
            threads.append(thread)

    def scan_selected_files(self):
        config.read(self.config_path.get())
        total_files = len(self.selected_paths)
        progress_step = 100 / total_files
        for idx, path in enumerate(self.selected_paths):
            self.progress_bars.append(
                Progressbar(
                    self.root, orient="horizontal", length=200, mode="indeterminate"
                )
            )
            self.progress_bars[-1].pack()
            path_ = os.path.dirname(path) if os.path.isfile(path) else path
            log = AgentScanner(
                path_,
                3,
                multi.global_priority_queue,
                (0 if self.priority_var.get() else 10),
                config,
            ).process_file(path)
            self.drop_text.insert(tk.END, f"Path: {path}\n{log}\n\n")
            self.drop_text.see(tk.END)
            self.scan_statuses[path] = True
            self.progress_bars[-1].stop()
            self.progress_bars[-1].pack_forget()
            self.bottom_progress["value"] += progress_step
            self.root.update_idletasks()
        self.bottom_progress["value"] = 100


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FileChooserApp(root)
    root.mainloop()
