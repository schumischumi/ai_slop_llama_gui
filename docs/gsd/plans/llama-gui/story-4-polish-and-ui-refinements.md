# Story 4: Polish — copy, clear, error handling, collapsible groups

**Files:**
- Modify: `llama_gui/widgets.py` — add collapsible group toggles
- Modify: `llama_gui/main.py` — improve error handling, add clear-all button, refine layout
- Modify: `tests/test_parser.py` — add more edge case tests

**Context:**
- Stories 1-3 provide full functional UI with parser, widgets, command builder/parser, and profiles
- This story refines UX without adding new features

**Changes:**

1. **Collapsible groups** (widgets.py + main.py):
   - Each `ttk.LabelFrame` gets a small "▼" / "▶" toggle button on its right side
   - Toggling shows/hides the frame's children
   - Implementation: each group frame has a `tk.BooleanVar` (collapsed), the toggle button calls `var.set(not var.get())`, a `trace_add` on the var shows/hides children via `pack_forget()` / `pack()`
   - Default: all groups expanded

2. **Clear all button** (main.py):
   - Add `ttk.Button(text="Clear All")` in preview section
   - Calls `set_widget_values(widgets, {param_name: default_value for each param})` — resets all to defaults
   - For params without explicit defaults: flag/bool → False, int → 0, choice → first choice, string → ""

3. **Error handling refinements** (main.py):
   - `HelpParser.parse()` failure: show `messagebox.showerror("llama-server not found", "...")`, continue with empty param list (app still launches)
   - Profile save failure (disk full, permissions): `messagebox.showerror("Save failed", ...)`
   - Profile load failure (corrupt YAML): `messagebox.showerror("Load failed", ...)`
   - Profile delete failure: `messagebox.showerror("Delete failed", ...)`
   - All errors caught in try/except in button callbacks, never crash the app

4. **Better layout** (main.py):
   - Ensure scrollbar works correctly with group frames
   - Add padding/margins for visual separation
   - Make window minimum size reasonable (e.g., 800x600)

**Collapsible group implementation:**

```python
def create_group_frame(container: tk.Frame, group: ParamGroup) -> ttk.LabelFrame:
    """Create a collapsible LabelFrame for the group.
    Returns the LabelFrame and a dict of created widgets.
    """
    frame = ttk.LabelFrame(container, text=group.name, padding=(5, 5, 5, 5))
    # ... create widgets inside frame ...
    
    # Toggle button
    var = tk.BooleanVar(value=False)  # False = expanded (default)
    toggle = ttk.Button(frame, text="▼", width=2, command=lambda v=var: toggle_group(frame, v))
    toggle.pack(side=tk.RIGHT)
    
    def on_toggle(*_):
        if var.get():
            for child in frame.children:
                if child != toggle:
                    child.pack_forget()
        else:
            for child in frame.children:
                if child != toggle:
                    child.pack()
    
    var.trace_add("write", on_toggle)
    return frame, widgets_dict
```

**Clear all implementation:**

```python
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
```

**Verify:**
- `python -m pytest tests/ -v` — all tests pass
- `python main.py` — manual:
  - Toggle groups collapse/expand
  - Clear All resets all widgets to defaults
  - Copy button copies to clipboard
  - Error dialogs appear for bad profile operations
  - Scrollbar works correctly

**Commit:** `refactor: polish UI — collapsible groups, clear-all, error handling`

**Depends on:** Story 3

**Tasks:**
- [ ] Add collapsible toggle to group frames in `widgets.py`
- [ ] Add `clear_all()` function to `widgets.py` or `main.py`
- [ ] Add error handling try/except to all button callbacks in `main.py`
- [ ] Add "Clear All" button in preview section
- [ ] Set window minimum size
- [ ] Run `pytest tests/` — confirm green
- [ ] Manual test: all polish features work

**Resume note:** -
**Open questions:** none
