from __future__ import annotations

from threading import Event

import cv2
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage

from app.capture.camera import Camera
from app.config import CameraConfig


class CameraPreviewWorker(QObject):
    frame_ready = Signal(QImage)
    error = Signal(str)
    finished = Signal()

    def __init__(
        self,
        config: CameraConfig,
    ) -> None:
        super().__init__()

        self._config = config
        self._stop_event = Event()

    @Slot()
    def run(self) -> None:
        camera: Camera | None = None

        try:
            camera = Camera(self._config)

            while not self._stop_event.is_set():
                packet = camera.read()

                if packet is None:
                    raise RuntimeError("Camera frame unavailable.")

                rgb = cv2.cvtColor(
                    packet.image,
                    cv2.COLOR_BGR2RGB,
                )

                height, width, channels = rgb.shape

                bytes_per_line = channels * width

                image = QImage(
                    rgb.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format.Format_RGB888,
                ).copy()

                self.frame_ready.emit(image)

        except (
            RuntimeError,
            ValueError,
            cv2.error,
        ) as exc:
            self.error.emit(str(exc))

        finally:
            if camera is not None:
                camera.close()

            self.finished.emit()

    def request_stop(self) -> None:
        self._stop_event.set()
