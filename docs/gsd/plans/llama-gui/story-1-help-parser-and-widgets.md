# Story 1: Help parser + widget factory + basic UI

**Files:**
- Create: `llama_gui/__init__.py`
- Create: `llama_gui/parser.py`
- Create: `llama_gui/widgets.py`
- Create: `llama_gui/main.py`
- Create: `main.py` (entry shim)
- Create: `requirements.txt`
- Create: `tests/__init__.py`
- Create: `tests/test_parser.py`

**Context:**
- Fresh project, no existing code
- Python 3.14.6, tkinter and pyyaml available
- `llama-server` binary available at `/usr/bin/llama-server`

**File summaries:**

- `llama_gui/__init__.py` — empty, makes it a package
- `llama_gui/parser.py` — `HelpParser` class with `parse()` method. Reads `llama-server --help` stdout, splits into `ParamGroup`s, each containing `Param` objects. Type detection via regex heuristics.
- `llama_gui/widgets.py` — `create_param_widgets()` function. Takes `root: tk.Frame`, `groups: list[ParamGroup]`, returns dict of `{param_name: widget_value}` (e.g. `tk.BooleanVar`, `tk.IntVar`, `tk.StringVar`). Groups widgets in `ttk.LabelFrame` containers.
- `llama_gui/main.py` — `LlamaGuiApp` class. Creates root window, loads params, creates widgets frame. Shows "Help loaded: N params in M groups" in a status bar.
- `main.py` — entry shim: `from llama_gui.main import LlamaGuiApp; LlamaGuiApp().run()`
- `requirements.txt` — `pyyaml`
- `tests/test_parser.py` — unit tests for `HelpParser.parse()` with sample help text

**Symbols to implement:**

```python
class Param:
    long_name: str
    short_flags: list[str]
    description: str
    param_type: str  # "int" | "bool" | "flag" | "choice" | "string"
    default: str | None
    choices: list[str] | None
    has_value: bool

class ParamGroup:
    name: str
    params: list[Param]

class HelpParser:
    def parse(self) -> list[ParamGroup]: ...
```

**Parser rules:**
- Skip lines starting with `WARNING:`, `-----`, `--help`, `--version`, `--usage`, `--completion-bash`, `--cache-list`
- Section headers: `----- common params -----` → group name extracted from between dashes (lowercase, space→underscore)
- Param line format: `<flags> <long-name> [value-placeholder] <description>`
  - Flags: `-t,` or `-tb,` or just `--cpu-strict`
  - Value placeholder: `N`, `FNAME`, `[on|off|auto]`, `{a,b,c}`, `<user>/<model>`
  - Description: rest of line, may continue on next indented lines
- Type detection:
  - `N` or integer pattern in placeholder → `"int"`
  - `[a|b|c]` or `{a,b,c}` → `"choice"`, extract choices from brackets
  - `--flag` with matching `--no-flag` variant in same help output → `"bool"`, pair them
  - Standalone `--flag` (no value placeholder) → `"flag"`
  - Everything else → `"string"`
- Default extraction: regex `(default:\s*([^)]+))` from the line or continuation lines
- Multi-line descriptions: if next line starts with spaces and no `-`, it's a continuation

**Widget mapping (in widgets.py):**
- `"flag"` → `tk.BooleanVar` + `ttk.Checkbutton(text=description)`
- `"bool"` → `tk.BooleanVar` + `ttk.Checkbutton(text=description)` (checked = positive form active)
- `"int"` → `tk.IntVar` + `ttk.Spinbox(from_=0, to=99999, textvariable=var, width=10)`
- `"choice"` → `tk.StringVar` + `ttk.Combobox(textvariable=var, values=choices, state="readonly")`
- `"string"` → `tk.StringVar` + `ttk.Entry(textvariable=var, width=40)`

**create_param_widgets signature:**
```python
def create_param_widgets(root: tk.Frame, groups: list[ParamGroup]) -> dict[str, tk.Variable]:
    """Create all widgets for the given param groups.
    Returns dict mapping param long_name to its Tkinter Variable (IntVar/StrVar/BooleanVar).
    Each widget stores its param name in the 'param_name' attribute for later lookup.
    """
```

**Main app behavior:**
- `LlamaGuiApp.__init__()`: creates `tk.Tk()`, tries `HelpParser().parse()`, shows error dialog if fails, creates `ttk.LabelFrame` per group, calls `create_param_widgets`, places in a `Canvas` + `Scrollbar` for scrolling
- `LlamaGuiApp.run()`: mainloop

**Verify:**
- `python -m pytest tests/test_parser.py -v` — all tests pass
- `python main.py` — window opens with parameter groups and widgets (manual test)

**Commit:** `feat: help parser, widget factory, and basic UI layout`

**Depends on:** none

**Tasks:**
- [ ] Write `parser.py` with `HelpParser` class
- [ ] Write `tests/test_parser.py` with sample help text parsing tests
- [ ] Write `widgets.py` with widget factory
- [ ] Write `main.py` app entry with scrolling canvas layout
- [ ] Write `main.py` entry shim and `requirements.txt`
- [ ] Run `pytest tests/test_parser.py` — confirm green
- [ ] Run `python main.py` — confirm window renders

**Resume note:** -
**Open questions:** none
