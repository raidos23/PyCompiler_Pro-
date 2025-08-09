# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2025 Samuel Amen Ague

"""
Dialogues personnalisés pour PyCompiler Pro++.
Inclut ProgressDialog, boîtes de message, et autres dialogues spécifiques.
"""

# À compléter avec les classes de dialogues personnalisés
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QProgressBar, QDialog, QApplication
)
class ProgressDialog(QDialog):
    def __init__(self, title="Progression", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(False)  # Non modale pour ne pas bloquer l'UI
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        self.label = QLabel("Préparation...", self)
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 0)  # Indéterminé au début
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setLayout(layout)

    def set_message(self, msg):
        self.label.setText(msg)
        QApplication.processEvents()

    def set_progress(self, value, maximum=None):
        if maximum is not None:
            self.progress.setMaximum(maximum)
        self.progress.setValue(value)
        QApplication.processEvents()