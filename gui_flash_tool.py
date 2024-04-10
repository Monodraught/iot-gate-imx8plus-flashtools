import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import subprocess
import threading

class FlasherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("IMX8 Board Flasher")

        self.dram_conf = "d2d4"
        self.balena_image = tk.StringVar()

        self.arch = self.get_system_architecture()
        if self.arch not in ["armv7", "armv8", "aarch64"]:
            self.arch = None  # Default to None if architecture is not recognized

        self.create_widgets()
        self.flash_process = None
        self.flash_thread = None

    def create_widgets(self):
        ttk.Label(self.root, text="Balena Image:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.balena_image).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(self.root, text="Browse", command=self.browse_image).grid(row=0, column=2, padx=5, pady=5)

        if self.arch:
            ttk.Label(self.root, text="Architecture:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            ttk.Label(self.root, text=self.arch).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(self.root, text="Flash", command=self.start_flash).grid(row=2, column=0, padx=5, pady=10)
        ttk.Button(self.root, text="Cancel", command=self.cancel_flash).grid(row=2, column=1, padx=5, pady=10)

    def browse_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Balena Images", "*.img")])
        if filename:
            self.balena_image.set(filename)

    def start_flash(self):
        balena_image = self.balena_image.get()

        if not balena_image:
            messagebox.showerror("Error", "Balena Image is required.")
            return

        cmd = f"./run_container.sh -d {self.dram_conf} -i {balena_image}"
        if self.arch:
            cmd += f" -a {self.arch}"

        try:
            self.flash_thread = threading.Thread(target=self.execute_flash, args=(cmd,))
            self.flash_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start flashing process: {e}")

    def execute_flash(self, cmd):
        try:
            self.flash_process = subprocess.Popen(cmd, shell=True)
            self.flash_process.wait()  # Wait for the process to finish
            if self.flash_process.returncode == 0:
                self.root.after(0, lambda: messagebox.showinfo("Success", "Board flashed successfully."))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to flash the board."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to start flashing process: {e}"))

    def cancel_flash(self):
        if self.flash_process:
            self.flash_process.terminate()
            self.root.after(0, lambda: messagebox.showinfo("Info", "Flashing process cancelled."))
            self.flash_process = None
        elif self.flash_thread and self.flash_thread.is_alive():
            self.root.after(0, lambda: messagebox.showinfo("Info", "Cancelling flashing process."))
            self.flash_thread.join()
            self.root.after(0, lambda: messagebox.showinfo("Info", "Flashing process cancelled."))
            self.flash_thread = None
        else:
            self.root.after(0, lambda: messagebox.showinfo("Info", "No flashing process to cancel."))

    def get_system_architecture(self):
        try:
            arch = subprocess.check_output(["uname", "-m"]).decode().strip()
            if arch.startswith("arm"):
                if "armv7" in arch:
                    return "armv7"
                elif "aarch64" in arch:
                    return "aarch64"
                else:
                    return "armv8"  # Assume ARMv8 if not explicitly armv7 or aarch64
            elif arch.startswith("x86"):
                return "x86"
            else:
                return arch  # Return actual architecture if not arm or x86
        except Exception as e:
            print("Error determining architecture:", e)
            return "Unknown"

def main():
    root = tk.Tk()
    app = FlasherGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
