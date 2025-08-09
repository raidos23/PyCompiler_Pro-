# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2025 Samuel Amen Ague

import os
import shutil
import subprocess
import platform
from pathlib import Path
from PySide6.QtWidgets import QMessageBox, QProgressDialog
from PySide6.QtCore import Qt

class PyArmorAPI:
    def __init__(self, parent_widget=None):
        self.parent_widget = parent_widget

    def tr(self, fr: str, en: str) -> str:
        try:
            lang = getattr(self.parent_widget, "current_language", "Français")
            return en if lang == "English" else fr
        except Exception:
            return fr

    def afficher_dialogue_utilisation_pyarmor(self):
        """Affiche un dialogue pour demander si l'utilisateur veut utiliser PyArmor même s'il est installé."""
        msg = QMessageBox(self.parent_widget)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle(self.tr("Utiliser la protection PyArmor ?", "Use PyArmor protection?"))
        msg.setText(self.tr(
            "PyArmor est installé sur ce système.\n\nSouhaitez-vous protéger votre code avec PyArmor ?\n\n- Oui : Votre code sera protégé contre la rétro-ingénierie.\n- Non : La compilation se fera sans protection.\n- Annuler : Annule la compilation.",
            "PyArmor is installed on this system.\n\nDo you want to protect your code with PyArmor?\n\n- Yes: Your code will be protected against reverse engineering.\n- No: The build will proceed without protection.\n- Cancel: Cancels the build."
        ))
        btn_oui = msg.addButton(self.tr("Oui, utiliser PyArmor", "Yes, use PyArmor"), QMessageBox.YesRole)
        btn_non = msg.addButton(self.tr("Non, sans protection", "No, without protection"), QMessageBox.NoRole)
        btn_annuler = msg.addButton(QMessageBox.Cancel)
        msg.setDefaultButton(btn_oui)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == btn_oui:
            print("[INFO] L'utilisateur a choisi d'utiliser PyArmor.")
            return "use_pyarmor"
        elif clicked == btn_non:
            print("[INFO] L'utilisateur a choisi de compiler sans protection PyArmor.")
            QMessageBox.warning(
                self.parent_widget,
                self.tr("Attention : code non protégé", "Warning: unprotected code"),
                self.tr("Vous avez choisi de compiler sans protection PyArmor.\nVotre code sera vulnérable à la rétro-ingénierie.",
                        "You chose to build without PyArmor protection.\nYour code will be vulnerable to reverse engineering.")
            )
            return "continue_unprotected"
        else:
            print("[INFO] L'utilisateur a annulé la compilation (PyArmor installé).")
            QMessageBox.information(
                self.parent_widget,
                self.tr("Compilation annulée", "Build cancelled"),
                self.tr("La compilation a été annulée.", "The build has been cancelled.")
            )
            return "cancel"

    def est_pyarmor_installe(self):
        """Vérifie si PyArmor est installé sur le système."""
        return shutil.which("pyarmor") is not None

    def afficher_alerte_absence_pyarmor(self):
        """Affiche une alerte et propose d'installer PyArmor, ou de continuer sans protection."""
        systeme = platform.system()
        if systeme == "Windows":
            install_cmd = ["python", "-m", "pip", "install", "pyarmor"]
            install_text = "pip install pyarmor"
        else:
            install_cmd = ["pipx", "install", "pyarmor"]
            install_text = "pipx install pyarmor"

        msg = QMessageBox(self.parent_widget)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(self.tr("PyArmor non détecté", "PyArmor not detected"))
        msg.setText(self.tr(
            "PyArmor n'est pas installé sur ce système.\n\nPyArmor est nécessaire pour protéger votre code contre la rétro-ingénierie.\nVous pouvez :\n- Installer PyArmor (recommandé)\n- Continuer sans protection (votre code sera vulnérable)\n- Annuler la compilation\n\nCommande suggérée :\n{cmd}\n",
            "PyArmor is not installed on this system.\n\nPyArmor is required to protect your code against reverse engineering.\nYou can:\n- Install PyArmor (recommended)\n- Continue without protection (your code will be vulnerable)\n- Cancel the build\n\nSuggested command:\n{cmd}\n"
        ).format(cmd=install_text))
        btn_installer = msg.addButton(self.tr("Installer PyArmor", "Install PyArmor"), QMessageBox.AcceptRole)
        btn_sans_protection = msg.addButton(self.tr("Continuer sans protection", "Continue without protection"), QMessageBox.DestructiveRole)
        btn_annuler = msg.addButton(QMessageBox.Cancel)
        msg.setDefaultButton(btn_installer)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == btn_installer:
            try:
                qprogress = QProgressDialog(self.tr("Installation de PyArmor...", "Installing PyArmor..."), None, 0, 0, self.parent_widget)
                qprogress.setWindowTitle(self.tr("Installation en cours", "Installing"))
                qprogress.setWindowModality(Qt.ApplicationModal)
                qprogress.setCancelButton(None)
                qprogress.setMinimumDuration(0)
                qprogress.show()
                print("[INFO] Lancement de l'installation automatique de PyArmor...")
                subprocess.run(install_cmd, check=True)
                qprogress.close()
                QMessageBox.information(
                    self.parent_widget,
                    self.tr("Installation réussie", "Installation successful"),
                    self.tr("PyArmor a été installé avec succès !\nVous pouvez maintenant protéger votre code.",
                            "PyArmor was installed successfully!\nYou can now protect your code.")
                )
                print("[INFO] PyArmor installé avec succès.")
                return "retry"
            except Exception as e:
                qprogress.close()
                print(f"[ERREUR] L'installation automatique de PyArmor a échoué : {e}")
                QMessageBox.critical(
                    self.parent_widget,
                    self.tr("Erreur d'installation", "Installation error"),
                    self.tr("L'installation automatique a échoué.\nErreur : {err}\n\nVous pouvez réessayer ou installer manuellement avec :\n{cmd}",
                            "Automatic installation failed.\nError: {err}\n\nYou can retry or install manually with:\n{cmd}").format(err=e, cmd=install_text)
                )
                return "retry"
        elif clicked == btn_sans_protection:
            print("[INFO] L'utilisateur a choisi de continuer sans protection PyArmor.")
            QMessageBox.warning(
                self.parent_widget,
                self.tr("Attention : code non protégé", "Warning: unprotected code"),
                self.tr("Vous avez choisi de compiler sans protection PyArmor.\nVotre code sera vulnérable à la rétro-ingénierie.",
                        "You chose to build without PyArmor protection.\nYour code will be vulnerable to reverse engineering.")
            )
            return "continue_unprotected"
        else:
            print("[INFO] L'utilisateur a annulé la compilation (PyArmor non installé).")
            QMessageBox.information(
                self.parent_widget,
                self.tr("Compilation annulée", "Build cancelled"),
                self.tr("La compilation a été annulée.\nVous ne pourrez pas utiliser la protection tant que PyArmor n'est pas installé.",
                        "The build has been cancelled.\nYou cannot use protection until PyArmor is installed.")
            )
            return "cancel"

    def obfusquer_workspace(self, workspace_path: str, dossier_temporaire: str) -> bool:
        """
        Obfusque un dossier complet avec PyArmor, en excluant le venv.

        Args:
            workspace_path: Chemin vers le projet original.
            dossier_temporaire: Dossier où stocker les scripts obfusqués.

        Returns:
            True si l'obfuscation a réussi, False sinon.
        """
        try:
            print(f"[INFO] Démarrage de l'obfuscation du dossier : {workspace_path}")
            # Exclure le venv si présent
            venv_path = os.path.join(workspace_path, "venv")
            exclude_args = []
            if os.path.isdir(venv_path):
                exclude_args = ["--exclude", venv_path]
                print(f"[INFO] Exclusion du dossier venv de l'obfuscation : {venv_path}")
            cmd = [
                "pyarmor", "gen", "-r", workspace_path, "-O", dossier_temporaire
            ] + exclude_args
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = (result.stdout or "") + "\n" + (result.stderr or "")
            # Considérer comme succès si pas d'ERROR/FAIL dans la sortie
            if (result.returncode == 0 or ("ERROR" not in output and "FAIL" not in output)):
                print(f"[INFO] Obfuscation terminée. Résultat dans : {dossier_temporaire}")
                QMessageBox.information(
                    self.parent_widget,
                    self.tr("Obfuscation réussie", "Obfuscation successful"),
                    self.tr("Le projet a été protégé avec succès !\n\nDossier de sortie : {out}", "The project was protected successfully!\n\nOutput folder: {out}").format(out=dossier_temporaire)
                )
                return True
            else:
                print(f"[ERREUR] lors de l'obfuscation : {output}")
                QMessageBox.critical(
                    self.parent_widget,
                    self.tr("Erreur d'obfuscation", "Obfuscation error"),
                    self.tr("L'obfuscation a échoué.\n\nCommande exécutée :\n{cmd}\n\nSortie PyArmor :\n{out}",
                            "Obfuscation failed.\n\nExecuted command:\n{cmd}\n\nPyArmor output:\n{out}").format(cmd=' '.join(cmd), out=output)
                )
                return False
        except Exception as e:
            print(f"[ERREUR] Exception lors de l'obfuscation : {e}")
            QMessageBox.critical(
                self.parent_widget,
                self.tr("Erreur d'obfuscation", "Obfuscation error"),
                self.tr("L'obfuscation a échoué suite à une exception.\nErreur : {err}",
                        "Obfuscation failed due to an exception.\nError: {err}").format(err=e)
            )
            return False

    def nettoyer_temp(self, path):
        """Supprime un dossier temporaire s'il existe."""
        if os.path.exists(path):
            print(f"[INFO] Suppression du dossier temporaire : {path}")
            shutil.rmtree(path)

    def lancer_processus_compilation_depuis_temp(self, path_temp):
        """
        Fonction à adapter selon ton système : compile depuis le dossier obfusqué.
        """
        print(f"[INFO] Compilation à lancer depuis : {path_temp}")
        QMessageBox.information(
            self.parent_widget,
            self.tr("Compilation à lancer", "Build to start"),
            self.tr("Lancez la compilation à partir du dossier protégé :\n{p}",
                    "Start the build from the protected folder:\n{p}").format(p=path_temp)
        )
        # ici, tu appelles ton compilateur en passant path_temp au lieu du projet brut
        # ex: compiler_depuis(path_temp)

    def pre_compilation_obfuscation(self, workspace: str):
        if not self.est_pyarmor_installe():
            choix = self.afficher_alerte_absence_pyarmor()
            if choix == "retry":
                # Après installation, retenter la détection
                return self.pre_compilation_obfuscation(workspace)
            elif choix == "continue_unprotected":
                return True
            else:
                return False
        else:
            # PyArmor est installé, demander à l'utilisateur s'il veut l'utiliser
            choix = self.afficher_dialogue_utilisation_pyarmor()
            if choix == "continue_unprotected":
                return True
            elif choix == "cancel":
                return False
            # sinon, continuer avec la protection

        temp_obf_path = os.path.join(workspace, ".temp_obfuscated")
        self.nettoyer_temp(temp_obf_path)

        print("[INFO] Obfuscation du projet en cours...")
        if self.obfusquer_workspace(workspace, temp_obf_path):
            print("[INFO] Obfuscation réussie ✅")
            self.lancer_processus_compilation_depuis_temp(temp_obf_path)
            return True
        else:
            print("[ERREUR] L'obfuscation a échoué ❌")
            return False
