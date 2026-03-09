---
description: How to run Python commands in the NotifyMe project
---

The project uses a `uv`-managed virtual environment located at the repo root.

### Python Interpreter
The Python interpreter is located at:
`e:\ws-notifyme\notifyme\.venv\Scripts\python.exe` (Relative: `.venv\Scripts\python.exe`)

### Running Commands
To run scripts or tests, use the absolute path to the virtual environment's python:

```bash
# Example: Running the app
e:\ws-notifyme\notifyme\.venv\Scripts\python.exe -m notifyme_app.notifyme

# Example: Running tests
e:\ws-notifyme\notifyme\.venv\Scripts\python.exe -m pytest
```

### Environment Setup
- **OS**: Windows
- **Package Manager**: uv
- **Venv Path**: `.venv`
