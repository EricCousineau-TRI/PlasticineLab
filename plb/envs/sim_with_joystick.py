import time

import cv2
import numpy as np

from plb.envs import make
from plb.envs.user_input import (
    JoystickAxis,
    JoystickButton,
    JoystickHat,
    JoystickWrapper,
)


def main():
    cv2.namedWindow("sim")
    cv2.moveWindow("sim", 0, 0)

    env = make("CustomDough-v1")
    env.seed(0)
    env.reset()
    taichi_env = env.unwrapped.taichi_env
    T = env._max_episode_steps
    assert taichi_env.primitives.action_dim == 3

    joystick = JoystickWrapper.make_singleton()
    print("Please release any buttons...")
    while True:
        events = joystick.get_events()
        if joystick.are_any_buttons_pressed(events):
            time.sleep(0.1)
        else:
            break
    print("  Done")

    while True:
        events = joystick.get_events()
        if events[JoystickButton.START_BUTTON]:
            env.reset()

        # see action_scale for rationale here...
        act = np.zeros(3)
        # displacement along body x-axis
        act[0] = -events[JoystickHat.LEFT_RIGHT] * 0.01
        # spin about world y-axis
        act[1] = events[JoystickAxis.RIGHTJOY_UP_DOWN] * 0.05
        # displacement along world y-axis
        act[2] = events[JoystickHat.UP_DOWN] * 0.01

        print(act)
        env.step(act)
        img = env.render(mode='rgb_array')
        bgr = img[..., ::-1]
        cv2.imshow("sim", bgr)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
