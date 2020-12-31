from copy import copy, deepcopy


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
