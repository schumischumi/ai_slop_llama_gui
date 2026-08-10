import tkinter as tk
from tkinter import ttk
from llama_gui.parser import Param, ParamGroup

def create_param_widgets(root: tk.Frame, groups: list[ParamGroup]) -> dict[str, tk.Variable]:
    """Create all widgets for the given param groups.
    Returns dict mapping param long_name to its Tkinter Variable (IntVar/StrVar/BooleanVar).
    Each widget stores its param name in the 'param_name' attribute for later lookup.
    """
    vars_dict = {}

    for group in groups:
        frame = ttk.LabelFrame(root, text=group.name.replace('_', ' ').title())
        frame.pack(fill="x", padx=10, pady=5, expand=True)

        collapsed_var = tk.BooleanVar(value=False)  # False = expanded
        toggle_btn = ttk.Button(frame, text="▼", width=2)
        toggle_btn.pack(side="right")

        content_frame = tk.Frame(frame)
        content_frame.pack(fill="x", expand=True)

        def on_toggle(v=collapsed_var, btn=toggle_btn, cf=content_frame):
            if v.get():
                cf.pack_forget()
                btn.config(text="▶")
            else:
                cf.pack(fill="x", expand=True)
                btn.config(text="▼")

        collapsed_var.trace_add("write", on_toggle)
        toggle_btn.config(command=lambda: collapsed_var.set(not collapsed_var.get()))

        for param in group.params:
            container = tk.Frame(content_frame)
            container.pack(fill="x", padx=5, pady=2, anchor="w")

            label = tk.Label(container, text=param.description, anchor="w")
            label.pack(side="top", fill="x")

            widget = None
            if param.param_type == "bool" or param.param_type == "flag":
                var = tk.BooleanVar(value=False)
                widget = ttk.Checkbutton(container, variable=var)
                widget.pack(side="left")
                vars_dict[param.long_name] = var
            elif param.param_type == "int":
                var = tk.IntVar(value=param.default if param.default and param.default.isdigit() else 0)
                widget = ttk.Spinbox(container, from_=0, to=99999, textvariable=var, width=10)
                widget.pack(side="left")
                vars_dict[param.long_name] = var
            elif param.param_type == "choice":
                var = tk.StringVar(value=str(param.default) if param.default else "")
                widget = ttk.Combobox(container, textvariable=var, values=param.choices, state="readonly")
                widget.pack(fill="x", expand=True, side="left")
                vars_dict[param.long_name] = var
            elif param.param_type == "string":
                var = tk.StringVar(value=param.default if param.default else "")
                widget = ttk.Entry(container, textvariable=var, width=40)
                widget.pack(fill="x", expand=True, side="left")
                vars_dict[param.long_name] = var

            if widget:
                widget.param_name = param.long_name

    return vars_dict

def set_widget_values(widgets: dict[str, tk.Variable], values: dict[str, str | int | bool]) -> None:
    """Set Tkinter variable values from a dict.
    Skips params not in widgets dict.
    Converts string values to int for IntVar widgets.
    """
    for name, value in values.items():
        if name not in widgets:
            continue
        
        var = widgets[name]
        
        try:
            if isinstance(var, tk.BooleanVar):
                # If value is truthy/falsy
                var.set(bool(value))
            elif isinstance(var, tk.IntVar):
                # If it's an int or a string that can be an int
                if isinstance(value, int):
                    var.set(value)
                elif isinstance(value, str) and value.isdigit():
                    var.set(int(value))
                else:
                    print(f"Warning: Cannot convert {type(value).__name__} to int for {name}")
            else:
                # StringVar or others
                var.set(str(value))
        except Exception as e:
            print(f"Warning: Error setting {name}: {e}")

def clear_all(widgets: dict[str, tk.Variable], groups: list[ParamGroup]) -> None:
    """Reset all widgets to default values."""
    values = {}
    for group in groups:
        for param in group.params:
            default = param.default
            if param.param_type == "flag":
                values[param.long_name] = False
            elif param.param_type == "bool":
                values[param.long_name] = False
            elif param.param_type == "int":
                values[param.long_name] = int(default) if default else 0
            elif param.param_type == "choice":
                values[param.long_name] = param.choices[0] if param.choices else ""
            else:  # string
                values[param.long_name] = default or ""
    set_widget_values(widgets, values)
