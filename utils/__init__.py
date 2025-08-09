# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2025 Samuel Amen Ague

"""
PyCompiler Pro++ - API utilitaires

Ce projet est open source sous licence GNU GPL v3.0 (voir LICENSE.txt).

Expose :
- Les constantes et fonctions de gestion des préférences utilisateur
- Les fonctions et classes de compilation (PyInstaller/Nuitka)
- Les outils d’analyse de dépendances
- Les dialogues graphiques principaux
- Le point d’entrée principal de l’UI

# Préférences utilisateur
    MAX_PARALLEL, PREFS_FILE, load_preferences, save_preferences, update_ui_state

# Compilation
    compile_all, try_start_processes, start_compilation_process, handle_stdout, handle_stderr,
    handle_finished, try_install_missing_modules, show_error_dialog, cancel_all_compilations,
    build_pyinstaller_command, build_nuitka_command

# Analyse de dépendances
    suggest_missing_dependencies, _install_next_dependency, _on_dep_pip_output, _on_dep_pip_finished

# Dialogues
    ProgressDialog

# UI principale
    PyInstallerWorkspaceGUI
"""

# Préférences utilisateur
from .preferences import (
    MAX_PARALLEL as MAX_PARALLEL,
    PREFS_FILE as PREFS_FILE,
    load_preferences as load_preferences,
    save_preferences as save_preferences,
    update_ui_state as update_ui_state,
)

# Compilation
from .compiler import (
    compile_all as compile_all,
    try_start_processes as try_start_processes,
    start_compilation_process as start_compilation_process,
    handle_stdout as handle_stdout,
    handle_stderr as handle_stderr,
    handle_finished as handle_finished,
    try_install_missing_modules as try_install_missing_modules,
    show_error_dialog as show_error_dialog,
    cancel_all_compilations as cancel_all_compilations,
    build_pyinstaller_command as build_pyinstaller_command,
    build_nuitka_command as build_nuitka_command,
)

# Analyse de dépendances
from .dependency_analysis import (
    suggest_missing_dependencies as suggest_missing_dependencies,
    _install_next_dependency as _install_next_dependency,
    _on_dep_pip_output as _on_dep_pip_output,
    _on_dep_pip_finished as _on_dep_pip_finished,
)

# Dialogues
from .dialogs import (
    ProgressDialog as ProgressDialog,
)

# UI principale
from .worker import PyInstallerWorkspaceGUI as PyInstallerWorkspaceGUI

# API structurée (optionnel)
api = {
    "preferences": {
        "MAX_PARALLEL": MAX_PARALLEL,
        "PREFS_FILE": PREFS_FILE,
        "load_preferences": load_preferences,
        "save_preferences": save_preferences,
        "update_ui_state": update_ui_state,
    },
    "compiler": {
        "compile_all": compile_all,
        "try_start_processes": try_start_processes,
        "start_compilation_process": start_compilation_process,
        "handle_stdout": handle_stdout,
        "handle_stderr": handle_stderr,
        "handle_finished": handle_finished,
        "try_install_missing_modules": try_install_missing_modules,
        "show_error_dialog": show_error_dialog,
        "cancel_all_compilations": cancel_all_compilations,
        "build_pyinstaller_command": build_pyinstaller_command,
        "build_nuitka_command": build_nuitka_command,
    },
    "dependency_analysis": {
        "suggest_missing_dependencies": suggest_missing_dependencies,
        "_install_next_dependency": _install_next_dependency,
        "_on_dep_pip_output": _on_dep_pip_output,
        "_on_dep_pip_finished": _on_dep_pip_finished,
    },
    "dialogs": {
        "ProgressDialog": ProgressDialog,
    },
    "ui": {
        "PyInstallerWorkspaceGUI": PyInstallerWorkspaceGUI,
    }
}

__all__ = [
    # Préférences utilisateur
    "MAX_PARALLEL", "PREFS_FILE", "load_preferences", "save_preferences", "update_ui_state",
    # Compilation
    "compile_all", "try_start_processes", "start_compilation_process", "handle_stdout", "handle_stderr",
    "handle_finished", "try_install_missing_modules", "show_error_dialog", "cancel_all_compilations",
    "build_pyinstaller_command", "build_nuitka_command",
    # Analyse de dépendances
    "suggest_missing_dependencies", "_install_next_dependency", "_on_dep_pip_output", "_on_dep_pip_finished",
    # Dialogues
    "ProgressDialog",
    # UI principale
    "PyInstallerWorkspaceGUI",
    # API structurée
    "api",
]
