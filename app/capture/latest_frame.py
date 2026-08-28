from __future__ import annotations

from queue import Empty, Full, Queue
from threading import Event, Lock, Thread

from app.capture.camera import Camera, FramePacket


class LatestFrameStream:
    def __init__(
        self,
        camera: Camera,
    ) -> None:
        self._camera = camera

        self._queue: Queue[FramePacket] = Queue(
            maxsize=1
        )

        self._stop_event = Event()

        self._thread: Thread | None = None

        self._dropped_frames = 0
        self._counter_lock = Lock()

    @property
    def dropped_frames(self) -> int:
        with self._counter_lock:
            return self._dropped_frames

    def start(self) -> None:
        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            return

        self._stop_event.clear()

        self._thread = Thread(
            target=self._capture_loop,
            name="camera-capture",
            daemon=True,
        )

        self._thread.start()

    def _capture_loop(self) -> None:
        while not self._stop_event.is_set():
            packet = self._camera.read()

            if packet is None:
                self._stop_event.set()
                break

            try:
                self._queue.put_nowait(
                    packet
                )

            except Full:
                try:
                    self._queue.get_nowait()
                except Empty:
                    pass

                try:
                    self._queue.put_nowait(
                        packet
                    )
                except Full:
                    continue

                with self._counter_lock:
                    self._dropped_frames += 1

    def read(
        self,
        timeout: float = 1.0,
    ) -> FramePacket | None:
        try:
            return self._queue.get(
                timeout=timeout
            )

        except Empty:
            return None

    def stop(self) -> None:
        self._stop_event.set()

        if self._thread is not None:
            self._thread.join(
                timeout=2.0
            )