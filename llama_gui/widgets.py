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

        for param in group.params:
            container = tk.Frame(frame)
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
