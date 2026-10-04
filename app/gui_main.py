from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.config import load_config
from app.gui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)

    config = load_config("configs/default.yaml")

    window = MainWindow(config)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
