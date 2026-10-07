from __future__ import annotations

from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.runtime.snapshot import RuntimeSnapshot


class DiagnosticSection(QFrame):
    def __init__(
        self,
        title: str,
    ) -> None:
        super().__init__()

        self.setProperty(
            "diagSection",
            True,
        )

        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(
            18,
            16,
            18,
            16,
        )
        self._grid.setHorizontalSpacing(24)
        self._grid.setVerticalSpacing(10)

        title_label = QLabel(title)
        title_label.setProperty(
            "diagSectionTitle",
            True,
        )

        self._grid.addWidget(
            title_label,
            0,
            0,
            1,
            2,
        )

        self._next_row = 1
        self._values: dict[str, QLabel] = {}

    def add_metric(
        self,
        key: str,
        label: str,
        value: str = "--",
    ) -> None:
        name_label = QLabel(label)
        name_label.setProperty(
            "diagKey",
            True,
        )

        value_label = QLabel(value)
        value_label.setProperty(
            "diagValue",
            True,
        )

        self._grid.addWidget(
            name_label,
            self._next_row,
            0,
        )

        self._grid.addWidget(
            value_label,
            self._next_row,
            1,
        )

        self._values[key] = value_label
        self._next_row += 1

    def set_value(
        self,
        key: str,
        value: str,
    ) -> None:
        label = self._values.get(key)

        if label is not None:
            label.setText(value)


class DiagnosticsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(
            28,
            24,
            28,
            24,
        )
        root.setSpacing(18)

        title = QLabel("DIAGNOSTICS")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Telemetry, target state và trạng thái hệ thống")
        subtitle.setObjectName("pageSubtitle")

        root.addWidget(title)
        root.addWidget(subtitle)

        top = QHBoxLayout()
        top.setSpacing(14)

        self.performance = DiagnosticSection("PERFORMANCE")

        self.performance.add_metric(
            "camera_fps",
            "Camera FPS",
        )
        self.performance.add_metric(
            "pipeline_fps",
            "Pipeline FPS",
        )
        self.performance.add_metric(
            "frame_age",
            "Frame Age P95",
        )
        self.performance.add_metric(
            "frame_id",
            "Frame ID",
        )

        self.performance.add_metric(
            "detections",
            "Detections",
        )

        self.performance.add_metric(
            "tracks",
            "Tracks",
        )

        self.performance.add_metric(
            "inference",
            "Inference",
        )

        self.performance.add_metric(
            "inference_p95",
            "Inference P95",
        )

        self.performance.add_metric(
            "detector",
            "Detector Total",
        )

        self.performance.add_metric(
            "detector_p95",
            "Detector P95",
        )

        self.performance.add_metric(
            "tracker",
            "Tracker",
        )

        self.performance.add_metric(
            "tracker_p95",
            "Tracker P95",
        )

        self.performance.add_metric(
            "frame_age_current",
            "Frame Age",
        )

        self.target = DiagnosticSection("TARGET")

        self.target.add_metric(
            "status",
            "Status",
        )
        self.target.add_metric(
            "target_id",
            "Target ID",
        )
        self.target.add_metric(
            "search",
            "Search State",
        )

        self.target.add_metric(
            "class",
            "Class",
        )

        self.target.add_metric(
            "confidence",
            "Confidence",
        )

        self.target.add_metric(
            "bbox",
            "Bounding Box",
        )

        self.target.add_metric(
            "center",
            "Center",
        )

        self.target.add_metric(
            "missing",
            "Missing Frames",
        )

        self.control = DiagnosticSection("CONTROL / OUTPUT")

        self.control.add_metric(
            "mode",
            "Control Mode",
        )
        self.control.add_metric(
            "gamepad",
            "Gamepad",
        )
        self.control.add_metric(
            "pan",
            "Pan Command",
        )
        self.control.add_metric(
            "tilt",
            "Tilt Command",
        )
        self.control.add_metric(
            "output",
            "Output Mode",
        )

        top.addWidget(self.performance, 1)
        top.addWidget(self.target, 1)
        top.addWidget(self.control, 1)

        root.addLayout(top)

        log_frame = QFrame()
        log_frame.setProperty(
            "diagSection",
            True,
        )

        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(
            18,
            16,
            18,
            16,
        )

        log_title = QLabel("EVENT LOG")
        log_title.setProperty(
            "diagSectionTitle",
            True,
        )

        self.event_log = QPlainTextEdit()
        self.event_log.setObjectName("eventLog")
        self.event_log.setReadOnly(True)
        self.event_log.setMaximumBlockCount(300)

        log_layout.addWidget(log_title)
        log_layout.addWidget(
            self.event_log,
            1,
        )

        root.addWidget(
            log_frame,
            1,
        )

    def apply_snapshot(
        self,
        snapshot: RuntimeSnapshot,
    ) -> None:
        # -------------------------
        # PERFORMANCE
        # -------------------------
        self.performance.set_value(
            "camera_fps",
            f"{snapshot.camera_fps:.1f}",
        )

        self.performance.set_value(
            "pipeline_fps",
            f"{snapshot.pipeline_fps:.1f}",
        )

        self.performance.set_value(
            "frame_age",
            f"{snapshot.frame_age_p95_ms:.1f} ms",
        )

        self.performance.set_value(
            "frame_id",
            str(snapshot.frame_id),
        )

        self.performance.set_value(
            "detections",
            str(snapshot.detection_count),
        )

        self.performance.set_value(
            "tracks",
            str(snapshot.track_count),
        )

        self.performance.set_value(
            "inference",
            f"{snapshot.model_inference_ms:.2f} ms",
        )

        self.performance.set_value(
            "inference_p95",
            f"{snapshot.model_inference_p95_ms:.2f} ms",
        )

        self.performance.set_value(
            "detector",
            f"{snapshot.detector_total_ms:.2f} ms",
        )

        self.performance.set_value(
            "detector_p95",
            f"{snapshot.detector_total_p95_ms:.2f} ms",
        )

        self.performance.set_value(
            "tracker",
            f"{snapshot.tracking_ms:.2f} ms",
        )

        self.performance.set_value(
            "tracker_p95",
            f"{snapshot.tracking_p95_ms:.2f} ms",
        )

        self.performance.set_value(
            "frame_age_current",
            f"{snapshot.frame_age_ms:.2f} ms",
        )

        # -------------------------
        # TARGET
        # -------------------------
        self.target.set_value(
            "status",
            snapshot.target_status.value.upper(),
        )

        self.target.set_value(
            "target_id",
            (str(snapshot.target_id) if snapshot.target_id is not None else "--"),
        )

        self.target.set_value(
            "search",
            snapshot.search_state.value.upper(),
        )

        self.target.set_value(
            "class",
            snapshot.target_class or "--",
        )

        confidence = (
            f"{snapshot.target_confidence:.3f}"
            if snapshot.target_confidence is not None
            else "--"
        )

        self.target.set_value(
            "confidence",
            confidence,
        )

        if snapshot.target_bbox is None:
            bbox_text = "--"
        else:
            x1, y1, x2, y2 = snapshot.target_bbox

            bbox_text = f"{x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}"

        self.target.set_value(
            "bbox",
            bbox_text,
        )

        if snapshot.target_center is None:
            center_text = "--"
        else:
            center_x, center_y = snapshot.target_center

            center_text = f"{center_x:.0f}, {center_y:.0f}"

        self.target.set_value(
            "center",
            center_text,
        )

        self.target.set_value(
            "missing",
            str(snapshot.target_missing_frames),
        )

        # -------------------------
        # CONTROL / OUTPUT
        # -------------------------
        self.control.set_value(
            "mode",
            snapshot.control_mode.value.upper(),
        )

        self.control.set_value(
            "gamepad",
            ("CONNECTED" if snapshot.gamepad_connected else "DISCONNECTED"),
        )

        self.control.set_value(
            "pan",
            f"{snapshot.pan_command:+.3f}",
        )

        self.control.set_value(
            "tilt",
            f"{snapshot.tilt_command:+.3f}",
        )

        self.control.set_value(
            "output",
            snapshot.output_mode.upper(),
        )

    def add_event(
        self,
        message: str,
    ) -> None:
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")

        self.event_log.appendPlainText(f"{timestamp}  {message}")
