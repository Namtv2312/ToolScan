from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, StringVar, filedialog, messagebox, Toplevel
from tkinter.ttk import Combobox

from scanner import scanner

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets/frame1")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def check_soket(host, port):
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        return 1
    except socket.error as e:
        return 0
    finally:
        sock.close()

def config_setup():
    Config()
    
class Config(Toplevel):
    def __init__(self, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)
        self.title("Setup Config")
        self.on = PhotoImage(file=relative_to_assets("on.png"))
        self.off = PhotoImage(file=relative_to_assets("off.png"))
        self.geometry("940x634")
        self.configure(bg = "#FFFFFF")

        self.canvas = Canvas(
            self,
            bg = "#FFFFFF",
            height = 634,
            width = 940,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        self.canvas.place(x = 0, y = 0)
        self.canvas.create_text(
            407.0,
            19.0,
            anchor="nw",
            text="Configuration Setup",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.canvas.create_text(
            34.0,
            80.0,
            anchor="nw",
            text="URL AV Scan",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.canvas.create_text(
            415.0,
            165.0,
            anchor="nw",
            text="Folder Path Monitor",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.canvas.create_text(
            411.0,
            237.0,
            anchor="nw",
            text="SFTP mode",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_1.png"))
        entry_bg_1 = self.canvas.create_image(
            267.54562201407344,
            79.05370626772486,
            image=self.entry_image_1
        )
        self.entry_1 = Entry(
            self,
            name="url_avscan",
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_1.place(
            x=147.99996803813758,
            y=65.0,
            width=239.09130795187173,
            height=26.107412535449726
        )

        self.entry_image_2 = PhotoImage(
            file=relative_to_assets("entry_2.png"))
        entry_bg_2 = self.canvas.create_image(
            277.5,
            136.0,
            image=self.entry_image_2
        )
        self.entry_2 = Entry(
            self,
            name="urlPDF",
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_2.place(
            x=168.0,
            y=124.0,
            width=219.0,
            height=22.0
        )

        self.entry_image_3 = PhotoImage(
            file=relative_to_assets("entry_3.png"))
        entry_bg_3 = self.canvas.create_image(
            465.0,
            207.0,
            image=self.entry_image_3
        )
        selected_folder =[]
        # entry_3 = Entry(
        #     name="folder_path",
        #     bd=0,
        #     bg="#D9D9D9",
        #     fg="#000716",
        #     highlightthickness=0
        # )
        textt = StringVar(value="Upload folder here")
        cb_listpath = Combobox(self, name="cb_listpath", values=selected_folder,textvariable= textt , state="normal", background="#D9D9D9",foreground="#000716")
        cb_listpath.place(
            x=360.0,
            y=194.0,
            width=210.0,
            height=24.0
        )
        def upload_folder():
            sel_folder = filedialog.askdirectory()
            selected_folder.append(sel_folder)
            cb_listpath["values"] = selected_folder

        button_image_4 = PhotoImage(
            file=relative_to_assets("button_4.png"))
        btn_Upload = Button(
            self,
            image=button_image_4,
            borderwidth=0,
            highlightthickness=0,
            command=upload_folder,
            relief="flat"
        )
        btn_Upload.place(
            x=579.0,
            y=185.0,
            width=56.0,
            height=39.0
        )
        self.canvas.create_text(
            33.0,
            278.0,
            anchor="nw",
            text="SFTP folders monitor",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.canvas.create_text(
            455.0,
            274.0,
            anchor="nw",
            text="Map local folder",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.canvas.create_text(
            210.0,
            327.0,
            anchor="nw",
            text="Hostname",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.canvas.create_text(
            107.0,
            373.0,
            anchor="nw",
            text="Username",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.canvas.create_text(
            107.0,
            373.0,
            anchor="nw",
            text="Username",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.canvas.create_text(
            488.0,
            374.0,
            anchor="nw",
            text="Password",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.canvas.create_text(
            563.0,
            324.0,
            anchor="nw",
            text="Port",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.entry_image_4 = PhotoImage(
            file=relative_to_assets("entry_4.png"))
        entry_bg_4 = self.canvas.create_image(
            282.0,
            285.0,
            image=self.entry_image_4
        )
        self.entry_4 = Entry(
            self,
            name="sftp_folder",
            state='readonly',
            readonlybackground='#D9D9D9',
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_4.place(
            x=177.0,
            y=272.0,
            width=210.0,
            height=24.0
        )

        self.entry_image_5 = PhotoImage(
            file=relative_to_assets("entry_5.png"))
        entry_bg_5 = self.canvas.create_image(
            668.0,
            279.0,
            image=self.entry_image_5
        )
        self.entry_5 = Entry(
            self,
            name="root_local",
            state='readonly',
            readonlybackground='#D9D9D9',
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_5.place(
            x=563.0,
            y=266.0,
            width=210.0,
            height=24.0
        )

        self.entry_image_6 = PhotoImage(
            file=relative_to_assets("entry_6.png"))
        entry_bg_6 = self.canvas.create_image(
            668.0,
            380.0,
            image=self.entry_image_6
        )
        self.entry_6 = Entry(
            self,
            name="password",
            state='readonly',
            readonlybackground='#D9D9D9',
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_6.place(
            x=563.0,
            y=367.0,
            width=210.0,
            height=24.0
        )

        self.entry_image_7 = PhotoImage(
            file=relative_to_assets("entry_7.png"))
        entry_bg_7 = self.canvas.create_image(
            392.0,
            331.0,
            image=self.entry_image_7
        )
        self.entry_7 = Entry(
            self,
            name="host_name",
            state='readonly',
            readonlybackground='#D9D9D9',
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_7.place(
            x=287.0,
            y=318.0,
            width=210.0,
            height=24.0
        )

        self.entry_image_8 = PhotoImage(
            file=relative_to_assets("entry_8.png"))
        entry_bg_8 = self.canvas.create_image(
            303.0,
            378.0,
            image=self.entry_image_8
        )
        self.entry_8 = Entry(
            self,
            name="user_name",
            state='readonly',
            readonlybackground='#D9D9D9',
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_8.place(
            x=198.0,
            y=365.0,
            width=210.0,
            height=24.0
        )

        self.entry_image_9 = PhotoImage(
            file=relative_to_assets("entry_9.png"))
        entry_bg_9 = self.canvas.create_image(
            635.0,
            331.0,
            image=self.entry_image_9
        )
        self.entry_9 = Entry(
            self,
            name="port",
            state='readonly',
            readonlybackground='#D9D9D9',
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_9.place(
            x=613.0,
            y=318.0,
            width=44.0,
            height=24.0
        )

        self.entry_image_10 = PhotoImage(
            file=relative_to_assets("entry_10.png"))
        entry_bg_10 = self.canvas.create_image(
            676.5,
            126.5,
            image=self.entry_image_10
        )
        self.entry_10 = Entry(
            self,
            name="token_sets",
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_10.place(
            x=563.0,
            y=111.0,
            width=227.0,
            height=29.0
        )

        self.canvas.create_text(
            813.0,
            80.0,
            anchor="nw",
            text="10",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        image_image_1 = PhotoImage(
            file=relative_to_assets("image_1.png"))
        image_1 = self.canvas.create_image(
            561.0,
            22.0,
            image=image_image_1
        )

        self.canvas.create_text(
            33.0,
            130.0,
            anchor="nw",
            text="URL Convert to PDF",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.canvas.create_text(
            449.0,
            80.0,
            anchor="nw",
            text="Max File Size",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.canvas.create_text(
            449.0,
            121.0,
            anchor="nw",
            text="Token",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.canvas.create_text(
            91.0,
            451.0,
            anchor="nw",
            text="URL AI Scan",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.entry_image_11 = PhotoImage(
            file=relative_to_assets("entry_11.png"))
        entry_bg_11 = self.canvas.create_image(
            298.5,
            456.0,
            image=self.entry_image_11
        )
        self.entry_11 = Entry(
            self,
            name="url_ai",
            state='readonly',
            readonlybackground='#D9D9D9',
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_11.place(
            x=189.0,
            y=444.0,
            width=219.0,
            height=22.0
        )

        self.entry_image_12 = PhotoImage(
            file=relative_to_assets("entry_12.png"))
        entry_bg_12 = self.canvas.create_image(
            677.0,
            452.5,
            image=self.entry_image_12
        )
        self.entry_12 = Entry(
            self,
            name="token_ai",
            state='readonly',
            readonlybackground='#D9D9D9',
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_12.place(
            x=572.0,
            y=437.0,
            width=210.0,
            height=29.0
        )

        self.canvas.create_text(
            481.0,
            448.0,
            anchor="nw",
            text="Token",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )

        self.entry_image_13 = PhotoImage(
            file=relative_to_assets("entry_13.png"))
        entry_bg_13 = self.canvas.create_image(
            675.5,
            80.5,
            image=self.entry_image_13
        )
        self.entry_13 = Entry(
            self,
            name="max_file_size",
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_13.place(
            x=558.5,
            y=68.0,
            width=234.0,
            height=23.0
        )

        image_image_2 = PhotoImage(
            file=relative_to_assets("image_2.png"))
        image_2 = self.canvas.create_image(
            374.0,
            22.0,
            image=image_image_2
        )

        button_image_1 = PhotoImage(
            file=relative_to_assets("button_1.png"))
        btn_Generate = Button(
            self,
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.generate_config(),
            relief="flat"
        )
        btn_Generate.place(
            x=407.0,
            y=514.0,
            width=126.0,
            height=37.0
        )

        self.canvas.create_text(
            397.0,
            409.0,
            anchor="nw",
            text="AI detect",
            fill="#000000",
            font=("Inter ExtraBold", 12 * -1)
        )
        sftp_frame = ["sftp_folder", "root_local", "host_name", "port", "user_name", "password"]
        ai_frame = ["url_ai", "token_ai"]
        self.is_on = False
        def Switch(self, button):
            if self.is_on:
                button.config(image = self.off)
                self.is_on = False
                if button._name =="btn_sftp":
                    for i in sftp_frame:
                        self.nametowidget(i).configure(state='readonly', readonlybackground='#D9D9D9')
                if button._name =="btn_ai":
                    for i in ai_frame:
                        self.nametowidget(i).configure(state='readonly', readonlybackground='#D9D9D9')
            else:
                button.config(image = self.on)
                self.is_on = True
                if button._name =="btn_sftp":
                    for i in sftp_frame:
                        self.nametowidget(i).configure(state='normal')
                if button._name =="btn_ai":
                    for i in ai_frame:
                        self.nametowidget(i).configure(state='normal')

        btn_sftp = Button(
            self,
            name="btn_sftp",
            image=self.off,
            borderwidth=0,
            highlightthickness=0,
            command= lambda: Switch(self, btn_sftp),
            relief="flat"
        )
        btn_sftp.place(
            x=488.0,
            y=231.0,
            width=65.0,
            height=26.0
        )

        button_image_3 = PhotoImage(
            file=relative_to_assets("button_3.png"))
        btn_ai = Button(
            self,
            name="btn_ai",
            image=button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: Switch(self, btn_ai),
            relief="flat"
        )
        btn_ai.place(
            x=488.0,
            y=403.0,
            width=65.0,
            height=26.0
        )

        self.resizable(False, False)
        self.mainloop()

    def loginFunc(self):
        global user
        self.destroy()
        scanner()
        messagebox.showerror(
            title="Invalid Credentials",
            message="The username and self.password don't match",
        )
    def generate_config(self):
        print('heelo')
        print("url AV SCAN",self.nametowidget("url_avscan").get())
        print("sftp_folder",self.nametowidget("sftp_folder").get())
        print("root local",self.nametowidget("root_local").get())
        print("hostname",self.nametowidget("host_name").get())
        print("port",self.nametowidget("port").get())
        print("username",self.nametowidget("user_name").get())
        print("password",self.nametowidget("password").get())
        print("URLAI",self.nametowidget("url_ai").get())
        print("toeken ai",self.nametowidget("token_ai").get())
        print("max_file_size",self.nametowidget("max_file_size").get())
        print("urlpdf",self.nametowidget("urlPDF").get())
        print("toeken setting",self.nametowidget("token_sets").get())

        replace_values = {
            'url_avscan': self.nametowidget("url_avscan").get(),
            'url_off2pdf':self.nametowidget("urlPDF").get(),
            'folder_paths': "[('C:\\Users\\Admin\\Desktop\\TEST_SCANN\\foldertest\\1', 1), ('C:\\Users\\Admin\\Desktop\\TEST_SCANN\\foldertest\\2', 2)]",
            'max_file_size': self.nametowidget("max_file_size").get(),
            'token': self.nametowidget("token_sets").get(),
            'sftp_on_demand': 1 if self.nametowidget("host_name").get() else 0,
            'sftp_folder_paths': "[(r'C:\\Users\\IEUser\\Desktop\\Scan\\1', 1), (r'C:\\Users\\IEUser\\Desktop\\Scan\\2', 2)]",
            'sftp_root_local_folder': self.nametowidget("root_local").get(),
            'sftp_hostname': self.nametowidget("host_name").get(),
            'sftp_port': self.nametowidget("port").get(),
            'sftp_username': self.nametowidget("user_name").get(),
            'sftp_password': self.nametowidget("password").get(),
            'virustotal_on_demand': 0,
            'virustotal_key': '359990a6ffa1c180283eab65975fb6bff1345b94eff44b6e0a194d891618cb5b',
            'ai_detect_on_demand': 1 if self.nametowidget("url_ai").get() else 0,
            'url_ai_detect': self.nametowidget("url_ai").get(),
            'ai_detect_token': self.nametowidget("token_ai").get()
        }
        template = """
        [Settings]
        URL_avscan = {url_avscan}
        URL_off2pdf = {url_off2pdf}
        Folder_path = {folder_paths}
        Max_file_size = {max_file_size}
        token = {token}
        [sftp]
        on_demand = {sftp_on_demand}
        sftp_folder_path = {sftp_folder_paths}
        root_local_folder = {sftp_root_local_folder}
        hostname = {sftp_hostname}
        port = {sftp_port}
        username = {sftp_username}
        password = {sftp_password}
        [virustotal]
        on_demand = {virustotal_on_demand}
        key = {virustotal_key}
        [ai_detect]
        on_demand = {ai_detect_on_demand}
        URL_ai_detect = {url_ai_detect}
        token = {ai_detect_token}
        """
        result = template.format_map(replace_values)
        file_path = "config.ini"
        with open(file_path, "w") as file:
            file.write(result)
        messagebox.showinfo("Successful", "Details updated successfully")
        scanner()
        self.destroy()

# if __name__ == "__main__":
#     config_setup()