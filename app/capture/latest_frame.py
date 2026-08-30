from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from queue import Empty, Full, Queue
from threading import Event, Lock, Thread

from app.capture.camera import Camera, FramePacket


@dataclass(
    frozen=True,
    slots=True,
)
class StreamStats:
    captured_frames: int
    dropped_frames: int
    captured_fps: float
    drop_rate_pct: float


class LatestFrameStream:
    def __init__(
        self,
        camera: Camera,
        rate_window_frames: int = 120,
    ) -> None:
        self._camera = camera

        self._queue: Queue[FramePacket] = Queue(maxsize=1)
        self._stop_event = Event()
        self._thread: Thread | None = None
        self._stats_lock = Lock()
        self._captured_frames = 0
        self._dropped_frames = 0

        self._capture_times_ns: deque[int] = deque(
            maxlen=max(
                2,
                rate_window_frames,
            )
        )

    @property
    # def dropped_frames(self) -> int:
    #     with self._stats_lock:
    #         return self._dropped_frames

    def stats(self) -> StreamStats:
        with self._stats_lock:
            captured_frames = self._captured_frames

            dropped_frames = self._dropped_frames

            timestamps = tuple(self._capture_times_ns)

        captured_fps = 0.0

        if len(timestamps) >= 2:
            elapsed_s = (timestamps[-1] - timestamps[0]) / 1_000_000_000

            if elapsed_s > 0:
                captured_fps = (len(timestamps) - 1) / elapsed_s

        drop_rate_pct = 0.0

        if captured_frames > 0:
            drop_rate_pct = (dropped_frames / captured_frames) * 100.0

        return StreamStats(
            captured_frames=captured_frames,
            dropped_frames=dropped_frames,
            captured_fps=captured_fps,
            drop_rate_pct=drop_rate_pct,
        )

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
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

            with self._stats_lock:
                self._captured_frames += 1
                self._capture_times_ns.append(packet.received_at_ns)

            try:
                self._queue.put_nowait(packet)

            except Full:
                try:
                    self._queue.get_nowait()
                except Empty:
                    pass

                try:
                    self._queue.put_nowait(packet)
                except Full:
                    continue

                with self._stats_lock:
                    self._dropped_frames += 1

    def read(
        self,
        timeout: float = 1.0,
    ) -> FramePacket | None:
        try:
            return self._queue.get(timeout=timeout)

        except Empty:
            return None

    def stop(self) -> None:
        self._stop_event.set()

        if self._thread is not None:
            self._thread.join(timeout=2.0)
