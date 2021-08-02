import dataclasses as dc

import numpy as np
import torch

import neural_renderer as nr


@dc.dataclass
class Mesh:
    vertices: torch.Tensor  # [num_vertices, 3], float32
    faces: torch.Tensor  # [num_faces, 3], int32
    textures: torch.Tensor  # [num_faces, num_tex, num_tex, num_tex, 3], float32

    def __post_init__(self):
        if self.vertices is None:
            assert self.faces is None
            assert self.textures is None
        else:
            assert self.vertices.dim() == 2
            assert self.vertices.shape[1] == 3
            assert self.vertices.dtype == torch.float32
            assert self.faces.dim() == 2
            assert self.faces.shape[1] == 3
            assert self.faces.dtype == torch.int32

    @classmethod
    def from_file(cls, filename, *, load_texture=False, color=None):
        if load_texture:
            assert color is None
            vertices, faces, textures = nr.load_obj(
                filename, normalization=False, load_texture=True
            )
        else:
            vertices, faces = nr.load_obj(
                filename, normalization=False, load_texture=False
            )
            textures = make_fake_textures(faces, color=color)
        return Mesh(
            vertices=vertices,
            faces=faces,
            textures=textures,
        )

    @classmethod
    def empty(self):
        return Mesh(
            vertices=None,
            faces=None,
            textures=None,
        )

    def add_object(self, obj, p_WO, R_WO=None):
        assert isinstance(obj, Mesh)
        # Transform vertices (with gradient).
        v = obj.vertices
        if R_WO is not None:
            v = v @ R_WO.transpose(0, 1)
        new_vertices = p_WO.unsqueeze(0) + v
        # Offset face vertex indices (no gradient).
        if self.vertices is not None:
            prev_num_vertices = len(self.vertices)
        else:
            prev_num_vertices = 0
        with torch.no_grad():
            new_faces = obj.faces + prev_num_vertices
        # Naively get new textures
        new_textures = obj.textures.clone()
        # Now concatenate.
        if self.vertices is None:
            self.vertices = new_vertices
            self.faces = new_faces
            self.textures = new_textures
        else:
            self.vertices = torch.cat([self.vertices, new_vertices])
            self.faces = torch.cat([self.faces, new_faces])
            self.textures = torch.cat([self.textures, new_textures])

    def unsqueeze(self):
        # Unsqueeze to add batch dimension.
        return self.vertices.unsqueeze(0), self.faces.unsqueeze(0), self.textures.unsqueeze(0)


@dc.dataclass
class RgbDepth:
    rgb: torch.Tensor = None  # Batched, NCHW
    depth: torch.Tensor = None  # Batched

    def add(self, other):
        if self.rgb is None:
            assert self.depth is None
            self.rgb = other.rgb
            self.depth = other.depth
        else:
            assert self.depth is not None
            new = other.depth < self.depth
            new_rgb = new.unsqueeze(1).repeat(1, 3, 1, 1)  # For color channel
            self.rgb[new_rgb] = other.rgb[new_rgb]
            self.depth[new] = other.depth[new]

    def numpy(self):
        rgb = self.rgb.squeeze(0).cpu().numpy().transpose(1, 2, 0)
        depth = self.depth.cpu().numpy()
        return rgb, depth


def make_fake_textures(faces, color=None, num_tex=1):
    num_faces, vertices_per_face = faces.shape
    assert vertices_per_face == 3
    num_channels = 3
    textures = torch.ones(
        (num_faces, num_tex, num_tex, num_tex, num_channels),
        dtype=torch.float32,
        device=faces.device,
    )
    if color is not None:
        textures[..., :] = color
    return textures


def intrinsic_matrix_from_fov(width, height, fov_y):
    # https://github.com/RobotLocomotion/drake/blob/v0.32.0/systems/sensors/camera_info.cc
    focal_x = height * 0.5 / np.tan(0.5 * fov_y)
    focal_y = focal_x
    pp_x = width / 2 - 0.5  # OpenGL half-pixel
    pp_y = height / 2 - 0.5
    return np.array([
        [focal_x, 0, pp_x],
        [0, focal_y, pp_y],
        [0, 0, 1],
    ])
