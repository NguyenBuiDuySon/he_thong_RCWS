from app.targeting.search import SearchController, SearchState
from app.targeting.types import TargetStatus


def test_locked_is_inactive() -> None:
    controller = SearchController(
        coast_frames=2,
        reacquire_frames=3,
    )

    state = controller.update(
        target_status=TargetStatus.LOCKED,
        missing_frames=0,
    )

    assert state is SearchState.INACTIVE


def test_short_loss_enters_coast() -> None:
    controller = SearchController(
        coast_frames=2,
        reacquire_frames=3,
    )

    state = controller.update(
        target_status=TargetStatus.LOST,
        missing_frames=1,
    )

    assert state is SearchState.COAST


def test_loss_enters_reacquire_after_coast() -> None:
    controller = SearchController(
        coast_frames=2,
        reacquire_frames=3,
    )

    state = controller.update(
        target_status=TargetStatus.LOST,
        missing_frames=3,
    )

    assert state is SearchState.REACQUIRE


def test_longer_loss_enters_searching() -> None:
    controller = SearchController(
        coast_frames=2,
        reacquire_frames=3,
    )

    state = controller.update(
        target_status=TargetStatus.LOST,
        missing_frames=6,
    )

    assert state is SearchState.SEARCHING


def test_timeout_enters_lost() -> None:
    controller = SearchController()

    state = controller.update(
        target_status=TargetStatus.IDLE,
        missing_frames=0,
        timed_out=True,
    )

    assert state is SearchState.LOST


def test_reacquired_target_returns_inactive() -> None:
    controller = SearchController(
        coast_frames=2,
        reacquire_frames=3,
    )

    controller.update(
        target_status=TargetStatus.LOST,
        missing_frames=6,
    )

    state = controller.update(
        target_status=TargetStatus.LOCKED,
        missing_frames=0,
    )

    assert state is SearchState.INACTIVE
