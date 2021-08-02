from os.path import dirname, join, realpath
import time

import numpy as np

from pydrake.common.eigen_geometry import Quaternion

import taichi as ti
import taichi_three as t3

from plb.envs import make
from plb.envs.user_input import (
    JoystickAxis,
    JoystickButton,
    JoystickHat,
    JoystickWrapper,
)

data_dir = join(dirname(realpath(__file__)), "../../sandbox")


def pose_to_affine(pose, affine):
    xyz = pose[:3]
    affine.offset.from_numpy(xyz)
    wxyz = pose[3:]
    wxyz /= np.linalg.norm(wxyz)
    R = Quaternion(wxyz).rotation()
    affine.matrix.from_numpy(R)


def make_cylinder_model():
    # Lazy textured cylinder + scaling.    
    obj = t3.readobj(join(data_dir, "textured_cylinder.obj"))
    texture = ti.imread(join(data_dir, "textured_cylinder.png"))
    obj["vp"] = obj["vp"][:, :3]  # dunno why this is 6-elem; some weird export from MeshLab?
    # see config file
    r = 0.0254
    h = 0.254
    obj["vp"] *= np.array([[r, h, r]])
    cylinder = t3.Model.from_obj(obj, texture)
    return cylinder


class HackRenderer:
    def __init__(self, state):
        x, _, _, _, primitive = state
        self.pos = ti.Vector.field(3, ti.f32, len(x))

        self.particles = t3.ScatterModel(radius=4)
        self.particles.particles = self.pos

        self.cylinder = make_cylinder_model()

        self.camera = t3.Camera(
            pos=[0.5, 0.8 , 1.5],
            target=x.mean(axis=0).tolist(),
        )
        self._camera_param = [
            self.camera.pos,
            self.camera.trans,
            self.camera.target,
        ]
        self._camera_param0 = [
            p.to_numpy() for p in self._camera_param
        ]

        self.light = t3.Light()

        self.scene = t3.Scene()
        self.scene.add_model(self.particles)
        self.scene.add_model(self.cylinder)
        self.scene.add_camera(self.camera)
        self.scene.add_light(self.light)

        # N.B. For whatever reason, we have to call `scene.render()` to
        # ensure we can change the cylinder pose.
        self.scene.render()

        self.gui = ti.GUI("test", self.camera.res)
        self.step(state)

    def _read(self, state):
        x, _, _, _, primitive = state
        self.pos.from_numpy(x)
        pose_to_affine(primitive, self.cylinder.L2W)

    def reset(self):
        pass
        # TODO(eric.cousineau): This doesn't work. Meh.
        # for p, p0 in zip(self._camera_param, self._camera_param0):
        #     p.from_numpy(p0)

    def step(self, state):
        self._read(state)
        self.gui.get_event(None)
        self.camera.from_mouse(self.gui)
        self.scene.render()
        self.gui.set_image(self.camera.img)
        self.gui.show()
        return not self.gui.is_pressed(ti.GUI.ESCAPE)


def main():
    env = make("CustomDough-v1")
    env.seed(0)
    env.reset()
    taichi_env = env.unwrapped.taichi_env
    T = env._max_episode_steps
    assert taichi_env.primitives.action_dim == 3

    full_state = taichi_env.get_state()
    renderer = HackRenderer(full_state["state"])

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
            renderer.reset()

        p_vel = 0.0025

        # see action_scale for rationale here...
        act = np.zeros(3)
        # displacement along body x-axis
        act[0] = events[JoystickHat.LEFT_RIGHT] * p_vel
        # spin about world y-axis
        act[1] = events[JoystickAxis.RIGHTJOY_UP_DOWN] * 0.05
        # displacement along world y-axis
        act[2] = events[JoystickHat.UP_DOWN] * p_vel

        print(act)

        t_start = time.time()
        env.step(act)
        dt_step = time.time() - t_start
        print(f"  dt_step: {dt_step}")

        full_state = taichi_env.get_state()
        renderer.step(full_state["state"])


if __name__ == '__main__':
    main()
