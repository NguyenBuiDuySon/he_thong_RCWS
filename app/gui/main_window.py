from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.config import AppConfig
from app.gui.pages.diagnostics import (
    DiagnosticsPage,
)
from app.gui.pages.operate import OperatePage


class PlaceholderPage(QWidget):
    def __init__(
        self,
        title: str,
        subtitle: str,
    ) -> None:
        super().__init__()

        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("pageSubtitle")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(8)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addStretch()


class MainWindow(QMainWindow):
    def __init__(
        self,
        config: AppConfig,
    ) -> None:
        super().__init__()

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        self.setWindowTitle("Multi-Sensor Tracking Platform — System V1")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 700)

        self._pages = QStackedWidget()

        self._operate_page = OperatePage(config)

        self._diagnostics_page = DiagnosticsPage()

        self._operate_page.snapshot_updated.connect(
            self._diagnostics_page.apply_snapshot
        )

        self._operate_page.runtime_event.connect(self._diagnostics_page.add_event)

        self._pages.addWidget(self._operate_page)
        self._pages.addWidget(self._diagnostics_page)
        self._pages.addWidget(
            PlaceholderPage(
                "SETUP",
                "Camera, gamepad, output và serial",
            )
        )
        self._pages.addWidget(
            PlaceholderPage(
                "TUNING",
                "Các tham số điều khiển được phép chỉnh",
            )
        )

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = self._build_sidebar()

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self._pages, 1)

        self.setCentralWidget(root)

        self._apply_theme()

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 24, 16, 20)
        layout.setSpacing(10)

        app_title = QLabel("SYSTEM V1")
        app_title.setObjectName("appTitle")

        app_subtitle = QLabel("TRACKING PLATFORM")
        app_subtitle.setObjectName("appSubtitle")

        layout.addWidget(app_title)
        layout.addWidget(app_subtitle)
        layout.addSpacing(28)

        buttons = (
            ("OPERATE", 0),
            ("DIAGNOSTICS", 1),
            ("SETUP", 2),
            ("TUNING", 3),
        )

        for text, index in buttons:
            button = QPushButton(text)
            button.setCheckable(True)
            button.setProperty("navButton", True)

            if index == 0:
                button.setChecked(True)

            self._nav_group.addButton(
                button,
                index,
            )
            layout.addWidget(button)

        self._nav_group.idClicked.connect(self._pages.setCurrentIndex)

        layout.addStretch()

        version = QLabel("Vision V1 • Control V1")
        version.setObjectName("versionText")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(version)

        return sidebar

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow,
            QWidget {
                background-color: #08131c;
                color: #d8e7f0;
                font-family: "Segoe UI";
                font-size: 14px;
            }

            QWidget#sidebar {
                background-color: #0b1822;
                border-right: 1px solid #1d3545;
            }

            QLabel#appTitle {
                color: #53f0c0;
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#appSubtitle {
                color: #6e8797;
                font-size: 11px;
                font-weight: 600;
            }

            QLabel#pageTitle {
                color: #53f0c0;
                font-size: 30px;
                font-weight: 700;
            }

            QLabel#pageSubtitle {
                color: #8199a8;
                font-size: 15px;
            }

            QLabel#versionText {
                color: #607887;
                font-size: 11px;
            }

            QPushButton[navButton="true"] {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 7px;
                color: #90a8b7;
                padding: 13px 16px;
                text-align: left;
                font-weight: 600;
            }

            QPushButton[navButton="true"]:hover {
                background-color: #102430;
                color: #d8e7f0;
            }

            QPushButton[navButton="true"]:checked {
                background-color: #10372f;
                border: 1px solid #2ccf9c;
                color: #53f0c0;
            }

            QFrame[videoPanel="true"] {
            background-color: #050c12;
            border: 1px solid #1f3d4d;
            border-radius: 10px;
        }

        QLabel[videoPlaceholder="true"] {
            color: #486473;
            font-size: 18px;
            font-weight: 600;
        }

        QFrame[statusCard="true"] {
            background-color: #0d1c26;
            border: 1px solid #1c3848;
            border-radius: 8px;
        }

        QLabel[cardTitle="true"] {
            color: #7793a3;
            font-size: 11px;
            font-weight: 600;
        }

        QLabel[cardValue="true"] {
            color: #53f0c0;
            font-size: 20px;
            font-weight: 700;
        }

        QFrame[metricCard="true"] {
            background-color: #0d1c26;
            border: 1px solid #1c3848;
            border-radius: 8px;
        }

        QLabel[metricTitle="true"] {
            color: #7793a3;
            font-size: 10px;
            font-weight: 600;
        }

        QLabel[metricValue="true"] {
            color: #d8e7f0;
            font-size: 16px;
            font-weight: 700;
        }

        QLabel[systemBadge="true"] {
            background-color: #10372f;
            border: 1px solid #2ccf9c;
            border-radius: 6px;
            color: #53f0c0;
            font-weight: 700;
            padding: 8px 16px;
        }

        QFrame[diagSection="true"] {
            background-color: #0d1c26;
            border: 1px solid #1c3848;
            border-radius: 9px;
        }

        QLabel[diagSectionTitle="true"] {
            color: #53f0c0;
            font-size: 15px;
            font-weight: 700;
        }

        QLabel[diagKey="true"] {
            color: #7892a1;
            font-size: 12px;
        }

        QLabel[diagValue="true"] {
            color: #d8e7f0;
            font-size: 13px;
            font-weight: 600;
        }

        QPlainTextEdit#eventLog {
            background-color: #071119;
            border: 1px solid #183342;
            border-radius: 6px;
            color: #9fb8c7;
            font-family: "Cascadia Mono";
            font-size: 12px;
            padding: 8px;
        }
            """
        )

    def closeEvent(
        self,
        event: QCloseEvent,
    ) -> None:
        self._operate_page.stop_runtime()

        super().closeEvent(event)
