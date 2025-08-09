# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2025 Samuel Amen Ague

from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QCheckBox, QLabel, QLineEdit, QListWidget, QProgressBar, QPushButton, QTextEdit, QVBoxLayout


import os
import sys


def init_ui(self):
        loader = QUiLoader()
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ui", "ui_design.ui")
        ui_file = QFile(os.path.abspath(ui_path))
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # Supprimer tous les styles inline du .ui pour laisser le style global s'appliquer
        try:
            from PySide6.QtWidgets import QWidget
            widgets = [self.ui] + self.ui.findChildren(QWidget)
            for w in widgets:
                if hasattr(w, 'styleSheet') and w.styleSheet():
                    w.setStyleSheet("")
        except Exception:
            pass

        # Charger un stylesheet global si présent (ui/style.qss)
        try:
            from PySide6.QtWidgets import QApplication
            style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ui", "style.qss")
            style_path = os.path.abspath(style_path)
            if os.path.exists(style_path):
                with open(style_path, "r", encoding="utf-8") as f:
                    css = f.read()
                app = QApplication.instance()
                if app:
                    app.setStyleSheet(css)
        except Exception as _e:
            # En cas d'échec de chargement du style, on loggue sans casser l'UI
            try:
                if hasattr(self, "log") and self.log:
                    self.log.append(f"⚠️ Échec chargement style.qss: {_e}")
            except Exception:
                pass


        # Remplacer le layout principal par celui du .ui
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        self.setLayout(layout)

        # Récupérer les widgets depuis l'UI chargée
        self.sidebar_logo = self.ui.findChild(QLabel, "sidebar_logo")
        self.btn_select_folder = self.ui.findChild(QPushButton, "btn_select_folder")
        self.venv_button = self.ui.findChild(QPushButton, "venv_button")
        self.venv_label = self.ui.findChild(QLabel, "venv_label")
        self.label_folder = self.ui.findChild(QLabel, "label_folder")
        self.label_workspace_section = self.ui.findChild(QLabel, "label_workspace_section")
        self.label_files_section = self.ui.findChild(QLabel, "label_files_section")
        self.label_logs_section = self.ui.findChild(QLabel, "label_logs_section")
        self.file_list = self.ui.findChild(QListWidget, "file_list")
        # Afficher le logo dans la sidebar (chemin absolu depuis le dossier projet)
        from PySide6.QtGui import QPixmap
        project_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        logo_path = os.path.join(project_dir, "logo", "sidebar_logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            self.sidebar_logo.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.sidebar_logo.setToolTip("PyCompiler")
        else:
            self.sidebar_logo.setText("PyCompiler")
        self.btn_select_files = self.ui.findChild(QPushButton, "btn_select_files")
        self.btn_remove_file = self.ui.findChild(QPushButton, "btn_remove_file")
        self.btn_build_all = self.ui.findChild(QPushButton, "btn_build_all")
        self.btn_cancel_all = self.ui.findChild(QPushButton, "btn_cancel_all")
        self.btn_export_config = self.ui.findChild(QPushButton, "btn_export_config")
        self.btn_import_config = self.ui.findChild(QPushButton, "btn_import_config")
        self.btn_help = self.ui.findChild(QPushButton, "btn_help")
        self.btn_suggest_deps = self.ui.findChild(QPushButton, "btn_suggest_deps")
        self.btn_select_icon = self.ui.findChild(QPushButton, "btn_select_icon")
        self.btn_show_stats = self.ui.findChild(QPushButton, "btn_show_stats")
        self.select_lang = self.ui.findChild(QPushButton, "select_lang")
        # Tooltips pour les boutons principaux (après initialisation)
        if self.btn_select_folder:
            self.btn_select_folder.setToolTip("Sélectionner le dossier de travail (workspace) contenant vos scripts Python.")
        if self.btn_select_files:
            self.btn_select_files.setToolTip("Ajouter manuellement des fichiers Python à compiler dans le workspace.")
        if self.btn_build_all:
            self.btn_build_all.setToolTip("Lancer la compilation de tous les fichiers sélectionnés.")
        if self.btn_export_config:
            self.btn_export_config.setToolTip("Exporter la configuration actuelle dans un fichier JSON.")
        if self.btn_import_config:
            self.btn_import_config.setToolTip("Importer une configuration depuis un fichier JSON.")
        if self.btn_cancel_all:
            self.btn_cancel_all.setToolTip("Annuler toutes les compilations en cours.")
        if self.btn_remove_file:
            self.btn_remove_file.setToolTip("Supprimer le ou les fichiers sélectionnés de la liste.")
        if self.btn_select_icon:
            self.btn_select_icon.setToolTip("Choisir une icône (.ico) pour l'exécutable généré (Windows uniquement).")
            import platform
            self.btn_select_icon.setEnabled(platform.system() == "Windows")
        if self.btn_help:
            self.btn_help.setToolTip("Afficher l'aide et les informations sur le logiciel.")
        if self.venv_button:
            self.venv_button.setToolTip("Sélectionner manuellement un dossier venv à utiliser pour la compilation.")
        if self.btn_suggest_deps:
            self.btn_suggest_deps.setToolTip("Analyser les dépendances Python manquantes dans le projet.")
        self.opt_onefile = self.ui.findChild(QCheckBox, "opt_onefile")
        self.opt_windowed = self.ui.findChild(QCheckBox, "opt_windowed")
        self.opt_noconfirm = self.ui.findChild(QCheckBox, "opt_noconfirm")
        self.opt_clean = self.ui.findChild(QCheckBox, "opt_clean")
        self.opt_noupx = self.ui.findChild(QCheckBox, "opt_noupx")
        self.opt_main_only = self.ui.findChild(QCheckBox, "opt_main_only")
        self.btn_select_icon = self.ui.findChild(QPushButton, "btn_select_icon")
        self.opt_debug = self.ui.findChild(QCheckBox, "opt_debug")
        self.opt_auto_install = self.ui.findChild(QCheckBox, "opt_auto_install")
        self.opt_silent_errors = self.ui.findChild(QCheckBox, "opt_silent_errors")
        # Onglets compilateur (correction robuste)
        from PySide6.QtWidgets import QTabWidget, QWidget
        self.compiler_tabs = self.ui.findChild(QTabWidget, "compiler_tabs")
        self.tab_pyinstaller = self.ui.findChild(QWidget, "tab_pyinstaller")
        self.tab_nuitka = self.ui.findChild(QWidget, "tab_nuitka")
        # Widgets Nuitka (doit être AVANT update_compiler_options_enabled)
        self.nuitka_onefile = self.tab_nuitka.findChild(QCheckBox, "nuitka_onefile") if self.tab_nuitka else None
        self.nuitka_standalone = self.tab_nuitka.findChild(QCheckBox, "nuitka_standalone") if self.tab_nuitka else None
        self.nuitka_disable_console = self.tab_nuitka.findChild(QCheckBox, "nuitka_disable_console") if self.tab_nuitka else None
        if self.nuitka_disable_console:
            self.nuitka_disable_console.setToolTip("Désactiver la console Windows (--windows-disable-console). Option Windows uniquement.")
            import platform
            _is_win = platform.system() == "Windows"
            self.nuitka_disable_console.setEnabled(_is_win)
            if not _is_win:
                self.nuitka_disable_console.setChecked(False)
        self.nuitka_show_progress = self.tab_nuitka.findChild(QCheckBox, "nuitka_show_progress") if self.tab_nuitka else None
        if self.nuitka_show_progress:
            self.nuitka_show_progress.setChecked(True)
        self.nuitka_plugins = self.tab_nuitka.findChild(QLineEdit, "nuitka_plugins") if self.tab_nuitka else None
        self.nuitka_output_dir = self.tab_nuitka.findChild(QLineEdit, "nuitka_output_dir") if self.tab_nuitka else None
        self.nuitka_add_data = self.tab_nuitka.findChild(QPushButton, "nuitka_add_data") if self.tab_nuitka else None
        self.nuitka_data_files = []  # Liste des tuples (source, dest)
        if self.nuitka_add_data:
            self.nuitka_add_data.clicked.connect(self.add_nuitka_data_file)
        self.btn_nuitka_icon = self.tab_nuitka.findChild(QPushButton, "btn_nuitka_icon") if self.tab_nuitka else None
        import platform
        if self.btn_nuitka_icon:
            self.btn_nuitka_icon.setToolTip("Choisir une icône (.ico) pour l'exécutable Nuitka (Windows uniquement).")
            self.btn_nuitka_icon.setEnabled(platform.system() == "Windows")
            self.btn_nuitka_icon.clicked.connect(self.select_nuitka_icon)
        # Tooltips pour les cases à cocher principales
        if self.opt_onefile:
            self.opt_onefile.setToolTip("Générer un exécutable unique (mode onefile).")
        if self.opt_windowed:
            self.opt_windowed.setToolTip("Ne pas ouvrir de console lors de l'exécution (mode fenêtré, --windowed).")
            import platform
            is_win = platform.system() == "Windows"
            self.opt_windowed.setEnabled(is_win)
            if not is_win:
                self.opt_windowed.setChecked(False)
        if self.opt_noconfirm:
            self.opt_noconfirm.setToolTip("Ne pas demander de confirmation pour écraser les fichiers existants (--noconfirm).")
        if self.opt_clean:
            self.opt_clean.setToolTip("Nettoyer les fichiers temporaires avant compilation (--clean).")
        if self.opt_noupx:
            self.opt_noupx.setToolTip("Ne pas utiliser UPX pour compresser l'exécutable (--noupx).")
        if self.opt_main_only:
            self.opt_main_only.setToolTip("Compiler uniquement les fichiers main.py ou app.py du projet.")
        if self.opt_debug:
            self.opt_debug.setToolTip("Activer le mode debug (--debug) pour obtenir plus de logs.")
        if self.opt_auto_install:
            self.opt_auto_install.setToolTip("Installer automatiquement les modules Python manquants détectés.")
        if self.opt_silent_errors:
            self.opt_silent_errors.setToolTip("Ne pas afficher de boîte d'erreur graphique (mode silencieux).")
        # self.custom_args supprimé (widget inutilisé)
        # self.custom_args supprimé (widget inutilisé)
        self.btn_build_all = self.ui.findChild(QPushButton, "btn_build_all")
        self.btn_cancel_all = self.ui.findChild(QPushButton, "btn_cancel_all")
        self.progress = self.ui.findChild(QProgressBar, "progress")
        self.log = self.ui.findChild(QTextEdit, "log")
        self.pyinstaller_add_data = self.tab_pyinstaller.findChild(QPushButton, "pyinstaller_add_data") if self.tab_pyinstaller else None
        self.pyinstaller_data = []  # Liste des tuples (source, dest)
        if self.pyinstaller_add_data:
            self.pyinstaller_add_data.clicked.connect(self.add_pyinstaller_data)
        self.output_dir_input = self.tab_pyinstaller.findChild(QLineEdit, "output_dir_input") if self.tab_pyinstaller else None
        def find_widget_recursive(parent, widget_type, name):
            for child in parent.findChildren(widget_type):
                if child.objectName() == name:
                    return child
            for child in parent.children():
                if hasattr(child, 'findChildren'):
                    result = find_widget_recursive(child, widget_type, name)
                    if result:
                        return result
            return None
        self.btn_browse_output_dir = find_widget_recursive(self.tab_pyinstaller, QPushButton, "btn_browse_output_dir") if self.tab_pyinstaller else None
        if self.output_dir_input:
            self.output_dir_input.setToolTip("Dossier de sortie pour les exécutables générés (option --distpath de PyInstaller). Laisser vide pour utiliser le dossier par défaut 'dist'.")
        if self.btn_browse_output_dir and self.output_dir_input:
            def browse_output_dir():
                from PySide6.QtWidgets import QFileDialog
                # Utilise self comme parent pour garantir l'affichage du dialog
                dir_path = QFileDialog.getExistingDirectory(self, "Choisir le dossier de sortie", "")
                if dir_path:
                    self.output_dir_input.setText(dir_path)
            self.btn_browse_output_dir.clicked.connect(browse_output_dir)
        self.btn_export_config = self.ui.findChild(QPushButton, "btn_export_config")
        self.btn_import_config = self.ui.findChild(QPushButton, "btn_import_config")
        self.btn_help = self.ui.findChild(QPushButton, "btn_help")
        self.output_name_input = QLineEdit()  # Si non présent dans le .ui, à ajouter dans le .ui pour conformité

        # Connecter les signaux
        self.btn_select_folder.clicked.connect(self.select_workspace)
        self.venv_button.clicked.connect(self.select_venv_manually)
        self.btn_select_files.clicked.connect(self.select_files_manually)
        self.btn_remove_file.clicked.connect(self.remove_selected_file)
        self.opt_main_only.stateChanged.connect(self.on_main_only_changed)
        self.btn_select_icon.clicked.connect(self.select_icon)
        self.btn_build_all.clicked.connect(self.compile_all)
        self.btn_cancel_all.clicked.connect(self.cancel_all_compilations)
        self.btn_export_config.clicked.connect(self.export_config)
        self.btn_import_config.clicked.connect(self.import_config)
        if self.btn_help:
            self.btn_help.clicked.connect(self.show_help_dialog)
        if self.btn_show_stats:
            self.btn_show_stats.setToolTip("Afficher les statistiques de compilation (temps, nombre de fichiers, mémoire)")
            self.btn_show_stats.clicked.connect(self.show_statistics)
        for checkbox in [self.opt_onefile, self.opt_windowed, self.opt_noconfirm,
                         self.opt_clean, self.opt_noupx, self.opt_main_only, self.opt_debug,
                         self.opt_auto_install, self.opt_silent_errors]:
            checkbox.stateChanged.connect(self.update_command_preview)
        # self.custom_args supprimé (widget inutilisé)
        if self.select_lang:
            self.select_lang.setToolTip("Choisir la langue de l'interface utilisateur.")
            self.select_lang.clicked.connect(self.show_language_dialog)

        # Désactivation croisée des options PyInstaller/Nuitka selon l'onglet
        import platform
        def update_compiler_options_enabled():
            if self.compiler_tabs.currentIndex() == 0:  # PyInstaller
                for w in [self.opt_onefile, self.opt_windowed, self.opt_noconfirm, self.opt_clean, self.opt_noupx, self.opt_main_only, self.opt_debug, self.opt_auto_install, self.opt_silent_errors]:
                    if not w:
                        continue
                    if w is self.opt_windowed:
                        is_win = platform.system() == "Windows"
                        w.setEnabled(is_win)
                        if not is_win:
                            w.setChecked(False)
                    else:
                        w.setEnabled(True)
                if self.btn_select_icon:
                    self.btn_select_icon.setEnabled(platform.system() == "Windows")
                for w in [self.nuitka_onefile, self.nuitka_standalone, self.nuitka_disable_console, self.nuitka_show_progress, self.nuitka_plugins, self.nuitka_output_dir]:
                    if w: w.setEnabled(False)
            else:  # Nuitka
                for w in [self.opt_onefile, self.opt_windowed, self.opt_noconfirm, self.opt_clean, self.opt_noupx, self.opt_main_only, self.opt_debug, self.opt_auto_install, self.opt_silent_errors, self.btn_select_icon]:
                    if w: w.setEnabled(False)
                for w in [self.nuitka_onefile, self.nuitka_standalone, self.nuitka_disable_console, self.nuitka_show_progress, self.nuitka_plugins, self.nuitka_output_dir]:
                    if not w:
                        continue
                    if w is self.nuitka_disable_console:
                        is_win = platform.system() == "Windows"
                        w.setEnabled(is_win)
                        if not is_win:
                            w.setChecked(False)
                    else:
                        w.setEnabled(True)
        self.compiler_tabs.currentChanged.connect(update_compiler_options_enabled)
        update_compiler_options_enabled()

        # Exclusivité onefile/standalone pour Nuitka
        if self.nuitka_onefile and self.nuitka_standalone:
            def nuitka_onefile_changed(state):
                if state:
                    self.nuitka_standalone.setChecked(False)
                    self.nuitka_standalone.setEnabled(False)
                else:
                    self.nuitka_standalone.setEnabled(True)
            def nuitka_standalone_changed(state):
                if state:
                    self.nuitka_onefile.setChecked(False)
                    self.nuitka_onefile.setEnabled(False)
                else:
                    self.nuitka_onefile.setEnabled(True)
            self.nuitka_onefile.stateChanged.connect(nuitka_onefile_changed)
            self.nuitka_standalone.stateChanged.connect(nuitka_standalone_changed)

        
        # Message d'aide contextuel à la première utilisation
        if not self.workspace_dir:
            self.log.append("Astuce : Commencez par sélectionner un dossier workspace, puis ajoutez vos fichiers Python à compiler. Configurez les options selon vos besoins et cliquez sur Compiler.")

        self.btn_suggest_deps = self.ui.findChild(QPushButton, "btn_suggest_deps")
        if self.btn_suggest_deps:
            self.btn_suggest_deps.clicked.connect(self.suggest_missing_dependencies)

        # Mode silencieux actif par défaut
        self.opt_silent_errors.setChecked(True)

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
    # Demander à l'utilisateur s'il veut ajouter un fichier ou un dossier
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

def show_language_dialog(self):
    from PySide6.QtWidgets import QInputDialog
    languages = ["Français", "English"]
    lang, ok = QInputDialog.getItem(self, "Choisir la langue", "Langue :", languages, 0, False)
    if ok and lang:
        # Ici, il faudrait appliquer la langue à l'interface
        self.log.append(f"Langue sélectionnée : {lang}")
    else:
        self.log.append("Sélection de la langue annulée.")