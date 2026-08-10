# llama-server GUI Implementation Plan

**Intent:** #feature

**Goal:** A tkinter-based GUI frontend for `llama-server` that parses `--help` output into interactive UI elements, maintains a live-updating command preview, supports parsing pasted commands into the UI, and saves/loads YAML profiles.

**Design:** docs/gsd/specs/2025-08-10-llama-server-gui-design.md

**Target session model:** qwen2.5-coder:12b

**Estimated stories:** 4

**Next story:** 5

## Status Board

| # | Title | Status | Commit |
|---|-------|--------|--------|
| 1 | Help parser + widget factory + basic UI | done | [pending] |
| 2 | Command builder + live preview + command parser + paste-to-UI | done | d2f06b1 |
| 3 | Profile system (save/load/delete) | done | 3730beb |
| 4 | Polish: copy, clear, error handling, collapsible groups | done | 1c72149b7a335310758dbc8c83351a7444acb52e |

## Dependencies

```
Story 1 → Story 2 → Story 3 → Story 4
```

Each story depends on the previous one. Story 1 must establish the parser and widget factory before Story 2 can wire up command building. Story 2 must establish the command builder/parser interface before Story 3's profiles can serialize meaningful state. Story 4 refines what Stories 1-3 build.
