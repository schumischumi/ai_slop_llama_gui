import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from llama_gui.parser import HelpParser
from llama_gui.widgets import create_param_widgets

class LlamaGuiApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Llama Server Configurator")
        self.root.geometry("600x500")

        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # Scrollable Canvas setup
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Status bar
        self.status_var = tk.StringVar(value="Initializing...")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")

        self.vars_dict = {}
        self.load_parameters()

    def load_parameters(self):
        try:
            # Attempt to get help text from llama-server
            try:
                help_text = subprocess.check_output(["llama-server", "--help"], text=True, stderr=subprocess.STDOUT)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                # Fallback/Mock for development if llama-server is not installed
                help_text = """
                ----- common params -----
                -t, --threads N (default: 8)
                --cpu-strict
                --no-cpu-strict
                --model <model_name>
                --choices [a|b|c]
                --flag-only
                """
                print(f"Warning: llama-server not found or failed. Using mock help text. Error: {e}")

            parser = HelpParser()
            groups = parser.parse(help_text)

            if not groups:
                self.status_var.set("No parameters found in help text.")
                return

            # Create widgets
            self.vars_dict = create_param_widgets(self.scrollable_frame, groups)

            param_count = sum(len(g.params) for g in groups)
            self.status_var.set(f"Help loaded: {param_count} params in {len(groups)} groups")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load parameters:\n{e}")
            self.status_var.set("Error loading parameters.")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = LlamaGuiApp()
    app.run()
