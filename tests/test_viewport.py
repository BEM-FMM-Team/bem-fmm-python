from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QEvent, QPoint

from bemfmm.gui.viewport import VIEW_PRESETS, Viewport


@pytest.mark.parametrize(
    ("angle_delta", "pixel_delta", "factor"),
    [(120, 0, 1.1), (-120, 0, 1 / 1.1), (0, 60, 1.1**0.5)],
)
def test_wheel_zoom_uses_qt_scroll_delta(angle_delta, pixel_delta, factor):
    camera = Mock()
    renderer = Mock()
    viewport = Viewport.__new__(Viewport)
    viewport.plt = SimpleNamespace(camera=camera, renderer=renderer)
    viewport.render = Mock()
    event = SimpleNamespace(
        type=lambda: QEvent.Wheel,
        angleDelta=lambda: QPoint(0, angle_delta),
        pixelDelta=lambda: QPoint(0, pixel_delta),
    )

    assert viewport._on_mouse(event)

    camera.Dolly.assert_called_once_with(factor)
    renderer.ResetCameraClippingRange.assert_called_once_with()
    viewport.render.assert_called_once_with()


@pytest.mark.parametrize(
    ("name", "position", "up"),
    [(name, *orientation) for name, orientation in VIEW_PRESETS.items()],
)
def test_view_preset_sets_camera_orientation(name, position, up):
    camera = Mock()
    renderer = Mock()
    viewport = Viewport.__new__(Viewport)
    viewport.plt = SimpleNamespace(camera=camera, renderer=renderer)
    viewport.render = Mock()

    viewport.view(name)

    camera.SetFocalPoint.assert_called_once_with(0, 0, 0)
    camera.SetPosition.assert_called_once_with(*position)
    camera.SetViewUp.assert_called_once_with(*up)
    renderer.ResetCamera.assert_called_once_with()
    viewport.render.assert_called_once_with()


@pytest.mark.parametrize(
    ("actor_name", "should_pick"),
    [("tissue:skin", True), ("tissue:brain", False), ("field:Emag", False)],
)
def test_point_pick_can_be_limited_to_a_surface(actor_name, should_pick):
    viewport = Viewport.__new__(Viewport)
    viewport.press2d = (10, 20)
    viewport.target_surface = None
    viewport.point_pick = True
    viewport.point_pick_surface = "skin"
    viewport.on_point = Mock()
    viewport.on_select = Mock()
    event = SimpleNamespace(
        picked2d=(10, 20),
        picked3d=(1.0, 2.0, 3.0),
        actor=SimpleNamespace(name=actor_name),
    )
    viewport.plt = SimpleNamespace(
        interactor=SimpleNamespace(GetEventPosition=lambda: (10, 20)),
        fill_event=Mock(return_value=event),
    )

    viewport._on_release()

    if should_pick:
        viewport.on_point.assert_called_once()
    else:
        viewport.on_point.assert_not_called()
    viewport.on_select.assert_not_called()
