import tkinter as tk
from gui.config_setup import config_setup
from gui.scanner import scanner

root = tk.Tk()  # Make temporary window for app to start
root.withdraw()  # WithDraw the window


if __name__ == "__main__":

    config_setup()
    # root.destroy()
