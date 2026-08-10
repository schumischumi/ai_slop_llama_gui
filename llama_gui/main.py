import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
from pathlib import Path
from llama_gui.parser import HelpParser
from llama_gui.widgets import create_param_widgets, collect_widget_values, set_widget_values, clear_all
from llama_gui.command_builder import build_command
from llama_gui.command_parser import parse_command
from llama_gui.profile_manager import ProfileManager

class LlamaGuiApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Llama Server Configurator")
        self.root.geometry("600x700")
        self.root.minsize(800, 600)

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
        self.groups = []
        self.profile_manager = ProfileManager()
        self.load_parameters()
        self.setup_control_panel()

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
            self.groups = parser.parse(help_text)

            if not self.groups:
                self.status_var.set("No parameters found in help text.")
                return

            # Create widgets
            self.vars_dict = create_param_widgets(self.scrollable_frame, self.groups)

            # Add trace to each variable
            for var in self.vars_dict.values():
                var.trace_add("write", lambda *args: self.update_preview())

            param_count = sum(len(g.params) for g in self.groups)
            self.status_var.set(f"Help loaded: {param_count} params in {len(self.groups)} groups")

        except Exception as e:
            messagebox.showerror("llama-server not found", f"Failed to load parameters:\n{e}")
            self.status_var.set("Error loading parameters.")

    def setup_control_panel(self):
        # Profile toolbar
        profile_toolbar = ttk.Frame(self.root)
        profile_toolbar.pack(fill="x", padx=10, pady=5)

        ttk.Label(profile_toolbar, text="Profile:").pack(side="left", padx=(0, 5))
        
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(profile_toolbar, textvariable=self.profile_var, state="readonly")
        self.profile_combo.pack(side="left", padx=5)
        self.update_profile_list()

        ttk.Button(profile_toolbar, text="Load", command=self.on_load).pack(side="left", padx=2)
        ttk.Button(profile_toolbar, text="Save", command=self.on_save).pack(side="left", padx=2)
        ttk.Button(profile_toolbar, text="Delete", command=self.on_delete).pack(side="left", padx=2)
        ttk.Button(profile_toolbar, text="Clear All", command=self.on_clear_all).pack(side="left", padx=2)

        # Control panel
        control_frame = ttk.LabelFrame(self.main_frame, text="Command Control")
        control_frame.pack(fill="x", padx=10, pady=10)

        # Command Preview
        preview_frame = ttk.Frame(control_frame)
        preview_frame.pack(fill="x", padx=5, pady=5)
        
        self.preview_text = tk.Text(preview_frame, height=1, wrap=tk.NONE)
        self.preview_text.pack(side="left", fill="x", expand=True)
        
        copy_btn = ttk.Button(preview_frame, text="Copy", command=self.on_copy)
        copy_btn.pack(side="right", padx=5)

        # Paste field
        paste_frame = ttk.Frame(control_frame)
        paste_frame.pack(fill="x", padx=5, pady=5)
        
        self.paste_entry = ttk.Entry(paste_frame)
        self.paste_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        parse_btn = ttk.Button(paste_frame, text="Parse →", command=self.on_parse)
        parse_btn.pack(side="right")

        self.update_preview()

    def update_profile_list(self):
        profiles = self.profile_manager.list_profiles()
        self.profile_combo['values'] = profiles
        if self.profile_var.get() in profiles:
            self.profile_var.set(profiles[self.profile_var.get()])
        else:
            self.profile_var.set("")

    def on_save(self):
        name = simpledialog.askstring("Save Profile", "Profile name:")
        if name:
            try:
                self.profile_manager.save(name, collect_widget_values(self.vars_dict))
                self.update_profile_list()
            except Exception as e:
                messagebox.showerror("Save failed", f"{e}")

    def on_load(self):
        name = self.profile_var.get()
        if not name:
            return
        try:
            values = self.profile_manager.load(name)
            set_widget_values(self.vars_dict, values)
            self.update_preview()
        except Exception as e:
            messagebox.showerror("Load failed", f"{e}")

    def on_delete(self: None) -> None:
        name = self.profile_var.get()
        if not name:
            return
        if messagebox.askyesno("Delete Profile", f"Are you sure you want to delete '{name}'?"):
            try:
                if self.profile_manager.delete(name):
                    self.update_profile_list()
                else:
                    messagebox.showwarning("Warning", "Profile not found.")
            except Exception as e:
                messagebox.showerror("Delete failed", f"{e}")

    def update_preview(self):
        if not self.vars_dict:
            return
        
        cmd = build_command(self.vars_dict, self.groups)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, cmd)

    def on_copy(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.preview_text.get("1.0", tk.END).strip())

    def on_parse(self):
        cmd = self.paste_entry.get().strip()
        if not cmd:
            return
        
        try:
            parsed_values = parse_command(cmd, self.groups)
            for param_name, val in parsed_values.items():
                if param_name in self.vars_dict:
                    self.vars_dict[param_name].set(val)
            self.update_preview()
        except Exception as e:
            messagebox.showerror("Parse Error", f"Failed to parse command:\n{e}")

    def on_clear_all(self):
        try:
            clear_all(self.vars_dict, self.groups)
            self.update_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear all: {e}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = LlamaGuiApp()
    app.run()
