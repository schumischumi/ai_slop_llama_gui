# Story 2: Command builder + live preview + command parser + paste-to-UI

**Files:**
- Create: `llama_gui/command_builder.py`
- Create: `llama_gui/command_parser.py`
- Modify: `llama_gui/widgets.py` — add widget value collectors
- Modify: `llama_gui/main.py` — add preview panel, paste-to-parse panel, wire live updates

**Context:**
- Story 1 creates `ParamGroup`, `Param`, and the widget factory returning `{param_name: tk.Variable}`
- Widgets have a `param_name` attribute set on them for reverse lookup
- `llama-server` binary is available for testing

**File summaries:**

- `llama_gui/command_builder.py` — `build_command(widgets: dict[str, tk.Variable], params: list[ParamGroup]) -> str`. Iterates widget values, emits appropriate CLI tokens, skips defaults.
- `llama_gui/command_parser.py` — `parse_command(command: str, params: list[ParamGroup]) -> dict[str, str | int | bool]`. Tokenizes, matches against param registry, returns dict.
- `llama_gui/widgets.py` — `collect_widget_values(widgets: dict[str, tk.Variable]) -> dict[str, str | int | bool]`. Reads current values from Tkinter variables.
- `llama_gui/main.py` — adds a `tk.Text` widget for command preview (read-only, single-line), a `tk.Entry` for paste field, a "Parse →" button, and `trace_add` callbacks on all widgets to update preview live.

**Symbols to implement:**

```python
# command_builder.py
def build_command(widgets: dict[str, tk.Variable], groups: list[ParamGroup]) -> str:
    """Build llama-server command string from widget values.
    Omits params whose value matches the default.
    Uses short flags when available and preferred.
    Returns string like 'llama-server -c 8192 -ngl 99 -fa on'
    """

# command_parser.py
def parse_command(command: str, groups: list[ParamGroup]) -> dict[str, str | int | bool]:
    """Parse a llama-server command string into widget values dict.
    Handles both short and long flag forms.
    Skips unrecognised tokens silently.
    Returns dict mapping param long_name to parsed value.
    """

# widgets.py
def collect_widget_values(widgets: dict[str, tk.Variable]) -> dict[str, str | int | bool]:
    """Read current values from Tkinter variables.
    Returns dict mapping param_name to Python value (int/str/bool).
    BooleanVar values come as 0/1 from tkinter, convert to False/True.
    """
```

**build_command rules:**
1. Start with `"llama-server"`
2. For each param (in group order, then param order within group):
   - Skip if value equals default (compare raw values; for bool, skip if True means default)
   - `"flag"` type: if value is True, append `--long-name`
   - `"bool"` type: if True, emit short flag first (if exists), else `--long-name`; if False and negation exists, emit `--no-*`
   - `"int"` type: if non-default, append `--long-name value`
   - `"choice"` type: if non-default, append `--long-name value`
   - `"string"` type: if non-default and non-empty, append `--long-name value`
3. Join with spaces

**parse_command rules:**
1. `shlex.split(command)` to tokenize (handles quoted args)
2. Strip leading `llama-server`
3. Build reverse lookup: `{short_flag: param, long_name: param, ...}` from `groups`
4. Iterate tokens:
   - Token starts with `--` or `-`: look up in reverse map
   - If found and type is `"flag"` or `"bool"` (no value): set value True
   - If found and type has value: next token is the value
   - If `--no-*` variant: set bool to False
   - Unknown: skip
5. Return dict

**Main.py UI additions:**
- Below widget canvas: a `tk.LabelFrame` containing:
  - `tk.Text` (read-only, 1 line, `wrap=tk.NONE`) — command preview
  - `ttk.Button(text="Copy", command=on_copy)` — copies preview to clipboard
  - `tk.Entry` — paste field
  - `ttk.Button(text="Parse →", command=on_parse)` — parses pasted command into UI
- Each widget's `trace_add("write", on_widget_change)` calls `update_preview()`
- `update_preview()`: calls `collect_widget_values()`, calls `build_command()`, updates preview text
- `on_copy()`: `root.clipboard_clear()`, `root.clipboard_append(preview_text)`
- `on_parse()`: reads paste entry, calls `parse_command()`, sets widget values

**Widget value storage for trace:**
- Each created widget stores `widget.param_name = param.long_name`
- `trace_add` callback reads `event_name`, widget reference → looks up `param_name` → collects all values → rebuilds preview

**Verify:**
- `python -m pytest tests/ -v` — all tests pass (new tests for command_builder and command_parser)
- `python main.py` — manual: change widgets, see preview update; paste `llama-server -c 4096 -ngl 33` and click Parse →, verify widgets update

**Commit:** `feat: command builder, command parser, live preview, and paste-to-UI`

**Depends on:** Story 1

**Tasks:**
- [ ] Write `command_builder.py` with `build_command()`
- [ ] Write `command_parser.py` with `parse_command()`
- [ ] Write `tests/test_command_builder.py` — unit tests
- [ ] Write `tests/test_command_parser.py` — unit tests
- [ ] Update `widgets.py` — add `collect_widget_values()`
- [ ] Update `main.py` — add preview panel, paste field, trace callbacks
- [ ] Run `pytest tests/` — confirm green
- [ ] Manual test: live preview updates on widget change
- [ ] Manual test: paste command → widgets update

**Resume note:** -
**Open questions:** none
