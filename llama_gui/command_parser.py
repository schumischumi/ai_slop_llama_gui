import shlex

from llama_gui.parser import ParamGroup


def parse_command(command: str, groups: list[ParamGroup]) -> dict[str, str | int | bool]:
    """Parse a llama-server command string into widget values dict.
    Handles both short and long flag forms.
    Skips unrecognised tokens silently.
    Returns dict mapping param long_name to parsed value.
    """
    tokens = shlex.split(command)
    if not tokens:
        return {}

    # Remove 'llama-server' if it is the first token
    if tokens[0] == "llama-server":
        tokens = tokens[1:]

    # Build reverse lookup: {short_flag: param, long_name: param, ...}
    reverse_lookup = {}
    for group in groups:
        for param in group.params:
            reverse_lookup[f"--{param.long_name}"] = param
            for short in param.short_flags:
                reverse_lookup[f"-{short}"] = param

    result = {}
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        if token.startswith('-'):
            param = reverse_lookup.get(token)
            if param:
                if param.param_type in ("flag", "bool") and param.has_value is False:
                    result[param.long_name] = True
                elif i + 1 < len(tokens) and not tokens[i+1].startswith('-'):
                    val = tokens[i+1]
                    if param.param_type == "int":
                        try:
                            val = int(val)
                        except ValueError:
                            pass
                    elif param.param_type == "bool":
                        if val.lower() in ("true", "on", "1", "yes"):
                            val = True
                        elif val.lower() in ("false", "off", "0", "no"):
                            val = False
                    result[param.long_name] = val
                    i += 1
                else:
                    # If it's a boolean flag without a value but it's not a 'no-' variant
                    # (which we already skipped in parser if it was a negation)
                    # For now, let's just set to True.
                    result[param.long_name] = True
            elif token.startswith("--no-"):
                # If we see a --no- flag, we should probably set it to False.
                # But we don't know which param it belongs to if it wasn't in reverse_lookup.
                pass
        i += 1
    
    return result
