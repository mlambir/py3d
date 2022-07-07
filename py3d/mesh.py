import glm
import pywavefront


class Mesh:
    def __init__(self) -> None:
        self.pos = glm.vec3()
        self.rot = glm.vec3()
        self.scale = glm.vec3(1)
        self.vertices = []
        self.faces = []
        self.normals = []

    def load_obj(self, path):
        o = pywavefront.Wavefront(path)
        for v in o.vertices:
            self.vertices.append(glm.vec3(*v))
        for mat_name, mat in o.materials.items():
            for i in range(0, len(mat.vertices), 9):
                v1 = (mat.vertices[i], mat.vertices[i + 1], mat.vertices[i + 2])
                v2 = (mat.vertices[i + 3], mat.vertices[i + 4], mat.vertices[i + 5])
                v3 = (mat.vertices[i + 6], mat.vertices[i + 7], mat.vertices[i + 8])
                self.faces.append((o.vertices.index(v1), o.vertices.index(v2), o.vertices.index(v3)))
        self.calculate_normals()

    def calculate_normals(self):
        for f in self.faces:
            v1, v2, v3 = (self.vertices[i] for i in f)
            normal = glm.cross(v2 - v1, v3 - v1)
            self.normals.append(glm.normalize(normal))

    def world_matrix(self):
        world_matrix = glm.mat4(1)
        world_matrix = glm.translate(world_matrix, self.pos)
        world_matrix = glm.rotate(world_matrix, self.rot.x, glm.vec3(1, 0, 0))
        world_matrix = glm.rotate(world_matrix, self.rot.y, glm.vec3(0, 1, 0))
        world_matrix = glm.rotate(world_matrix, self.rot.z, glm.vec3(0, 0, 1))
        return glm.scale(world_matrix, self.scale)

    def world_vertices(self):
        return [self.world_matrix() * v for v in self.vertices]

    def world_normals(self):
        return [glm.normalize((self.world_matrix() * v).xyz) for v in self.normals]


class Cube(Mesh):
    def __init__(self) -> None:
        super().__init__()

        self.vertices = [glm.vec3(*v) for v in [
            (-1, -1, -1),
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, 1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, 1, 1),
        ]]

        self.faces = [
            (0, 2, 1),
            (0, 3, 2),

            (1, 2, 6),
            (6, 5, 1),

            (4, 5, 6),
            (6, 7, 4),

            (2, 3, 6),
            (6, 3, 7),

            (0, 7, 3),
            (0, 4, 7),

            (0, 1, 5),
            (0, 5, 4)

        ]
        self.calculate_normals()
