from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class StatusCard(QFrame):
    def __init__(
        self,
        title: str,
        value: str = "--",
    ) -> None:
        super().__init__()

        self.setProperty("statusCard", True)

        title_label = QLabel(title)
        title_label.setProperty("cardTitle", True)

        self.value_label = QLabel(value)
        self.value_label.setProperty("cardValue", True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)


class MetricCard(QFrame):
    def __init__(
        self,
        title: str,
        value: str = "--",
    ) -> None:
        super().__init__()

        self.setProperty("metricCard", True)

        title_label = QLabel(title)
        title_label.setProperty("metricTitle", True)

        self.value_label = QLabel(value)
        self.value_label.setProperty("metricValue", True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(3)

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)


class OperatePage(QWidget):
    def __init__(self) -> None:
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        header = self._build_header()
        content = self._build_content()
        telemetry = self._build_telemetry()

        root.addLayout(header)
        root.addLayout(content, 1)
        root.addLayout(telemetry)

    def _build_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title = QLabel("OPERATE")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Vận hành và theo dõi mục tiêu")
        subtitle.setObjectName("pageSubtitle")

        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)

        system_badge = QLabel("GUI READY")
        system_badge.setProperty("systemBadge", True)
        system_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(system_badge)

        return layout

    def _build_content(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(16)

        video_panel = self._build_video_panel()
        status_panel = self._build_status_panel()

        layout.addWidget(video_panel, 3)
        layout.addLayout(status_panel, 1)

        return layout

    def _build_video_panel(self) -> QFrame:
        frame = QFrame()
        frame.setProperty("videoPanel", True)

        self.video_label = QLabel("CAMERA PREVIEW\nRuntime chưa được kết nối")

        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setProperty(
            "videoPlaceholder",
            True,
        )

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)

        layout.addWidget(self.video_label)

        return frame

    def _build_status_panel(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(10)

        self.system_card = StatusCard(
            "SYSTEM",
            "GUI READY",
        )

        self.mode_card = StatusCard("CONTROL MODE")

        self.target_card = StatusCard("TARGET")

        self.target_id_card = StatusCard("TARGET ID")

        self.search_card = StatusCard("SEARCH STATE")

        self.pan_card = StatusCard("PAN COMMAND")

        self.tilt_card = StatusCard("TILT COMMAND")

        for card in (
            self.system_card,
            self.mode_card,
            self.target_card,
            self.target_id_card,
            self.search_card,
            self.pan_card,
            self.tilt_card,
        ):
            layout.addWidget(card)

        layout.addStretch()

        return layout

    def _build_telemetry(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(10)

        self.camera_fps = MetricCard("CAMERA FPS")

        self.pipeline_fps = MetricCard("PIPELINE FPS")

        self.frame_age = MetricCard("FRAME AGE P95")

        self.gamepad = MetricCard("GAMEPAD")

        self.output = MetricCard("OUTPUT")

        for card in (
            self.camera_fps,
            self.pipeline_fps,
            self.frame_age,
            self.gamepad,
            self.output,
        ):
            layout.addWidget(card)

        return layout
