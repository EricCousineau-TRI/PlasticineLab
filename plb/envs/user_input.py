"""
Provides simple wrappers for accessing specific joysticks / gamepads via
PyGame.

Purchase link for Logitech F710 Wireless Gamepad:
https://www.amazon.com/Logitech-940-000117-Gamepad-F710/dp/B0041RR0TW
"""

from enum import Enum
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"  # noqa
import pygame

# Inspired by drake setup:
# https://github.com/RobotLocomotion/drake/blob/v0.26.0/examples/manipulation_station/end_effector_teleop_dualshock4.py  # noqa

# WARNING: Changing gamepads may change mappings! Be sure to check w/ pygame
# demo:
# https://www.pygame.org/docs/ref/joystick.html
# https://github.com/pygame/pygame/blob/1.9.6/docs/reST/ref/code_examples/joystick_calls.py  # noqa
GAMEPAD = "Logitech Gamepad F710"
# To map from L2/R2 trigger axes to a button boolean.
TRIGGER_TO_BUTTON_THRESHOLD = 0.5


class JoystickButton(Enum):
    # N.B. These buttons are defined in (A, B, X, Y) order, according to
    # Logitech controller.
    # This contrasts w/ PlayStation controller, which is (X, O, ☐, Δ).
    A_BUTTON = 0  # PS: X
    B_BUTTON = 1  # PS: O
    X_BUTTON = 2  # PS: ☐
    Y_BUTTON = 3  # PS: Δ
    L1_BUTTON = 4
    R1_BUTTON = 5
    SELECT_BUTTON = 6
    START_BUTTON = 7
    LEFTJOY_PRESSED = 9
    RIGHTJOY_PRESSED = 10
    # Virtual mappings (not directly from pygame, but using thresholds).
    L2_BUTTON = 100
    R2_BUTTON = 101

    def is_virtual(self):
        return self.value >= 100


class JoystickAxis(Enum):
    LEFTJOY_UP_DOWN = 1  # Up: -1, Down: 1
    LEFTJOY_LEFT_RIGHT = 0  # Left: -1, Right: 1
    RIGHTJOY_LEFT_RIGHT = 3  # Left: -1, Right: 1
    RIGHTJOY_UP_DOWN = 4  # Up: -1, Down: 1
    L2_BUTTON = 2  # Release: -1, Press: 1
    R2_BUTTON = 5  # Release: -1, Press: 1

    @classmethod
    def get_triggers(cls):
        return [
            cls.L2_BUTTON,
            cls.R2_BUTTON,
        ]


class JoystickHat(Enum):
    # (hat index, hat sub-index)
    LEFT_RIGHT = (0, 0)
    UP_DOWN = (0, 1)


class JoystickWrapper:
    _JOYSTICK_SINGLETON = None

    def __init__(self, joystick):
        assert joystick.get_name() == GAMEPAD, joystick.get_name()
        self._joystick = joystick
        self._is_trigger_initially_zero = dict()
        for trigger in JoystickAxis.get_triggers():
            self._is_trigger_initially_zero[trigger] = True

    @classmethod
    def make_singleton(cls, joystick_index=0):
        joystick = cls._JOYSTICK_SINGLETON
        if joystick is None:
            pygame.display.init()  # Necessary to use `pygame.event`.
            pygame.joystick.init()
            joystick = pygame.joystick.Joystick(joystick_index)
            joystick.init()
            cls._JOYSTICK_SINGLETON = joystick
        assert joystick.get_id() == joystick_index
        # Hm... sketchy, but meh.
        return JoystickWrapper(joystick)

    def can_reset(self):
        events = self.get_events()
        return not self.are_any_buttons_pressed(events)

    def reset(self):
        # N.B. Should ensure statefulness is only in polling class, not in
        # pygame device... somehow?
        pass

    def get_events(self):
        """
        Polls event directly from pygame device.

        (So we can have multiple subscribers to same joystick)
        """
        # TODO(eric): Is it a bad thing to pump events here?
        pygame.event.pump()
        events = dict()

        def deadband(x):
            # The logitech controller seems to have some stiction.
            if abs(x) < 0.1:
                return 0.0
            else:
                return x

        # To get mappings, use example code here:
        # https://www.pygame.org/docs/ref/joystick.html#controller-mappings
        # - Axes.
        for enum in JoystickAxis:
            events[enum] = deadband(self._joystick.get_axis(enum.value))
        # - Hat (direction pad).
        for enum in JoystickHat:
            hat_index, hat_subindex = enum.value
            hat_data = self._joystick.get_hat(hat_index)
            events[enum] = hat_data[hat_subindex]
        # Buttons.
        for enum in JoystickButton:
            if not enum.is_virtual():
                events[enum] = self._joystick.get_button(enum.value)
        # For whatever reason, the L2 and R2 axis start at zero, even though
        # they should start at -1.0. To fix, we latch read values of 0 to -1.0
        # at the very start.
        for trigger in JoystickAxis.get_triggers():
            if self._is_trigger_initially_zero[trigger]:
                if events[trigger] == 0.0:
                    events[trigger] = -1.0
                else:
                    self._is_trigger_initially_zero[trigger] = False
        # Map the (fixed) trigger values to booleans according to threshold.
        events[JoystickButton.L2_BUTTON] = (
            events[JoystickAxis.L2_BUTTON] >= TRIGGER_TO_BUTTON_THRESHOLD
        )
        events[JoystickButton.R2_BUTTON] = (
            events[JoystickAxis.R2_BUTTON] >= TRIGGER_TO_BUTTON_THRESHOLD
        )
        return events

    @staticmethod
    def _make_empty():
        empty = dict()
        empty[JoystickAxis.LEFTJOY_LEFT_RIGHT] = 0
        empty[JoystickAxis.LEFTJOY_UP_DOWN] = 0
        empty[JoystickAxis.RIGHTJOY_LEFT_RIGHT] = 0
        empty[JoystickAxis.RIGHTJOY_UP_DOWN] = 0
        empty[JoystickAxis.L2_BUTTON] = -1.0
        empty[JoystickAxis.R2_BUTTON] = -1.0
        empty[JoystickHat.LEFT_RIGHT] = 0
        empty[JoystickHat.UP_DOWN] = 0
        empty[JoystickButton.A_BUTTON] = False
        empty[JoystickButton.B_BUTTON] = False
        empty[JoystickButton.X_BUTTON] = False
        empty[JoystickButton.Y_BUTTON] = False
        empty[JoystickButton.L1_BUTTON] = False
        empty[JoystickButton.R1_BUTTON] = False
        empty[JoystickButton.L2_BUTTON] = False
        empty[JoystickButton.R2_BUTTON] = False
        empty[JoystickButton.SELECT_BUTTON] = False
        empty[JoystickButton.START_BUTTON] = False
        empty[JoystickButton.LEFTJOY_PRESSED] = False
        empty[JoystickButton.RIGHTJOY_PRESSED] = False
        return empty

    @classmethod
    def are_any_buttons_pressed(cls, events):
        empty = cls._make_empty()
        assert events.keys() == empty.keys(), set(events.keys()) ^ set(
            empty.keys()
        )
        return events != empty
