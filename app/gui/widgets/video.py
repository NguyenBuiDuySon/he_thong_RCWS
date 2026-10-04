from __future__ import annotations

from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QImage,
    QMouseEvent,
    QPixmap,
    QResizeEvent,
)
from PySide6.QtWidgets import QLabel


def map_display_point_to_frame(
    *,
    x: float,
    y: float,
    widget_width: int,
    widget_height: int,
    frame_width: int,
    frame_height: int,
) -> tuple[int, int] | None:
    if widget_width <= 0 or widget_height <= 0 or frame_width <= 0 or frame_height <= 0:
        return None

    scale = min(
        widget_width / frame_width,
        widget_height / frame_height,
    )

    display_width = frame_width * scale
    display_height = frame_height * scale

    offset_x = (widget_width - display_width) / 2.0

    offset_y = (widget_height - display_height) / 2.0

    if (
        x < offset_x
        or y < offset_y
        or x >= offset_x + display_width
        or y >= offset_y + display_height
    ):
        return None

    frame_x = int((x - offset_x) / scale)

    frame_y = int((y - offset_y) / scale)

    frame_x = min(
        frame_width - 1,
        max(0, frame_x),
    )

    frame_y = min(
        frame_height - 1,
        max(0, frame_y),
    )

    return frame_x, frame_y


class VideoWidget(QLabel):
    frame_clicked = Signal(
        int,
        int,
    )
    clear_requested = Signal()

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
        self.setCursor(Qt.CursorShape.CrossCursor)

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

    def mousePressEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if self._frame is None:
            return

        if event.button() == Qt.MouseButton.RightButton:
            self.clear_requested.emit()
            return

        if event.button() != Qt.MouseButton.LeftButton:
            return

        point = event.position()

        mapped = map_display_point_to_frame(
            x=point.x(),
            y=point.y(),
            widget_width=self.width(),
            widget_height=self.height(),
            frame_width=self._frame.width(),
            frame_height=self._frame.height(),
        )

        if mapped is None:
            return

        frame_x, frame_y = mapped

        self.frame_clicked.emit(
            frame_x,
            frame_y,
        )
