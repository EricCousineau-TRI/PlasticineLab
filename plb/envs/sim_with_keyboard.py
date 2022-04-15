import time

import cv2
import numpy as np

from plb.envs import make


def main():
    env = make("CustomDough-v1")
    env.seed(0)
    env.reset()
    taichi_env = env.unwrapped.taichi_env
    T = env._max_episode_steps
    assert taichi_env.primitives.action_dim == 3

    while True:
        p_vel = 0.0025
        w_vel = 0.05
        # see action_scale for rationale here...
        act = np.zeros(3)

        key = cv2.waitKey(1) & 0xFF
        # using cv2 for keys kinda sucks compared to joystick or pygame :(
        if key == ord('r'):
            env.reset()
            if renderer is not None:
                renderer.reset()
        # # displacement along body x-axis
        if key == ord('a'):
            act[0] = p_vel
        if key == ord('d'):
            act[0] = -p_vel
        # displacement along world y-axis
        if key == ord('w'):
            act[2] = p_vel
        if key == ord('s'):
            act[2] = -p_vel
        # spin about world y-axis
        if key == ord('q'):
            act[1] = w_vel
        if key == ord('e'):
            act[1] = -w_vel

        t_start = time.time()
        env.step(act)
        rgb = env.render(mode="rgb")  # slow :(
        dt_step = time.time() - t_start

        bgr = rgb[..., ::-1]
        print(f"  dt_step: {dt_step}")

        cv2.imshow("image", bgr)


if __name__ == '__main__':
    main()
