from dotenv import load_dotenv
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pytesseract
import mss
import numpy as np
from deep_translator import GoogleTranslator

load_dotenv()

# 🔧 SET THIS PATH (IMPORTANT for Windows)
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")


class ScreenTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Translator")
        self.root.geometry("300x400")

        self.label = tk.Label(root, text="Click to select screen area")
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Select Area", command=self.start_selection)
        self.btn.pack(pady=5)

        # ✅ Delete button
        self.clear_btn = tk.Button(root, text="Clear Text", command=self.clear_text)
        self.clear_btn.pack(pady=5)

        # ✅ Frame for Text + Scrollbar
        frame = tk.Frame(root)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.result_box = tk.Text(
            frame,
            height=14,
            wrap="word",
            yscrollcommand=self.scrollbar.set
        )
        self.result_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.result_box.yview)

        self.start_x = None
        self.start_y = None
        self.rect = None

    # ✅ Clear function
    def clear_text(self):
        self.result_box.delete("1.0", tk.END)

    def start_selection(self):
        self.overlay = tk.Toplevel(self.root)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-alpha", 0.3)
        self.overlay.configure(bg="black")

        self.canvas = tk.Canvas(self.overlay, cursor="cross", bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y

        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.start_x, self.start_y,
            outline="red", width=2
        )

    def on_mouse_drag(self, event):
        self.canvas.coords(
            self.rect,
            self.start_x, self.start_y,
            event.x, event.y
        )

    def on_mouse_up(self, event):
        end_x = event.x
        end_y = event.y

        # Convert to SCREEN coordinates
        x1 = self.overlay.winfo_rootx() + min(self.start_x, end_x)
        y1 = self.overlay.winfo_rooty() + min(self.start_y, end_y)
        x2 = self.overlay.winfo_rootx() + max(self.start_x, end_x)
        y2 = self.overlay.winfo_rooty() + max(self.start_y, end_y)

        # ✅ Hide overlay BEFORE capture
        self.overlay.withdraw()
        self.root.update_idletasks()
        self.root.update()

        # ✅ REAL delay (important!)
        self.root.after(150, lambda: self.capture_and_destroy(x1, y1, x2, y2))
    
    def capture_and_destroy(self, x1, y1, x2, y2):
        self.process_region(x1, y1, x2, y2)
        self.overlay.destroy()

    def process_region(self, x1, y1, x2, y2):
        width = x2 - x1
        height = y2 - y1

        if width < 10 or height < 10:
            return

        with mss.mss() as sct:
            monitor = {
                "top": y1,
                "left": x1,
                "width": width,
                "height": height
            }
            screenshot = sct.grab(monitor)

        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        # OCR
        text = pytesseract.image_to_string(img, lang='chi_sim_vert')

        if not text.strip():
            messagebox.showinfo("Result", "No text detected.")
            return

        try:
            clean_text = "".join(text.split())
            translated = GoogleTranslator(source='zh-CN', target='en').translate(clean_text)
            result_text = translated
        except Exception as e:
            result_text = f"Translation error:\n{e}"

        # ✅ Append instead of replace
        self.result_box.insert(tk.END, text + "\n" + result_text + "\n\n")

        # ✅ Auto scroll to bottom
        self.result_box.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTranslator(root)
    root.mainloop()