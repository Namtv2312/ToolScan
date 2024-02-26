from pathlib import Path
from tkinter import (
    Toplevel,
    Frame,
    Canvas,
    Button,
    PhotoImage,
    messagebox,
    StringVar,
    Tk
)

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets/frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)
def scanner():
    Scanner()
class Scanner(Toplevel):
    def __init__(self, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)
        self.geometry("1106x832")
        self.configure(bg = "#FFFFFF")

        self.canvas = Canvas(
            self,
            bg = "#FFFFFF",
            height = 832,
            width = 1106,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        self.canvas.place(x = 0, y = 0)
        self.image_image_1 = PhotoImage(
            file=relative_to_assets("image_1.png"))
        self.image_1 = self.canvas.create_image(
            553.0,
            185.0,
            image=self.image_image_1
        )

        self.canvas.create_rectangle(
            488.0,
            732.0,
            605.0,
            793.0,
            fill="#D9D9D9",
            outline="")

        self.canvas.create_text(
            496.0,
            737.0,
            anchor="nw",
            text="SCAN",
            fill="#E20000",
            font=("Inter ExtraBold", 18 * -1)
        )
        self.resizable(False, False)
        self.mainloop()
