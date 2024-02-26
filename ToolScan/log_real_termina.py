import tkinter as tk
from subprocess import Popen, PIPE, STDOUT
import threading
import time

def endless_print():
    count = 1
    while True:
        print(f"Message {count}")
        count += 1
        time.sleep(1)

class RealTimeLogViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("Real-Time Log Viewer")

        self.text_area = tk.Text(self.master, wrap="word", height=20, width=50)
        self.text_area.pack(padx=10, pady=10)

        self.start_button = tk.Button(self.master, text="Start Logging", command=self.start_logging)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.master, text="Stop Logging", command=self.stop_logging)
        self.stop_button.pack(pady=10)

        self.process = None
        self.is_logging = False

    def start_logging(self):
        if not self.is_logging:
            self.is_logging = True
            self.process = Popen(['python', '-u', '-c', 'from log_real_terminal import endless_print; endless_print()'], stdout=PIPE, stderr=STDOUT, text=True, bufsize=1, universal_newlines=True)
            self.log_thread = threading.Thread(target=self.update_text_area)
            self.log_thread.start()

    def stop_logging(self):
        if self.is_logging:
            self.is_logging = False
            self.process.terminate()

    def update_text_area(self):
        while self.is_logging:
            line = self.process.stdout.readline()
            if not line:
                break
            self.text_area.insert(tk.END, line)
            self.text_area.see(tk.END)  # Scroll to the end of the text area
            self.text_area.update_idletasks()  # Update the Tkinter GUI

def main():
    root = tk.Tk()
    app = RealTimeLogViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()