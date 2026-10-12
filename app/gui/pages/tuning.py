from __future__ import annotations

from pathlib import Path

import yaml
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.config import AppConfig, load_config


class TuningSection(QFrame):
    def __init__(
        self,
        title: str,
    ) -> None:
        super().__init__()

        self.setProperty(
            "tuningSection",
            True,
        )

        self._grid = QGridLayout(self)

        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._grid.setContentsMargins(
            14,
            12,
            14,
            12,
        )

        self._grid.setHorizontalSpacing(16)
        self._grid.setVerticalSpacing(10)

        title_label = QLabel(title)

        title_label.setProperty(
            "tuningSectionTitle",
            True,
        )

        self._grid.addWidget(
            title_label,
            0,
            0,
            1,
            2,
        )

        self._grid.setColumnStretch(
            0,
            2,
        )

        self._grid.setColumnStretch(
            1,
            3,
        )

        self._row = 1

    def add_row(
        self,
        label: str,
        widget: QWidget,
    ) -> None:
        name_label = QLabel(label)

        name_label.setProperty(
            "tuningKey",
            True,
        )

        widget.setMinimumHeight(38)

        self._grid.addWidget(
            name_label,
            self._row,
            0,
        )

        self._grid.addWidget(
            widget,
            self._row,
            1,
        )

        self._row += 1


class TuningPage(QWidget):
    def __init__(
        self,
        config: AppConfig,
    ) -> None:
        super().__init__()

        self._config = config

        self._config_path = Path("configs/default.yaml")

        root = QVBoxLayout(self)

        root.setContentsMargins(
            18,
            16,
            18,
            16,
        )

        root.setSpacing(12)

        title = QLabel("TUNING")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Tinh chỉnh tham số Vision, tracking và control")
        subtitle.setObjectName("pageSubtitle")

        root.addWidget(title)
        root.addWidget(subtitle)

        dashboard = QGridLayout()

        dashboard.setHorizontalSpacing(10)
        dashboard.setVerticalSpacing(10)

        # =====================================================
        # DETECTOR
        # =====================================================
        self.detector_section = TuningSection("DETECTOR")

        self.detector_confidence = QDoubleSpinBox()

        self.detector_confidence.setRange(
            0.0,
            1.0,
        )

        self.detector_confidence.setDecimals(2)

        self.detector_confidence.setSingleStep(0.01)

        self.detector_max_det = QSpinBox()

        self.detector_max_det.setRange(
            1,
            1000,
        )

        self.detector_section.add_row(
            "Confidence",
            self.detector_confidence,
        )

        self.detector_section.add_row(
            "Max Detections",
            self.detector_max_det,
        )

        # =====================================================
        # TRACKER
        # =====================================================
        self.tracker_section = TuningSection("TRACKER")

        self.lost_track_buffer = QSpinBox()

        self.lost_track_buffer.setRange(
            0,
            300,
        )

        self.track_activation = QDoubleSpinBox()

        self.track_activation.setRange(
            0.0,
            1.0,
        )

        self.track_activation.setDecimals(2)

        self.track_activation.setSingleStep(0.01)

        self.minimum_frames = QSpinBox()

        self.minimum_frames.setRange(
            1,
            30,
        )

        self.minimum_iou = QDoubleSpinBox()

        self.minimum_iou.setRange(
            0.0,
            1.0,
        )

        self.minimum_iou.setDecimals(2)

        self.minimum_iou.setSingleStep(0.01)

        self.high_conf_threshold = QDoubleSpinBox()

        self.high_conf_threshold.setRange(
            0.0,
            1.0,
        )

        self.high_conf_threshold.setDecimals(2)

        self.high_conf_threshold.setSingleStep(0.01)

        self.tracker_section.add_row(
            "Lost Track Buffer",
            self.lost_track_buffer,
        )

        self.tracker_section.add_row(
            "Activation Threshold",
            self.track_activation,
        )

        self.tracker_section.add_row(
            "Minimum Frames",
            self.minimum_frames,
        )

        self.tracker_section.add_row(
            "Minimum IoU",
            self.minimum_iou,
        )

        self.tracker_section.add_row(
            "High Conf Threshold",
            self.high_conf_threshold,
        )

        # =====================================================
        # TARGETING
        # =====================================================
        self.targeting_section = TuningSection("TARGETING")

        self.lost_timeout = QSpinBox()

        self.lost_timeout.setRange(
            1,
            600,
        )

        self.dead_zone_x = QDoubleSpinBox()

        self.dead_zone_x.setRange(
            0.0,
            0.5,
        )

        self.dead_zone_x.setDecimals(3)

        self.dead_zone_x.setSingleStep(0.01)

        self.dead_zone_y = QDoubleSpinBox()

        self.dead_zone_y.setRange(
            0.0,
            0.5,
        )

        self.dead_zone_y.setDecimals(3)

        self.dead_zone_y.setSingleStep(0.01)

        self.filter_tau = QDoubleSpinBox()

        self.filter_tau.setRange(
            0.0,
            1000.0,
        )

        self.filter_tau.setDecimals(1)

        self.filter_tau.setSingleStep(10.0)

        self.filter_tau.setSuffix(" ms")

        self.targeting_section.add_row(
            "Lost Timeout (frames)",
            self.lost_timeout,
        )

        self.targeting_section.add_row(
            "Dead Zone X",
            self.dead_zone_x,
        )

        self.targeting_section.add_row(
            "Dead Zone Y",
            self.dead_zone_y,
        )

        self.targeting_section.add_row(
            "Control Filter Tau",
            self.filter_tau,
        )

        # =====================================================
        # CONTROL
        # =====================================================
        self.control_section = TuningSection("CONTROL")

        self.kp_pan = QDoubleSpinBox()
        self.kp_tilt = QDoubleSpinBox()

        for widget in (
            self.kp_pan,
            self.kp_tilt,
        ):
            widget.setRange(
                0.0,
                5.0,
            )

            widget.setDecimals(3)
            widget.setSingleStep(0.05)

        self.max_pan_command = QDoubleSpinBox()

        self.max_tilt_command = QDoubleSpinBox()

        for widget in (
            self.max_pan_command,
            self.max_tilt_command,
        ):
            widget.setRange(
                0.0,
                1.0,
            )

            widget.setDecimals(3)
            widget.setSingleStep(0.05)

        self.pan_rate = QDoubleSpinBox()
        self.tilt_rate = QDoubleSpinBox()

        for widget in (
            self.pan_rate,
            self.tilt_rate,
        ):
            widget.setRange(
                0.01,
                20.0,
            )

            widget.setDecimals(2)
            widget.setSingleStep(0.10)

        self.watchdog_timeout = QDoubleSpinBox()

        self.watchdog_timeout.setRange(
            0.05,
            5.0,
        )

        self.watchdog_timeout.setDecimals(2)

        self.watchdog_timeout.setSingleStep(0.05)

        self.watchdog_timeout.setSuffix(" s")

        self.control_section.add_row(
            "Kp Pan",
            self.kp_pan,
        )

        self.control_section.add_row(
            "Kp Tilt",
            self.kp_tilt,
        )

        self.control_section.add_row(
            "Max Pan Command",
            self.max_pan_command,
        )

        self.control_section.add_row(
            "Max Tilt Command",
            self.max_tilt_command,
        )

        self.control_section.add_row(
            "Pan Rate / s",
            self.pan_rate,
        )

        self.control_section.add_row(
            "Tilt Rate / s",
            self.tilt_rate,
        )

        self.control_section.add_row(
            "Watchdog Timeout",
            self.watchdog_timeout,
        )

        # =====================================================
        # DASHBOARD
        # =====================================================
        dashboard.addWidget(
            self.detector_section,
            0,
            0,
        )

        dashboard.addWidget(
            self.tracker_section,
            0,
            1,
        )

        dashboard.addWidget(
            self.targeting_section,
            1,
            0,
        )

        dashboard.addWidget(
            self.control_section,
            1,
            1,
        )

        dashboard.setColumnStretch(
            0,
            1,
        )

        dashboard.setColumnStretch(
            1,
            1,
        )

        dashboard.setRowStretch(
            0,
            1,
        )

        dashboard.setRowStretch(
            1,
            1,
        )

        root.addLayout(
            dashboard,
            1,
        )

        # =====================================================
        # ACTION BAR
        # =====================================================
        self.notice = QLabel("Tuning changes require application restart.")

        self.notice.setProperty(
            "setupNotice",
            True,
        )

        self.reset_button = QPushButton("RESET")

        self.reset_button.setProperty(
            "secondaryButton",
            True,
        )

        self.save_button = QPushButton("SAVE TUNING")

        self.save_button.setProperty(
            "primaryButton",
            True,
        )

        self.save_button.clicked.connect(self._save_config)
        self.reset_button.clicked.connect(self._load_config)

        bottom = QHBoxLayout()
        bottom.setSpacing(10)

        bottom.addWidget(self.notice)
        bottom.addStretch()

        bottom.addWidget(self.reset_button)

        bottom.addWidget(self.save_button)

        root.addLayout(bottom)

        self._load_config()

    def _load_config(
        self,
    ) -> None:
        try:
            config = load_config(self._config_path)
        except (
            OSError,
            KeyError,
            TypeError,
            ValueError,
            yaml.YAMLError,
        ) as exc:
            self.notice.setText(f"RESET FAILED: {exc}")
            return

        self._config = config

        detector = config.detector
        tracker = config.tracker
        targeting = config.targeting
        control = config.control

        # DETECTOR
        self.detector_confidence.setValue(detector.confidence)

        self.detector_max_det.setValue(detector.max_det)

        # TRACKER
        self.lost_track_buffer.setValue(tracker.lost_track_buffer)

        self.track_activation.setValue(tracker.track_activation_threshold)

        self.minimum_frames.setValue(tracker.minimum_consecutive_frames)

        self.minimum_iou.setValue(tracker.minimum_iou_threshold)

        self.high_conf_threshold.setValue(tracker.high_conf_det_threshold)

        # TARGETING
        self.lost_timeout.setValue(targeting.lost_timeout_frames)

        self.dead_zone_x.setValue(targeting.dead_zone_x_norm)

        self.dead_zone_y.setValue(targeting.dead_zone_y_norm)

        self.filter_tau.setValue(targeting.control_filter_tau_ms)

        # CONTROL
        self.kp_pan.setValue(control.kp_pan)

        self.kp_tilt.setValue(control.kp_tilt)

        self.max_pan_command.setValue(control.max_pan_command)

        self.max_tilt_command.setValue(control.max_tilt_command)

        self.pan_rate.setValue(control.pan_rate_per_s)

        self.tilt_rate.setValue(control.tilt_rate_per_s)

        self.watchdog_timeout.setValue(control.watchdog_timeout_s)

        self.notice.setText("Tuning values loaded from disk.")

    def _validate_inputs(
        self,
    ) -> tuple[bool, str]:
        if self.dead_zone_x.value() >= 0.5 or self.dead_zone_y.value() >= 0.5:
            return (
                False,
                "Target dead zone is too large.",
            )

        if self.max_pan_command.value() <= 0:
            return (
                False,
                "Max pan command must be > 0.",
            )

        if self.max_tilt_command.value() <= 0:
            return (
                False,
                "Max tilt command must be > 0.",
            )

        if self.pan_rate.value() <= 0:
            return (
                False,
                "Pan rate must be > 0.",
            )

        if self.tilt_rate.value() <= 0:
            return (
                False,
                "Tilt rate must be > 0.",
            )

        if self.watchdog_timeout.value() <= 0:
            return (
                False,
                "Watchdog timeout must be > 0.",
            )

        return (
            True,
            "",
        )

    def _save_config(
        self,
    ) -> None:
        valid, error_message = self._validate_inputs()

        if not valid:
            self.notice.setText(f"SAVE FAILED: {error_message}")
            return

        config_path = self._config_path

        try:
            with config_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                raw = yaml.safe_load(file)

            # ==========================================
            # DETECTOR
            # ==========================================
            raw["detector"]["confidence"] = self.detector_confidence.value()

            raw["detector"]["max_det"] = self.detector_max_det.value()

            # ==========================================
            # TRACKER
            # ==========================================
            raw["tracker"]["lost_track_buffer"] = self.lost_track_buffer.value()

            raw["tracker"]["track_activation_threshold"] = self.track_activation.value()

            raw["tracker"]["minimum_consecutive_frames"] = self.minimum_frames.value()

            raw["tracker"]["minimum_iou_threshold"] = self.minimum_iou.value()

            raw["tracker"]["high_conf_det_threshold"] = self.high_conf_threshold.value()

            # ==========================================
            # TARGETING
            # ==========================================
            raw["targeting"]["lost_timeout_frames"] = self.lost_timeout.value()

            raw["targeting"]["dead_zone_x_norm"] = self.dead_zone_x.value()

            raw["targeting"]["dead_zone_y_norm"] = self.dead_zone_y.value()

            raw["targeting"]["control_filter_tau_ms"] = self.filter_tau.value()

            # ==========================================
            # CONTROL
            # ==========================================
            raw["control"]["kp_pan"] = self.kp_pan.value()

            raw["control"]["kp_tilt"] = self.kp_tilt.value()

            raw["control"]["max_pan_command"] = self.max_pan_command.value()

            raw["control"]["max_tilt_command"] = self.max_tilt_command.value()

            raw["control"]["pan_rate_per_s"] = self.pan_rate.value()

            raw["control"]["tilt_rate_per_s"] = self.tilt_rate.value()

            raw["control"]["watchdog_timeout_s"] = self.watchdog_timeout.value()

        except (
            OSError,
            KeyError,
            TypeError,
            yaml.YAMLError,
        ) as exc:
            self.notice.setText(f"SAVE FAILED: {exc}")
            return

        temp_path = config_path.with_suffix(".yaml.tmp")

        try:
            with temp_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                yaml.safe_dump(
                    raw,
                    file,
                    sort_keys=False,
                    allow_unicode=True,
                )

            validated_config = load_config(temp_path)

            temp_path.replace(config_path)

            self._config = validated_config

        except (
            OSError,
            KeyError,
            TypeError,
            ValueError,
            yaml.YAMLError,
        ) as exc:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)

            self.notice.setText(f"SAVE FAILED: {exc}")
            return

        self.notice.setText("Tuning saved. Restart application to apply changes.")
