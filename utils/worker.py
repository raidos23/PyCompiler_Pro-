# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2025 Samuel Amen Ague

import sys
import os
import platform
import subprocess
import json
import shutil
from PySide6.QtWidgets import (
    QWidget, QFileDialog,
    QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QDropEvent, QPixmap

from .dialogs import ProgressDialog

class PyInstallerWorkspaceGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCompiler Pro++")
        self.setGeometry(100, 100, 1280, 720)
        self.setAcceptDrops(True)

        self.workspace_dir = None
        self.python_files = []
        self.icon_path = None
        self.selected_files = []
        self.venv_path_manuel = None

        self.processes = []
        self.queue = []
        self.current_compiling = set()
        self._closing = False
        # Références aux QProcess pour arrêt propre lors de la fermeture
        self._venv_create_process = None
        self._venv_install_pyinstaller_process = None
        self._venv_install_nuitka_process = None
        self._venv_check_process = None
        self._venv_check_install_process = None
        self._req_install_process = None

        self.load_preferences()
        self.init_ui()
        # Appliquer la langue des préférences si présente, sinon anglais
        lang = getattr(self, "language", "English")
        self.apply_language(lang)
        self.update_ui_state()

    from .init_ui import init_ui

    def add_pyinstaller_data(self):
        from PySide6.QtWidgets import QFileDialog, QInputDialog
        import os
        from PySide6.QtCore import QDir
        choix, ok = QInputDialog.getItem(self, "Type d'inclusion", "Inclure un fichier ou un dossier ?", ["Fichier", "Dossier"], 0, False)
        if not ok:
            return
        if choix == "Fichier":
            file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier à inclure avec PyInstaller")
            if file_path:
                dest, ok = QInputDialog.getText(self, "Chemin de destination", "Chemin de destination dans l'exécutable :", text=os.path.basename(file_path))
                if ok and dest:
                    self.pyinstaller_data.append((file_path, dest))
                    if hasattr(self, 'log'):
                        self.log.append(f"Fichier ajouté à PyInstaller : {file_path} => {dest}")
        elif choix == "Dossier":
            dir_path = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier à inclure avec PyInstaller", QDir.homePath())
            if dir_path:
                dest, ok = QInputDialog.getText(self, "Chemin de destination", "Chemin de destination dans l'exécutable :", text=os.path.basename(dir_path))
                if ok and dest:
                    self.pyinstaller_data.append((dir_path, dest))
                    if hasattr(self, 'log'):
                        self.log.append(f"Dossier ajouté à PyInstaller : {dir_path} => {dest}")

    def add_nuitka_data_file(self):
        from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox
        import os
        from PySide6.QtCore import QDir
        choix, ok = QInputDialog.getItem(self, "Type d'inclusion", "Inclure un fichier ou un dossier ?", ["Fichier", "Dossier"], 0, False)
        if not ok:
            return
        if not hasattr(self, 'nuitka_data_files'):
            self.nuitka_data_files = []
        if not hasattr(self, 'nuitka_data_dirs'):
            self.nuitka_data_dirs = []
        if choix == "Fichier":
            file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier à inclure avec Nuitka")
            if file_path:
                dest, ok = QInputDialog.getText(self, "Chemin de destination", "Chemin de destination dans l'exécutable :", text=os.path.basename(file_path))
                if ok and dest:
                    self.nuitka_data_files.append((file_path, dest))
                    if hasattr(self, 'log'):
                        self.log.append(f"Fichier ajouté à Nuitka : {file_path} => {dest}")
        elif choix == "Dossier":
            dir_path = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier à inclure avec Nuitka", QDir.homePath())
            if dir_path:
                dest, ok = QInputDialog.getText(self, "Chemin de destination", "Chemin de destination dans l'exécutable :", text=os.path.basename(dir_path))
                if ok and dest:
                    self.nuitka_data_dirs.append((dir_path, dest))
                    if hasattr(self, 'log'):
                        self.log.append(f"Dossier ajouté à Nuitka : {dir_path} => {dest}")

    def dragEnterEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        added = 0
        for url in urls:
            path = url.toLocalFile()
            if os.path.isdir(path):
                added += self.add_py_files_from_folder(path)
            elif path.endswith(".py"):
                # Vérifie que le fichier est dans workspace (si défini)
                if self.workspace_dir and not os.path.commonpath([path, self.workspace_dir]) == self.workspace_dir:
                    self.log.append(f"⚠️ Ignoré (hors workspace): {path}")
                    continue
                if path not in self.python_files:
                    self.python_files.append(path)
                    relative_path = os.path.relpath(path, self.workspace_dir) if self.workspace_dir else path
                    self.file_list.addItem(relative_path)
                    added += 1
        self.log.append(f"✅ {added} fichier(s) ajouté(s) via drag & drop.")
        self.update_command_preview()

    def add_py_files_from_folder(self, folder):
        count = 0
        for root, _, files in os.walk(folder):
            for f in files:
                if f.endswith(".py"):
                    full_path = os.path.join(root, f)
                    if self.workspace_dir and not os.path.commonpath([full_path, self.workspace_dir]) == self.workspace_dir:
                        continue
                    if full_path not in self.python_files:
                        self.python_files.append(full_path)
                        relative_path = os.path.relpath(full_path, self.workspace_dir) if self.workspace_dir else full_path
                        self.file_list.addItem(relative_path)
                        count += 1
        return count

    def select_workspace(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir le dossier du projet")
        if folder:
            self.workspace_dir = folder
            self.label_folder.setText(f"Dossier sélectionné : {folder}")
            self.python_files.clear()
            self.file_list.clear()
            self.add_py_files_from_folder(folder)
            self.selected_files.clear()
            self.update_command_preview()
            self.save_preferences()

            # -- Ajout automatique --
            self.create_venv_if_needed(folder)
            venv_path = os.path.join(folder, "venv")
            if not os.path.isdir(venv_path):
                self.log.append("Aucun dossier venv détecté dans ce workspace.")
            else:
                self.log.append("Dossier venv détecté.")
                # Vérification/installation auto de nuitka et pyinstaller (asynchrone avec ProgressDialog)
                pip_exe = os.path.join(venv_path, "bin", "pip")
                self._venv_check_pkgs = ["pyinstaller", "nuitka"]
                self._venv_check_index = 0
                self._venv_check_pip_exe = pip_exe
                self._venv_check_path = venv_path
                self.venv_check_progress = ProgressDialog("Vérification du venv", self)
                self.venv_check_progress.set_message("Vérification de PyInstaller...")
                self.venv_check_progress.set_progress(0, 2)
                self.venv_check_progress.show()
                self._check_next_venv_pkg()

    def _check_next_venv_pkg(self):
        if self._venv_check_index >= len(self._venv_check_pkgs):
            self.venv_check_progress.set_message("Vérification terminée.")
            self.venv_check_progress.set_progress(2, 2)
            self.venv_check_progress.close()
            # Installer les dépendances du projet si un requirements.txt est présent
            if self.workspace_dir:
                self.install_requirements_if_needed(self.workspace_dir)
            return
        pkg = self._venv_check_pkgs[self._venv_check_index]
        process = QProcess(self)
        self._venv_check_process = process
        process.setProgram(self._venv_check_pip_exe)
        process.setArguments(["show", pkg])
        process.setWorkingDirectory(self._venv_check_path)
        process.finished.connect(lambda code, status: self._on_venv_pkg_checked(process, code, status, pkg))
        process.start()

    def _on_venv_pkg_checked(self, process, code, status, pkg):
        if code == 0:
            self.log.append(f"✅ {pkg} déjà installé dans le venv.")
            self._venv_check_index += 1
            self.venv_check_progress.set_message(f"Vérification de {self._venv_check_pkgs[self._venv_check_index] if self._venv_check_index < len(self._venv_check_pkgs) else ''}...")
            self.venv_check_progress.set_progress(self._venv_check_index, 2)
            self._check_next_venv_pkg()
        else:
            self.log.append(f"📦 Installation automatique de {pkg} dans le venv...")
            self.venv_check_progress.set_message(f"Installation de {pkg}...")
            self.venv_check_progress.progress.setRange(0, 0)
            process2 = QProcess(self)
            self._venv_check_install_process = process2
            process2.setProgram(self._venv_check_pip_exe)
            process2.setArguments(["install", pkg])
            process2.setWorkingDirectory(self._venv_check_path)
            process2.readyReadStandardOutput.connect(lambda: self._on_venv_check_output(process2))
            process2.readyReadStandardError.connect(lambda: self._on_venv_check_output(process2, error=True))
            process2.finished.connect(lambda code2, status2: self._on_venv_pkg_installed(process2, code2, status2, pkg))
            process2.start()

    def _on_venv_check_output(self, process, error=False):
        if getattr(self, "_closing", False):
            return
        data = process.readAllStandardError().data().decode() if error else process.readAllStandardOutput().data().decode()
        if hasattr(self, 'venv_check_progress') and self.venv_check_progress:
            lines = data.strip().splitlines()
            if lines:
                self.venv_check_progress.set_message(lines[-1])
        self._safe_log(data)

    def _on_venv_pkg_installed(self, process, code, status, pkg):
        if getattr(self, "_closing", False):
            return
        if code == 0:
            self._safe_log(f"✅ {pkg} installé dans le venv.")
        else:
            self._safe_log(f"❌ Erreur installation {pkg} (code {code})")
        self._venv_check_index += 1
        self.venv_check_progress.progress.setRange(0, 2)
        self.venv_check_progress.set_progress(self._venv_check_index, 2)
        self._check_next_venv_pkg()


    def select_venv_manually(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir un dossier venv", "")
        if folder:
            self.venv_path_manuel = folder
            self.venv_label.setText(f"Venv sélectionné : {folder}")
        else:
            self.venv_path_manuel = None
            self.venv_label.setText("Venv sélectionné : Aucun")

            


    def create_venv_if_needed(self, path):
        venv_path = os.path.join(path, "venv")
        if not os.path.exists(venv_path):
            self._safe_log("🔧 Aucun venv trouvé, création automatique...")
            try:
                # Recherche d'un python embarqué à côté de l'exécutable
                python_candidate = None
                exe_dir = os.path.dirname(sys.executable)
                # Windows: python.exe, Linux/Mac: python3 ou python
                candidates = [
                    os.path.join(exe_dir, "python.exe"),
                    os.path.join(exe_dir, "python3"),
                    os.path.join(exe_dir, "python"),
                    os.path.join(exe_dir, "python_embedded", "python.exe"),
                    os.path.join(exe_dir, "python_embedded", "python3"),
                    os.path.join(exe_dir, "python_embedded", "python"),
                ]
                # Recherche également les interpréteurs système disponibles dans le PATH
                path_candidates = []
                try:
                    if platform.system() == "Windows":
                        w = shutil.which("py")
                        if w:
                            path_candidates.append(w)
                    for name in ("python3", "python"):
                        w = shutil.which(name)
                        if w:
                            path_candidates.append(w)
                except Exception:
                    pass
                for c in path_candidates:
                    if c not in candidates:
                        candidates.append(c)
                for c in candidates:
                    if os.path.isfile(c):
                        python_candidate = c
                        break
                if not python_candidate:
                    python_candidate = sys.executable
                # Journalisation du type d'interpréteur détecté
                base = os.path.basename(python_candidate).lower()
                if python_candidate.startswith(exe_dir) or "python_embedded" in python_candidate:
                    self.log.append(f"➡️ Utilisation de l'interpréteur Python embarqué : {python_candidate}")
                elif base in ("py", "py.exe") or shutil.which(base):
                    self.log.append(f"➡️ Utilisation de l'interpréteur système : {python_candidate}")
                else:
                    self.log.append(f"➡️ Utilisation de sys.executable : {python_candidate}")
                self.venv_progress_dialog = ProgressDialog("Création de l'environnement virtuel", self)
                self.venv_progress_dialog.set_message("Création du venv...")
                process = QProcess(self)
                self._venv_create_process = process
                process.setProgram(python_candidate)
                args = ["-m", "venv", venv_path]
                # Si l'on utilise le launcher Windows 'py', forcer Python 3 avec -3
                if base in ("py", "py.exe"):
                    args = ["-3"] + args
                process.setArguments(args)
                process.setWorkingDirectory(path)
                process.readyReadStandardOutput.connect(lambda: self._on_venv_output(process))
                process.readyReadStandardError.connect(lambda: self._on_venv_output(process, error=True))
                process.finished.connect(lambda code, status: self._on_venv_created(process, code, status, venv_path))
                self._venv_progress_lines = 0
                self.venv_progress_dialog.show()
                process.start()
            except Exception as e:
                self._safe_log(f"❌ Échec de création du venv ou installation de PyInstaller : {e}")

    def _on_venv_output(self, process, error=False):
        if getattr(self, "_closing", False):
            return
        data = process.readAllStandardError().data().decode() if error else process.readAllStandardOutput().data().decode()
        if hasattr(self, 'venv_progress_dialog') and self.venv_progress_dialog:
            lines = data.strip().splitlines()
            if lines:
                self.venv_progress_dialog.set_message(lines[-1])
            self._venv_progress_lines += len(lines)
            self.venv_progress_dialog.set_progress(self._venv_progress_lines, 0)
        self._safe_log(data)

    def _on_venv_created(self, process, code, status, venv_path):
        if getattr(self, "_closing", False):
            return
        if code == 0:
            self._safe_log("✅ Environnement virtuel créé avec succès.")
            if hasattr(self, 'venv_progress_dialog') and self.venv_progress_dialog:
                self.venv_progress_dialog.set_message("Installation de PyInstaller...")
                self.venv_progress_dialog.set_progress(0, 2)
            # Installer PyInstaller dans le venv, puis Nuitka
            pip_exe = os.path.join(venv_path, "Scripts" if platform.system() == "Windows" else "bin", "pip")
            self._venv_pip_exe = pip_exe
            self._venv_path = venv_path
            self._install_pyinstaller_then_nuitka()
        else:
            self._safe_log(f"❌ Échec de création du venv (code {code})")
            if hasattr(self, 'venv_progress_dialog') and self.venv_progress_dialog:
                self.venv_progress_dialog.set_message("Erreur lors de la création du venv.")
                self.venv_progress_dialog.close()
        QApplication.processEvents()

    def _install_pyinstaller_then_nuitka(self):
        # Installe PyInstaller
        process = QProcess(self)
        self._venv_install_pyinstaller_process = process
        process.setProgram(self._venv_pip_exe)
        process.setArguments(["install", "pyinstaller"])
        process.setWorkingDirectory(self._venv_path)
        process.readyReadStandardOutput.connect(lambda: self._on_venv_output(process))
        process.readyReadStandardError.connect(lambda: self._on_venv_output(process, error=True))
        process.finished.connect(lambda code, status: self._on_pyinstaller_then_nuitka_installed(process, code, status, step=1))
        process.start()

    def _on_pyinstaller_then_nuitka_installed(self, process, code, status, step):
        if getattr(self, "_closing", False):
            return
        if step == 1:
            if code == 0:
                self._safe_log("✅ PyInstaller installé dans le venv.")
                if hasattr(self, 'venv_progress_dialog') and self.venv_progress_dialog:
                    self.venv_progress_dialog.set_message("Installation de Nuitka...")
                    self.venv_progress_dialog.set_progress(1, 2)
                # Installe Nuitka
                process2 = QProcess(self)
                self._venv_install_nuitka_process = process2
                process2.setProgram(self._venv_pip_exe)
                process2.setArguments(["install", "nuitka"])
                process2.setWorkingDirectory(self._venv_path)
                process2.readyReadStandardOutput.connect(lambda: self._on_venv_output(process2))
                process2.readyReadStandardError.connect(lambda: self._on_venv_output(process2, error=True))
                process2.finished.connect(lambda code2, status2: self._on_pyinstaller_then_nuitka_installed(process2, code2, status2, step=2))
                process2.start()
            else:
                self._safe_log(f"❌ Échec installation PyInstaller dans le venv (code {code})")
                if hasattr(self, 'venv_progress_dialog') and self.venv_progress_dialog:
                    self.venv_progress_dialog.set_message("Erreur lors de l'installation de PyInstaller.")
                    self.venv_progress_dialog.close()
        elif step == 2:
            if code == 0:
                self._safe_log("✅ Nuitka installé dans le venv.")
                if hasattr(self, 'venv_progress_dialog') and self.venv_progress_dialog:
                    self.venv_progress_dialog.set_message("Installation terminée.")
                    self.venv_progress_dialog.set_progress(2, 2)
            else:
                self._safe_log(f"❌ Échec installation Nuitka dans le venv (code {code})")
                if hasattr(self, 'venv_progress_dialog') and self.venv_progress_dialog:
                    self.venv_progress_dialog.set_message("Erreur lors de l'installation de Nuitka.")
            if hasattr(self, 'venv_progress_dialog') and self.venv_progress_dialog:
                self.venv_progress_dialog.close()
            # Installer les dépendances du projet à partir de requirements.txt si présent
            self.install_requirements_if_needed(os.path.dirname(self._venv_path))
        QApplication.processEvents()

    def install_requirements_if_needed(self, path):
        req_path = os.path.join(path, "requirements.txt")
        if os.path.exists(req_path):
            self._safe_log("📦 Installation des dépendances à partir de requirements.txt...")
            pip_exe = os.path.join(path, "venv", "Scripts" if platform.system() == "Windows" else "bin", "pip")
            try:
                self.progress_dialog = ProgressDialog("Installation des dépendances", self)
                self.progress_dialog.set_message("Démarrage de l'installation des dépendances...")
                process = QProcess(self)
                self._req_install_process = process
                process.setProgram(pip_exe)
                process.setArguments(["install", "-r", req_path])
                process.setWorkingDirectory(path)
                process.readyReadStandardOutput.connect(lambda: self._on_pip_output(process))
                process.readyReadStandardError.connect(lambda: self._on_pip_output(process, error=True))
                process.finished.connect(lambda code, status: self._on_pip_finished(process, code, status))
                self._pip_progress_lines = 0
                self.progress_dialog.show()
                process.start()
                # NE PAS bloquer ici, la fermeture se fait dans _on_pip_finished
            except Exception as e:
                self.log.append(f"❌ Échec installation requirements.txt : {e}")

    def _on_pip_output(self, process, error=False):
        if getattr(self, "_closing", False):
            return
        data = process.readAllStandardError().data().decode() if error else process.readAllStandardOutput().data().decode()
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            # Affiche la dernière ligne reçue
            lines = data.strip().splitlines()
            if lines:
                self.progress_dialog.set_message(lines[-1])
            self._pip_progress_lines += len(lines)
            # Simule une progression (pip ne donne pas de %)
            self.progress_dialog.set_progress(self._pip_progress_lines, 0)
        self._safe_log(data)

    def _on_pip_finished(self, process, code, status):
        if getattr(self, "_closing", False):
            return
        if code == 0:
            self._safe_log("✅ requirements.txt installé.")
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.set_message("Installation terminée.")
        else:
            self._safe_log(f"❌ Échec installation requirements.txt (code {code})")
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.set_message("Erreur lors de l'installation.")
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
        QApplication.processEvents()

    
    
    def select_files_manually(self):
        if not self.workspace_dir:
            QMessageBox.warning(self, self.tr("Attention", "Warning"), self.tr("Veuillez d'abord sélectionner un dossier workspace.", "Please select a workspace folder first."))
            return
        files, _ = QFileDialog.getOpenFileNames(self, "Sélectionner des fichiers Python", self.workspace_dir, "Python Files (*.py)")
        if files:
            valid_files = []
            for f in files:
                if os.path.commonpath([f, self.workspace_dir]) == self.workspace_dir:
                    valid_files.append(f)
                else:
                    QMessageBox.warning(self, self.tr("Fichier hors workspace", "File outside workspace"), self.tr(f"Le fichier {f} est en dehors du workspace et sera ignoré.", f"The file {f} is outside the workspace and will be ignored."))
            if valid_files:
                self.selected_files = valid_files
                self.log.append(f"✅ {len(valid_files)} fichier(s) sélectionné(s) manuellement.\n")
                self.update_command_preview()

    def on_main_only_changed(self):
        if self.opt_main_only.isChecked():
            mains = [f for f in self.python_files if os.path.basename(f) in ("main.py", "app.py")]
            if len(mains) > 1:
                QMessageBox.information(self, self.tr("Info", "Info"), self.tr(f"{len(mains)} fichiers main.py ou app.py détectés dans le workspace.", f"{len(mains)} main.py or app.py files detected in the workspace."))
        self.update_command_preview()

    def select_icon(self):
        file, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier .ico", "", "Icon Files (*.ico)")
        if file:
            self.icon_path = file
            self.log.append(f"🎨 Icône sélectionnée : {file}")
            pixmap = QPixmap(file)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(64,64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                self.icon_preview.setPixmap(scaled_pixmap)
                self.icon_preview.show()
            else:
                self.icon_preview.hide()
        else:
            self.icon_preview.hide()    

            self.update_command_preview()
            self.save_preferences()

    from .compiler import build_nuitka_command, build_pyinstaller_command

    def select_nuitka_icon(self):
        from PySide6.QtWidgets import QFileDialog
        import platform
        if platform.system() != "Windows":
            return
        file, _ = QFileDialog.getOpenFileName(self, "Choisir une icône .ico pour Nuitka", "", "Icon Files (*.ico)")
        if file:
            self.nuitka_icon_path = file
            self.log.append(f"🎨 Icône Nuitka sélectionnée : {file}")
        else:
            self.nuitka_icon_path = None
        self.update_command_preview()
    
    def add_remove_file_button(self):
        # Cette méthode n'est plus nécessaire car le bouton est déjà dans le .ui
        pass

    def remove_selected_file(self):
        selected_items = self.file_list.selectedItems()
        for item in selected_items:
            # Récupère le chemin relatif affiché
            rel_path = item.text()
            # Construit le chemin absolu si workspace_dir défini
            abs_path = os.path.join(self.workspace_dir, rel_path) if self.workspace_dir else rel_path
            # Supprime de python_files si présent
            if abs_path in self.python_files:
                self.python_files.remove(abs_path)
            # Supprime de selected_files si présent
            if abs_path in self.selected_files:
                self.selected_files.remove(abs_path)
            # Supprime l'item de la liste graphique
            self.file_list.takeItem(self.file_list.row(item))
        self.update_command_preview()

    def show_help_dialog(self):
        if getattr(self, "current_language", "Français") == "English":
            help_text = (
                "<b>Help PyCompiler Pro++</b><br>"
                "<ul>"
                "<li>1) Select the Workspace folder and add your .py files.</li>"
                "<li>2) Configure options (PyInstaller/Nuitka).</li>"
                "<li>3) Start the build and follow the logs.</li>"
                "</ul>"
                "<b>Environment</b><br>"
                "<ul>"
                "<li>A virtual environment (venv) can be created/used automatically in the project (or selected manually).</li>"
                "<li>requirements.txt is installed if present.</li>"
                "</ul>"
                "<b>External tools</b><br>"
                "<ul>"
                "<li>PyInstaller and Nuitka are not distributed with this software; they are installed in the venv if needed.</li>"
                "<li>This software can use PyArmor if it is installed on the machine.</li>"
                "</ul>"
                "<b>Licenses (links)</b><br>"
                "<ul>"
                "<li>PyInstaller (GPL v2+): <a href='https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt'>github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt</a></li>"
                "<li>Nuitka (Apache-2.0): <a href='https://github.com/Nuitka/Nuitka/blob/develop/LICENSE.txt'>github.com/Nuitka/Nuitka/blob/develop/LICENSE.txt</a></li>"
                "<li>PyArmor (EULA): <a href='https://pyarmor.readthedocs.io/en/latest/license.html'>pyarmor.readthedocs.io/en/latest/license.html</a></li>"
                "<li>PySide6/Qt (LGPL v3): <a href='https://www.gnu.org/licenses/lgpl-3.0.html'>gnu.org/licenses/lgpl-3.0.html</a></li>"
                "<li>PyCompiler Pro++ (GPL-3.0): <a href='https://www.gnu.org/licenses/gpl-3.0.html'>gnu.org/licenses/gpl-3.0.html</a></li>"
                "</ul>"
                "<br><b>License note</b>: This software is distributed under GPL-3.0; any redistributed modification must be made available to the community under GPL-3.0 (see: <a href='https://www.gnu.org/licenses/gpl-3.0.html'>gnu.org/licenses/gpl-3.0.html</a>)."
                "<br><br>© 2025 PyCompiler_Pro++ by Samuel Amen AGUE"
            )
        else:
            help_text = (
                "<b>Aide PyCompiler Pro++</b><br>"
                "<ul>"
                "<li>1) Sélectionnez le dossier Workspace et ajoutez vos fichiers .py.</li>"
                "<li>2) Configurez les options (PyInstaller/Nuitka).</li>"
                "<li>3) Lancez la compilation et suivez les logs.</li>"
                "</ul>"
                "<b>Environnement</b><br>"
                "<ul>"
                "<li>Un venv peut être créé/utilisé automatiquement dans le projet (ou sélection manuelle).</li>"
                "<li>requirements.txt est installé s'il est présent.</li>"
                "</ul>"
                "<b>Outils externes</b><br>"
                "<ul>"
                "<li>PyInstaller et Nuitka ne sont pas distribués avec ce logiciel; ils sont installés dans le venv si nécessaire.</li>"
                "<li>Ce logiciel peut utiliser PyArmor s'il est installé sur la machine.</li>"
                "</ul>"
                "<b>Licences (liens)</b><br>"
                "<ul>"
                "<li>PyInstaller (GPL v2+): <a href='https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt'>github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt</a></li>"
                "<li>Nuitka (Apache-2.0): <a href='https://github.com/Nuitka/Nuitka/blob/develop/LICENSE.txt'>github.com/Nuitka/Nuitka/blob/develop/LICENSE.txt</a></li>"
                "<li>PyArmor (EULA): <a href='https://pyarmor.readthedocs.io/en/latest/license.html'>pyarmor.readthedocs.io/en/latest/license.html</a></li>"
                "<li>PySide6/Qt (LGPL v3): <a href='https://www.gnu.org/licenses/lgpl-3.0.html'>gnu.org/licenses/lgpl-3.0.html</a></li>"
                "<li>PyCompiler Pro++ (GPL-3.0): <a href='https://www.gnu.org/licenses/gpl-3.0.html'>gnu.org/licenses/gpl-3.0.html</a></li>"
                "</ul>"
                "<br><b>Note licence</b>: Ce logiciel est distribué sous licence GPL-3.0; toute modification redistribuée doit être mise à disposition de la communauté sous GPL-3.0 (voir: <a href='https://www.gnu.org/licenses/gpl-3.0.html'>gnu.org/licenses/gpl-3.0.html</a>)."
                "<br><br>© 2025 PyCompiler_Pro++ by Samuel Amen AGUE"
            )
        dlg = QMessageBox(self)
        dlg.setWindowTitle(self.tr("Aide", "Help"))
        dlg.setTextFormat(Qt.TextFormat.RichText)
        dlg.setText(help_text)
        dlg.setIcon(QMessageBox.Icon.Information)
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.exec()

    def export_config(self):
        file, _ = QFileDialog.getSaveFileName(self, "Exporter la configuration", "", "JSON Files (*.json)")
        if file:
            if not file.endswith(".json"):
                file += ".json"
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
            }
            try:
                with open(file, "w", encoding="utf-8") as f:
                    json.dump(prefs, f, indent=4)
                self.log.append(f"✅ Configuration exportée : {file}")
            except Exception as e:
                self.log.append(f"❌ Erreur export configuration : {e}")

    def import_config(self):
        file, _ = QFileDialog.getOpenFileName(self, "Importer la configuration", "", "JSON Files (*.json)")
        if file:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    prefs = json.load(f)
                self.icon_path = prefs.get("icon_path", None)
                self.opt_onefile.setChecked(prefs.get("opt_onefile", False))
                self.opt_windowed.setChecked(prefs.get("opt_windowed", False))
                self.opt_noconfirm.setChecked(prefs.get("opt_noconfirm", False))
                self.opt_clean.setChecked(prefs.get("opt_clean", False))
                self.opt_noupx.setChecked(prefs.get("opt_noupx", False))
                self.opt_main_only.setChecked(prefs.get("opt_main_only", False))
                self.opt_debug.setChecked(prefs.get("opt_debug", False))
                self.opt_auto_install.setChecked(prefs.get("auto_install", True))
                # self.custom_args supprimé (widget supprimé)
                self.output_dir_input.setText(prefs.get("output_dir", ""))
                self.log.append(f"✅ Configuration importée : {file}")
                self.update_command_preview()
            except Exception as e:
                self.log.append(f"❌ Erreur import configuration : {e}")

    def check_versions(self):
        python_version = platform.python_version()
        try:
            import PyInstaller
            pyinstaller_version = PyInstaller.__version__
        except Exception:
            pyinstaller_version = "Non installé"
        self.log.append(f"Version Python : {python_version}")
        self.log.append(f"Version PyInstaller : {pyinstaller_version}")

    def update_command_preview(self):
        # Aperçu de commande désactivé: widget label_cmd retiré
        # Résumé des options
        summary = []
        if self.opt_onefile.isChecked(): summary.append("Onefile")
        if self.opt_windowed.isChecked(): summary.append("Windowed")
        if self.opt_noconfirm.isChecked(): summary.append("Noconfirm")
        if self.opt_clean.isChecked(): summary.append("Clean")
        if self.opt_noupx.isChecked(): summary.append("NoUPX")
        if self.opt_debug.isChecked(): summary.append("Debug")
        if self.opt_auto_install.isChecked(): summary.append("Auto-install modules")
        if self.icon_path: summary.append("Icone")
        if self.output_dir_input.text().strip(): summary.append(f"Sortie: {self.output_dir_input.text().strip()}")
        # Widget options_summary supprimé; plus de mise à jour de résumé visuel

    from .compiler import compile_all, try_start_processes, try_install_missing_modules, handle_finished, handle_stderr, handle_stdout, show_error_dialog, start_compilation_process, cancel_all_compilations
    def set_controls_enabled(self, enabled):
        self.btn_build_all.setEnabled(enabled)
        self.btn_cancel_all.setEnabled(not enabled)
        self.btn_select_folder.setEnabled(enabled)
        self.btn_select_icon.setEnabled(enabled)
        self.btn_select_files.setEnabled(enabled)
        self.btn_remove_file.setEnabled(enabled)
        self.btn_export_config.setEnabled(enabled)
        self.btn_import_config.setEnabled(enabled)
        self.venv_button.setEnabled(enabled)
        self.output_dir_input.setEnabled(enabled)
        # Désactive toutes les cases à cocher d'options
        for checkbox in [self.opt_onefile, self.opt_windowed, self.opt_noconfirm,
                         self.opt_clean, self.opt_noupx, self.opt_main_only, self.opt_debug,
                         self.opt_auto_install, self.opt_silent_errors]:
            checkbox.setEnabled(enabled)
        # self.custom_args supprimé (widget supprimé)

    def open_dist_folder(self):
        dist_dir = os.path.join(self.workspace_dir, "dist")
        if os.path.exists(dist_dir):
            try:
                system = platform.system()
                if system == "Windows":
                    os.startfile(dist_dir)
                elif system == "Linux":
                    subprocess.run(["xdg-open", dist_dir])
                elif system == "Darwin":
                    subprocess.run(["open", dist_dir])
            except Exception as e:
                self.log.append(f"⚠️ Impossible d'ouvrir le dossier dist : {e}")

    def open_nuitka_dist_folder(self, script_path, output_dir=None):
        """
        Ouvre le dossier de sortie Nuitka pour le script donné.
        - script_path : chemin du script compilé
        - output_dir : dossier de sortie Nuitka (--output-dir), optionnel
        """
        try:
            if output_dir and os.path.isdir(output_dir):
                target_dir = output_dir
            else:
                base = os.path.splitext(os.path.basename(script_path))[0]
                target_dir = os.path.join(os.path.dirname(script_path), f"{base}.dist")
            if os.path.isdir(target_dir):
                system = platform.system()
                if system == "Windows":
                    os.startfile(target_dir)
                elif system == "Linux":
                    subprocess.run(["xdg-open", target_dir])
                elif system == "Darwin":
                    subprocess.run(["open", target_dir])
            else:
                self.log.append(f"❌ Dossier Nuitka introuvable : {target_dir}")
        except Exception as e:
            self.log.append(f"⚠️ Impossible d'ouvrir le dossier Nuitka : {e}")

    from .preferences import load_preferences, save_preferences, update_ui_state
    def show_statistics(self):
        import psutil
        import time
        # Statistiques de compilation
        if not hasattr(self, '_compilation_times') or not self._compilation_times:
            QMessageBox.information(self, self.tr("Statistiques", "Statistics"), self.tr("Aucune compilation récente à analyser.", "No recent builds to analyze."))
            return
        total_files = len(self._compilation_times)
        total_time = sum(self._compilation_times.values())
        avg_time = total_time / total_files if total_files else 0
        try:
            mem_info = psutil.Process().memory_info().rss / (1024*1024)
        except Exception:
            mem_info = None
        msg = f"<b>Statistiques de compilation</b><br>"
        msg += f"Fichiers compilés : {total_files}<br>"
        msg += f"Temps total : {total_time:.2f} secondes<br>"
        msg += f"Temps moyen par fichier : {avg_time:.2f} secondes<br>"
        if mem_info:
            msg += f"Mémoire utilisée (processus GUI) : {mem_info:.1f} Mo<br>"
        QMessageBox.information(self, self.tr("Statistiques de compilation", "Build statistics"), msg)

    # Dictionnaires de traduction minimal (à étendre selon les besoins)
    translations = {
        "Français": {
            # Sidebar & principaux boutons
            "select_folder": "📁 Workspace",
            "select_files": "📋 Fichiers",
            "build_all": "🚀 Compiler",
            "export_config": "💾 Exporter config",
            "import_config": "📥 Importer config",
            "cancel_all": "⛔ Annuler",
            "suggest_deps": "🔎 Analyser les dépendances",
            "help": "❓ Aide",
            "show_stats": "📊 Statistiques",
            "select_lang": "Choisir une langue",
            # Workspace
            "venv_button": "Choisir un dossier venv manuellement",
            "label_workspace_section": "1. Sélection du dossier de travail",
            "venv_label": "venv sélectionné : Aucun",
            "label_folder": "Aucun dossier sélectionné",
            # Fichiers
            "label_files_section": "2. Fichiers à compiler",
            "btn_remove_file": "🗑️ Supprimer le fichier sélectionné",
            # Logs
            "label_logs_section": "Logs de compilation",
            # PyInstaller tab
            "tab_pyinstaller": "PyInstaller",
            "opt_onefile": "Onefile",
            "opt_windowed": "Mode fenêtré",
            "opt_noconfirm": "Noconfirm",
            "opt_clean": "Nettoyer",
            "opt_noupx": "No UPX",
            "opt_main_only": "Compiler uniquement main.py ou app.py",
            "btn_select_icon": "🎨 Choisir une icône (.ico)",
            "opt_debug": "Mode debug (--debug)",
            "opt_auto_install": "Auto-installer les modules manquants",
            "opt_silent_errors": "Ne pas afficher de boîte d'erreur (mode silencieux)",
            # "custom_args" supprimé (widget supprimé)
            # Nuitka tab
            "tab_nuitka": "Nuitka",
            "nuitka_onefile": "Onefile (--onefile)",
            "nuitka_standalone": "Standalone (--standalone)",
            "nuitka_disable_console": "Désactiver la console Windows (--windows-disable-console)",
            "nuitka_show_progress": "Afficher la progression (--show-progress)",
            "nuitka_plugins": "Plugins (ex: qt-plugins, séparés par des virgules)",
            "nuitka_output_dir": "Dossier de sortie (--output-dir)",
            # "nuitka_custom_args" supprimé (widget supprimé)
            "btn_nuitka_icon": "🎨 Choisir une icône (.ico) Nuitka",
        },
        "English": {
            # Sidebar & main buttons
            "select_folder": "📁 Workspace",
            "select_files": "📋 Files",
            "build_all": "🚀 Build",
            "export_config": "💾 Export config",
            "import_config": "📥 Import config",
            "cancel_all": "⛔ Cancel",
            "suggest_deps": "🔎 Analyze dependencies",
            "help": "❓ Help",
            "show_stats": "📊 Statistics",
            "select_lang": "Choose language",
            # Workspace
            "venv_button": "Choose venv folder manually",
            "label_workspace_section": "1. Select workspace folder",
            "venv_label": "venv selected: None",
            "label_folder": "No folder selected",
            # Files
            "label_files_section": "2. Files to build",
            "btn_remove_file": "🗑️ Remove selected file",
            # Logs
            "label_logs_section": "Build logs",
            # PyInstaller tab
            "tab_pyinstaller": "PyInstaller",
            "opt_onefile": "Onefile",
            "opt_windowed": "Windowed",
            "opt_noconfirm": "Noconfirm",
            "opt_clean": "Clean",
            "opt_noupx": "No UPX",
            "opt_main_only": "Build only main.py or app.py",
            "btn_select_icon": "🎨 Choose icon (.ico)",
            "opt_debug": "Debug mode (--debug)",
            "opt_auto_install": "Auto-install missing modules",
            "opt_silent_errors": "Do not show error box (silent mode)",
            # "custom_args" supprimé (widget supprimé)
            # Nuitka tab
            "tab_nuitka": "Nuitka",
            "nuitka_onefile": "Onefile (--onefile)",
            "nuitka_standalone": "Standalone (--standalone)",
            "nuitka_disable_console": "Disable Windows console (--windows-disable-console)",
            "nuitka_show_progress": "Show progress (--show-progress)",
            "nuitka_plugins": "Plugins (e.g.: qt-plugins, comma separated)",
            "nuitka_output_dir": "Output folder (--output-dir)",
            # "nuitka_custom_args" supprimé (widget supprimé)
            "btn_nuitka_icon": "🎨 Choose Nuitka icon (.ico)",
        }
    }
    current_language = "English"

    def apply_language(self, lang):
        tr = self.translations.get(lang, self.translations["Français"])
        # Sidebar & principaux boutons
        self.btn_select_folder.setText(tr["select_folder"])
        self.btn_select_files.setText(tr["select_files"])
        self.btn_build_all.setText(tr["build_all"])
        self.btn_export_config.setText(tr["export_config"])
        self.btn_import_config.setText(tr["import_config"])
        self.btn_cancel_all.setText(tr["cancel_all"])
        self.btn_suggest_deps.setText(tr["suggest_deps"])
        self.btn_help.setText(tr["help"])
        self.btn_show_stats.setText(tr["show_stats"])
        self.select_lang.setText(tr["select_lang"])
        # Workspace
        self.venv_button.setText(tr["venv_button"])
        self.label_workspace_section.setText(tr["label_workspace_section"])
        self.venv_label.setText(tr["venv_label"])
        self.label_folder.setText(tr["label_folder"])
        # Fichiers
        self.label_files_section.setText(tr["label_files_section"])
        self.btn_remove_file.setText(tr["btn_remove_file"])
        # Logs
        self.label_logs_section.setText(tr["label_logs_section"])
        # Onglets
        self.compiler_tabs.setTabText(0, tr["tab_pyinstaller"])
        self.compiler_tabs.setTabText(1, tr["tab_nuitka"])
        # PyInstaller options
        self.opt_onefile.setText(tr["opt_onefile"])
        self.opt_windowed.setText(tr["opt_windowed"])
        self.opt_noconfirm.setText(tr["opt_noconfirm"])
        self.opt_clean.setText(tr["opt_clean"])
        self.opt_noupx.setText(tr["opt_noupx"])
        self.opt_main_only.setText(tr["opt_main_only"])
        self.btn_select_icon.setText(tr["btn_select_icon"])
        self.opt_debug.setText(tr["opt_debug"])
        self.opt_auto_install.setText(tr["opt_auto_install"])
        self.opt_silent_errors.setText(tr["opt_silent_errors"])
        # self.custom_args supprimé (widget supprimé)
        # Nuitka options
        self.nuitka_onefile.setText(tr["nuitka_onefile"])
        self.nuitka_standalone.setText(tr["nuitka_standalone"])
        self.nuitka_disable_console.setText(tr["nuitka_disable_console"])
        self.nuitka_show_progress.setText(tr["nuitka_show_progress"])
        self.nuitka_plugins.setPlaceholderText(tr["nuitka_plugins"])
        self.nuitka_output_dir.setPlaceholderText(tr["nuitka_output_dir"])
        # Ajout d'un exemple dans le placeholder Nuitka custom args
        # self.nuitka_custom_args supprimé (widget supprimé)
        self.btn_nuitka_icon.setText(tr["btn_nuitka_icon"])
        self.current_language = lang
        self.save_preferences()
        self.log.append(f"🌐 Langue appliquée : {lang}")

    def tr(self, fr: str, en: str) -> str:
        return en if getattr(self, "current_language", "Français") == "English" else fr

    def set_compilation_ui_enabled(self, enabled):
        self.set_controls_enabled(enabled)

    def show_language_dialog(self):
        from PySide6.QtWidgets import QInputDialog
        languages = ["Français", "English"]
        lang, ok = QInputDialog.getItem(self, "Choisir la langue", "Langue :", languages, 0, False)
        if ok and lang:
            self.apply_language(lang)
        else:
            self.log.append("Sélection de la langue annulée.")

    

    from .dependency_analysis import suggest_missing_dependencies, _install_next_dependency, _on_dep_pip_finished, _on_dep_pip_output

    def _safe_log(self, text):
        try:
            if hasattr(self, "log") and self.log:
                self.log.append(text)
            else:
                print(text)
        except Exception:
            try:
                print(text)
            except Exception:
                pass

    def _has_active_background_tasks(self):
        # Compilation en cours
        if self.processes:
            return True
        # Création du venv en cours
        if hasattr(self, 'venv_progress_dialog') and self.venv_progress_dialog and self.venv_progress_dialog.isVisible():
            return True
        # Installation des dépendances (requirements.txt)
        if hasattr(self, 'progress_dialog') and self.progress_dialog and self.progress_dialog.isVisible():
            return True
        # Vérification/installation d'outils dans le venv (pyinstaller, nuitka)
        if hasattr(self, 'venv_check_progress') and self.venv_check_progress and self.venv_check_progress.isVisible():
            return True
        return False

    def _terminate_background_tasks(self):
        # Tuer proprement les QProcess en cours
        for attr in [
            '_venv_create_process',
            '_venv_install_pyinstaller_process',
            '_venv_install_nuitka_process',
            '_venv_check_process',
            '_venv_check_install_process',
            '_req_install_process',
        ]:
            proc = getattr(self, attr, None)
            try:
                if proc:
                    proc.kill()
            except Exception:
                pass
            setattr(self, attr, None)
        # Fermer les boîtes de progression
        for dlg_attr in ['venv_progress_dialog', 'progress_dialog', 'venv_check_progress']:
            dlg = getattr(self, dlg_attr, None)
            try:
                if dlg:
                    dlg.close()
            except Exception:
                pass

    def closeEvent(self, event):
        if self._has_active_background_tasks():
            details = []
            if self.processes:
                details.append("compilation")
            if hasattr(self, 'venv_progress_dialog') and self.venv_progress_dialog and self.venv_progress_dialog.isVisible():
                details.append("création du venv")
            if hasattr(self, 'progress_dialog') and self.progress_dialog and self.progress_dialog.isVisible():
                details.append("installation des dépendances")
            if hasattr(self, 'venv_check_progress') and self.venv_check_progress and self.venv_check_progress.isVisible():
                details.append("vérification/installation du venv")
            if getattr(self, "current_language", "Français") == "English":
                mapping = {
                    "compilation": "build",
                    "création du venv": "venv creation",
                    "installation des dépendances": "dependencies installation",
                    "vérification/installation du venv": "venv check/installation",
                }
                details_disp = [mapping.get(d, d) for d in details]
                msg = "A process is running"
                if details_disp:
                    msg += " (" + ", ".join(details_disp) + ")"
                msg += ". Do you really want to stop and quit?"
                title = "Process running"
            else:
                msg = "Un processus est en cours"
                if details:
                    msg += " (" + ", ".join(details) + ")"
                msg += ". Voulez-vous vraiment arrêter et quitter ?"
                title = "Processus en cours"
            reply = QMessageBox.question(
                self,
                title,
                msg,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._closing = True
                # Annule les compilations en cours si nécessaire
                if self.processes:
                    self.cancel_all_compilations()
                # Stoppe les processus/boîtes de progression en arrière-plan
                self._terminate_background_tasks()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()