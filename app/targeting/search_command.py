from __future__ import annotations

from app.control.types import PanTiltCommand
from app.targeting.motion import MotionEstimate
from app.targeting.search import SearchState


def _stopped() -> PanTiltCommand:
    return PanTiltCommand(
        pan_norm=0.0,
        tilt_norm=0.0,
        active=False,
    )


class SearchCommandGenerator:
    def __init__(
        self,
        *,
        coast_command: float = 0.18,
        search_command: float = 0.22,
        sweep_leg_frames: int = 12,
    ) -> None:
        if not 0.0 <= coast_command <= 1.0:
            raise ValueError("coast_command must satisfy 0 <= value <= 1")

        if not 0.0 <= search_command <= 1.0:
            raise ValueError("search_command must satisfy 0 <= value <= 1")

        if sweep_leg_frames <= 0:
            raise ValueError("sweep_leg_frames must be > 0")

        self._coast_command = coast_command
        self._search_command = search_command
        self._sweep_leg_frames = sweep_leg_frames

    def update(
        self,
        *,
        state: SearchState,
        motion: MotionEstimate,
        search_age_frames: int = 0,
    ) -> PanTiltCommand:
        if search_age_frames < 0:
            raise ValueError("search_age_frames must be >= 0")

        if state in {
            SearchState.INACTIVE,
            SearchState.REACQUIRE,
            SearchState.LOST,
        }:
            return _stopped()

        if state is SearchState.COAST:
            return self._coast_command_for(motion)

        if state is SearchState.SEARCHING:
            return self._sweep_command_for(
                motion,
                search_age_frames=search_age_frames,
            )

        return _stopped()

    def _coast_command_for(
        self,
        motion: MotionEstimate,
    ) -> PanTiltCommand:
        if motion.sample_count == 0 or (
            motion.direction_x == 0 and motion.direction_y == 0
        ):
            return _stopped()

        return PanTiltCommand(
            pan_norm=(self._coast_command * motion.direction_x),
            tilt_norm=(self._coast_command * motion.direction_y),
            active=True,
        )

    def _sweep_command_for(
        self,
        motion: MotionEstimate,
        *,
        search_age_frames: int,
    ) -> PanTiltCommand:
        leg_index = search_age_frames // self._sweep_leg_frames

        reverse = -1 if leg_index % 2 else 1

        dominant_axis = self._dominant_axis(motion)

        if dominant_axis == "tilt":
            initial_direction = motion.direction_y if motion.direction_y != 0 else 1

            return PanTiltCommand(
                pan_norm=0.0,
                tilt_norm=(self._search_command * initial_direction * reverse),
                active=True,
            )

        initial_direction = motion.direction_x if motion.direction_x != 0 else 1

        return PanTiltCommand(
            pan_norm=(self._search_command * initial_direction * reverse),
            tilt_norm=0.0,
            active=True,
        )

    @staticmethod
    def _dominant_axis(
        motion: MotionEstimate,
    ) -> str:
        if motion.direction_x == 0 and motion.direction_y != 0:
            return "tilt"

        return "pan"
