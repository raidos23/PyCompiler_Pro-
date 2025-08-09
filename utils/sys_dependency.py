# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2025 Samuel Amen Ague

import platform
import subprocess
import webbrowser
from PySide6.QtWidgets import QMessageBox, QInputDialog, QLineEdit

class SysDependencyManager:
    def __init__(self, parent_widget=None):
        self.parent_widget = parent_widget

    def tr(self, fr: str, en: str) -> str:
        try:
            lang = getattr(self.parent_widget, "current_language", "Français")
            return en if lang == "English" else fr
        except Exception:
            return fr

    def detect_linux_package_manager(self):
        """Détecte le gestionnaire de paquets Linux (apt, dnf, pacman, zypper)."""
        import shutil
        for pm in ["apt", "dnf", "pacman", "zypper"]:
            if shutil.which(pm):
                return pm
        return None

    def ask_sudo_password(self):
        """Demande le mot de passe sudo à l'utilisateur (champ masqué)."""
        pwd, ok = QInputDialog.getText(
            self.parent_widget,
            self.tr("Mot de passe administrateur requis", "Administrator password required"),
            self.tr("Pour installer les dépendances, entrez votre mot de passe administrateur :", "To install dependencies, enter your administrator password:"),
            QLineEdit.Password
        )
        if ok and pwd:
            return pwd
        return None

    def check_dependencies_installed(self):
        import shutil
        os_name = platform.system()
        if os_name == "Linux":
            gcc = shutil.which("gcc")
            p7zip = shutil.which("7z") or shutil.which("p7zip") or shutil.which("p7zip-full")
            patchelf = shutil.which("patchelf")
            return bool(gcc and p7zip and patchelf)
        elif os_name == "Windows":
            mingw = shutil.which("gcc") or shutil.which("mingw32-gcc")
            return bool(mingw)
        return False

    def install_gcc_and_p7zip(self):
        """Propose d'installer gcc, p7zip-full et patchelf selon l'OS et la distribution."""
        if self.check_dependencies_installed():
            return True
        os_name = platform.system()
        if os_name == "Linux":
            pm = self.detect_linux_package_manager()
            if not pm:
                QMessageBox.critical(
                    self.parent_widget,
                    self.tr("Gestionnaire de paquets non détecté", "Package manager not detected"),
                    self.tr("Impossible de détecter le gestionnaire de paquets pour installer gcc, p7zip-full et patchelf.", "Unable to detect the package manager to install gcc, p7zip-full, and patchelf.")
                )
                return False
            if pm == "apt":
                install_cmd = ["sudo", "-S", "apt", "update", "&&", "sudo", "-S", "apt", "install", "-y", "gcc", "p7zip-full", "patchelf"]
                cmd_str = "sudo -S apt update && sudo -S apt install -y gcc p7zip-full patchelf"
            elif pm == "dnf":
                install_cmd = ["sudo", "-S", "dnf", "install", "-y", "gcc", "p7zip", "patchelf"]
                cmd_str = "sudo -S dnf install -y gcc p7zip patchelf"
            elif pm == "pacman":
                install_cmd = ["sudo", "-S", "pacman", "-Sy", "gcc", "p7zip", "patchelf"]
                cmd_str = "sudo -S pacman -Sy gcc p7zip patchelf"
            elif pm == "zypper":
                install_cmd = ["sudo", "-S", "zypper", "install", "-y", "gcc", "p7zip-full", "patchelf"]
                cmd_str = "sudo -S zypper install -y gcc p7zip-full patchelf"
            else:
                QMessageBox.critical(
                    self.parent_widget,
                    self.tr("Distribution non supportée", "Unsupported distribution"),
                    self.tr(f"Le gestionnaire de paquets {pm} n'est pas encore supporté.", f"Package manager {pm} is not supported yet.")
                )
                return False

            msg = QMessageBox(self.parent_widget)
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle(self.tr("Installer GCC, p7zip et patchelf", "Install GCC, p7zip and patchelf"))
            msg.setText(self.tr(
                "Pour compiler avec Nuitka, un compilateur C (gcc), p7zip-full et patchelf sont nécessaires.\n\nVoulez-vous installer automatiquement ces dépendances ?\n\nCommande utilisée :\n{cmd}",
                "To build with Nuitka, a C compiler (gcc), p7zip-full and patchelf are required.\n\nDo you want to install these dependencies automatically?\n\nCommand used:\n{cmd}"
            ).format(cmd=cmd_str))
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            ret = msg.exec()
            if ret == QMessageBox.Yes:
                password = self.ask_sudo_password()
                if not password:
                    QMessageBox.warning(
                        self.parent_widget,
                        self.tr("Mot de passe requis", "Password required"),
                        self.tr("L'installation a été annulée car aucun mot de passe n'a été fourni.", "Installation cancelled because no password was provided.")
                    )
                    return False
                try:
                    # On exécute la commande dans un shell pour gérer '&&', et on passe le mot de passe à sudo via stdin
                    proc = subprocess.run(cmd_str, shell=True, input=password + "\n", encoding="utf-8", capture_output=True)
                    if proc.returncode == 0:
                        QMessageBox.information(
                            self.parent_widget,
                            self.tr("Installation réussie", "Installation successful"),
                            self.tr("GCC, p7zip-full et patchelf ont été installés avec succès.", "GCC, p7zip-full and patchelf were installed successfully.")
                        )
                        return True
                    else:
                        QMessageBox.critical(
                            self.parent_widget,
                            self.tr("Erreur d'installation", "Installation error"),
                            self.tr("L'installation a échoué.\n\nSortie :\n{out}\n\nErreur :\n{err}", "Installation failed.\n\nOutput:\n{out}\n\nError:\n{err}").format(out=proc.stdout, err=proc.stderr)
                        )
                        return False
                except Exception as e:
                    QMessageBox.critical(
                        self.parent_widget,
                        self.tr("Erreur d'installation", "Installation error"),
                        self.tr("L'installation a échoué.\nErreur : {err}", "Installation failed.\nError: {err}").format(err=e)
                    )
                    return False
            else:
                QMessageBox.information(
                    self.parent_widget,
                    self.tr("Installation annulée", "Installation cancelled"),
                    self.tr("L'installation de gcc, p7zip-full et patchelf a été annulée.", "The installation of gcc, p7zip-full and patchelf was cancelled.")
                )
                return False
        elif os_name == "Windows":
            msg = QMessageBox(self.parent_widget)
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle(self.tr("Installer MinGW-w64 (mhw)", "Install MinGW-w64 (mhw)"))
            msg.setText(self.tr(
                "Pour compiler avec Nuitka sous Windows, il faut installer MinGW-w64 (mhw).\n\nVoulez-vous ouvrir la page de téléchargement officielle ?\n\nAprès installation, relancez la compilation.",
                "To build with Nuitka on Windows, MinGW-w64 (mhw) must be installed.\n\nDo you want to open the official download page?\n\nAfter installation, restart the build."
            ))
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            ret = msg.exec()
            if ret == QMessageBox.Yes:
                url = "https://winlibs.com/"
                webbrowser.open(url)
                QMessageBox.information(
                    self.parent_widget,
                    self.tr("Téléchargement lancé", "Download started"),
                    self.tr("La page officielle de MinGW-w64 a été ouverte dans votre navigateur.\nTéléchargez et installez la version recommandée, puis relancez la compilation.",
                            "The official MinGW-w64 page has been opened in your browser.\nDownload and install the recommended version, then restart the build.")
                )
                return True
            else:
                QMessageBox.information(
                    self.parent_widget,
                    self.tr("Installation annulée", "Installation cancelled"),
                    self.tr("L'installation de MinGW-w64 a été annulée.", "The installation of MinGW-w64 was cancelled.")
                )
                return False
        else:
            QMessageBox.information(
                self.parent_widget,
                self.tr("OS non supporté", "Unsupported OS"),
                self.tr("L'installation automatique de gcc/p7zip ou MinGW-w64 n'est supportée que sous Linux et Windows.", "Automatic installation of gcc/p7zip or MinGW-w64 is only supported on Linux and Windows.")
            )
            return False
