# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2025 Samuel Amen Ague

"""
Logique de compilation pour PyCompiler Pro++.
Inclut la construction des commandes PyInstaller/Nuitka et la gestion des processus de compilation.
"""
import os
import platform
import subprocess
import re
from PySide6.QtWidgets import (
    QMessageBox
)
from PySide6.QtCore import QProcess
from .preferences import MAX_PARALLEL
from .pyarmor_api import PyArmorAPI
from .sys_dependency import SysDependencyManager


def compile_all(self):
    import os
    # Protection du code par PyArmor avant compilation
    pyarmor_api = PyArmorAPI(parent_widget=self)
    if not pyarmor_api.pre_compilation_obfuscation(self.workspace_dir):
        self.log.append("⛔ Compilation annulée : PyArmor requis pour la protection du code.\n")
        return
    if self.processes:
        QMessageBox.warning(self, self.tr("Attention", "Warning"), self.tr("Des compilations sont déjà en cours.", "Builds are already running."))
        return
    if not self.workspace_dir or (not self.python_files and not self.selected_files):
        self.log.append("❌ Aucun fichier à compiler.\n")
        return

    def is_executable_script(path):
        # Vérifie que le fichier existe, n'est pas dans site-packages, et contient un point d'entrée
        if not os.path.exists(path):
            self.log.append(f"❌ Fichier inexistant : {path}")
            return False
        if "site-packages" in path:
            self.log.append(f"⏩ Ignoré (site-packages) : {path}")
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                if "if __name__ == '__main__'" in content or 'if __name__ == "__main__"' in content:
                    return True
                else:
                    self.log.append(f"⏩ Ignoré (pas de point d'entrée) : {path}")
                    return False
        except Exception as e:
            self.log.append(f"⏩ Ignoré (erreur lecture) : {path} ({e})")
            return False

    # Détection du compilateur actif
    use_nuitka = False
    if hasattr(self, 'compiler_tabs') and self.compiler_tabs:
        self.compiler_tabs.setEnabled(False)  # Désactive les onglets au début de la compilation
        if self.compiler_tabs.currentIndex() == 1:  # 0 = PyInstaller, 1 = Nuitka
            use_nuitka = True

    # Sélection des fichiers à compiler selon le compilateur
    if use_nuitka:
        # Nuitka : compile tous les fichiers sélectionnés ou tous les fichiers du workspace
        if self.selected_files:
            files_ok = [f for f in self.selected_files if is_executable_script(f)]
        else:
            files_ok = [f for f in self.python_files if is_executable_script(f)]
        self.queue = [(f, True) for f in files_ok]
        total_files = len(files_ok)
    else:
        # PyInstaller : applique la logique main.py/app.py uniquement si l'option est cochée
        if self.selected_files:
            files_ok = [f for f in self.selected_files if is_executable_script(f)]
            self.queue = [(f, True) for f in files_ok]
            total_files = len(files_ok)
        elif self.opt_main_only.isChecked():
            files = [f for f in self.python_files if os.path.basename(f) in ("main.py", "app.py")]
            files_ok = [f for f in files if is_executable_script(f)]
            self.queue = [(f, True) for f in files_ok]
            total_files = len(files_ok)
            if not files_ok:
                self.log.append("⚠️ Aucun main.py ou app.py exécutable trouvé dans le workspace.\n")
                return
        else:
            files_ok = [f for f in self.python_files if is_executable_script(f)]
            self.queue = [(f, True) for f in files_ok]
            total_files = len(files_ok)

    self.current_compiling.clear()
    self.processes.clear()
    self.progress.setRange(0, 0)  # Mode indéterminé pendant toute la compilation
    self.log.append("🔨 Compilation parallèle démarrée...\n")

    self.set_controls_enabled(False)
    self.try_start_processes()

# Nouvelle version de try_start_processes pour gérer les fichiers ignorés dynamiquement

def try_start_processes(self):
    from PySide6.QtWidgets import QApplication
    while len(self.processes) < MAX_PARALLEL and self.queue:
        file, to_compile = self.queue.pop(0)
        if to_compile:
            self.start_compilation_process(file)
        # Si le fichier est ignoré (to_compile == False), on ne touche pas à la barre de progression
        # et on passe simplement au suivant
    if not self.processes and not self.queue:
        # Toutes les compilations sont terminées : mettre la barre à 100%
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        self.log.append("✔️ Toutes les compilations sont terminées.\n")
        if hasattr(self, 'compiler_tabs') and self.compiler_tabs:
            self.compiler_tabs.setEnabled(True)  # Réactive les onglets à la toute fin
        self.set_controls_enabled(True)
        self.save_preferences()

def start_compilation_process(self, file):
    import time
    file_basename = os.path.basename(file)
    # Choix du compilateur selon l'onglet actif
    use_nuitka = False
    if hasattr(self, 'compiler_tabs') and self.compiler_tabs:
        if self.compiler_tabs.currentIndex() == 1:  # 0 = PyInstaller, 1 = Nuitka
            use_nuitka = True
    if use_nuitka:
        # Vérification et installation des dépendances système pour Nuitka
        sysdep = SysDependencyManager(parent_widget=self)
        if not sysdep.install_gcc_and_p7zip():
            self.log.append("⛔ Compilation Nuitka annulée : dépendances système manquantes ou installation refusée.\n")
            return
        cmd = self.build_nuitka_command(file)
        # Nuitka s'exécute avec python -m nuitka dans le venv
        if self.venv_path_manuel:
            venv_bin = os.path.join(self.venv_path_manuel, "venv", "Scripts" if platform.system() == "Windows" else "bin")
        else:
            venv_bin = os.path.join(self.workspace_dir, "venv", "Scripts" if platform.system() == "Windows" else "bin")
        python_path = os.path.join(venv_bin, "python" if platform.system() != "Windows" else "python.exe")
        if not os.path.isfile(python_path):
            self.log.append(f"❌ python non trouvé dans le venv : {python_path}")
            self.show_error_dialog(file_basename)
            return
        self.log.append(f"▶️ Lancement compilation Nuitka : {file_basename}\nCommande : {' '.join(cmd)}\n")
        process = QProcess(self)
        process.setProgram(python_path)
        process.setArguments(cmd[1:])
        process.setWorkingDirectory(self.workspace_dir)
        process.file_path = file
        process.file_basename = file_basename
        process._start_time = time.time()
        process.readyReadStandardOutput.connect(lambda p=process: self.handle_stdout(p))
        process.readyReadStandardError.connect(lambda p=process: self.handle_stderr(p))
        process.finished.connect(lambda ec, es, p=process: self.handle_finished(p, ec, es))
        self.processes.append(process)
        self.current_compiling.add(file)
        # Suppression de la désactivation ici (déjà fait dans compile_all)
        if hasattr(self, 'update_compiler_options_enabled'):
                self.update_compiler_options_enabled()
        process.start()
    else:
        cmd = self.build_pyinstaller_command(file_basename)
        if self.venv_path_manuel:
            venv_bin = os.path.join(self.venv_path_manuel, "venv", "Scripts" if platform.system() == "Windows" else "bin")
        else:
            venv_bin = os.path.join(self.workspace_dir, "venv", "Scripts" if platform.system() == "Windows" else "bin")
        pyinstaller_path = os.path.join(venv_bin, "pyinstaller" if platform.system() == "windows" else "pyinstaller")
        if not os.path.isfile(pyinstaller_path):
            self.log.append(f"❌ pyinstaller non trouvé dans le venv : {pyinstaller_path}")
            self.show_error_dialog(file_basename)
            return
        self.log.append(f"▶️ Lancement compilation : {file_basename}\nCommande : {' '.join([pyinstaller_path] + cmd[1:])}\n")
        # Met la barre en mode indéterminé pendant la compilation du fichier pour PyInstaller ET Nuitka
        self.progress.setRange(0, 0)
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        process = QProcess(self)
        process.setProgram(pyinstaller_path)
        process.setArguments(cmd[1:])
        process.setWorkingDirectory(self.workspace_dir)
        process.file_path = file
        process.file_basename = file_basename
        process._start_time = time.time()
        process.readyReadStandardOutput.connect(lambda p=process: self.handle_stdout(p))
        process.readyReadStandardError.connect(lambda p=process: self.handle_stderr(p))
        process.finished.connect(lambda ec, es, p=process: self.handle_finished(p, ec, es))
        self.processes.append(process)
        self.current_compiling.add(file)
        # Suppression de la désactivation ici (déjà fait dans compile_all)
        process.start()

    # Ajout pour Nuitka : barre ind��terminée aussi
    if use_nuitka:
        self.progress.setRange(0, 0)
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()

def handle_stdout(self, process):
    data = process.readAllStandardOutput().data().decode()
    self.log.append(data)

    # Détection de la fin Nuitka dans le log
    if "Successfully created" in data or "Nuitka: Successfully created" in data:
        # Forcer la barre à 100% et sortir du mode animation
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        # S'assurer que le message est à la fin du log
        lines = data.strip().splitlines()
        for line in lines:
            if "Nuitka: Successfully created" in line or "Successfully created" in line:
                self.log.append(f"<b style='color:green'>{line}</b>")
        # Forcer la terminaison du process si besoin
        if process.state() != QProcess.NotRunning:
            self.log.append("<span style='color:orange;'>ℹ️ Nuitka a signalé la fin de compilation dans le log, mais le process n'est pas terminé. Forçage du kill immédiat et nettoyage UI...</span>")
            process.kill()
            process.waitForFinished(2000)
            # Nettoyage manuel si le signal finished ne se déclenche pas
            if process in self.processes:
                self.handle_finished(process, 0, QProcess.NormalExit)
    # --- Progression Nuitka (--show-progress) ---
    # Désormais, la barre reste indéterminée pendant toute la compilation
    # (aucune mise à jour de valeur ici)

def handle_stderr(self, process):
    data = process.readAllStandardError().data().decode()
    self.log.append(f"<span style='color:red;'>{data}</span>")

def handle_finished(self, process, exit_code, exit_status):
    # Suppression de la réactivation ici (gérée à la toute fin dans try_start_processes)
    import traceback
    import time
    import psutil
    file = process.file_path
    file_basename = process.file_basename

    # Mesure du temps de compilation
    elapsed = None
    if hasattr(process, '_start_time'):
        elapsed = time.time() - process._start_time
        if not hasattr(self, '_compilation_times'):
            self._compilation_times = {}
        self._compilation_times[file_basename] = elapsed

    # Mesure mémoire (si psutil dispo)
    mem_info = None
    try:
        p = psutil.Process()
        mem_info = p.memory_info().rss / (1024*1024)
    except Exception:
        mem_info = None

    if exit_code == 0:
        msg = f"✅ {file_basename} compilé avec succès."
        if elapsed:
            msg += f" Temps de compilation : {elapsed:.2f} secondes."
        if mem_info:
            msg += f" Mémoire utilisée (processus GUI) : {mem_info:.1f} Mo."
        # Suppression de la vérification stricte du dossier/fichier de sortie
        self.log.append(msg + "\n")
        self.log.append("<span style='color:#7faaff;'>ℹ️ Certains messages d’erreur ou de warning peuvent apparaître dans les logs, mais si l’exécutable fonctionne, ils ne sont pas bloquants.</span>\n")
        # Ouvre le dossier Nuitka si la compilation a été faite avec Nuitka
        if hasattr(self, 'compiler_tabs') and self.compiler_tabs.currentIndex() == 1 and hasattr(self, 'open_nuitka_dist_folder'):
            try:
                self.open_nuitka_dist_folder(file)
            except Exception as e:
                self.log.append(f"⚠️ Impossible d'ouvrir le dossier Nuitka automatiquement : {e}")
        # Ouvre le dossier dist si la compilation a été faite avec PyInstaller
        if hasattr(self, 'compiler_tabs') and self.compiler_tabs.currentIndex() == 0 and hasattr(self, 'open_dist_folder'):
            try:
                self.open_dist_folder()
            except Exception as e:
                self.log.append(f"⚠️ Impossible d'ouvrir le dossier dist automatiquement : {e}")
    else:
        # Ajout d'un affichage détaillé pour les erreurs inattendues
        error_details = process.readAllStandardError().data().decode()
        self.log.append(f"<span style='color:red;'>❌ La compilation de {file_basename} ({file}) a échoué (code {exit_code}).</span>\n")
        if error_details:
            self.log.append(f"<span style='color:red;'>Détails de l'erreur :<br><pre>{error_details}</pre></span>")
        self.show_error_dialog(file_basename, file, exit_code, error_details)

        # Auto-install modules manquants si activé
        if self.opt_auto_install.isChecked():
            self.try_install_missing_modules(process)

    if process in self.processes:
        self.processes.remove(process)
    if file in self.current_compiling:
        self.current_compiling.remove(file)

    # Ne pas toucher à la barre ici : elle sera gérée dans try_start_processes

    # Si toutes les compilations sont terminées, afficher un résumé
    if not self.processes and not self.queue and hasattr(self, '_compilation_times'):
        self.log.append("\n<b>Résum�� des performances :</b>")
        total = 0
        for fname, t in self._compilation_times.items():
            self.log.append(f"- {fname} : {t:.2f} secondes")
            total += t
        self.log.append(f"<b>Temps total de compilation :</b> {total:.2f} secondes\n")
        del self._compilation_times

    # Essaye de lancer d’autres compilations dans la file d’attente
    self.try_start_processes()

def try_install_missing_modules(self, process):
    output = process.readAllStandardError().data().decode()
    missing_modules = re.findall(r"No module named '([\w\d_]+)'", output)
    if not hasattr(self, '_already_tried_modules'):
        self._already_tried_modules = set()
    if not hasattr(self, '_install_report'):
        self._install_report = []
    if missing_modules:
        pip_exe = os.path.join(self.workspace_dir, "venv", "Scripts" if platform.system() == "Windows" else "bin", "pip")
        all_installed = True
        new_modules = [m for m in missing_modules if m not in self._already_tried_modules]
        if not new_modules:
            self.log.append("❌ Boucle d'installation stoppée : mêmes modules manquants détectés à nouveau.")
            self.log.append("Rapport final :")
            for line in self._install_report:
                self.log.append(line)
            self._already_tried_modules.clear()
            self._install_report.clear()
            return
        for module in new_modules:
            self._already_tried_modules.add(module)
            self.log.append(f"📦 Tentative d'installation du module manquant : {module}")
            try:
                subprocess.run([pip_exe, "install", module], check=True)
                msg = f"✅ Module {module} installé avec succès."
                self.log.append(msg)
                self._install_report.append(msg)
            except Exception as e:
                msg = f"❌ Échec d'installation de {module} : {e}"
                self.log.append(msg)
                self._install_report.append(msg)
                all_installed = False
        # Relancer la compilation après installation, si tout s'est bien passé
        if all_installed:
            reply = QMessageBox.question(
                self,
                self.tr("Relancer la compilation", "Restart build"),
                self.tr("Des modules manquants ont été installés. Voulez-vous relancer la compilation de ce fichier ?", "Missing modules were installed. Do you want to restart the build for this file?"),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.log.append("🔁 Relance de la compilation après installation des modules manquants...")
                self.queue.insert(0, process.file_path)
                self.try_start_processes()
            else:
                self.log.append("⏹️ Compilation non relancée après installation des modules. Rapport final :")
                for line in self._install_report:
                    self.log.append(line)
                self._already_tried_modules.clear()
                self._install_report.clear()
        else:
            self.log.append("❌ Certains modules n'ont pas pu être installés. Compilation non relancée.")
            self.log.append("Rapport final :")
            for line in self._install_report:
                self.log.append(line)
            self._already_tried_modules.clear()
            self._install_report.clear()
    else:
        # Si plus de modules manquants, afficher le rapport final
        if hasattr(self, '_install_report') and self._install_report:
            self.log.append("Rapport final :")
            for line in self._install_report:
                self.log.append(line)
            self._already_tried_modules.clear()
            self._install_report.clear()

def show_error_dialog(self, filename, filepath=None, exit_code=None, error_details=None):
    # Mode silencieux : ne rien afficher si la case est cochée
    if hasattr(self, 'opt_silent_errors') and self.opt_silent_errors.isChecked():
        return
    dlg = QMessageBox(self)
    dlg.setWindowTitle(self.tr("Erreur de compilation", "Build error"))
    base = self.tr("La compilation de {filename} a échoué.", "Build of {filename} failed.")
    msg = base.format(filename=filename)
    if filepath:
        msg += f"\n{self.tr('Fichier', 'File')} : {filepath}"
    if exit_code is not None:
        msg += "\n{} : {}".format(self.tr("Code d'erreur", "Error code"), exit_code)
    if error_details:
        msg += f"\n\n{self.tr('Détails techniques', 'Technical details')} :\n{error_details}"
    dlg.setText(msg)
    dlg.setIcon(QMessageBox.Icon.Critical)
    dlg.exec()

def cancel_all_compilations(self):
    errors = []
    for process in self.processes[:]:
        try:
            if process.state() != QProcess.NotRunning:
                process.kill()
                if not process.waitForFinished(3000):  # Attendre 3s max
                    errors.append(process.file_path if hasattr(process, 'file_path') else str(process))
                    self.log.append(f"⚠️ Impossible de tuer le process {getattr(process, 'file_path', process)}")
                else:
                    self.log.append(f"✅ Process tué : {getattr(process, 'file_path', process)}")
            else:
                self.log.append(f"ℹ️ Process déjà arrêté : {getattr(process, 'file_path', process)}")
        except Exception as e:
            errors.append(str(e))
            self.log.append(f"❌ Erreur lors de l'arrêt d'un process : {e}")
        self.processes.remove(process)
    self.queue.clear()
    self.current_compiling.clear()
    self.progress.setRange(0, 1)
    self.progress.setValue(0)
    self.set_controls_enabled(True)
    if errors:
        self.log.append(f"❌ Certains processus n'ont pas pu être arrêtés : {errors}")
    else:
        self.log.append("⛔ Toutes les compilations ont été annulées.\n")

def build_pyinstaller_command(self, file):
    cmd = ["pyinstaller"]
    if self.opt_onefile.isChecked():
        cmd.append("--onefile")
    if self.opt_windowed.isChecked():
        cmd.append("--windowed")
    if self.opt_noconfirm.isChecked():
        cmd.append("--noconfirm")
    if self.opt_clean.isChecked():
        cmd.append("--clean")
    if self.opt_noupx.isChecked():
        cmd.append("--noupx")
    if self.opt_debug.isChecked():
        cmd.append("--debug")
    if self.icon_path:
        cmd.append(f"--icon={self.icon_path}")
    # Ajout des fichiers/dossiers de données PyInstaller
    if hasattr(self, 'pyinstaller_data'):
        for src, dest in self.pyinstaller_data:
            cmd.append(f"--add-data={src}:{dest}")
    cmd.append(file)
    
    custom_name = self.output_name_input.text().strip()
    if custom_name:
        output_name = custom_name + ".exe" if platform.system() == "Windows" else custom_name
    else:
        base_name = os.path.splitext(os.path.basename(file))[0]
        output_name = base_name + ".exe" if platform.system() == "Windows" else base_name
    cmd += ["--name", output_name]

    # Dossier de sortie
    output_dir = self.output_dir_input.text().strip()
    if output_dir:
        cmd += ["--distpath", output_dir]

    return cmd

def build_nuitka_command(self, file):
    cmd = ["python3", "-m", "nuitka"]
    if self.nuitka_onefile and self.nuitka_onefile.isChecked():
        cmd.append("--onefile")
    if self.nuitka_standalone and self.nuitka_standalone.isChecked():
        cmd.append("--standalone")
    import platform
    if self.nuitka_disable_console and self.nuitka_disable_console.isChecked() and platform.system() == "Windows":
        cmd.append("--windows-disable-console")
    if self.nuitka_show_progress and self.nuitka_show_progress.isChecked():
        cmd.append("--show-progress")
    # Ajout automatique du plugin PySide6 ou PyQt6 si utilisé, mais jamais les deux
    plugins = []
    if self.nuitka_plugins and self.nuitka_plugins.text().strip():
        plugins = [p.strip().lower() for p in self.nuitka_plugins.text().strip().split(",") if p.strip()]
    # Forcer l'ajout de pyside6 ou pyqt6 si importés dans le projet
    found_pyside6 = False
    found_pyqt6 = False
    try:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            if ("import PySide6" in content or "from PySide6" in content):
                found_pyside6 = True
            if ("import PyQt6" in content or "from PyQt6" in content):
                found_pyqt6 = True
    except Exception:
        pass
    # Ne jamais activer les deux plugins Qt en même temps
    if found_pyside6:
        if "pyqt6" in plugins:
            plugins.remove("pyqt6")
        if "pyside6" not in plugins:
            plugins.append("pyside6")
    elif found_pyqt6:
        if "pyside6" in plugins:
            plugins.remove("pyside6")
        if "pyqt6" not in plugins:
            plugins.append("pyqt6")
    # Si les deux sont dans la liste, n'en garder qu'un (priorité à pyside6)
    if "pyside6" in plugins and "pyqt6" in plugins:
        plugins.remove("pyqt6")
    for plugin in plugins:
        cmd.append(f"--plugin-enable={plugin}")
    # Nuitka icon: priorité à self.nuitka_icon_path si défini, sinon self.icon_path
    import platform
    if platform.system() == "Windows":
        if hasattr(self, 'nuitka_icon_path') and self.nuitka_icon_path:
            cmd.append(f"--windows-icon-from-ico={self.nuitka_icon_path}")
        elif self.icon_path:
            cmd.append(f"--windows-icon-from-ico={self.icon_path}")
    if self.nuitka_output_dir and self.nuitka_output_dir.text().strip():
        cmd.append(f"--output-dir={self.nuitka_output_dir.text().strip()}")
    # Ajout des fichiers de données Nuitka
    if hasattr(self, 'nuitka_data_files'):
        for src, dest in self.nuitka_data_files:
            cmd.append(f"--include-data-files={src}={dest}")
    if hasattr(self, 'nuitka_data_dirs'):
        for src, dest in self.nuitka_data_dirs:
            cmd.append(f"--include-data-dir={src}={dest}")
    cmd.append(file)
    return cmd



