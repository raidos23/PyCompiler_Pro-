# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2025 Samuel Amen Ague

from utils import PyInstallerWorkspaceGUI
from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PyInstallerWorkspaceGUI()
    win.show()
    sys.exit(app.exec())

