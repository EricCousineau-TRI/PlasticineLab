import argparse

import cv2
import numpy as np

from plb.envs import make


def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument("--env_name", type=str, default="Move-v1")
    parser.add_argument("--path", type=str, default='./tmp')
    parser.add_argument("--seed", type=int, default=0)
    args=parser.parse_args()
    return args


def main():
    args = get_args()

    cv2.namedWindow("sim")
    cv2.moveWindow("sim", 0, 0)

    env = make(args.env_name)
    env.seed(args.seed)
    env.reset()
    taichi_env = env.unwrapped.taichi_env
    T = env._max_episode_steps

    movie = []
    for idx in range(T):
        print(f"idx: {idx}")
        act = np.zeros(taichi_env.primitives.action_dim)
        state = env.step(act)

        print(state)
        # img = env.render(mode='rgb_array')
        bgr = img[..., ::-1]
        cv2.imshow("sim", bgr)
        cv2.waitKey(1)
        movie.append(bgr.copy())

    print("Press A / D to move back/forward in time")

    idx = T - 1
    prev_idx = idx
    while True:
        bgr = movie[idx]
        cv2.imshow("sim", bgr)
        key = cv2.waitKey(100) & 0xFF
        if key == ord("a"):
            idx -= 1
        elif key == ord("d"):
            idx += 1
        idx = max(0, idx)
        idx = min(T - 1, idx)
        if idx != prev_idx:
            print(f"idx: {idx}")
            prev_idx = idx



if __name__ == '__main__':
    main()
