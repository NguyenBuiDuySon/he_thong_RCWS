from __future__ import annotations

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.config import CameraConfig
from app.gui.widgets.video import VideoWidget
from app.gui.workers.camera_preview import (
    CameraPreviewWorker,
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
    def __init__(
        self,
        camera_config: CameraConfig,
    ) -> None:
        super().__init__()

        self._camera_config = camera_config

        self._camera_thread: QThread | None = None
        self._camera_worker: CameraPreviewWorker | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(
            28,
            24,
            28,
            24,
        )
        root.setSpacing(18)

        header = self._build_header()
        content = self._build_content()
        telemetry = self._build_telemetry()

        root.addLayout(header)
        root.addLayout(content, 1)
        root.addLayout(telemetry)

        # PHẢI nằm cuối cùng
        # vì _build_content() mới tạo self.video_widget
        self._start_camera_preview()

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
        frame.setProperty(
            "videoPanel",
            True,
        )

        self.video_widget = VideoWidget()

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(
            8,
            8,
            8,
            8,
        )

        layout.addWidget(self.video_widget)

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

    def _start_camera_preview(self) -> None:
        self._camera_thread = QThread(self)

        self._camera_worker = CameraPreviewWorker(self._camera_config)

        self._camera_worker.moveToThread(self._camera_thread)

        self._camera_thread.started.connect(self._camera_worker.run)

        self._camera_worker.frame_ready.connect(self.video_widget.set_frame)

        self._camera_worker.error.connect(self._on_camera_error)

        self._camera_worker.finished.connect(self._camera_thread.quit)

        self._camera_thread.start()

    def _on_camera_error(
        self,
        message: str,
    ) -> None:
        self.video_widget.setText(f"CAMERA ERROR\n{message}")

        self.system_card.value_label.setText("CAMERA ERROR")

    def stop_camera_preview(self) -> None:
        if self._camera_worker is not None:
            self._camera_worker.request_stop()

        if self._camera_thread is not None:
            self._camera_thread.quit()
            self._camera_thread.wait(2000)

        self._camera_worker = None
        self._camera_thread = None
