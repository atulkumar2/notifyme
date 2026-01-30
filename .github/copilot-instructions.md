# Copilot Instructions

- Run all terminal commands from the project home directory (the workspace root).
- Prefer editing files using apply_patch instead of terminal commands.
- Avoid reformatting unrelated code; keep changes minimal and focused.
- Update or add tests when changing behavior.
- Run linter checks or fix lint issues introduced by changes.
- Keep README in sync with user-facing changes.
- Use existing dependencies when possible; only add new ones if necessary.
- For Python files, ensure compatibility with Python 3.8 or higher.
- All imports should be absolute imports.
- All imports should be sorted according to PEP 8 guidelines.
- All imports should be at the top of the file, after any module comments and docstrings, and before module globals and constants.
- Add module-level docstrings to all Python files that lack them, following the style of existing docstrings in the project.
- When editing documentation files, maintain consistent formatting and style with existing content.
