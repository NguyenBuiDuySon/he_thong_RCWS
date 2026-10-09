from __future__ import annotations

from PySide6.QtCore import (
    QDateTime,
    Qt,
)
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.runtime.snapshot import RuntimeSnapshot


class DiagnosticSection(QFrame):
    def __init__(
        self,
        title: str,
        *,
        metric_columns: int = 1,
    ) -> None:
        super().__init__()

        self.setProperty(
            "diagSection",
            True,
        )

        self._metric_columns = max(
            1,
            metric_columns,
        )

        self._metric_count = 0

        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(
            14,
            12,
            14,
            12,
        )
        self._grid.setHorizontalSpacing(18)
        self._grid.setVerticalSpacing(5)

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
            self._metric_columns * 2,
        )

        for column in range(self._metric_columns):
            key_column = column * 2
            value_column = key_column + 1

            self._grid.setColumnStretch(
                key_column,
                1,
            )

            self._grid.setColumnStretch(
                value_column,
                1,
            )

        self._values: dict[
            str,
            QLabel,
        ] = {}

    def add_metric(
        self,
        key: str,
        label: str,
        value: str = "--",
    ) -> None:
        metric_index = self._metric_count

        column_group = metric_index % self._metric_columns

        row = (metric_index // self._metric_columns) + 1

        key_column = column_group * 2

        value_column = key_column + 1

        name_label = QLabel(label)
        name_label.setProperty(
            "diagKey",
            True,
        )
        name_label.setMinimumHeight(25)

        value_label = QLabel(value)
        value_label.setProperty(
            "diagValue",
            True,
        )
        value_label.setMinimumHeight(25)

        value_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        self._grid.addWidget(
            name_label,
            row,
            key_column,
        )

        self._grid.addWidget(
            value_label,
            row,
            value_column,
        )

        self._values[key] = value_label

        self._metric_count += 1

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
        # =====================================================
        # ROOT
        # =====================================================
        root = QVBoxLayout(self)
        root.setContentsMargins(
            18,
            16,
            18,
            16,
        )
        root.setSpacing(12)

        title = QLabel("DIAGNOSTICS")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Telemetry, target state và trạng thái hệ thống")
        subtitle.setObjectName("pageSubtitle")

        root.addWidget(title)
        root.addWidget(subtitle)

        # =====================================================
        # MAIN DASHBOARD
        # 2 rows x 3 columns
        # =====================================================
        dashboard = QGridLayout()

        dashboard.setHorizontalSpacing(10)
        dashboard.setVerticalSpacing(10)

        # =====================================================
        # 1. PERFORMANCE
        # =====================================================
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
            "objects",
            "Detections / Tracks",
        )

        self.performance.add_metric(
            "inference",
            "Inference cur / p95",
        )

        self.performance.add_metric(
            "detector",
            "Detector cur / p95",
        )

        self.performance.add_metric(
            "tracker",
            "Tracker cur / p95",
        )

        self.performance.add_metric(
            "frame_age",
            "Frame Age cur / p95",
        )

        # =====================================================
        # 2. TARGET
        # =====================================================
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

        # =====================================================
        # 3. CONTROL
        # =====================================================
        self.control = DiagnosticSection("CONTROL")

        self.control.add_metric(
            "mode",
            "Control Mode",
        )

        self.control.add_metric(
            "vision_pan",
            "Vision Pan",
        )

        self.control.add_metric(
            "vision_tilt",
            "Vision Tilt",
        )

        self.control.add_metric(
            "selected_pan",
            "Selected Pan",
        )

        self.control.add_metric(
            "selected_tilt",
            "Selected Tilt",
        )

        self.control.add_metric(
            "pan",
            "Final Pan",
        )

        self.control.add_metric(
            "tilt",
            "Final Tilt",
        )

        # =====================================================
        # 4. INPUT
        # =====================================================
        self.input_section = DiagnosticSection("INPUT")

        self.input_section.add_metric(
            "gamepad",
            "Gamepad",
        )

        self.input_section.add_metric(
            "pan_axis",
            "Pan Axis",
        )

        self.input_section.add_metric(
            "tilt_axis",
            "Tilt Axis",
        )

        self.input_section.add_metric(
            "manual_pan",
            "Manual Pan",
        )

        self.input_section.add_metric(
            "manual_tilt",
            "Manual Tilt",
        )

        # =====================================================
        # 5. OUTPUT
        # =====================================================
        self.output_section = DiagnosticSection("OUTPUT")

        self.output_section.add_metric(
            "mode",
            "Output Mode",
        )

        self.output_section.add_metric(
            "pan",
            "Final Pan",
        )

        self.output_section.add_metric(
            "tilt",
            "Final Tilt",
        )

        # =====================================================
        # 6. EVENTS
        # =====================================================
        event_frame = QFrame()

        event_frame.setProperty(
            "diagSection",
            True,
        )

        event_layout = QVBoxLayout(event_frame)

        event_layout.setContentsMargins(
            14,
            12,
            14,
            12,
        )

        event_layout.setSpacing(6)

        event_header = QGridLayout()

        event_title = QLabel("EVENTS")

        event_title.setProperty(
            "diagSectionTitle",
            True,
        )

        clear_button = QPushButton("CLEAR")

        clear_button.setProperty(
            "secondaryButton",
            True,
        )

        clear_button.setMaximumWidth(90)

        event_header.addWidget(
            event_title,
            0,
            0,
        )

        event_header.setColumnStretch(
            0,
            1,
        )

        event_header.addWidget(
            clear_button,
            0,
            1,
        )

        self.event_log = QPlainTextEdit()

        self.event_log.setObjectName("eventLog")

        self.event_log.setReadOnly(True)

        # Không giữ 300 dòng trên dashboard nữa.
        self.event_log.setMaximumBlockCount(50)

        clear_button.clicked.connect(self.event_log.clear)

        event_layout.addLayout(event_header)

        event_layout.addWidget(
            self.event_log,
            1,
        )

        # =====================================================
        # PLACE 6 BLOCKS
        # =====================================================

        # Row 0
        dashboard.addWidget(
            self.performance,
            0,
            0,
        )

        dashboard.addWidget(
            self.target,
            0,
            1,
        )

        dashboard.addWidget(
            self.control,
            0,
            2,
        )

        # Row 1
        dashboard.addWidget(
            self.input_section,
            1,
            0,
        )

        dashboard.addWidget(
            self.output_section,
            1,
            1,
        )

        dashboard.addWidget(
            event_frame,
            1,
            2,
        )

        # 3 cột bằng nhau.
        dashboard.setColumnStretch(
            0,
            1,
        )

        dashboard.setColumnStretch(
            1,
            1,
        )

        dashboard.setColumnStretch(
            2,
            1,
        )

        # Hàng trên lớn hơn hàng dưới một chút.
        dashboard.setRowStretch(
            0,
            11,
        )

        dashboard.setRowStretch(
            1,
            8,
        )

        root.addLayout(
            dashboard,
            1,
        )

    def apply_snapshot(
        self,
        snapshot: RuntimeSnapshot,
    ) -> None:
        # =====================================================
        # PERFORMANCE
        # =====================================================
        self.performance.set_value(
            "camera_fps",
            f"{snapshot.camera_fps:.1f}",
        )

        self.performance.set_value(
            "pipeline_fps",
            f"{snapshot.pipeline_fps:.1f}",
        )

        self.performance.set_value(
            "objects",
            (f"{snapshot.detection_count} / {snapshot.track_count}"),
        )

        self.performance.set_value(
            "inference",
            (
                f"{snapshot.model_inference_ms:.2f} / "
                f"{snapshot.model_inference_p95_ms:.2f} ms"
            ),
        )

        self.performance.set_value(
            "detector",
            (
                f"{snapshot.detector_total_ms:.2f} / "
                f"{snapshot.detector_total_p95_ms:.2f} ms"
            ),
        )

        self.performance.set_value(
            "tracker",
            (f"{snapshot.tracking_ms:.2f} / {snapshot.tracking_p95_ms:.2f} ms"),
        )

        self.performance.set_value(
            "frame_age",
            (f"{snapshot.frame_age_ms:.2f} / {snapshot.frame_age_p95_ms:.2f} ms"),
        )

        # =====================================================
        # TARGET
        # =====================================================
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

        # =====================================================
        # CONTROL
        # =====================================================
        self.control.set_value(
            "mode",
            snapshot.control_mode.value.upper(),
        )

        self.control.set_value(
            "vision_pan",
            f"{snapshot.vision_pan_command:+.3f}",
        )

        self.control.set_value(
            "vision_tilt",
            f"{snapshot.vision_tilt_command:+.3f}",
        )

        self.control.set_value(
            "selected_pan",
            f"{snapshot.selected_pan_command:+.3f}",
        )

        self.control.set_value(
            "selected_tilt",
            f"{snapshot.selected_tilt_command:+.3f}",
        )

        self.control.set_value(
            "pan",
            f"{snapshot.pan_command:+.3f}",
        )

        self.control.set_value(
            "tilt",
            f"{snapshot.tilt_command:+.3f}",
        )

        # =====================================================
        # INPUT
        # =====================================================
        self.input_section.set_value(
            "gamepad",
            ("CONNECTED" if snapshot.gamepad_connected else "DISCONNECTED"),
        )

        self.input_section.set_value(
            "pan_axis",
            f"{snapshot.gamepad_pan_axis:+.3f}",
        )

        self.input_section.set_value(
            "tilt_axis",
            f"{snapshot.gamepad_tilt_axis:+.3f}",
        )

        self.input_section.set_value(
            "manual_pan",
            f"{snapshot.manual_pan_command:+.3f}",
        )

        self.input_section.set_value(
            "manual_tilt",
            f"{snapshot.manual_tilt_command:+.3f}",
        )

        # =====================================================
        # OUTPUT
        # =====================================================
        self.output_section.set_value(
            "mode",
            snapshot.output_mode.upper(),
        )

        self.output_section.set_value(
            "pan",
            f"{snapshot.pan_command:+.3f}",
        )

        self.output_section.set_value(
            "tilt",
            f"{snapshot.tilt_command:+.3f}",
        )

    def add_event(
        self,
        message: str,
    ) -> None:
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")

        self.event_log.appendPlainText(f"{timestamp}  {message}")
