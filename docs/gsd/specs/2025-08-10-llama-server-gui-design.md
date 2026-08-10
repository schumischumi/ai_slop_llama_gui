#feature

# llama-server GUI (tkinter)

**Goal:** A tkinter-based GUI frontend for `llama-server` that parses `--help` output into interactive UI elements, maintains a live-updating command preview, supports parsing pasted commands into the UI, and saves/loads YAML profiles.

## Scope and Non-Goals

### In scope
- Parse `llama-server --help` at startup into a structured parameter list
- Generate tkinter widgets per parameter type (int, bool, flag, choice, string/path)
- Live-updating command preview as any widget changes
- Paste existing `llama-server` command into UI → widgets update to match
- YAML profiles: save current state, load into UI
- Copy-to-clipboard button
- (Out of scope for design, but planned: "start server" button with output window — can be added later without affecting core design)

### Non-goals (v1)
- No live re-parsing of `--help` (static parse at startup only — per user direction)
- No model download, no chat UI, no server monitoring
- No dark theme or theming
- No keyboard shortcuts

## Architecture

Single-window tkinter application, modular packages:

```
kat-coderv25/
├── llama_gui/
│   ├── __init__.py
│   ├── main.py              # App entry, window layout
│   ├── parser.py            # llama-server --help → structured data
│   ├── command_builder.py   # widget values → command string
│   ├── command_parser.py    # command string → widget values
│   ├── profile_manager.py   # YAML save/load CRUD
│   └── widgets.py           # widget factory + layout logic
├── tests/
│   ├── test_parser.py
│   ├── test_command_builder.py
│   └── test_command_parser.py
├── main.py                  # entry shim: python main.py
└── requirements.txt         # pyyaml (tkinter is stdlib)
```

## Components

### 1. Help Parser (`parser.py`)
One-shot parse of `llama-server --help` output (captured once at startup).

**Data model:**

```python
class Param:
    long_name: str              # e.g. "ctx_size"
    short_flags: list[str]      # e.g. ["-c"]
    negation_flag: str | None   # e.g. "--no-escape" if this is "--escape"
    description: str
    param_type: str             # "int" | "bool" | "flag" | "choice" | "string"
    default: str | None         # raw default string from help
    choices: list[str] | None   # for "choice" type
    has_value: bool             # False for flags/bools without value

class ParamGroup:
    name: str                   # e.g. "common"
    params: list[Param]
```

**Parsing logic:**
- Sections delimited by `----- ... -----` headers
- Each parameter line starts with `-` or `--`
- Extract all flag variants (short and long) from the first token column
- The value placeholder (`N`, `FNAME`, `[on|off|auto]`, `{a,b,c}`) determines type
- `(default: ...)` parenthetical captures default value
- `--no-*` variants are paired with their positive counterparts (e.g. `--escape` / `--no-escape` → single bool)
- Skip `--help`, `--version`, `--usage`
- Multi-line descriptions: join continuation lines

**Type detection heuristic:**
| Pattern in help | type | Example |
|---|---|---|
| `N` (integer) | `int` | `--threads N`, `--ctx-size N` |
| `[a\|b\|c]` or `{a,b,c}` | `choice` | `--flash-attn [on\|off\|auto]` |
| `--flag` / `--no-flag` pair | `bool` | `--escape` / `--no-escape` |
| `--flag` (no value) | `flag` | `--swa-full` |
| `FNAME`, `FILE`, `STRING`, or no placeholder | `string` | `--model FNAME`, `--hf-repo REPO` |

### 2. Widget Factory (`widgets.py`)
Maps `Param` → tkinter widget with appropriate control:

| type | widget | control |
|---|---|---|
| `flag` | `tk.BooleanVar` + `ttk.Checkbutton` | Checked = emit flag |
| `bool` | `tk.BooleanVar` + `ttk.Checkbutton` | Checked = emit positive form |
| `int` | `tk.IntVar` + `ttk.Spinbox` | Spinbox with +/- buttons |
| `choice` | `tk.StringVar` + `ttk.Combobox` | Dropdown with choices |
| `string` | `tk.StringVar` + `ttk.Entry` | Free text field |

Each widget stores a reference to its `Param` object. The factory also groups widgets under collapsible `ttk.LabelFrame` headers (one per `ParamGroup`).

### 3. Command Builder (`command_builder.py`)
Takes `{param_name: raw_value, ...}` → command string.

**Rules:**
- `flag`: emit `--long-name` when value is `True`
- `bool`: emit the short or long positive flag when checked; emit `--no-*` when unchecked (if negation exists)
- `int`: emit `--long-name value`
- `choice`: emit `--long-name value`
- `string`: emit `--long-name value`
- Omit params whose value matches the default (only emit if non-default)
- Handle multi-flag params: `--escape` checked → emit `-e` (short form preferred) or `--escape`

### 4. Command Parser (`command_parser.py`)
Reverse of command builder: `llama-server -c 8192 -ngl 99 --hf-repo foo` → `{ctx_size: 8192, n_gpu_layers: 99, hf_repo: "foo", ...}`.

**Algorithm:**
1. Tokenize: `shlex.split()` handles quoting
2. Strip `llama-server` from the front
3. Iterate tokens:
   - `--long-name` → lookup in param registry → next token is value (unless type is `flag`/`bool` without value)
   - `-X` → lookup short flag → next token is value (unless flag has no value)
   - `--no-*` → lookup, set bool to `False`
   - `--flag` with no next token or next token looks like another flag → emit as flag
4. Unknown tokens: skip silently (future-proofing)

### 5. Profile Manager (`profile_manager.py`)
YAML CRUD in `~/.config/llama-gui/profiles/`.

```python
class ProfileManager:
    def save(name: str, params: dict) -> Path    # save profile
    def load(name: str) -> dict                   # load profile
    def list_profiles() -> list[str]              # list available
    def delete(name: str) -> None                 # remove profile
```

**YAML schema:**
```yaml
name: my-profile
created: 2025-08-10T12:00:00
params:
  ctx_size: 8192
  n_gpu_layers: 99
  hf_repo: unsloth/Qwen3.6-35B-A3B-MTP-GGUF:UD-Q4_K_XL
```

### 6. Main UI (`main.py`)
**Layout:**

```
┌────────────────────────────────────────────────────────────┐
│  [Load ▼] [Save] [Delete]  Profile: "Qwen3-35B"           │
├────────────────────────────────────────────────────────────┤
│  ┌─── Common Parameters ─────────────────────────────┐     │
│  │  Threads: [-100+8-]  Threads Batch: [-100+8-]     │     │
│  │  CPU Mask: [____________]  CPU Range: [__-__]     │     │
│  └───────────────────────────────────────────────────┘     │
│  ┌─── Model ─────────────────────────────────────────┐     │
│  │  HF Repo: [unsloth/Qwen3...               ]       │     │
│  │  Model Path: [/path/to/model.gguf]        [...]   │     │
│  └───────────────────────────────────────────────────┘     │
│  ┌─── Context ───────────────────────────────────────┐    │
│  │  Context Size: [-100+8192-]  Predict: [-100+512-] │    │
│  └───────────────────────────────────────────────────┘    │
│  ... (scrollable, collapsible groups) ...                 │
├────────────────────────────────────────────────────────────┤
│  Command Preview:                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  llama-server -hf unsloth/Qwen3... -c 8192 -ngl 99  │ │
│  │  [Copy] [Clear All]                                  │ │
│  └──────────────────────────────────────────────────────┘ │
│  Paste command to parse: [__________________] [Parse →]  │
└────────────────────────────────────────────────────────────┘
```

**Key behaviors:**
- Groups are `ttk.LabelFrame` widgets that can be collapsed/expanded
- Main parameter area is in a `Canvas` + `Scrollbar` for scrolling
- Command preview updates on every widget `trace_add` callback
- "Copy" copies the preview to clipboard
- Paste field: user pastes, clicks "Parse →", command parser extracts values, all widgets update via their `trace_add` callbacks
- Profile save: prompts for name, calls `ProfileManager.save()`
- Profile load: dropdown of saved profiles, loads into UI (resets non-loaded params to defaults)

## Data Flow

```
startup
    llama-server --help ──→ parser.py ──→ Param[] ──→ widgets factory ──→ tkinter UI
                                                                          │
                                                                  user changes
                                                                          │
                                                              command_builder ──→ preview
                                                                          │
                                              command_parser ←────────────┘
                                              (from paste field)
                                                           │
                                              profile_manager
                                              (save/load)
```

## Error Handling
- `llama-server` not in PATH: show `tkinter.messagebox` warning, use empty param list
- YAML I/O errors: show error dialog, don't crash
- Command parse errors: skip unrecognised tokens silently
- Profile name conflicts: overwrite with confirmation dialog
- Empty profile names: reject

## Testing Approach
- **Unit tests (pytest)**: parser, command_builder, command_parser — all pure logic, no GUI
  - `test_parser.py`: parse sample help text, verify Param objects
  - `test_command_builder.py`: given a param dict, verify command string
  - `test_command_parser.py`: given a command string, verify param dict extraction
  - Edge cases: negation flags, choice params with spaces, quoted arguments, unknown flags
- **Manual testing**: GUI layout, widget behavior, profile save/load — done by hand

## Approximate Story Count
4 stories:
1. Help parser + widget factory + basic UI layout
2. Command builder + live preview + command parser + paste-to-UI
3. Profile system (save/load/delete)
4. Polish: copy button, clear all, error handling, grouping
