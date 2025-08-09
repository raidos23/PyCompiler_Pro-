# PyCompiler Pro++

A modern PySide6 GUI to compile your Python scripts with PyInstaller or Nuitka. It manages a per-project virtual environment, analyzes dependencies, and offers a polished, themeable interface.


## Table of Contents
- [Features](#features)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Theming (Style)](#theming-style)
- [Language (EN/FR)](#language-enfr)
- [Build and Distribution](#build-and-distribution)
- [Dependencies and Compliance](#dependencies-and-compliance)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)


## Features
- Workspace & Files
  - Choose a workspace (project folder)
  - Drag & drop Python files/folders
  - File list management, remove entries, optional filter for main.py/app.py
- Virtual Environment & Tools
  - Automatically creates a venv inside the selected workspace
  - Auto-check/install PyInstaller and Nuitka into that venv
  - Installs project `requirements.txt` (if present) into the workspace venv
- Compilers
  - PyInstaller: common options (onefile, windowed, noconfirm, clean, noupx, debug)
  - Nuitka: key options (onefile, standalone, Windows console toggle, show-progress, plugins, output dir)
- Dependency analysis
  - Detects missing imports and offers to install them (into the workspace venv)
- Logs & stats
  - Live stdout/stderr stream and enriched logs
  - Build statistics (average/total time, GUI process memory)
- Help & compliance
  - Concise bilingual help dialog with license links and notices
- UI/UX
  - Centralized global stylesheet at `ui/style.qss` (current theme: Ivory Luxury)
  - Inline styles removed from the `.ui` to improve maintainability
  - Windows icon support for executables
- Internationalization
  - English/French UI with a language switcher (preference is persisted)


## Quick Start
Requirements: Python 3.9+

```bash
# 1) Clone the repository
git clone <repository-url> PyCompiler_Pro++
cd PyCompiler_Pro++

# 2) Create a venv for the app (optional but recommended)
python -m venv venv
# Windows
venv\Scripts\activate
# Linux
source venv/bin/activate

# 3) Install tool dependencies
pip install -r requirements.txt

# 4) Run the application
python main.py
```


## Usage
1) Open PyCompiler Pro++ and select a workspace (a folder that contains the Python scripts you want to build)
2) The tool will detect (or create) a venv in that workspace and check/install PyInstaller and Nuitka there
3) Add your `.py` files (drag & drop or file chooser) and configure your options (PyInstaller/Nuitka)
4) Optionally run dependency analysis (auto-install missing modules into the workspace venv)
5) Click "Build" to start the compilation(s)

Notes
- If a `requirements.txt` exists at the workspace root, the tool can install it into the workspace venv
- The venv created/used here belongs to the user project being built, not to the GUI itself
- PyInstaller outputs go to `workspace/dist` by default
- For Nuitka, the default output is `scriptname.dist` (or use `--output-dir`)


## Theming (Style)
- Current theme: "Ivory Luxury" — a light, refined theme (ivory/soft gold accents)
- The global stylesheet is at `ui/style.qss`
  - You can tweak colors/spacing and restart the app to apply your custom look
- The app clears inline styles from the `.ui` at startup so the global QSS fully applies


## Language (EN/FR)
- Built-in language switcher ("Choose language")
- The UI, help, and message boxes are bilingual and update immediately
- The selected language is saved in preferences


## Build and Distribution
- You can distribute the tool itself as source (this repository) or as a binary bundle (PyInstaller/Nuitka)
- Tips for bundling the GUI:
  - Include runtime resources: `ui/ui_design.ui`, `ui/style.qss`, `logo/`
  - With PyInstaller, handle resource paths (e.g., `sys._MEIPASS`) or switch to a Qt resource `.qrc`
  - Ship Qt libraries as dynamic libraries and include Qt notices/licenses (LGPL compliance)
- User projects built by PyCompiler Pro++:
  - The workspace venv and PyInstaller/Nuitka are managed within the user’s workspace
  - The resulting executables belong to the user project, not to PyCompiler Pro++


## Dependencies and Compliance
This tool uses:
- PySide6 / Qt (LGPL v3)
- PyInstaller (GPL v2+)
- Nuitka (Apache-2.0)
- psutil (BSD)
- (Optional) PyArmor — not distributed; users may install it if they choose

Important
- PyInstaller and Nuitka are not distributed with the app; they are installed into the user project’s venv when needed
- If you distribute executables built with these tools, include relevant third-party notices/licenses

License links
- PySide6/Qt (LGPL v3): https://www.gnu.org/licenses/lgpl-3.0.html
- PyInstaller (GPL v2+): https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt
- Nuitka (Apache-2.0): https://github.com/Nuitka/Nuitka/blob/develop/LICENSE.txt
- PyArmor (EULA): https://pyarmor.readthedocs.io/en/latest/license.html

Recommended for source/binary distribution
- Provide a `LICENSES/` folder with third-party license texts
- Add an "About" dialog and/or extend the help with versions and credits


## Project Structure
```
PyCompiler_Pro++/
├─ main.py
├─ requirements.txt
├─ LICENSE.txt
├─ ui/
│  ├─ ui_design.ui         # Qt Designer layout
│  └─ style.qss            # global stylesheet (Ivory Luxury)
├─ logo/
│  └─ sidebar_logo.png     # sidebar logo (if present)
└─ utils/
   ├─ worker.py            # main GUI logic
   ├─ init_ui.py           # .ui loading and initialization
   ├─ compiler.py          # PyInstaller/Nuitka build logic & processes
   ├─ dependency_analysis.py# dependency detection and auto-install
   ├─ preferences.py       # user preferences persistence
   ├─ dialogs.py           # progress dialogs
   ├─ sys_dependency.py    # system dependencies for Nuitka
   └─ pyarmor_api.py       # optional PyArmor integration
```


## Roadmap
- Theme switcher (light/dark) at runtime with persistence
- Resource packaging via `.qrc` (optimized for binary distribution)
- More advanced Nuitka options (plugins, data, LTO)
- Example guides for common stacks (PySide6, FastAPI, etc.)


## Contributing
- Issues and PRs are welcome — please include OS, Python version, and logs
- Coding style: keep a consistent PEP8 (black/isort recommended locally)
- Test changes on Windows/Linux if they touch venv/PyInstaller/Nuitka


## License
- PyCompiler Pro++ is released under **GPL-3.0**: https://www.gnu.org/licenses/gpl-3.0.html
- © 2025 PyCompiler_Pro++ by Samuel Amen AGUE

---
For questions, suggestions, or bug reports, open an issue in the repository. Happy compiling!
