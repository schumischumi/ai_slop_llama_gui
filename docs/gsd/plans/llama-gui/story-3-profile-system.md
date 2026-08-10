# Story 3: Profile system (save/load/delete)

**Files:**
- Create: `llama_gui/profile_manager.py`
- Modify: `llama_gui/main.py` — add profile toolbar with Load dropdown, Save, Delete buttons
- Modify: `llama_gui/widgets.py` — add `set_widget_values()` function to apply a dict of values

**Context:**
- Stories 1-2 provide `collect_widget_values() -> dict` and the full widget system
- Profile dir: `~/.config/llama-gui/profiles/`
- YAML format: `{name, created (ISO timestamp), params: {param_name: value, ...}}`

**File summaries:**

- `llama_gui/profile_manager.py` — `ProfileManager` class with `save()`, `load()`, `list_profiles()`, `delete()` methods. Handles directory creation, YAML I/O, error cases.
- `llama_gui/main.py` — adds profile toolbar (`ttk.Frame` at top): `ttk.Combobox` (Load dropdown), `ttk.Button("Save")`, `ttk.Button("Delete")`. Save prompts for name (simple `tk.simpledialog.askstring`), load sets widgets, delete confirms and removes.
- `llama_gui/widgets.py` — adds `set_widget_values(widgets: dict[str, tk.Variable], values: dict[str, str | int | bool]) -> None`. Sets Tkinter variable values programmatically.

**Symbols to implement:**

```python
# profile_manager.py
class ProfileManager:
    def __init__(self, profiles_dir: Path | None = None):
        # defaults to ~/.config/llama-gui/profiles/
    
    def save(self, name: str, params: dict[str, str | int | bool]) -> Path:
        """Save profile. Returns path to saved file.
        Creates profiles_dir if missing.
        Overwrites existing profile with same name.
        """
    
    def load(self, name: str) -> dict[str, str | int | bool]:
        """Load profile. Returns params dict.
        Raises FileNotFoundError if not found.
        """
    
    def list_profiles(self) -> list[str]:
        """List profile names (without .yaml extension).
        Returns sorted list.
        """
    
    def delete(self, name: str) -> bool:
        """Delete profile. Returns True if deleted, False if not found."""

# widgets.py
def set_widget_values(widgets: dict[str, tk.Variable], values: dict[str, str | int | bool]) -> None:
    """Set Tkinter variable values from a dict.
    Skips params not in widgets dict.
    Converts string values to int for IntVar widgets.
    """
```

**ProfileManager implementation details:**
- `profiles_dir`: `Path.home() / ".config" / "llama-gui" / "profiles"`
- `save()`: creates parent dirs, writes YAML with `yaml.dump()`, filename `{name}.yaml`
- `load()`: reads file, parses YAML, returns `data["params"]`
- `list_profiles()`: glob `profiles/*.yaml`, strip `.yaml` extension, sort
- `delete()`: `path.unlink()`, catches `FileNotFoundError` → return False

**Main.py profile toolbar:**
- Top toolbar: `ttk.Frame(root)`
- Left: `ttk.Combobox(root, values=profile_names, state="readonly", width=20)` — Load dropdown
- Middle: `ttk.Button(root, text="Save Profile", command=on_save)` 
- Right: `ttk.Button(root, text="Delete Profile", command=on_delete)`
- `on_save()`: `tk.simpledialog.askstring("Save Profile", "Profile name:")` → if name and not empty → `profile_manager.save(name, collect_widget_values())` → refresh dropdown
- `on_load()`: combobox selection → get name → `values = profile_manager.load(name)` → `set_widget_values(widgets, values)`
- `on_delete()`: combobox selection → confirm dialog → `profile_manager.delete(name)` → refresh dropdown
- `update_profile_list()`: calls `profile_manager.list_profiles()`, updates combobox values, sets current value

**set_widget_values details:**
- For each `(param_name, value)` in values dict:
  - If `param_name` not in widgets: skip
  - Get the widget's Tkinter variable
  - If value is bool: `var.set(value)`
  - If value is int and var is IntVar: `var.set(value)`
  - If value is str: `var.set(value)`
  - If value is str but var is IntVar: try `int(value)`, else skip with warning

**Verify:**
- `python -m pytest tests/ -v` — all tests pass (add `tests/test_profile_manager.py`)
- `python main.py` — manual: change widgets, save as "test-profile", verify YAML file exists, load "test-profile", verify widgets match

**Commit:** `feat: YAML profile save/load/delete system`

**Depends on:** Story 2

**Tasks:**
- [ ] Write `profile_manager.py` with `ProfileManager` class
- [ ] Write `tests/test_profile_manager.py` — unit tests
- [ ] Add `set_widget_values()` to `widgets.py`
- [ ] Add profile toolbar to `main.py` (Save, Load dropdown, Delete)
- [ ] Run `pytest tests/` — confirm green
- [ ] Manual test: save profile, verify YAML content
- [ ] Manual test: load profile, verify widgets update
- [ ] Manual test: delete profile, verify file removed

**Resume note:** -
**Open questions:** none
