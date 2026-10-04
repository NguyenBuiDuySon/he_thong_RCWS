from __future__ import annotations

from PySide6.QtCore import (
    Qt,
    QThread,
    Slot,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.config import AppConfig
from app.gui.widgets.video import VideoWidget
from app.gui.workers.vision_runtime import (
    VisionRuntimeWorker,
)
from app.runtime.snapshot import (
    RuntimeSnapshot,
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
        config: AppConfig,
    ) -> None:
        super().__init__()

        self._config = config

        self._runtime_thread: QThread | None = None
        self._runtime_worker: VisionRuntimeWorker | None = None

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

        self._start_runtime()

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
        self.video_widget.frame_clicked.connect(self._on_video_clicked)

        self.video_widget.clear_requested.connect(self._on_clear_requested)

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

    def _start_runtime(self) -> None:
        self._runtime_thread = QThread(self)

        self._runtime_worker = VisionRuntimeWorker(self._config)

        self._runtime_worker.moveToThread(self._runtime_thread)

        self._runtime_thread.started.connect(self._runtime_worker.run)

        self._runtime_worker.frame_ready.connect(self.video_widget.set_frame)

        self._runtime_worker.snapshot_ready.connect(self.apply_snapshot)

        self._runtime_worker.notice.connect(self._on_runtime_notice)

        self._runtime_worker.error.connect(self._on_runtime_error)

        self._runtime_worker.finished.connect(self._runtime_thread.quit)

        self._runtime_thread.start()

    def _on_camera_error(
        self,
        message: str,
    ) -> None:
        self.video_widget.setText(f"CAMERA ERROR\n{message}")

        self.system_card.value_label.setText("CAMERA ERROR")

    def stop_runtime(self) -> None:
        if self._runtime_worker is not None:
            self._runtime_worker.request_stop()

        if self._runtime_thread is not None:
            self._runtime_thread.quit()
            self._runtime_thread.wait(5000)

        self._runtime_worker = None
        self._runtime_thread = None

    @Slot(int, int)
    def _on_video_clicked(
        self,
        x: int,
        y: int,
    ) -> None:
        if self._runtime_worker is None:
            return

        self._runtime_worker.request_select(
            x,
            y,
        )

    @Slot()
    def _on_clear_requested(
        self,
    ) -> None:
        if self._runtime_worker is None:
            return

        self._runtime_worker.request_clear()

    @Slot(str)
    def _on_runtime_notice(
        self,
        message: str,
    ) -> None:
        print(f"GUI RUNTIME: {message}")

        display_text = {
            "CAMERA READY": "CAMERA READY",
            "LOADING DETECTOR": "LOADING AI",
            "DETECTOR WARMUP": "AI WARMUP",
            "SYSTEM READY": "READY",
        }.get(
            message,
            message,
        )

        self.system_card.value_label.setText(display_text)

    @Slot(str)
    def _on_runtime_error(
        self,
        message: str,
    ) -> None:
        self.system_card.value_label.setText("ERROR")

        print(f"GUI RUNTIME ERROR: {message}")

    def apply_snapshot(
        self,
        snapshot: RuntimeSnapshot,
    ) -> None:
        self.mode_card.value_label.setText(snapshot.control_mode.value.upper())

        self.target_card.value_label.setText(snapshot.target_status.value.upper())

        target_id = str(snapshot.target_id) if snapshot.target_id is not None else "--"

        self.target_id_card.value_label.setText(target_id)

        self.search_card.value_label.setText(snapshot.search_state.value.upper())

        self.pan_card.value_label.setText(f"{snapshot.pan_command:+.3f}")

        self.tilt_card.value_label.setText(f"{snapshot.tilt_command:+.3f}")

        self.camera_fps.value_label.setText(f"{snapshot.camera_fps:.1f}")

        self.pipeline_fps.value_label.setText(f"{snapshot.pipeline_fps:.1f}")

        self.frame_age.value_label.setText(f"{snapshot.frame_age_p95_ms:.1f} ms")

        self.gamepad.value_label.setText("ON" if snapshot.gamepad_connected else "OFF")

        self.output.value_label.setText(snapshot.output_mode.upper())
