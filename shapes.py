import bpy
from copy import deepcopy
import numpy as np

from .enum_types import Axis


class BasicShape:
    vertices = []

    def __init__(self, scale=1.0):
        # make vertices unique to instance
        self.vertices = deepcopy(self.vertices)
        self.scale(scale)

    def scale(self, factor):
        for verts in self.vertices:
            for i, co in enumerate(verts):
                verts[i] = co * factor


class Tris2D(BasicShape):
    vertices = [
        [0.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
    ]


class Quad2D(BasicShape):
    vertices = deepcopy(Tris2D.vertices) + [deepcopy(Tris2D.vertices[-1]),
                                            [deepcopy(Tris2D.vertices[-1][0]), deepcopy(Tris2D.vertices[0][1])],
                                            deepcopy(Tris2D.vertices[0])]


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


class MeshShape3D(BasicShape):
    def __init__(self, mesh, scale=1.0):
        super().__init__(scale)
        self.tris_from_mesh(mesh, scale=scale)

    def tris_from_mesh(self, obj, scale=100, matrix=None, view_axis=Axis.Y):
        dg = bpy.context.evaluated_depsgraph_get()  # getting the dependency graph

        # This has to be done every time the object updates:
        ob = obj.evaluated_get(dg)  # this gives us the evaluated version of the object. Aka with all modifiers and deformations applied.
        mesh = ob.to_mesh()  # turn it into the mesh data block we want.

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

        # scale
        average = np.average(vertices, axis=0)

        vertices -= average
        vertices *= scale
        vertices += average

        self.vertices = [vertices[i] for i in np.concatenate(indices)]
        bpy.data.meshes.remove(mesh)


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
