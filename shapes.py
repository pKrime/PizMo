import bpy

from math import pi
from math import cos
from math import sin
from math import sqrt

from copy import deepcopy
import numpy as np

from .enum_types import Axis


class BasicShape:
    vertices = []

    def __init__(self, scale=1.0, offset=(0.0, 0.0)):
        # make vertices unique to instance
        self.vertices = deepcopy(self.vertices)
        self.scale(scale)
        self.offset(offset)
        self.center()

    def scale(self, factor):
        for verts in self.vertices:
            for i, co in enumerate(verts):
                verts[i] = co * factor

    def offset(self, offset):
        for verts in self.vertices:
            for i, co in enumerate(verts):
                verts[i] = co + offset[i]

    @property
    def size(self):
        # TODO
        return 1.0, 1.0

    def center(self):
        size_x, size_y = self.size
        self.offset((size_x/-2.0, size_y/-2.0))


class Tris2D(BasicShape):
    vertices = [
        [0.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
    ]


class Quad2D(BasicShape):
    vertices = deepcopy(Tris2D.vertices) + [deepcopy(Tris2D.vertices[-1]),
                                            [Tris2D.vertices[-1][0], Tris2D.vertices[0][1]],
                                            deepcopy(Tris2D.vertices[0])]

    @property
    def size(self):
        low_left = self.vertices[0]
        up_right = self.vertices[2]
        return abs(up_right[0] - low_left[0]), abs(up_right[1] - low_left[1])

    def frame_vertices(self, thickness=0.25):
        inner = Quad2D(scale=1 - thickness)
        inner.center()

        verts = []
        for i in range(0, 4, 3):
            verts.append(self.vertices[i])
            verts.append(self.vertices[i + 1])
            verts.append(inner.vertices[i])

            verts.append(inner.vertices[i])
            verts.append(inner.vertices[i + 1])
            verts.append(self.vertices[i + 1])

            verts.append(self.vertices[i + 1])
            verts.append(self.vertices[i + 2])
            verts.append(inner.vertices[i + 1])

            verts.append(inner.vertices[i + 1])
            verts.append(inner.vertices[i + 2])
            verts.append(self.vertices[i + 2])

        return verts


class Rect2D(BasicShape):
    # Coordinates (each one is a triangle).
    vertices = [
        [-0.5, -1.0],
        [-0.5, 1.0],
        [0.5, 1.0],

        [0.5, 1.0],
        [0.5, -1.0],
        [-0.5, -1.0],
    ]


class Cross2D(BasicShape):
    vertices = deepcopy(Rect2D.vertices) + [
        [-1.0, -0.5],
        [-1.0, 0.5],
        [1.0, 0.5],

        [1.0, 0.5],
        [1.0, -0.5],
        [-1.0, -0.5],
    ]


class Circle2D(BasicShape):
    def __init__(self, scale=1.0, offset=(0.0, 0.0), segments=24):
        self.segments = segments
        self.vertices = []

        if any(offset):
            raise NotImplementedError

        full_circle = 2 * pi
        arc_len = full_circle / self.segments

        for i in range(self.segments):
            arc = arc_len * i
            self.vertices.append([cos(arc) * scale, sin(arc * scale)])
            arc = arc_len * (i + 1)
            self.vertices.append([cos(arc) * scale, sin(arc) * scale])
            self.vertices.append([0.0, 0.0])

    @property
    def size(self):
        vert = self.vertices[0]
        diameter = sqrt(pow(vert[0], 2) + pow(vert[1], 2))
        return diameter, diameter

    def frame_vertices(self, thickness=0.25):
        scale = 1 - thickness
        verts = []

        inner = None
        for vert in self.vertices:
            if inner:
                verts.append(vert)
                verts.append(inner)
            verts.append(vert)
            inner = [vert[0] * scale, vert[1] * scale]
            verts.append(inner)

        return verts


class MeshShape3D(BasicShape):

    def __init__(self, mesh, scale=1.0, vertex_groups=None, weight_threshold=0.2):
        self._indices = []
        self._obj = None
        self.scale_factor = scale
        self.tris_from_mesh(mesh, vertex_groups=vertex_groups, weight_threshold=weight_threshold)

    @property
    def vertices(self):
        if not self._obj:
            return []

        dg = bpy.context.evaluated_depsgraph_get()
        ob = self._obj.evaluated_get(dg)
        mesh = ob.to_mesh()
        mesh.calc_loop_triangles()

        verts = np.array([mesh.vertices[i].co for i in self._indices], 'f')

        # scale
        average = np.average(verts, axis=0)
        verts -= average
        verts *= self.scale_factor
        verts += average

        return verts

    def tris_from_mesh(self, obj, vertex_groups=[], weight_threshold=0.2):
        self._obj = obj

        mesh = self._obj.data
        mesh.calc_loop_triangles()

        self._indices = []
        if vertex_groups:
            group_idx = [obj.vertex_groups[vertex_group].index for vertex_group in vertex_groups]

            for tris in mesh.loop_triangles:
                if all(any(g.weight > weight_threshold for g in mesh.vertices[i].groups if g.group in group_idx) for i in tris.vertices):
                    self._indices.extend(tris.vertices)
        else:
            indices = np.empty((len(mesh.loop_triangles), 3), 'i')
            mesh.loop_triangles.foreach_get(
                "vertices", np.reshape(indices, len(mesh.loop_triangles) * 3))

            self._indices = np.concatenate(indices)


class MeshShape2D(BasicShape):
    def __init__(self, mesh, scale=1.0):
        super().__init__(scale)
        self.tris_from_mesh(mesh, scale=scale)

    def tris_from_mesh(self, mesh, scale=100, matrix=None, view_axis=Axis.Y):
        mesh.calc_loop_triangles()

        vertices = np.empty((len(mesh.vertices), 3), 'f')
        indices = np.empty((len(mesh.loop_triangles), 3), 'i')

        mesh.vertices.foreach_get(
            "co", np.reshape(vertices, len(mesh.vertices) * 3))
        mesh.loop_triangles.foreach_get(
            "vertices", np.reshape(indices, len(mesh.loop_triangles) * 3))

        if matrix:
            # we invert the matrix as we are facing the object
            np_mat = np.array(matrix.normalized().inverted().to_3x3())
            vertices *= matrix.to_scale()
            np.copyto(vertices, vertices @ np_mat)
            vertices += matrix.translation

        # remove view axis
        vertices = np.delete(vertices, view_axis.value, 1)
        # scale
        vertices *= scale

        self.vertices = [vertices[i] for i in np.concatenate(indices)]
