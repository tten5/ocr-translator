import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 🔥 FIX DPI SHIFT (IMPORTANT)

from dotenv import load_dotenv
import os
import tkinter as tk
from tkinter import messagebox
import pytesseract
import mss
from PIL import Image
from deep_translator import GoogleTranslator

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")


class ScreenTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Translator")
        self.root.geometry("300x400")

        tk.Button(root, text="Select Area", command=self.start_selection).pack(pady=5)
        tk.Button(root, text="Clear", command=self.clear_text).pack(pady=5)

        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_box = tk.Text(frame, wrap="word", yscrollcommand=self.scrollbar.set)
        self.text_box.pack(fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.text_box.yview)

        self.start_x = 0
        self.start_y = 0
        self.rect = None

    # ---------------- UI ----------------

    def clear_text(self):
        self.text_box.delete("1.0", tk.END)

    # ---------------- OVERLAY ----------------

    def start_selection(self):
        self.overlay = tk.Toplevel(self.root)

        # TRUE SCREEN SIZE (fix shift/empty area bug)
        screen_w = self.overlay.winfo_screenwidth()
        screen_h = self.overlay.winfo_screenheight()

        self.overlay.geometry(f"{screen_w}x{screen_h}+0+0")
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.25)
        self.overlay.overrideredirect(True)  # removes border = true fullscreen

        self.canvas = tk.Canvas(self.overlay, cursor="cross", bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_down)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_up)

    # ---------------- MOUSE ----------------

    def on_down(self, event):
        self.start_x = event.x
        self.start_y = event.y

        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.start_x, self.start_y,
            outline="red", width=2
        )

    def on_drag(self, event):
        self.canvas.coords(
            self.rect,
            self.start_x,
            self.start_y,
            event.x,
            event.y
        )

    def on_up(self, event):
        end_x = event.x
        end_y = event.y

        # Convert canvas coords → screen coords correctly
        ox = self.overlay.winfo_rootx()
        oy = self.overlay.winfo_rooty()

        x1 = ox + min(self.start_x, end_x)
        y1 = oy + min(self.start_y, end_y)
        x2 = ox + max(self.start_x, end_x)
        y2 = oy + max(self.start_y, end_y)

        self.overlay.destroy()

        self.root.after(100, lambda: self.capture(x1, y1, x2, y2))

    # ---------------- CAPTURE ----------------

    def capture(self, x1, y1, x2, y2):
        width = x2 - x1
        height = y2 - y1

        if width < 10 or height < 10:
            return

        with mss.mss() as sct:
            monitor = {
                "left": int(x1),
                "top": int(y1),
                "width": int(width),
                "height": int(height)
            }
            img = sct.grab(monitor)

        image = Image.frombytes("RGB", img.size, img.rgb)

        text = pytesseract.image_to_string(image, lang="chi_sim_vert")

        if not text.strip():
            messagebox.showinfo("Result", "No text detected")
            return

        try:
            translated = GoogleTranslator(
                source="zh-CN",
                target="en"
            ).translate("".join(text.split()))
        except Exception as e:
            translated = str(e)

        self.text_box.insert(tk.END, text + "\n" + translated + "\n\n")
        self.text_box.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTranslator(root)
    root.mainloop()