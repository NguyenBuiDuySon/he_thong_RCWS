from __future__ import annotations

from dataclasses import dataclass

from app.tracking.types import Track


@dataclass(frozen=True, slots=True)
class MotionEstimate:
    dx_norm_per_frame: float = 0.0
    dy_norm_per_frame: float = 0.0

    direction_x: int = 0
    direction_y: int = 0

    sample_count: int = 0


class TargetMotionMemory:
    def __init__(
        self,
        *,
        alpha: float = 0.5,
        direction_deadband: float = 0.001,
    ) -> None:
        if not 0.0 < alpha <= 1.0:
            raise ValueError("alpha must be in (0, 1]")

        if direction_deadband < 0.0:
            raise ValueError("direction_deadband must be >= 0")

        self._alpha = alpha
        self._direction_deadband = direction_deadband

        self.reset()

    @property
    def estimate(
        self,
    ) -> MotionEstimate:
        return self._estimate

    def reset(self) -> None:
        self._previous_frame_id: int | None = None

        self._previous_x_norm: float | None = None

        self._previous_y_norm: float | None = None

        self._estimate = MotionEstimate()

    def update(
        self,
        *,
        frame_id: int,
        track: Track,
        frame_width: int,
        frame_height: int,
    ) -> MotionEstimate:
        if frame_width <= 0:
            raise ValueError("frame_width must be > 0")

        if frame_height <= 0:
            raise ValueError("frame_height must be > 0")

        x_norm = track.center_x / frame_width

        y_norm = track.center_y / frame_height

        if self._previous_frame_id is None:
            self._remember_position(
                frame_id=frame_id,
                x_norm=x_norm,
                y_norm=y_norm,
            )

            return self._estimate

        if frame_id <= self._previous_frame_id:
            raise ValueError("frame_id must increase")

        assert self._previous_x_norm is not None

        assert self._previous_y_norm is not None

        delta_frames = frame_id - self._previous_frame_id

        raw_dx = (x_norm - self._previous_x_norm) / delta_frames

        raw_dy = (y_norm - self._previous_y_norm) / delta_frames

        if self._estimate.sample_count == 0:
            dx = raw_dx
            dy = raw_dy
        else:
            dx = (
                self._alpha * raw_dx
                + (1.0 - self._alpha) * self._estimate.dx_norm_per_frame
            )

            dy = (
                self._alpha * raw_dy
                + (1.0 - self._alpha) * self._estimate.dy_norm_per_frame
            )

        self._estimate = MotionEstimate(
            dx_norm_per_frame=dx,
            dy_norm_per_frame=dy,
            direction_x=self._direction(dx),
            direction_y=self._direction(dy),
            sample_count=(self._estimate.sample_count + 1),
        )

        self._remember_position(
            frame_id=frame_id,
            x_norm=x_norm,
            y_norm=y_norm,
        )

        return self._estimate

    def _remember_position(
        self,
        *,
        frame_id: int,
        x_norm: float,
        y_norm: float,
    ) -> None:
        self._previous_frame_id = frame_id
        self._previous_x_norm = x_norm
        self._previous_y_norm = y_norm

    def _direction(
        self,
        value: float,
    ) -> int:
        if abs(value) <= self._direction_deadband:
            return 0

        return 1 if value > 0.0 else -1

    def rebase(
        self,
        *,
        frame_id: int,
        track: Track,
        frame_width: int,
        frame_height: int,
    ) -> MotionEstimate:
        if frame_width <= 0:
            raise ValueError("frame_width must be > 0")

        if frame_height <= 0:
            raise ValueError("frame_height must be > 0")

        self._remember_position(
            frame_id=frame_id,
            x_norm=track.center_x / frame_width,
            y_norm=track.center_y / frame_height,
        )

        return self._estimate
