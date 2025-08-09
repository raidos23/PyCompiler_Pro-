# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2025 Samuel Amen Ague

"""
Gestion des préférences utilisateur pour PyCompiler Pro++.
Inclut la sauvegarde et le chargement des préférences.
La langue sélectionnée par l'utilisateur (clé "language") est enregistrée et restaurée automatiquement.
"""

import json

MAX_PARALLEL = 3
PREFS_FILE = "pyinstaller_gui_prefs.json"


def load_preferences(self):
    try:
        with open(PREFS_FILE, "r", encoding="utf-8") as f:
            prefs = json.load(f)
        self.icon_path = prefs.get("icon_path", None)
        self.opt_onefile_state = prefs.get("opt_onefile", False)
        self.opt_windowed_state = prefs.get("opt_windowed", False)
        self.opt_noconfirm_state = prefs.get("opt_noconfirm", False)
        self.opt_clean_state = prefs.get("opt_clean", False)
        self.opt_noupx_state = prefs.get("opt_noupx", False)
        self.opt_main_only_state = prefs.get("opt_main_only", False)
        self.opt_debug_state = prefs.get("opt_debug", False)
        self.opt_auto_install_state = prefs.get("auto_install", True)
        # self.custom_args_text supprimé (widget supprimé)
        self.output_dir = prefs.get("output_dir", "")
        self.language = prefs.get("language", "English")
    except Exception:
        self.icon_path = None
        self.opt_onefile_state = False
        self.opt_windowed_state = False
        self.opt_noconfirm_state = False
        self.opt_clean_state = False
        self.opt_noupx_state = False
        self.opt_main_only_state = False
        self.opt_debug_state = False
        self.opt_auto_install_state = True
        # self.custom_args_text supprimé (widget supprimé)
        self.output_dir = ""

def save_preferences(self):
    prefs = {
        "icon_path": self.icon_path,
        "opt_onefile": self.opt_onefile.isChecked(),
        "opt_windowed": self.opt_windowed.isChecked(),
        "opt_noconfirm": self.opt_noconfirm.isChecked(),
        "opt_clean": self.opt_clean.isChecked(),
        "opt_noupx": self.opt_noupx.isChecked(),
        "opt_main_only": self.opt_main_only.isChecked(),
        "opt_debug": self.opt_debug.isChecked(),
        "auto_install": self.opt_auto_install.isChecked(),
        # "custom_args" supprimé (widget supprimé)
        "output_dir": self.output_dir_input.text(),
        "language": getattr(self, "current_language", "English"),
    }
    try:
        with open(PREFS_FILE, "w", encoding="utf-8") as f:
            json.dump(prefs, f, indent=4)
    except Exception as e:
        self.log.append(f"⚠️ Impossible de sauvegarder les préférences : {e}")

def update_ui_state(self):
    self.opt_onefile.setChecked(self.opt_onefile_state)
    self.opt_windowed.setChecked(self.opt_windowed_state)
    self.opt_noconfirm.setChecked(self.opt_noconfirm_state)
    self.opt_clean.setChecked(self.opt_clean_state)
    self.opt_noupx.setChecked(self.opt_noupx_state)
    self.opt_main_only.setChecked(self.opt_main_only_state)
    self.opt_debug.setChecked(self.opt_debug_state)
    self.opt_auto_install.setChecked(self.opt_auto_install_state)
    # self.custom_args supprimé (widget supprimé)
    if self.output_dir_input:
        self.output_dir_input.setText(self.output_dir)
    if self.icon_path:
        self.log.append(f"🎨 Icône chargée depuis préférences : {self.icon_path}")
    self.update_command_preview()
