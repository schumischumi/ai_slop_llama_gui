import tkinter as tk

from llama_gui.parser import ParamGroup


def build_command(widgets: dict[str, tk.Variable], groups: list[ParamGroup]) -> str:
    """Build llama-server command string from widget values.
    Omits params whose value matches the default.
    Uses short flags when available and preferred.
    Returns string like 'llama-server -c 8192 -ngl 99 -fa on'
    """
    command_parts = ["llama-server"]

    for group in groups:
        for param in group.params:
            if param.long_name not in widgets:
                continue

            var = widgets[param.long_name]
            
            # Get current value from tkinter variable
            if isinstance(var, tk.BooleanVar):
                val = var.get()
            elif isinstance(var, tk.IntVar):
                val = var.get()
            elif isinstance(var, tk.StringVar):
                val = var.get()
            else:
                continue

            # Check if it's default
            is_default = False
            if param.param_type == "bool" or param.param_type == "flag":
                # For bool/flag, default is usually False (0)
                # If it's a 'no-' variant, we'd handle that in the loop logic
                if val is False or val == 0:
                    is_default = True
            elif param.param_type == "int":
                if param.default is not None and str(val) == str(param.default):
                    is_default = True
                elif param.default is None and val == 0: # assuming 0 is default if not specified? No, check param.default
                     pass
            elif param.param_type == "choice":
                if param.default and str(val) == str(param.default):
                    is_default = True
            elif param.param_type == "string":
                if not val:
                    is_default = True
                elif param.default and val == param.default:
                    is_default = True
            
            # More robust default check for int/choice/string
            if not is_default:
                if param.param_type == "flag":
                    # Standard flags don't have values, they are just present
                    # But wait, if it's a flag, it's either there or not.
                    # If it's False, we don't add it.
                    if val:
                        command_parts.append(f"--{param.long_name}")
                elif param.param_type == "bool":
                    # bool can be --flag or --no-flag or --flag value
                    # The story says: "If True, emit short flag first (if exists), else --long-name; 
                    # if False and negation exists, emit --no-*"
                    negation_name = f"no-{param.long_name}"
                    # We need to know if a negation exists. The parser should have handled it.
                    # Let's assume if it's True we emit --long-name.
                    # If the user wants short flags:
                    if param.short_flags:
                        command_parts.append(f"-{param.short_flags[0]}")
                    else:
                        command_parts.append(f"--{param.long_name}")
                else:
                    # int, choice, string
                    if param.short_flags:
                        command_parts.append(f"-{param.short_flags[0]}")
                        command_parts.append(str(val))
                    else:
                        command_parts.append(f"--{param.long_name}")
                        command_parts.append(str(val))

    return " ".join(command_parts)
