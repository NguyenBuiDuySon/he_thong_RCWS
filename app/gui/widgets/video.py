from __future__ import annotations

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import (
    QImage,
    QPixmap,
    QResizeEvent,
)
from PySide6.QtWidgets import QLabel


class VideoWidget(QLabel):
    def __init__(self) -> None:
        super().__init__()

        self._frame: QImage | None = None

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setMinimumSize(
            640,
            360,
        )

        self.setText("CAMERA PREVIEW\nĐang chờ camera...")

        self.setProperty(
            "videoPlaceholder",
            True,
        )

    @Slot(QImage)
    def set_frame(
        self,
        frame: QImage,
    ) -> None:
        self._frame = frame
        self.setText("")

        self._refresh_pixmap()

    def resizeEvent(
        self,
        event: QResizeEvent,
    ) -> None:
        super().resizeEvent(event)

        self._refresh_pixmap()

    def _refresh_pixmap(self) -> None:
        if self._frame is None:
            return

        pixmap = QPixmap.fromImage(self._frame)

        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setPixmap(scaled)
