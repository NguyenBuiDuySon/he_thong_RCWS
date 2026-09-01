import cv2

from app.targeting.mouse import (
    MouseActionType,
    MouseTargetInput,
)


def test_left_click_requests_selection() -> None:
    mouse = MouseTargetInput()

    mouse.callback(
        cv2.EVENT_LBUTTONDOWN,
        120,
        240,
        0,
        None,
    )

    action = mouse.consume()

    assert action is not None
    assert action.action is MouseActionType.SELECT
    assert action.x == 120
    assert action.y == 240


def test_right_click_requests_clear() -> None:
    mouse = MouseTargetInput()

    mouse.callback(
        cv2.EVENT_RBUTTONDOWN,
        0,
        0,
        0,
        None,
    )

    action = mouse.consume()

    assert action is not None
    assert action.action is MouseActionType.CLEAR


def test_action_is_consumed_once() -> None:
    mouse = MouseTargetInput()

    mouse.callback(
        cv2.EVENT_LBUTTONDOWN,
        10,
        20,
        0,
        None,
    )

    assert mouse.consume() is not None
    assert mouse.consume() is None
