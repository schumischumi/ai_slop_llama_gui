import re
from dataclasses import dataclass


@dataclass
class Param:
    long_name: str
    short_flags: list[str]
    description: str
    param_type: str  # "int" | "bool" | "flag" | "choice" | "string"
    default: str | None
    choices: list[str] | None
    has_value: bool
    is_no_variant: bool = False

@dataclass
class ParamGroup:
    name: str
    params: list[Param]

class HelpParser:
    def parse(self, help_text: str) -> list[ParamGroup]:
        lines = help_text.splitlines()
        groups = []
        current_group = None
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()
            if not stripped_line:
                i += 1
                continue
                
            if stripped_line.startswith('-----') and stripped_line.endswith('-----'):
                group_name = stripped_line.strip('- ').lower().replace(' ', '_')
                current_group = ParamGroup(name=group_name, params=[])
                groups.append(current_group)
                i += 1
                continue

            if current_group is None:
                i += 1
                continue

            if stripped_line.startswith('-'):
                tokens = stripped_line.split()
                dash_tokens_indices = [idx for idx, token in enumerate(tokens) if token.startswith('-')]
                
                if dash_tokens_indices:
                    name_idx = dash_tokens_indices[-1]
                    raw_name = tokens[name_idx].lstrip('-').strip(',')
                    
                    is_no_variant = raw_name.startswith('no-')
                    effective_name = raw_name[3:] if is_no_variant else raw_name
                    
                    short_flags = []
                    for f_idx in range(name_idx):
                        if tokens[f_idx].startswith('-'):
                            short_flags.append(tokens[f_idx].strip('-').strip(','))
                    
                    remainder_parts = tokens[name_idx+1:]
                    description = ""
                    value_placeholder = None
                    
                    if remainder_parts:
                        if re.match(r'^(\[on|off|auto\]|\{[^}]+\}|<[^>]+>|[a-zA-Z0-9]+|\[[^\]]+\])$', remainder_parts[0]):
                            value_placeholder = remainder_parts[0]
                            description = " ".join(remainder_parts[1:])
                        else:
                            description = " ".join(remainder_parts)

                    while i + 1 < len(lines):
                        next_line = lines[i+1]
                        next_stripped = next_line.strip()
                        if not next_stripped:
                            i += 1
                            continue
                        if (next_line.startswith(' ') or next_line.startswith('\t')) and not next_stripped.startswith('-'):
                            description += " " + next_stripped
                            i += 1
                        else:
                            break
                
                param_type = "string"
                choices = None
                has_value = True
                
                if value_placeholder:
                    if value_placeholder.upper() == "N" or re.match(r'^\d+$', value_placeholder):
                        param_type = "int"
                    elif value_placeholder.startswith('[') and value_placeholder.endswith(']'):
                        choices_str = value_placeholder[1:-1]
                        choices = [c.strip() for c in choices_str.split('|')]
                        param_type = "choice"
                    elif value_placeholder.startswith('{') and value_placeholder.endswith('}'):
                        choices_str = value_placeholder[1:-1]
                        choices = [c.strip() for c in choices_str.split(',')]
                        param_type = "choice"
                    elif value_placeholder == "[on|off|auto]":
                        choices = ["on", "off", "auto"]
                        param_type = "choice"
                    else:
                        param_type = "string"
                    has_value = True
                else:
                    if is_no_variant:
                        param_type = "bool"
                        has_value = False
                    else:
                        param_type = "flag"
                        has_value = False
                        if re.search(rf'--no-{re.escape(effective_name)}(?:\s|$|\()', help_text):
                            param_type = "bool"
                            has_value = False
                
                default = None
                default_match = re.search(r'\(default:\s*([^)]+)\)', description)
                if default_match:
                    default = default_match.group(1).strip()

                p = Param(
                    long_name=effective_name,
                    short_flags=short_flags,
                    description=description,
                    param_type=param_type,
                    default=default,
                    choices=choices,
                    has_value=has_value,
                    is_no_variant=is_no_variant
                )
                current_group.params.append(p)
            
            i += 1

        for group in groups:
            final_params = []
            # Find all effective names that have a positive version
            positive_names = {p.long_name for p in group.params if not p.is_no_variant}
            
            for p in group.params:
                if p.is_no_variant and p.long_name in positive_names:
                    # This is a 'no-' variant and the positive version exists. Skip it.
                    continue
                final_params.append(p)
            group.params = final_params
            
        return groups
